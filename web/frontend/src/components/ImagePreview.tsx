'use client';

import Image from 'next/image';
import { useState } from 'react';

interface ImagePreviewProps {
  imageDataUrl: string;
  originalFilename: string;
  onDownload: () => void;
  watermarkSize?: string;
  processingTime?: number;
}

/**
 * Image Preview Component with Download Button
 * 
 * Displays the processed image and provides download functionality
 */
export default function ImagePreview({
  imageDataUrl,
  originalFilename,
  onDownload,
  watermarkSize,
  processingTime,
}: ImagePreviewProps) {
  const [imageLoaded, setImageLoaded] = useState(false);

  return (
    <div className="w-full">
      {/* Success Header */}
      <div
        className="p-4 rounded-medium mb-4"
        style={{
          backgroundColor: 'var(--md-sys-color-surface-container-high)',
          borderRadius: 'var(--md-sys-shape-corner-medium)',
        }}
      >
        <div className="flex items-center mb-2">
          <svg
            className="w-6 h-6 mr-2"
            style={{ color: 'var(--md-sys-color-primary)' }}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
          <h3 className="title-large" style={{ color: 'var(--md-sys-color-on-surface)' }}>
            Watermark Removed Successfully!
          </h3>
        </div>

        {/* Processing Stats */}
        {(watermarkSize || processingTime) && (
          <div className="flex gap-4 mt-2">
            {watermarkSize && (
              <p className="body-small" style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
                Detected: {watermarkSize === 'small_48x48' ? '48×48px' : '96×96px'} watermark
              </p>
            )}
            {processingTime && (
              <p className="body-small" style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
                Processed in {processingTime}ms
              </p>
            )}
          </div>
        )}
      </div>

      {/* Image Preview */}
      <div
        className="relative w-full overflow-hidden elevation-2"
        style={{
          backgroundColor: 'var(--md-sys-color-surface-container)',
          borderRadius: 'var(--md-sys-shape-corner-large)',
          boxShadow: 'var(--md-sys-elevation-level2)',
        }}
      >
        <div className="relative w-full" style={{ minHeight: '400px' }}>
          {!imageLoaded && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="animate-pulse">Loading preview...</div>
            </div>
          )}
          <img
            src={imageDataUrl}
            alt="Processed image without watermark"
            className="w-full h-auto"
            onLoad={() => setImageLoaded(true)}
            style={{ display: imageLoaded ? 'block' : 'none' }}
          />
        </div>
      </div>

      {/* Download Button */}
      <div className="mt-6 flex justify-center">
        <button
          onClick={onDownload}
          className="px-6 py-3 rounded-full label-large transition-all duration-200"
          style={{
            backgroundColor: 'var(--md-sys-color-primary)',
            color: 'var(--md-sys-color-on-primary)',
            borderRadius: 'var(--md-sys-shape-corner-full)',
            boxShadow: 'var(--md-sys-elevation-level1)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.boxShadow = 'var(--md-sys-elevation-level2)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.boxShadow = 'var(--md-sys-elevation-level1)';
          }}
        >
          <div className="flex items-center gap-2">
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            Download Cleaned Image
          </div>
        </button>
      </div>

      {/* Original Filename */}
      <p
        className="body-small text-center mt-4"
        style={{ color: 'var(--md-sys-color-on-surface-variant)' }}
      >
        Original: {originalFilename}
      </p>
    </div>
  );
}
