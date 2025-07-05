'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FileText } from 'lucide-react';  // icône “papier”

export default function Taskbar() {
  const pathname = usePathname();

  const linkStyle = (path) =>
    pathname === path
      ? 'text-blue-500 font-semibold'
      : 'text-gray-700 hover:text-blue-500';

  return (
    <nav className="w-full py-4 bg-none flex justify-between items-center mx-auto max-w-5xl">
      <div className="flex items-center">
        <Link href="/">
          <span className="text-xl font-bold text-blue-600">COLLE</span>
        </Link>

        <Link href="/papers" className="ml-2">
          <FileText className="w-6 h-6 text-blue-600 hover:text-blue-500" />
        </Link>
      </div>

      {/* Liens de navigation */}
      <div className="space-x-6">
        <Link href="/guide" className={linkStyle('/guide')}>Guide</Link>
        <Link href="/FAQ" className={linkStyle('/FAQ')}>FAQ</Link>
        <Link href="/contact" className={linkStyle('/contact')}>Contact us</Link>
        <Link href={`${pathname}?show=submit`} className={linkStyle('/submit')}>Submit your results</Link>
        <Link href="/benchmarks" className={linkStyle('/benchmarks')}>Our tasks</Link>
        <Link href="/results" className={linkStyle('/results')}>Results</Link>
        <Link href="/leaderboard" className={linkStyle('/leaderboard')}>COLLE Leaderboard</Link>
        <Link href="https://huggingface.co/datasets/graalul/COLLE-public" className={linkStyle('/hf')}>Our datasets</Link>
      </div>
    </nav>
  );
}
