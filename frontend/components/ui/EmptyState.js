import React from 'react';

export default function EmptyState({
  icon: Icon,
  title = 'No items found',
  description = '',
  action = null,
}) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4">
      {Icon && (
        <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-6">
          <Icon className="w-8 h-8 text-slate-300" />
        </div>
      )}
      <h3 className="text-lg font-bold text-slate-800 mb-2">{title}</h3>
      {description && (
        <p className="text-slate-500 text-sm text-center max-w-sm mb-6">
          {description}
        </p>
      )}
      {action && <div>{action}</div>}
    </div>
  );
}
