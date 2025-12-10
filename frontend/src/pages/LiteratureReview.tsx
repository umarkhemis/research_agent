import React, { useState } from 'react';
import { FileText, Download, BookOpen } from 'lucide-react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { projectsApi } from '../api/projects';
import { literatureReviewApi } from '../api/literatureReview';
import { Button } from '../components/common/Button';
import { Loading } from '../components/common/Loading';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';

export const LiteratureReview: React.FC = () => {
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [reviewType, setReviewType] = useState('thematic');
  const [detailLevel, setDetailLevel] = useState('medium');
  const [customInstructions, setCustomInstructions] = useState('');
  const [generatedReview, setGeneratedReview] = useState<any>(null);

  const { data: projects } = useQuery({
    queryKey: ['projects'],
    queryFn: projectsApi.list,
  });

  const generateMutation = useMutation({
    mutationFn: literatureReviewApi.generate,
    onSuccess: (data) => {
      setGeneratedReview(data);
      toast.success('Literature review generated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to generate review');
    },
  });

  const handleGenerate = () => {
    if (!selectedProjectId) {
      toast.error('Please select a project');
      return;
    }

    generateMutation.mutate({
      project_id: selectedProjectId,
      review_type: reviewType,
      detail_level: detailLevel,
      custom_instructions: customInstructions,
    });
  };

  const handleExport = async (format: string) => {
    if (!generatedReview) return;
    
    try {
      const data = await literatureReviewApi.export(generatedReview.id, format);
      
      // Create a blob and download
      const blob = new Blob([data.content], { 
        type: format === 'latex' ? 'text/plain' : 'text/markdown' 
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${data.title || 'literature-review'}.${format === 'latex' ? 'tex' : 'md'}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success(`Exported as ${format.toUpperCase()}`);
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Export failed');
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text mb-2">Literature Review Generator</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Generate comprehensive literature reviews from your project papers
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Panel */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 space-y-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Configuration
          </h2>

          {/* Project Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Project
            </label>
            <select
              value={selectedProjectId || ''}
              onChange={(e) => setSelectedProjectId(parseInt(e.target.value) || null)}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 
                bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="">Choose a project...</option>
              {projects?.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name} ({project.papers_count} papers)
                </option>
              ))}
            </select>
          </div>

          {/* Review Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Review Type
            </label>
            <div className="space-y-2">
              {[
                { value: 'thematic', label: 'Thematic', desc: 'Organized by research themes' },
                { value: 'chronological', label: 'Chronological', desc: 'Organized by time' },
                { value: 'methodological', label: 'Methodological', desc: 'Organized by methods' },
              ].map((type) => (
                <label key={type.value} className="flex items-start gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="reviewType"
                    value={type.value}
                    checked={reviewType === type.value}
                    onChange={(e) => setReviewType(e.target.value)}
                    className="mt-1 text-primary focus:ring-primary"
                  />
                  <div>
                    <div className="text-gray-700 dark:text-gray-300">{type.label}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">{type.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Detail Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Detail Level
            </label>
            <div className="space-y-2">
              {[
                { value: 'short', label: 'Short', desc: '2-3 pages, concise overview' },
                { value: 'medium', label: 'Medium', desc: '5-10 pages, comprehensive' },
                { value: 'long', label: 'Long', desc: '15-20 pages, thesis-ready' },
              ].map((level) => (
                <label key={level.value} className="flex items-start gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="detailLevel"
                    value={level.value}
                    checked={detailLevel === level.value}
                    onChange={(e) => setDetailLevel(e.target.value)}
                    className="mt-1 text-primary focus:ring-primary"
                  />
                  <div>
                    <div className="text-gray-700 dark:text-gray-300">{level.label}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">{level.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Custom Instructions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Custom Instructions (Optional)
            </label>
            <textarea
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              placeholder="Add any specific requirements or focus areas..."
              rows={4}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 
                bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                focus:ring-2 focus:ring-primary focus:border-transparent
                placeholder-gray-400 dark:placeholder-gray-500"
            />
          </div>

          {/* Generate Button */}
          <Button
            onClick={handleGenerate}
            loading={generateMutation.isPending}
            icon={<FileText className="w-5 h-5" />}
            className="w-full"
          >
            Generate Literature Review
          </Button>
        </div>

        {/* Preview Panel */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Preview
            </h2>
            {generatedReview && (
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  icon={<Download className="w-4 h-4" />}
                  onClick={() => handleExport('markdown')}
                >
                  Markdown
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  icon={<Download className="w-4 h-4" />}
                  onClick={() => handleExport('latex')}
                >
                  LaTeX
                </Button>
              </div>
            )}
          </div>

          {generateMutation.isPending && (
            <Loading text="Generating literature review..." />
          )}

          {generatedReview ? (
            <div className="prose dark:prose-invert max-w-none">
              <ReactMarkdown>{generatedReview.content}</ReactMarkdown>
            </div>
          ) : (
            <div className="text-center py-12">
              <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">
                Configure options and generate a literature review
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
