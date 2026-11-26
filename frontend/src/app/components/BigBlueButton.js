const VARIANTS = {
  primary: 'bg-accent text-white hover:bg-accent-strong',
  secondary: 'border border-gray-400 bg-white text-gray-800 hover:bg-gray-100',
};

export default function BigBlueButton({
  children,
  onClick,
  disabled,
  type = 'button',
  variant = 'primary',
  className = '',
}) {
  const state = disabled
    ? 'cursor-not-allowed bg-gray-200 text-gray-600 border-transparent'
    : VARIANTS[variant];

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex min-h-11 items-center justify-center rounded-md px-4 py-2 text-base font-medium ${state} ${className}`}
    >
      {children}
    </button>
  );
}
