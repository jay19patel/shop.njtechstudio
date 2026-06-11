import React from 'react';

export default function Textarea({
  placeholder = '',
  value = '',
  onChange = () => {},
  disabled = false,
  className = '',
  error = false,
  label = '',
  rows = 4,
  ...props
}) {
  const baseClasses = `
    w-full bg-slate-50 border rounded-lg py-2 px-3 text-sm
    outline-none focus:border-slate-400 focus:bg-white transition-all
    ${error ? 'border-red-300 focus:border-red-400' : 'border-slate-200'}
    ${disabled ? 'bg-slate-100 cursor-not-allowed opacity-60' : ''}
    resize-none
  `;

  return (
    <div className="w-full">
      {label && (
        <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
          {label}
        </label>
      )}
      <textarea
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        rows={rows}
        className={`${baseClasses} ${className}`}
        {...props}
      />
      {error && (
        <p className="text-xs text-red-600 mt-1">{error}</p>
      )}
    </div>
  );
}
