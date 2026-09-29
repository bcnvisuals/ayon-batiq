"""Build the AYON server package: dist/batiq-<version>.zip.

Layout matches what the AYON server stores for an installed add-on:
package.py, LICENSE, server/, and private/client.zip holding ayon_batiq/.
"""
import io
import runpy
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKIP = {"__pycache__"}


def _files(base: Path):
    for path in sorted(base.rglob("*")):
        if path.is_file() and not SKIP.intersection(path.parts) and path.suffix != ".pyc":
            yield path


def main() -> Path:
    package = runpy.run_path(str(ROOT / "package.py"))
    name, version = package["name"], package["version"]
    client_version = runpy.run_path(str(ROOT / "client" / package["client_dir"] / "version.py"))["__version__"]
    if client_version != version:
        raise SystemExit(f"version mismatch: package.py {version}, client {client_version}")

    client = io.BytesIO()
    with zipfile.ZipFile(client, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in _files(ROOT / "client"):
            archive.write(path, path.relative_to(ROOT / "client").as_posix())

    output = ROOT / "dist" / f"{name}-{version}.zip"
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(ROOT / "package.py", "package.py")
        archive.write(ROOT / "LICENSE", "LICENSE")
        for path in _files(ROOT / "server"):
            archive.write(path, path.relative_to(ROOT).as_posix())
        archive.writestr("private/client.zip", client.getvalue())
    print(output)
    return output


if __name__ == "__main__":
    main()
