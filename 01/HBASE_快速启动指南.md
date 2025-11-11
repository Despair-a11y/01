# HBase 快速启动指南

本指南帮助你快速配置和使用 HBase 作为 MovieLens 数据源。

---

## 📋 前置条件

### 1. 环境要求
- ✅ Java 8 或更高版本
- ✅ HBase 2.0+ 已安装
- ✅ Python 3.8+
- ✅ HBase Thrift 服务运行中

### 2. Python 依赖
```bash
pip install happybase thrift
```

---

## 🚀 快速开始（5步完成）

### 步骤 1: 启动 HBase 服务

```bash
# 启动 HBase
start-hbase.sh

# 启动 Thrift 服务器（重要！）
hbase thrift start -p 9090
```

**验证服务运行**:
```bash
# 检查 HBase 是否运行
jps | grep HMaster

# 检查 Thrift 是否运行
netstat -an | grep 9090
```

---

### 步骤 2: 创建 HBase 表

**方法 1: 使用 Shell 脚本（推荐）**
```bash
# Linux/Mac
hbase shell hbase_create_tables.sh

# Windows
hbase shell hbase_create_tables.sh
```

**方法 2: 手动创建**
```bash
# 进入 HBase Shell
hbase shell

# 创建命名空间
create_namespace 'movielens'

# 创建表
create 'movielens:movies', {NAME => 'info', VERSIONS => 1, COMPRESSION => 'SNAPPY'}
create 'movielens:ratings', {NAME => 'info', VERSIONS => 1, COMPRESSION => 'SNAPPY'}

# 退出
exit
```

**验证表创建**:
```bash
hbase shell
list 'movielens:.*'
exit
```

---

### 步骤 3: 配置连接参数

编辑 `hbase_config.py`:

```python
HBASE_CONFIG = {
    'host': 'localhost',      # 改为你的 HBase 主机地址
    'port': 9090,             # Thrift 端口
    'timeout': 3000,
    'enabled': True,          # ⚠️ 改为 True
}

DATA_SOURCE = {
    'type': 'hbase',          # ⚠️ 改为 'hbase'
    'csv_dir': 'ml-latest-small',
}
```

---

### 步骤 4: 导入数据

```bash
# 运行导入脚本
python import_to_hbase.py
```

**预期输出**:
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

**导入时间估算**:
- Movies 表: ~10 秒
- Ratings 表: ~1-2 分钟

---

### 步骤 5: 验证数据

```bash
# 运行验证脚本
python verify_hbase_data.py
```

**或手动验证**:
```bash
hbase shell

# 统计行数
count 'movielens:movies'
count 'movielens:ratings'

# 查看样例数据
scan 'movielens:movies', {LIMIT => 5}
scan 'movielens:ratings', {LIMIT => 5}

exit
```

---

### 步骤 6: 启动应用

```bash
# 启动 Streamlit 应用
streamlit run app.py
```

访问 `http://localhost:8501` 即可使用！

---

## 🔧 常见问题解决

### 1. 无法连接到 HBase

**问题**: `ConnectionError: 未连接到 HBase`

**解决方案**:
```bash
# 1. 检查 Thrift 是否运行
netstat -an | grep 9090

# 2. 如果没有运行，启动 Thrift
hbase thrift start -p 9090

# 3. 检查防火墙
# 确保端口 9090 开放
```

---

### 2. happybase 未安装

**问题**: `ImportError: No module named 'happybase'`

**解决方案**:
```bash
# 安装 happybase
pip install happybase thrift

# 或者使用 requirements.txt
# 取消注释 happybase 相关行
pip install -r requirements.txt
```

---

### 3. 表已存在错误

**问题**: `Table already exists`

**解决方案**:
```bash
# 删除现有表
hbase shell hbase_drop_tables.sh

# 重新创建
hbase shell hbase_create_tables.sh
```

---

### 4. 数据导入失败

**问题**: 导入过程中断或失败

**解决方案**:
```bash
# 1. 检查 HBase 日志
tail -f $HBASE_HOME/logs/hbase-*-master-*.log

# 2. 清空表重新导入
hbase shell
truncate 'movielens:movies'
truncate 'movielens:ratings'
exit

# 3. 重新导入
python import_to_hbase.py
```

---

### 5. 应用仍使用 CSV

**问题**: 配置了 HBase 但应用仍从 CSV 加载

**检查清单**:
```python
# ✅ hbase_config.py 中
HBASE_CONFIG['enabled'] = True
DATA_SOURCE['type'] = 'hbase'

# ✅ happybase 已安装
pip list | grep happybase

# ✅ HBase Thrift 运行中
netstat -an | grep 9090

# ✅ 重启应用
# Ctrl+C 停止，然后重新运行
streamlit run app.py
```

---

## 📊 性能优化

### 1. 批量写入优化

编辑 `hbase_config.py`:
```python
HBASE_CONFIG = {
    'batch_size': 5000,  # 增大批量大小（默认1000）
    # ... 其他配置
}
```

### 2. 连接池优化

```python
HBASE_CONFIG = {
    'pool_size': 20,  # 增加连接池大小（默认10）
    # ... 其他配置
}
```

### 3. 启用压缩

表已默认启用 SNAPPY 压缩，可手动修改：
```bash
hbase shell

# 修改压缩算法
alter 'movielens:movies', {NAME => 'info', COMPRESSION => 'GZ'}

exit
```

---

## 🔄 切换数据源

### 切换到 HBase
```python
# hbase_config.py
HBASE_CONFIG['enabled'] = True
DATA_SOURCE['type'] = 'hbase'
```

### 切换回 CSV
```python
# hbase_config.py
HBASE_CONFIG['enabled'] = False
DATA_SOURCE['type'] = 'csv'
```

**重启应用使配置生效**

---

## 📝 HBase Shell 常用命令

```bash
# 进入 Shell
hbase shell

# 查看所有表
list

# 查看表结构
describe 'movielens:movies'

# 统计行数
count 'movielens:movies'

# 扫描数据
scan 'movielens:movies', {LIMIT => 10}

# 获取单行
get 'movielens:movies', '1'

# 删除表（需先禁用）
disable 'movielens:movies'
drop 'movielens:movies'

# 清空表
truncate 'movielens:movies'

# 退出
exit
```

---

## 🎯 测试清单

完成以下检查确保系统正常运行：

- [ ] HBase 服务运行中
- [ ] Thrift 服务运行中（端口 9090）
- [ ] happybase 已安装
- [ ] HBase 表已创建
- [ ] 数据已导入
- [ ] hbase_config.py 配置正确
- [ ] 验证脚本运行成功
- [ ] 应用可以从 HBase 读取数据

---

## 📞 获取帮助

### 查看日志
```bash
# HBase Master 日志
tail -f $HBASE_HOME/logs/hbase-*-master-*.log

# RegionServer 日志
tail -f $HBASE_HOME/logs/hbase-*-regionserver-*.log

# Thrift 日志
tail -f $HBASE_HOME/logs/hbase-*-thrift-*.log
```

### 运行诊断脚本
```bash
# 验证数据
python verify_hbase_data.py

# 查询示例
hbase shell hbase_query_examples.sh
```

---

## 🎉 完成！

如果以上步骤都顺利完成，恭喜你！你已经成功配置了 HBase 数据源。

现在可以：
✅ 使用 HBase 存储海量数据
✅ 享受分布式数据库的性能优势
✅ 随时切换回 CSV 模式

**Happy Coding! 🚀**

