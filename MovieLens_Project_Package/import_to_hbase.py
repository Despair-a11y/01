"""
数据导入工具 - 将 CSV 数据导入 HBase
使用方法: python import_to_hbase.py
"""
import pandas as pd
import os
from hbase_connector import get_hbase_connector
from hbase_config import HBASE_CONFIG

def import_csv_to_hbase():
    """将 CSV 数据导入 HBase"""
    
    print("=" * 60)
    print("MovieLens 数据导入 HBase 工具")
    print("=" * 60)
    
    # 检查 CSV 文件
    csv_dir = 'ml-latest-small'
    movies_csv = os.path.join(csv_dir, 'movies.csv')
    ratings_csv = os.path.join(csv_dir, 'ratings.csv')
    
    if not os.path.exists(movies_csv):
        print(f"❌ 错误: 找不到文件 {movies_csv}")
        return
    
    if not os.path.exists(ratings_csv):
        print(f"❌ 错误: 找不到文件 {ratings_csv}")
        return
    
    print(f"\n📁 CSV 文件检查完成")
    print(f"  - {movies_csv}")
    print(f"  - {ratings_csv}")
    
    # 连接 HBase
    print(f"\n🔌 正在连接 HBase...")
    print(f"  主机: {HBASE_CONFIG['host']}:{HBASE_CONFIG['port']}")
    
    try:
        connector = get_hbase_connector()
        
        if not connector.is_connected():
            print("❌ 无法连接到 HBase，请检查配置")
            return
        
        print("✅ HBase 连接成功")
        
        # 创建表
        print(f"\n📋 创建 HBase 表...")
        connector.create_tables()
        print("✅ 表创建完成")
        
        # 读取 CSV 数据
        print(f"\n📖 读取 CSV 数据...")
        
        print("  - 读取 movies.csv...")
        movies = pd.read_csv(movies_csv)
        # 提取年份
        movies['year'] = movies['title'].str.extract(r'\((\d{4})\)')
        movies['year'] = pd.to_numeric(movies['year'], errors='coerce')
        print(f"    ✅ 读取 {len(movies)} 条电影数据")
        
        print("  - 读取 ratings.csv...")
        ratings = pd.read_csv(ratings_csv)
        # 转换时间戳
        ratings['datetime'] = pd.to_datetime(ratings['timestamp'], unit='s')
        ratings['year'] = ratings['datetime'].dt.year
        ratings['month'] = ratings['datetime'].dt.month
        print(f"    ✅ 读取 {len(ratings)} 条评分数据")
        
        # 导入电影数据
        print(f"\n⬆️  导入电影数据到 HBase...")
        connector.write_movies(movies)
        print(f"✅ 电影数据导入完成")
        
        # 导入评分数据
        print(f"\n⬆️  导入评分数据到 HBase...")
        connector.write_ratings(ratings)
        print(f"✅ 评分数据导入完成")
        
        # 断开连接
        connector.disconnect()
        
        print("\n" + "=" * 60)
        print("✅ 所有数据导入完成！")
        print("=" * 60)
        print("\n💡 提示:")
        print("  1. 修改 hbase_config.py 中的 HBASE_CONFIG['enabled'] = True")
        print("  2. 修改 hbase_config.py 中的 DATA_SOURCE['type'] = 'hbase'")
        print("  3. 重启应用即可使用 HBase 数据源")
        print("")
        
    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import_csv_to_hbase()

