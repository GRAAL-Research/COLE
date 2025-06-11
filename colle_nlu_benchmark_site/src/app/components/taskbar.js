'use client';
import Link from 'next/link';
import Modal from './Modal';

import { usePathname,useRouter,useSearchParams } from 'next/navigation';


export default function Taskbar() {
  const pathname = usePathname();

  const linkStyle = (path) =>
    pathname === path
      ? 'text-blue-500 font-semibold'
      : 'text-gray-700 hover:text-blue-500';
  return (
    <nav className="w-full py-4 bg-None flex justify-between items-center mx-auto max-w-5xl">
      
      <Link href="/" className="text-xl font-bold text-blue-600">COLLE</Link>
      
      <div className="space-x-6">
        <Link href="/guide" className={linkStyle('/guide')}>Guide</Link>
        <Link href="/FAQ" className={linkStyle('/FAQ')}>FAQ</Link>
        <Link href="/contact" className={linkStyle('/contact')}>Contact us</Link>
        <Link href={`${pathname}?show=submit`} className={linkStyle("/submit")}>Submit your results</Link>
        <Link href="/benchmarks" className={linkStyle('/benchmarks')}>Our tasks</Link>
        <Link href="/results" className={linkStyle('/results')}>Results</Link>
        <Link href="/leaderboard" className={linkStyle('/leaderboard')}>Colle Leaderboard</Link>
        <Link href="https://huggingface.co/datasets/COLLE-Graal/ColleGraal" className={linkStyle("/hf")}>Our datasets</Link>
      </div>
    </nav>
  );
}