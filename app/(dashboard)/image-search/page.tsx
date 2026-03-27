'use client';

import { useState, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { ImageRotator } from '@/components/ImageRotator';
import { ImageGrid } from '@/components/ImageGrid';
import { Pagination } from '@/components/Pagination';
import { apiClient } from '@/lib/api';
import { Upload, Search, Loader2 } from 'lucide-react';
import type { SearchResult } from '@/lib/types';

const RESULTS_PER_PAGE = 9;

export default function ImageSearchPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [rotation, setRotation] = useState(0);
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [currentPage, setCurrentPage] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setImagePreview(url);
      setRotation(0);
      // Clear previous results when new image is selected
      setSearchResults([]);
      setCurrentPage(0);
    }
  };

  const handleClearImage = () => {
    setSelectedFile(null);
    setImagePreview('');
    setRotation(0);
    setSearchResults([]);
    setCurrentPage(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSearch = async () => {
    if (!selectedFile) return;

    setIsSearching(true);
    try {
      // If image is rotated, we need to create a rotated version
      let fileToUpload = selectedFile;

      if (rotation !== 0) {
        // Create rotated image
        const rotatedBlob = await rotateImage(selectedFile, rotation);
        fileToUpload = new File([rotatedBlob], selectedFile.name, { type: selectedFile.type });
      }

      const results = await apiClient.searchByImage(fileToUpload);
      setSearchResults(results);
      setCurrentPage(0);
    } catch (error: any) {
      console.error('Search error:', error);
      alert(error?.response?.data?.detail || 'Failed to search. Please ensure the backend API is running.');
    } finally {
      setIsSearching(false);
    }
  };

  const rotateImage = (file: File, degrees: number): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          reject(new Error('Failed to get canvas context'));
          return;
        }

        const radians = (degrees * Math.PI) / 180;
        const sin = Math.abs(Math.sin(radians));
        const cos = Math.abs(Math.cos(radians));

        canvas.width = img.height * sin + img.width * cos;
        canvas.height = img.height * cos + img.width * sin;

        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate(radians);
        ctx.drawImage(img, -img.width / 2, -img.height / 2);

        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob);
            } else {
              reject(new Error('Failed to create blob'));
            }
          },
          file.type,
          0.95
        );
      };
      img.onerror = reject;
      img.src = URL.createObjectURL(file);
    });
  };

  const totalPages = Math.ceil(searchResults.length / RESULTS_PER_PAGE);
  const paginatedResults = searchResults.slice(
    currentPage * RESULTS_PER_PAGE,
    (currentPage + 1) * RESULTS_PER_PAGE
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold gradient-text mb-2">Image Search</h1>
        <p className="text-muted-foreground">
          Upload an image to find visually similar images in the database
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Section */}
        <div className="space-y-4">
          <Card>
            <CardContent className="p-6 space-y-4">
              <div>
                <Label htmlFor="image-upload">Upload Image</Label>
                <div className="mt-2">
                  <input
                    ref={fileInputRef}
                    id="image-upload"
                    type="file"
                    accept="image/jpeg,image/jpg,image/png,image/gif,image/bmp"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    className="w-full"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Choose Image
                  </Button>
                </div>
              </div>

              {imagePreview && (
                <>
                  <ImageRotator
                    imageUrl={imagePreview}
                    onRotationChange={setRotation}
                  />

                  <div className="space-y-2">
                    <Button
                      className="w-full"
                      onClick={handleSearch}
                      disabled={isSearching}
                    >
                      {isSearching ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Searching...
                        </>
                      ) : (
                        <>
                          <Search className="h-4 w-4 mr-2" />
                          Search by Image
                        </>
                      )}
                    </Button>

                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={handleClearImage}
                    >
                      Clear
                    </Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Results Section */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-semibold">Similar Images</h2>

          {searchResults.length === 0 && !isSearching && (
            <div className="text-center py-12 text-muted-foreground">
              Upload an image and click "Search by Image" to see results
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
