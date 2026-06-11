import React from 'react';

export default function Input({
  placeholder = '',
  value = '',
  onChange = () => {},
  type = 'text',
  disabled = false,
  className = '',
  error = false,
  label = '',
  icon: Icon = null,
  ...props
}) {
  const baseClasses = `
    w-full bg-slate-50 border rounded-lg py-2 px-3 text-sm
    outline-none focus:border-slate-400 focus:bg-white transition-all
    ${Icon ? 'pl-9' : 'pl-3'}
    ${error ? 'border-red-300 focus:border-red-400' : 'border-slate-200'}
    ${disabled ? 'bg-slate-100 cursor-not-allowed opacity-60' : ''}
  `;

  return (
    <div className="w-full">
      {label && (
        <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
        )}
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          disabled={disabled}
          className={`${baseClasses} ${className}`}
          {...props}
        />
      </div>
      {error && (
        <p className="text-xs text-red-600 mt-1">{error}</p>
      )}
    </div>
  );
}
