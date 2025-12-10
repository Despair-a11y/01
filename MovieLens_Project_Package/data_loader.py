"""
MovieLens数据加载和处理模块
支持从 CSV 文件或 HBase 数据库加载数据
"""
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
import os

# 导入 HBase 配置（可选）
try:
    from hbase_config import is_hbase_enabled, get_data_source_config
    from hbase_connector import get_hbase_connector
    HBASE_SUPPORT = True
except ImportError:
    HBASE_SUPPORT = False
    print("HBase支持未启用，使用CSV模式")


def _should_use_hbase():
    """判断是否使用 HBase 作为数据源"""
    if not HBASE_SUPPORT:
        return False
    try:
        return is_hbase_enabled()
    except:
        return False


@st.cache_data
def load_movies(data_dir='ml-latest-small'):
    """
    加载电影数据
    
    Args:
        data_dir: CSV文件目录（当使用CSV模式时）
    
    Returns:
        pd.DataFrame: 电影数据
    """
    # 如果启用了 HBase，从 HBase 加载
    if _should_use_hbase():
        try:
            connector = get_hbase_connector()
            movies = connector.read_movies()
            print("从 HBase 加载电影数据")
            return movies
        except Exception as e:
            print(f"从 HBase 加载失败，回退到 CSV: {e}")
    
    # 默认从 CSV 文件加载
    movies_path = os.path.join(data_dir, 'movies.csv')
    movies = pd.read_csv(movies_path)
    
    # 提取年份
    movies['year'] = movies['title'].str.extract(r'\((\d{4})\)')
    movies['year'] = pd.to_numeric(movies['year'], errors='coerce')
    
    return movies


@st.cache_data(ttl=3600)
def load_ratings(data_dir='ml-latest-small'):
    """
    加载评分数据
    
    Args:
        data_dir: CSV文件目录（当使用CSV模式时）
    
    Returns:
        pd.DataFrame: 评分数据
    """
    # 如果启用了 HBase，从 HBase 加载
    if _should_use_hbase():
        try:
            connector = get_hbase_connector()
            ratings = connector.read_ratings()
            print("从 HBase 加载评分数据")
            return ratings
        except Exception as e:
            print(f"从 HBase 加载失败，回退到 CSV: {e}")
    
    # 默认从 CSV 文件加载
    ratings_path = os.path.join(data_dir, 'ratings.csv')
    ratings = pd.read_csv(ratings_path)
    
    # 转换时间戳
    ratings['datetime'] = pd.to_datetime(ratings['timestamp'], unit='s')
    ratings['year'] = ratings['datetime'].dt.year
    ratings['month'] = ratings['datetime'].dt.month
    
    return ratings


@st.cache_data
def get_merged_data(movies, ratings):
    """合并电影和评分数据"""
    merged = ratings.merge(movies, on='movieId', how='left')
    return merged


@st.cache_data
def get_basic_stats(movies, ratings):
    """获取基本统计信息"""
    stats = {
        '电影总数': len(movies),
        '评分总数': len(ratings),
        '用户总数': ratings['userId'].nunique(),
        '平均评分': round(ratings['rating'].mean(), 2),
        '评分中位数': ratings['rating'].median(),
        '最高评分': ratings['rating'].max(),
        '最低评分': ratings['rating'].min(),
        '时间跨度': f"{ratings['datetime'].min().year} - {ratings['datetime'].max().year}"
    }
    return stats


@st.cache_data
def get_top_movies(movies, ratings, n=20):
    """获取评分最高的电影（至少有指定数量的评分）"""
    min_ratings = 50  # 最少评分数
    
    # 如果 movies 中已经包含统计信息（HBase 模式），直接使用
    if 'rating_count' in movies.columns and 'avg_rating' in movies.columns:
        # 确保数据类型正确
        movies['rating_count'] = pd.to_numeric(movies['rating_count'], errors='coerce').fillna(0)
        movies['avg_rating'] = pd.to_numeric(movies['avg_rating'], errors='coerce').fillna(0)
        
        top_movies = movies[movies['rating_count'] >= min_ratings]
        top_movies = top_movies.sort_values('avg_rating', ascending=False).head(n)
        return top_movies
    
    # 否则从 ratings 计算
    movie_stats = ratings.groupby('movieId').agg({
        'rating': ['mean', 'count']
    }).reset_index()
    movie_stats.columns = ['movieId', 'avg_rating', 'rating_count']
    
    # 过滤评分数量少的电影
    movie_stats = movie_stats[movie_stats['rating_count'] >= min_ratings]
    
    # 合并电影信息
    # 注意：这里只取必要的列，避免冲突
    cols_to_use = ['movieId', 'title', 'genres']
    # 确保这些列存在
    cols_to_use = [c for c in cols_to_use if c in movies.columns]
    
    top_movies = movie_stats.merge(movies[cols_to_use], on='movieId')
    top_movies = top_movies.sort_values('avg_rating', ascending=False).head(n)
    
    return top_movies


@st.cache_data
def get_genre_stats(movies, ratings):
    """获取类型统计"""
    merged = get_merged_data(movies, ratings)
    
    # 展开类型
    genre_ratings = []
    for _, row in merged.iterrows():
        if pd.notna(row['genres']) and row['genres'] != '(no genres listed)':
            for genre in row['genres'].split('|'):
                genre_ratings.append({
                    'genre': genre,
                    'rating': row['rating']
                })
    
    genre_df = pd.DataFrame(genre_ratings)
    
    # 统计每个类型的评分
    genre_stats = genre_df.groupby('genre').agg({
        'rating': ['mean', 'count']
    }).reset_index()
    genre_stats.columns = ['genre', 'avg_rating', 'count']
    genre_stats = genre_stats.sort_values('avg_rating', ascending=False)
    
    return genre_stats


@st.cache_data
def get_rating_distribution(ratings):
    """获取评分分布"""
    rating_dist = ratings['rating'].value_counts().sort_index()
    return rating_dist


@st.cache_data
def get_yearly_stats(ratings):
    """获取年度评分统计"""
    yearly = ratings.groupby('year').agg({
        'rating': ['mean', 'count']
    }).reset_index()
    yearly.columns = ['year', 'avg_rating', 'count']
    yearly = yearly.sort_values('year')
    return yearly


@st.cache_data
def search_movies(movies, keyword):
    """搜索电影"""
    if not keyword:
        return movies
    
    keyword_lower = keyword.lower()
    mask = movies['title'].str.lower().str.contains(keyword_lower, na=False, regex=False)
    return movies[mask]


@st.cache_data
def get_movie_ratings(ratings, movies, movie_id):
    """获取特定电影的评分详情"""
    movie_ratings = ratings[ratings['movieId'] == movie_id]
    movie_info = movies[movies['movieId'] == movie_id].iloc[0] if len(movies[movies['movieId'] == movie_id]) > 0 else None
    
    if movie_info is None or len(movie_ratings) == 0:
        return None, None
    
    stats = {
        '电影名称': movie_info['title'],
        '类型': movie_info['genres'],
        '评分总数': len(movie_ratings),
        '平均评分': round(movie_ratings['rating'].mean(), 2),
        '评分中位数': movie_ratings['rating'].median(),
        '最高评分': movie_ratings['rating'].max(),
        '最低评分': movie_ratings['rating'].min(),
    }
    
    return stats, movie_ratings


@st.cache_data
def get_user_stats(ratings, movies, user_id):
    """获取特定用户的评分统计"""
    user_ratings = ratings[ratings['userId'] == user_id]
    
    if len(user_ratings) == 0:
        return None, None
    
    # 合并电影信息
    user_data = user_ratings.merge(movies[['movieId', 'title', 'genres']], on='movieId', how='left')
    
    stats = {
        '用户ID': user_id,
        '评分总数': len(user_ratings),
        '平均评分': round(user_ratings['rating'].mean(), 2),
        '最高评分': user_ratings['rating'].max(),
        '最低评分': user_ratings['rating'].min(),
        '最早评分时间': user_ratings['datetime'].min(),
        '最晚评分时间': user_ratings['datetime'].max(),
    }
    
    return stats, user_data

