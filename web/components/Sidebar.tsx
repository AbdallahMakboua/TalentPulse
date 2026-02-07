'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_ITEMS = [
  { href: '/', label: 'Org Overview', icon: '🏠' },
  { href: '/teams', label: 'Teams', icon: '🏢' },
  { href: '/employees', label: 'Employees', icon: '👥' },
  { href: '/settings', label: 'Settings', icon: '⚙️' },
  { href: '/transparency', label: 'Transparency', icon: '🔒' },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-white border-r border-slate-200 flex flex-col z-10">
      {/* Logo */}
      <div className="p-6 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-pulse-500 to-pulse-700 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg">
            T
          </div>
          <div>
            <h1 className="font-bold text-slate-900 text-lg leading-tight">TalentPulse</h1>
            <p className="text-xs text-slate-400">AI Performance Intelligence</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-pulse-50 text-pulse-700 border border-pulse-100'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-100">
        <div className="bg-green-50 p-3 rounded-lg">
          <div className="flex items-center gap-2 text-xs text-green-700 font-medium">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            Privacy-First Mode Active
          </div>
          <p className="text-xs text-green-600 mt-1">No content data collected</p>
        </div>
      </div>
    </aside>
  );
}
