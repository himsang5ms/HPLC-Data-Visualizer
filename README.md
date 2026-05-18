# HPLC-Data-Visualizer 🚀

**A minimalist HPLC data plotting tool for researchers**

[🇨🇳 简体中文 (Read in Chinese)](README_ZH.md)

## 🌐 Online Demo (Global Access)

https://hplc-plot.streamlit.app/

## 💡 Why was this built?

As a researcher tortured daily by heterologous expression and compound synthesis, I was fed up with opening the incredibly bloated Origin software every time I ran an HPLC. The hellish cycle of "create layers -> import data -> tweak axes -> software crashes" was unbearable.
To get off work on time, I hand-coded this minimalist Web tool over the weekend. The main goal: **leave the mechanical manual labor to code, and save your time for actual research (or sleeping).**

## ✨ Core Features

- **🚀 Idiot-proof Batch Operations:** Reject tedious import steps. Just drag and drop multiple raw data files (supports Shimadzu `.txt`, Hitachi `.ctx`, generic `.csv`, etc.) directly into the webpage for automatic parsing.
- **📊 Waterfall Stacking & Custom Sorting:** Instantly generate neatly aligned multi-chromatogram waterfall stacked plots. Rearrange layer order effortlessly by dragging and dropping in the sidebar.
- **🖱️ Interactive Peak Integration (New!):** Click the "Box Select" icon in the top-right toolbar of the chart, then simply drag across a target peak to instantly shade its integration area. Manage and delete colored regions in real-time via the sidebar.
- **📍 Precise Peak Marking:** "Single click" anywhere on a curve to automatically mark the exact Retention Time with a vertical dashed red line down to a thousandth of a minute. Click again to toggle off.
- **🎨 Publication-Grade Aesthetics:** Built-in 4 scientific color palettes (including colorblind-safe). Minimalist UI control panel stripping away useless menus. One-click export to pure, high-definition SVG vector graphics that never pixelate.
- **🌍 Multi-language Support:** Natively supports 🇨🇳 Chinese, 🇺🇸 English, and 🇯🇵 Japanese interfaces with instant, seamless switching.

## 🛠️ How to run locally?

If you have a Python environment, it only takes two steps:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run web_app.py
```

A browser window will automatically pop up. Just drag your data in and you're good to go.

## ⚠️ Developer Notes

My main job is doing research (and babysitting experiments), not a professional programmer. Bugs are inevitable, and data format compatibility is currently limited.

- Brothers who know Python are extremely welcome to submit PRs to optimize it together.
- For users who don't know how to code, if you can't get it running, feel free to leave an Issue. If there's enough demand, I'll look into packaging a no-install executable later.

Wish everyone a speedy escape from the lab and smooth Paper publications!

## ☕ Support

If this little tool saved you from fighting with Origin and helped you get off work earlier, feel free to scan the QR code to buy this miserable heterologous expression worker a coffee to protect his stomach, or sponsor a spicy hotpot! (Also welcome to report bugs in Issues)

![Buy Me a Coffee](bmc_qr.png)
