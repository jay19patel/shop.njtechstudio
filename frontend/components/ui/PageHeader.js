import React from 'react';

export default function PageHeader({
  title,
  subtitle = '',
  actions = null,
  showDivider = true,
}) {
  return (
    <div className={`flex flex-col md:flex-row justify-between items-start md:items-center gap-4 ${showDivider ? 'pb-8 border-b border-slate-200' : ''}`}>
      <div>
        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">
          {subtitle}
        </p>
        <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
      </div>
      {actions && <div className="flex items-center gap-3">{actions}</div>}
    </div>
  );
}
