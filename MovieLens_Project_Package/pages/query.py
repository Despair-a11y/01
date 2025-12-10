"""
数据查询页面 - 电影查询模块
"""
import streamlit as st
import pandas as pd
from data_loader import (
    search_movies,
    get_movie_ratings
)


def show(movies, ratings):
    """显示数据查询页面"""
    st.title("🔍 数据查询")
    st.markdown("---")
    
    # 直接显示电影查询
    movie_query_section(movies, ratings)


def movie_query_section(movies, ratings):
    """电影查询部分"""
    st.subheader("🎬 电影信息查询")
    
    # 搜索框
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_keyword = st.text_input(
            "输入电影名称关键词",
            placeholder="例如: Toy Story, Matrix, Star Wars..."
        )
    
    with col2:
        search_button = st.button("🔍 搜索", use_container_width=True)
    
    if search_keyword or search_button:
        # 搜索电影
        search_results = search_movies(movies, search_keyword)
        
        if len(search_results) == 0:
            st.warning(f"未找到包含 '{search_keyword}' 的电影")
        else:
            st.success(f"找到 {len(search_results)} 部相关电影")
            
            # 显示搜索结果
            st.subheader("📝 搜索结果")
            
            # 添加评分统计
            search_results_with_stats = search_results.copy()
            
            # 计算每部电影的评分统计
            rating_stats = ratings.groupby('movieId').agg({
                'rating': ['count', 'mean']
            }).reset_index()
            
            rating_stats.columns = ['movieId', 'rating_count', 'avg_rating']

            # 避免列名冲突，先删除 search_results 中的统计列（如果存在）
            cols_to_drop = ['rating_count', 'avg_rating']
            search_results_with_stats = search_results.drop(columns=[c for c in cols_to_drop if c in search_results.columns])

            search_results_with_stats = search_results_with_stats.merge(
                rating_stats,
                on='movieId',
                how='left'
            )
            
            # 填充缺失值
            search_results_with_stats['rating_count'] = search_results_with_stats['rating_count'].fillna(0).astype(int)
            search_results_with_stats['avg_rating'] = search_results_with_stats['avg_rating'].fillna(0).round(2)
            
            # 显示表格
            display_df = search_results_with_stats[['movieId', 'title', 'genres', 'rating_count', 'avg_rating']].copy()
            display_df.columns = ['电影ID', '电影名称', '类型', '评分数量', '平均评分']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "电影ID": st.column_config.NumberColumn(
                        "电影ID",
                        width="small",
                    ),
                    "电影名称": st.column_config.TextColumn(
                        "电影名称",
                        width="large",
                    ),
                    "类型": st.column_config.TextColumn(
                        "类型",
                        width="medium",
                    ),
                    "评分数量": st.column_config.NumberColumn(
                        "评分数量",
                        width="small",
                    ),
                    "平均评分": st.column_config.ProgressColumn(
                        "平均评分",
                        format="%.2f",
                        min_value=0,
                        max_value=5,
                        width="medium",
                    ),
                }
            )
            
            # 选择电影查看详情
            st.markdown("---")
            st.subheader("📊 电影详细信息")
            
            selected_movie = st.selectbox(
                "选择一部电影查看详情",
                options=search_results_with_stats['movieId'].tolist(),
                format_func=lambda x: search_results_with_stats[
                    search_results_with_stats['movieId'] == x
                ]['title'].values[0]
            )
            
            if selected_movie:
                show_movie_details(selected_movie, movies, ratings)
    else:
        st.info("💡 请输入电影名称关键词进行搜索")
        
        # 显示随机推荐
        st.subheader("🎲 随机推荐")
        random_movies = movies.sample(10)
        
        # 添加评分信息
        rating_stats = ratings.groupby('movieId').agg({
            'rating': ['count', 'mean']
        }).reset_index()
        rating_stats.columns = ['movieId', 'rating_count', 'avg_rating']
        
        # 避免列名冲突，先删除 random_movies 中的统计列（如果存在）
        cols_to_drop = ['rating_count', 'avg_rating']
        random_movies = random_movies.drop(columns=[c for c in cols_to_drop if c in random_movies.columns])

        random_movies = random_movies.merge(rating_stats, on='movieId', how='left')
        random_movies['rating_count'] = random_movies['rating_count'].fillna(0).astype(int)
        random_movies['avg_rating'] = random_movies['avg_rating'].fillna(0).round(2)
        
        display_df = random_movies[['movieId', 'title', 'genres', 'rating_count', 'avg_rating']].copy()
        display_df.columns = ['电影ID', '电影名称', '类型', '评分数量', '平均评分']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def show_movie_details(movie_id, movies, ratings):
    """显示电影详细信息"""
    stats, movie_ratings = get_movie_ratings(ratings, movies, movie_id)
    
    if stats is None:
        st.warning("该电影暂无评分数据")
        return
    
    # 显示基本信息
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 基本信息")
        st.write(f"**电影名称：** {stats['电影名称']}")
        st.write(f"**类型：** {stats['类型']}")
        st.write(f"**电影ID：** {movie_id}")
    
    with col2:
        st.markdown("### ⭐ 评分统计")
        st.metric("评分总数", f"{stats['评分总数']:,}")
        st.metric("平均评分", stats['平均评分'])
        st.metric("评分范围", f"{stats['最低评分']} - {stats['最高评分']}")
    
    # 评分分布统计表
    st.markdown("### 📊 评分分布统计")
    rating_dist = movie_ratings['rating'].value_counts().sort_index()
    rating_dist_df = pd.DataFrame({
        '评分': rating_dist.index,
        '数量': rating_dist.values,
        '占比': (rating_dist.values / rating_dist.sum() * 100).round(2)
    })
    rating_dist_df['占比'] = rating_dist_df['占比'].astype(str) + '%'
    st.dataframe(rating_dist_df, use_container_width=True, hide_index=True)
    
    # 年度评分统计
    if 'datetime' in movie_ratings.columns:
        st.markdown("### 📅 年度评分统计")
        
        # 按年份统计
        movie_ratings = movie_ratings.copy()
        movie_ratings['year'] = pd.to_datetime(movie_ratings['datetime']).dt.year
        yearly_ratings = movie_ratings.groupby('year').agg({
            'rating': ['count', 'mean']
        }).reset_index()
        yearly_ratings.columns = ['年份', '评分数量', '平均评分']
        yearly_ratings['平均评分'] = yearly_ratings['平均评分'].round(2)
        
        st.dataframe(yearly_ratings, use_container_width=True, hide_index=True)
    
    # 最新评分
    st.markdown("### 📝 最新评分记录")
    latest_ratings = movie_ratings.nlargest(20, 'timestamp')[
        ['userId', 'rating', 'datetime']
    ].copy()
    latest_ratings.columns = ['用户ID', '评分', '评分时间']
    st.dataframe(latest_ratings, use_container_width=True, hide_index=True)
