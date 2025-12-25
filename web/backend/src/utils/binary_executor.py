"""Binary execution utility for running GeminiWatermarkTool"""

import asyncio
import subprocess
from pathlib import Path

from ..core.config import get_settings
from ..core.exceptions import BinaryExecutionError
from ..core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class BinaryExecutor:
    """Wrapper for executing the GeminiWatermarkTool binary"""

    def __init__(self, binary_path: str | None = None, timeout: int | None = None):
        self.binary_path = binary_path or settings.binary_path
        self.timeout = timeout or settings.binary_timeout_seconds

    async def execute(
        self, input_path: str, output_path: str, additional_args: list[str] | None = None
    ) -> dict[str, any]:
        """
        Execute the watermark removal binary

        Args:
            input_path: Path to input image file
            output_path: Path to save output image
            additional_args: Optional additional command-line arguments

        Returns:
            Dictionary with execution results (exit_code, stdout, stderr, success)

        Raises:
            BinaryExecutionError: If binary execution fails
        """
        # Verify binary exists
        if not Path(self.binary_path).is_file():
            raise BinaryExecutionError(
                f"Binary not found at {self.binary_path}",
                details={"binary_path": self.binary_path},
            )

        # Build command with proper flags
        cmd = [
            self.binary_path,
            "-i", input_path,
            "-o", output_path,
            "-r"  # Remove watermark mode
        ]
        if additional_args:
            cmd.extend(additional_args)

        logger.info(
            "Executing binary",
            extra={"command": " ".join(cmd), "timeout": self.timeout},
        )

        try:
            # Execute command with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise BinaryExecutionError(
                    f"Binary execution timed out after {self.timeout} seconds",
                    details={"timeout_seconds": self.timeout},
                )

            exit_code = process.returncode
            stdout_text = stdout.decode("utf-8", errors="replace")
            stderr_text = stderr.decode("utf-8", errors="replace")

            result = {
                "exit_code": exit_code,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "success": exit_code == 0,
            }

            if exit_code != 0:
                logger.error(
                    "Binary execution failed",
                    extra={
                        "exit_code": exit_code,
                        "stderr": stderr_text,
                    },
                )
                raise BinaryExecutionError(
                    f"Binary execution failed with exit code {exit_code}",
                    exit_code=exit_code,
                    details={"stderr": stderr_text, "stdout": stdout_text},
                )

            logger.info(
                "Binary execution successful",
                extra={"exit_code": exit_code},
            )

            return result

        except subprocess.SubprocessError as e:
            raise BinaryExecutionError(
                f"Failed to execute binary: {str(e)}",
                details={"error": str(e)},
            )

    async def verify_binary(self) -> bool:
        """
        Verify that the binary exists and is executable

        Returns:
            True if binary is valid, False otherwise
        """
        binary = Path(self.binary_path)
        if not binary.is_file():
            logger.warning(f"Binary not found: {self.binary_path}")
            return False

        if not binary.stat().st_mode & 0o111:
            logger.warning(f"Binary is not executable: {self.binary_path}")
            return False

        return True

    async def get_version(self) -> str | None:
        """
        Get the binary version

        Returns:
            Version string or None if version check fails
        """
        try:
            process = await asyncio.create_subprocess_exec(
                self.binary_path,
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5)
            version_text = stdout.decode("utf-8", errors="replace").strip()

            return version_text if version_text else None

        except Exception as e:
            logger.warning(f"Failed to get binary version: {e}")
            return None
