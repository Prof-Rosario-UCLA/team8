'use client';
import { useState, useEffect, createContext, useContext } from 'react';
import { useRouter, usePathname } from 'next/navigation';

import { User } from '@/lib/types/User';
import LoadingPage from '@/components/loading/Loading';

interface AuthContextType {
  user: User | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();
  const pathname = usePathname();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);

    // waiting for auth setup

    fetch('/api/user/me', { credentials: 'include' })
      .then(res => (res.ok ? res.json() : null))
      .then(data => {
        if (!data) {
          router.push(`/api/auth/login?next=${pathname}`);
        } else {
          setUser(data);
        }
      }).catch(() => {
        router.push(`/api/auth/login?next=${pathname}`);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [router, pathname]);

  if (isLoading) return <LoadingPage />;

  return (
    <AuthContext.Provider value={{ user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
