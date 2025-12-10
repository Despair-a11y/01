"""
可视化分析页面
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_loader import (
    get_merged_data,
    get_yearly_stats,
    get_genre_stats,
    get_rating_distribution
)


def show(movies, ratings):
    """显示可视化分析页面"""
    st.title("📈 可视化分析")
    st.markdown("---")
    
    # 获取合并数据
    merged_data = get_merged_data(movies, ratings)
    
    # 侧边栏筛选
    st.sidebar.markdown("### 📊 数据筛选")
    
    # 年份筛选
    if 'year' in ratings.columns:
        year_range = st.sidebar.slider(
            "选择年份范围",
            min_value=int(ratings['year'].min()),
            max_value=int(ratings['year'].max()),
            value=(int(ratings['year'].min()), int(ratings['year'].max()))
        )
        filtered_ratings = ratings[
            (ratings['year'] >= year_range[0]) & 
            (ratings['year'] <= year_range[1])
        ]
    else:
        filtered_ratings = ratings
    
    # 评分筛选
    rating_range = st.sidebar.slider(
        "选择评分范围",
        min_value=0.5,
        max_value=5.0,
        value=(0.5, 5.0),
        step=0.5
    )
    filtered_ratings = filtered_ratings[
        (filtered_ratings['rating'] >= rating_range[0]) & 
        (filtered_ratings['rating'] <= rating_range[1])
    ]
    
    st.info(f"📊 当前筛选条件下共有 **{len(filtered_ratings):,}** 条评分数据")
    
    # Tab 布局
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 评分趋势分析", 
        "🎭 类型分析", 
        "📅 时间序列分析", 
        "📈 高级分析"
    ])
    
    # Tab 1: 评分趋势分析
    with tab1:
        st.subheader("⭐ 评分分布分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 评分分布直方图
            rating_dist = get_rating_distribution(filtered_ratings)
            
            fig = px.histogram(
                filtered_ratings,
                x='rating',
                nbins=10,
                title='评分分布直方图',
                labels={'rating': '评分', 'count': '数量'},
                color_discrete_sequence=['#636EFA']
            )
            fig.update_layout(
                xaxis_title="评分",
                yaxis_title="数量",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 评分分布饼图
            fig = px.pie(
                values=rating_dist.values,
                names=rating_dist.index,
                title='评分分布占比',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # 评分箱线图
        st.subheader("📦 评分箱线图分析")
        
        fig = go.Figure()
        fig.add_trace(go.Box(
            y=filtered_ratings['rating'],
            name='评分分布',
            marker_color='lightseagreen',
            boxmean='sd'  # 显示均值和标准差
        ))
        
        fig.update_layout(
            title='评分箱线图（显示中位数、四分位数和异常值）',
            yaxis_title="评分",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 统计描述
        st.subheader("📊 评分统计描述")
        stats_df = filtered_ratings['rating'].describe().to_frame()
        stats_df.columns = ['统计值']
        stats_df.index = ['数量', '平均值', '标准差', '最小值', '25%分位', '50%分位', '75%分位', '最大值']
        st.dataframe(stats_df, use_container_width=True)
    
    # Tab 2: 类型分析
    with tab2:
        st.subheader("🎭 电影类型分析")
        
        # 合并筛选后的数据
        filtered_merged = filtered_ratings.merge(movies, on='movieId', how='left')
        
        # 展开类型统计
        genre_ratings = []
        for _, row in filtered_merged.iterrows():
            if pd.notna(row['genres']) and row['genres'] != '(no genres listed)':
                for genre in row['genres'].split('|'):
                    genre_ratings.append({
                        'genre': genre,
                        'rating': row['rating']
                    })
        
        genre_df = pd.DataFrame(genre_ratings)
        
        if len(genre_df) > 0:
            # 类型评分统计
            genre_stats = genre_df.groupby('genre').agg({
                'rating': ['mean', 'count', 'std']
            }).reset_index()
            genre_stats.columns = ['genre', 'avg_rating', 'count', 'std']
            genre_stats = genre_stats.sort_values('count', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 各类型评分数量
                fig = px.bar(
                    genre_stats,
                    x='genre',
                    y='count',
                    title='各类型评分数量',
                    labels={'genre': '类型', 'count': '评分数量'},
                    color='count',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(
                    xaxis_title="类型",
                    yaxis_title="评分数量",
                    xaxis={'categoryorder': 'total descending'},
                    height=400
                )
                fig.update_xaxes(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 各类型平均评分
                fig = px.bar(
                    genre_stats.sort_values('avg_rating', ascending=False),
                    x='genre',
                    y='avg_rating',
                    title='各类型平均评分',
                    labels={'genre': '类型', 'avg_rating': '平均评分'},
                    color='avg_rating',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    xaxis_title="类型",
                    yaxis_title="平均评分",
                    xaxis={'categoryorder': 'total descending'},
                    height=400
                )
                fig.update_xaxes(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # 类型评分小提琴图
            st.subheader("🎻 类型评分分布（小提琴图）")
            
            # 选择显示的类型
            top_genres = genre_stats.head(10)['genre'].tolist()
            selected_genres = st.multiselect(
                "选择要显示的类型（默认显示Top 10）",
                options=sorted(genre_df['genre'].unique()),
                default=top_genres
            )
            
            if selected_genres:
                genre_violin_data = genre_df[genre_df['genre'].isin(selected_genres)]
                
                fig = px.violin(
                    genre_violin_data,
                    x='genre',
                    y='rating',
                    box=True,
                    points='outliers',
                    title='各类型评分分布（小提琴图）',
                    labels={'genre': '类型', 'rating': '评分'},
                    color='genre'
                )
                fig.update_layout(
                    height=500,
                    showlegend=False
                )
                fig.update_xaxes(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # 类型统计表格
            st.subheader("📋 类型详细统计")
            display_genre_stats = genre_stats.copy()
            display_genre_stats['avg_rating'] = display_genre_stats['avg_rating'].round(2)
            display_genre_stats['std'] = display_genre_stats['std'].round(2)
            display_genre_stats.columns = ['类型', '平均评分', '评分数量', '标准差']
            st.dataframe(display_genre_stats, use_container_width=True, hide_index=True)
        else:
            st.warning("当前筛选条件下没有类型数据")
    
    # Tab 3: 时间序列分析
    with tab3:
        st.subheader("📅 时间序列分析")
        
        if 'year' in filtered_ratings.columns:
            # 年度评分趋势
            yearly_stats = filtered_ratings.groupby('year').agg({
                'rating': ['mean', 'count']
            }).reset_index()
            yearly_stats.columns = ['year', 'avg_rating', 'count']
            
            # 创建双轴图
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # 添加平均评分线
            fig.add_trace(
                go.Scatter(
                    x=yearly_stats['year'],
                    y=yearly_stats['avg_rating'],
                    name="平均评分",
                    line=dict(color='blue', width=2),
                    mode='lines+markers'
                ),
                secondary_y=False,
            )
            
            # 添加评分数量柱状图
            fig.add_trace(
                go.Bar(
                    x=yearly_stats['year'],
                    y=yearly_stats['count'],
                    name="评分数量",
                    marker_color='lightblue',
                    opacity=0.6
                ),
                secondary_y=True,
            )
            
            # 更新坐标轴标题
            fig.update_xaxes(title_text="年份")
            fig.update_yaxes(title_text="平均评分", secondary_y=False)
            fig.update_yaxes(title_text="评分数量", secondary_y=True)
            
            fig.update_layout(
                title='年度评分趋势分析',
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 月度评分趋势
            if 'month' in filtered_ratings.columns:
                st.subheader("📆 月度评分趋势")
                
                monthly_stats = filtered_ratings.groupby('month').agg({
                    'rating': ['mean', 'count']
                }).reset_index()
                monthly_stats.columns = ['month', 'avg_rating', 'count']
                
                month_names = {
                    1: '一月', 2: '二月', 3: '三月', 4: '四月',
                    5: '五月', 6: '六月', 7: '七月', 8: '八月',
                    9: '九月', 10: '十月', 11: '十一月', 12: '十二月'
                }
                monthly_stats['month_name'] = monthly_stats['month'].map(month_names)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.line(
                        monthly_stats,
                        x='month_name',
                        y='avg_rating',
                        title='各月份平均评分',
                        markers=True,
                        labels={'month_name': '月份', 'avg_rating': '平均评分'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(
                        monthly_stats,
                        x='month_name',
                        y='count',
                        title='各月份评分数量',
                        labels={'month_name': '月份', 'count': '评分数量'},
                        color='count',
                        color_continuous_scale='Greens'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("时间数据不可用")
    
    # Tab 4: 高级分析
    with tab4:
        st.subheader("📊 高级分析")
        
        # 用户活跃度分析
        st.subheader("👥 用户活跃度分析")
        
        user_activity = filtered_ratings.groupby('userId').agg({
            'rating': ['count', 'mean']
        }).reset_index()
        user_activity.columns = ['userId', 'rating_count', 'avg_rating']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 用户评分数量分布
            fig = px.histogram(
                user_activity,
                x='rating_count',
                nbins=50,
                title='用户评分数量分布',
                labels={'rating_count': '评分数量', 'count': '用户数量'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 用户平均评分分布
            fig = px.histogram(
                user_activity,
                x='avg_rating',
                nbins=20,
                title='用户平均评分分布',
                labels={'avg_rating': '平均评分', 'count': '用户数量'},
                color_discrete_sequence=['coral']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # 电影热度分析
        st.subheader("🎬 电影热度分析")
        
        movie_popularity = filtered_ratings.groupby('movieId').agg({
            'rating': ['count', 'mean']
        }).reset_index()
        movie_popularity.columns = ['movieId', 'rating_count', 'avg_rating']
        
        # 合并电影名称
        movie_popularity = movie_popularity.merge(
            movies[['movieId', 'title']],
            on='movieId',
            how='left'
        )
        
        # 散点图：评分数量 vs 平均评分
        fig = px.scatter(
            movie_popularity,
            x='rating_count',
            y='avg_rating',
            hover_data=['title'],
            title='电影热度分析：评分数量 vs 平均评分',
            labels={'rating_count': '评分数量', 'avg_rating': '平均评分'},
            color='avg_rating',
            color_continuous_scale='Viridis',
            size='rating_count',
            size_max=20
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # 热度排行
        st.subheader("🔥 最受欢迎电影 (评分数量)")
        top_popular = movie_popularity.nlargest(20, 'rating_count')
        
        fig = px.bar(
            top_popular,
            x='rating_count',
            y='title',
            orientation='h',
            title='评分数量 Top 20',
            labels={'rating_count': '评分数量', 'title': '电影名称'},
            color='avg_rating',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

