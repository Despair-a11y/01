"""
HBase 数据库配置模块
"""
import os

# HBase 连接配置
HBASE_CONFIG = {
    # HBase Thrift 服务器配置
    'host': 'localhost',
    'port': 9099,
    'timeout': 3000,
    
    # 表名配置
    'tables': {
        'movies': 'movies',
        'ratings': 'ratings',
        'tags': 'tags'
    },
    
    # 列族配置
    'column_families': {
        'movies': {
            'info': ['movieId', 'title', 'genres', 'year']
        },
        'ratings': {
            'info': ['userId', 'movieId', 'rating', 'timestamp', 'datetime', 'year', 'month']
        },
        'tags': {
            'info': ['userId', 'movieId', 'tag', 'timestamp']
        }
    },
    
    # 是否启用 HBase（已启用，用于演示导入功能）
    'enabled': True,
    
    # 批量写入配置
    'batch_size': 1000,
    
    # 连接池配置
    'pool_size': 10,
}

# 数据源配置
DATA_SOURCE = {
    'type': 'hbase',  # 可选: 'csv' 或 'hbase'
    'csv_dir': 'ml-latest-small',  # CSV 文件目录
}


def get_hbase_config():
    """获取 HBase 配置"""
    return HBASE_CONFIG.copy()


def get_data_source_config():
    """获取数据源配置"""
    return DATA_SOURCE.copy()


def is_hbase_enabled():
    """检查是否启用 HBase"""
    return HBASE_CONFIG.get('enabled', False) and DATA_SOURCE.get('type') == 'hbase'


def get_table_name(table_type):
    """
    获取表名
    
    Args:
        table_type: 表类型 ('movies', 'ratings', 'tags')
    
    Returns:
        str: 表名
    """
    return HBASE_CONFIG['tables'].get(table_type, '')


def get_column_family(table_type):
    """
    获取列族配置
    
    Args:
        table_type: 表类型 ('movies', 'ratings', 'tags')
    
    Returns:
        dict: 列族配置
    """
    return HBASE_CONFIG['column_families'].get(table_type, {})


# 环境变量覆盖配置（可选）
def load_config_from_env():
    """从环境变量加载配置"""
    if os.getenv('HBASE_HOST'):
        HBASE_CONFIG['host'] = os.getenv('HBASE_HOST')
    
    if os.getenv('HBASE_PORT'):
        HBASE_CONFIG['port'] = int(os.getenv('HBASE_PORT'))
    
    if os.getenv('HBASE_ENABLED'):
        HBASE_CONFIG['enabled'] = os.getenv('HBASE_ENABLED').lower() == 'true'
    
    if os.getenv('DATA_SOURCE'):
        DATA_SOURCE['type'] = os.getenv('DATA_SOURCE')


# 自动加载环境变量配置
load_config_from_env()

