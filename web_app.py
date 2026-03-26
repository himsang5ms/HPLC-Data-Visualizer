import streamlit as st
import pandas as pd
import base64
import os

# 引入我们刚刚写的极简图表引擎
from hplc_engine import generate_plot

# 1. 网页基础配置
st.set_page_config(
    page_title="HPLC 极简可视化", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 新增：全局 CSS 注入，用于缩小字体和定制侧边栏宽度 ---
st.markdown(
    """
    <style>
    /* 恢复全局基础字体大小 */
    html, body, [class*="css"] {
        font-size: 16px !important;
    }
    
    /* 恢复主标题和副标题 */
    h1 {
        font-size: 2.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    p {
        font-size: 1rem !important;
    }

    /* 隐藏整个 Header，包括顶部展开/收缩按钮和右上角菜单，实现究极极简 */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* 彻底隐藏各种版本的侧边栏收缩按钮，涵盖了 Streamlit 的多个版本 */
    [data-testid="collapsedControl"], 
    [data-testid="stSidebarCollapseButton"], 
    section[data-testid="stSidebar"] button[kind="header"],
    div[data-testid="stSidebarHeader"] button {
        display: none !important;
    }

    /* 强制缩小侧边栏宽度到 240px，使其永远可见并禁止位移 */
    section[data-testid="stSidebar"] {
        min-width: 240px !important;
        max-width: 240px !important;
        display: block !important; 
        visibility: visible !important;
        transform: none !important; 
    }
    
    /* 让 main block 去掉默认的超厚左右内边距，使其无限贴近屏幕边缘，适配 wide 模式 */
    div.block-container {
        padding-top: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }

    /* 美化侧栏横向颜色块，针对 Streamlit >= 1.30 结构优化，强制正方形 */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] button {
        height: 32px !important;
        width: 32px !important;
        padding: 0 !important;
        border-radius: 4px !important;
        border: 2px solid transparent !important;
        transition: all 0.2s;
        min-height: 32px !important;
        margin: 0 auto;
        display: block;
    }
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] button p {
        display: none !important; /* 隐藏按钮内置文字 */
    }
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] button:focus {
        border: 2px solid white !important;
        box-shadow: 0 0 5px white !important;
        transform: scale(1.1);
    }
    
    /* 强行给前 5 个按钮上色 - 100% 精准命中 stHorizontalBlock 的直接子列 */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { background-color: #1f77b4 !important; }
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { background-color: #0c2c84 !important; }
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { background-color: #2ca02c !important; }
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(4) button { background-color: #d62728 !important; }
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(5) button { background-color: #9467bd !important; }

    /* 第6个：强制取色器外壳显示为白色正方块 */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(6) div[data-testid="stColorPicker"] > div > div {
        background: #FFFFFF !important;
        height: 32px !important;
        width: 32px !important;
        border-radius: 4px !important;
        border: 1px solid #444 !important;
        box-shadow: none !important;
        cursor: pointer !important;
        margin: 0 auto;
    }
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(6) div[data-testid="stColorPicker"] > div > div:hover {
        border: 2px solid white !important;
        transform: scale(1.1);
    }
    /* 隐藏原生的颜色圆圈核心 */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(6) div[data-testid="stColorBlock"] {
        opacity: 0 !important;
        width: 100% !important;
        height: 100% !important;
    }

    /* 让取色器底部右侧的hsl/rgb切换小按钮缩小实现持平 */
    div[data-baseweb="popover"] button {
        transform: scale(0.7) !important;
        transform-origin: right bottom;
        margin-bottom: 2px;
    }

    /* 终极解法：隐藏 Streamlit 原生的已上传文件列表 (避免重复显示) */
    [data-testid="stFileUploader"] ul,
    [data-testid="stFileUploaderDropzone"] + div,
    [data-testid="stFileUploaderDropzone"] + ul,
    [data-testid="stFileUploadDropzone"] + div,
    [data-testid="stFileUploadDropzone"] + ul,
    [data-testid="stUploadedFile"],
    [data-testid="stFileUploaderFile"],
    section[aria-label="File uploader"] > div {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. 显示网页大标题
st.title("HPLC 极简可视化")
st.markdown("上传您的 HPLC 数据，将自动渲染交互式折线图。")

# --- 初始化 Session State ---
if 'line_width' not in st.session_state:
    st.session_state.line_width = 1.1
if 'palette' not in st.session_state:
    st.session_state.palette = "Vibrant (For Screen)"
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'file_order' not in st.session_state:
    st.session_state.file_order = []
if 'deleted_files' not in st.session_state:
    st.session_state.deleted_files = set()

def clear_uploaded_files():
    st.session_state.uploader_key += 1
    st.session_state.deleted_files = set()

# 3. 提供一个多文件上传器，限定只能传 csv 格式
uploaded_files = st.file_uploader(
    "请上传一个或多个 HPLC 数据文件 (CSV, CTX)", 
    type=["csv", "ctx"], 
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.uploader_key}"
)

if uploaded_files:
    st.button("🧹 一键清空所有导入文件", on_click=clear_uploaded_files)

data_dict = {}
recommended_offset = 500.0  # 默认兜底偏移量

# 4. 如果有文件上传，先解析数据并计算智能偏移量
if uploaded_files:
    try:
        global_min = float('inf')
        global_max = float('-inf')
        global_min_x = float('inf')
        global_max_x = float('-inf')
        
        for file in uploaded_files:
            file_name_clean = file.name[:-4] if file.name.lower().endswith(('.csv', '.ctx')) else file.name
            
            # 如果文件在用户手动删除的黑名单内，则直接跳过，防止再次进入堆叠序列
            if file_name_clean in st.session_state.deleted_files:
                continue

            if file.name.lower().endswith('.csv'):
                df = pd.read_csv(file)
                y_col = 'Intensity' if 'Intensity' in df.columns else df.columns[1]
            elif file.name.lower().endswith('.ctx'):
                content = file.getvalue().decode("utf-8")
                lines = content.splitlines()
                data_lines = []
                is_data = False
                for line in lines:
                    if line.strip() == "[Chromatogram Data]":
                        is_data = True
                        continue
                    if is_data and line.strip():
                        parts = line.strip().split(';')
                        if len(parts) >= 2:
                            try:
                                data_lines.append([float(parts[0]), float(parts[1])])
                            except ValueError:
                                pass
                df = pd.DataFrame(data_lines, columns=['min', 'Intensity'])
                y_col = 'Intensity'
            
            data_dict[file_name_clean] = df
            
            # 计算适合这个批次数据的偏移量 (y 轴数据默认在第2列)
            clean_y = pd.to_numeric(df[y_col], errors='coerce').dropna()
            if not clean_y.empty:
                global_min = min(global_min, clean_y.min())
                global_max = max(global_max, clean_y.max())
                
            x_col = 'min' if 'min' in df.columns else df.columns[0]
            clean_x = pd.to_numeric(df[x_col], errors='coerce').dropna()
            if not clean_x.empty:
                global_min_x = min(global_min_x, clean_x.min())
                global_max_x = max(global_max_x, clean_x.max())
                
        # 智能计算：最大峰高减去基线的跨度，加 10% 的空白间距
        if global_max > global_min:
            recommended_offset = float((global_max - global_min) * 1.1)

        # 维护基于用户操作的独立渲染顺序 (file_order)
        current_files = list(data_dict.keys())
        
        # 1. 剔除已经被用户从上传框(或清空操作)里物理删除的文件
        st.session_state.file_order = [f for f in st.session_state.file_order if f in current_files]
        
        # 2. 将新拖进来的文件追加到顺序列表末尾
        for f in current_files:
            if f not in st.session_state.file_order:
                st.session_state.file_order.append(f)

        # 渲染我们自己的自定义可排序文件列表
        st.markdown("### 已导入文件")
        
        for i, file_name in enumerate(st.session_state.file_order):
            col1, col2, col3, col4, col5 = st.columns([1, 6, 1, 1, 1])
            with col1:
                # 简单色块标识 (提取自色板库对应的顺序)
                from hplc_engine import PALETTES
                colors = PALETTES.get(st.session_state.palette, PALETTES["Vibrant (For Screen)"])
                # 因为画布引擎是对列表做 reversed() 渲染的，所以这里的颜色索引也要倒过来取才能图文一致
                color_index = (len(st.session_state.file_order) - 1 - i) % len(colors)
                color = colors[color_index]
                st.markdown(f"<div style='width: 20px; height: 20px; background-color: {color}; border-radius: 3px; margin-top: 5px;'></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='margin-top: 5px; font-weight: 500;'>{file_name}</div>", unsafe_allow_html=True)
            with col3:
                # 向上移动按钮
                if st.button("↑", key=f"up_{file_name}", disabled=(i == 0)):
                    st.session_state.file_order[i], st.session_state.file_order[i-1] = st.session_state.file_order[i-1], st.session_state.file_order[i]
                    st.rerun()
            with col4:
                # 向下移动按钮
                if st.button("↓", key=f"down_{file_name}", disabled=(i == len(st.session_state.file_order) - 1)):
                    st.session_state.file_order[i], st.session_state.file_order[i+1] = st.session_state.file_order[i+1], st.session_state.file_order[i]
                    st.rerun()
            with col5:
                # 单点移除按钮 (完全可控黑名单机制)
                if st.button("🗑️", key=f"del_{file_name}", help="从本次绘图中移除"):
                    # 提示：直接将文件加入黑名单，防止其再次被系统尾部追加回来导致变相移动到底部
                    st.session_state.deleted_files.add(file_name)
                    st.session_state.file_order.pop(i)
                    st.rerun()
            
    except Exception as e:
        st.error(f"解析文件前置发生错误: {e}")

# --- 新增功能：侧边栏样式控制 ---
with st.sidebar:
    st.header("🎨 论文排版设置")
    
    st.markdown("##### 1. 选择全局配色包")
    palette_options = [
        "Vibrant (For Screen)", 
        "Pure Black (Single Color)",
        "Nature (Colorblind Safe)", 
        "Grayscale Cascade"
    ]
    st.selectbox(
        "自动为多条曲线分配颜色",
        options=palette_options,
        key="palette"
    )
        
    st.markdown("##### 2. Y轴错开堆叠 (Waterfall)")
    # 默认针对多文件开启堆叠
    enable_stacking = st.checkbox("启用均匀错开 (防止曲线重叠)", value=True if len(uploaded_files) > 1 else False)
    
    y_offset_val = 0.0
    if enable_stacking:
        # 自由输入框，初始化为系统算好的智能偏移量
        y_offset_val = st.number_input(
            "堆叠间距 (Y-Offset)", 
            value=float(recommended_offset), 
            step=float(recommended_offset * 0.1) if recommended_offset > 0 else 100.0
        )
        
    st.markdown("##### 3. 设置全局线条粗细")
    st.slider(
        "统一调节线宽", min_value=0.5, max_value=5.0, step=0.1, key="line_width"
    )

    st.markdown("##### 4. 辅助显示设置")
    show_legend = st.checkbox("在图表中显示注释图例", value=True)
    show_y_axis = st.checkbox("显示 Y 轴及刻度", value=True)
    
    # 动态初始化 X 轴滑块范围
    if uploaded_files and global_max_x > global_min_x:
        default_x_min, default_x_max = float(global_min_x), float(global_max_x)
    else:
        default_x_min, default_x_max = 0.0, 30.0
        
    selected_x_range = st.slider(
        "裁剪/缩放时间轴 (X轴范围)", 
        min_value=max(0.0, default_x_min - 5.0), # 给左边界稍微留点余地，但不能小于0
        max_value=default_x_max + 10.0,          # 给右边界留点余地
        value=(default_x_min, default_x_max),
        step=0.5
    )
    
    


# 5. 开始绘制图表
if data_dict:
    try:
        # 提取字典里第一个 key 对应的 DataFrame
        first_key = list(data_dict.keys())[0] if data_dict else None
        if first_key:
            with st.expander(f"查看 {first_key} 原始数据"):
                st.dataframe(data_dict[first_key].head())
        
        # 步骤 2: 生成引擎需要按照我们自己维护的顺序传递字典
        # 重构传递给画布的字典顺序
        # 核心改动：由于图表堆叠是按索引 index 从 0 算起（即第一条线在最底下，最后一条线 Y 偏移量最大在最顶上）
        # 而我们的列表是从上到下看的（index=0在最上面），所以为了保持视觉所见即所得，这里传给图表引擎前要反转顺序！
        ordered_data_dict = {f: data_dict[f] for f in reversed(st.session_state.file_order) if f in data_dict}
        
        fig = generate_plot(
            data_dict=ordered_data_dict, 
            palette_name=st.session_state.palette,
            line_width=st.session_state.line_width,
            y_offset=float(y_offset_val),
            x_range=selected_x_range,
            show_legend=show_legend,
            show_y_axis=show_y_axis
        )
        
        # 步骤 3: 用 st.plotly_chart() 把图表显示在网页上，设为自适应宽度
        # 并在此处加上针对 Plotly 交互栏的极简配置
        st.plotly_chart(
            fig, 
            width="stretch",
            config={
                'scrollZoom': True,  # 开启：鼠标滚轮缩放功能
                'displaylogo': False, # 隐藏 Plotly 右侧的注册商标 Logo，更极简
                'editable': True,     # 关键配置：允许拖动图例
                'edits': {
                    'legendPosition': True,       # 允许拖拽图例位置
                    'legendText': False,          # 禁止修改图例文字内容
                    'titleText': False,           # 禁止修改标题内容
                    'annotationPosition': False,  # 禁止拖动其它注释
                    'annotationText': False       # 禁止修改其它注释内容
                },
                'modeBarButtons': [
                    # 第一个分组：只保留 框选放大(zoom2d)、平移(pan2d)、恢复默认坐标轴(resetScale2d)
                    # 按照用户习惯，把 resetAxes 按钮放在 pan2d 的右边
                    ['zoom2d', 'pan2d', 'resetScale2d'],
                    # 第二个分组：只保留 导出图片 按钮
                    ['toImage']
                ],
                'toImageButtonOptions': {
                    'format': 'svg',   # 核心改动：导出矢量图(svg)，无限放大不失真，等同于科研常用的 PDF 质量，且不带网页边框
                    'filename': 'HPLC_Plot_Export',
                    'scale': 1         # 导出比例
                }
            }
        )

    except Exception as e:
        # 此处抓取任何解析或画图过程中可能的报错，避免直接网页红屏瘫痪
        st.error(f"处理文件时发生错误: {e}")

# 在页面最底部压入页脚版权信息
st.markdown(
    """
    <div style='text-align: center; margin-top: 50px; padding-bottom: 20px; color: #888; font-size: 0.85rem;'>
        Made by 想准点下班的小J
    </div>
    """,
    unsafe_allow_html=True
)

# 在网页最右下角悬浮显示打赏二维码 (如果有的话)
reward_path = "reward.jpg"
if os.path.exists(reward_path):
    with open(reward_path, "rb") as f:
        encoded_img = base64.b64encode(f.read()).decode()
    
    st.markdown(
        f"""
        <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999; 
                    background: rgba(255, 255, 255, 0.9); padding: 8px; border-radius: 8px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15); text-align: center;">
            <p style="margin: 0 0 5px 0; font-size: 0.8rem; color: #666; font-weight: bold;">
                👍 觉得好用？
            </p>
            <img src="data:image/jpeg;base64,{encoded_img}" width="100" style="border-radius: 4px;">
        </div>
        """,
        unsafe_allow_html=True
    )
