#!/bin/bash

# 定义打包文件名
PACKAGE_NAME="MovieLens_Project_Package.zip"

# 清理旧的打包文件
if [ -f "$PACKAGE_NAME" ]; then
    rm "$PACKAGE_NAME"
fi

# 创建打包文件
# 排除项：
# - venv: 虚拟环境
# - __pycache__: Python缓存
# - .git: Git版本控制
# - .idea: IDE配置
# - .DS_Store: Mac系统文件
# - *.zip: 防止打包自己
# - .streamlit: Streamlit配置（如果是用户级配置可能不需要，但项目级配置需要保留，这里保留）

echo "正在打包项目..."

zip -r "$PACKAGE_NAME" . \
    -x "venv/*" \
    -x "*/__pycache__/*" \
    -x ".git/*" \
    -x ".idea/*" \
    -x "**/.DS_Store" \
    -x "*.zip" \
    -x "check_*.py"

if [ $? -eq 0 ]; then
    echo "✅ 打包成功！文件名为: $PACKAGE_NAME"
    echo "您可以将此文件发送给其他人。"
else
    echo "❌ 打包失败，请检查 zip 命令是否安装。"
fi
