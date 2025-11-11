#!/bin/bash
# HBase 查询示例脚本
# 使用方法: hbase shell hbase_query_examples.sh

echo "======================================"
echo "HBase 查询示例"
echo "======================================"

# 1. 查看表结构
echo ""
echo "1. 查看 movies 表结构"
echo "--------------------------------------"
describe 'movielens:movies'

# 2. 统计表行数
echo ""
echo "2. 统计各表行数"
echo "--------------------------------------"
count 'movielens:movies'
count 'movielens:ratings'

# 3. 查询前10部电影
echo ""
echo "3. 查询前10部电影"
echo "--------------------------------------"
scan 'movielens:movies', {LIMIT => 10}

# 4. 获取特定电影信息（电影ID=1）
echo ""
echo "4. 获取电影ID=1的信息"
echo "--------------------------------------"
get 'movielens:movies', '1'

# 5. 只查询电影标题
echo ""
echo "5. 查询前10部电影的标题"
echo "--------------------------------------"
scan 'movielens:movies', {COLUMNS => ['info:title'], LIMIT => 10}

# 6. 查询评分数据样例
echo ""
echo "6. 查询评分数据样例（前5条）"
echo "--------------------------------------"
scan 'movielens:ratings', {LIMIT => 5}

# 7. 查询用户ID=1的所有评分
echo ""
echo "7. 查询用户ID=1的评分"
echo "--------------------------------------"
scan 'movielens:ratings', {ROWPREFIXFILTER => '1_', LIMIT => 10}

# 8. 查询高分电影（评分>=4.5）
echo ""
echo "8. 查询高分评分记录（评分>=4.5）"
echo "--------------------------------------"
scan 'movielens:ratings', {
  FILTER => "SingleColumnValueFilter('info', 'rating', >=, 'binary:4.5')",
  LIMIT => 10
}

# 9. 按年份查询（2000年的评分）
echo ""
echo "9. 查询2000年的评分记录"
echo "--------------------------------------"
scan 'movielens:ratings', {
  FILTER => "SingleColumnValueFilter('info', 'year', =, 'binary:2000')",
  LIMIT => 10
}

# 10. 查询表状态
echo ""
echo "10. 查看表状态"
echo "--------------------------------------"
status 'movielens:movies'
status 'movielens:ratings'

echo ""
echo "======================================"
echo "✅ 查询示例执行完成！"
echo "======================================"

