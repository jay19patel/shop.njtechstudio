import React from 'react';

export default function Card({
  children,
  className = '',
  hoverable = false,
  padding = 'md',
}) {
  const paddings = {
    sm: 'p-4',
    md: 'p-5',
    lg: 'p-6',
    none: 'p-0',
  };

  const baseClasses = `
    bg-white border border-slate-200 rounded-xl
    ${hoverable ? 'hover:shadow-md hover:border-slate-300 transition-all' : 'shadow-sm'}
  `;

  return (
    <div className={`${baseClasses} ${paddings[padding]} ${className}`}>
      {children}
    </div>
  );
}
