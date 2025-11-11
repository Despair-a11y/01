# HBase 配置说明

本系统支持两种数据源：**CSV 文件**（默认）和 **HBase 数据库**（可选）。

## 📋 目录

- [默认配置（CSV模式）](#默认配置csv模式)
- [HBase模式配置](#hbase模式配置)
- [数据导入](#数据导入)
- [配置参数说明](#配置参数说明)
- [故障排除](#故障排除)

---

## 🎯 默认配置（CSV模式）

系统默认使用 **CSV 文件** 作为数据源，无需任何额外配置即可运行。

### 默认数据源
- 📁 电影数据：`ml-latest-small/movies.csv`
- 📁 评分数据：`ml-latest-small/ratings.csv`

### 无需安装
默认模式下**不需要**安装 HBase 相关依赖，系统会自动使用 CSV 模式。

---

## 🔧 HBase模式配置

如果您想使用 HBase 作为数据源，请按照以下步骤操作：

### 步骤 1: 安装 HBase 依赖

编辑 `requirements.txt`，取消以下行的注释：

```txt
# 将这两行的注释去掉
happybase>=1.2.0
thrift>=0.16.0
```

然后安装依赖：

```bash
pip install happybase thrift
```

### 步骤 2: 配置 HBase 连接

编辑 `hbase_config.py` 文件：

```python
# HBase 连接配置
HBASE_CONFIG = {
    'host': 'your-hbase-host',  # 修改为你的 HBase 主机地址
    'port': 9090,                # HBase Thrift 端口
    'timeout': 3000,
    
    # ... 其他配置保持不变
    
    # 启用 HBase
    'enabled': True,  # 改为 True
}

# 数据源配置
DATA_SOURCE = {
    'type': 'hbase',  # 改为 'hbase'
    'csv_dir': 'ml-latest-small',
}
```

### 步骤 3: 确保 HBase Thrift 服务运行

HBase 需要启动 Thrift 服务器才能被 Python 访问：

```bash
# 在 HBase 服务器上启动 Thrift 服务
hbase thrift start -p 9090
```

---

## 📥 数据导入

如果使用 HBase 模式，需要先将 CSV 数据导入 HBase。

### 自动导入工具

使用提供的导入脚本：

```bash
python import_to_hbase.py
```

### 导入过程

脚本会自动完成以下操作：

1. ✅ 连接到 HBase
2. ✅ 创建必要的表
3. ✅ 读取 CSV 数据
4. ✅ 导入电影数据到 `movielens:movies` 表
5. ✅ 导入评分数据到 `movielens:ratings` 表

### 导入示例输出

```
============================================================
MovieLens 数据导入 HBase 工具
============================================================

📁 CSV 文件检查完成
  - ml-latest-small\movies.csv
  - ml-latest-small\ratings.csv

🔌 正在连接 HBase...
  主机: localhost:9090
✅ HBase 连接成功

📋 创建 HBase 表...
✅ 表创建完成

📖 读取 CSV 数据...
  - 读取 movies.csv...
    ✅ 读取 9742 条电影数据
  - 读取 ratings.csv...
    ✅ 读取 100836 条评分数据

⬆️  导入电影数据到 HBase...
✅ 电影数据导入完成

⬆️  导入评分数据到 HBase...
✅ 评分数据导入完成

============================================================
✅ 所有数据导入完成！
============================================================
```

---

## ⚙️ 配置参数说明

### HBase 连接参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `host` | HBase Thrift 服务器地址 | `localhost` |
| `port` | Thrift 端口 | `9090` |
| `timeout` | 连接超时时间（毫秒） | `3000` |
| `enabled` | 是否启用 HBase | `False` |

### 表名配置

| 表名 | HBase 表名 | 说明 |
|------|-----------|------|
| movies | `movielens:movies` | 电影信息表 |
| ratings | `movielens:ratings` | 评分数据表 |
| tags | `movielens:tags` | 标签数据表（暂未使用） |

### 列族结构

#### movies 表
- **列族**: `info`
- **列**: `movieId`, `title`, `genres`, `year`

#### ratings 表
- **列族**: `info`
- **列**: `userId`, `movieId`, `rating`, `timestamp`, `datetime`, `year`, `month`

---

## 🔄 切换数据源

### 切换到 HBase 模式

编辑 `hbase_config.py`：

```python
HBASE_CONFIG = {
    'enabled': True,  # 启用 HBase
    # ... 其他配置
}

DATA_SOURCE = {
    'type': 'hbase',  # 使用 HBase
}
```

### 切换回 CSV 模式

编辑 `hbase_config.py`：

```python
HBASE_CONFIG = {
    'enabled': False,  # 禁用 HBase
    # ... 其他配置
}

DATA_SOURCE = {
    'type': 'csv',  # 使用 CSV
}
```

---

## 🌍 环境变量配置（可选）

也可以通过环境变量配置 HBase：

```bash
# Linux/Mac
export HBASE_HOST=your-hbase-server
export HBASE_PORT=9090
export HBASE_ENABLED=true
export DATA_SOURCE=hbase

# Windows PowerShell
$env:HBASE_HOST="your-hbase-server"
$env:HBASE_PORT="9090"
$env:HBASE_ENABLED="true"
$env:DATA_SOURCE="hbase"
```

环境变量会自动覆盖配置文件中的设置。

---

## 🛠️ 故障排除

### 1. 无法连接到 HBase

**问题**: `ConnectionError: 未连接到 HBase`

**解决方案**:
- 检查 HBase 服务是否运行
- 检查 Thrift 服务是否启动
- 验证 host 和 port 配置是否正确
- 检查防火墙设置

### 2. happybase 未安装

**问题**: `ImportError: No module named 'happybase'`

**解决方案**:
```bash
pip install happybase thrift
```

### 3. 数据加载失败

**问题**: 提示 "从 HBase 加载失败，回退到 CSV"

**解决方案**:
- 系统会自动回退到 CSV 模式，不影响使用
- 检查 HBase 配置是否正确
- 确认数据已导入 HBase
- 查看控制台错误信息

### 4. 表不存在

**问题**: `Table not found`

**解决方案**:
- 运行导入脚本: `python import_to_hbase.py`
- 或手动创建表

---

## 📊 性能对比

| 特性 | CSV 模式 | HBase 模式 |
|------|---------|-----------|
| 配置难度 | ⭐ 简单 | ⭐⭐⭐ 中等 |
| 部署要求 | 无 | 需要 HBase 服务器 |
| 启动速度 | 快 | 中等 |
| 数据查询 | 内存加载 | 分布式查询 |
| 扩展性 | 有限 | 优秀 |
| 适用场景 | 小数据集、开发测试 | 大数据集、生产环境 |

---

## 💡 建议

### 开发和测试环境
- ✅ 推荐使用 **CSV 模式**
- 无需额外配置
- 启动快速
- 调试方便

### 生产环境（大数据集）
- ✅ 推荐使用 **HBase 模式**
- 支持海量数据
- 分布式存储
- 更好的性能

---

## 📞 技术支持

如有问题，请检查：

1. HBase 服务状态
2. Thrift 服务状态
3. 网络连接
4. 配置文件设置
5. 日志输出信息

---

**注意**: 默认情况下系统使用 CSV 模式，即使配置了 HBase 也不会影响现有功能。

