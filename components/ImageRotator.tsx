'use client';

import { useState } from 'react';
import Image from 'next/image';
import { RotateCcw, RotateCw, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';

interface ImageRotatorProps {
  imageUrl: string;
  onRotationChange?: (angle: number) => void;
}

export function ImageRotator({ imageUrl, onRotationChange }: ImageRotatorProps) {
  const [rotation, setRotation] = useState(0);

  const rotateLeft = () => {
    const newRotation = (rotation + 90) % 360;
    setRotation(newRotation);
    onRotationChange?.(newRotation);
  };

  const rotateRight = () => {
    const newRotation = (rotation - 90 + 360) % 360;
    setRotation(newRotation);
    onRotationChange?.(newRotation);
  };

  const resetRotation = () => {
    setRotation(0);
    onRotationChange?.(0);
  };

  return (
    <div className="space-y-3">
      <div className="relative aspect-square bg-muted rounded-lg overflow-hidden">
        <Image
          src={imageUrl}
          alt="Preview"
          fill
          className="object-contain"
          style={{ transform: `rotate(${rotation}deg)` }}
          sizes="(max-width: 768px) 100vw, 500px"
        />
      </div>

      <div className="grid grid-cols-3 gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={rotateLeft}
          className="w-full"
        >
          <RotateCcw className="h-4 w-4 mr-1" />
          90°
        </Button>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={resetRotation}
          className="w-full"
        >
          <RefreshCw className="h-4 w-4 mr-1" />
          Reset
        </Button>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={rotateRight}
          className="w-full"
        >
          <RotateCw className="h-4 w-4 mr-1" />
          90°
        </Button>
      </div>
    </div>
  );
}
