import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { FolderOpen, FileText, Search as SearchIcon, BookOpen } from 'lucide-react';
import { statisticsApi } from '../api/statistics';
import { Loading } from '../components/common/Loading';
import { Button } from '../components/common/Button';
import { useNavigate } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: statisticsApi.getDashboard,
  });
  
  if (isLoading) {
    return <Loading text="Loading dashboard..." />;
  }
  
  const statCards = [
    {
      title: 'Projects',
      value: stats?.counts.projects || 0,
      icon: FolderOpen,
      color: 'from-blue-500 to-blue-600',
      onClick: () => navigate('/projects'),
    },
    {
      title: 'Papers',
      value: stats?.counts.papers || 0,
      icon: FileText,
      color: 'from-green-500 to-green-600',
    },
    {
      title: 'Searches',
      value: stats?.counts.searches || 0,
      icon: SearchIcon,
      color: 'from-purple-500 to-purple-600',
      onClick: () => navigate('/search'),
    },
    {
      title: 'Reviews',
      value: stats?.counts.reviews || 0,
      icon: BookOpen,
      color: 'from-pink-500 to-pink-600',
      onClick: () => navigate('/literature-review'),
    },
  ];
  
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-5xl font-bold gradient-text">
          Welcome to ResearchHub Pro
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Your intelligent research assistant powered by AI
        </p>
        <div className="flex gap-4 justify-center mt-6">
          <Button
            variant="primary"
            size="lg"
            icon={<SearchIcon className="w-5 h-5" />}
            onClick={() => navigate('/search')}
          >
            Search Papers
          </Button>
          <Button
            variant="outline"
            size="lg"
            icon={<FolderOpen className="w-5 h-5" />}
            onClick={() => navigate('/projects')}
          >
            My Projects
          </Button>
        </div>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => (
          <div
            key={stat.title}
            onClick={stat.onClick}
            className={`bg-gradient-to-br ${stat.color} rounded-xl p-6 text-white shadow-lg ${
              stat.onClick ? 'cursor-pointer hover:scale-105' : ''
            } transition-transform`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/80 text-sm font-medium">
                  {stat.title}
                </p>
                <p className="text-3xl font-bold mt-2">{stat.value}</p>
              </div>
              <stat.icon className="w-12 h-12 text-white/50" />
            </div>
          </div>
        ))}
      </div>
      
      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Projects */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">
            Recent Projects
          </h2>
          {stats?.recent.projects && stats.recent.projects.length > 0 ? (
            <div className="space-y-3">
              {stats.recent.projects.slice(0, 5).map((project) => (
                <div
                  key={project.id}
                  onClick={() => navigate(`/projects/${project.id}`)}
                  className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer transition-colors"
                >
                  <h3 className="font-medium text-gray-900 dark:text-gray-100">
                    {project.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {project.papers_count} papers
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-center py-8">
              No projects yet. Create your first project!
            </p>
          )}
        </div>
        
        {/* Recent Papers */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">
            Recent Papers
          </h2>
          {stats?.recent.papers && stats.recent.papers.length > 0 ? (
            <div className="space-y-3">
              {stats.recent.papers.slice(0, 5).map((paper) => (
                <div
                  key={paper.id}
                  className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <h3 className="font-medium text-gray-900 dark:text-gray-100 line-clamp-2">
                    {paper.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {paper.authors?.slice(0, 3).join(', ')} • {paper.year}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-center py-8">
              No papers yet. Start searching!
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
