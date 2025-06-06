'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Taskbar() {
  const pathname = usePathname();

  const linkStyle = (path) =>
    pathname === path
      ? 'text-blue-500 font-semibold'
      : 'text-gray-700 hover:text-blue-500';

  return (
    <nav className="w-full px-6 py-4 bg-white shadow-md flex justify-between items-center">
      <Link href="/" className="text-xl font-bold text-blue-600">COLLE</Link>
      <div className="space-x-6">
        <Link href="/guide" className={linkStyle('/guide')}>Guide</Link>
        <Link href="/FAQ" className={linkStyle('/FAQ')}>FAQ</Link>
        <Link href="/contact" className={linkStyle('/contact')}>Contact us</Link>
        <button className={linkStyle("/submit")}>Submit your results</button>
        <Link href="https://huggingface.co/datasets/COLLE-Graal/ColleGraal" className={linkStyle("/hf")}>Our datasets</Link>
      </div>
    </nav>
  );
}