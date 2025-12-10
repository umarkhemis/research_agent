import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, Search, FolderOpen, FileText, Settings } from 'lucide-react';

const navItems = [
  { to: '/', icon: Home, label: 'Dashboard' },
  { to: '/search', icon: Search, label: 'Search Papers' },
  { to: '/projects', icon: FolderOpen, label: 'Projects' },
  { to: '/literature-review', icon: FileText, label: 'Literature Review' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 min-h-screen">
      <nav className="p-4 space-y-2">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive
                  ? 'bg-primary text-white'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`
            }
          >
            <Icon className="w-5 h-5" />
            <span className="font-medium">{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};
