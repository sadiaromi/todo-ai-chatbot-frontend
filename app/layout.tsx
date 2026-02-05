import type { Metadata } from "next";
import { GeistSans, GeistMono } from 'geist/font';
import "./globals.css";
import { Providers } from '../src/components/Providers';

const geistSans = GeistSans;
const geistMono = GeistMono;

export const metadata: Metadata = {
  title: "Todo AI Chatbot",
  description: "AI-powered Todo Application with natural language processing",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
