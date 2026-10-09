# -*- coding: utf-8 -*-
"""Post JSON fayllarini tekshiradi. Xato bo'lsa — 1 kodi bilan chiqadi (GitHub Actions to'xtaydi).

    python tools/check_posts.py            # hamma kanal (channels.json)
    python tools/check_posts.py posts      # faqat asosiy kanal (Pochtachi)
    python tools/check_posts.py channels/ai/posts
"""
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ["id", "rubric", "title", "scheduled_at", "caption", "prompt", "status"]
STATUSES = {"draft", "needs_input", "approved", "published", "failed", "overdue"}
RUBRICS = {"#narx", "#obraz", "#topilma", "#keys", "#boj", "#taqiq", "#dokon", "#kuryer",
           "#olcham", "#savol", "#firibgar", "#flesh", "#digest", "#post"}
TAGS = "b|i|u|s|code|a|pre|blockquote|tg-spoiler"
FILE_LIMIT = 45 * 1024 * 1024      # Telegram bot hujjat chegarasi 50 MB


def vislen(caption: str) -> int:
    lines = [l for l in caption.split("\n") if "{{APP_URL}}" not in l and "{{CONSULT_URL}}" not in l]
    text = html.unescape(re.sub(r"<[^>]+>", "", "\n".join(lines)))
    return len(text.encode("utf-16-le")) // 2


def read_json(p: Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return default


def check_folder(root: Path, label: str = "") -> tuple[int, int, int]:
    """root — posts papkasi; kanal papkasi (settings.json, images/, files/) — uning ustidagi papka."""
    base = root.resolve().parent
    cfg = read_json(base / "settings.json", {}) or {}
    rubrics = set(cfg.get("rubrics") or RUBRICS)
    handle = str(cfg.get("channel_id") or "").strip()
    pre = f"{label}: " if label else ""
    files = sorted(root.glob("*.json"))
    if not files:
        print(f"{pre}post topilmadi: {root}")
        return 0, 0, 0
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
        if p.get("rubric") not in rubrics:
            warns.append(f"{f.name}: noma'lum rubrika {p.get('rubric')}")
        cap = p.get("caption", "")
        n = vislen(cap)
        if n > 1024:
            # Rasmli postda matn 1024 dan uzun bo'lsa — rasm va matn ikki xabar bo'lib chiqadi.
            # Uzun dars postlari uchun bu ataylab qilingan bo'lishi mumkin ("long_ok": true).
            if not p.get("long_ok"):
                warns.append(f"{f.name}: matn {n} belgi (>1024) — rasm va matn alohida chiqadi")
        if n > 4096:
            errors.append(f"{f.name}: matn {n} belgi — Telegram chegarasi 4096")
        for target in re.findall(r"\{\{LINK:([A-Za-z0-9_\-]+)\}\}", cap):
            if target not in ids:
                warns.append(f"{f.name}: havola mavjud bo'lmagan postga — {target}")
        if "{{CHANNEL}}" not in cap and (not handle or handle not in cap):
            warns.append(f"{f.name}: oxirida {handle or '{{CHANNEL}}'} yo'q")
        opened = re.findall(rf"<({TAGS})\b", cap)
        closed = re.findall(rf"</({TAGS})>", cap)
        if sorted(opened) != sorted(closed):
            errors.append(f"{f.name}: HTML teglar yopilmagan")
        if p.get("image") and p.get("status") != "published" and not (base / "images" / p["image"]).is_file():
            warns.append(f"{f.name}: rasm fayli yo'q — images/{p['image']}")
        atts = p.get("attachments") or []
        if not isinstance(atts, list):
            errors.append(f"{f.name}: attachments ro'yxat bo'lishi kerak")
            atts = []
        for a in atts:
            rel = str((a or {}).get("file") or "") if isinstance(a, dict) else ""
            if not re.fullmatch(r"files/[A-Za-z0-9_\-./]{1,150}", rel) or ".." in rel:
                errors.append(f"{f.name}: biriktirilgan fayl yo'li noto'g'ri — {rel!r} (files/… bo'lsin)")
                continue
            fp = base / rel
            if not fp.is_file():
                errors.append(f"{f.name}: biriktirilgan fayl topilmadi — {rel}")
            elif fp.stat().st_size > FILE_LIMIT:
                errors.append(f"{f.name}: fayl juda katta — {rel}")
            if vislen(str(a.get("caption") or "")) > 1024:
                errors.append(f"{f.name}: fayl izohi 1024 belgidan uzun — {rel}")

    for w in warns:
        print(f"  ogohlantirish: {pre}{w}")
    for e in errors:
        print(f"  XATO: {pre}{e}")
    print(f"{pre}{len(files)} ta post tekshirildi — {len(errors)} xato, {len(warns)} ogohlantirish")
    return len(files), len(errors), len(warns)


def main(argv: list[str]) -> int:
    if argv:
        return 1 if check_folder(Path(argv[0]))[1] else 0
    chans = (read_json(ROOT / "channels.json", {}) or {}).get("channels") or [{"key": "", "dir": ""}]
    bad = 0
    for c in chans:
        d = str(c.get("dir") or "").strip("/")
        bad += check_folder(ROOT / d / "posts" if d else ROOT / "posts", c.get("key") or "")[1]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
