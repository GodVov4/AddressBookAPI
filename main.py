from fastapi import FastAPI, Depends, HTTPException
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.database.fu_db import get_db
from src.routes import address_book, auth, users

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "src" / "static"), name="static")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(address_book.router, prefix="/api")


@app.on_event("startup")
async def startup():
    """
    Initializes the application when it starts up.

    This function is called automatically when the application starts up.
    It connects to the Redis server using the configuration provided and initializes the FastAPILimiter.
    """
    r = await Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(r)


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    A function that checks the health of the API.

    :param db: An instance of the AsyncSession class used to interact with the database.
    :type db: AsyncSession

    :return: A dictionary containing a welcome message if the health check is successful.
    :rtype: dict

    :raises HTTPException: If there is an error connecting to the database or if the database is not configured correctly.
    """
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
