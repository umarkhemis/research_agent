import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingProps {
  text?: string;
  fullScreen?: boolean;
}

export const Loading: React.FC<LoadingProps> = ({ text, fullScreen = false }) => {
  const content = (
    <div className="flex flex-col items-center justify-center gap-3">
      <Loader2 className="w-10 h-10 text-primary animate-spin" />
      {text && (
        <p className="text-gray-600 dark:text-gray-400">{text}</p>
      )}
    </div>
  );
  
  if (fullScreen) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm z-50">
        {content}
      </div>
    );
  }
  
  return <div className="flex items-center justify-center p-8">{content}</div>;
};

export const Skeleton: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`animate-pulse bg-gray-200 dark:bg-gray-700 rounded ${className}`} />
  );
};
