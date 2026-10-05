# -*- coding: utf-8 -*-
"""
Pochtachi — Telegram'ga joylovchi. GitHub Actions ichida ishlaydi (server kerak emas).

Rejimlar (MODE muhit o'zgaruvchisi):
  due     — vaqti kelgan tasdiqlangan va «hozir joylash» belgilangan postlarni kanalga chiqaradi (jadval)
  test    — POST_ID postini faqat adminning shaxsiy chatiga yuboradi -> state/last_test.json
  health  — bot, kanal, huquqlarni tekshiradi, admin_id ni topadi -> state/health.json

Muhit: TELEGRAM_BOT_TOKEN (GitHub secret), MODE, POST_ID, REQ (panel so'rov ID si),
       TG_API_BASE (faqat sinov uchun), NO_GIT=1 (git commit/push qilmaslik).
Faqat Python standart kutubxonasi — pip kerak emas.
"""
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"
IMAGES = ROOT / "images"
STATE = ROOT / "state"
SETTINGS_PATH = ROOT / "settings.json"
TZ = timezone(timedelta(hours=5))  # Toshkent
CAPTION_LIMIT, TEXT_LIMIT = 1024, 4096
USE_GIT = os.environ.get("NO_GIT") != "1"


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ fayllar
def read_json(p: Path, default=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def write_json(p: Path, data) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def settings() -> dict:
    return read_json(SETTINGS_PATH, {}) or {}


def list_posts() -> list[dict]:
    out = []
    for f in sorted(POSTS.glob("*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception as e:
            log(f"o'qilmadi: {f.name} ({e})")
    out.sort(key=lambda p: p.get("scheduled_at", ""))
    return out


def post_file(pid: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_\-]{1,80}", pid or ""):
        raise SystemExit(f"Noto'g'ri post ID: {pid!r}")
    return POSTS / f"{pid}.json"


def parse_dt(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=TZ)


def now() -> datetime:
    fake = os.environ.get("FAKE_NOW")  # sinov uchun
    return parse_dt(fake) if fake else datetime.now(TZ)


# ------------------------------------------------------------------ git
def git(*args, check=True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, check=check, capture_output=True, text=True)


def sync() -> None:
    """Eng so'nggi holatni oladi (panel shu orada nimadir o'zgartirgan bo'lishi mumkin)."""
    if USE_GIT:
        git("pull", "--rebase", "-X", "theirs", "origin", "main", check=False)


def commit(msg: str) -> None:
    """O'zgarishni darhol GitHub'ga yozadi. Panel bilan to'qnashuvda — qayta urinadi."""
    if not USE_GIT:
        return
    git("add", "-A")
    if git("diff", "--cached", "--quiet", check=False).returncode == 0:
        return
    git("commit", "-m", f"bot: {msg}")
    for attempt in range(6):
        if git("push", "origin", "HEAD:main", check=False).returncode == 0:
            return
        time.sleep(2 + attempt * 2)
        # rebase paytida «theirs» = bot commiti: kanalga chiqqan holat ustun turadi
        r = git("pull", "--rebase", "-X", "theirs", "origin", "main", check=False)
        if r.returncode != 0:
            git("rebase", "--abort", check=False)
    log("OGOHLANTIRISH: GitHub'ga yozib bo'lmadi:", msg)


# ------------------------------------------------------------------ caption
TAG_RE = re.compile(r"<[^>]+>")


def vislen(caption_html: str) -> int:
    text = html.unescape(TAG_RE.sub("", caption_html))
    return len(text.encode("utf-16-le")) // 2


def render_caption(caption: str, cfg: dict, posts_by_id: dict) -> str:
    tokens = {"{{APP_URL}}": (cfg.get("app_url") or "").strip(),
              "{{CONSULT_URL}}": (cfg.get("consult_url") or "").strip()}
    lines = []
    for line in caption.split("\n"):
        drop = False
        for tok, val in tokens.items():
            if tok in line:
                if not val:
                    drop = True
                    break
                line = line.replace(tok, html.escape(val, quote=True))
        if not drop:
            lines.append(line)
    out = "\n".join(lines)
    channel = (cfg.get("channel_id") or "").strip()
    uname = channel[1:] if channel.startswith("@") else ""

    def link_sub(m):
        target = posts_by_id.get(m.group(1))
        if target and target.get("message_id") and uname:
            return f'<a href="https://t.me/{uname}/{target["message_id"]}">{m.group(2)}</a>'
        return m.group(2)

    return re.sub(r'<a href="\{\{LINK:([A-Za-z0-9_\-]+)\}\}">(.*?)</a>', link_sub, out, flags=re.S)


# ------------------------------------------------------------------ telegram
class TgError(RuntimeError):
    pass


def _multipart(fields: dict, files: dict) -> tuple[bytes, str]:
    boundary = "----pochtachi" + uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, (name, data) in files.items():
        ctype = "image/png" if name.endswith(".png") else "image/webp" if name.endswith(".webp") else "image/jpeg"
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{name}"\r\n'
                     f'Content-Type: {ctype}\r\n\r\n'.encode() + data + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def tg(method: str, data: dict | None = None, files: dict | None = None) -> dict:
    token = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    if not token:
        raise TgError("TELEGRAM_BOT_TOKEN secret o'rnatilmagan")
    base = os.environ.get("TG_API_BASE", "https://api.telegram.org")
    fields = {k: (v if isinstance(v, str) else json.dumps(v)) for k, v in (data or {}).items() if v is not None}
    if fields or files:
        body, ctype = _multipart(fields, files or {})
        req = urllib.request.Request(f"{base}/bot{token}/{method}", data=body, headers={"Content-Type": ctype})
    else:
        # Parametrsiz so'rov (getMe) — bo'sh multipart yubormaymiz, oddiy GET
        req = urllib.request.Request(f"{base}/bot{token}/{method}")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                j = json.loads(r.read().decode())
            break
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            try:
                j = json.loads(raw)
            except Exception:
                snippet = re.sub(r"<[^>]+>", " ", raw.replace(token, "***"))
                snippet = " ".join(snippet.split())[:120]
                raise TgError(f"Telegram HTTP {e.code}" + (f" — {snippet}" if snippet else ""))
            retry = (j.get("parameters") or {}).get("retry_after")
            if e.code == 429 and retry and attempt < 2:
                time.sleep(min(int(retry), 30))
                continue
            break
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == 2:
                raise TgError(f"Telegram'ga ulanib bo'lmadi ({type(e).__name__})")
            time.sleep(3)
    if not j.get("ok"):
        raise TgError(j.get("description") or "Noma'lum Telegram xatosi")
    return j["result"]


NO_PREVIEW = {"is_disabled": True}


def send_post(post: dict, chat_id, cfg: dict, posts_by_id: dict) -> int:
    caption = render_caption(post.get("caption", ""), cfg, posts_by_id)
    n = vislen(caption)
    if n > TEXT_LIMIT:
        raise TgError(f"Matn juda uzun: {n} belgi (chegara {TEXT_LIMIT})")
    img = post.get("image")
    if img:
        path = IMAGES / img
        if not path.exists():
            raise TgError(f"Rasm fayli topilmadi ({img}) — panelda qayta yuklang")
        photo = {"photo": (path.name, path.read_bytes())}
        if n <= CAPTION_LIMIT:
            return tg("sendPhoto", {"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"}, photo)["message_id"]
        res = tg("sendPhoto", {"chat_id": chat_id}, photo)
        tg("sendMessage", {"chat_id": chat_id, "text": caption, "parse_mode": "HTML",
                           "link_preview_options": NO_PREVIEW,
                           "reply_parameters": {"message_id": res["message_id"]}})
        return res["message_id"]
    return tg("sendMessage", {"chat_id": chat_id, "text": caption, "parse_mode": "HTML",
                              "link_preview_options": NO_PREVIEW})["message_id"]


def notify_admin(cfg: dict, text: str) -> None:
    if not cfg.get("admin_id"):
        return
    try:
        tg("sendMessage", {"chat_id": cfg["admin_id"], "text": text, "parse_mode": "HTML",
                           "link_preview_options": NO_PREVIEW})
    except TgError as e:
        log("admin xabari yuborilmadi:", e)


def esc(s) -> str:
    return html.escape(str(s or ""), quote=False)


# ------------------------------------------------------------------ rejimlar
def publish_one(pid: str, reason: str, cfg: dict) -> bool:
    sync()
    pf = post_file(pid)
    post = read_json(pf)
    if not post or post.get("status") == "published":
        return False
    channel = (cfg.get("channel_id") or "").strip()
    if not channel:
        raise SystemExit("settings.json da channel_id yo'q")
    by_id = {p["id"]: p for p in list_posts()}
    try:
        mid = send_post(post, channel, cfg, by_id)
    except TgError as e:
        post.update(status="failed", error=str(e))
        post.pop("publish_now", None)
        write_json(pf, post)
        commit(f"xato {pid}")
        log(f"JOYLANMADI {pid}: {e}")
        notify_admin(cfg, f"❌ <b>Joylanmadi:</b> {esc(post.get('title', pid))}\n{esc(e)}")
        return False
    post.update(status="published", message_id=mid, error=None,
                published_at=now().isoformat(timespec="seconds"), published_by=reason)
    post.pop("publish_now", None)
    write_json(pf, post)
    commit(f"joylandi {pid}")  # darhol — qayta yuborilmasligi uchun
    uname = channel[1:] if channel.startswith("@") else ""
    log(f"joylandi {pid} -> {mid} ({reason})")
    notify_admin(cfg, f"✅ <b>Kanalga chiqdi:</b> {esc(post.get('title', pid))}\n"
                      + (f"https://t.me/{uname}/{mid}" if uname else ""))
    return True


def mode_due(cfg: dict) -> None:
    t = now()
    grace = timedelta(hours=float(cfg.get("late_grace_hours", 2)))
    for p in list_posts():
        st = p.get("status")
        if p.get("publish_now") and st not in ("published",):
            publish_one(p["id"], "qo'lda", cfg)
            continue
        if st != "approved" or not p.get("scheduled_at"):
            continue
        when = parse_dt(p["scheduled_at"])
        if when > t:
            continue
        if t - when > grace:
            sync()
            p = read_json(post_file(p["id"])) or p
            if p.get("status") != "approved" or p.get("publish_now"):
                continue
            p["status"] = "overdue"
            write_json(post_file(p["id"]), p)
            commit(f"vaqti o'tdi {p['id']}")
            notify_admin(cfg, f"⏰ <b>Vaqti o'tib ketdi:</b> {esc(p.get('title', p['id']))}\n"
                              "Panelda «Hozir joylash» ni bosing yoki vaqtini o'zgartiring.")
            continue
        publish_one(p["id"], "jadval", cfg)
    daily_reminder(cfg, t)


def daily_reminder(cfg: dict, t: datetime) -> None:
    """Har kuni ertalab (08:00–09:59 dagi birinchi ishga tushishda) bugungi tayyor bo'lmagan postlar haqida."""
    if not (8 <= t.hour < 10) or not cfg.get("admin_id"):
        return
    rpath = STATE / "reminder.json"
    today = t.date().isoformat()
    if (read_json(rpath, {}) or {}).get("date") == today:
        return
    end = t + timedelta(hours=24)
    todo = []
    for p in list_posts():
        if p.get("status") in ("published", "approved") or not p.get("scheduled_at"):
            continue
        when = parse_dt(p["scheduled_at"])
        if t <= when <= end:
            need = []
            if not p.get("image"):
                need.append("rasm")
            if p.get("status") == "needs_input":
                need.append("material")
            need.append("tasdiq")
            todo.append(f"• {when:%H:%M} {esc(p.get('rubric'))} {esc(p.get('title'))} — {', '.join(need)}")
    write_json(rpath, {"date": today})
    commit("kunlik eslatma")
    if todo:
        notify_admin(cfg, "☀️ <b>Keyingi 24 soatda tayyor bo'lmagan postlar:</b>\n" + "\n".join(todo)
                          + ("\n\n" + cfg["panel_url"] if cfg.get("panel_url") else ""))


def mode_test(cfg: dict, pid: str, req: str) -> None:
    res = {"req": req, "post_id": pid, "at": now().isoformat(timespec="seconds")}
    try:
        if not cfg.get("admin_id"):
            raise TgError("Sizning Telegram ID'ingiz noma'lum — botga /start yozing va «Ulanishni tekshirish» ni bosing")
        post = read_json(post_file(pid))
        if not post:
            raise TgError("Post topilmadi")
        send_post(post, cfg["admin_id"], cfg, {p["id"]: p for p in list_posts()})
        res["ok"] = True
    except TgError as e:
        res.update(ok=False, error=str(e))
    log("sinov:", res)
    write_json(STATE / "last_test.json", res)
    commit(f"sinov {pid}")


def mode_health(cfg: dict, req: str) -> None:
    out = {"req": req, "at": now().isoformat(timespec="seconds"), "channel_id": cfg.get("channel_id"),
           "token": bool(os.environ.get("TELEGRAM_BOT_TOKEN"))}
    # Tokenning o'zi chiqarilmaydi — faqat ko'rinishi to'g'rimi (123456789:AAH…)
    tok = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    out["token_format_ok"] = bool(re.fullmatch(r"\d{5,}:[A-Za-z0-9_-]{30,}", tok))
    try:
        me = tg("getMe")
        out["bot"] = "@" + me.get("username", "")
        if not cfg.get("admin_id") and cfg.get("admin_username"):
            want = cfg["admin_username"].lstrip("@").lower()
            try:
                for u in tg("getUpdates", {"timeout": 0, "allowed_updates": ["message"]}):
                    frm = (u.get("message") or {}).get("from") or {}
                    if (frm.get("username") or "").lower() == want:
                        sync()
                        s = settings()
                        s["admin_id"] = frm["id"]
                        write_json(SETTINGS_PATH, s)
                        cfg["admin_id"] = frm["id"]
                        out["admin_found"] = True
                        break
            except TgError as e:
                out["admin_lookup_error"] = str(e)
        out["admin_known"] = bool(cfg.get("admin_id"))
        try:
            chat = tg("getChat", {"chat_id": cfg.get("channel_id")})
            out["channel_title"] = chat.get("title")
            m = tg("getChatMember", {"chat_id": cfg.get("channel_id"), "user_id": me["id"]})
            out["bot_status"] = m.get("status")
            out["can_post"] = m.get("status") == "creator" or bool(m.get("can_post_messages"))
        except TgError as e:
            out["error"] = f"Kanal: {e}"
    except TgError as e:
        out["error"] = f"Bot: {e}"
    log("holat:", out)
    write_json(STATE / "health.json", out)
    commit("ulanish tekshiruvi")


def main() -> int:
    if USE_GIT:
        git("config", "user.name", "pochtachi-bot", check=False)
        git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com", check=False)
    mode = (os.environ.get("MODE") or "due").strip()
    pid = (os.environ.get("POST_ID") or "").strip()
    req = (os.environ.get("REQ") or "").strip()
    sync()
    cfg = settings()
    if mode == "due":
        mode_due(cfg)
    elif mode == "test":
        mode_test(cfg, pid, req)
    elif mode == "health":
        mode_health(cfg, req)
    else:
        log("Noma'lum rejim:", mode)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
