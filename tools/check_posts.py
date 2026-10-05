# -*- coding: utf-8 -*-
"""Post JSON fayllarini tekshiradi. Xato bo'lsa — 1 kodi bilan chiqadi (GitHub Actions to'xtaydi).

    python tools/check_posts.py posts
"""
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REQUIRED = ["id", "rubric", "title", "scheduled_at", "caption", "prompt", "status"]
STATUSES = {"draft", "needs_input", "approved", "published", "failed", "overdue"}
RUBRICS = {"#narx", "#obraz", "#topilma", "#keys", "#boj", "#taqiq", "#dokon", "#kuryer",
           "#olcham", "#savol", "#firibgar", "#flesh", "#digest", "#post"}


def vislen(caption: str) -> int:
    lines = [l for l in caption.split("\n") if "{{APP_URL}}" not in l and "{{CONSULT_URL}}" not in l]
    text = html.unescape(re.sub(r"<[^>]+>", "", "\n".join(lines)))
    return len(text.encode("utf-16-le")) // 2


def main(folder: str) -> int:
    root = Path(folder)
    files = sorted(root.glob("*.json"))
    if not files:
        print(f"Post topilmadi: {root}")
        return 0
    ids = {f.stem for f in files}
    errors, warns = [], []
    for f in files:
        try:
            p = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"{f.name}: JSON buzilgan — {e}")
            continue
        for k in REQUIRED:
            if k not in p:
                errors.append(f"{f.name}: '{k}' maydoni yo'q")
        if p.get("id") != f.stem:
            errors.append(f"{f.name}: id ({p.get('id')}) fayl nomiga mos emas")
        try:
            dt = datetime.fromisoformat(p.get("scheduled_at", ""))
            if dt.utcoffset() is None:
                errors.append(f"{f.name}: scheduled_at da vaqt zonasi yo'q (+05:00 bo'lishi kerak)")
        except ValueError:
            errors.append(f"{f.name}: scheduled_at noto'g'ri")
        if p.get("status") not in STATUSES:
            errors.append(f"{f.name}: status noto'g'ri — {p.get('status')}")
        if p.get("rubric") not in RUBRICS:
            warns.append(f"{f.name}: noma'lum rubrika {p.get('rubric')}")
        cap = p.get("caption", "")
        n = vislen(cap)
        if n > 1024:
            warns.append(f"{f.name}: matn {n} belgi (>1024) — rasm va matn alohida chiqadi")
        if n > 4096:
            errors.append(f"{f.name}: matn {n} belgi — Telegram chegarasi 4096")
        for target in re.findall(r"\{\{LINK:([A-Za-z0-9_\-]+)\}\}", cap):
            if target not in ids:
                warns.append(f"{f.name}: havola mavjud bo'lmagan postga — {target}")
        if "@Pochtam_shopo" not in cap:
            warns.append(f"{f.name}: oxirida @Pochtam_shopo yo'q")
        opened = re.findall(r"<(b|i|u|s|code|a)\b", cap)
        closed = re.findall(r"</(b|i|u|s|code|a)>", cap)
        if sorted(opened) != sorted(closed):
            errors.append(f"{f.name}: HTML teglar yopilmagan")

    for w in warns:
        print("  ogohlantirish:", w)
    for e in errors:
        print("  XATO:", e)
    print(f"{len(files)} ta post tekshirildi — {len(errors)} xato, {len(warns)} ogohlantirish")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "posts"))
