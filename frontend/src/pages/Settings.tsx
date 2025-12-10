import React from 'react';
import { Moon, Sun, Info, Database, Zap } from 'lucide-react';
import { useThemeStore } from '../store';
import { Button } from '../components/common/Button';

export const Settings: React.FC = () => {
  const { isDark, toggleTheme } = useThemeStore();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text mb-2">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Manage your application preferences
        </p>
      </div>

      {/* Appearance Section */}
      <div className="card-3d glass-effect bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-primary/10 rounded-lg">
            {isDark ? <Moon className="w-5 h-5 text-primary" /> : <Sun className="w-5 h-5 text-primary" />}
          </div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Appearance
          </h2>
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100">Theme</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Choose your preferred color theme
              </p>
            </div>
            <Button
              variant="outline"
              icon={isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              onClick={toggleTheme}
            >
              {isDark ? 'Light Mode' : 'Dark Mode'}
            </Button>
          </div>
        </div>
      </div>

      {/* Performance Section */}
      <div className="card-3d glass-effect bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Zap className="w-5 h-5 text-primary" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Performance
          </h2>
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100">Cache Status</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Results are cached for faster access
              </p>
            </div>
            <span className="text-sm px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full">
              Enabled
            </span>
          </div>
        </div>
      </div>

      {/* Database Section */}
      <div className="card-3d glass-effect bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Database className="w-5 h-5 text-primary" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Data Sources
          </h2>
        </div>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100">Semantic Scholar</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Academic paper database
              </p>
            </div>
            <span className="text-sm px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full">
              Connected
            </span>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100">ArXiv</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Preprint repository
              </p>
            </div>
            <span className="text-sm px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full">
              Connected
            </span>
          </div>
        </div>
      </div>

      {/* About Section */}
      <div className="card-3d glass-effect bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Info className="w-5 h-5 text-primary" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            About ResearchHub Pro
          </h2>
        </div>
        
        <div className="space-y-3 text-gray-700 dark:text-gray-300">
          <p>
            <strong>Version:</strong> 2.0.0
          </p>
          <p>
            ResearchHub Pro is an AI-powered academic research assistant that helps you search,
            organize, and analyze academic papers from multiple databases.
          </p>
          <p>
            <strong>Features:</strong>
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2 text-sm">
            <li>Multi-database paper search (Semantic Scholar, ArXiv)</li>
            <li>AI-powered summarization and analysis</li>
            <li>Project-based paper organization</li>
            <li>Automated literature review generation</li>
            <li>Multiple export formats</li>
          </ul>
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <a
              href="https://github.com/umarkhemis/research_agent"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              View on GitHub →
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
