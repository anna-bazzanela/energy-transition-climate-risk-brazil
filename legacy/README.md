# Sanitized reference script

`spatial_trends_ppe_reference.py` retains the supplied source's executable
plotting statements and historical disabled string blocks. Personal absolute
paths were replaced with relative example paths, and comments and identifiers
were translated into English. Original execution order and the fixed country
mask `== 2` remain for comparison. The source SHA-256 is recorded at repository
root; this reference file has a different checksum because it was sanitized.

This is a historical reference, not the recommended entry point. It still
requires the original data layout, GIS feature order, an ocean polygon,
regionmask, and an existing `outputs/figures/` directory. Install
`requirements-legacy.txt` if inspecting its runtime behavior. Its blocked
calculation is not enabled by running the file. Use the main script and
configuration examples for new executions.

The masked p-value files conflate significant and invalid/missing cells as NaN.
The main script deliberately does not infer significance from those NaNs.
