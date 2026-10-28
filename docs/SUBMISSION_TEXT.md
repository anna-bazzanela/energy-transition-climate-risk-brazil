# Code availability wording

Use the statement matching what you actually publish. Replace all bracketed
placeholders before submission. These are templates, not live repository links.

## For this repository after public upload

The Python code for the observed-trend component of this study is available at
[REPOSITORY URL] (version [VERSION]; release: [RELEASE URL]). The repository
includes a sanitized reference of the original plotting script, a configurable
implementation of Sen slope and Mann–Kendall analyses, and documentation of input
requirements and methodological limitations. Daily ETCCDI index generation and
the CMIP6 projection and ensemble workflows are not included in this repository.

## Once an archived software release has a DOI

The Python code for the observed-trend component of this study is available at
[REPOSITORY URL]. The submitted software version ([VERSION], commit [COMMIT SHA])
is archived at [VERSION-SPECIFIC SOFTWARE DOI URL]. The repository documents data
requirements, execution instructions and the scope of the available implementation.
Daily ETCCDI index generation and CMIP6 projection and ensemble workflows are
outside the scope of this code release.

## If you later add and verify every computational component

Only after those components are genuinely present and checked, replace the
scope-specific statement with one that lists the actual included operations
and the figure/table reproduction commands. Do not use a claim of complete
reproducibility for the currently supplied code alone.

## Data availability is a separate statement

Describe BR-DWGD and CMIP6 access separately using the exact dataset references,
versions and model identifiers used. This package contains no research datasets.
Do not state that all data are hosted in the GitHub repository. The scientific
data-source bibliography and the software-release DOI serve different purposes.
