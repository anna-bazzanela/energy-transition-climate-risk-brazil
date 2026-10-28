# Publish the code on GitHub and cite it in your submission

You will create a GitHub repository containing the extracted project files.
The repository URL becomes available when you create it. A GitHub release
identifies a specific version; an optional Zenodo archive adds a DOI.

Suggested repository name: **`energy-transition-climate-risk-brazil`**.

Suggested description:

> Observed ETCCDI trend analysis and mapping for Brazil, with optional electricity infrastructure overlays.

## 1. Prepare the folder

Download and extract the supplied ZIP. Work inside `energy-transition-climate-risk/`.
Its top level should contain `README.md`, `spatial_trends_ppe.py`, the configuration
examples, `CITATION.cff`, `docs/`, `legacy/`, `examples/`, `tests/`, and the other
support files. Upload these extracted contents; uploading the ZIP alone will
not create a browsable code repository.

Read `README.md`, `docs/REPRODUCIBILITY.md`, and `docs/SUBMISSION_TEXT.md`.
Check the software author list in `CITATION.cff`, add other software contributors
when appropriate, and verify the title. Paper authors and software contributors
are not automatically identical. No ORCID, journal information or DOI was invented.

Choose a reuse license before calling the repository open source. If you want
a permissive software license, MIT is a common option; GitHub provides a license
chooser. Keep the relevant copyright names and year. See `LICENSE_NOTICE.md`.
This package deliberately leaves that choice to the copyright holder.

The supplied source documents only the observed-trend component. Either retain
that accurate scope or add the missing index-generation/projection scripts
before claiming that the entire article is reproducible from the repository.

## 2. Create an empty repository

1. Sign in at [GitHub](https://github.com/), creating an account if needed.
2. Open [New repository](https://github.com/new).
3. Choose your account as owner and enter the suggested name and description.
4. Choose **Public** for an openly accessible submission link, subject to your
   journal's review requirements. A normal personal repository identifies its
   owner; it is not an anonymous-review service. If review must be anonymous,
   follow the journal's prescribed code-sharing procedure before making it public.
5. Leave the automatic README, `.gitignore` and license initialization options
   off, because you will upload the prepared project first.
6. Select **Create repository**.

Your actual address will have the form
`https://github.com/YOUR-USERNAME/energy-transition-climate-risk-brazil`.
Replace `YOUR-USERNAME` with your account name; it is a placeholder, not a live
repository created by this preparation.

## 3. Upload the extracted contents in the browser

On the empty repository page, choose the link for uploading an existing file.
In an existing repository, the route is **Add file → Upload files**.

Drag the **contents** of the extracted project folder into the upload area,
including its subfolders. Keep `README.md` directly at repository root rather
than one directory deeper. Verify nested paths such as `docs/METHODS.md` before
committing. Include `.gitignore` and `.github/workflows/checks.yml`; on macOS,
press **Command + Shift + .** in Finder to show dot-prefixed items for selection.

Use this first commit message: `Add observed climate trend analysis and documentation`.
Commit the uploaded files to the default branch, normally `main`.

If the browser cannot retain the folder structure, use the command-line route
below. This prepared package is small; GitHub's browser upload limit is 25 MiB
per file and up to 100 files per upload. The ZIP archive itself is not the item
to drag into the source tree.

**Only upload the prepared project.** After running it locally, exclude actual
data files, `.venv/`, `outputs/`, `demo_data/`, `demo_outputs/`, local configurations
and run records unless you deliberately intend to publish them. Browser uploads
do not honor `.gitignore` exclusions.

Refresh the main repository page. The README should display below the file
list. Open several files to confirm the folders and code are present.

## 4. Complete citation metadata and licensing

Open `CITATION.cff`, select the edit button, and add the **real** repository URL:

```yaml
repository-code: "https://github.com/YOUR-USERNAME/energy-transition-climate-risk-brazil"
```

Replace the placeholder first. Keep `version: 0.1.0` if that is the version you
will release. Add `date-released` as an ISO date on the actual release day.
Add your verified ORCID and additional software contributors if applicable.
Do not use an unrelated paper's DOI. Save the change with a descriptive commit.
GitHub can then show a **Cite this repository** option from this citation file.

To add your chosen license through the website, select **Add file → Create new file**,
name it `LICENSE`, and use **Choose a license template**. Select the license,
review its copyright details and commit it. Update `LICENSE_NOTICE.md` and the
README to identify the selected license instead of saying it is unselected.

## 5. Check the scientific record

The included tests and synthetic example are already intended to run locally.
After upload, the **Actions** tab can run the same checks if GitHub Actions is
enabled. A green workflow validates synthetic behavior, not manuscript figures.

Run with the original data and compare against your research results as described
in `docs/REPRODUCIBILITY.md`. Complete the missing data-version and aggregation
details. If the source cannot yet reproduce a figure, keep that limitation
explicit in the repository and submission statement.

## 6. Freeze the submission version

After your checks and metadata edits:

1. On the repository page, open **Releases → Draft a new release**.
2. Create a new tag **`v0.1.0`** targeting the checked `main` commit.
3. Use the title `Observed trend analysis for manuscript submission`.
4. Describe the scope, supported indices, validation performed and missing data.
   Do not say the manuscript figures were reproduced unless you have checked them.
5. Select **Publish release**.

The release URL will be
`https://github.com/YOUR-USERNAME/energy-transition-climate-risk-brazil/releases/tag/v0.1.0`.
Record the full commit SHA as well. Keep that submitted version unchanged;
release a new version for subsequent corrections.

## 7. Optional Zenodo DOI

For a persistent scholarly identifier, connect the public repository to
[Zenodo](https://zenodo.org/) **before publishing the release you want archived**:

1. Sign in to Zenodo with GitHub and authorize the integration.
2. In Zenodo's GitHub settings, enable the repository.
3. Publish the GitHub release described above. Confirm that Zenodo creates the
   archive, then review the archived files, software authors and license metadata.
4. Copy the DOI for that specific software version into your submission.

If you already published the release before enabling the integration, follow
Zenodo's current instructions to archive it, or publish a newly checked version
after enabling it; do not assume an older release was archived automatically.
The GitHub address and Zenodo DOI are separate identifiers. Adding the DOI to
`CITATION.cff` afterward updates the active branch, not the previously archived
release. Version-specific DOIs identify the exact submitted software version.

## 8. Add the link to the submission

Use the code-availability field or an appropriate manuscript section. Copy the
scope-specific wording in `docs/SUBMISSION_TEXT.md`, replacing every placeholder.
Use the repository URL plus the frozen release URL or software DOI. Test access
in a private/incognito window when the repository is intended to be public.

## Alternative upload using Git in Terminal

Use this route **instead of the browser upload**. It assumes you created an
empty repository in step 2 and have Git installed (`git --version`). Open a
terminal in the extracted project folder and run the commands one line at a time:

```bash
git init
git branch -M main
git config user.name "YOUR NAME"
git config user.email "YOUR VERIFIED OR GITHUB NOREPLY EMAIL"
git add .
git status
git commit -m "Add observed climate trend analysis and documentation"
git remote add origin https://github.com/YOUR-USERNAME/energy-transition-climate-risk-brazil.git
git push -u origin main
```

Replace the name, email and username placeholders before use. The identity
commands apply to this repository only. At `git status`, inspect the staged
files before committing. `.gitignore` excludes local data and environments.
Authenticate through GitHub's supported browser/credential flow; a GitHub account
password is not used as the Git HTTPS password. Never place credentials in code
or in the remote URL.

If you already uploaded using the browser, **do not push an unrelated newly
initialized history**. Instead, clone the existing repository and work in that
clone:

```bash
git clone https://github.com/YOUR-USERNAME/energy-transition-climate-risk-brazil.git
cd energy-transition-climate-risk-brazil
```

For later local edits in an existing clone:

```bash
git pull --ff-only
git add .
git status
git commit -m "Document the updated analysis"
git push
```

Resolve any reported conflicts before continuing; do not force-push over an
existing repository to solve a first-upload mismatch.

## Official instructions

- [Create a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)
- [Upload files](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)
- [Citation metadata](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)
- [Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [Licensing](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- [GitHub and Zenodo identifiers](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content)
- [Zenodo GitHub integration](https://help.zenodo.org/docs/github/)

Web instructions checked on October 27, 2026; button labels may change.
