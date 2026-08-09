import React from 'react';
import './globals.css';

export const metadata = {
  title: 'Autonomous Supply Chain Command Center',
  description: 'AI-Powered Autonomous Supply Chain Exception Management System & LangGraph Agent Operations',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="bg-[#070a12] text-slate-100 antialiased font-sans" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
