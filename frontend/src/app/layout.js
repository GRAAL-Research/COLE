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
  title: {
    default: "COLE - Comprehensive Benchmark for French Language Understanding",
    template: "%s | COLE",
  },
  description: "COLE is a benchmark of 23 tasks for evaluating French Natural Language Understanding (NLU) in large language models.",
  openGraph: {
    title: "COLE - French NLU Benchmark",
    description: "Evaluate LLMs on 23 French NLU tasks: sentiment analysis, NLI, QA, and more.",
    url: "https://colebenchmark.org",
    siteName: "COLE Benchmark",
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "COLE - French NLU Benchmark",
    description: "Evaluate LLMs on 23 French NLU tasks: sentiment analysis, NLI, QA, and more.",
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} font-sans antialiased`}>
        <ClientHeader />
        <main id="main-content" className="mx-auto w-full max-w-7xl px-4 pb-12 pt-8 sm:px-6">
          {children}
        </main>
        <Suspense fallback={null}>
          <ModalManager/>
        </Suspense>
      </body>
    </html>
  );
}
