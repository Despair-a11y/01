# MovieLens 电影评分数据查询系统

基于Python和Streamlit开发的MovieLens电影评分数据查询系统，提供强大的电影和用户数据查询功能。

## 📋 项目简介

本系统使用著名的MovieLens电影评分数据集，通过Web界面实现数据可视化和交互式查询。目前使用的是ml-latest-small抽样数据集，包含：

- 📽️ **9,742** 部电影
- ⭐ **100,836** 条评分
- 👥 **610** 位用户
- 📅 评分时间跨度：**1996-2018**

## 🌟 主要功能

### 🔍 电影查询
系统专注于电影信息查询功能：

#### 核心功能
- 🔎 **关键词搜索** - 支持模糊匹配电影名称
- 📋 **电影详情** - 查看电影基本信息和统计数据
- 📊 **评分分布** - 展示电影评分分布统计表
- 📅 **年度统计** - 按年份统计评分数量和平均分
- 📝 **评分记录** - 查看最新20条评分记录
- 🎲 **随机推荐** - 随机展示10部电影供浏览

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 包管理工具

### 安装步骤

1. **克隆或下载项目**
```bash
cd 桌面/车辆数据分析/01
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **确认数据文件**

确保`ml-latest-small`文件夹与脚本在同一目录下，并包含以下文件：
- `movies.csv` - 电影数据
- `ratings.csv` - 评分数据

4. **运行应用**
```bash
streamlit run app.py
```

5. **访问应用**

浏览器会自动打开，或手动访问：
```
http://localhost:8501
```

## 📁 项目结构

```
01/
├── app.py                  # 主应用入口
├── data_loader.py          # 数据加载和处理模块（支持CSV/HBase）
├── hbase_config.py         # HBase 配置文件
├── hbase_connector.py      # HBase 连接器
├── import_to_hbase.py      # CSV 数据导入 HBase 工具
├── requirements.txt        # Python依赖包
├── README.md              # 项目说明文档
├── HBASE_配置说明.md       # HBase 配置详细说明
├── .streamlit/            # Streamlit 配置
│   └── config.toml
├── pages/                 # 页面模块
│   ├── __init__.py
│   └── query.py           # 数据查询页面（纯表格版）
└── ml-latest-small/       # 数据集文件夹
    ├── movies.csv         # 电影数据
    ├── ratings.csv        # 评分数据
    ├── tags.csv
    ├── links.csv
    └── README.txt
```

## 🔧 技术栈

- **Web框架**：Streamlit 1.28.0
- **数据处理**：Pandas 2.1.1
- **数据可视化**：Plotly 5.17.0
- **数值计算**：NumPy 1.26.0
- **数据库支持**（可选）：
  - HBase（通过 happybase）
  - 默认使用 CSV 文件

## 📊 数据说明

### movies.csv（电影数据）
| 字段 | 说明 |
|------|------|
| movieId | 电影ID（唯一标识） |
| title | 电影名称（包含年份） |
| genres | 电影类型（用\|分隔） |

### ratings.csv（评分数据）
| 字段 | 说明 |
|------|------|
| userId | 用户ID |
| movieId | 电影ID |
| rating | 评分（0.5-5.0，步长0.5） |
| timestamp | 时间戳（秒） |

## 💡 使用技巧

1. **电影搜索**：输入电影名称关键词（如"Star Wars"），支持模糊匹配
2. **查看详情**：从搜索结果中选择电影，查看详细的评分统计信息
3. **数据查看**：所有统计数据以表格形式展示，清晰直观
4. **数据复制**：可以直接从表格中选择和复制数据
5. **随机推荐**：未输入关键词时自动显示10部随机电影
6. **完整信息**：每部电影显示评分分布、年度统计、最新评分等完整信息

## 📝 功能特点

- ✅ **简洁界面**：专注于电影查询功能
- ✅ **数据缓存**：使用Streamlit缓存机制，提升加载速度
- ✅ **纯表格展示**：所有数据以表格形式呈现，无图表干扰
- ✅ **快速搜索**：支持关键词模糊匹配，快速找到目标电影
- ✅ **详细统计**：提供评分分布、年度统计等多维度数据
- ✅ **响应式设计**：适配不同屏幕尺寸
- ✅ **HBase支持**：可选择使用HBase数据库（默认CSV模式）

## 🎯 未来扩展

本系统目前使用ml-latest-small抽样数据集。未来可以扩展：

- [ ] 支持ml-latest完整数据集（3300万评分）
- [ ] 集成tags.csv标签数据查询
- [ ] 按类型、年份等条件筛选电影
- [ ] 电影排行榜功能
- [ ] 导出查询结果为Excel/CSV
- [ ] 批量查询多部电影
- [ ] 收藏夹功能
- [ ] 评分趋势预测

## 📖 数据来源

数据来自GroupLens Research的MovieLens项目：
- 官网：https://movielens.org
- 数据集：https://grouplens.org/datasets/movielens/

## 🙏 致谢

- MovieLens数据集由GroupLens Research提供
- 可视化框架基于Streamlit
- 图表库使用Plotly

## 📄 许可说明

本项目仅供学习和研究使用。MovieLens数据集的使用需遵循GroupLens Research的许可协议。

## ❓ 常见问题

### Q: 无法加载数据？
A: 请确保`ml-latest-small`文件夹与`app.py`在同一目录下，并包含`movies.csv`和`ratings.csv`文件。

### Q: 图表显示不正常？
A: 请确保已安装所有依赖包，可以尝试重新安装：`pip install -r requirements.txt`

### Q: 如何更换数据集？
A: 修改`data_loader.py`中的`data_dir`参数，指向新的数据集路径。

### Q: 可以部署到服务器吗？
A: 可以。使用Streamlit Cloud或其他云平台部署。具体方法请参考Streamlit官方文档。

## 📧 联系方式

如有问题或建议，欢迎反馈！

---

**Powered by Streamlit | Python Data Analysis Project**

