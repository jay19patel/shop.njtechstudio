import React from 'react';

export default function SectionHeader({
  title,
  count = null,
  action = null,
}) {
  return (
    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-4 border-b border-slate-100">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-bold text-slate-900">{title}</h2>
        {count !== null && (
          <span className="text-xs text-slate-400 bg-slate-50 border border-slate-100 px-2 py-0.5 rounded-md">
            {count}
          </span>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}
