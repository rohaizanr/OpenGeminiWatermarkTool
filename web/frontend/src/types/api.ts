/**
 * TypeScript type definitions matching OpenAPI schemas
 */

/**
 * Error response from API
 */
export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
}

/**
 * Processing job response
 */
export interface ProcessingJob {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
  original_filename: string;
  output_filename?: string;
  download_url?: string;
  error?: string;
  processing_time_ms?: number;
}

/**
 * Health check response
 */
export interface HealthResponse {
  status: string;
  version: string;
}

/**
 * Readiness check response
 */
export interface ReadinessResponse {
  ready: boolean;
  checks: Record<string, boolean>;
  message?: string;
}

/**
 * File upload metadata
 */
export interface FileMetadata {
  filename: string;
  size_bytes: number;
  size_mb: number;
  format: string;
  width: number;
  height: number;
  mime_type: string;
}

/**
 * Batch processing job (User Story 3)
 */
export interface BatchProcessingJob {
  batch_id: string;
  status: 'queued' | 'processing' | 'completed' | 'partial' | 'failed';
  total_files: number;
  completed_files: number;
  failed_files: number;
  created_at: string;
  completed_at?: string;
  jobs: ProcessingJob[];
}

/**
 * Upload progress callback
 */
export type UploadProgressCallback = (progress: number) => void;

/**
 * Processing status callback
 */
export type StatusCallback = (status: ProcessingJob['status']) => void;
