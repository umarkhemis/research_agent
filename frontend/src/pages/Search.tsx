import React, { useState } from 'react';
import { Search as SearchIcon, Filter, X } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import { papersApi } from '../api/papers';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Loading } from '../components/common/Loading';
import toast from 'react-hot-toast';
import type { Paper } from '../api/types';

export const Search: React.FC = () => {
  const [query, setQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    limit: 10,
    yearFrom: '',
    yearTo: '',
    databases: ['semantic_scholar', 'arxiv'],
    openAccessOnly: false,
  });
  const [results, setResults] = useState<Paper[]>([]);

  const searchMutation = useMutation({
    mutationFn: papersApi.search,
    onSuccess: (data) => {
      setResults(data.papers);
      toast.success(`Found ${data.count} papers in ${data.duration.toFixed(2)}s`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Search failed');
    },
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }
    
    searchMutation.mutate({
      query,
      limit: filters.limit,
      year_from: filters.yearFrom ? parseInt(filters.yearFrom) : undefined,
      year_to: filters.yearTo ? parseInt(filters.yearTo) : undefined,
      databases: filters.databases,
      open_access_only: filters.openAccessOnly,
    });
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text mb-2">Search Papers</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Search across Semantic Scholar and ArXiv databases
        </p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="flex gap-2">
          <div className="flex-1">
            <Input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter search query (e.g., 'machine learning transformers')"
              icon={<SearchIcon className="w-5 h-5" />}
            />
          </div>
          <Button
            type="button"
            variant="outline"
            icon={<Filter className="w-5 h-5" />}
            onClick={() => setShowFilters(!showFilters)}
          >
            Filters
          </Button>
          <Button
            type="submit"
            loading={searchMutation.isPending}
            icon={<SearchIcon className="w-5 h-5" />}
          >
            Search
          </Button>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                Search Filters
              </h3>
              <button
                type="button"
                onClick={() => setShowFilters(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                type="number"
                label="Results Limit"
                value={filters.limit}
                onChange={(e) => setFilters({ ...filters, limit: parseInt(e.target.value) || 10 })}
                min="1"
                max="50"
              />
              <div className="flex gap-2">
                <Input
                  type="number"
                  label="Year From"
                  value={filters.yearFrom}
                  onChange={(e) => setFilters({ ...filters, yearFrom: e.target.value })}
                  placeholder="2020"
                />
                <Input
                  type="number"
                  label="Year To"
                  value={filters.yearTo}
                  onChange={(e) => setFilters({ ...filters, yearTo: e.target.value })}
                  placeholder="2024"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Databases
              </label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.databases.includes('semantic_scholar')}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFilters({
                          ...filters,
                          databases: [...filters.databases, 'semantic_scholar'],
                        });
                      } else {
                        setFilters({
                          ...filters,
                          databases: filters.databases.filter((d) => d !== 'semantic_scholar'),
                        });
                      }
                    }}
                    className="rounded text-primary focus:ring-primary"
                  />
                  <span className="text-gray-700 dark:text-gray-300">Semantic Scholar</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.databases.includes('arxiv')}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFilters({
                          ...filters,
                          databases: [...filters.databases, 'arxiv'],
                        });
                      } else {
                        setFilters({
                          ...filters,
                          databases: filters.databases.filter((d) => d !== 'arxiv'),
                        });
                      }
                    }}
                    className="rounded text-primary focus:ring-primary"
                  />
                  <span className="text-gray-700 dark:text-gray-300">ArXiv</span>
                </label>
              </div>
            </div>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.openAccessOnly}
                onChange={(e) => setFilters({ ...filters, openAccessOnly: e.target.checked })}
                className="rounded text-primary focus:ring-primary"
              />
              <span className="text-gray-700 dark:text-gray-300">Open Access Only</span>
            </label>
          </div>
        )}
      </form>

      {/* Loading State */}
      {searchMutation.isPending && <Loading text="Searching papers..." />}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Results ({results.length})
          </h2>
          <div className="grid gap-4">
            {results.map((paper) => (
              <div
                key={paper.id}
                className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow"
              >
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  {paper.title}
                </h3>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  {paper.authors.slice(0, 3).join(', ')}
                  {paper.authors.length > 3 && ' et al.'}
                  {' • '}
                  {paper.year}
                  {paper.venue && ` • ${paper.venue}`}
                </div>
                {paper.abstract && (
                  <p className="text-gray-700 dark:text-gray-300 mb-4 line-clamp-3">
                    {paper.abstract}
                  </p>
                )}
                <div className="flex items-center gap-4 flex-wrap">
                  <span className="text-sm px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">
                    {paper.citation_count} citations
                  </span>
                  {paper.has_pdf && (
                    <span className="text-sm px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full">
                      PDF Available
                    </span>
                  )}
                  <span className="text-sm px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full">
                    {paper.source}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Results */}
      {!searchMutation.isPending && results.length === 0 && query && (
        <div className="text-center py-12">
          <SearchIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            No papers found. Try adjusting your search query or filters.
          </p>
        </div>
      )}

      {/* Empty State */}
      {!query && results.length === 0 && (
        <div className="text-center py-12">
          <SearchIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            Enter a search query to find academic papers
          </p>
        </div>
      )}
    </div>
  );
};
