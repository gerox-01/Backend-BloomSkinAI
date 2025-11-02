"""
Firebase Storage integration for BloomSkin image uploads.
"""
from typing import Optional
import uuid
from datetime import datetime, timedelta
import os

from firebase_admin import storage
from fastapi import UploadFile

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import InternalServerException


class FirebaseStorageService:
    """
    Firebase Storage service for uploading and managing user images.

    Handles:
    - User profile photos
    - Skin analysis images
    - Before/after comparison photos
    """

    def __init__(self):
        """Initialize Firebase Storage bucket."""
        try:
            self.bucket = storage.bucket(settings.FIREBASE_STORAGE_BUCKET)
            logger.info(f"Firebase Storage initialized: {settings.FIREBASE_STORAGE_BUCKET}")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Storage: {e}")
            raise InternalServerException(f"Storage initialization failed: {e}")

    async def upload_profile_photo(
        self,
        file: UploadFile,
        user_id: int
    ) -> str:
        """
        Upload user profile photo to Firebase Storage.

        Args:
            file: Uploaded file from FastAPI
            user_id: User ID for organizing files

        Returns:
            Public URL of uploaded image
        """
        try:
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
            unique_filename = f"photos/{user_id}/photo_{user_id}_{int(datetime.utcnow().timestamp())}.{file_extension}"

            # Upload to Firebase Storage
            blob = self.bucket.blob(unique_filename)

            # Read file content
            content = await file.read()

            # Upload with metadata
            blob.upload_from_string(
                content,
                content_type=file.content_type or 'image/jpeg'
            )

            # Make public
            blob.make_public()

            # Get public URL
            public_url = blob.public_url

            logger.info(f"Uploaded profile photo for user {user_id}: {unique_filename}")
            return public_url

        except Exception as e:
            logger.error(f"Error uploading profile photo: {e}")
            raise InternalServerException(f"Failed to upload profile photo: {e}")

    async def upload_analysis_image(
        self,
        file: UploadFile,
        user_id: int,
        analysis_id: str
    ) -> str:
        """
        Upload skin analysis image to Firebase Storage.

        Args:
            file: Uploaded file from FastAPI
            user_id: User ID for organizing files
            analysis_id: Analysis ID for tracking

        Returns:
            Public URL of uploaded image
        """
        try:
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
            unique_filename = f"acne_analysis/{user_id}/acne_analysis_{user_id}_{int(datetime.utcnow().timestamp())}.{file_extension}"

            # Upload to Firebase Storage
            blob = self.bucket.blob(unique_filename)

            # Read file content
            content = await file.read()

            # Upload with metadata
            blob.metadata = {
                'user_id': str(user_id),
                'analysis_id': analysis_id,
                'uploaded_at': datetime.utcnow().isoformat(),
            }

            blob.upload_from_string(
                content,
                content_type=file.content_type or 'image/jpeg'
            )

            # Make public (or keep private and use signed URLs)
            blob.make_public()

            # Get public URL
            public_url = blob.public_url

            logger.info(f"Uploaded analysis image for user {user_id}, analysis {analysis_id}: {unique_filename}")
            return public_url

        except Exception as e:
            logger.error(f"Error uploading analysis image: {e}")
            raise InternalServerException(f"Failed to upload analysis image: {e}")

    async def get_signed_url(
        self,
        file_path: str,
        expiration_minutes: int = 60
    ) -> str:
        """
        Generate a signed URL for private file access.

        Args:
            file_path: Path to file in Firebase Storage
            expiration_minutes: URL expiration time in minutes

        Returns:
            Signed URL with expiration
        """
        try:
            blob = self.bucket.blob(file_path)

            # Generate signed URL
            url = blob.generate_signed_url(
                expiration=timedelta(minutes=expiration_minutes),
                method='GET'
            )

            return url

        except Exception as e:
            logger.error(f"Error generating signed URL: {e}")
            raise InternalServerException(f"Failed to generate signed URL: {e}")

    async def delete_image(self, file_url: str) -> bool:
        """
        Delete an image from Firebase Storage.

        Args:
            file_url: Public URL or path of the file to delete

        Returns:
            True if deleted successfully
        """
        try:
            # Extract file path from URL
            # URL format: https://storage.googleapis.com/{bucket}/{file_path}
            if 'storage.googleapis.com' in file_url:
                file_path = file_url.split(f'{settings.FIREBASE_STORAGE_BUCKET}/')[-1]
            else:
                file_path = file_url

            # Delete the blob
            blob = self.bucket.blob(file_path)
            blob.delete()

            logger.info(f"Deleted image: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error deleting image: {e}")
            return False

    async def list_user_images(
        self,
        user_id: int,
        folder: str = "acne_analysis"
    ) -> list[str]:
        """
        List all images for a user in a specific folder.

        Args:
            user_id: User ID
            folder: Folder name (e.g., 'photos', 'acne_analysis')

        Returns:
            List of public URLs
        """
        try:
            prefix = f"{folder}/{user_id}/"
            blobs = self.bucket.list_blobs(prefix=prefix)

            urls = []
            for blob in blobs:
                if blob.public_url:
                    urls.append(blob.public_url)
                else:
                    # Generate temporary signed URL if not public
                    url = await self.get_signed_url(blob.name)
                    urls.append(url)

            return urls

        except Exception as e:
            logger.error(f"Error listing user images: {e}")
            return []

    def get_image_metadata(self, file_url: str) -> Optional[dict]:
        """
        Get metadata for an image.

        Args:
            file_url: Public URL or path of the file

        Returns:
            Dictionary with metadata or None
        """
        try:
            # Extract file path from URL
            if 'storage.googleapis.com' in file_url:
                file_path = file_url.split(f'{settings.FIREBASE_STORAGE_BUCKET}/')[-1]
            else:
                file_path = file_url

            blob = self.bucket.blob(file_path)
            blob.reload()

            return {
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created,
                'updated': blob.updated,
                'metadata': blob.metadata,
            }

        except Exception as e:
            logger.error(f"Error getting image metadata: {e}")
            return None


# Singleton instance
_storage_service: Optional[FirebaseStorageService] = None


def get_storage_service() -> FirebaseStorageService:
    """Get singleton instance of Firebase Storage service."""
    global _storage_service

    if _storage_service is None:
        _storage_service = FirebaseStorageService()

    return _storage_service
