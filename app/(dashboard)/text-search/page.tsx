'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ImageGrid } from '@/components/ImageGrid';
import { Pagination } from '@/components/Pagination';
import { apiClient } from '@/lib/api';
import { Search, Loader2 } from 'lucide-react';
import type { SearchResult } from '@/lib/types';

const RESULTS_PER_PAGE = 9;

export default function TextSearchPage() {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [currentPage, setCurrentPage] = useState(0);

  const handleSearch = async () => {
    if (!query.trim()) {
      alert('Please enter a search query');
      return;
    }

    setIsSearching(true);
    try {
      const results = await apiClient.searchByText(query);
      setSearchResults(results);
      setCurrentPage(0);
    } catch (error: any) {
      console.error('Search error:', error);
      alert(error?.response?.data?.detail || 'Failed to search. Please ensure the backend API is running.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleClear = () => {
    setQuery('');
    setSearchResults([]);
    setCurrentPage(0);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSearch();
    }
  };

  const totalPages = Math.ceil(searchResults.length / RESULTS_PER_PAGE);
  const paginatedResults = searchResults.slice(
    currentPage * RESULTS_PER_PAGE,
    (currentPage + 1) * RESULTS_PER_PAGE
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold gradient-text mb-2">Text Search</h1>
        <p className="text-muted-foreground">
          Describe what you're looking for and find matching images using AI
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Search Input Section */}
        <div className="space-y-4">
          <Card>
            <CardContent className="p-6 space-y-4">
              <div className="space-y-2">
                <Label htmlFor="query">Search Query</Label>
                <Textarea
                  id="query"
                  placeholder="Enter a description (e.g., 'golden retriever', 'beach sunset', 'pizza')..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyPress}
                  rows={6}
                  className="resize-none"
                />
                <p className="text-xs text-muted-foreground">
                  Press Ctrl+Enter to search
                </p>
              </div>

              <div className="space-y-2">
                <Button
                  className="w-full"
                  onClick={handleSearch}
                  disabled={isSearching || !query.trim()}
                >
                  {isSearching ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="h-4 w-4 mr-2" />
                      Search by Text
                    </>
                  )}
                </Button>

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={handleClear}
                  disabled={isSearching}
                >
                  Clear
                </Button>
              </div>

              {/* Example Queries */}
              <div className="pt-4 border-t border-border">
                <p className="text-sm font-medium mb-2">Example queries:</p>
                <div className="space-y-1">
                  {['cute cat', 'sunset over mountains', 'red sports car', 'pizza with pepperoni'].map((example) => (
                    <button
                      key={example}
                      onClick={() => setQuery(example)}
                      className="block w-full text-left text-xs text-muted-foreground hover:text-primary transition-colors px-2 py-1 rounded hover:bg-muted"
                    >
                      "{example}"
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Results Section */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-semibold">Similar Images</h2>

          {searchResults.length === 0 && !isSearching && (
            <div className="text-center py-12 text-muted-foreground">
              Enter a text query and click "Search by Text" to see results
            </div>
          )}

          {isSearching && <ImageGrid results={[]} isLoading={true} />}

          {!isSearching && searchResults.length > 0 && (
            <>
              <ImageGrid results={paginatedResults} />
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
