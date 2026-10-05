# -*- coding: utf-8 -*-
"""ui/index.html ni alohida ochiq panel repo'siga (GitHub Pages) yuboradi. `gh` dasturi orqali ishlaydi.

    python tools/sync_ui.py

settings.json da `ui_repo` bo'sh bo'lsa — panel shu repo'ning o'zidan chiqadi
(.github/workflows/pages.yml), ui/index.html push qilinsa o'zi yangilanadi.
"""
import base64
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def gh(*args, inp=None, check=True):
    r = subprocess.run(["gh", *args], input=inp, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode:
        raise SystemExit(f"gh {' '.join(args[:3])}… xato: {r.stderr.strip()}")
    return r


def main() -> int:
    settings = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
    ui_repo = settings.get("ui_repo")
    if not ui_repo:
        print("Panel shu repo'dan GitHub Actions (pages.yml) orqali chiqadi — ui/index.html ni push qilish kifoya: "
              + (settings.get("panel_url") or ""))
        return 0
    data_repo = gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner").stdout.strip()

    html = (ROOT / "ui" / "index.html").read_text(encoding="utf-8").replace("__DATA_REPO__", data_repo)
    files = {"index.html": html, ".nojekyll": ""}
    changed = 0
    for path, text in files.items():
        r = gh("api", f"repos/{ui_repo}/contents/{path}", check=False)
        sha, same = None, False
        if r.returncode == 0:
            cur = json.loads(r.stdout)
            sha = cur["sha"]
            same = base64.b64decode(cur.get("content") or "").decode("utf-8", "replace") == text
        if same:
            continue
        body = {"message": "Panel yangilandi", "content": base64.b64encode(text.encode("utf-8")).decode()}
        if sha:
            body["sha"] = sha
        gh("api", "-X", "PUT", f"repos/{ui_repo}/contents/{path}", "--input", "-", inp=json.dumps(body))
        changed += 1
    owner, name = ui_repo.split("/")
    url = f"https://{owner.lower()}.github.io/{name}/"
    print(("Panel yangilandi" if changed else "Panel o'zgarmagan") + f": {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
