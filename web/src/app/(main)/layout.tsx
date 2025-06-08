'use client';

import { useAuth } from '@/auth/AuthProvider';
import Navbar from '@/components/navbar/Navbar';
import LoadingPage from '@/components/loading/Loading';

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const auth = useAuth();

  if (!auth || !auth.user) {
    console.log("Loading page. Auth state:", auth, "User:", auth ? auth.user : 'No user object');
    return <LoadingPage />;
  }

  return (
    <>
      <Navbar />
      {children}
    </>
  );
}
