from pickle import dumps

from cloudinary import CloudinaryImage, uploader, config
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config as cfg
from src.database.fu_db import get_db
from src.entity.models import User
from src.repository.users import update_avatar_url
from src.schemas.user import UserRead, UserUpdate
from src.services.auth import fastapi_users, current_active_user

router = APIRouter()

config(
    cloud_name=cfg.CLD_NAME,
    api_key=cfg.CLD_API_KEY,
    api_secret=cfg.CLD_API_SECRET,
    secure=True,
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=False),
    prefix="/users",
    tags=["users"],
)


@router.patch("/avatar", response_model=UserRead, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_avatar(
    file: UploadFile = File(),
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    public_id = f"AddressBook/{user.email}/{file.filename}"
    res = uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await update_avatar_url(user.email, res_url, db)
    # auth_service.cache.set(user.email, dumps(user))
    # auth_service.cache.expire(user.email, 300)
    return user
