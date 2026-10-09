# -*- coding: utf-8 -*-
"""
Pochtachi — Telegram'ga joylovchi. GitHub Actions ichida ishlaydi (server kerak emas).

Rejimlar (MODE muhit o'zgaruvchisi):
  due     — vaqti kelgan tasdiqlangan va «hozir joylash» belgilangan postlarni kanalga chiqaradi (jadval)
  test    — POST_ID postini faqat adminning shaxsiy chatiga yuboradi -> state/last_test.json
  health  — bot, kanal, huquqlarni tekshiradi, admin_id ni topadi -> state/health.json

Bir nechta kanal: channels.json — kanallar ro'yxati ({key, name, dir}). `dir` bo'sh — asosiy kanal
(repo ildizi: posts/, images/, settings.json, state/); boshqalari o'z papkasida (masalan channels/ai/).
`due` hamma kanalni aylanib chiqadi; `test` va `health` kanalni POST_ID oldidagi «<key>:» dan oladi
(masalan POST_ID=ai:2026-10-12-0830, tekshiruv uchun POST_ID=ai:) yoki CHANNEL=<key> dan.
Bot bitta — hamma kanalda admin bo'lishi kerak.

Muhit: TELEGRAM_BOT_TOKEN (GitHub secret), MODE, POST_ID, REQ (panel so'rov ID si), CHANNEL,
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
CHANNELS_PATH = ROOT / "channels.json"
TZ = timezone(timedelta(hours=5))  # Toshkent
CAPTION_LIMIT, TEXT_LIMIT = 1024, 4096
ATTACH_TRIES = 3                   # biriktirilgan fayl necha marta qayta yuboriladi
USE_GIT = os.environ.get("NO_GIT") != "1"

# Joriy kanal — use_channel() almashtiradi. Standart: asosiy kanal (repo ildizi).
CH = {"key": "", "name": "", "dir": ""}
BASE = ROOT
POSTS = ROOT / "posts"
IMAGES = ROOT / "images"
STATE = ROOT / "state"
SETTINGS_PATH = ROOT / "settings.json"
# Qo'shimcha kanal o'z settings.json ida bermasa — asosiy kanalnikidan olinadigan kalitlar
INHERIT = ("admin_username", "admin_id", "late_grace_hours", "panel_url")


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


def own_settings() -> dict:
    return read_json(SETTINGS_PATH, {}) or {}


def settings() -> dict:
    cfg = own_settings()
    if CH["dir"]:
        base = read_json(ROOT / "settings.json", {}) or {}
        for k in INHERIT:
            if cfg.get(k) in (None, "") and base.get(k) not in (None, ""):
                cfg[k] = base[k]
    return cfg


def channels() -> list[dict]:
    """channels.json dagi kanallar. Fayl bo'lmasa — bitta asosiy kanal (eski tuzilma)."""
    data = read_json(CHANNELS_PATH, None)
    items = data.get("channels") if isinstance(data, dict) else None
    out = []
    for c in items or [{}]:
        d = str(c.get("dir") or "").strip().strip("/")
        if d and not re.fullmatch(r"[A-Za-z0-9_\-]+(/[A-Za-z0-9_\-]+)*", d):
            log(f"channels.json: noto'g'ri papka {d!r} — o'tkazib yuborildi")
            continue
        out.append({"key": str(c.get("key") or ""), "name": str(c.get("name") or ""), "dir": d})
    return out


def use_channel(ch: dict) -> None:
    global CH, BASE, POSTS, IMAGES, STATE, SETTINGS_PATH
    CH = ch
    BASE = ROOT / ch["dir"] if ch["dir"] else ROOT
    POSTS, IMAGES, STATE, SETTINGS_PATH = BASE / "posts", BASE / "images", BASE / "state", BASE / "settings.json"


def ref(pid: str) -> str:
    """Commit va log uchun: qo'shimcha kanalda «ai/2026-10-12-0830»."""
    return f"{CH['key']}/{pid}" if CH["dir"] else pid


def who() -> str:
    """Admin xabarlarida kanal nomi (asosiy kanalda bo'sh)."""
    return f" · {esc(CH['name'] or CH['key'])}" if CH["dir"] else ""


def channel_of(cfg: dict) -> str:
    return str(cfg.get("channel_id") or "").strip()


def msg_url(cfg: dict, mid) -> str:
    """Kanaldagi xabar havolasi: ochiq kanal — t.me/<nom>/<id>, yopiq (-100…) — t.me/c/<raqam>/<id>."""
    ch = channel_of(cfg)
    if ch.startswith("@"):
        return f"https://t.me/{ch[1:]}/{mid}"
    if re.fullmatch(r"-100\d+", ch):
        return f"https://t.me/c/{ch[4:]}/{mid}"
    return ""


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
    channel = channel_of(cfg)
    handle = channel if channel.startswith("@") else ""
    lines = []
    for line in caption.split("\n"):
        drop = False
        for tok, val in tokens.items():
            if tok in line:
                if not val:
                    drop = True
                    break
                line = line.replace(tok, html.escape(val, quote=True))
        if not drop and "{{CHANNEL}}" in line:   # kanal manzili (@nom); yopiq kanalda — bo'sh
            line = line.replace("{{CHANNEL}}", handle).strip()
            if not line:                         # qator bo'shab qoldi — undan oldingi bo'sh qatorlar bilan olib tashlanadi
                while lines and not lines[-1].strip():
                    lines.pop()
                drop = True
        if not drop:
            lines.append(line)
    out = "\n".join(lines)

    def link_sub(m):
        target = posts_by_id.get(m.group(1))
        url = msg_url(cfg, target["message_id"]) if target and target.get("message_id") else ""
        if url:
            return f'<a href="{url}">{m.group(2)}</a>'
        return m.group(2)

    return re.sub(r'<a href="\{\{LINK:([A-Za-z0-9_\-]+)\}\}">(.*?)</a>', link_sub, out, flags=re.S)


# ------------------------------------------------------------------ telegram
class TgError(RuntimeError):
    pass


DOC_TYPES = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "pdf": "application/pdf", "csv": "text/csv", "txt": "text/plain", "zip": "application/zip",
    "png": "image/png", "jpg": "image/jpeg",
}


def _multipart(fields: dict, files: dict) -> tuple[bytes, str]:
    boundary = "----pochtachi" + uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, (name, data) in files.items():
        if k == "document":
            ctype = DOC_TYPES.get(name.rsplit(".", 1)[-1].lower(), "application/octet-stream")
        else:
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


def attachments(post: dict) -> list[dict]:
    a = post.get("attachments")
    return [x for x in a if isinstance(x, dict) and x.get("file")] if isinstance(a, list) else []


def send_file(att: dict, chat_id, cfg: dict, posts_by_id: dict, reply_to=None) -> int:
    """Postga biriktirilgan faylni (mashq fayli, shablon) hujjat qilib yuboradi. Yo'l — kanal papkasidagi files/…"""
    rel = str(att.get("file") or "")
    if not re.fullmatch(r"files/[A-Za-z0-9_\-./]{1,150}", rel) or ".." in rel:
        raise TgError(f"Fayl yo'li noto'g'ri: {rel!r} (kanal papkasidagi files/… bo'lishi kerak)")
    path = BASE / rel
    if not path.is_file():
        raise TgError(f"Biriktirilgan fayl topilmadi: {rel}")
    name = re.sub(r'[\r\n"\\/]', "_", str(att.get("name") or path.name))
    data = {"chat_id": chat_id}
    cap = render_caption(str(att.get("caption") or ""), cfg, posts_by_id)
    if cap:
        if vislen(cap) > CAPTION_LIMIT:
            raise TgError(f"Fayl izohi juda uzun: {name}")
        data.update(caption=cap, parse_mode="HTML")
    if reply_to:
        data["reply_parameters"] = {"message_id": reply_to, "allow_sending_without_reply": True}
    return tg("sendDocument", data, {"document": (name, path.read_bytes())})["message_id"]


def send_files(pid: str, cfg: dict) -> None:
    """Kanalga chiqqan postning hali yuborilmagan fayllarini yuboradi. Xato bo'lsa — keyingi ishga
    tushishda qayta uriniladi (ATTACH_TRIES marta), post esa «joylangan» bo'lib qolaveradi."""
    sync()
    pf = post_file(pid)
    post = read_json(pf)
    if not post or post.get("status") != "published":
        return
    todo = [a for a in attachments(post) if not a.get("message_id")]
    if not todo or int(post.get("attach_tries") or 0) >= ATTACH_TRIES:
        return
    by_id = {p["id"]: p for p in list_posts()}
    err = None
    for a in todo:
        try:
            a["message_id"] = send_file(a, channel_of(cfg), cfg, by_id, reply_to=post.get("message_id"))
            log(f"fayl yuborildi {ref(pid)}: {a['file']} -> {a['message_id']}")
        except TgError as e:
            err = (a, e)
            break
    if err:
        post["attach_tries"] = int(post.get("attach_tries") or 0) + 1
        post["attach_error"] = f"{err[0]['file']}: {err[1]}"
    else:
        post.pop("attach_tries", None)
        post["attach_error"] = None
    write_json(pf, post)
    commit(f"fayl {ref(pid)}")
    if err:
        tries = post["attach_tries"]
        log(f"FAYL YUBORILMADI {ref(pid)} ({tries}/{ATTACH_TRIES}): {post['attach_error']}")
        tail = ("Bir necha daqiqadan keyin qayta urinaman." if tries < ATTACH_TRIES
                else "Qayta urinilmaydi — faylni kanalga qo'lda yuboring.")
        if tries in (1, ATTACH_TRIES):
            notify_admin(cfg, f"📎 <b>Fayl yuborilmadi{who()}:</b> {esc(post.get('title', pid))}\n"
                              f"{esc(post['attach_error'])}\n{tail}")


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
    channel = channel_of(cfg)
    if not channel:
        raise SystemExit(f"{SETTINGS_PATH.relative_to(ROOT).as_posix()} da channel_id yo'q")
    by_id = {p["id"]: p for p in list_posts()}
    try:
        mid = send_post(post, channel, cfg, by_id)
    except TgError as e:
        post.update(status="failed", error=str(e))
        post.pop("publish_now", None)
        write_json(pf, post)
        commit(f"xato {ref(pid)}")
        log(f"JOYLANMADI {ref(pid)}: {e}")
        notify_admin(cfg, f"❌ <b>Joylanmadi{who()}:</b> {esc(post.get('title', pid))}\n{esc(e)}")
        return False
    post.update(status="published", message_id=mid, error=None,
                published_at=now().isoformat(timespec="seconds"), published_by=reason)
    post.pop("publish_now", None)
    write_json(pf, post)
    commit(f"joylandi {ref(pid)}")  # darhol — qayta yuborilmasligi uchun
    log(f"joylandi {ref(pid)} -> {mid} ({reason})")
    if attachments(post):
        send_files(pid, cfg)
    notify_admin(cfg, f"✅ <b>Kanalga chiqdi{who()}:</b> {esc(post.get('title', pid))}\n" + msg_url(cfg, mid))
    return True


def mode_due(cfg: dict) -> None:
    t = now()
    grace = timedelta(hours=float(cfg.get("late_grace_hours", 2)))
    if CH["dir"] and not channel_of(cfg):
        log(f"{CH['key']}: channel_id sozlanmagan — o'tkazib yuborildi")
        return
    for p in list_posts():   # oldingi ishga tushishda yuborilmay qolgan fayllar
        if p.get("status") == "published" and any(not a.get("message_id") for a in attachments(p)):
            send_files(p["id"], cfg)
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
            commit(f"vaqti o'tdi {ref(p['id'])}")
            notify_admin(cfg, f"⏰ <b>Vaqti o'tib ketdi{who()}:</b> {esc(p.get('title', p['id']))}\n"
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
    commit("kunlik eslatma" + (f" {CH['key']}" if CH["dir"] else ""))
    if todo:
        notify_admin(cfg, f"☀️ <b>Keyingi 24 soatda tayyor bo'lmagan postlar{who()}:</b>\n" + "\n".join(todo)
                          + ("\n\n" + cfg["panel_url"] if cfg.get("panel_url") else ""))


def mode_test(cfg: dict, pid: str, req: str) -> None:
    res = {"req": req, "post_id": pid, "at": now().isoformat(timespec="seconds")}
    try:
        if not cfg.get("admin_id"):
            raise TgError("Sizning Telegram ID'ingiz noma'lum — botga /start yozing va «Ulanishni tekshirish» ni bosing")
        post = read_json(post_file(pid))
        if not post:
            raise TgError("Post topilmadi")
        by_id = {p["id"]: p for p in list_posts()}
        mid = send_post(post, cfg["admin_id"], cfg, by_id)
        for a in attachments(post):
            send_file(a, cfg["admin_id"], cfg, by_id, reply_to=mid)
        res["ok"] = True
    except TgError as e:
        res.update(ok=False, error=str(e))
    log("sinov:", res)
    write_json(STATE / "last_test.json", res)
    commit(f"sinov {ref(pid)}")


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
                        s = own_settings()
                        s["admin_id"] = frm["id"]
                        write_json(SETTINGS_PATH, s)
                        cfg["admin_id"] = frm["id"]
                        out["admin_found"] = True
                        break
            except TgError as e:
                out["admin_lookup_error"] = str(e)
        out["admin_known"] = bool(cfg.get("admin_id"))
        try:
            if not channel_of(cfg):
                raise TgError(f"{SETTINGS_PATH.relative_to(ROOT).as_posix()} da channel_id yozilmagan")
            chat = tg("getChat", {"chat_id": channel_of(cfg)})
            out["channel_title"] = chat.get("title")
            m = tg("getChatMember", {"chat_id": channel_of(cfg), "user_id": me["id"]})
            out["bot_status"] = m.get("status")
            out["can_post"] = m.get("status") == "creator" or bool(m.get("can_post_messages"))
        except TgError as e:
            out["error"] = f"Kanal: {e}"
    except TgError as e:
        out["error"] = f"Bot: {e}"
    log("holat:", out)
    write_json(STATE / "health.json", out)
    commit("ulanish tekshiruvi" + (f" {CH['key']}" if CH["dir"] else ""))


def main() -> int:
    if USE_GIT:
        git("config", "user.name", "pochtachi-bot", check=False)
        git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com", check=False)
    mode = (os.environ.get("MODE") or "due").strip()
    pid = (os.environ.get("POST_ID") or "").strip()
    req = (os.environ.get("REQ") or "").strip()
    key = (os.environ.get("CHANNEL") or "").strip()
    if ":" in pid:                       # panel kanalni shu yerda beradi: «ai:2026-10-12-0830», «ai:»
        key, pid = pid.split(":", 1)
    if mode not in ("due", "test", "health"):
        log("Noma'lum rejim:", mode)
        return 2
    sync()
    chans = channels()
    if mode == "due":                    # jadval — hamma kanal; bittasidagi xato boshqasini to'xtatmaydi
        rc = 0
        for ch in chans:
            use_channel(ch)
            try:
                mode_due(settings())
            except SystemExit as e:
                log(f"XATO{' ' + ch['key'] if ch['dir'] else ''}: {e}")
                rc = 1
            except Exception as e:  # noqa: BLE001
                log(f"XATO{' ' + ch['key'] if ch['dir'] else ''}: {type(e).__name__}: {e}")
                rc = 1
        return rc
    ch = next((c for c in chans if c["key"] == key), None) if key else next((c for c in chans if not c["dir"]), None)
    if ch is None:
        log("Kanal topilmadi:", key or "(asosiy)")
        return 2
    use_channel(ch)
    cfg = settings()
    if mode == "test":
        mode_test(cfg, pid, req)
    else:
        mode_health(cfg, req)
    return 0


if __name__ == "__main__":
    sys.exit(main())
