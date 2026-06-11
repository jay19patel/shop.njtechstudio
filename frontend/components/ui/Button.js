import React from 'react';

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
  ...props
}) {
  const variants = {
    primary: 'bg-slate-900 text-white hover:bg-slate-800',
    secondary: 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50',
    ghost: 'text-slate-600 hover:bg-slate-50',
    danger: 'bg-red-600 text-white hover:bg-red-700',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs font-bold',
    md: 'px-4 py-2 text-xs font-bold',
    lg: 'px-6 py-3 text-sm font-bold',
    pill: 'px-6 py-2 text-xs font-bold rounded-full',
  };

  const baseClasses = `
    uppercase tracking-wider rounded-lg transition-colors
    ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
  `;

  const finalClassName = `
    ${baseClasses}
    ${variants[variant]}
    ${sizes[size]}
    ${className}
  `;

  return (
    <button
      className={finalClassName}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
