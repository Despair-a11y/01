# MovieLens 数据分析系统启动指南

本指南将帮助您在另一台电脑上快速启动本项目。

## 1. 前置要求

在运行本项目之前，请确保您的电脑上已安装：

*   **Docker Desktop**: [下载地址](https://www.docker.com/products/docker-desktop/)
    *   安装完成后请启动 Docker Desktop。

## 2. 启动步骤

1.  **解压文件**：将压缩包解压到任意目录。
2.  **打开终端**：
    *   **Windows**: 右键点击文件夹空白处，选择 "在终端中打开" 或 "Open in Terminal"。
    *   **Mac/Linux**: 打开终端 (Terminal)，使用 `cd` 命令进入解压后的文件夹。
3.  **运行启动命令**：
    在终端中输入以下命令并回车：
    ```bash
    docker-compose up -d
    ```
    *   如果是第一次运行，Docker 会自动下载所需环境（Spark, HBase 等），可能需要几分钟时间，请耐心等待。

## 3. 访问应用

启动完成后，您可以访问以下服务：

*   **Web 数据分析系统**: [http://localhost:8501](http://localhost:8501)
*   **HBase 管理界面**: [http://localhost:16010](http://localhost:16010)
*   **Spark Master 界面**: [http://localhost:8080](http://localhost:8080)

## 4. 停止应用

如果需要停止服务，请在终端中运行：

```bash
docker-compose down
```

## 5. 常见问题

*   **端口占用**：如果启动失败提示端口被占用，请确保 8501, 9090, 8080, 16010 端口未被其他程序使用。
*   **数据加载慢**：首次启动时，HBase 需要初始化，Web 应用加载数据可能需要几十秒，请刷新页面重试。

---
祝您使用愉快！
