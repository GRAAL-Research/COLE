export default function ErrorMessage({ id, children }) {
  if (!children) return null;
  return (
    <p id={id} className="mt-1 text-sm font-medium text-red-700">
      {children}
    </p>
  );
}
