"""Cloudflare Turnstile verification service"""

import httpx

from ..core.config import get_settings
from ..core.exceptions import TurnstileError
from ..core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class TurnstileService:
    """Service for verifying Cloudflare Turnstile tokens"""

    def __init__(self):
        self.secret_key = settings.turnstile_secret_key
        self.verify_url = settings.turnstile_verify_url

    async def verify_token(self, token: str, client_ip: str | None = None) -> dict:
        """
        Verify a Turnstile token with Cloudflare API

        Args:
            token: Turnstile token from frontend
            client_ip: Optional client IP address for additional validation

        Returns:
            Dictionary with verification result

        Raises:
            TurnstileError: If verification fails
        """
        if not self.secret_key:
            logger.warning("Turnstile secret key not configured, skipping verification")
            # In development, allow bypass if secret key not set
            if settings.app_env == "development":
                return {"success": True, "bypass": True}
            raise TurnstileError(
                "Turnstile verification not configured",
                details={"error": "missing_secret_key"},
            )

        # Prepare request payload
        payload = {
            "secret": self.secret_key,
            "response": token,
        }
        if client_ip:
            payload["remoteip"] = client_ip

        logger.info(
            "Verifying Turnstile token",
            extra={"ip_address": client_ip or "unknown"},
        )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.verify_url, data=payload)
                response.raise_for_status()
                result = response.json()

            # Check verification result
            if not result.get("success"):
                error_codes = result.get("error-codes", [])
                logger.warning(
                    "Turnstile verification failed",
                    extra={
                        "error_codes": error_codes,
                        "ip_address": client_ip or "unknown",
                    },
                )
                raise TurnstileError(
                    "Turnstile verification failed",
                    details={
                        "error_codes": error_codes,
                        "message": self._get_error_message(error_codes),
                    },
                )

            logger.info(
                "Turnstile verification successful",
                extra={
                    "hostname": result.get("hostname"),
                    "challenge_ts": result.get("challenge_ts"),
                },
            )

            return result

        except httpx.HTTPError as e:
            logger.error(f"Failed to verify Turnstile token: {e}")
            raise TurnstileError(
                "Failed to verify Turnstile token",
                details={"error": str(e)},
            )

    def _get_error_message(self, error_codes: list[str]) -> str:
        """
        Get human-readable error message from Cloudflare error codes

        Args:
            error_codes: List of error codes from Turnstile API

        Returns:
            Human-readable error message
        """
        error_messages = {
            "missing-input-secret": "Server configuration error",
            "invalid-input-secret": "Server configuration error",
            "missing-input-response": "Verification token is missing",
            "invalid-input-response": "Verification token is invalid or expired",
            "bad-request": "Invalid verification request",
            "timeout-or-duplicate": "Token has expired or was already used",
        }

        # Return first known error message, or generic message
        for code in error_codes:
            if code in error_messages:
                return error_messages[code]

        return "Verification failed"


# Singleton instance
turnstile_service = TurnstileService()
