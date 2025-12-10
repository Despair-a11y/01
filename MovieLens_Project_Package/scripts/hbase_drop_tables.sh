#!/bin/bash
# HBase 删除表脚本
# 使用方法: hbase shell hbase_drop_tables.sh
# 警告：此脚本会删除所有 MovieLens 表数据！

echo "======================================"
echo "删除 MovieLens HBase 表"
echo "警告：此操作不可恢复！"
echo "======================================"

# 禁用并删除 movies 表
echo "删除 movies 表..."
disable 'movielens:movies'
drop 'movielens:movies'

# 禁用并删除 ratings 表
echo "删除 ratings 表..."
disable 'movielens:ratings'
drop 'movielens:ratings'

# 禁用并删除 tags 表
echo "删除 tags 表..."
disable 'movielens:tags'
drop 'movielens:tags'

# 删除命名空间
echo "删除命名空间..."
drop_namespace 'movielens'

# 列出剩余表
echo "======================================"
echo "当前表列表:"
list

echo "======================================"
echo "✅ HBase 表删除完成！"
echo "======================================"

