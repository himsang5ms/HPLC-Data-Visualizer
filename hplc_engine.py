import pandas as pd
import plotly.graph_objects as go
import itertools

# --- 预设的顶刊/高级配色方案 ---
PALETTES = {
    "Pure Black (Single Color)": ["#000000"],
    "Nature (Colorblind Safe)": ["#0072B2", "#D55E00", "#009E73", "#F0E442", "#56B4E9", "#E69F00", "#CC79A7"],
    "Grayscale Cascade": ["#111111", "#444444", "#777777", "#AAAAAA", "#DDDDDD"],
    "Vibrant (For Screen)": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
}

def generate_plot(
    data_dict: dict, 
    palette_name: str = "Vibrant (For Screen)", 
    line_width: float = 2.0,
    y_offset: float = 0.0,
    x_range: tuple = None,
    show_legend: bool = True,
    show_y_axis: bool = True
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
        current_color = next(color_cycle)
        
        # 添加此条曲线到画布
        fig.add_trace(go.Scatter(
            x=df[x_col], 
            y=y_data,
            mode='lines',
            line=dict(color=current_color, width=line_width),
            name=filename  # 图例显示文件名
        ))

    # 3. 优化图表样式，保持极简白底风格，符合顶刊要求
    fig.update_layout(
        template="plotly_white",        # 纯白极简主题
        xaxis_title="Time (min)",       # X轴中文提示
        yaxis_title="Intensity",        # Y轴中文提示
        hovermode="x unified",          # 显示统一的悬浮数据框，方便精确看数据点
        margin=dict(l=20, r=20, t=30, b=20), # 减少四周留白
        dragmode="pan",                 # 默认启用平移模式
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
