# Publishing

How miras is built, uploaded and checked (first used for 0.1.0; the same
procedure applies to every release), and what to check for the 0.2 series.

## 1. Build

From the project folder, in a fresh virtual environment:

```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install build twine
rm -rf dist build src/*.egg-info
python -m build              # writes dist/miras-X.Y.Z.tar.gz and dist/miras-X.Y.Z-py3-none-any.whl
twine check dist/*           # both must say PASSED
```

## 2. Upload

```
python -m twine upload dist/*
```

twine asks for an API token (create one at https://pypi.org/manage/account/token/;
the username is `__token__` if asked). The line
`WARNING This environment is not supported for trusted publishing` is harmless:
it means the upload used a token rather than GitHub-based trusted publishing.
To avoid pasting the token each time, put it in `~/.pypirc`:

```
[pypi]
username = __token__
password = pypi-...
```

A dry run on TestPyPI first is optional:
`twine upload --repository testpypi dist/*`, then
`pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple miras`.

## 3. Check the release as a user would

In a new environment (or the same one), install from PyPI rather than from
the source folder:

```
pip install --no-cache-dir -U miras
pip install "miras[all]" pytest
install_cmdstan                  # once per machine; see README "Installing CmdStan"
miras doctor                     # every line should say ok
pytest -q                        # 130 passed, 1 skipped (0.2.1)
```

Then the end-to-end checks in `TESTING.md` (the README example and the four
paper workflows).

## 4. Next release

- Bump the version in **three** places: `pyproject.toml`,
  `src/miras/__init__.py` and `CITATION.cff` (`version` and `date-released`).
- Add a `CHANGELOG.md` entry.
- If a default in `miras/commons/model.py` changed, regenerate the model
  reference: `python docs/_generate_commons_model.py` (a test fails if it is
  stale).
- Run `pytest -q --run-slow` (needs CmdStan).
- Build, check and upload as above.

## The 0.2 series

0.2.0 added `miras.commons`; 0.2.1 adds the analysis tools and fixes found in
its first full runs. Nothing in 0.2.1 changes a simulation result: the same
command and seed give the same numbers as 0.2.0 (checked by the unchanged V1
to V9 tests and the resume test). 0.2.1 summaries have two extra columns
(`a_star`, `adoption_gap`); `analyze` reads summaries from both versions.

Before uploading 0.2.1:

1. `pytest -q` in a clean environment with `pip install "miras[all]" pytest`:
   130 passed, 1 skipped.
2. `miras commons example > /tmp/g.json && miras commons scenario /tmp/g.json --reps 3`
   finishes and prints a report.
3. `miras commons analyze` on the 0.2.0 summaries reproduces
   `docs/commons-results-0.2.0.md`.

If 0.2.0 was never uploaded, uploading only 0.2.1 is fine: versions need not
be consecutive on PyPI.

## PyPI releases are immutable

The project page on PyPI shows the README (the `long_description`) of the
**latest release**, as stored inside the uploaded files. It cannot be edited
afterwards, and a file name can never be uploaded twice, even after deleting
it. So there is no way to change what PyPI shows for 0.1.0.

To publish documentation changes you need a new version number:

- **Documentation only**: a *post-release*, e.g. `0.1.0.post1`. PEP 440 defines
  post-releases for minor fixes that do not change the distributed software,
  such as documentation. pip treats it as newer than 0.1.0, and the PyPI page then
  shows its README.
- **Any code change**: a normal version, e.g. `0.1.1`.

The README on GitHub can be updated at any time without a release; the PyPI
page catches up with the next upload.

If a release is broken, *yank* it from the release's management page on PyPI
rather than deleting it: pip then skips it unless the exact
version is requested, and nobody's pinned install breaks.

## Publishing documentation changes for 0.2.1

The README on PyPI is the one inside the uploaded 0.2.1 files. To show the
updated README (with the results of the full runs) without changing any code,
upload a post-release:

1. Set the version to `0.2.1.post1` in `pyproject.toml`, `src/miras/__init__.py`
   and `CITATION.cff`.
2. Turn the CHANGELOG's "Unreleased" heading into `0.2.1.post1 — <date>`.
3. Build, check and upload as in sections 1 and 2.

Alternatively, keep the changes unreleased until 0.2.2 (planned: `--set` for
model parameters and the identifiability adapter); GitHub shows the new
README as soon as it is pushed.
