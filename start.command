#!/bin/bash
# WAR3 训练营本地预览：双击本文件，或终端执行 ./start.command
cd "$(dirname "$0")"
echo "预览地址 → http://127.0.0.1:8931/  （Ctrl+C 停止）"
python3 -m http.server 8931 --bind 0.0.0.0
