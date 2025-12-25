'use client';

import { useCallback, useState } from 'react';

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  maxSizeMB?: number;
  acceptedFormats?: string[];
  disabled?: boolean;
}

/**
 * Drag-and-Drop Upload Zone Component
 * 
 * Provides drag-and-drop and click-to-upload functionality
 */
export default function UploadZone({
  onFileSelect,
  maxSizeMB = 10,
  acceptedFormats = ['image/jpeg', 'image/png', 'image/webp', 'image/bmp'],
  disabled = false,
}: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): boolean => {
    setError(null);

    // Check file type
    if (!acceptedFormats.includes(file.type)) {
      setError(`Invalid file type. Accepted: ${acceptedFormats.map(f => f.split('/')[1].toUpperCase()).join(', ')}`);
      return false;
    }

    // Check file size
    const sizeMB = file.size / (1024 * 1024);
    if (sizeMB > maxSizeMB) {
      setError(`File too large. Maximum size: ${maxSizeMB}MB (received: ${sizeMB.toFixed(2)}MB)`);
      return false;
    }

    return true;
  };

  const handleFile = (file: File) => {
    if (validateFile(file)) {
      onFileSelect(file);
    }
  };

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      if (disabled) return;

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        handleFile(files[0]);
      }
    },
    [disabled]
  );

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleClick = () => {
    if (disabled) return;
    document.getElementById('file-input')?.click();
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  return (
    <div className="w-full">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
        className={`
          relative border-2 border-dashed rounded-large p-12
          transition-all duration-200 cursor-pointer
          ${isDragging ? 'border-primary bg-primary/5' : 'border-outline-variant'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-primary hover:bg-surface-container-high'}
        `}
        style={{
          borderRadius: 'var(--md-sys-shape-corner-large)',
          borderColor: isDragging ? 'var(--md-sys-color-primary)' : 'var(--md-sys-color-outline-variant)',
          backgroundColor: isDragging ? 'var(--md-sys-color-primary-container)' : 'transparent',
        }}
        role="button"
        aria-label="Upload image file"
        tabIndex={disabled ? -1 : 0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            handleClick();
          }
        }}
      >
        <input
          id="file-input"
          type="file"
          accept={acceptedFormats.join(',')}
          onChange={handleFileInput}
          className="hidden"
          disabled={disabled}
          aria-label="File input"
        />

        <div className="flex flex-col items-center justify-center text-center">
          <svg
            className="w-16 h-16 mb-4"
            style={{ color: 'var(--md-sys-color-on-surface-variant)' }}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>

          <p className="title-large mb-2" style={{ color: 'var(--md-sys-color-on-surface)' }}>
            {isDragging ? 'Drop image here' : 'Drag & drop your image'}
          </p>

          <p className="body-medium mb-4" style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
            or click to browse
          </p>

          <p className="body-small" style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
            Supported: JPG, PNG, WebP, BMP • Max {maxSizeMB}MB
          </p>
        </div>
      </div>

      {error && (
        <div
          className="mt-4 p-4 rounded-medium"
          style={{
            backgroundColor: 'var(--md-sys-color-error-container)',
            color: 'var(--md-sys-color-on-error-container)',
            borderRadius: 'var(--md-sys-shape-corner-medium)',
          }}
          role="alert"
        >
          <p className="body-medium">{error}</p>
        </div>
      )}
    </div>
  );
}
