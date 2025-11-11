#!/bin/bash
# HBase 建表脚本
# 使用方法: hbase shell hbase_create_tables.sh

echo "======================================"
echo "创建 MovieLens HBase 表"
echo "======================================"

# 创建命名空间
create_namespace 'movielens'

# 创建 movies 表
echo "创建 movies 表..."
create 'movielens:movies', {NAME => 'info', VERSIONS => 1, COMPRESSION => 'SNAPPY'}

# 创建 ratings 表  
echo "创建 ratings 表..."
create 'movielens:ratings', {NAME => 'info', VERSIONS => 1, COMPRESSION => 'SNAPPY'}

# 创建 tags 表（可选）
echo "创建 tags 表..."
create 'movielens:tags', {NAME => 'info', VERSIONS => 1, COMPRESSION => 'SNAPPY'}

# 列出所有表
echo "======================================"
echo "当前表列表:"
list 'movielens:.*'

# 显示表结构
echo "======================================"
echo "Movies 表结构:"
describe 'movielens:movies'

echo "======================================"
echo "Ratings 表结构:"
describe 'movielens:ratings'

echo "======================================"
echo "✅ HBase 表创建完成！"
echo "======================================"

