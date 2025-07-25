import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from api.routes import router

# 硬编码配置
APP_NAME = "PDF转Markdown工具"
APP_VERSION = "1.0.0"
HOST = "0.0.0.0"
PORT = 8001
DEBUG = False
WORKERS = 1
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://127.0.0.1:3000",
]

# 创建FastAPI应用
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="基于marker库的PDF转Markdown工具",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册API路由
app.include_router(router, prefix="/api", tags=["API"])


@app.get("/")
async def root():
    """根路径，重定向到Web界面"""
    return RedirectResponse(url="/static/index.html")


@app.get("/info")
async def info():
    """应用信息"""
    return {"docs_url": "/docs", "redoc_url": "/redoc"}


def main():
    """主函数"""
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        workers=WORKERS,
    )


if __name__ == "__main__":
    main()
