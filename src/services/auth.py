import uuid

from typing import Optional
from fastapi import Depends, Request, BackgroundTasks
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, schemas, models
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.exceptions import UserAlreadyExists
from libgravatar import Gravatar

from src.conf.config import config
from src.database.fu_db import User, get_user_db
from src.services.email import send_email


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = config.SECRET_KEY_JWT
    verification_token_secret = config.SECRET_KEY_JWT

    def __init__(self, user_db: SQLAlchemyUserDatabase, background_tasks: BackgroundTasks):
        super().__init__(user_db)
        self.background_tasks = background_tasks

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        await self.request_verify(user, request)

    async def create(self, user_create: schemas.UC, safe: bool = False, request: Optional[Request] = None) -> models.UP:
        await self.validate_password(user_create.password, user_create)
        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise UserAlreadyExists()

        user_dict = (user_create.create_update_dict() if safe else user_create.create_update_dict_superuser())
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        avatar = None
        try:
            g = Gravatar(user_create.email)
            avatar = g.get_image()
        except Exception as err:
            print(err)
        user_dict["avatar"] = avatar

        created_user = await self.user_db.create(user_dict)
        await self.on_after_register(created_user, request)
        return created_user

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        host = str(request.base_url)
        self.background_tasks.add_task(send_email, user.email, user.username, token, host)

    async def on_after_verify(self, user: models.UP, request: Optional[Request] = None) -> None:
        print('verified user', user.email)


async def get_user_manager(background_tasks: BackgroundTasks, user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db, background_tasks)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=config.SECRET_KEY_JWT, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
