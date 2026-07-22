# HPLC Data Visualizer v1.3.0

This release improves instrument-export compatibility and the workflow for organizing multiple chromatograms.

## Added

- Import sequential two-column signals stored in one CSV and choose signals before plotting.
- Show likely UV/DAD or MS TIC/EIC labels from source column names, with detector-type selection presets.
- Review import diagnostics including source columns, valid point count, time range, skipped rows, duplicate times, encoding, and delimiter.
- Reorder sample cards by dragging.
- Rename imported curves before export; names are synchronized across legends, curve labels, and SVG output.
- Read semicolon-delimited CTX data starting from the first line while retaining support for `[Chromatogram Data]` sections.
- Parse comma, semicolon, or tab-delimited CSV files in UTF-8, UTF-16, or GB18030 encoding.
- Exit the Windows portable app automatically after the final browser page closes, or close it manually from the sidebar.
- Include separate Chinese and English quick-start guides in the Windows ZIP.
