'use client';

import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Image as ImageIcon, FileText, Settings, ArrowRight } from 'lucide-react';

export default function HomePage() {
  const features = [
    {
      title: 'Image Search',
      description: 'Upload an image to find visually similar images in your database. Perfect for finding duplicates, similar styles, or related content.',
      icon: ImageIcon,
      href: '/image-search',
      gradient: 'from-purple-500 to-pink-500',
    },
    {
      title: 'Text Search',
      description: 'Describe what you\'re looking for in words and find matching images. Uses AI to understand semantic meaning, not just keywords.',
      icon: FileText,
      href: '/text-search',
      gradient: 'from-pink-500 to-purple-500',
    },
    {
      title: 'Manage Images',
      description: 'Browse your image database, edit metadata, upload new images, and manage your collection with ease.',
      icon: Settings,
      href: '/manage-images',
      gradient: 'from-purple-600 to-pink-600',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-5xl font-bold gradient-text">
          CLIP Vector Search
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          AI-powered image search using CLIP embeddings. Search by image or text to find visually similar content.
        </p>
      </div>

      <div className="h-px bg-border" />

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Link key={feature.href} href={feature.href}>
              <Card className="h-full hover:border-primary transition-all duration-300 hover:shadow-lg hover:shadow-primary/20 group cursor-pointer">
                <CardHeader>
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="flex items-center justify-between">
                    {feature.title}
                    <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                  </CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            </Link>
          );
        })}
      </div>

      {/* Info Section */}
      <div className="bg-muted/50 border border-border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-2">How it works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-muted-foreground">
          <div>
            <p className="font-medium text-foreground mb-1">1. CLIP Embeddings</p>
            <p>Images are encoded into high-dimensional vectors using OpenAI's CLIP model</p>
          </div>
          <div>
            <p className="font-medium text-foreground mb-1">2. Vector Database</p>
            <p>Embeddings are stored in ChromaDB for efficient similarity search</p>
          </div>
          <div>
            <p className="font-medium text-foreground mb-1">3. Semantic Search</p>
            <p>Search by image or text to find visually and semantically similar content</p>
          </div>
        </div>
      </div>
    </div>
  );
}
