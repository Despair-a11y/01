"""
HBase 数据验证脚本
用于验证数据是否正确导入 HBase
"""
from hbase_connector import get_hbase_connector
from hbase_config import get_table_name
import pandas as pd


def verify_hbase_data():
    """验证 HBase 数据"""
    
    print("=" * 60)
    print("HBase 数据验证工具")
    print("=" * 60)
    
    try:
        # 连接 HBase
        print("\n🔌 连接 HBase...")
        connector = get_hbase_connector()
        
        if not connector.is_connected():
            print("❌ 无法连接到 HBase")
            return
        
        print("✅ HBase 连接成功\n")
        
        # 验证 movies 表
        print("=" * 60)
        print("验证 Movies 表")
        print("=" * 60)
        verify_movies_table(connector)
        
        # 验证 ratings 表
        print("\n" + "=" * 60)
        print("验证 Ratings 表")
        print("=" * 60)
        verify_ratings_table(connector)
        
        # 数据一致性检查
        print("\n" + "=" * 60)
        print("数据一致性检查")
        print("=" * 60)
        check_data_consistency(connector)
        
        # 断开连接
        connector.disconnect()
        
        print("\n" + "=" * 60)
        print("✅ 验证完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()


def verify_movies_table(connector):
    """验证 movies 表"""
    try:
        # 读取数据
        print("📖 读取 movies 表数据...")
        movies = connector.read_movies()
        
        print(f"✅ 成功读取 {len(movies)} 条记录")
        
        # 检查必要字段
        print("\n📋 检查字段完整性:")
        required_fields = ['movieId', 'title', 'genres']
        for field in required_fields:
            if field in movies.columns:
                non_null = movies[field].notna().sum()
                null_count = movies[field].isna().sum()
                print(f"  - {field}: {non_null} 非空, {null_count} 空值")
            else:
                print(f"  - {field}: ❌ 缺失")
        
        # 统计信息
        print("\n📊 统计信息:")
        print(f"  - 电影ID范围: {movies['movieId'].min()} - {movies['movieId'].max()}")
        if 'year' in movies.columns:
            print(f"  - 年份范围: {movies['year'].min():.0f} - {movies['year'].max():.0f}")
        
        # 显示样例数据
        print("\n📝 样例数据（前5条）:")
        print(movies.head(5).to_string())
        
        # 检查重复数据
        duplicates = movies['movieId'].duplicated().sum()
        if duplicates > 0:
            print(f"\n⚠️  警告: 发现 {duplicates} 条重复的 movieId")
        else:
            print(f"\n✅ 无重复数据")
        
    except Exception as e:
        print(f"❌ Movies 表验证失败: {e}")


def verify_ratings_table(connector):
    """验证 ratings 表"""
    try:
        # 读取数据（限制数量以避免内存溢出）
        print("📖 读取 ratings 表数据...")
        
        # 获取表对象并扫描
        table_name = get_table_name('ratings')
        table = connector.get_table(table_name)
        
        # 统计总行数
        print("📊 统计行数...")
        row_count = 0
        for _ in table.scan():
            row_count += 1
            if row_count % 10000 == 0:
                print(f"  已扫描 {row_count} 行...")
        
        print(f"✅ 总行数: {row_count:,}")
        
        # 读取样例数据
        print("\n📖 读取样例数据（前1000条）...")
        sample_data = []
        for i, (key, value) in enumerate(table.scan(limit=1000)):
            row = {}
            for col, val in value.items():
                col_name = col.decode().split(':')[1]
                row[col_name] = val.decode()
            sample_data.append(row)
        
        ratings_sample = pd.DataFrame(sample_data)
        
        # 检查必要字段
        print("\n📋 检查字段完整性:")
        required_fields = ['userId', 'movieId', 'rating', 'timestamp']
        for field in required_fields:
            if field in ratings_sample.columns:
                non_null = ratings_sample[field].notna().sum()
                null_count = ratings_sample[field].isna().sum()
                print(f"  - {field}: {non_null} 非空, {null_count} 空值")
            else:
                print(f"  - {field}: ❌ 缺失")
        
        # 统计信息
        print("\n📊 统计信息（基于样例）:")
        if 'userId' in ratings_sample.columns:
            ratings_sample['userId'] = pd.to_numeric(ratings_sample['userId'], errors='coerce')
            print(f"  - 用户ID范围: {ratings_sample['userId'].min():.0f} - {ratings_sample['userId'].max():.0f}")
        
        if 'rating' in ratings_sample.columns:
            ratings_sample['rating'] = pd.to_numeric(ratings_sample['rating'], errors='coerce')
            print(f"  - 评分范围: {ratings_sample['rating'].min()} - {ratings_sample['rating'].max()}")
            print(f"  - 平均评分: {ratings_sample['rating'].mean():.2f}")
        
        # 显示样例数据
        print("\n📝 样例数据（前5条）:")
        print(ratings_sample.head(5).to_string())
        
    except Exception as e:
        print(f"❌ Ratings 表验证失败: {e}")


def check_data_consistency(connector):
    """检查数据一致性"""
    try:
        print("📋 检查数据一致性...")
        
        # 读取数据
        movies = connector.read_movies()
        
        # 从 ratings 表读取样例数据
        table_name = get_table_name('ratings')
        table = connector.get_table(table_name)
        
        sample_data = []
        for i, (key, value) in enumerate(table.scan(limit=1000)):
            row = {}
            for col, val in value.items():
                col_name = col.decode().split(':')[1]
                row[col_name] = val.decode()
            sample_data.append(row)
        
        ratings_sample = pd.DataFrame(sample_data)
        
        if 'movieId' in ratings_sample.columns:
            ratings_sample['movieId'] = pd.to_numeric(ratings_sample['movieId'], errors='coerce')
            
            # 检查引用完整性
            movie_ids_in_movies = set(movies['movieId'])
            movie_ids_in_ratings = set(ratings_sample['movieId'].dropna())
            
            # 找出 ratings 中但不在 movies 中的 movieId
            orphan_movies = movie_ids_in_ratings - movie_ids_in_movies
            
            print(f"\n  - Movies 表中的电影数: {len(movie_ids_in_movies)}")
            print(f"  - Ratings 样例中涉及的电影数: {len(movie_ids_in_ratings)}")
            
            if orphan_movies:
                print(f"  - ⚠️  发现 {len(orphan_movies)} 个孤儿电影ID（在ratings中但不在movies中）")
                print(f"    示例: {list(orphan_movies)[:5]}")
            else:
                print(f"  - ✅ 引用完整性检查通过")
        
        # 检查评分值范围
        if 'rating' in ratings_sample.columns:
            ratings_sample['rating'] = pd.to_numeric(ratings_sample['rating'], errors='coerce')
            valid_ratings = ratings_sample['rating'].dropna()
            invalid_ratings = valid_ratings[(valid_ratings < 0.5) | (valid_ratings > 5.0)]
            
            if len(invalid_ratings) > 0:
                print(f"  - ⚠️  发现 {len(invalid_ratings)} 个无效评分值")
            else:
                print(f"  - ✅ 评分值范围检查通过（0.5-5.0）")
        
    except Exception as e:
        print(f"❌ 一致性检查失败: {e}")


if __name__ == '__main__':
    verify_hbase_data()

