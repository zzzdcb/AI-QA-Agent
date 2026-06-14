from typing import Any, Optional

from fastapi import status
from fastapi.responses import JSONResponse


class ApiResponse:
    """统一 RESTful 响应格式"""

    @staticmethod
    def success(data: Any = None, message: str = "ok") -> JSONResponse:
        return JSONResponse(
            content={"code": 0, "message": message, "data": data},
            status_code=status.HTTP_200_OK,
        )

    @staticmethod
    def created(data: Any = None, message: str = "created") -> JSONResponse:
        return JSONResponse(
            content={"code": 0, "message": message, "data": data},
            status_code=status.HTTP_201_CREATED,
        )

    @staticmethod
    def error(
        code: int,
        message: str,
        error_type: str = "internal",
        detail: Optional[str] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> JSONResponse:
        error = {"type": error_type}
        if detail:
            error["detail"] = detail
        return JSONResponse(
            content={"code": code, "message": message, "error": error},
            status_code=status_code,
        )


# 错误码定义
class ErrorCode:
    # 4xxx - 客户端错误
    BAD_REQUEST = 40001
    NOT_FOUND = 40401
    RATE_LIMITED = 42901

    # 5xxx - 服务端错误
    INTERNAL = 50001
    AI_SERVICE_ERROR = 50201
    DB_ERROR = 50301
