'use client';

import { useState } from 'react';
import ImagePreview from '../components/ImagePreview';
import ProcessingIndicator from '../components/ProcessingIndicator';
import TurnstileWidget from '../components/TurnstileWidget';
import UploadZone from '../components/UploadZone';

type ProcessingStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';

interface ProcessingResult {
  imageDataUrl: string;
  originalFilename: string;
  watermarkSize?: string;
  processingTime?: number;
}

export default function HomePage() {
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [status, setStatus] = useState<ProcessingStatus>('idle');
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const turnstileSiteKey = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY || '';
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const handleTurnstileVerify = (token: string) => {
    setTurnstileToken(token);
    setError(null);
  };

  const handleTurnstileError = (errorMessage: string) => {
    setError(errorMessage);
    setTurnstileToken(null);
  };

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setError(null);

    // Auto-upload if Turnstile is verified
    if (turnstileToken) {
      await processImage(file, turnstileToken);
    }
  };

  const processImage = async (file: File, token: string) => {
    setStatus('uploading');
    setError(null);

    try {
      // Create FormData
      const formData = new FormData();
      formData.append('file', file);
      formData.append('turnstile_token', token);

      setStatus('processing');

      // Call API
      const response = await fetch(`${apiUrl}/api/v1/remove-watermark`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Processing failed');
      }

      const data = await response.json();

      // Convert base64 to data URL
      const imageDataUrl = `data:image/png;base64,${data.processed_image_base64}`;

      setResult({
        imageDataUrl,
        originalFilename: data.original_filename,
        watermarkSize: data.watermark_size,
        processingTime: data.duration_ms,
      });

      setStatus('completed');
    } catch (err) {
      console.error('Processing error:', err);
      setError(err instanceof Error ? err.message : 'Failed to process image');
      setStatus('error');
    }
  };

  const handleDownload = () => {
    if (!result) return;

    // Create download link
    const link = document.createElement('a');
    link.href = result.imageDataUrl;
    link.download = `cleaned_${result.originalFilename}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleReset = () => {
    setSelectedFile(null);
    setStatus('idle');
    setResult(null);
    setError(null);
    setTurnstileToken(null);
  };

  return (
    <main className="min-h-screen p-8" style={{ backgroundColor: 'var(--md-sys-color-surface)' }}>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="headline-large mb-4" style={{ color: 'var(--md-sys-color-on-surface)' }}>
            GeminiWatermarkTool
          </h1>
          <p className="body-large" style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
            Remove Gemini watermarks from your images in seconds
          </p>
        </header>

        {/* Upload Section with Conditional Turnstile Overlay */}
        {status === 'idle' && (
          <section>
            <h2 className="title-large mb-4" style={{ color: 'var(--md-sys-color-on-surface)' }}>
              Upload your image
            </h2>
            
            {/* Show Turnstile verification overlay if not verified */}
            {!turnstileToken ? (
              <div
                className="p-8 rounded-large surface-container-high flex flex-col items-center justify-center min-h-[300px]"
                style={{
                  backgroundColor: 'var(--md-sys-color-surface-container-high)',
                  borderRadius: 'var(--md-sys-shape-corner-large)',
                }}
              >
                <p className="body-large mb-6 text-center" style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
                  Please verify you're human to continue
                </p>
                {turnstileSiteKey ? (
                  <TurnstileWidget
                    siteKey={turnstileSiteKey}
                    onVerify={handleTurnstileVerify}
                    onError={handleTurnstileError}
                  />
                ) : (
                  <p className="body-medium text-center" style={{ color: 'var(--md-sys-color-error)' }}>
                    Turnstile not configured. Set NEXT_PUBLIC_TURNSTILE_SITE_KEY environment variable.
                  </p>
                )}
              </div>
            ) : (
              /* Show upload zone once verified */
              <UploadZone
                onFileSelect={handleFileSelect}
                maxSizeMB={10}
                disabled={false}
              />
            )}
          </section>
        )}

        {/* Processing State */}
        {(status === 'uploading' || status === 'processing') && (
          <ProcessingIndicator status={status} />
        )}

        {/* Error State */}
        {status === 'error' && (
          <div>
            <ProcessingIndicator status="error" message={error || undefined} />
            <div className="flex justify-center mt-6">
              <button
                onClick={handleReset}
                className="px-6 py-3 rounded-full label-large"
                style={{
                  backgroundColor: 'var(--md-sys-color-primary)',
                  color: 'var(--md-sys-color-on-primary)',
                  borderRadius: 'var(--md-sys-shape-corner-full)',
                }}
              >
                Try Again
              </button>
            </div>
          </div>
        )}

        {/* Success State */}
        {status === 'completed' && result && (
          <div>
            <ImagePreview
              imageDataUrl={result.imageDataUrl}
              originalFilename={result.originalFilename}
              onDownload={handleDownload}
              watermarkSize={result.watermarkSize}
              processingTime={result.processingTime}
            />

            <div className="flex justify-center mt-6">
              <button
                onClick={handleReset}
                className="px-6 py-3 rounded-full label-large"
                style={{
                  backgroundColor: 'var(--md-sys-color-secondary)',
                  color: 'var(--md-sys-color-on-secondary)',
                  borderRadius: 'var(--md-sys-shape-corner-full)',
                }}
              >
                Process Another Image
              </button>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-16 text-center">
          <p className="body-small" style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
            Powered by GeminiWatermarkTool • All processing done securely • Files deleted after 1 hour
          </p>
        </footer>
      </div>
    </main>
  );
}
