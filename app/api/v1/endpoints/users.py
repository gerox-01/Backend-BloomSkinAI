"""
User API endpoints with Firebase Firestore.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.infrastructure.database.firestore_client import FirestoreClient, get_db
from app.infrastructure.database.repositories.firestore_user_repository import FirestoreUserRepository
from app.infrastructure.auth.firebase import get_current_user_firebase_uid
from app.application.schemas.user_schemas import (
    UserCreateSchema,
    UserUpdateSchema,
    UserResponseSchema,
    OnboardingUpdateSchema,
    SkinProfileUpdateSchema,
)
from app.core.exceptions import NotFoundException, ConflictException
from app.core.logging import logger

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    user_data: UserCreateSchema,
    firebase_uid: str = Depends(get_current_user_firebase_uid),
    db: FirestoreClient = Depends(get_db),
):
    """
    Create a new user after Firebase authentication.

    This endpoint should be called after the user signs up with Firebase Auth.
    """
    repo = FirestoreUserRepository(db)

    # Check if user already exists
    existing_user = await repo.get_by_firebase_uid(firebase_uid)
    if existing_user:
        raise ConflictException("User already exists")

    # Ensure firebase_uid from token matches the one in request
    if user_data.firebase_uid != firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Firebase UID mismatch",
        )

    # Create user entity from schema
    from app.domain.entities.user import User

    user = User(
        firebase_uid=user_data.firebase_uid,
        email=user_data.email,
        display_name=user_data.display_name,
        name=user_data.name,
        bio=user_data.bio,
        profile_photo_url=user_data.profile_photo_url,
        date_of_birth=user_data.date_of_birth,
        gender=user_data.gender,
    )

    # Save to Firestore
    created_user = await repo.create(user)

    logger.info(f"Created new user: {created_user.firebase_uid}")
    return created_user


@router.get(
    "/me",
    response_model=UserResponseSchema,
    summary="Get current user profile",
)
async def get_current_user(
    firebase_uid: str = Depends(get_current_user_firebase_uid),
    db: FirestoreClient = Depends(get_db),
):
    """
    Get the current authenticated user's profile.
    """
    repo = FirestoreUserRepository(db)

    user = await repo.get_by_firebase_uid(firebase_uid)
    if not user:
        raise NotFoundException("User not found")

    return user


@router.put(
    "/me",
    response_model=UserResponseSchema,
    summary="Update current user profile",
)
async def update_current_user(
    user_update: UserUpdateSchema,
    firebase_uid: str = Depends(get_current_user_firebase_uid),
    db: FirestoreClient = Depends(get_db),
):
    """
    Update the current authenticated user's profile.
    """
    repo = FirestoreUserRepository(db)

    # Get current user
    user = await repo.get_by_firebase_uid(firebase_uid)
    if not user:
        raise NotFoundException("User not found")

    # Update fields
    if user_update.display_name is not None:
        user.display_name = user_update.display_name
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.bio is not None:
        user.bio = user_update.bio
    if user_update.profile_photo_url is not None:
        user.profile_photo_url = user_update.profile_photo_url
    if user_update.date_of_birth is not None:
        user.date_of_birth = user_update.date_of_birth
    if user_update.gender is not None:
        user.gender = user_update.gender

    # Update skin profile if provided
    if any(
        [
            user_update.skin_type,
            user_update.skin_care_experience,
            user_update.budget_preference,
            user_update.main_skin_concerns is not None,
        ]
    ):
        user.update_skin_profile(
            skin_type=user_update.skin_type,
            experience=user_update.skin_care_experience,
            budget=user_update.budget_preference,
            concerns=user_update.main_skin_concerns,
        )

    # Save changes to Firestore
    updated_user = await repo.update(firebase_uid, user)

    logger.info(f"Updated user: {firebase_uid}")
    return updated_user


@router.put(
    "/me/onboarding",
    response_model=UserResponseSchema,
    summary="Update onboarding progress",
)
async def update_onboarding(
    onboarding_update: OnboardingUpdateSchema,
    firebase_uid: str = Depends(get_current_user_firebase_uid),
    db: FirestoreClient = Depends(get_db),
):
    """
    Update the current user's onboarding progress.
    """
    repo = FirestoreUserRepository(db)

    user = await repo.get_by_firebase_uid(firebase_uid)
    if not user:
        raise NotFoundException("User not found")

    # Update onboarding
    user.complete_onboarding_step(onboarding_update.onboarding_step)

    if onboarding_update.face_image_captured is not None:
        user.face_image_captured = onboarding_update.face_image_captured

    if onboarding_update.face_analysis_completed is not None:
        user.face_analysis_completed = onboarding_update.face_analysis_completed

    # Save changes to Firestore
    updated_user = await repo.update(firebase_uid, user)

    logger.info(f"Updated onboarding for user: {firebase_uid} (step: {user.onboarding_step})")
    return updated_user


@router.put(
    "/me/skin-profile",
    response_model=UserResponseSchema,
    summary="Update skin profile",
)
async def update_skin_profile(
    profile_update: SkinProfileUpdateSchema,
    firebase_uid: str = Depends(get_current_user_firebase_uid),
    db: FirestoreClient = Depends(get_db),
):
    """
    Update the current user's skin profile.
    """
    repo = FirestoreUserRepository(db)

    user = await repo.get_by_firebase_uid(firebase_uid)
    if not user:
        raise NotFoundException("User not found")

    # Update skin profile
    user.update_skin_profile(
        skin_type=profile_update.skin_type,
        experience=profile_update.skin_care_experience,
        budget=profile_update.budget_preference,
        concerns=profile_update.main_skin_concerns,
    )

    # Save changes to Firestore
    updated_user = await repo.update(firebase_uid, user)

    logger.info(f"Updated skin profile for user: {firebase_uid}")
    return updated_user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user",
)
async def delete_current_user(
    firebase_uid: str = Depends(get_current_user_firebase_uid),
    db: FirestoreClient = Depends(get_db),
):
    """
    Delete the current authenticated user's account.
    """
    repo = FirestoreUserRepository(db)

    user = await repo.get_by_firebase_uid(firebase_uid)
    if not user:
        raise NotFoundException("User not found")

    # Delete user from Firestore
    await repo.delete(firebase_uid)

    # TODO: Also delete from Firebase Auth
    # from app.infrastructure.auth.firebase import delete_firebase_user
    # await delete_firebase_user(firebase_uid)

    logger.info(f"Deleted user: {firebase_uid}")
    return None
