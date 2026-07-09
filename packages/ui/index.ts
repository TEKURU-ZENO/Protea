import React from 'react';

// Shared UI components placeholder
export function StatusBadge({ status }: { status: 'online' | 'offline' | 'loading' }) {
  const colors = {
    online: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    offline: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    loading: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  };

  return React.createElement(
    'span',
    {
      className: `px-2 py-0.5 rounded text-xs font-mono font-medium border ${colors[status]}`,
    },
    status.toUpperCase()
  );
}

export function PanelCard({ title, children }: { title: string; children: React.ReactNode }) {
  return React.createElement(
    'div',
    {
      className: 'bg-slate-900 border border-slate-800 rounded-lg p-4 shadow-xl',
    },
    [
      React.createElement(
        'h3',
        { key: 'title', className: 'text-sm font-semibold text-slate-200 mb-2 font-mono' },
        title
      ),
      React.createElement('div', { key: 'content' }, children),
    ]
  );
}
