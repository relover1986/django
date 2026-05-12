module.exports = {
  apps: [{
    name: "django",
    cwd: "/root/django",
    script: "/root/django/venv/bin/uvicorn",
    args: "lnjx2025.asgi:application --host 127.0.0.1 --port 8000 --workers 4",
    interpreter: "/root/django/venv/bin/python",
    env: {
      PYTHONPATH: "/root/django"
    },
    max_memory_restart: "500M",
    error_file: "/var/log/django-err.log",
    out_file: "/var/log/django-out.log",
    merge_logs: true,
    log_date_format: "YYYY-MM-DD HH:mm:ss"
  }]
};
