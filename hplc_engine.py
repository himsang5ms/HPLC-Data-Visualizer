import pandas as pd
import plotly.graph_objects as go
import itertools
import math
import unicodedata

# --- 预设的顶刊/高级配色方案 ---
PALETTES = {
    "Pure Black (Single Color)": ["#000000"],
    "Nature (Colorblind Safe)": ["#0072B2", "#D55E00", "#009E73", "#F0E442", "#56B4E9", "#E69F00", "#CC79A7"],
    "Grayscale Cascade": ["#111111", "#444444", "#777777", "#AAAAAA", "#DDDDDD"],
    "Vibrant (For Screen)": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
}


def estimate_sample_label_margin(
    data_dict: dict,
    sample_label_position: str,
    sample_label_font_size: int
) -> int:
    """Estimate the side margin needed to keep full sample names inside exports."""
    if sample_label_position not in ("left", "right") or not data_dict:
        return 20

    def character_width_units(text: str) -> float:
        return sum(
            1.0 if unicodedata.east_asian_width(char) in ("W", "F") else 0.62
            for char in str(text)
        )

    longest_name_width = max(
        character_width_units(filename) * sample_label_font_size
        for filename in data_dict
    )
    return max(160, math.ceil(longest_name_width + 36))

def generate_plot(
    data_dict: dict, 
    palette_name: str = "Vibrant (For Screen)", 
    line_width: float = 2.0,
    y_offset: float = 0.0,
    x_range: tuple = None,
    show_legend: bool = True,
    show_y_axis: bool = True,
    x_title: str = "Time (min)",
    y_title: str = "Intensity",
    colored_regions: list = None,
    sample_label_position: str = "none",
    sample_label_font_size: int = 18
) -> go.Figure:
    """
    核心图表引擎：支持多文件、自动配色和瀑布流堆叠(Y-offset)。
    
    参数:
        data_dict: 字典格式，{ '文件名': DataFrame } 
        palette_name: 预设配色方案名称
        line_width: 线的粗细
        y_offset: 每增加一条线，Y轴自动向上平移的量 (mAu)
        
    返回:
        fig: 渲染好的 plotly 图表对象。
    """
    fig = go.Figure()
    colored_regions = colored_regions or []
    
    # 获取选中的配色板，并使用 cycle 以防文件数超分配色数
    colors = PALETTES.get(palette_name, PALETTES["Vibrant (For Screen)"])
    color_cycle = itertools.cycle(colors)

    global_x_max = 0

    # 遍历所有数据，依次叠加到画布上
    for idx, (filename, df) in enumerate(data_dict.items()):
        # 识别列
        x_col = 'min' if 'min' in df.columns else df.columns[0]
        y_col = 'Intensity' if 'Intensity' in df.columns else df.columns[1]

        # 核心改动：移除写死的 24，尊重真实数据的右边界
        current_x_max = df[x_col].max()
        global_x_max = max(global_x_max, current_x_max)

        # 核心逻辑：计算并应用 Y 轴偏移量 (Waterfall effect)
        # 强制转换为数值类型，防止仪器导出的烂格式带了字符串导致 + 报错而被拦截
        clean_y = pd.to_numeric(df[y_col], errors='coerce').fillna(0)
        y_data = clean_y + (idx * float(y_offset))
        
        # 从调色板取色
        current_color = colors[idx % len(colors)]
        
        # 添加此条曲线到画布 (重新启用 WebGL 硬件加速，解决几十万数据点的渲染卡顿)
        fig.add_trace(go.Scattergl(
            x=df[x_col], 
            y=y_data,
            mode='lines+markers',
            marker=dict(size=6, opacity=0),  # 透明的散点，用于捕获用户的点击事件
            line=dict(color=current_color, width=line_width),
            name=filename  # 图例显示文件名
        ))

        if sample_label_position in ("left", "right"):
            x_numeric = pd.to_numeric(df[x_col], errors='coerce')
            label_points = pd.DataFrame({"x": x_numeric, "y": y_data}).dropna()

            if x_range is not None:
                x_min, x_max = min(x_range), max(x_range)
                label_points = label_points[(label_points["x"] >= x_min) & (label_points["x"] <= x_max)]

            if not label_points.empty:
                label_point = label_points.sort_values("x").iloc[0 if sample_label_position == "left" else -1]
                fig.add_annotation(
                    x=0 if sample_label_position == "left" else 1,
                    xref="paper",
                    y=label_point["y"],
                    yref="y",
                    text=filename,
                    showarrow=False,
                    font=dict(color=current_color, size=sample_label_font_size),
                    bgcolor="rgba(255,255,255,0)",
                    xanchor="right" if sample_label_position == "left" else "left",
                    yanchor="middle",
                    xshift=-12 if sample_label_position == "left" else 12
                )

    # === 新增：遍历并绘制框选的染色区域 ===
    # 1. 优先绘制“应用到所有”的全局垂直色带 (场景A: 对比有无)
    for region in colored_regions:
        target_file = "All" if isinstance(region, tuple) else region.get("target_file", "All")
        if target_file == "All":
            x_min = region[0] if isinstance(region, tuple) else region["xmin"]
            x_max = region[1] if isinstance(region, tuple) else region["xmax"]
            fig.add_vrect(
                x0=x_min, x1=x_max,
                fillcolor="rgba(169, 169, 169, 0.2)", # 更淡的灰色，防止遮挡
                layer="below",
                line_width=0,
            )
            
    # 2. 接着绘制应用到“特定单根曲线”的面积积分染色 (场景B: 强调目标产物)
    for idx, (filename, df) in enumerate(data_dict.items()):
        x_col = 'min' if 'min' in df.columns else df.columns[0]
        y_col = 'Intensity' if 'Intensity' in df.columns else df.columns[1]
        
        for region in colored_regions:
            # 兼容老版本元组结构
            if isinstance(region, tuple):
                continue # All 已经在上面画过了
            
            x_min = region["xmin"]
            x_max = region["xmax"]
            target_file = region["target_file"]
                
            # 只处理指定给当前曲线的染色
            if target_file != filename:
                continue

            mask = (df[x_col] >= x_min) & (df[x_col] <= x_max)
            df_slice = df[mask]
            if not df_slice.empty:
                x_filled = df_slice[x_col].tolist()
                y_filled = (pd.to_numeric(df_slice[y_col], errors='coerce').fillna(0) + (idx * float(y_offset))).tolist()
                
                # 构建闭合的多边形：沿着曲线走，然后垂直落回基线，再沿着基线回起点，闭合
                x_poly = x_filled + [x_filled[-1], x_filled[0], x_filled[0]]
                y_poly = y_filled + [(idx * float(y_offset)), (idx * float(y_offset)), y_filled[0]]
                
                fig.add_trace(go.Scatter(
                    x=x_poly,
                    y=y_poly,
                    fill='toself',
                    fillcolor='rgba(169, 169, 169, 0.4)',  # 稍微深一点的半透明灰色
                    line=dict(color='rgba(255,255,255,0)'), # 透明边框
                    hoverinfo='skip',
                    showlegend=False
                ))

    # 3. 优化图表样式，保持极简白底风格，符合顶刊要求
    sample_label_margin = estimate_sample_label_margin(
        data_dict,
        sample_label_position,
        sample_label_font_size
    )

    fig.update_layout(
        template="plotly_white",        # 纯白极简主题
        xaxis_title=x_title,            # X轴多语言提示
        yaxis_title=y_title,            # Y轴多语言提示
        hovermode="x unified",          # 显示统一的悬浮数据框，方便精确看数据点
        margin=dict(
            l=sample_label_margin if sample_label_position == "left" else 20,
            r=sample_label_margin if sample_label_position == "right" else 20,
            t=30,
            b=20
        ), # 样品名显示在图外侧时，为文字预留边距
        dragmode="pan",                 # 默认启用平移模式
        clickmode="event+select",       # 确保点击能被当做 select 事件捕捉
        uirevision=True,                # 核心机制：保持用户的缩放和平移状态，不会因为加了线而重置图表
        showlegend=show_legend,         # 控制图例显示与否
        legend=dict(
            orientation="v", yanchor="top", y=1, xanchor="right", x=0.99,
            traceorder="reversed"       # 修复：图例顺序与堆叠顺序相反的问题
        ) # 把图例放到右上角防遮挡
    )
    
    # 4. 定制坐标轴样式
    final_x_range = x_range if x_range is not None else [0, global_x_max]
    
    fig.update_xaxes(
        range=final_x_range,
        showline=True,              # 显示底部的实线
        linewidth=1.5,              # 底部实线厚度
        linecolor='black',          # 实线黑色
        ticks="outside",            # 主刻度向外突出
        tickwidth=1.5,              # 主刻度厚度
        tickcolor='black',          # 主刻度黑色
        ticklen=6,                  # 主刻度长度
        minor=dict(
            ticks="outside",        # 副刻度也是向外
            tickcolor='black',
            tickwidth=1.5,
            ticklen=3               # 副刻度长度更短，不显示文字
        )
    )
    
    fig.update_yaxes(
        showgrid=False,           # 去除默认的水平灰色网格线
        zeroline=False,           # 去除 Y=0 这条特殊基准线，保持纯净
        visible=show_y_axis,      # 控制 Y 轴整体是否可见
        showticklabels=show_y_axis # 控制 Y 轴刻度文字是否可见
    )

    return fig
