import { ReactNode } from 'react';
import { AuthProvider } from '../lib/auth-react';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
}