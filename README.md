<p align="center">
  <a href="README_ZH.md">Chinese</a> &middot;
  <a href="output/pdf/HPLC-Data-Visualizer-v1.3.0-Quick-Guide-EN.pdf">Quick Guide</a> &middot;
  <a href="https://hplc-data-visualizer.streamlit.app/">Online Demo</a> &middot;
  <a href="https://github.com/himsang5ms/HPLC-Data-Visualizer/releases/latest">Windows Download</a> &middot;
  <a href="CASE_STUDY.md">Case Study</a> &middot;
  <a href="#screenshots">Screenshots</a> &middot;
  <a href="#development-setup">Development Setup</a>
</p>

<h1 align="center">HPLC Data Visualizer</h1>

<p align="center">
  Browser-based HPLC chromatogram visualization for faster, cleaner lab presentation figures.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.x-blue">
  <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-app-ff4b4b">
  <img alt="Plotly" src="https://img.shields.io/badge/Plotly-visualization-3f4f75">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow">
</p>

## Overview

HPLC Data Visualizer helps pharmaceutical sciences and natural products researchers turn raw HPLC chromatogram data into presentation-ready figures with less manual formatting. Instead of repeatedly importing data into Origin or similar desktop tools, users can upload files in a browser, compare samples, adjust figure styling, and export SVG figures.

The app is designed for a focused lab workflow: fast chromatogram visualization, multi-sample comparison, and consistent figure preparation for meetings and research discussions.

## Key Features

- Upload multiple HPLC data files and render chromatograms in the browser.
- Run locally on Windows from a portable package without installing Python.
- Supports two-column or sequential multi-signal `.csv` files and semicolon-delimited `.ctx` chromatogram data.
- Load built-in example chromatograms directly from the web interface.
- Download example CSV files as a ZIP for testing the upload workflow.
- Generate stacked waterfall plots for multi-sample comparison.
- Reorder samples by dragging, and rename imported curves before export.
- Review import diagnostics such as detected columns, signal type, point count, time range, skipped rows, and duplicate times.
- Choose UV/DAD or MS signals when one CSV contains multiple detector exports.
- Switch between built-in color palettes for different presentation styles.
- Adjust line width, stacking distance, visible X-axis range, sample-label font size, and figure width.
- Size figures automatically from the selected time range, fill the page width, or choose a custom width.
- Show sample names directly at the left or right edge of each curve.
- Toggle legend and Y-axis display for cleaner presentation figures.
- Mark retention times by clicking on chromatogram curves.
- Highlight selected peak regions with box selection.
- Export presentation-ready SVG figures through a visible download button or the Plotly toolbar.
- Switch between Chinese, English, and Japanese interfaces.

## Demo

Online demo:

https://hplc-data-visualizer.streamlit.app/

## Windows Portable Version

The latest Windows x64 portable version is available from [GitHub Releases](https://github.com/himsang5ms/HPLC-Data-Visualizer/releases/latest).

Download and fully extract the ZIP archive, then double-click `HPLC Data Visualizer.exe`. A separate Python installation is not required. The app opens directly in the browser without a persistent startup dialog. It exits automatically after the browser tab is closed, or you can use **Close local app** at the bottom of the sidebar.

Windows may show a SmartScreen prompt on first launch. Choose **More info**, verify the downloaded file, and select **Run anyway**.

See the [English quick guide](output/pdf/HPLC-Data-Visualizer-v1.3.0-Quick-Guide-EN.pdf) for detailed instructions. Separate [Chinese](output/pdf/HPLC-Data-Visualizer-v1.3.0-Quick-Guide-ZH.pdf) and English guides are included in the Windows ZIP.

## Supported Data Formats

### CSV

- The first column contains time and the second contains signal values; both data columns must be numeric or convertible to numbers.
- Comma, semicolon, and tab delimiters are supported.
- UTF-8, UTF-16, and GB18030 encodings are supported.
- One file may contain several sequential blocks, each with a two-column header followed by numeric data. Signals can be selected individually during import.
- A column name containing `Intensity` is shown as likely UV/DAD; `Counts` is shown as likely MS TIC/EIC. These labels are selection hints only.

### CTX

- Supports two-column numeric data written as `time;signal;` from the first line.
- Supports CTX files with a `[Chromatogram Data]` section marker.

## Screenshots

Example SVG export:

![Example HPLC chromatogram export](assets/example-export.svg)

## Usage and Chart Interaction

1. Open the online demo or Windows portable app.
2. Upload one or more HPLC data files, or load the built-in example data.
3. Drag sample cards to reorder curves. Expand **Rename or remove curves** to edit final display names.
4. Adjust stacking, color palette, line width, sample labels, time range, and figure width from the sidebar.
5. Use the mouse wheel to zoom, drag the chart to pan, and double-click to restore the initial range.
6. Click a curve to add or remove a retention-time marker. Use **Zoom** to drag a precise zoom region, **Box Select** to highlight a peak region, and **Reset axes** to restore the axes.
7. Export SVG with the large download button or the download button in the chart toolbar.

### Figure width

- **Auto by time range** sizes the figure from the current X-axis span, keeping short time ranges from producing unnecessarily long exports.
- **Fill page width** follows the available browser width for preview.
- **Custom** sets an explicit pixel width. The app keeps enough minimum width for the chromatogram and sample labels.

## Adoption

This project has been used by members of my pharmaceutical sciences / natural products research lab. Figures generated by the app have been used in group meetings and research presentations.

Early external testing has also included a postdoctoral researcher and a principal investigator from two other universities. Their feedback supported the core idea and the usefulness of the current example workflow, while suggesting that only minor refinements were needed.

More details are available in the [case study](CASE_STUDY.md).

## Tech Stack

- Python
- Streamlit
- pandas
- Plotly
- PyInstaller for Windows portable packaging
- CSV / CTX data parsing
- Browser-based SVG export

## Roadmap

Planned or potential improvements:

- Add a compact in-app quick-start guide.
- Add separate UV/DAD and MS panels.
- Continue adapting parsers from real instrument export files shared by users.
- Improve peak integration workflows and exportable peak metadata.
- Add project/session saving for repeated figure preparation.
- Explore a more productized version for research groups or small labs.

## Development Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run web_app.py
```

Then open the local Streamlit URL shown in the terminal.

## License

MIT License

## Contact

For questions, bugs, or suggestions, please use GitHub Issues.
