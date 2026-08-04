"""Generate the code reference pages."""

from pathlib import Path

root = Path(__file__).parent.parent.parent
src = root / "src"

for path in sorted(src.rglob("*.py")):
    module_path = path.relative_to(src).with_suffix("")
    doc_path = path.relative_to(src / "runible").with_suffix(".md")
    full_doc_path = Path("docs/reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
    elif parts[-1] == "__main__":
        continue

    full_doc_path.parent.mkdir(exist_ok=True)
    print(f"VERBOSE: Writing to '{full_doc_path}'")
    with open(full_doc_path, "w") as fd:
        identifier = ".".join(parts)
        content = "## ::: " + identifier
        print(f"VERBOSE:    `{content}`")
        fd.write(content)
