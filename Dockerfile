# 基础镜像：选和云端一致的 Python 版本，用 slim 版省空间
FROM python:3.13.2-slim

# 设置容器内工作目录
WORKDIR /app

# 复制依赖文件并安装，用清华源加速
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目所有代码到容器
COPY . .

# 暴露 Django 运行端口
EXPOSE 8000

# 容器启动命令，允许外部访问
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]