"""
Haut.ai API Service for skin analysis.
"""
import base64
import httpx
from typing import Optional, Dict, Any
from loguru import logger

from app.core.config import settings


class HautAIService:
    """Service for interacting with Haut.ai API."""

    def __init__(self):
        self.api_url = settings.HAUT_AI_API_URL
        self.username = settings.HAUT_AI_USERNAME
        self.password = settings.HAUT_AI_PASSWORD
        self.dataset_id = settings.HAUT_AI_DATASET_ID
        self.access_token: Optional[str] = None
        self.company_id: Optional[str] = None

    async def login(self) -> Dict[str, Any]:
        """
        Login to Haut.ai and get access token and company ID.

        Returns:
            Dict containing company_id and access_token
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/api/v1/auth/login/",
                json={
                    "username": self.username,
                    "password": self.password
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            self.access_token = data.get("access_token")
            self.company_id = data.get("company_id")

            logger.info(f"Logged in to Haut.ai - Company ID: {self.company_id}")
            return data

    async def ensure_authenticated(self):
        """Ensure we have valid authentication."""
        if not self.access_token or not self.company_id:
            await self.login()

    async def create_subject(self, firebase_uid: str) -> str:
        """
        Create a subject in Haut.ai using Firebase UID.

        Args:
            firebase_uid: User's Firebase UID

        Returns:
            subject_id
        """
        await self.ensure_authenticated()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/api/v1/companies/{self.company_id}/datasets/{self.dataset_id}/subjects/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={"name": firebase_uid},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            subject_id = data.get("id")

            logger.info(f"Created subject for {firebase_uid}: {subject_id}")
            return subject_id

    async def create_batch(self, subject_id: str) -> str:
        """
        Create a batch for a subject.

        Args:
            subject_id: Subject ID from Haut.ai

        Returns:
            batch_id
        """
        await self.ensure_authenticated()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/api/v1/companies/{self.company_id}/datasets/{self.dataset_id}/subjects/{subject_id}/batches/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            batch_id = data.get("id")

            logger.info(f"Created batch for subject {subject_id}: {batch_id}")
            return batch_id

    async def send_image(
        self,
        subject_id: str,
        batch_id: str,
        image_base64: str,
        side_id: int = 1,
        light_id: int = 1
    ) -> str:
        """
        Send image to Haut.ai for analysis.

        Args:
            subject_id: Subject ID
            batch_id: Batch ID
            image_base64: Base64 encoded image
            side_id: Side ID (1 for front)
            light_id: Light ID (1 for standard)

        Returns:
            image_id
        """
        await self.ensure_authenticated()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/api/v1/companies/{self.company_id}/datasets/{self.dataset_id}/subjects/{subject_id}/batches/{batch_id}/images/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={
                    "side_id": side_id,
                    "light_id": light_id,
                    "b64data": image_base64
                },
                timeout=60.0  # Longer timeout for image upload
            )
            response.raise_for_status()
            data = response.json()
            image_id = data.get("id")

            logger.info(f"Sent image for subject {subject_id}, batch {batch_id}: {image_id}")
            return image_id

    async def get_results(
        self,
        subject_id: str,
        batch_id: str,
        image_id: str
    ) -> Dict[str, Any]:
        """
        Get analysis results from Haut.ai.

        Args:
            subject_id: Subject ID
            batch_id: Batch ID
            image_id: Image ID

        Returns:
            Analysis results
        """
        await self.ensure_authenticated()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/api/v1/companies/{self.company_id}/datasets/{self.dataset_id}/subjects/{subject_id}/batches/{batch_id}/images/{image_id}/results/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=30.0
            )
            response.raise_for_status()
            
            # Get the raw response text first to handle any potential encoding issues
            response_text = response.text
            
            try:
                # Parse JSON response
                data = response.json()
                logger.info(f"Retrieved results for image {image_id}: {len(data) if isinstance(data, list) else 'object'} items")
                return data
            except Exception as e:
                logger.error(f"Failed to parse JSON response for image {image_id}: {str(e)}")
                logger.error(f"Response text: {response_text[:500]}...") 
                raise ValueError(f"Invalid JSON response from Haut.ai: {str(e)}")

    async def analyze_image(
        self,
        firebase_uid: str,
        image_base64: str,
        side_id: int = 1,
        light_id: int = 1
    ) -> Dict[str, Any]:
        """
        Complete workflow: create subject, batch, upload image.

        Args:
            firebase_uid: User's Firebase UID
            image_base64: Base64 encoded image
            side_id: Side ID (1 for front)
            light_id: Light ID (1 for standard)

        Returns:
            Dict containing subject_id, batch_id, image_id
        """
        # Create subject
        subject_id = await self.create_subject(firebase_uid)

        # Create batch
        batch_id = await self.create_batch(subject_id)

        # Send image
        image_id = await self.send_image(
            subject_id=subject_id,
            batch_id=batch_id,
            image_base64=image_base64,
            side_id=side_id,
            light_id=light_id
        )

        return {
            "subject_id": subject_id,
            "batch_id": batch_id,
            "image_id": image_id,
            "message": "Image uploaded successfully. Analysis is being processed."
        }


def get_haut_ai_service() -> HautAIService:
    """Get Haut.ai service instance."""
    return HautAIService()
