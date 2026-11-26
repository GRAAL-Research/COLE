const VARIANTS = {
  primary: 'bg-accent text-white hover:bg-accent-strong',
  secondary: 'border border-gray-400 bg-white text-gray-800 hover:bg-gray-100',
};

const BASE =
  'inline-flex min-h-11 items-center justify-center rounded-md px-4 py-2 text-base font-medium';

// Shared by <button> and <Link> so page-level actions look the same.
export const buttonClass = (variant = 'primary', disabled = false, className = '') => {
  const state = disabled
    ? 'cursor-not-allowed border border-transparent bg-gray-200 text-gray-600'
    : VARIANTS[variant];
  return `${BASE} ${state} ${className}`.trim();
};

export default function BigBlueButton({
  children,
  onClick,
  disabled,
  type = 'button',
  variant = 'primary',
  className = '',
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={buttonClass(variant, disabled, className)}
    >
      {children}
    </button>
  );
}
