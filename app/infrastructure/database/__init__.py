"""Database infrastructure - Firebase Firestore only."""
from app.infrastructure.database.firestore_client import FirestoreClient, get_firestore_client, get_db

__all__ = [
    "FirestoreClient",
    "get_firestore_client",
    "get_db",
]
