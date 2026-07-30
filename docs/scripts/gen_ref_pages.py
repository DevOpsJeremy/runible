"""Generate the code reference pages."""

from pathlib import Path

root = Path(__file__).parent.parent.parent
src = root / "src"
print(src)

for path in sorted(src.rglob("*.py")):
    print(f"path: {path}")
    module_path = path.relative_to(src).with_suffix("")
    print(f"module_path: {module_path}")
    doc_path = path.relative_to(src / "runible").with_suffix(".md")
    print(f"doc_path: {doc_path}")
    full_doc_path = Path("docs/reference", doc_path)
    print(f"full_doc_path: {full_doc_path}")

    parts = tuple(module_path.parts)
    print(f"parts: {parts}")

    if parts[-1] == "__init__":
        parts = parts[:-1]
    elif parts[-1] == "__main__":
        continue
    print(f"parts: {parts}")

    full_doc_path.parent.mkdir(exist_ok=True)
    with open(full_doc_path, "w") as fd:
        identifier = ".".join(parts)
        print(f"identifier: {identifier}")
        print("::: " + identifier, file=fd)

