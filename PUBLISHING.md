# Publishing

```
pip install build twine
rm -rf dist build
python -m build                          # sdist + wheel
twine check dist/*
python -m venv /tmp/v && /tmp/v/bin/pip install dist/miras-*.whl
/tmp/v/bin/miras doctor                  # installs and runs outside the source tree
twine upload --repository testpypi dist/*  # optional dry run
twine upload dist/*
```

Before tagging a release: update `version` in `pyproject.toml`,
`src/miras/__init__.py` and `CITATION.cff`, add a CHANGELOG entry, and run
`pytest -q --run-slow`.
