import React from 'react';
import { User } from 'lucide-react';

export default function Avatar({
  src = '',
  alt = 'User avatar',
  size = 'md',
  className = '',
}) {
  const sizes = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-10 h-10',
    xl: 'w-12 h-12',
  };

  return (
    <div className={`${sizes[size]} rounded-lg bg-slate-200 flex items-center justify-center overflow-hidden shrink-0 border border-slate-200 ${className}`}>
      {src ? (
        <img
          src={src}
          alt={alt}
          className="w-full h-full object-cover"
          referrerPolicy="no-referrer"
        />
      ) : (
        <User className={`text-slate-600 ${size === 'sm' ? 'w-3 h-3' : size === 'md' ? 'w-4 h-4' : size === 'lg' ? 'w-5 h-5' : 'w-6 h-6'}`} />
      )}
    </div>
  );
}
