"""Watermark removal orchestration service"""

import base64
import uuid
from datetime import datetime
from pathlib import Path

from ..api.models import (
    ImageFormat,
    ImageMetadata,
    JobStatus,
    ProcessingJob,
    SingleImageResponse,
    UploadSession,
    WatermarkSize,
)
from ..core.exceptions import ProcessingError, ValidationError
from ..core.logging import get_logger
from ..utils.binary_executor import BinaryExecutor
from ..utils.validators import FileValidator
from .file_service import FileService

logger = get_logger(__name__)


class WatermarkService:
    """Service for orchestrating watermark removal workflow"""

    def __init__(self):
        self.file_service = FileService()
        self.file_validator = FileValidator()
        self.binary_executor = BinaryExecutor()

    async def process_single_image(
        self,
        file_content: bytes,
        filename: str,
        session: UploadSession,
    ) -> SingleImageResponse:
        """
        Process a single image through the watermark removal workflow

        Args:
            file_content: Image file bytes
            filename: Original filename
            session: Upload session context

        Returns:
            SingleImageResponse with processed image

        Raises:
            ValidationError: If file validation fails
            ProcessingError: If image processing fails
        """
        job_id = uuid.uuid4()
        logger.info(
            "Starting image processing",
            extra={
                "job_id": str(job_id),
                "session_id": str(session.session_id),
                "file_name": filename,
            },
        )

        # Step 1: Save uploaded file
        upload_result = await self.file_service.save_upload(file_content, filename)
        input_path = upload_result["path"]

        # Step 2: Validate file
        validation_result = self.file_validator.validate_file(
            input_path, len(file_content), filename
        )

        # Step 3: Extract image metadata
        metadata = self._create_image_metadata(
            job_id, filename, validation_result
        )

        # Step 4: Determine watermark size
        watermark_size = self._detect_watermark_size(
            metadata.width_pixels, metadata.height_pixels
        )

        # Step 5: Create processing job
        output_path = self.file_service.get_output_path(upload_result["filename"])
        job = ProcessingJob(
            job_id=job_id,
            session_id=session.session_id,
            input_file_path=input_path,
            output_file_path=output_path,
            status=JobStatus.PROCESSING,
            started_at=datetime.utcnow(),
            detected_watermark_size=watermark_size,
        )

        try:
            # Step 6: Execute binary
            start_time = datetime.utcnow()
            result = await self.binary_executor.execute(input_path, output_path)

            # Step 7: Update job status
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.duration_ms = int((job.completed_at - start_time).total_seconds() * 1000)
            job.binary_exit_code = result["exit_code"]

            # Step 8: Read processed image and encode to base64
            processed_content = await self.file_service.get_file(
                Path(output_path).name, from_output=True
            )
            processed_base64 = base64.b64encode(processed_content).decode("utf-8")

            logger.info(
                "Image processing completed",
                extra={
                    "job_id": str(job_id),
                    "duration_ms": job.duration_ms,
                    "watermark_size": watermark_size,
                },
            )

            # Step 9: Return response
            return SingleImageResponse(
                job_id=str(job_id),
                status=job.status,
                processed_image_base64=processed_base64,
                original_filename=filename,
                output_filename=Path(output_path).name,
                duration_ms=job.duration_ms,
                watermark_size=watermark_size,
                error=None,
            )

        except Exception as e:
            # Update job status on failure
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.error_message = str(e)

            logger.error(
                f"Image processing failed: {e}",
                extra={"job_id": str(job_id)},
                exc_info=True,
            )

            raise ProcessingError(
                f"Failed to process image: {str(e)}",
                details={"job_id": str(job_id), "error": str(e)},
            )

    def _create_image_metadata(
        self, job_id: uuid.UUID, filename: str, validation_result: dict
    ) -> ImageMetadata:
        """Create ImageMetadata from validation result"""
        metadata_dict = validation_result["metadata"]

        # Map format string to enum
        format_str = metadata_dict["format"].lower()
        if format_str in ["jpg", "jpeg"]:
            image_format = ImageFormat.JPEG
        elif format_str == "png":
            image_format = ImageFormat.PNG
        elif format_str == "webp":
            image_format = ImageFormat.WEBP
        elif format_str == "bmp":
            image_format = ImageFormat.BMP
        else:
            raise ValidationError(f"Unsupported format: {format_str}")

        # Detect watermark size
        watermark_size = self._detect_watermark_size(
            metadata_dict["width"], metadata_dict["height"]
        )

        return ImageMetadata(
            job_id=job_id,
            file_name=filename,
            file_size_bytes=validation_result["size_bytes"],
            file_format=image_format,
            mime_type=f"image/{format_str}",
            width_pixels=metadata_dict["width"],
            height_pixels=metadata_dict["height"],
            has_watermark=True,
            watermark_size=watermark_size,
            watermark_position="bottom-right",
            validation_passed=True,
        )

    def _detect_watermark_size(self, width: int, height: int) -> WatermarkSize:
        """
        Detect watermark size based on image dimensions

        Args:
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            WatermarkSize enum value
        """
        if width <= 1024 or height <= 1024:
            return WatermarkSize.SMALL_48X48
        else:
            return WatermarkSize.LARGE_96X96


# Singleton instance
watermark_service = WatermarkService()
