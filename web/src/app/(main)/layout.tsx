'use client';

import { useAuth } from '@/auth/AuthProvider';
import Navbar from '@/components/navbar/Navbar';
import LoadingPage from '@/components/loading/Loading';

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const auth = useAuth();

  return (
    <div className="flex flex-col h-screen">
      <Navbar />
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
