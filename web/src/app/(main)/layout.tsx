'use client';

import Navbar from '@/components/navbar/Navbar';
import { AuthProvider } from '@/auth/AuthProvider';

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
    <div className="flex flex-col h-screen">
      <Navbar />
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
    </AuthProvider>
  );
}
