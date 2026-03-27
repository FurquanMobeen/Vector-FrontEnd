'use client';

import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ImageRotator } from '@/components/ImageRotator';
import { apiClient } from '@/lib/api';
import { Upload, Loader2, RefreshCcw, Download, Trash2 } from 'lucide-react';
import type { ImageData } from '@/lib/types';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';

const VECTOR_SEARCH_API_URL = process.env.NEXT_PUBLIC_VECTOR_SEARCH_API_URL || 'http://localhost:8001';

export default function ManageImagesPage() {
  // Upload state
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadPreview, setUploadPreview] = useState('');
  const [uploadRotation, setUploadRotation] = useState(0);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadDescription, setUploadDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const uploadInputRef = useRef<HTMLInputElement>(null);

  // Manage state
  const [allImages, setAllImages] = useState<ImageData[]>([]);
  const [isLoadingImages, setIsLoadingImages] = useState(false);
  const [searchFilter, setSearchFilter] = useState('');
  const [selectedImage, setSelectedImage] = useState<ImageData | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Export state
  const [exportScope, setExportScope] = useState<'all' | 'selected'>('all');

  useEffect(() => {
    loadImages();
  }, []);

  useEffect(() => {
    if (selectedImage) {
      setEditTitle(selectedImage.title);
      setEditDescription(selectedImage.description);
    }
  }, [selectedImage]);

  const loadImages = async () => {
    setIsLoadingImages(true);
    try {
      const images = await apiClient.getAllImages();
      setAllImages(images);
    } catch (error) {
      console.error('Failed to load images:', error);
      alert('Failed to load images. Please ensure the backend API is running.');
    } finally {
      setIsLoadingImages(false);
    }
  };

  const handleUploadFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadFile(file);
      const url = URL.createObjectURL(file);
      setUploadPreview(url);
      setUploadRotation(0);
    }
  };

  const handleUpload = async () => {
    if (!uploadFile || !uploadTitle.trim() || !uploadDescription.trim()) {
      alert('Please provide an image, title, and description');
      return;
    }

    setIsUploading(true);
    try {
      let fileToUpload = uploadFile;

      if (uploadRotation !== 0) {
        const rotatedBlob = await rotateImage(uploadFile, uploadRotation);
        fileToUpload = new File([rotatedBlob], uploadFile.name, { type: uploadFile.type });
      }

      await apiClient.uploadImage({
        image: fileToUpload,
        title: uploadTitle,
        description: uploadDescription,
      });

      alert('Image uploaded successfully!');
      // Clear form
      setUploadFile(null);
      setUploadPreview('');
      setUploadRotation(0);
      setUploadTitle('');
      setUploadDescription('');
      if (uploadInputRef.current) {
        uploadInputRef.current.value = '';
      }
      // Reload images list
      await loadImages();
    } catch (error: any) {
      console.error('Upload error:', error);
      alert(error?.response?.data?.detail || 'Failed to upload image');
    } finally {
      setIsUploading(false);
    }
  };

  const handleUpdateMetadata = async () => {
    if (!selectedImage || !editTitle.trim() || !editDescription.trim()) {
      alert('Please provide both title and description');
      return;
    }

    setIsUpdating(true);
    try {
      await apiClient.updateMetadata({
        image_path: selectedImage.path,
        title: editTitle,
        description: editDescription,
      });

      alert('Metadata updated successfully!');
      await loadImages();
      // Update selected image
      setSelectedImage({
        ...selectedImage,
        title: editTitle,
        description: editDescription,
      });
    } catch (error: any) {
      console.error('Update error:', error);
      alert(error?.response?.data?.detail || 'Failed to update metadata');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedImage) return;

    setIsDeleting(true);
    try {
      await apiClient.deleteImage(selectedImage.path);
      alert('Image deleted successfully!');
      setSelectedImage(null);
      await loadImages();
    } catch (error: any) {
      console.error('Delete error:', error);
      alert(error?.response?.data?.detail || 'Failed to delete image');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleExport = async () => {
    try {
      const imagePath = exportScope === 'selected' ? selectedImage?.path : undefined;
      const metadata = await apiClient.exportMetadata(imagePath);

      const json = JSON.stringify(metadata, null, 2);
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = exportScope === 'all' ? 'all_metadata.json' : `${selectedImage?.title || 'image'}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      alert('Metadata exported successfully!');
    } catch (error: any) {
      console.error('Export error:', error);
      alert(error?.response?.data?.detail || 'Failed to export metadata');
    }
  };

  const rotateImage = (file: File, degrees: number): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      const img = new globalThis.Image();
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

  const filteredImages = allImages.filter((img) =>
    img.title.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold gradient-text mb-2">Manage Images</h1>
        <p className="text-muted-foreground">
          Upload new images, edit metadata, and manage your collection
        </p>
      </div>

      {/* Upload Section */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Upload Image to Database</h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="space-y-4">
            <Card>
              <CardContent className="p-6 space-y-4">
                <div>
                  <Label htmlFor="upload-image">Upload Image</Label>
                  <div className="mt-2">
                    <input
                      ref={uploadInputRef}
                      id="upload-image"
                      type="file"
                      accept="image/jpeg,image/jpg,image/png,image/gif,image/bmp"
                      onChange={handleUploadFileSelect}
                      className="hidden"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      className="w-full"
                      onClick={() => uploadInputRef.current?.click()}
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      Choose Image
                    </Button>
                  </div>
                </div>

                {uploadPreview && (
                  <ImageRotator
                    imageUrl={uploadPreview}
                    onRotationChange={setUploadRotation}
                  />
                )}
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-2">
            <Card>
              <CardContent className="p-6 space-y-4">
                <h3 className="font-medium">Image Details</h3>

                <div className="space-y-2">
                  <Label htmlFor="upload-title">Title *</Label>
                  <Input
                    id="upload-title"
                    placeholder="Enter a title"
                    value={uploadTitle}
                    onChange={(e) => setUploadTitle(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="upload-description">Description *</Label>
                  <Textarea
                    id="upload-description"
                    placeholder="Enter a description"
                    value={uploadDescription}
                    onChange={(e) => setUploadDescription(e.target.value)}
                    rows={4}
                  />
                </div>

                <Button
                  className="w-full"
                  onClick={handleUpload}
                  disabled={!uploadFile || !uploadTitle || !uploadDescription || isUploading}
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Add Image
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <div className="h-px bg-border" />

      {/* Manage Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Select Image to Manage</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={loadImages}
            disabled={isLoadingImages}
          >
            <RefreshCcw className={`h-4 w-4 mr-2 ${isLoadingImages ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Select Section */}
          <div className="space-y-4">
            <Card>
              <CardContent className="p-6 space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="search">Search Images</Label>
                  <Input
                    id="search"
                    placeholder="Filter by title..."
                    value={searchFilter}
                    onChange={(e) => setSearchFilter(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Select Image ({filteredImages.length} images)</Label>
                  <div className="max-h-[400px] overflow-y-auto border border-border rounded-md">
                    {filteredImages.map((img) => (
                      <button
                        key={img.path}
                        onClick={() => setSelectedImage(img)}
                        className={`w-full text-left p-3 hover:bg-muted transition-colors border-b border-border last:border-0 ${
                          selectedImage?.path === img.path ? 'bg-muted' : ''
                        }`}
                      >
                        <p className="font-medium text-sm truncate">{img.title}</p>
                        <p className="text-xs text-muted-foreground truncate">{img.path}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {selectedImage && (
                  <>
                    <div className="h-px bg-border" />

                    <div className="space-y-4">
                      <h3 className="font-medium">Edit Metadata</h3>

                      <div className="space-y-2">
                        <Label htmlFor="edit-title">Title</Label>
                        <Input
                          id="edit-title"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="edit-description">Description</Label>
                        <Textarea
                          id="edit-description"
                          value={editDescription}
                          onChange={(e) => setEditDescription(e.target.value)}
                          rows={3}
                        />
                      </div>

                      <Button
                        className="w-full"
                        onClick={handleUpdateMetadata}
                        disabled={isUpdating}
                      >
                        {isUpdating ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Updating...
                          </>
                        ) : (
                          'Update Metadata'
                        )}
                      </Button>
                    </div>

                    <div className="h-px bg-border" />

                    <div className="space-y-4">
                      <h3 className="font-medium text-destructive">Delete Image</h3>
                      <p className="text-sm text-muted-foreground">
                        This will permanently remove the image from the database and delete it from disk.
                      </p>

                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button variant="destructive" className="w-full">
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete from Database
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                            <AlertDialogDescription>
                              This action cannot be undone. This will permanently delete "{selectedImage.title}" from the database and remove the file from disk.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction
                              onClick={handleDelete}
                              disabled={isDeleting}
                              className="bg-destructive hover:bg-destructive/90"
                            >
                              {isDeleting ? 'Deleting...' : 'Delete'}
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Preview Section */}
          <div className="lg:col-span-2 space-y-4">
            <Card>
              <CardContent className="p-6 space-y-4">
                <h3 className="font-medium">Preview</h3>

                {selectedImage ? (
                  <div className="space-y-4">
                    <div className="relative aspect-square bg-muted rounded-lg overflow-hidden">
                      <Image
                        src={`${VECTOR_SEARCH_API_URL}/static/${selectedImage.path}`}
                        alt={selectedImage.title}
                        fill
                        className="object-contain"
                        sizes="(max-width: 768px) 100vw, 600px"
                      />
                    </div>

                    <div className="bg-muted/50 border border-border rounded-lg p-4 space-y-2">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Title</p>
                        <p className="text-foreground">{selectedImage.title}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Description</p>
                        <p className="text-foreground">{selectedImage.description}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Path</p>
                        <p className="text-xs text-muted-foreground font-mono">{selectedImage.path}</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                    <p className="text-muted-foreground">Select an image to preview</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Export Section */}
            <Card>
              <CardContent className="p-6 space-y-4">
                <h3 className="font-medium">Export Metadata</h3>

                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="export-scope"
                      value="all"
                      checked={exportScope === 'all'}
                      onChange={() => setExportScope('all')}
                      className="accent-primary"
                    />
                    <span className="text-sm">All Images</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="export-scope"
                      value="selected"
                      checked={exportScope === 'selected'}
                      onChange={() => setExportScope('selected')}
                      disabled={!selectedImage}
                      className="accent-primary"
                    />
                    <span className="text-sm">Selected Image Only</span>
                  </label>
                </div>

                <p className="text-sm text-muted-foreground">
                  {exportScope === 'all'
                    ? 'Export all image metadata to a JSON file for backup or external use.'
                    : 'Export metadata for the currently selected image only.'}
                </p>

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={handleExport}
                  disabled={exportScope === 'selected' && !selectedImage}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export to JSON
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
