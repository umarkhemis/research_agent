import React, { useState } from 'react';
import { FolderOpen, Plus, Edit, Trash2 } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '../api/projects';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Modal } from '../components/common/Modal';
import { Loading } from '../components/common/Loading';
import toast from 'react-hot-toast';

export const Projects: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<any>(null);
  const [formData, setFormData] = useState({ name: '', description: '', tags: '' });
  const queryClient = useQueryClient();

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: projectsApi.list,
  });

  const createMutation = useMutation({
    mutationFn: projectsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast.success('Project created successfully');
      setIsCreateModalOpen(false);
      setFormData({ name: '', description: '', tags: '' });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create project');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => projectsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast.success('Project updated successfully');
      setEditingProject(null);
      setFormData({ name: '', description: '', tags: '' });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to update project');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: projectsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast.success('Project deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to delete project');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      toast.error('Project name is required');
      return;
    }

    const tags = formData.tags
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);

    if (editingProject) {
      updateMutation.mutate({
        id: editingProject.id,
        data: {
          name: formData.name,
          description: formData.description,
          tags,
        },
      });
    } else {
      createMutation.mutate({
        name: formData.name,
        description: formData.description,
        tags,
      });
    }
  };

  const handleEdit = (project: any) => {
    setEditingProject(project);
    setFormData({
      name: project.name,
      description: project.description || '',
      tags: project.tags?.join(', ') || '',
    });
  };

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Are you sure you want to delete "${name}"?`)) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) {
    return <Loading text="Loading projects..." />;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Projects</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Organize your research papers into projects
          </p>
        </div>
        <Button
          icon={<Plus className="w-5 h-5" />}
          onClick={() => {
            setFormData({ name: '', description: '', tags: '' });
            setIsCreateModalOpen(true);
          }}
        >
          New Project
        </Button>
      </div>

      {/* Projects Grid */}
      {projects && projects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div
              key={project.id}
              className="card-3d shine-effect bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <FolderOpen className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                      {project.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {project.papers_count} papers
                    </p>
                  </div>
                </div>
                <div className="flex gap-1">
                  <button
                    onClick={() => handleEdit(project)}
                    className="p-2 text-gray-400 hover:text-primary transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(project.id, project.name)}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {project.description && (
                <p className="text-gray-700 dark:text-gray-300 text-sm mb-4 line-clamp-2">
                  {project.description}
                </p>
              )}

              {project.tags && project.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {project.tags.slice(0, 3).map((tag: string, idx: number) => (
                    <span
                      key={idx}
                      className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                  {project.tags.length > 3 && (
                    <span className="text-xs px-2 py-1 text-gray-500">
                      +{project.tags.length - 3} more
                    </span>
                  )}
                </div>
              )}

              <div className="text-xs text-gray-500 dark:text-gray-400">
                Updated {new Date(project.updated_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <FolderOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            No projects yet. Create your first project to get started.
          </p>
          <Button
            icon={<Plus className="w-5 h-5" />}
            onClick={() => setIsCreateModalOpen(true)}
          >
            Create Project
          </Button>
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isCreateModalOpen || editingProject !== null}
        onClose={() => {
          setIsCreateModalOpen(false);
          setEditingProject(null);
          setFormData({ name: '', description: '', tags: '' });
        }}
        title={editingProject ? 'Edit Project' : 'Create Project'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Project Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="My Research Project"
            required
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Project description..."
              rows={4}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 
                bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                focus:ring-2 focus:ring-primary focus:border-transparent
                placeholder-gray-400 dark:placeholder-gray-500"
            />
          </div>
          <Input
            label="Tags (comma-separated)"
            value={formData.tags}
            onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
            placeholder="machine learning, nlp, transformers"
          />
          <div className="flex gap-2 justify-end">
            <Button
              type="button"
              variant="ghost"
              onClick={() => {
                setIsCreateModalOpen(false);
                setEditingProject(null);
                setFormData({ name: '', description: '', tags: '' });
              }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              loading={createMutation.isPending || updateMutation.isPending}
            >
              {editingProject ? 'Update' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
