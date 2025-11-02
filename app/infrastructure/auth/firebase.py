"""
Firebase Authentication integration for BloomSkin.

Handles Firebase Auth token verification while user data is stored in PostgreSQL.
"""
from typing import Optional
import os

import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import UnauthorizedException

# Security scheme for Bearer token
security = HTTPBearer()

# Initialize Firebase Admin SDK
_firebase_initialized = False


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK with credentials."""
    global _firebase_initialized

    if _firebase_initialized:
        return

    try:
        # Check if running on Cloud Run (uses Application Default Credentials)
        if os.getenv("K_SERVICE"):
            logger.info("Running on Cloud Run, using Application Default Credentials")
            firebase_admin.initialize_app(
                options={"projectId": settings.FIREBASE_PROJECT_ID}
            )
        # Check if credentials file exists
        elif os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            logger.info(f"Using Firebase credentials from {settings.FIREBASE_CREDENTIALS_PATH}")
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(
                cred, {"projectId": settings.FIREBASE_PROJECT_ID}
            )
        else:
            logger.warning(
                f"Firebase credentials file not found at {settings.FIREBASE_CREDENTIALS_PATH}. "
                "Attempting to use Application Default Credentials."
            )
            # Try using default credentials anyway
            firebase_admin.initialize_app(
                options={"projectId": settings.FIREBASE_PROJECT_ID}
            )

        _firebase_initialized = True
        logger.info("Firebase Admin SDK initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        raise


async def verify_firebase_token(token: str) -> dict:
    """
    Verify Firebase ID token and return decoded token.

    Args:
        token: Firebase ID token from client

    Returns:
        Decoded token containing user info

    Raises:
        UnauthorizedException: If token is invalid
    """
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(token)
        return decoded_token

    except auth.InvalidIdTokenError:
        logger.warning("Invalid Firebase ID token")
        raise UnauthorizedException("Invalid authentication token")

    except auth.ExpiredIdTokenError:
        logger.warning("Expired Firebase ID token")
        raise UnauthorizedException("Authentication token has expired")

    except auth.RevokedIdTokenError:
        logger.warning("Revoked Firebase ID token")
        raise UnauthorizedException("Authentication token has been revoked")

    except Exception as e:
        logger.error(f"Error verifying Firebase token: {e}")
        raise UnauthorizedException("Failed to verify authentication token")


async def get_current_user_firebase_uid(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """
    Dependency to get current user's Firebase UID from Bearer token.

    Usage in endpoints:
        @router.get("/me")
        async def get_me(firebase_uid: str = Depends(get_current_user_firebase_uid)):
            # Use firebase_uid to fetch user from database
            pass

    Args:
        credentials: HTTP Bearer token from request header

    Returns:
        Firebase UID of authenticated user

    Raises:
        UnauthorizedException: If token is invalid
    """
    if not credentials:
        raise UnauthorizedException("Authentication credentials not provided")

    token = credentials.credentials
    decoded_token = await verify_firebase_token(token)

    firebase_uid = decoded_token.get("uid")
    if not firebase_uid:
        raise UnauthorizedException("Invalid token: missing user ID")

    return firebase_uid


async def get_firebase_user_info(firebase_uid: str) -> Optional[dict]:
    """
    Get user information from Firebase Auth.

    Args:
        firebase_uid: Firebase UID

    Returns:
        User information dictionary or None if not found
    """
    try:
        user = auth.get_user(firebase_uid)
        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "photo_url": user.photo_url,
            "email_verified": user.email_verified,
            "disabled": user.disabled,
        }
    except auth.UserNotFoundError:
        logger.warning(f"Firebase user not found: {firebase_uid}")
        return None
    except Exception as e:
        logger.error(f"Error fetching Firebase user info: {e}")
        return None


async def create_firebase_custom_token(firebase_uid: str, additional_claims: Optional[dict] = None) -> str:
    """
    Create a custom Firebase token for a user.

    Useful for admin operations or testing.

    Args:
        firebase_uid: Firebase UID
        additional_claims: Optional additional claims to include in token

    Returns:
        Custom Firebase token
    """
    try:
        token = auth.create_custom_token(firebase_uid, additional_claims)
        return token.decode("utf-8")
    except Exception as e:
        logger.error(f"Error creating custom token: {e}")
        raise


async def revoke_firebase_tokens(firebase_uid: str) -> None:
    """
    Revoke all refresh tokens for a user.

    Args:
        firebase_uid: Firebase UID
    """
    try:
        auth.revoke_refresh_tokens(firebase_uid)
        logger.info(f"Revoked refresh tokens for user: {firebase_uid}")
    except Exception as e:
        logger.error(f"Error revoking tokens: {e}")
        raise


async def delete_firebase_user(firebase_uid: str) -> None:
    """
    Delete a user from Firebase Auth.

    Args:
        firebase_uid: Firebase UID
    """
    try:
        auth.delete_user(firebase_uid)
        logger.info(f"Deleted Firebase user: {firebase_uid}")
    except Exception as e:
        logger.error(f"Error deleting Firebase user: {e}")
        raise
