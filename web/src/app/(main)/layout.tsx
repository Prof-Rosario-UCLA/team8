'use client';

import Navbar from '@/components/navbar/Navbar';

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col h-screen">
      <Navbar />
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
