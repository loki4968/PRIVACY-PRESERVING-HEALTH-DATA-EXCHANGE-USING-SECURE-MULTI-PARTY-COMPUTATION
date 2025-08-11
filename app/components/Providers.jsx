"use client";

import { AuthProvider } from '../context/AuthContext';
import NextTopLoader from "nextjs-toploader";

export default function Providers({ children }) {
  return (
    <AuthProvider>
      <NextTopLoader
        color="#29D"
        initialPosition={0.08}
        crawlSpeed={200}
        height={3}
        crawl={true}
        showSpinner={false}
        easing="ease"
        speed={200}
        shadow="0 0 10px #29D,0 0 5px #29D"
      />
      {children}
    </AuthProvider>
  );
} 