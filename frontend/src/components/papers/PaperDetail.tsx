import React, { useState } from 'react';
import { FileText, Download, Sparkles, Search } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import { papersApi } from '../../api/papers';
import { Button } from '../common/Button';
import { Modal } from '../common/Modal';
import { Loading } from '../common/Loading';
import toast from 'react-hot-toast';
import type { Paper } from '../../api/types';

interface PaperDetailProps {
  paper: Paper;
  isOpen: boolean;
  onClose: () => void;
}

export const PaperDetail: React.FC<PaperDetailProps> = ({ paper, isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'abstract' | 'summary' | 'gaps' | 'findings'>('abstract');
  const [summaryLevel, setSummaryLevel] = useState<'short' | 'medium' | 'long'>('medium');
  const [summary, setSummary] = useState<string>('');
  const [gaps, setGaps] = useState<any>(null);
  const [findings, setFindings] = useState<string>('');

  const summarizeMutation = useMutation({
    mutationFn: ({ level, usePdf }: { level: string; usePdf: boolean }) =>
      papersApi.summarize(paper.id, level, usePdf),
    onSuccess: (data) => {
      setSummary(data.summary);
      toast.success('Summary generated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to generate summary');
    },
  });

  const analyzeMutation = useMutation({
    mutationFn: () => papersApi.analyze(paper.id),
    onSuccess: (data) => {
      setGaps(data);
      setFindings(data.key_findings);
      toast.success('Analysis completed');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Analysis failed');
    },
  });

  const downloadPdfMutation = useMutation({
    mutationFn: () => papersApi.downloadPdf(paper.id),
    onSuccess: () => {
      toast.success('PDF downloaded and processed');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to download PDF');
    },
  });

  const handleSummarize = () => {
    summarizeMutation.mutate({ level: summaryLevel, usePdf: false });
  };

  const handleAnalyze = () => {
    analyzeMutation.mutate();
  };

  const tabs = [
    { id: 'abstract' as const, label: 'Abstract', icon: FileText },
    { id: 'summary' as const, label: 'Summary', icon: Sparkles },
    { id: 'gaps' as const, label: 'Research Gaps', icon: Search },
    { id: 'findings' as const, label: 'Key Findings', icon: FileText },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={paper.title} size="xl">
      <div className="space-y-4">
        {/* Paper Metadata */}
        <div className="glass-effect p-4 rounded-lg space-y-2">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            <strong>Authors:</strong> {paper.authors.slice(0, 5).join(', ')}
            {paper.authors.length > 5 && ' et al.'}
          </div>
          <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
            {paper.year && <span><strong>Year:</strong> {paper.year}</span>}
            {paper.venue && <span><strong>Venue:</strong> {paper.venue}</span>}
            <span><strong>Citations:</strong> {paper.citation_count}</span>
          </div>
          <div className="flex gap-2 flex-wrap">
            {paper.has_pdf && (
              <span className="text-xs px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full">
                PDF Available
              </span>
            )}
            <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full">
              {paper.source}
            </span>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-primary'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="min-h-[300px] max-h-[500px] overflow-y-auto">
          {activeTab === 'abstract' && (
            <div className="prose dark:prose-invert max-w-none">
              <p>{paper.abstract || 'No abstract available'}</p>
            </div>
          )}

          {activeTab === 'summary' && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <select
                  value={summaryLevel}
                  onChange={(e) => setSummaryLevel(e.target.value as any)}
                  className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 
                    bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                >
                  <option value="short">Short Summary</option>
                  <option value="medium">Medium Summary</option>
                  <option value="long">Detailed Summary</option>
                </select>
                <Button
                  onClick={handleSummarize}
                  loading={summarizeMutation.isPending}
                  icon={<Sparkles className="w-4 h-4" />}
                  size="sm"
                >
                  Generate
                </Button>
                {paper.has_pdf && (
                  <Button
                    onClick={() => downloadPdfMutation.mutate()}
                    loading={downloadPdfMutation.isPending}
                    variant="outline"
                    icon={<Download className="w-4 h-4" />}
                    size="sm"
                  >
                    Process PDF
                  </Button>
                )}
              </div>

              {summarizeMutation.isPending && <Loading text="Generating summary..." />}

              {summary ? (
                <div className="card-3d p-4 rounded-lg bg-white dark:bg-gray-800">
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{summary}</p>
                </div>
              ) : (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                  Click "Generate" to create an AI summary
                </p>
              )}
            </div>
          )}

          {activeTab === 'gaps' && (
            <div className="space-y-4">
              {!gaps && (
                <div className="text-center py-8">
                  <Button
                    onClick={handleAnalyze}
                    loading={analyzeMutation.isPending}
                    icon={<Search className="w-4 h-4" />}
                  >
                    Analyze Research Gaps
                  </Button>
                </div>
              )}

              {analyzeMutation.isPending && <Loading text="Analyzing paper..." />}

              {gaps && (
                <div className="space-y-4">
                  <div className="card-3d p-4 rounded-lg bg-white dark:bg-gray-800">
                    <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                      Methodology Gaps
                    </h4>
                    <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {gaps.methodology_gaps || 'No methodology gaps identified'}
                    </p>
                  </div>

                  <div className="card-3d p-4 rounded-lg bg-white dark:bg-gray-800">
                    <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                      Knowledge Gaps
                    </h4>
                    <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {gaps.knowledge_gaps || 'No knowledge gaps identified'}
                    </p>
                  </div>

                  <div className="card-3d p-4 rounded-lg bg-white dark:bg-gray-800">
                    <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                      Future Directions
                    </h4>
                    <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {gaps.future_directions || 'No future directions identified'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'findings' && (
            <div className="space-y-4">
              {!findings && !gaps && (
                <div className="text-center py-8">
                  <Button
                    onClick={handleAnalyze}
                    loading={analyzeMutation.isPending}
                    icon={<Search className="w-4 h-4" />}
                  >
                    Extract Key Findings
                  </Button>
                </div>
              )}

              {analyzeMutation.isPending && <Loading text="Extracting findings..." />}

              {findings ? (
                <div className="card-3d p-4 rounded-lg bg-white dark:bg-gray-800">
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{findings}</p>
                </div>
              ) : (
                gaps && (
                  <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                    No findings available. Click "Extract Key Findings" above.
                  </p>
                )
              )}
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
};
