'use client';

interface ProcessingIndicatorProps {
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
  message?: string;
}

/**
 * Material Design 3 Processing Indicator
 * 
 * Shows circular progress with status message
 */
export default function ProcessingIndicator({ status, message }: ProcessingIndicatorProps) {
  if (status === 'idle' || status === 'completed') {
    return null;
  }

  const statusMessages = {
    uploading: 'Uploading image...',
    processing: 'Removing watermark...',
    error: 'Processing failed',
  };

  const displayMessage = message || statusMessages[status as keyof typeof statusMessages];

  return (
    <div className="flex flex-col items-center justify-center py-8">
      {/* Circular Progress Indicator */}
      {status !== 'error' && (
        <div className="relative w-16 h-16 mb-4">
          <svg
            className="animate-spin"
            style={{ color: 'var(--md-sys-color-primary)' }}
            viewBox="0 0 24 24"
            fill="none"
            aria-label="Loading"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        </div>
      )}

      {/* Error Icon */}
      {status === 'error' && (
        <div className="w-16 h-16 mb-4 flex items-center justify-center">
          <svg
            className="w-full h-full"
            style={{ color: 'var(--md-sys-color-error)' }}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-label="Error"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
      )}

      {/* Status Message */}
      <p
        className="title-medium text-center"
        style={{
          color:
            status === 'error'
              ? 'var(--md-sys-color-error)'
              : 'var(--md-sys-color-on-surface)',
        }}
      >
        {displayMessage}
      </p>

      {/* Progress Bar (optional) */}
      {status === 'processing' && (
        <div
          className="mt-4 w-64 h-1 overflow-hidden"
          style={{
            backgroundColor: 'var(--md-sys-color-surface-container-high)',
            borderRadius: 'var(--md-sys-shape-corner-full)',
          }}
        >
          <div
            className="h-full animate-pulse"
            style={{
              backgroundColor: 'var(--md-sys-color-primary)',
              width: '60%',
            }}
          />
        </div>
      )}
    </div>
  );
}
