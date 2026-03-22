import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import ClientHeader from "./components/ClientHeader";
import ModalManager from "./components/ModalManager";
import {Suspense} from "react";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "COLE NLU",
  description: "COLE : An NLU benchmark",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <ClientHeader />
        <main className="w-full flex justify-center px-4 pt-8">
          <div className="w-full max-w-7xl">{children}</div>
        </main>
        <Suspense fallback={null}>
          <ModalManager/>
        </Suspense>
      </body>
    </html>
  );
}
