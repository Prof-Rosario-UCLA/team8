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
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // waiting for auth setup
    fetch('/api/user/me', { credentials: 'include' })
      .then(res => (res.ok ? res.json() : null))
      .then(data => {
        if (!data) {
          router.push('/');
        } else {
          setUser(data);
        }
      }).catch(() => {
        router.push('/');
      })
      .finally(() => {
        setIsLoaded(true);
      });
  }, [router, pathname]);

  if (!isLoaded) return <LoadingPage />;

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
