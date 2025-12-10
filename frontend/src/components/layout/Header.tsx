import React from 'react';
import { Moon, Sun, Search, Settings } from 'lucide-react';
import { useThemeStore } from '../../store';
import { Button } from '../common/Button';
import { useNavigate } from 'react-router-dom';

export const Header: React.FC = () => {
  const { isDark, toggleTheme } = useThemeStore();
  const navigate = useNavigate();
  
  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div
            onClick={() => navigate('/')}
            className="flex items-center gap-2 cursor-pointer"
          >
            <div className="text-3xl">🔬</div>
            <h1 className="text-2xl font-bold gradient-text">
              ResearchHub Pro
            </h1>
          </div>
          
          {/* Actions */}
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              icon={<Search className="w-5 h-5" />}
              onClick={() => navigate('/search')}
            />
            <Button
              variant="ghost"
              size="sm"
              icon={<Settings className="w-5 h-5" />}
              onClick={() => navigate('/settings')}
            />
            <Button
              variant="ghost"
              size="sm"
              icon={isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              onClick={toggleTheme}
            />
          </div>
        </div>
      </div>
    </header>
  );
};
