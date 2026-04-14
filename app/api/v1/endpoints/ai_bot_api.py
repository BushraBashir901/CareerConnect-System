# app/api/v1/endpoints/ai_evaluation_api.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependency import get_db
from app.dependencies.rbac_strict import require_permission_with_company_scope
from app.core.rbac import PermissionEnum
from app.repositories import ai_bot_repo
from app.schemas.ai_bot import AiBotCreate, AiBotUpdate, AiBotResponse


router = APIRouter(prefix="/ai-bot", tags=["AI Bots"])


# -------------------------
# Create AI Bot
# -------------------------
@router.post("/", response_model=AiBotResponse)
def create_ai_bot(
    bot: AiBotCreate,
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.RUN_AI_EVALUATION)),
    db: Session = Depends(get_db)
):
    """
    Create a new AI Bot.

    Requires RUN_AI_EVALUATION permission.

    Args:
        bot (AiBotCreate): AI bot input data.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        AiBotResponse: Created AI bot.
    """
    try:
        return ai_bot_repo.create_ai_evaluation(db, bot)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------
# Get AI Bot by ID
# -------------------------
@router.get("/{bot_id}", response_model=AiBotResponse)
def get_ai_bot(
    bot_id: int,
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.RUN_AI_EVALUATION)),
    db: Session = Depends(get_db)
):
    """
    Retrieve an AI Bot by ID.

    Requires RUN_AI_EVALUATION permission.

    Args:
        bot_id (int): AI Bot ID.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        AiBotResponse: AI bot object.

    Raises:
        HTTPException: If bot not found.
    """
    ai_bot = ai_bot_repo.get_ai_evaluation(db, bot_id)
    if not ai_bot:
        raise HTTPException(status_code=404, detail="AI Bot not found")
    return ai_bot


# -------------------------
# Update AI Bot
# -------------------------
@router.put("/{bot_id}", response_model=AiBotResponse)
def update_ai_bot(
    bot_id: int,
    bot_data: AiBotUpdate,
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.RUN_AI_EVALUATION)),
    db: Session = Depends(get_db)
):
    """
    Update an existing AI Bot.

    Requires RUN_AI_EVALUATION permission.

    Args:
        bot_id (int): AI Bot ID.
        bot_data (AiBotUpdate): Updated bot data.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        AiBotResponse: Updated AI bot.

    Raises:
        HTTPException: If bot not found.
    """
    ai_bot = ai_bot_repo.update_ai_evaluation(db, bot_id, bot_data)
    if not ai_bot:
        raise HTTPException(status_code=404, detail="AI Bot not found")
    return ai_bot


# -------------------------
# Delete AI Bot
# -------------------------
@router.delete("/{bot_id}", response_model=AiBotResponse)
def delete_ai_bot(
    bot_id: int,
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.RUN_AI_EVALUATION)),
    db: Session = Depends(get_db)
):
    """
    Delete an AI Bot.

    Requires RUN_AI_EVALUATION permission.

    Args:
        bot_id (int): AI Bot ID.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        AiBotResponse: Deleted AI bot.

    Raises:
        HTTPException: If bot not found.
    """
    ai_bot = ai_bot_repo.delete_ai_bot(db, bot_id)
    if not ai_bot:
        raise HTTPException(status_code=404, detail="AI Bot not found")
    return ai_bot


# -------------------------
# List all AI Bots
# -------------------------
@router.get("/", response_model=list[AiBotResponse])
def list_ai_bots(
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.RUN_AI_EVALUATION)),
    db: Session = Depends(get_db)
):
    """
    List all AI Bots.

    Requires RUN_AI_EVALUATION permission.

    Args:
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        list[AiBotResponse]: List of AI bots.
    """
    try:
        return ai_bot_repo.list_ai_bots(db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))