"""
HBase 连接器模块
提供 HBase 数据库的连接和操作功能
"""
import pandas as pd
from hbase_config import get_hbase_config, get_table_name, get_column_family, is_hbase_enabled

# 注意：这里使用条件导入，避免在未安装 happybase 时报错
try:
    import happybase
    HAPPYBASE_AVAILABLE = True
except ImportError:
    HAPPYBASE_AVAILABLE = False
    print("Warning: happybase not installed. HBase功能不可用，将使用CSV模式。")


class HBaseConnector:
    """HBase 连接器类"""
    
    def __init__(self):
        """初始化 HBase 连接"""
        self.connection = None
        self.config = get_hbase_config()
        
        if not HAPPYBASE_AVAILABLE:
            print("HBase connector initialized in CSV-only mode")
            return
        
        if is_hbase_enabled():
            try:
                self.connect()
            except Exception as e:
                print(f"无法连接到 HBase: {e}")
                print("将使用 CSV 文件作为数据源")
    
    def connect(self):
        """连接到 HBase"""
        if not HAPPYBASE_AVAILABLE:
            raise ImportError("happybase 未安装，无法连接 HBase")
        
        try:
            self.connection = happybase.Connection(
                host=self.config['host'],
                port=self.config['port'],
                timeout=self.config['timeout']
            )
            print(f"成功连接到 HBase: {self.config['host']}:{self.config['port']}")
        except Exception as e:
            print(f"HBase 连接失败: {e}")
            raise
    
    def disconnect(self):
        """断开 HBase 连接"""
        if self.connection:
            self.connection.close()
            print("HBase 连接已关闭")
    
    def is_connected(self):
        """检查是否已连接"""
        return self.connection is not None and HAPPYBASE_AVAILABLE
    
    def get_table(self, table_name):
        """
        获取表对象
        
        Args:
            table_name: 表名
        
        Returns:
            happybase.Table: 表对象
        """
        if not self.is_connected():
            raise ConnectionError("未连接到 HBase")
        
        return self.connection.table(table_name)
    
    def read_movies(self):
        """
        从 HBase 读取电影数据
        
        Returns:
            pd.DataFrame: 电影数据
        """
        if not self.is_connected():
            raise ConnectionError("未连接到 HBase")
        
        table_name = get_table_name('movies')
        table = self.get_table(table_name)
        
        data = []
        for key, value in table.scan():
            row = {'movieId': int(key.decode())}
            for col, val in value.items():
                col_name = col.decode().split(':')[1]
                row[col_name] = val.decode()
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # 数据类型转换
        if 'movieId' in df.columns:
            df['movieId'] = pd.to_numeric(df['movieId'], errors='coerce')
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
        
        return df
    
    def read_ratings(self):
        """
        从 HBase 读取评分数据
        
        Returns:
            pd.DataFrame: 评分数据
        """
        if not self.is_connected():
            raise ConnectionError("未连接到 HBase")
        
        table_name = get_table_name('ratings')
        table = self.get_table(table_name)
        
        data = []
        for key, value in table.scan():
            row = {}
            for col, val in value.items():
                col_name = col.decode().split(':')[1]
                row[col_name] = val.decode()
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # 如果 DataFrame 为空，返回带有正确列名的空 DataFrame
        if df.empty:
            columns = ['userId', 'movieId', 'rating', 'timestamp', 'datetime', 'year', 'month']
            return pd.DataFrame(columns=columns)
            
        # 数据类型转换
        if 'userId' in df.columns:
            df['userId'] = pd.to_numeric(df['userId'], errors='coerce')
        if 'movieId' in df.columns:
            df['movieId'] = pd.to_numeric(df['movieId'], errors='coerce')
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
        if 'month' in df.columns:
            df['month'] = pd.to_numeric(df['month'], errors='coerce')
        
        return df
    
    def write_movies(self, movies_df):
        """
        将电影数据写入 HBase
        
        Args:
            movies_df: 电影数据 DataFrame
        """
        if not self.is_connected():
            raise ConnectionError("未连接到 HBase")
        
        table_name = get_table_name('movies')
        table = self.get_table(table_name)
        
        batch = table.batch(batch_size=self.config['batch_size'])
        
        for _, row in movies_df.iterrows():
            row_key = str(row['movieId']).encode()
            data = {
                b'info:title': str(row['title']).encode(),
                b'info:genres': str(row['genres']).encode(),
            }
            
            if 'year' in row and pd.notna(row['year']):
                data[b'info:year'] = str(int(row['year'])).encode()
            
            batch.put(row_key, data)
        
        batch.send()
        print(f"成功写入 {len(movies_df)} 条电影数据到 HBase")
    
    def write_ratings(self, ratings_df):
        """
        将评分数据写入 HBase
        
        Args:
            ratings_df: 评分数据 DataFrame
        """
        if not self.is_connected():
            raise ConnectionError("未连接到 HBase")
        
        table_name = get_table_name('ratings')
        table = self.get_table(table_name)
        
        batch = table.batch(batch_size=self.config['batch_size'])
        
        for idx, row in ratings_df.iterrows():
            row_key = f"{row['userId']}_{row['movieId']}_{row['timestamp']}".encode()
            data = {
                b'info:userId': str(row['userId']).encode(),
                b'info:movieId': str(row['movieId']).encode(),
                b'info:rating': str(row['rating']).encode(),
                b'info:timestamp': str(row['timestamp']).encode(),
            }
            
            if 'datetime' in row and pd.notna(row['datetime']):
                data[b'info:datetime'] = str(row['datetime']).encode()
            if 'year' in row and pd.notna(row['year']):
                data[b'info:year'] = str(int(row['year'])).encode()
            if 'month' in row and pd.notna(row['month']):
                data[b'info:month'] = str(int(row['month'])).encode()
            
            batch.put(row_key, data)
        
        batch.send()
        print(f"成功写入 {len(ratings_df)} 条评分数据到 HBase")
    
    def create_tables(self):
        """创建 HBase 表"""
        if not self.is_connected():
            raise ConnectionError("未连接到 HBase")
        
        # 创建 movies 表
        movies_table = get_table_name('movies')
        if movies_table.encode() not in self.connection.tables():
            self.connection.create_table(
                movies_table,
                {'info': dict()}
            )
            print(f"创建表: {movies_table}")
        
        # 创建 ratings 表
        ratings_table = get_table_name('ratings')
        if ratings_table.encode() not in self.connection.tables():
            self.connection.create_table(
                ratings_table,
                {'info': dict()}
            )
            print(f"创建表: {ratings_table}")
    
    def delete_tables(self):
        """删除 HBase 表（慎用）"""
        if not self.is_connected():
            raise ConnectionError("未连接到 HBase")
        
        tables_to_delete = [
            get_table_name('movies'),
            get_table_name('ratings')
        ]
        
        for table_name in tables_to_delete:
            if table_name.encode() in self.connection.tables():
                self.connection.delete_table(table_name, disable=True)
                print(f"删除表: {table_name}")


# 全局连接器实例（单例模式）
_hbase_connector = None


def get_hbase_connector():
    """获取 HBase 连接器实例（单例）"""
    global _hbase_connector
    if _hbase_connector is None:
        _hbase_connector = HBaseConnector()
    return _hbase_connector

