import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import base64
import os
import io
import zipfile
from pathlib import Path
from lang import get_text

# 引入我们刚刚写的极简图表引擎
from hplc_engine import estimate_sample_label_margin, generate_plot

# 确定语言 (默认为英语)
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'
lang = st.session_state.lang

# 1. 网页基础配置
st.set_page_config(
    page_title=get_text(lang, "page_title"), 
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

    /* 强制缩小侧边栏宽度到 280px，使其永远可见并禁止位移 */
    section[data-testid="stSidebar"] {
        min-width: 280px !important;
        max-width: 280px !important;
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
st.title(get_text(lang, "app_title"))
st.markdown(get_text(lang, "app_subtitle"))

# --- 初始化 Session State ---
APP_DIR = Path(__file__).resolve().parent
EXAMPLE_DIR = APP_DIR / "examples"

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
if 'use_example_data' not in st.session_state:
    st.session_state.use_example_data = False

def clear_uploaded_files():
    st.session_state.uploader_key += 1
    st.session_state.deleted_files = set()
    st.session_state.file_order = []
    st.session_state.use_example_data = False

def load_example_data():
    st.session_state.uploader_key += 1
    st.session_state.deleted_files = set()
    st.session_state.file_order = []
    st.session_state.use_example_data = True

def get_example_file_paths():
    if not EXAMPLE_DIR.exists():
        return []
    return sorted(EXAMPLE_DIR.glob("*.csv"))

def build_example_zip(example_files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in example_files:
            zip_file.write(file_path, arcname=file_path.name)
    buffer.seek(0)
    return buffer.getvalue()

def calculate_auto_plot_width(x_range) -> int:
    """Keep short timelines compact while capping long plots at a useful size."""
    x_span = max(0.0, float(max(x_range) - min(x_range)))
    return max(650, min(1400, round(500 + (45 * x_span))))


def calculate_minimum_plot_width(
    data_dict,
    sample_label_position: str,
    sample_label_font_size: int
) -> int:
    """Reserve enough room for labels plus a usable chromatogram area."""
    label_margin = estimate_sample_label_margin(
        data_dict,
        sample_label_position,
        sample_label_font_size
    )
    required_width = 420 + 20 + label_margin
    return max(500, int(((required_width + 49) // 50) * 50))


def render_svg_export_button(label: str, export_width: int = None):
    export_width_option = f",\n                    width: {export_width}" if export_width else ""
    components.html(
        f"""
        <button id="hplc-svg-export-btn" style="
            width: 100%;
            border: 1px solid #bbb;
            border-radius: 6px;
            background: #fff;
            color: #111;
            font-size: 16px;
            font-weight: 700;
            padding: 0.7rem 1rem;
            cursor: pointer;
        ">{label}</button>
        <div id="hplc-svg-export-status" style="
            color: #777;
            font-size: 12px;
            height: 18px;
            margin-top: 4px;
        "></div>
        <script>
        const button = document.getElementById("hplc-svg-export-btn");
        const status = document.getElementById("hplc-svg-export-status");

        button.addEventListener("click", () => {{
            const parentWindow = window.parent;
            const parentDocument = parentWindow.document;
            const plots = parentDocument.querySelectorAll(".js-plotly-plot");
            const plot = plots[plots.length - 1];

            if (!plot) {{
                status.textContent = "Plot is not ready yet.";
                return;
            }}

            if (parentWindow.Plotly && parentWindow.Plotly.downloadImage) {{
                parentWindow.Plotly.downloadImage(plot, {{
                    format: "svg",
                    filename: "HPLC_Plot_Export",
                    scale: 1{export_width_option}
                }});
                status.textContent = "";
                return;
            }}

            const downloadButton = plot.querySelector("a[data-title*='Download'], a[data-title*='download']");
            if (downloadButton) {{
                downloadButton.click();
                status.textContent = "";
            }} else {{
                status.textContent = "Use the camera icon in the chart toolbar.";
            }}
        }});
        </script>
        """,
        height=70
    )

# 3. 提供一个多文件上传器，限定只能传 csv 格式
uploaded_files = st.file_uploader(
    get_text(lang, "upload_label"), 
    type=["csv", "ctx"], 
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.uploader_key}"
)

if uploaded_files:
    st.session_state.use_example_data = False

example_files = get_example_file_paths()
if example_files:
    st.markdown(get_text(lang, "example_data_title"))
    example_col1, example_col2 = st.columns(2)
    with example_col1:
        st.button(
            get_text(lang, "load_examples_btn"),
            on_click=load_example_data,
            use_container_width=True
        )
    with example_col2:
        st.download_button(
            get_text(lang, "download_examples_btn"),
            data=build_example_zip(example_files),
            file_name="hplc_example_data.zip",
            mime="application/zip",
            use_container_width=True
        )

using_examples = st.session_state.use_example_data and bool(example_files)

if uploaded_files or using_examples:
    st.button(get_text(lang, "clear_files_btn"), on_click=clear_uploaded_files)

data_dict = {}
ordered_data_dict = {}
recommended_offset = 500.0  # 默认兜底偏移量

# 4. 如果有文件上传，先解析数据并计算智能偏移量
if uploaded_files or using_examples:
    try:
        global_min = float('inf')
        global_max = float('-inf')
        global_min_x = float('inf')
        global_max_x = float('-inf')
        
        files_to_parse = example_files if using_examples else uploaded_files
        
        for file in files_to_parse:
            file_name = file.name
            file_name_clean = file_name[:-4] if file_name.lower().endswith(('.csv', '.ctx')) else file_name
            
            # 如果文件在用户手动删除的黑名单内，则直接跳过，防止再次进入堆叠序列
            if file_name_clean in st.session_state.deleted_files:
                continue

            if file_name.lower().endswith('.csv'):
                df = pd.read_csv(file)
                y_col = 'Intensity' if 'Intensity' in df.columns else df.columns[1]
            elif file_name.lower().endswith('.ctx'):
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
        st.markdown(get_text(lang, "imported_files"))
        
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
                if st.button("🗑️", key=f"del_{file_name}", help=get_text(lang, "remove_file_help")):
                    # 提示：直接将文件加入黑名单，防止其再次被系统尾部追加回来导致变相移动到底部
                    st.session_state.deleted_files.add(file_name)
                    st.session_state.file_order.pop(i)
                    st.rerun()
            
    except Exception as e:
        st.error(get_text(lang, "parse_error", str(e)))

if data_dict:
    # 重构传递给画布的字典顺序
    ordered_data_dict = {f: data_dict[f] for f in reversed(st.session_state.file_order) if f in data_dict}
    
    # --- 步骤 2.1: 在生成图表和侧边栏前，提前处理交互事件，消除单次刷新延迟 ---
    if "marked_peaks" not in st.session_state:
        st.session_state.marked_peaks = set()
    if "colored_regions" not in st.session_state:
        st.session_state.colored_regions = []
        
    if "last_selection" not in st.session_state:
        st.session_state.last_selection = []
    if "last_box_selection" not in st.session_state:
        st.session_state.last_box_selection = []
        
    # 尝试从 session_state 中获取此图表的选中状态
    plot_state = st.session_state.get("hplc_plot", {})
    current_selection = plot_state.get("selection", {}).get("points", [])
    current_box = plot_state.get("selection", {}).get("box", [])
    
    box_changed = current_box != st.session_state.last_box_selection
    points_changed = current_selection != st.session_state.last_selection
    
    # 1. 处理框选事件（染色）
    if box_changed:
        if len(current_box) > 0:
            x_range = current_box[0].get("x", [])
            if len(x_range) >= 2:
                x_min, x_max = min(x_range), max(x_range)
                target_file = "All"
                if len(current_selection) > 0:
                    curve_numbers = [pt.get("curve_number") for pt in current_selection if "curve_number" in pt]
                    if curve_numbers:
                        most_common_curve = max(set(curve_numbers), key=curve_numbers.count)
                        ordered_keys = list(ordered_data_dict.keys())
                        if most_common_curve < len(ordered_keys):
                            target_file = ordered_keys[most_common_curve]
                
                st.session_state.colored_regions.append({
                    "xmin": x_min,
                    "xmax": x_max,
                    "target_file": target_file
                })
        
        st.session_state.last_box_selection = current_box
        
    # 2. 处理点击事件（画红线/Toggle）
    if points_changed:
        # 只处理有实质选中的情况，忽略选区清空的情况（防止刷新或点击空白处误删标记）
        if len(current_selection) > 0:
            # 当且仅当用户只点击了一个点，或者没有框选时处理，避免框选时误触标记
            if len(current_box) == 0:
                for pt in current_selection:
                    if "x" in pt:
                        x_val = pt["x"]
                        already_exists = False
                        for marked_x in st.session_state.marked_peaks:
                            if abs(marked_x - x_val) < 0.05:
                                already_exists = True
                                break
                        
                        if not already_exists:
                            st.session_state.marked_peaks.add(x_val)
                        else:
                            to_remove = None
                            for marked_x in st.session_state.marked_peaks:
                                if abs(marked_x - x_val) < 0.05:
                                    to_remove = marked_x
                                    break
                            if to_remove is not None:
                                st.session_state.marked_peaks.remove(to_remove)
                            
        st.session_state.last_selection = current_selection

# --- 新增功能：侧边栏样式控制 ---
with st.sidebar:
    # 语言选择器放在最上面
    lang_map = {"zh": "🇨🇳 中文", "en": "🇺🇸 English", "jp": "🇯🇵 日本語"}
    # 倒推索引
    lang_options = list(lang_map.keys())
    current_index = lang_options.index(st.session_state.lang) if st.session_state.lang in lang_options else 1
    
    selected_lang = st.selectbox(
        get_text(lang, "lang_title"),
        options=lang_options,
        index=current_index,
        format_func=lambda x: lang_map[x]
    )
    if selected_lang != st.session_state.lang:
        st.session_state.lang = selected_lang
        st.rerun()

    st.header(get_text(lang, "sidebar_header"))
    
    st.markdown(get_text(lang, "palette_title"))
    palette_options = [
        "Vibrant (For Screen)", 
        "Pure Black (Single Color)",
        "Nature (Colorblind Safe)", 
        "Grayscale Cascade"
    ]
    st.selectbox(
        get_text(lang, "palette_select"),
        options=palette_options,
        key="palette"
    )
        
    st.markdown(get_text(lang, "y_offset_title"))
    # 默认针对多文件开启堆叠
    enable_stacking = st.checkbox(get_text(lang, "y_offset_check"), value=True if len(data_dict) > 1 else False)
    
    y_offset_val = 0.0
    if enable_stacking:
        # 自由输入框，初始化为系统算好的智能偏移量
        y_offset_val = st.number_input(
            get_text(lang, "y_offset_input"), 
            value=float(recommended_offset), 
            step=float(recommended_offset * 0.1) if recommended_offset > 0 else 100.0
        )
        
    st.markdown(get_text(lang, "line_width_title"))
    st.slider(
        get_text(lang, "line_width_slider"), min_value=0.5, max_value=5.0, step=0.1, key="line_width"
    )

    st.markdown(get_text(lang, "display_settings_title"))
    show_legend = st.checkbox(get_text(lang, "show_legend"), value=False)
    show_y_axis = st.checkbox(get_text(lang, "show_y_axis"), value=False)
    sample_label_options = ["none", "left", "right"]
    sample_label_position = st.selectbox(
        get_text(lang, "sample_label_position"),
        options=sample_label_options,
        index=2,
        format_func=lambda option: get_text(lang, f"sample_label_{option}")
    )
    sample_label_font_size = st.slider(
        get_text(lang, "sample_label_font_size"),
        min_value=10,
        max_value=32,
        value=18,
        step=1
    )
    
    # 动态初始化 X 轴滑块范围
    if data_dict and global_max_x > global_min_x:
        default_x_min, default_x_max = float(global_min_x), float(global_max_x)
    else:
        default_x_min, default_x_max = 0.0, 30.0
        
    selected_x_range = st.slider(
        get_text(lang, "x_range_slider"), 
        min_value=max(0.0, default_x_min - 5.0), # 给左边界稍微留点余地，但不能小于0
        max_value=default_x_max + 10.0,          # 给右边界留点余地
        value=(default_x_min, default_x_max),
        step=0.5
    )

    plot_width_options = ["auto", "stretch", "custom"]
    plot_width_mode = st.selectbox(
        get_text(lang, "plot_width_mode"),
        options=plot_width_options,
        format_func=lambda option: get_text(lang, f"plot_width_{option}")
    )
    minimum_plot_width = calculate_minimum_plot_width(
        ordered_data_dict,
        sample_label_position,
        sample_label_font_size
    )
    if plot_width_mode == "auto":
        plot_width = max(
            calculate_auto_plot_width(selected_x_range),
            minimum_plot_width
        )
    elif plot_width_mode == "custom":
        plot_width = st.slider(
            get_text(lang, "plot_width_custom_value"),
            min_value=minimum_plot_width,
            max_value=max(1800, minimum_plot_width + 50),
            value=max(900, minimum_plot_width),
            step=50
        )
    else:
        plot_width = "stretch"
    
    st.markdown(get_text(lang, "interaction_title"))
    if st.button(get_text(lang, "clear_marks_btn")):
        st.session_state.marked_peaks = set()
        st.session_state.last_selection = []
        st.rerun()

    if st.button(get_text(lang, "clear_colors_btn")):
        st.session_state.colored_regions = []
        st.session_state.last_box_selection = []
        st.rerun()

    if "colored_regions" in st.session_state and len(st.session_state.colored_regions) > 0:
        # 兼容老数据结构，如果里面是元组，转成字典
        new_regions = []
        for r in st.session_state.colored_regions:
            if isinstance(r, tuple):
                new_regions.append({"xmin": r[0], "xmax": r[1], "target_file": "All"})
            else:
                new_regions.append(r)
        st.session_state.colored_regions = new_regions

        st.markdown("---")
        st.markdown(get_text(lang, "sidebar_colored_title"))
        
        # 确保下拉菜单的选项按当前图表显示顺序排列
        ordered_files = list(reversed(st.session_state.file_order))
        options = ["All"] + ordered_files
        
        for i, region in enumerate(st.session_state.colored_regions):
            col_text, col_sel, col_btn = st.columns([1.5, 2.5, 1.2])
            with col_text:
                st.markdown(f"<div style='font-size: 0.85rem; font-family: monospace; white-space: nowrap; line-height: 38px;'>{region['xmin']:.2f}-{region['xmax']:.2f}</div>", unsafe_allow_html=True)
            with col_sel:
                current_target = region["target_file"]
                if current_target not in options:
                    current_target = "All"
                    
                new_target = st.selectbox(
                    "Target File", 
                    options=options, 
                    index=options.index(current_target), 
                    key=f"color_target_{i}", 
                    label_visibility="collapsed"
                )
                if new_target != region["target_file"]:
                    st.session_state.colored_regions[i]["target_file"] = new_target
                    st.rerun()
            with col_btn:
                if st.button(get_text(lang, "delete_btn"), key=f"del_color_{i}"):
                    st.session_state.colored_regions.pop(i)
                    st.rerun()

# 5. 开始绘制图表
if data_dict:
    try:
        # 提取字典里第一个 key 对应的 DataFrame
        first_key = list(data_dict.keys())[0] if data_dict else None
        if first_key:
            with st.expander(get_text(lang, "view_raw_data", first_key)):
                st.dataframe(data_dict[first_key].head())
        
        # 步骤 2: 生成引擎需要按照我们自己维护的顺序传递字典
        # 重构传递给画布的字典顺序
        # 核心改动：由于图表堆叠是按索引 index 从 0 算起（即第一条线在最底下，最后一条线 Y 偏移量最大在最顶上）
        # 步骤 2.2: 获取当前更新后的所有着色区域
        colored_regions = st.session_state.get("colored_regions", [])

        fig = generate_plot(
            data_dict=ordered_data_dict, 
            palette_name=st.session_state.palette,
            line_width=st.session_state.line_width,
            y_offset=float(y_offset_val),
            x_range=selected_x_range,
            show_legend=show_legend,
            show_y_axis=show_y_axis,
            x_title=get_text(lang, "axis_time"),
            y_title=get_text(lang, "axis_intensity"),
            colored_regions=colored_regions,
            sample_label_position=sample_label_position,
            sample_label_font_size=sample_label_font_size
        )
        
        # 为每个被记录的保留时间画线
        for x_val in st.session_state.marked_peaks:
            fig.add_vline(x=x_val, line_width=1.5, line_dash="dash", line_color="rgba(255,0,0,0.7)")
            fig.add_annotation(
                x=x_val, 
                y=1.02, # 显示在顶部，防止遮挡曲线
                yref="paper",
                text=f"{x_val:.3f} min",
                showarrow=False,
                font=dict(color="red", size=12),
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="red",
                borderwidth=1,
                borderpad=3
            )
        
        export_width = plot_width if isinstance(plot_width, int) else None
        render_svg_export_button(get_text(lang, "download_svg_btn"), export_width)

        to_image_options = {
            'format': 'svg',
            'filename': 'HPLC_Plot_Export',
            'scale': 1
        }
        if export_width:
            to_image_options['width'] = export_width

        # 步骤 3: 用 st.plotly_chart() 把图表显示在网页上，设为自适应宽度
        # 并在此处加上针对 Plotly 交互栏的极简配置
        st.plotly_chart(
            fig, 
            width=plot_width,
            on_select="rerun",          # 开启点击重新运行功能
            selection_mode=["points", "box"], # 核心修改：允许点选(画红线)和框选(染色)
            key="hplc_plot",            # 分配唯一的 key，用于捕捉点击状态
            config={
                'scrollZoom': True,  # 开启：鼠标滚轮缩放功能
                'displaylogo': False, # 隐藏 Plotly 右侧的注册商标 Logo，更极简
                'editable': True,     # 关键配置：允许拖动图例
                'edits': {
                    'legendPosition': True,       # 允许拖拽图例位置
                    'legendText': False,          # 禁止修改图例文字内容
                    'titleText': False,           # 禁止修改标题内容
                    'annotationPosition': False,  # 禁止拖动其它注释
                    'annotationText': False,      # 禁止修改其它注释内容
                    'shapePosition': False        # 禁止拖动辅助线（因为后端无法同步拖动状态）
                },
                'modeBarButtons': [
                    # 第一个分组：只保留 框选放大(zoom2d)、平移(pan2d)、框选(select2d)、恢复默认坐标轴(resetScale2d)
                    ['zoom2d', 'pan2d', 'select2d', 'resetScale2d'],
                    # 第二个分组：只保留 导出图片 按钮
                    ['toImage']
                ],
                'toImageButtonOptions': to_image_options
            }
        )

    except Exception as e:
        # 此处抓取任何解析或画图过程中可能的报错，避免直接网页红屏瘫痪
        st.error(get_text(lang, "plot_error", str(e)))

# 在页面最底部压入页脚版权信息
st.markdown(
    f"""
    <div style='text-align: center; margin-top: 50px; padding-bottom: 20px; color: #888; font-size: 0.85rem;'>
        {get_text(lang, "footer_made_by")}
    </div>
    """,
    unsafe_allow_html=True
)

# 在网页最右下角悬浮显示打赏二维码 (根据语言动态切换)
if lang == 'zh':
    reward_path = APP_DIR / "reward.jpg"
    mime_type = "image/jpeg"
else:
    reward_path = APP_DIR / "bmc_qr.png"
    mime_type = "image/png"

if os.path.exists(reward_path):
    with open(reward_path, "rb") as f:
        encoded_img = base64.b64encode(f.read()).decode()
    
    st.markdown(
        f"""
        <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999; 
                    background: rgba(255, 255, 255, 0.9); padding: 8px; border-radius: 8px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15); text-align: center;">
            <p style="margin: 0 0 5px 0; font-size: 0.8rem; color: #666; font-weight: bold;">
                {get_text(lang, "footer_support")}
            </p>
            <img src="data:{mime_type};base64,{encoded_img}" width="100" style="border-radius: 4px;">
        </div>
        """,
        unsafe_allow_html=True
    )
