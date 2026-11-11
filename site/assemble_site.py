import hashlib
import shutil
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
PAGES = ("index.html", "edit.html")
ASSETS = ("styles.css", "palette.css", "applications.css", "palette-data.js", "palette.js", "downloads-data.js", "downloads.js", "main.js")


def assemble(target):
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    versions = {name: hashlib.sha256((SITE / name).read_bytes()).hexdigest()[:10] for name in ASSETS}
    for name in ASSETS:
        shutil.copy2(SITE / name, target / name)
    for name in PAGES:
        page = (SITE / name).read_text(encoding="utf-8")
        for asset, version in versions.items():
            page = page.replace(f"href=\"{asset}\"", f"href=\"{asset}?v={version}\"").replace(f"src=\"{asset}\"", f"src=\"{asset}?v={version}\"")
        (target / name).write_text(page, encoding="utf-8", newline="\n")
    shutil.copytree(SITE / "downloads", target / "downloads")
    (target / ".nojekyll").write_text("", encoding="utf-8")
    (target / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8", newline="\n")
    return target


if __name__ == "__main__":
    print(assemble(Path(sys.argv[1]).resolve()))
