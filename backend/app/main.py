import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.response import ApiResponse, ErrorCode
from app.core.rate_limit import RateLimitMiddleware
from app.db.mongodb import connect_mongodb, close_mongodb
from app.db.redis import connect_redis, close_redis
from app.controllers.chat_controller import router as chat_router
from app.controllers.conversation_controller import router as conversation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    await connect_mongodb()
    await connect_redis()
    yield
    await close_mongodb()
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 限流
app.add_middleware(RateLimitMiddleware)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return ApiResponse.error(
        ErrorCode.INTERNAL, "服务器内部错误", "internal",
        str(exc) if settings.debug else None, 500,
    )


# 健康检查
@app.get("/api/v1/health")
async def health():
    return ApiResponse.success({
        "app": settings.app_name,
        "status": "running",
    })


# 挂载路由
app.include_router(chat_router, prefix="/api/v1")
app.include_router(conversation_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
