"""
Firebase Firestore client for BloomSkin database operations.
"""
from typing import Optional
from firebase_admin import firestore

from app.core.logging import logger


class FirestoreClient:
    """
    Firestore database client for BloomSkin.

    Collections structure:
    - users: User profiles and settings
    - skin_analyses: AI skin analysis results
    - subscriptions: User subscription data
    - routines: Daily skincare routines
    - products: Product catalog
    - product_bundles: Personalized product bundles
    """

    def __init__(self):
        """Initialize Firestore client."""
        try:
            self.db = firestore.client()
            logger.info("Firestore client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}")
            raise

    def get_collection(self, collection_name: str):
        """Get a Firestore collection reference."""
        return self.db.collection(collection_name)

    def get_document(self, collection_name: str, document_id: str):
        """Get a specific document reference."""
        return self.db.collection(collection_name).document(document_id)


# Singleton instance
_firestore_client: Optional[FirestoreClient] = None


def get_firestore_client() -> FirestoreClient:
    """Get singleton Firestore client instance."""
    global _firestore_client

    if _firestore_client is None:
        _firestore_client = FirestoreClient()

    return _firestore_client


def get_db():
    """
    Dependency for getting Firestore client.

    Usage in FastAPI endpoints:
    ```python
    @router.get("/")
    async def my_endpoint(db = Depends(get_db)):
        # Use db here
        pass
    ```
    """
    return get_firestore_client()
