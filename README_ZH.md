<p align="center">
  <a href="README.md">English</a> &middot;
  <a href="output/pdf/HPLC-Data-Visualizer-v1.3.0-Quick-Guide-ZH.pdf">中文说明书</a> &middot;
  <a href="https://hplc-data-visualizer.streamlit.app/">在线 Demo</a> &middot;
  <a href="https://github.com/himsang5ms/HPLC-Data-Visualizer/releases/latest">Windows 版下载</a> &middot;
  <a href="CASE_STUDY.md">Case Study</a> &middot;
  <a href="#截图">截图</a> &middot;
  <a href="#源码运行">源码运行</a>
</p>

<h1 align="center">HPLC Data Visualizer</h1>

<p align="center">
  面向实验室汇报和科研讨论的浏览器端 HPLC 色谱图快速绘图工具。
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.x-blue">
  <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-app-ff4b4b">
  <img alt="Plotly" src="https://img.shields.io/badge/Plotly-visualization-3f4f75">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow">
</p>

## 项目简介

HPLC Data Visualizer 是一个面向药学、天然产物及相关实验室场景的 HPLC 色谱图绘制工具。它把原本需要在 Origin 等桌面软件里反复完成的导入数据、调整坐标轴、修改线条样式和导出图片等步骤，集中到了一个浏览器界面里，帮助你快速查看 HPLC 色谱图、比较多个样品，并输出风格统一、适合组会和科研讨论的图片。

## 主要功能

- 在浏览器中上传多个 HPLC 数据文件并绘制色谱图。
- 提供 Windows x64 便携版，无需另行安装 Python。
- 支持两列或顺序包含多条曲线的 `.csv` 文件，以及分号分隔的 `.ctx` 色谱数据。
- 可以直接加载内置示例数据。
- 可以下载示例 CSV 压缩包，用于测试上传流程。
- 支持多样品瀑布图堆叠，方便进行样品间比较。
- 支持拖拽调整样品顺序，并在导出前重命名曲线。
- 提供导入诊断信息，包括识别列名、信号类型、有效点数、时间范围、跳过行数和重复时间点。
- 当一个 CSV 同时包含多种检测器信号时，可选择导入 UV/DAD 或质谱数据。
- 支持切换内置配色模板，适配不同展示场景。
- 支持调整线宽、堆叠间距、X 轴显示范围、样品名字号和图幅宽度。
- 支持按所选时间范围自动调整图幅，也可以铺满页面或使用自定义宽度。
- 支持将样品名显示在每条曲线的左侧或右侧。
- 支持隐藏图例和 Y 轴，让汇报图更简洁。
- 支持点击曲线标记保留时间。
- 支持框选峰区域并进行高亮显示。
- 支持通过显眼按钮或 Plotly 工具栏导出 SVG 矢量图。
- 支持中日英界面切换。

## Demo

在线 Demo：

https://hplc-data-visualizer.streamlit.app/

## Windows 便携版

最新的 Windows x64 便携版可前往 [GitHub Releases](https://github.com/himsang5ms/HPLC-Data-Visualizer/releases/latest) 下载。

下载后完整解压 ZIP，双击 `HPLC Data Visualizer.exe` 即可运行，无需另行安装 Python。程序会直接在浏览器中打开，不再显示需要一直保留的启动提示框；关闭浏览器页面后程序会自动退出，也可以使用侧边栏底部的“关闭本地程序”。

首次启动时，Windows 可能显示 SmartScreen 提示。点击“更多信息”，确认发布文件来源后选择“仍要运行”即可。

详细操作见[中文快速使用说明](output/pdf/HPLC-Data-Visualizer-v1.3.0-Quick-Guide-ZH.pdf)。Windows ZIP 内包含中文、英文两份独立说明书。

## 支持的数据格式

### CSV

- 第一列为时间，第二列为信号值；数据列需能转换为数值。
- 支持逗号、分号或制表符分隔。
- 支持 UTF-8、UTF-16 和 GB18030 编码。
- 一个文件可以顺序包含多组“两列标题 + 数值数据”。导入时可逐条选择曲线。
- 列名包含 `Intensity` 时提示为 UV/DAD，包含 `Counts` 时提示为质谱 TIC/EIC。该提示仅供选择时参考。

### CTX

- 支持从第一行开始的 `时间;信号值;` 两列数值格式。
- 支持带 `[Chromatogram Data]` 数据区标记的 CTX 文件。

## 截图

SVG 导出示例：

![Example HPLC chromatogram export](assets/example-export.svg)

## 使用流程与图表操作

1. 打开在线 Demo 或 Windows 便携版。
2. 上传一个或多个 HPLC 数据文件，或直接加载内置示例数据。
3. 拖动样品卡片调整曲线顺序；展开“重命名或移除曲线”可修改最终显示名称。
4. 在侧边栏调整堆叠、配色、线宽、样品名、时间范围和图幅宽度。
5. 鼠标滚轮可直接缩放，按住图表可平移，双击图表可恢复初始范围。
6. 点击曲线可标记或取消保留时间。点击图表右上角的 Zoom 后可框选区域放大；点击 Box Select 后可框选峰区域并染色；Reset axes 用于恢复坐标轴。
7. 点击页面上的“下载 SVG 矢量图”或图表工具栏中的下载按钮导出 SVG。

### 图幅宽度

- **按时间范围自动调整**：根据当前 X 轴时间跨度生成合适的图幅宽度，短时间范围不会导出过长的图片。
- **铺满页面**：预览图跟随浏览器可用宽度。
- **自定义**：手动指定像素宽度；程序会保留容纳样品名和曲线所需的最小宽度。

## 使用情况

该项目已在我所在的研究实验室中被频繁使用，且由该工具生成的图已经用于组会和科研汇报。

此外，两所校外高校的一名博后和一名 PI 也进行了早期试用。他们认可这个工具的思路和示例数据的绘图效果，并认为当前主要还需做少量细节调整。

更详细的项目背景、产品决策和开发过程见英文 [Case Study](CASE_STUDY.md)。

## 技术栈

- Python
- Streamlit
- pandas
- Plotly
- PyInstaller（Windows 便携版打包）
- CSV / CTX 数据解析
- 浏览器端 SVG 导出

## Roadmap

计划或可能的后续改进：

- 在软件页面内增加简短的“快速上手”折叠说明。
- 为 UV/DAD 与质谱信号提供上下分图显示模式。
- 继续根据用户提供的真实导出文件适配数据格式。
- 改进峰面积积分流程和峰信息导出。
- 支持保存项目或会话，方便重复整理。
- 探索面向课题组或小型实验室的产品化版本。

## 源码运行

安装依赖：

```bash
pip install -r requirements.txt
```

运行应用：

```bash
streamlit run web_app.py
```

然后打开终端中显示的本地 Streamlit 地址。

## License

MIT License

## Contact

如有问题、bug 或建议，请使用 GitHub Issues。
