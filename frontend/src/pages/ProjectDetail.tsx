import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, FileText, Trash2, Download } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '../api/projects';
import { Button } from '../components/common/Button';
import { Loading } from '../components/common/Loading';
import toast from 'react-hot-toast';

export const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const projectId = parseInt(id || '0');

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.get(projectId),
    enabled: !!projectId,
  });

  const { data: papers } = useQuery({
    queryKey: ['project-papers', projectId],
    queryFn: () => projectsApi.getPapers(projectId),
    enabled: !!projectId,
  });

  const removePaperMutation = useMutation({
    mutationFn: (paperId: number) => projectsApi.removePaper(projectId, paperId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project-papers', projectId] });
      toast.success('Paper removed from project');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to remove paper');
    },
  });

  if (isLoading) {
    return <Loading text="Loading project..." />;
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 dark:text-gray-400">Project not found</p>
        <Button onClick={() => navigate('/projects')} className="mt-4">
          Back to Projects
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            icon={<ArrowLeft className="w-5 h-5" />}
            onClick={() => navigate('/projects')}
          >
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold gradient-text">{project.name}</h1>
            {project.description && (
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                {project.description}
              </p>
            )}
          </div>
        </div>
        <Button
          icon={<Download className="w-5 h-5" />}
          onClick={() => navigate('/literature-review')}
        >
          Generate Review
        </Button>
      </div>

      {/* Tags */}
      {Array.isArray(project.tags) && project.tags.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          {project.tags.map((tag, idx) => (
            <span
              key={idx}
              className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card-3d glass-effect bg-white dark:bg-gray-800 rounded-xl p-6">
          <div className="text-3xl font-bold gradient-text">
            {project.papers_count || 0}
          </div>
          <div className="text-gray-600 dark:text-gray-400 mt-2">Papers</div>
        </div>
        <div className="card-3d glass-effect bg-white dark:bg-gray-800 rounded-xl p-6">
          <div className="text-3xl font-bold gradient-text">
            {Array.isArray(papers) ? papers.filter(p => p.notes).length : 0}
          </div>
          <div className="text-gray-600 dark:text-gray-400 mt-2">Papers with Notes</div>
        </div>
        <div className="card-3d glass-effect bg-white dark:bg-gray-800 rounded-xl p-6">
          <div className="text-3xl font-bold gradient-text">
            {new Date(project.updated_at).toLocaleDateString()}
          </div>
          <div className="text-gray-600 dark:text-gray-400 mt-2">Last Updated</div>
        </div>
      </div>

      {/* Papers List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Papers ({Array.isArray(papers) ? papers.length : 0})
          </h2>
          <Button
            icon={<Plus className="w-5 h-5" />}
            onClick={() => navigate('/search')}
          >
            Add Papers
          </Button>
        </div>

        {!papers || papers.length === 0 ? (
          <div className="card-3d glass-effect bg-white dark:bg-gray-800 rounded-xl p-12 text-center">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
              No papers yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Start by searching and adding papers to this project
            </p>
            <Button icon={<Plus className="w-5 h-5" />} onClick={() => navigate('/search')}>
              Search Papers
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {papers.map((projectPaper) => (
              <div
                key={projectPaper.paper.id}
                className="card-3d shine-effect bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                      {projectPaper.paper.title}
                    </h3>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {projectPaper.paper.authors?.slice(0, 3).join(', ')}
                      {projectPaper.paper.authors?.length > 3 && ' et al.'}
                      {projectPaper.paper.year && ` • ${projectPaper.paper.year}`}
                    </div>
                    {projectPaper.notes && (
                      <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          {projectPaper.notes}
                        </p>
                      </div>
                    )}
                    {Array.isArray(projectPaper.tags) && projectPaper.tags.length > 0 && (
                      <div className="flex gap-2 flex-wrap mt-3">
                        {projectPaper.tags.map((tag, idx) => (
                          <span
                            key={idx}
                            className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    icon={<Trash2 className="w-4 h-4" />}
                    onClick={() => removePaperMutation.mutate(projectPaper.paper.id)}
                    loading={removePaperMutation.isPending}
                  >
                    Remove
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
