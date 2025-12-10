"""
MovieLens电影评分数据查询系统
"""
import streamlit as st
import pandas as pd
from data_loader import load_movies, load_ratings
from pages import query

# 页面配置
st.set_page_config(
    page_title="MovieLens数据查询系统",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 标题
st.markdown('<h1 class="main-header">🔍 MovieLens 电影评分数据查询系统</h1>', unsafe_allow_html=True)

# 加载数据
@st.cache_data
def load_all_data():
    movies = load_movies()
    ratings = load_ratings()
    return movies, ratings

try:
    with st.spinner('正在加载数据...'):
        movies, ratings = load_all_data()
    
    # 侧边栏导航
    st.sidebar.title("导航")
    page = st.sidebar.radio("选择页面", ["数据概览", "数据查询", "可视化分析"])
    
    if page == "数据概览":
        from pages import overview
        overview.show(movies, ratings)
    elif page == "数据查询":
        from pages import query
        query.show(movies, ratings)
    elif page == "可视化分析":
        from pages import visualization
        visualization.show(movies, ratings)

except Exception as e:
    st.error(f"❌ 加载数据时出错: {str(e)}")
    st.info("请确保 'ml-latest-small' 文件夹与此脚本在同一目录下，并包含 movies.csv 和 ratings.csv 文件。")

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>MovieLens 电影评分数据分析系统 | Powered by Streamlit</p>
    <p>数据来源: <a href='https://grouplens.org/datasets/movielens/'>GroupLens Research</a></p>
</div>
""", unsafe_allow_html=True)

