'use client';

import Image from 'next/image';
import { Card, CardContent } from './ui/card';
import type { SearchResult } from '@/lib/types';

const VECTOR_SEARCH_API_URL = process.env.NEXT_PUBLIC_VECTOR_SEARCH_API_URL || 'http://localhost:8001';

interface ImageGridProps {
  results: SearchResult[];
  isLoading?: boolean;
}

export function ImageGrid({ results, isLoading = false }: ImageGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(9)].map((_, i) => (
          <Card key={i} className="overflow-hidden">
            <div className="aspect-square bg-muted animate-pulse" />
            <CardContent className="p-3">
              <div className="h-4 bg-muted rounded animate-pulse mb-2" />
              <div className="h-3 bg-muted rounded animate-pulse" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No results found</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {results.map((result, index) => (
        <Card key={`${result.path}-${index}`} className="overflow-hidden hover:border-primary transition-colors">
          <div className="relative aspect-square bg-muted">
            <Image
              src={`${VECTOR_SEARCH_API_URL}/static/${result.path}`}
              alt={result.title}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              onError={(e) => {
                // Fallback if image fails to load
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
              }}
            />
          </div>
          <CardContent className="p-3">
            <p className="font-medium text-sm text-foreground truncate mb-1">
              {result.title}
            </p>
            <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
              {result.description}
            </p>
            {result.similarity !== undefined && (
              <p className="text-xs text-primary font-medium">
                Similarity: {(1 - result.similarity).toFixed(4)}
              </p>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
