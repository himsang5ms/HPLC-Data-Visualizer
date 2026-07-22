# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all, copy_metadata


streamlit_data, streamlit_binaries, streamlit_hidden_imports = collect_all("streamlit")
sortables_data, sortables_binaries, sortables_hidden_imports = collect_all("streamlit_sortables")

analysis = Analysis(
    ["portable_launcher.py"],
    pathex=[],
    binaries=streamlit_binaries + sortables_binaries,
    datas=(
        streamlit_data
        + sortables_data
        + copy_metadata("streamlit")
        + copy_metadata("streamlit-sortables")
        + [
            ("web_app.py", "."),
            ("examples", "examples"),
            ("reward.jpg", "."),
            ("bmc_qr.png", "."),
            (".streamlit/config.toml", ".streamlit"),
        ]
    ),
    hiddenimports=streamlit_hidden_imports + sortables_hidden_imports + ["hplc_engine", "lang"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="HPLC Data Visualizer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

bundle = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="HPLC Data Visualizer",
)
