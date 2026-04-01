# run.py  项目启动 & 调试专用入口
import uvicorn

# 主程序入口
if __name__ == "__main__":
    # 启动 FastAPI 服务
    uvicorn.run(
        app="app.main:app",    # 指向你 main.py 里的 app
        host="127.0.0.1",      # 本地调试用 127.0.0.1
        port=8000,             # 端口
        reload=True,           # 热重载
        log_level="info"       # 日志级别
    )