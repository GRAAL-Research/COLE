export default function PageTitle({ children, className = '' }) {
  return (
    <h1
      className={`mb-8 border-l-4 border-accent pl-4 text-3xl font-bold text-gray-900 ${className}`}
    >
      {children}
    </h1>
  );
}

export function SectionTitle({ children, className = '' }) {
  return (
    <h2 className={`mb-4 text-2xl font-semibold text-gray-900 ${className}`}>
      {children}
    </h2>
  );
}
