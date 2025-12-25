"""File validation utilities"""

import mimetypes
from pathlib import Path

from PIL import Image

from ..core.config import get_settings
from ..core.exceptions import ValidationError
from ..core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class FileValidator:
    """Validate uploaded files"""

    def __init__(self):
        self.max_size_bytes = settings.max_file_size_mb * 1024 * 1024
        self.allowed_extensions = settings.allowed_extensions

    def validate_file_size(self, file_size: int) -> None:
        """
        Validate file size is within limits

        Args:
            file_size: File size in bytes

        Raises:
            ValidationError: If file size exceeds maximum
        """
        if file_size > self.max_size_bytes:
            raise ValidationError(
                f"File size exceeds maximum limit of {settings.max_file_size_mb}MB",
                details={
                    "max_size_mb": settings.max_file_size_mb,
                    "received_size_mb": round(file_size / (1024 * 1024), 2),
                },
            )

    def validate_file_extension(self, filename: str) -> None:
        """
        Validate file has an allowed extension

        Args:
            filename: Name of the file

        Raises:
            ValidationError: If extension is not allowed
        """
        extension = Path(filename).suffix.lower().lstrip(".")
        if extension not in self.allowed_extensions:
            raise ValidationError(
                f"File extension '{extension}' not allowed",
                details={
                    "allowed_extensions": self.allowed_extensions,
                    "received_extension": extension,
                },
            )

    def validate_mime_type(self, file_path: str) -> None:
        """
        Validate file MIME type matches expected image types

        Args:
            file_path: Path to the file

        Raises:
            ValidationError: If MIME type is not an image
        """
        mime_type, _ = mimetypes.guess_type(file_path)

        if not mime_type or not mime_type.startswith("image/"):
            raise ValidationError(
                "File is not a valid image",
                details={"mime_type": mime_type or "unknown"},
            )

    def validate_image_format(self, file_path: str) -> dict[str, any]:
        """
        Validate file is a valid image and extract metadata

        Args:
            file_path: Path to the image file

        Returns:
            Dictionary with image metadata (format, width, height, mode)

        Raises:
            ValidationError: If file is not a valid image
        """
        try:
            with Image.open(file_path) as img:
                metadata = {
                    "format": img.format,
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode,
                }

                logger.info(
                    "Image validated",
                    extra={"metadata": metadata},
                )

                return metadata

        except Exception as e:
            raise ValidationError(
                "Failed to read image file",
                details={"error": str(e)},
            )

    def validate_file(self, file_path: str, file_size: int, filename: str) -> dict[str, any]:
        """
        Perform comprehensive file validation

        Args:
            file_path: Path to the file
            file_size: File size in bytes
            filename: Original filename

        Returns:
            Dictionary with validation results and image metadata

        Raises:
            ValidationError: If any validation fails
        """
        # Validate size
        self.validate_file_size(file_size)

        # Validate extension
        self.validate_file_extension(filename)

        # Validate MIME type
        self.validate_mime_type(file_path)

        # Validate image format and get metadata
        metadata = self.validate_image_format(file_path)

        return {
            "valid": True,
            "filename": filename,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "metadata": metadata,
        }
