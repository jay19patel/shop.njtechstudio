import React from 'react';

export default function Badge({
  children,
  variant = 'neutral',
  className = '',
  size = 'md',
}) {
  const variants = {
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    warning: 'bg-orange-50 text-orange-700 border-orange-200',
    error: 'bg-red-50 text-red-700 border-red-200',
    neutral: 'bg-slate-50 text-slate-600 border-slate-200',
    primary: 'bg-slate-900 text-white border-slate-900',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-[10px] font-bold',
    md: 'px-2.5 py-1.5 text-xs font-semibold',
    lg: 'px-3 py-2 text-sm font-semibold',
  };

  const baseClasses = `border rounded-lg inline-flex items-center gap-1`;

  return (
    <span className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}>
      {children}
    </span>
  );
}
