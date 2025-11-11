# HBase 表结构说明

## 📋 命名空间

```
movielens
```

---

## 📊 表结构详情

### 1. Movies 表 (movielens:movies)

**用途**: 存储电影基本信息

**RowKey 设计**: `movieId` (字符串格式的电影ID)

**列族**: 
- `info` - 存储电影信息

**列**:
| 列名 | 完整限定名 | 数据类型 | 说明 | 示例 |
|------|-----------|---------|------|------|
| movieId | info:movieId | String | 电影ID（冗余存储） | "1" |
| title | info:title | String | 电影名称（含年份） | "Toy Story (1995)" |
| genres | info:genres | String | 电影类型（\|分隔） | "Adventure\|Animation\|Children" |
| year | info:year | String | 上映年份 | "1995" |

**示例数据**:
```
RowKey: "1"
info:movieId => "1"
info:title => "Toy Story (1995)"
info:genres => "Adventure|Animation|Children|Comedy|Fantasy"
info:year => "1995"
```

**索引建议**:
- 主索引: movieId (RowKey)
- 二级索引（可选）: title, year

---

### 2. Ratings 表 (movielens:ratings)

**用途**: 存储用户评分数据

**RowKey 设计**: `userId_movieId_timestamp` (组合键，确保唯一性)

**列族**: 
- `info` - 存储评分信息

**列**:
| 列名 | 完整限定名 | 数据类型 | 说明 | 示例 |
|------|-----------|---------|------|------|
| userId | info:userId | String | 用户ID | "1" |
| movieId | info:movieId | String | 电影ID | "1" |
| rating | info:rating | String | 评分值 | "4.0" |
| timestamp | info:timestamp | String | 时间戳（秒） | "964982703" |
| datetime | info:datetime | String | 格式化时间 | "2000-07-30 18:45:03" |
| year | info:year | String | 评分年份 | "2000" |
| month | info:month | String | 评分月份 | "7" |

**示例数据**:
```
RowKey: "1_1_964982703"
info:userId => "1"
info:movieId => "1"
info:rating => "4.0"
info:timestamp => "964982703"
info:datetime => "2000-07-30 18:45:03"
info:year => "2000"
info:month => "7"
```

**索引建议**:
- 主索引: userId_movieId_timestamp (RowKey)
- 二级索引（可选）: userId, movieId, year

---

### 3. Tags 表 (movielens:tags) - 可选

**用途**: 存储用户标签数据

**RowKey 设计**: `userId_movieId_timestamp`

**列族**: 
- `info` - 存储标签信息

**列**:
| 列名 | 完整限定名 | 数据类型 | 说明 | 示例 |
|------|-----------|---------|------|------|
| userId | info:userId | String | 用户ID | "2" |
| movieId | info:movieId | String | 电影ID | "60756" |
| tag | info:tag | String | 标签内容 | "funny" |
| timestamp | info:timestamp | String | 时间戳 | "1445714994" |

---

## 🔧 配置参数

### 列族配置
```
{
  NAME => 'info',
  VERSIONS => 1,              # 只保留最新版本
  COMPRESSION => 'SNAPPY',    # 使用SNAPPY压缩
  BLOOMFILTER => 'ROW',       # 行级布隆过滤器
  BLOCKSIZE => '65536'        # 块大小 64KB
}
```

### 性能优化建议

1. **预分区 (Pre-splitting)**
   - Movies 表: 按 movieId 范围分区（如 0-1000, 1001-2000...）
   - Ratings 表: 按 userId 范围分区

2. **压缩**
   - 使用 SNAPPY 压缩（快速压缩/解压）
   - 或使用 GZ 压缩（高压缩比，较慢）

3. **布隆过滤器**
   - 启用行级布隆过滤器，减少磁盘I/O

4. **缓存**
   - 启用块缓存，提高读取性能

---

## 📝 HBase Shell 常用命令

### 查看表信息
```bash
# 列出所有表
list

# 列出命名空间下的表
list 'movielens:.*'

# 查看表结构
describe 'movielens:movies'

# 查看表状态
status 'movielens:movies'
```

### 数据操作
```bash
# 插入数据
put 'movielens:movies', '1', 'info:title', 'Toy Story (1995)'

# 获取单行数据
get 'movielens:movies', '1'

# 扫描表（前10条）
scan 'movielens:movies', {LIMIT => 10}

# 按列族扫描
scan 'movielens:movies', {COLUMNS => ['info:title'], LIMIT => 10}

# 删除数据
delete 'movielens:movies', '1', 'info:title'
```

### 表管理
```bash
# 禁用表
disable 'movielens:movies'

# 启用表
enable 'movielens:movies'

# 删除表（需先禁用）
disable 'movielens:movies'
drop 'movielens:movies'

# 清空表
truncate 'movielens:movies'
```

---

## 🔍 查询示例

### 1. 查询特定电影
```bash
get 'movielens:movies', '1'
```

### 2. 查询某个用户的所有评分
```bash
scan 'movielens:ratings', {ROWPREFIXFILTER => '1_'}
```

### 3. 查询某部电影的所有评分
```bash
scan 'movielens:ratings', {FILTER => "SingleColumnValueFilter('info', 'movieId', =, 'binary:1')"}
```

### 4. 按时间范围查询
```bash
scan 'movielens:ratings', {FILTER => "SingleColumnValueFilter('info', 'year', =, 'binary:2000')"}
```

### 5. 复合过滤器查询
```bash
scan 'movielens:ratings', {
  FILTER => "SingleColumnValueFilter('info', 'rating', >=, 'binary:4.0') AND SingleColumnValueFilter('info', 'year', =, 'binary:2000')"
}
```

---

## 📈 数据量估算

基于 ml-latest-small 数据集：

| 表名 | 行数 | 估算大小（未压缩） | 估算大小（SNAPPY压缩） |
|------|------|-------------------|---------------------|
| movies | ~9,742 | ~500 KB | ~200 KB |
| ratings | ~100,836 | ~5 MB | ~2 MB |
| tags | ~3,683 | ~200 KB | ~80 KB |
| **总计** | **~114,261** | **~5.7 MB** | **~2.3 MB** |

基于 ml-latest 完整数据集：

| 表名 | 行数 | 估算大小（未压缩） | 估算大小（SNAPPY压缩） |
|------|------|-------------------|---------------------|
| movies | ~86,000 | ~4 MB | ~1.5 MB |
| ratings | ~33,000,000 | ~1.5 GB | ~600 MB |
| tags | ~2,300,000 | ~120 MB | ~50 MB |
| **总计** | **~35,386,000** | **~1.6 GB** | **~650 MB** |

---

## ⚡ 性能优化

### 1. 批量导入优化
```python
# 使用批量写入
batch_size = 1000
with table.batch(batch_size=batch_size) as batch:
    for row in data:
        batch.put(row_key, row_data)
```

### 2. 读取优化
```python
# 使用扫描器时指定列
scanner = table.scan(columns=['info:title', 'info:genres'])

# 限制扫描数量
scanner = table.scan(limit=1000)
```

### 3. 连接池优化
```python
# 使用连接池
pool = ConnectionPool(size=10, host='localhost')
```

---

## 🔐 安全建议

1. **访问控制**
   - 为不同用户设置不同的权限
   - 使用 Kerberos 认证

2. **数据加密**
   - 启用传输加密（TLS）
   - 启用存储加密

3. **备份策略**
   - 定期快照备份
   - 启用 WAL（Write-Ahead Log）

---

## 📞 故障排查

### 常见问题

1. **表不存在**
   ```bash
   # 检查表是否存在
   list 'movielens:.*'
   
   # 重新创建表
   hbase shell hbase_create_tables.sh
   ```

2. **数据写入失败**
   - 检查 RegionServer 状态
   - 检查磁盘空间
   - 查看 HBase 日志

3. **查询速度慢**
   - 检查是否需要预分区
   - 启用布隆过滤器
   - 增加缓存大小

---

## 📚 参考资源

- [HBase 官方文档](https://hbase.apache.org/book.html)
- [HBase Shell 命令参考](https://hbase.apache.org/book.html#shell)
- [HBase 性能优化指南](https://hbase.apache.org/book.html#performance)

