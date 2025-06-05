'use client';
import { useState, useEffect, createContext, useContext } from 'react';
import { useRouter, usePathname } from 'next/navigation';

import { User } from '@/lib/types/User';
import LoadingPage from '@/components/auth/Loading';

interface AuthContextType {
  user: User | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState(null);
  const [checked, setChecked] = useState(false);
  const router = useRouter();
  const pathname = usePathname();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    console.log('fetching user');
    setIsLoading(true);

    // waiting for auth setup

    fetch('/api/user/me', { credentials: 'include' })
      .then(res => {
        console.log(`Response: ${res.ok} ${JSON.stringify(res.body)}`);
        return res.ok ? res.json() : null;
      })
      .then(data => {
        console.log(`User data: ${JSON.stringify(data)}`);
        if (!data) {
          // router.push(`/api/auth/login?next=${pathname}`);
        } else {
          setUser(data);
        }
      }).catch(err => {
        // router.push(`/api/auth/login?next=${pathname}`);
      })
      .finally(() => {
        setChecked(true);
        setIsLoading(false);
      });
  }, []);

  if (!checked) return <LoadingPage />;

  return (
    <AuthContext.Provider value={{ user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
