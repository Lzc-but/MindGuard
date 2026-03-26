# run_db.py
import logging
from app.extensions.db import init_db, test_db_connection, create_all_tables

# 配置日志（方便查看输出）
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    try:
        # 初始化数据库（自动加载配置并测试连接）
        init_db()
        # 手动测试连接（可选，init_db 内部已调用）
        test_db_connection()
        print("数据库初始化和连接测试全部通过！")
        create_all_tables()
        print("所有数据表创建成功！")

    except Exception as e:
        print(f"初始化失败：{str(e)}")