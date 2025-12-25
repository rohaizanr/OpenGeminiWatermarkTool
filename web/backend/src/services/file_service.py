"""File service for managing ephemeral uploads and outputs"""

import asyncio
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from ..core.config import get_settings
from ..core.exceptions import FileNotFoundError
from ..core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class FileService:
    """Manage ephemeral file storage"""

    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.output_dir = Path(settings.output_dir)
        self.retention_hours = settings.ephemeral_retention_hours

        # Ensure directories exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_filename(self, original_filename: str) -> tuple[str, str]:
        """
        Generate a unique filename with UUID prefix

        Args:
            original_filename: Original uploaded filename

        Returns:
            Tuple of (unique_filename, file_extension)
        """
        file_uuid = str(uuid.uuid4())
        extension = Path(original_filename).suffix
        unique_filename = f"{file_uuid}{extension}"

        return unique_filename, extension

    async def save_upload(self, file_content: bytes, filename: str) -> dict[str, str]:
        """
        Save uploaded file to ephemeral storage

        Args:
            file_content: File content as bytes
            filename: Original filename

        Returns:
            Dictionary with file paths and identifiers
        """
        unique_filename, extension = self.generate_filename(filename)
        file_path = self.upload_dir / unique_filename

        # Write file asynchronously
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, file_path.write_bytes, file_content)

        logger.info(
            "File uploaded",
            extra={
                "original_filename": filename,
                "unique_filename": unique_filename,
                "size_bytes": len(file_content),
            },
        )

        return {
            "file_id": str(uuid.uuid4())[:8],  # Short ID for tracking
            "filename": unique_filename,
            "path": str(file_path),
            "original_filename": filename,
            "size_bytes": len(file_content),
        }

    def get_output_path(self, input_filename: str) -> str:
        """
        Generate output file path for processed image

        Args:
            input_filename: Input filename (with UUID)

        Returns:
            Full path to output file
        """
        # Keep same filename, different directory
        output_path = self.output_dir / input_filename
        return str(output_path)

    async def get_file(self, filename: str, from_output: bool = False) -> bytes:
        """
        Retrieve file content

        Args:
            filename: Filename to retrieve
            from_output: If True, look in output directory; otherwise upload directory

        Returns:
            File content as bytes

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        directory = self.output_dir if from_output else self.upload_dir
        file_path = directory / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {filename}",
                details={"file_name": filename, "directory": str(directory)},
            )

        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, file_path.read_bytes)

        return content

    async def delete_file(self, filename: str, from_output: bool = False) -> None:
        """
        Delete a file from storage

        Args:
            filename: Filename to delete
            from_output: If True, delete from output directory; otherwise upload directory
        """
        directory = self.output_dir if from_output else self.upload_dir
        file_path = directory / filename

        if file_path.exists():
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, file_path.unlink)
            logger.info(f"File deleted: {filename}")

    async def cleanup_old_files(self) -> dict[str, int]:
        """
        Clean up files older than retention period

        Returns:
            Dictionary with cleanup statistics
        """
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        deleted_count = {"uploads": 0, "outputs": 0}

        for directory_name, directory_path in [
            ("uploads", self.upload_dir),
            ("outputs", self.output_dir),
        ]:
            if not directory_path.exists():
                continue

            for file_path in directory_path.iterdir():
                if not file_path.is_file():
                    continue

                # Check file modification time
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

                if file_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count[directory_name] += 1
                        logger.debug(f"Cleaned up old file: {file_path.name}")
                    except Exception as e:
                        logger.warning(f"Failed to delete file {file_path.name}: {e}")

        logger.info(
            "File cleanup completed",
            extra={
                "deleted_uploads": deleted_count["uploads"],
                "deleted_outputs": deleted_count["outputs"],
                "retention_hours": self.retention_hours,
            },
        )

        return deleted_count

    def get_storage_stats(self) -> dict[str, any]:
        """
        Get storage statistics

        Returns:
            Dictionary with storage information
        """
        stats = {
            "upload_dir": str(self.upload_dir),
            "output_dir": str(self.output_dir),
            "upload_count": 0,
            "output_count": 0,
            "total_size_bytes": 0,
        }

        for directory_name, directory_path in [
            ("upload_count", self.upload_dir),
            ("output_count", self.output_dir),
        ]:
            if not directory_path.exists():
                continue

            count = 0
            total_size = 0

            for file_path in directory_path.iterdir():
                if file_path.is_file():
                    count += 1
                    total_size += file_path.stat().st_size

            stats[directory_name] = count
            stats["total_size_bytes"] += total_size

        stats["total_size_mb"] = round(stats["total_size_bytes"] / (1024 * 1024), 2)

        return stats
