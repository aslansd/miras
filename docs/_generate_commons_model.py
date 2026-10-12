import dataclasses, sys
sys.path.insert(0, "src")
from miras.commons.model import Group, Innovation, Resource, Learning, Mechanisms, Seeding

def table(cls):
    rows = ["| field | default |", "| --- | --- |"]
    for f in dataclasses.fields(cls):
        rows.append(f"| `{f.name}` | `{f.default!r}` |")
    return "\n".join(rows)

head = open("docs/_commons_model_head.md").read()
parts = [head, "## Defaults (generated from the code)\n",
         "This section is generated from the dataclasses in `miras/commons/model.py`; "
         "`tests/test_commons.py::test_reference_doc_matches_code` fails if it goes stale.\n"]
for cls in (Group, Innovation, Resource, Learning, Mechanisms, Seeding):
    parts += [f"### `{cls.__name__}`\n", table(cls), ""]
open("docs/commons-model.md", "w").write("\n".join(parts) + "\n")
