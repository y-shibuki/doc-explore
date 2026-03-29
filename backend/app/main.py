from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import check_db_initialized
from app.routers import config, files, index, search, tags, tree


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await check_db_initialized():
        raise RuntimeError(
            "DB が初期化されていません。先に 'task migrate' を実行してください。"
        )
    yield


app = FastAPI(title="doc-explore", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config.router)
app.include_router(index.router)
app.include_router(search.router)
app.include_router(tree.router)
app.include_router(files.router)
app.include_router(tags.router)
