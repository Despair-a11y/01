"""
数据总览页面
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import (
    get_basic_stats, 
    get_top_movies, 
    get_rating_distribution,
    get_genre_stats
)


def show(movies, ratings):
    """显示数据总览页面"""
    st.title("📊 数据总览")
    st.markdown("---")
    
    # 基础统计信息
    st.subheader("📈 基础统计信息")
    stats = get_basic_stats(movies, ratings)
    
    # 第一行统计卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎬 电影总数", f"{stats['电影总数']:,}")
    with col2:
        st.metric("⭐ 评分总数", f"{stats['评分总数']:,}")
    with col3:
        st.metric("👥 用户总数", f"{stats['用户总数']:,}")
    with col4:
        st.metric("📊 平均评分", stats['平均评分'])
    
    # 第二行统计卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 评分中位数", stats['评分中位数'])
    with col2:
        st.metric("⬆️ 最高评分", stats['最高评分'])
    with col3:
        st.metric("⬇️ 最低评分", stats['最低评分'])
    with col4:
        st.metric("📅 时间跨度", stats['时间跨度'])
    
    st.markdown("---")
    
    # 评分分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⭐ 评分分布")
        rating_dist = get_rating_distribution(ratings)
        
        fig = px.bar(
            x=rating_dist.index,
            y=rating_dist.values,
            labels={'x': '评分', 'y': '数量'},
            title='评分分布统计',
            color=rating_dist.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            xaxis_title="评分",
            yaxis_title="数量",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示评分占比
        st.write("**评分占比：**")
        rating_pct = (rating_dist / rating_dist.sum() * 100).round(2)
        for rating, pct in rating_pct.items():
            st.write(f"⭐ {rating} 分: {pct}%")
    
    with col2:
        st.subheader("🎭 类型统计 (Top 10)")
        genre_stats = get_genre_stats(movies, ratings)
        top_genres = genre_stats.head(10)
        
        fig = px.bar(
            top_genres,
            x='avg_rating',
            y='genre',
            orientation='h',
            labels={'avg_rating': '平均评分', 'genre': '类型'},
            title='各类型平均评分 Top 10',
            color='avg_rating',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 热门电影排行榜
    st.subheader("🏆 高分电影排行榜 (至少50个评分)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        top_n = st.slider("显示数量", min_value=5, max_value=50, value=20, step=5)
    
    top_movies = get_top_movies(movies, ratings, n=top_n)
    
    # 格式化显示
    display_df = top_movies.copy()
    display_df['avg_rating'] = display_df['avg_rating'].round(2)
    display_df['ranking'] = range(1, len(display_df) + 1)
    display_df = display_df[['ranking', 'title', 'genres', 'avg_rating', 'rating_count']]
    display_df.columns = ['排名', '电影名称', '类型', '平均评分', '评分数量']
    
    # 显示表格
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "排名": st.column_config.NumberColumn(
                "排名",
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
            "平均评分": st.column_config.ProgressColumn(
                "平均评分",
                format="%.2f",
                min_value=0,
                max_value=5,
                width="medium",
            ),
            "评分数量": st.column_config.NumberColumn(
                "评分数量",
                width="small",
            ),
        }
    )
    
    # 可视化热门电影
    st.subheader("📊 热门电影可视化")
    
    fig = go.Figure()
    
    # 添加平均评分柱状图
    fig.add_trace(go.Bar(
        name='平均评分',
        x=top_movies['title'][:15],  # 只显示前15个
        y=top_movies['avg_rating'][:15],
        marker_color='lightblue',
        yaxis='y',
        offsetgroup=1,
    ))
    
    # 添加评分数量
    fig.add_trace(go.Bar(
        name='评分数量',
        x=top_movies['title'][:15],
        y=top_movies['rating_count'][:15],
        marker_color='lightcoral',
        yaxis='y2',
        offsetgroup=2,
    ))
    
    # 更新布局
    fig.update_layout(
        title='热门电影：平均评分 vs 评分数量',
        xaxis=dict(title='电影名称', tickangle=-45),
        yaxis=dict(
            title='平均评分',
            titlefont=dict(color='lightblue'),
            tickfont=dict(color='lightblue'),
            range=[0, 5]
        ),
        yaxis2=dict(
            title='评分数量',
            titlefont=dict(color='lightcoral'),
            tickfont=dict(color='lightcoral'),
            anchor='x',
            overlaying='y',
            side='right'
        ),
        barmode='group',
        height=500,
        legend=dict(x=0, y=1.1, orientation='h')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 数据质量信息
    st.subheader("📋 数据质量信息")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**电影数据：**")
        st.write(f"- 总行数: {len(movies):,}")
        st.write(f"- 缺失值: {movies.isnull().sum().sum()}")
        st.write(f"- 无类型电影: {len(movies[movies['genres'] == '(no genres listed)'])}")
        
    with col2:
        st.write("**评分数据：**")
        st.write(f"- 总行数: {len(ratings):,}")
        st.write(f"- 缺失值: {ratings.isnull().sum().sum()}")
        st.write(f"- 最活跃用户评分数: {ratings['userId'].value_counts().max()}")
        st.write(f"- 最少活跃用户评分数: {ratings['userId'].value_counts().min()}")

