/// <reference lib="webworker" />

import type { PrecacheEntry, SerwistGlobalConfig } from "serwist";
import { Serwist } from "serwist";
import { BackgroundSyncPlugin } from "@serwist/background-sync";
import { CacheFirst, NetworkFirst, NetworkOnly } from "@serwist/strategies";
import { CacheableResponsePlugin } from "@serwist/cacheable-response";
import { ExpirationPlugin } from "@serwist/expiration";

declare const self: ServiceWorkerGlobalScope;

declare global {
  interface WorkerGlobalScope extends SerwistGlobalConfig {
    __SW_MANIFEST: (PrecacheEntry | string)[] | undefined;
  }
}

const bgSyncPlugin = new BackgroundSyncPlugin("resume-update-queue", {
  maxRetentionTime: 24 * 60, // Retry for up to 24 hours
  onSync: async () => {
    const windows = await self.clients.matchAll({ type: "window" });
    for (const window of windows) {
      window.postMessage({
        type: "RESUME_SYNC_SUCCESS",
        message: "Your resume has been successfully synced.",
      });
    }
  },
});

const serwist = new Serwist({
  precacheEntries: self.__SW_MANIFEST,
  skipWaiting: true,
  clientsClaim: true,
  navigationPreload: true,
  runtimeCaching: [
    {
      matcher: ({ url }) => url.pathname.startsWith("/api/user/me") || url.pathname.startsWith("/api/resume/all"),
      handler: new NetworkFirst({
        cacheName: "api-data-cache",
        networkTimeoutSeconds: 3,
        plugins: [ new CacheableResponsePlugin({ statuses: [0, 200] }) ],
      }),
    },
    {
      matcher: ({ url }) => url.pathname.startsWith("/api/resume/"),
      handler: new NetworkFirst({
        cacheName: "resume-document-cache",
        networkTimeoutSeconds: 3,
        plugins: [
          new CacheableResponsePlugin({ statuses: [0, 200] }),
          new ExpirationPlugin({ maxEntries: 50, maxAgeSeconds: 30 * 24 * 60 * 60 }),
        ],
      }),
    },
    {
      matcher: ({ request }) => request.destination === "font" || request.destination === "image",
      handler: new CacheFirst({
        cacheName: "static-assets-cache",
        plugins: [ new ExpirationPlugin({ maxEntries: 30, maxAgeSeconds: 60 * 60 * 24 * 30 }) ],
      }),
    },
    {
      matcher: ({ url, request }) => url.pathname.startsWith("/api/resume/update/") && request.method === "PUT",
      handler: new NetworkOnly({
        plugins: [bgSyncPlugin],
      }),
    },
  ],
});

serwist.addEventListeners(); 
serwist.addEventListeners(); 