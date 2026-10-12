# -*- coding: utf-8 -*-
"""12–18-oktabr 2026 haftasi uchun 21 ta postni yaratadi (posts/*.json).
Barcha narx hisob-kitoblari shu yerda bajariladi — matnga qo'lda raqam yozilmaydi."""

import html
import json
import sys
import math
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "posts"
OUT.mkdir(parents=True, exist_ok=True)

# Kurs — Markaziy bank (cbu.uz), state/rate.json dan: GitHub Actions (rate.yml) 6 soatda bir yangilaydi.
_RATE_FILE = Path(__file__).resolve().parent.parent / "state" / "rate.json"
_rate = json.loads(_RATE_FILE.read_text(encoding="utf-8")) if _RATE_FILE.exists() else {"usd": 11772.95, "date": "03.10.2026"}
RATE = float(_rate["usd"])
RATE_DATE = _rate["date"]
RATE_TXT = "1 $ = " + f"{RATE:,.2f}".replace(",", " ").replace(".", ",") + f" so'm ({RATE_DATE}, Markaziy bank)"
SHIP_PER_KG = 9.50         # Meest AQSh, yuqori chegara (Spot.uz, 16.07.2026)
LIMIT = 200.0              # kuryer, oylik
DUTY = 0.30                # PQ-4508 3-band (2026-yil oxirigacha)

FOOT = "➖➖➖\n@Pochtam_shopo  "


def som(usd: float) -> int:
    return int(round(usd * RATE / 1000.0)) * 1000


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def usd(x: float) -> str:
    return f"${x:,.2f}".replace(".00", "") if x != int(x) or True else f"${int(x)}"


def money(x: float) -> str:
    s = f"{x:,.2f}"
    if s.endswith(".00"):
        s = s[:-3]
    return "$" + s


BHM = 440000               # 01.09.2026 dan
BKO_FEE = round(BHM * 0.25)  # 1 ta BKO uchun yig'im (VM 55-son, 31.01.2025)


def uzn(x, dec=2):
    """O'zbekcha son: 1 009; 302,70"""
    s = f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")
    return s[:-3] if dec and s.endswith(",00") else s


def r2(x: float) -> float:
    """Pul yaxlitlash: 157,125 → 157,13 (yarimdan yuqoriga)."""
    return math.floor(x * 100 + 0.5 + 1e-9) / 100


def duty_usd(value: float, kg: float, per_kg_min: bool = True) -> float:
    """Yagona bojxona to'lovi. value — bojxona qiymati (tovar + yetkazish), kg — posilka og'irligi.
    Normadan ortig'ining 30 % i, lekin 1 kg uchun kamida 3 $ (#boj postidagi usul).
    #obraz da minimal hisoblanmaydi (muallif ko'rsatmasi, 05.10.2026) — per_kg_min=False."""
    if value <= LIMIT:
        return 0.0
    pct = (value - LIMIT) * DUTY
    return r2(max(pct, kg * 3) if per_kg_min else pct)


def customs(goods: float, road: float, limit: float = None):
    """Muallif qoidasi (11.10.2026): tovar narxi normagacha bo'lsa — boj yo'q, yo'l harajati qo'shilmaydi.
    Tovar narxi normadan oshsa — BKO rasmiylashtiriladi: bojxona qiymati = tovar + yo'l,
    boj = (qiymat − norma) × 30 %. Minimal 3 $/kg qo'llanmaydi. Qaytaradi: (qiymat, boj $, BKO yig'imi so'm)."""
    limit = LIMIT if limit is None else limit
    if goods <= limit:
        return goods, 0.0, 0
    value = r2(goods + road)
    return value, r2((value - limit) * DUTY), BKO_FEE


def ship(weight_kg: float) -> float:
    """Kichik posilka: taxminan 1 kg tarifi; kattasi — og'irlik × tarif."""
    return round(max(1.0, math.ceil(weight_kg * 2) / 2) * SHIP_PER_KG, 2)


def vislen(s: str) -> int:
    t = html.unescape(re.sub(r"<[^>]+>", "", s))
    t = "\n".join(l for l in t.split("\n") if "{{APP_URL}}" not in l and "{{CONSULT_URL}}" not in l)
    return len(t.encode("utf-16-le")) // 2


# ------------------------------------------------------------------ prompt shablonlari
STYLE_TAIL = ("One geometric sans-serif font family throughout (Poppins / Montserrat style). Generous whitespace. "
              "Render every piece of text EXACTLY as written, spelled correctly, with straight apostrophes; "
              "numbers use spaces as thousand separators. No other text, no logos, no brand marks, no watermarks.")


def deal_prompt(store, country, badge, disc, title, pnew, pold, uz_label, uz_price, imp_label, imp_price,
                bottom_label, bottom_value, bottom_color="green (#059669)"):
    return f"""Create a vertical 4:5 e-commerce discount card for a Telegram channel. Flat, modern, premium. Pure white background with one large soft lavender (#EEEEFC) rounded shape covering the top ~20% of the frame.

Use the attached product photo as the hero image. Keep the product exactly as it is — do not redraw, restyle or alter it; only cut it out cleanly from its background.

LAYOUT, top to bottom:
1) Top row of pills: left — a solid indigo (#4F46E5) rounded pill with white bold uppercase text "{store}" (plain text, no logo); next to it — a white pill with a thin light-grey border and grey text "{country}"; right edge — a solid crimson (#E11D48) rounded pill with white bold uppercase text "{badge}".
2) A large white rounded rectangle (24px radius) with a soft realistic drop shadow, about 40% of the frame height. The product photo centered inside it, with a soft studio shadow beneath.
3) Overlapping the top-right corner of that rectangle: a solid crimson (#E11D48) circle with a thin white outer ring. Inside, in white: large bold "{disc}" and beneath it small uppercase "CHEGIRMA".
4) Headline in bold near-black (#11111B), large: "{title}"
5) Price row: very large bold indigo (#4F46E5) "{pnew}" and immediately to its right, smaller grey "{pold}" with a horizontal strikethrough line.
6) A light grey (#F6F6FB) rounded panel with a thin border containing:
   - small bold indigo uppercase label: "NARX SOLISHTIRUVI"
   - row: left grey text "{uz_label}", right bold near-black "{uz_price}"
   - row: left grey text "{imp_label}", right bold indigo "{imp_price}"
   - a thin divider line
   - row: left bold {bottom_color} uppercase "{bottom_label}", right large bold {bottom_color} "{bottom_value}"
7) Bottom, above a thin divider: left bold near-black "@Pochtam_shopo", right smaller grey "Chegirmalar - Kuryerlik - Bojxona"

{STYLE_TAIL}"""


def cover_prompt(tag, headline, illustration, sub=None, accent="crimson (#E11D48)"):
    sub_line = f'\n4) Under the headline, a smaller medium-grey line: "{sub}"' if sub else ""
    n = 5 if sub else 4
    return f"""Create a vertical 4:5 cover image for a Telegram channel post. Clean, modern 3D-minimal style, calm and trustworthy. Pure white background with one large soft lavender (#EEEEFC) rounded shape behind the upper half.

1) Top-left: a small solid indigo (#4F46E5) rounded pill with white bold text "{tag}".
2) Center: {illustration} Render it as a soft 3D clay illustration with matte surfaces in white and indigo (#4F46E5) with small touches of {accent}; soft studio lighting, gentle shadows, generous space around it.
3) Below the illustration: a large bold near-black (#11111B) headline, at most two lines: "{headline}"{sub_line}
{n}) Bottom, above a thin light divider: left bold near-black "@Pochtam_shopo".

{STYLE_TAIL}"""


def outfit_prompt(headline, items, palette, footer, person="a young woman, natural look, neat hair"):
    """#obraz rasmi: odam AYNAN shu 5 ta tovarni kiyib turibdi (BRIEF.md → #obraz).
    items — har bir tovar sahifadagidek aniq: rang, mato, bichim, tafsilotlar (masalan
    "camel-beige single-breasted wool-blend car coat, notch lapels, hip-length")."""
    lines = "\n".join(f"{i}) {t}" for i, t in enumerate(items, 1))
    return f"""Create a vertical 4:5 fashion lookbook photo for a Telegram channel. Photorealistic, editorial e-commerce style.

One person — {person} — standing full-body (head to shoes visible), relaxed natural pose, in front of a clean light warm-grey studio wall with a soft lavender (#EEEEFC) tint. The person is wearing EXACTLY these five items, all clearly visible, nothing else added:
{lines}

Each item must match its description precisely: same colour, material, cut and details. No extra clothing, jewellery or accessories beyond the list. If reference product photos are attached, copy the items from them exactly.

Next to each item place a small solid indigo (#4F46E5) circle with a white number — 1, 2, 3, 4, 5 — matching the list order, with a thin line pointing to the item.

Top-left: a small solid indigo (#4F46E5) rounded pill with white bold text "#obraz", and next to it a bold near-black headline: "{headline}".
Bottom strip, above a thin divider: left bold near-black "@Pochtam_shopo", right grey "{footer}".

Soft even studio lighting, realistic fabric texture, muted palette ({palette}). No price tags.
{STYLE_TAIL}"""


# ------------------------------------------------------------------ chegirma posti
def deal(pid, title, emoji, headline, hook, store, country, pnew, pold, weight, uz_store, uz_price, uz_note,
         url, note_lines, card_title, notes, sources, badge="CHEGIRMA", honest=False, mid_line=None):
    sh = ship(weight)
    value, duty, fee = customs(pnew, sh)
    total_usd = pnew + sh + duty
    total = som(total_usd) + fee
    save = int(round((uz_price - total) / 1000.0)) * 1000
    pct = round(save / uz_price * 100)
    disc = round((pold - pnew) / pold * 100)

    duty_line = (f"• Bojxona — <b>0 so'm</b> (tovar 200 $ normadan arzon)" if duty == 0
                 else f"• Yagona bojxona to'lovi — ({money(pnew)} + {money(sh)} − 200) × 30 % = <b>{money(duty)}</b>\n"
                      f"• 1 ta BKO uchun yig'im — <b>{fmt(fee)} so'm</b>")
    w_txt = f"~{str(weight).replace('.', ',')} kg"
    ship_txt = f"~{money(round(sh))}" + (f" ({w_txt})" if weight >= 1 else "")

    parts = [f"{emoji} <b>{headline}</b>", "", f"{hook} {money(pold)} → <b>{money(pnew)}</b> (−{disc}%).", ""]
    parts += ["💰 <b>Chetdan olib kelish</b>" + (" — boj bilan ham" if duty else ""),
              f"• Tovar — {money(pnew)}", f"• AQShdan yetkazish — {ship_txt}", duty_line,
              f"• <b>Jami ≈ {fmt(total)} so'm</b>", "",
              f"🇺🇿 <b>Toshkentda:</b> {uz_store} — {fmt(uz_price)} so'm" + (f" ({uz_note})" if uz_note else ""), ""]
    if save < 0:
        parts += [f"🔺 <b>Chetdan ≈ {fmt(-save)} so'm qimmat ({-pct}%)</b>", ""]
    elif honest:
        parts += [f"➖ <b>Farq atigi ≈ {fmt(save)} so'm ({pct}%)</b>", ""]
    else:
        parts += [f"✅ <b>Tejaysiz ≈ {fmt(save)} so'm ({pct}%)</b>", ""]
    if mid_line:
        parts += [mid_line, ""]
    parts += note_lines + [""]
    if url:
        parts.append(f'🔗 <a href="{url}">{store.split()[0]}da ko\'rish</a>')
    parts.append('📲 <a href="{{APP_URL}}">Bojni ilovada hisoblang</a>')
    parts += ["", f"<i>Kurs: {RATE_TXT}. Narxlar o'zgarishi mumkin.</i>", FOOT + "#narx"]
    caption = "\n".join(parts)

    prompt = deal_prompt(
        store=store.split()[0].upper(), country=country, badge=badge, disc=f"-{disc}%", title=card_title,
        pnew=money(pnew), pold=money(pold),
        uz_label=f"O'zbekistonda ({uz_store})", uz_price=f"{fmt(uz_price)} so'm",
        imp_label="Chetdan (tovar+yetkazish+boj)", imp_price=f"{fmt(total)} so'm",
        bottom_label="QIMMAT" if save < 0 else ("FARQ" if honest else "TEJAYSIZ"), bottom_value=f"{fmt(abs(save))} so'm",
        bottom_color="crimson (#E11D48)" if save < 0 else ("amber (#D97706)" if honest else "green (#059669)"))

    calc = (f"Hisob: tovar {money(pnew)} + yetkazish ~{money(sh)} + boj {money(duty)} = {money(round(total_usd, 2))} "
            f"× {RATE}" + (f" + BKO {fmt(fee)}" if fee else "") + f" = {fmt(total)} so'm. Tejash: {fmt(uz_price)} − {fmt(total)} = {fmt(save)} so'm ({pct}%).")
    return dict(id=pid, rubric="#narx", title=title, caption=caption, prompt=prompt, product_url=url,
                notes=(notes + "\n" if notes else "") + calc, sources=sources)


# ------------------------------------------------------------------ postlar
posts = []

def add(pid, **kw):
    kw["id"] = pid
    kw["scheduled_at"] = f"{pid[:10]}T{pid[11:13]}:{pid[13:15]}:00+05:00"
    kw.setdefault("status", "draft")
    kw.setdefault("sources", [])
    kw.setdefault("notes", "")
    kw.setdefault("product_url", None)
    posts.append(kw)


LEX_PF174 = {"label": "PF-174, 27.08.2026 (lex.uz)", "url": "https://lex.uz/uz/docs/-8444993"}
LEX_PQ4508 = {"label": "PQ-4508, 07.11.2019 — 3-band, 2019-yil tahriri: 30 %, 3 $/kg (lex.uz)",
              "url": "https://lex.uz/uz/docs/-4585742?ONDATE=07.11.2019%2000"}
LEX_VM244 = {"label": "VM 244-son qarori, 19.04.2025 (lex.uz)", "url": "https://lex.uz/uz/docs/-7484114"}
SPOT_RATE = {"label": f"Markaziy bank kursi, {RATE_DATE} (cbu.uz)", "url": "https://cbu.uz/uz/arkhiv-kursov-valyut/"}
SPOT_COURIER = {"label": "Yetkazib beruvchilar narxi, 16.07.2026 (spot.uz)", "url": "https://www.spot.uz/oz/2026/07/16/delivery"}

PRICE_DATE = "11.10.2026"   # narxlar qidirilgan sana
LEX_VM191 = {"label": "VM 191-son, 08.06.2016 — Nizom 5-band (lex.uz da qidiring)", "url": "https://lex.uz/"}
LEX_VM244_A1 = {"label": "VM 244-son, 19.04.2025 — 1-ilova (lex.uz)", "url": "https://lex.uz/uz/docs/-7484114"}
LEX_VM55 = {"label": "VM 55-son qarori, 31.01.2025 — bojxona yig'imlari stavkalari (lex.uz)", "url": "https://lex.uz/uz/docs/-7357270"}
TIPIK = "<i>Holat bojxona amaliyotidagi tipik vaziyatlar asosida tuzilgan.</i>"
NUM = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

# ============ DUSHANBA 12-oktabr ============
# #boj — tovar normadan biroz oshdi: BKO rasmiylashtiriladi, yo'l qo'shiladi, yig'im bojdan katta (muallif qoidasi 11.10.2026)
B1_GOODS, B1_KG = 205.0, 2.0
b1_ship = ship(B1_KG)
b1_value, b1_duty, b1_fee = customs(B1_GOODS, b1_ship)
b1_over = r2(b1_value - LIMIT)
b1_duty_som = round(b1_duty * RATE)
B1_CUT = 15.0
b1_goods2 = r2(B1_GOODS - B1_CUT)
add("2026-10-12-0900", rubric="#boj", title="Normadan biroz oshish — yig'im bojdan qimmat",
    caption=f"""💸 <b>Tovar normadan {uzn(B1_GOODS - LIMIT)} $ oshdi — {fmt(b1_duty_som + b1_fee)} so'm to'laysiz</b>

Misol: kuryer orqali kiyim-kechak — tovarlar <b>{uzn(B1_GOODS)} $</b>, {uzn(B1_KG)} kg, yo'l harajati {uzn(b1_ship)} $.

Tovar narxi 200 $ dan oshgani uchun BKO rasmiylashtiriladi va bojxona qiymatiga <b>yo'l harajati ham qo'shiladi</b>:

1️⃣ <b>Bojxona qiymati:</b> {uzn(B1_GOODS)} + {uzn(b1_ship)} = <b>{uzn(b1_value)} $</b>
2️⃣ <b>Normadan ortig'i:</b> {uzn(b1_value)} − 200 = <b>{uzn(b1_over)} $</b>
3️⃣ <b>Boj 30 %:</b> {uzn(b1_over)} × 30 % = <b>{uzn(b1_duty)} $</b> ≈ {fmt(b1_duty_som)} so'm
4️⃣ <b>1 ta BKO uchun yig'im:</b> BHM ning 25 % = <b>{fmt(b1_fee)} so'm</b>

💰 <b>Jami: {fmt(b1_duty_som + b1_fee)} so'm</b>

✂️ <b>Yechim:</b> {uzn(B1_CUT)} $ lik bitta mayda tovarni keyingi oyga qoldiring — tovarlar {uzn(b1_goods2)} $ bo'ladi: norma ichida, yo'l hisobga olinmaydi, boj ham, yig'im ham yo'q.

📅 2027-yil 1-iyundan: boj yig'imdan kam bo'lsa, yig'im undirilmaydi (PF-174, 3-band «g»).

📄 Asos: VM 244-son; PQ-4508, 3-band; VM 55-son, 31.01.2025; PF-174 — lex.uz
📲 <a href="{{{{APP_URL}}}}">Normangizni ilovada hisoblang</a>

""" + FOOT + "#boj",
    prompt=cover_prompt("#boj", "Normadan biroz oshdingizmi?",
        "a cardboard parcel on a balance scale, tipping slightly past a thin indigo line marked 200 $; next to it a small coin and a much bigger stack of coins with a receipt slip, showing the fee outweighs the duty.",
        sub="Yig'im bojdan qimmat bo'lishi mumkin", accent="amber (#F59E0B)"),
    sources=[LEX_VM244, LEX_PQ4508, LEX_VM55, LEX_PF174, SPOT_COURIER, SPOT_RATE],
    notes=f"Muallif qoidasi (11.10.2026): tovar 200 $ gacha — boj yo'q, yo'l qo'shilmaydi; oshsa — BKO, bojxona qiymati = tovar + yo'l. Minimal 3 $/kg qo'llanmadi. "
          f"Hisob: ({B1_GOODS} + {b1_ship} − 200) × 30 % = {b1_duty} $ × {RATE} = {b1_duty_som} so'm; + BKO {b1_fee}. BKO stavkasi va BHM lex.uz da qayta tekshirilmagan.")

# ============ SESHANBA 13-oktabr ============
add("2026-10-13-0900", rubric="#taqiq", title="Dori va vitamin: posilkada qancha mumkin",
    caption="""💊 <b>Dori va vitamin buyurtma qilyapsizmi? Miqdorga qarang</b>

Bunday posilkalarda <b>pul emas, dona</b> hisoblanadi. Norma oshsa — posilka to'xtaydi.

💊 <b>Dori vositalari</b>
• <b>10 xil nomgacha</b>
• har bir nomdan <b>5 qadoqgacha</b>

🌿 <b>BAD (vitamin, omega-3, kollagen va h.k.)</b>
• <b>10 xil nomgacha</b>, jami <b>3 kg gacha</b>
• har bir nomdan <b>faqat 1 qadoq</b>

⚠️ <b>Ko'p uchraydigan xato:</b> iHerb yoki Amazon'dagi «2 ta oling — arzonroq» aksiyasi. BAD uchun ikkinchi qadoq normadan tashqarida qoladi.

✅ <b>Buyurtmadan oldin</b>
1. Savatdagi har bir nomni va qadoqlar sonini sanang
2. Dori va BAD ni alohida hisoblang — normalari har xil
3. Shubha bo'lsa — buyurtmani ikki oyga bo'ling

📄 Asos: VM 191-son, 08.06.2016, Nizom 5-band; VM 244-son, 19.04.2025, 1-ilova — lex.uz
📲 <a href="{{APP_URL}}">Savatingizni ilovada tekshiring</a>

""" + FOOT + "#taqiq",
    prompt=cover_prompt("#taqiq", "Dori va vitamin: qancha mumkin?",
        "an open matte cardboard parcel with several small medicine boxes and supplement bottles neatly lined up beside it; one extra identical bottle stands apart with a small amber warning tag, and a tiny indigo counter badge shows numbers.",
        sub="Pul emas, dona hisoblanadi", accent="emerald green (#059669)"),
    sources=[LEX_VM191, LEX_VM244_A1],
    notes="VM 191 uchun lex.uz dagi aniq havolani qo'shing (Claude muhitidan lex.uz ochilmadi). Normalar BRIEF.md dagi tekshirilgan faktlardan: dori — 10 nom, har biridan 5 qadoq (VM 191, Nizom 5-band); BAD — 10 nom, 3 kg, har nomdan 1 qadoq (VM 244, 1-ilova). "
          "«Buyurtmani ikki oyga bo'ling» maslahati — BAD normasi oyga yoki jo'natmaga bog'liqligini tekshiring.")

KIDS_SIZES = [("110–116", "4–6 yosh"), ("122–128", "6–8 yosh"), ("134–140", "8–10 yosh"), ("146–152", "10–12 yosh")]
add("2026-10-13-1400", rubric="#olcham", title="Bolalar kiyimi: yosh emas, bo'y",
    caption="""📏 <b>Bolalar kiyimi: yoshga emas, bo'yga qarang</b>

H&amp;M va Uniqlo bolalar o'lchamini <b>santimetrda — bo'y bo'yicha</b> yozadi. «7 yosh» degan yorliq hammaga mos kelmaydi: bir sinfdagi bolalar bo'yi 15–20 sm farq qiladi.

📐 <b>Qanday o'lchash kerak</b>
1. Bolani poyabzalsiz devorga yondashtirib turg'izing
2. Boshi ustiga kitob qo'yib, devorga belgi qo'ying
3. Poldan belgigacha — bu <b>bo'y (sm)</b>

👕 <b>H&amp;M bolalar o'lchami (bo'y, sm)</b>
""" + "\n".join(f"• {h} sm — taxminan {y}" for h, y in KIDS_SIZES) + """
Uniqlo'da: 110, 120, 130, 140, 150 — bu ham bo'y (sm).

💡 <b>Maslahat</b>
• Bo'yi ikki o'lcham orasida bo'lsa — kattasini oling
• Kurtka va qishki kiyimga 5–6 sm «o'sish zaxirasi» qo'shing
• Gap / Old Navy XS–L harflarini ishlatadi — jadvalidan sm ustunini toping

⚠️ Jadval taxminiy — har doim do'konning o'z o'lcham jadvalini tekshiring.

📲 <a href="{{APP_URL}}">O'lcham qo'llanmalari — ilovada</a>

""" + FOOT + "#olcham",
    prompt=cover_prompt("#olcham", "Bolalar kiyimi: yosh emas, bo'y",
        "a child's height chart drawn on a wall like a ruler with centimetre marks (110, 120, 130, 140), a small folded kids' jacket and a tiny sneaker at its base, and a book resting flat on top of an imaginary head line.",
        sub="O'lchamni santimetrda tanlang", accent="sky blue (#38BDF8)"),
    sources=[],
    notes="O'lcham va yosh mosligi taxminiy (H&M bolalar o'lchamlari bo'y bo'yicha). H&M/Uniqlo sahifalari Claude muhitidan ochilmadi — jadvalni do'kon saytida tekshiring.")

# ============ CHORSHANBA 14-oktabr ============
# #savol — yo'l harajati qachon hisoblanadi (muallif qoidasi 11.10.2026)
S1_A, S1_B, S1_KG = 185.0, 215.0, 2.0
s1_ship = ship(S1_KG)
s1_val_b, s1_duty, s1_fee = customs(S1_B, s1_ship)
s1_duty_som = round(s1_duty * RATE)
add("2026-10-14-0900", rubric="#savol", title="Yo'l harajati normaga qo'shiladimi?",
    caption=f"""❓ <b>Savol: «Yetkazish narxi ham 200 $ normaga qo'shiladimi?»</b>

<b>Tovar 200 $ gacha bo'lsa — yo'q.</b> Norma faqat tovar narxi bo'yicha tekshiriladi.
<b>Tovar 200 $ dan oshsa</b> — BKO rasmiylashtiriladi va bojxona qiymatiga yo'l harajati ham qo'shiladi.

🧮 <b>Ikki misol</b> (kuryer, {uzn(S1_KG)} kg, yo'l {uzn(s1_ship)} $)
• Kurtka <b>{uzn(S1_A)} $</b> → norma ichida, yo'l hisobga olinmaydi, <b>boj yo'q</b> ✅
• Kurtka <b>{uzn(S1_B)} $</b> → normadan oshdi ❌
  Bojxona qiymati: {uzn(S1_B)} + {uzn(s1_ship)} = {uzn(s1_val_b)} $
  Boj: ({uzn(s1_val_b)} − 200) × 30 % = {uzn(s1_duty)} $ ≈ {fmt(s1_duty_som)} so'm
  1 ta BKO uchun yig'im — {fmt(s1_fee)} so'm
  <b>Jami: {fmt(s1_duty_som + s1_fee)} so'm</b>

💡 <b>Qoida:</b> tovarlar 200 $ dan oshmasin — shunda yo'l harajati ham, boj ham, yig'im ham yo'q.

✏️ <b>Tuzatish:</b> <a href="{{{{LINK:2026-10-07-1400}}}}">7-oktabr</a> va <a href="{{{{LINK:2026-10-10-1400}}}}">10-oktabr</a> obrazlarida yo'l harajati normaga qo'shib hisoblangan edi — bu xato. Ikkalasida ham tovarlar 200 $ dan arzon: <b>boj ham, yig'im ham yo'q</b>.

📄 Asos: VM 244-son; PQ-4508, 3-band; VM 55-son — lex.uz
📲 <a href="{{{{APP_URL}}}}">Normangizni ilovada hisoblang</a>

""" + FOOT + "#savol",
    prompt=cover_prompt("#savol", "Yo'l harajati normaga qo'shiladimi?",
        "two cardboard parcels with price tags: the left tag reads 185 $ next to a green check mark and a crossed-out small delivery-truck tag; the right tag reads 215 $ with a delivery-truck tag attached and a small receipt, beside a thin indigo line marked 200 $.",
        sub="200 $ gacha — faqat tovar narxi", accent="sky blue (#38BDF8)"),
    sources=[LEX_VM244, LEX_PQ4508, LEX_VM55, SPOT_COURIER, SPOT_RATE],
    notes="Muallif qoidasi (11.10.2026): tovar 200 $ gacha — boj yo'q, yo'l qo'shilmaydi; oshsa — BKO, bojxona qiymati = tovar + yo'l. Minimal 3 $/kg qo'llanmadi. "
          f"Yo'l: {S1_KG} kg × 9,50 $ = {s1_ship} $. Hisob: ({S1_B} + {s1_ship} − 200) × 30 % = {s1_duty} $.")

# ============ PAYSHANBA 15-oktabr ============
K_ITEMS = [("Shokolad va pechenye to'plami", 34.0), ("Pishloq va kraker", 21.0), ("Bir shisha qizil sharob", 24.0)]
k_total = r2(sum(p for _, p in K_ITEMS))
add("2026-10-15-0900", rubric="#keys", title="Keys: sovg'a savatchasidagi sharob",
    caption="""🔍 <b>Keys: sovg'a savatchasi posilkani to'xtatdi</b>

📦 <b>Nima keldi:</b> kuryer orqali Amazon'dan tayyor «gourmet» sovg'a savatchasi — <b>""" + uzn(k_total) + """ $</b>:
""" + "\n".join(f"• {n}" for n, _ in K_ITEMS) + """

Summa normadan ancha kam, lekin posilka to'xtadi.

⛔ <b>Muammo:</b> savatchada <b>sharob</b> bor edi. Alkogol va tamaki mahsulotlarini pochta va kuryer orqali olib kirish <b>taqiqlangan</b> — narxi ahamiyatsiz. Xaridor tavsifdagi «wine» so'zini ko'rmagan.

🛠 <b>Qanday hal qilindi:</b> sharob chiqarilmadi, qolgan tovarlar bo'yicha qaror kutildi — jo'natma bir necha kun kechikdi.

✅ <b>Xulosa:</b> sovg'a to'plamlari tarkibini oxirigacha o'qing. «wine», «champagne», «liqueur», «cigar» bo'lsa — olmang.

📄 Asos: VM 244-son, 1-ilova «a» izohi (VM 154-son, 09.04.2026 tahriri) — lex.uz

Posilkangiz to'xtab qoldimi? Vaziyatingizni ko'rib chiqib, yo'l ko'rsataman 👇
💬 <a href="{{CONSULT_URL}}">Maslahat olish</a>

""" + TIPIK + "\n" + FOOT + "#keys",
    prompt=cover_prompt("#keys", "Sovg'a savatchasi posilkani to'xtatdi",
        "a wicker gift basket with chocolates, crackers and cheese on a customs inspection counter; a wine bottle lifted out of the basket stands beside it with a bold crimson prohibition circle, and a large indigo magnifying glass hovers over the basket label.",
        sub="Pochta va kuryerda alkogol taqiqlangan", accent="crimson (#E11D48)"),
    sources=[{"label": "VM 244-son, 1-ilova «a» izohi (VM 154-son, 09.04.2026 tahriri) (lex.uz)", "url": "https://lex.uz/uz/docs/-7484114"}],
    notes="Keysni Claude tuzdi (tipik holat, real voqea emas). Narxlar misol uchun. "
          "Tekshiring: «Qanday hal qilindi» qatoridagi amaliyot (sharob chiqarilmadi, qolgan tovarlar bo'yicha qaror) tajribangizga mos kelsinmi — kerak bo'lsa tahrir qiling.")

V_BOX = (50, 40, 25)
v_real, V_DIV = 1.2, 5000
v_vol = round(V_BOX[0] * V_BOX[1] * V_BOX[2] / V_DIV, 1)
V_BOX2 = (40, 30, 12)
v_vol2 = round(V_BOX2[0] * V_BOX2[1] * V_BOX2[2] / V_DIV, 1)
add("2026-10-15-1400", rubric="#kuryer", title="Hajmiy og'irlik — yengil posilka nega qimmat",
    caption=f"""📦 <b>Kurtka 1 kg chiqdi, kuryer {uzn(v_vol)} kg uchun pul so'radi. Nega?</b>

Bu — <b>hajmiy og'irlik</b>. Katta, lekin yengil qutida kuryer haqiqiy og'irlik emas, quti hajmi bo'yicha hisoblaydi.

🧮 <b>Formula</b> (ko'p xizmatlarda):
uzunlik × kenglik × balandlik (sm) ÷ {fmt(V_DIV)}

<b>Misol:</b> puxovik {fmt(V_BOX[0])}×{fmt(V_BOX[1])}×{fmt(V_BOX[2])} sm qutida
• Haqiqiy og'irlik — {uzn(v_real, 1)} kg
• Hajmiy — {fmt(V_BOX[0])}×{fmt(V_BOX[1])}×{fmt(V_BOX[2])} ÷ {fmt(V_DIV)} = <b>{uzn(v_vol)} kg</b>
• Kuryer kattasini oladi → <b>{uzn(v_vol)} kg</b> uchun to'laysiz

✅ <b>Qanday tejash mumkin</b>
1. Kuryerdan <b>qayta qadoqlash</b>ni so'rang — {fmt(V_BOX2[0])}×{fmt(V_BOX2[1])}×{fmt(V_BOX2[2])} sm paketda hajmiy og'irlik {uzn(v_vol2, 1)} kg
2. Bir nechta buyurtmani bitta qutiga birlashtiring (konsolidatsiya)
3. Hajmiy og'irlik qoidasini va bo'luvchini (5000 yoki 6000) xizmatning o'zidan so'rang

📲 <a href="{{{{APP_URL}}}}">Yetkazishni ilovada hisoblang</a>

""" + FOOT + "#kuryer",
    prompt=cover_prompt("#kuryer", "Hajmiy og'irlik nima?",
        "a large mostly empty cardboard box with a small folded puffer jacket inside, a tape measure stretched along its edges, and next to it the same jacket packed tightly in a small flat poly mailer.",
        sub="Katta quti — katta to'lov", accent="amber (#F59E0B)"),
    sources=[],
    notes="Hajmiy og'irlik — xalqaro kuryer xizmatlarida keng qo'llanadigan amaliyot; bo'luvchi (5000/6000) va qoidani har bir kuryer xizmati o'zi belgilaydi. Raqamlar misol uchun.")

# ============ SHANBA 17-oktabr ============
add("2026-10-17-0900", rubric="#savol", title="Oy oxiridagi buyurtma qaysi oyga yoziladi",
    caption="""❓ <b>Savol: «Buyurtmani oktabr oxirida berdim. Qaysi oy normasiga yoziladi?»</b>

Buyurtma sanasi ham, posilka kelgan kun ham emas — <b>bojxonada rasmiylashtirilgan sana</b> hisoblanadi.

📅 <b>Misol</b> (kuryer, norma — oyiga 200 $)
• 10-oktabr: 1-posilka rasmiylashtirildi — 150 $
• 28-oktabr: 2-buyurtma berildi — 120 $
• 3-noyabr: 2-posilka rasmiylashtirildi → <b>noyabr</b> normasiga yoziladi

Natija: oktabrda 150 $, noyabrda 120 $ — ikkalasi ham norma ichida, <b>boj yo'q</b> ✅

Agar 2-posilka 30-oktabrda rasmiylashtirilganda edi — oktabr jami 270 $, 70 $ normadan oshardi ❌

💡 <b>Maslahat</b>
• Oy oxirida xarid qilsangiz — trek-raqam orqali posilka qachon rasmiylashtirilishini kuzating
• Katta xaridni oy boshiga rejalang — oyning normasi to'liq turadi

📄 Asos: VM 244-son, 19.04.2025 — lex.uz
📲 <a href="{{APP_URL}}">Oylik normangizni ilovada kuzating</a>

""" + FOOT + "#savol",
    prompt=cover_prompt("#savol", "Qaysi oy normasiga yoziladi?",
        "two wall-calendar pages, October and November, side by side; a cardboard parcel with a small indigo stamp sits on the November page, and a curved arrow shows it moving from late October to early November.",
        sub="Rasmiylashtirilgan sana hisoblanadi", accent="sky blue (#38BDF8)"),
    sources=[LEX_VM244],
    notes="Norma kalendar oy bo'yicha, rasmiylashtirilgan sana bo'yicha — muallif tasdiqlagan (BRIEF.md). Summalar — tovar narxi (200 $ gacha yo'l qo'shilmaydi, muallif qoidasi).")

# ============ YAKSHANBA 18-oktabr ============
add("2026-10-18-1400", rubric="#firibgar", title="Soxta do'kon saytlari",
    caption="""⚠️ <b>«Nike −80 %» — soxta do'kon saytini qanday tanish mumkin</b>

Instagram va Telegram reklamalarida mashhur brendlarning «yopilish aksiyasi» ko'p uchraydi. Pul to'lanadi — tovar kelmaydi.

🚩 <b>Belgilari</b>
1️⃣ <b>Manzil g'alati:</b> brend nomi + «sale», «outlet», «-uz» va .shop / .store kabi qo'shimchalar — rasmiy sayt emas
2️⃣ <b>Narx haddan tashqari past:</b> yangi model 70–90 % arzon
3️⃣ <b>To'lov — shaxsiy kartaga o'tkazma</b> yoki faqat kripto
4️⃣ <b>Aloqa yo'q:</b> manzil, telefon, qaytarish shartlari ko'rsatilmagan
5️⃣ <b>Shoshiltirish:</b> «faqat bugun», «5 dona qoldi» taymerlari

✅ <b>O'zingizni himoya qiling</b>
• Do'konga reklamadan emas, <b>manzilni o'zingiz yozib</b> kiring yoki rasmiy ilova orqali
• Saytning yoshi va sharhlarini qidiruvda tekshiring
• Kartaga o'tkazma emas — do'kon saytidagi rasmiy to'lov
• Ishonchingiz komil bo'lmasa — xarid qilmang

Shunday saytga duch kelganmisiz? Izohda manzilini yozing — boshqalarni ogohlantiramiz 👇

""" + FOOT + "#firibgar",
    prompt=cover_prompt("#firibgar", "Soxta do'kon saytini qanday tanish mumkin?",
        "a laptop showing a flashy fake online shop page with a huge -80% badge and a countdown timer, a small fishing hook dangling from the top of the screen, and a bold amber warning triangle in front of the laptop.",
        sub="5 ta belgi", accent="amber (#F59E0B)"),
    sources=[],
    notes="Umumiy xavfsizlik maslahatlari; statistik raqam yoki huquqiy norma keltirilmagan. Real sayt nomlari keltirilmagan.")

# ============ JUMA 16-oktabr — #boj: pochta va kuryer normasi ============
POST_LIMIT = 100.0
B2_GOODS, B2_ROAD = 150.0, 10.0
b2_val, b2_duty, b2_fee = customs(B2_GOODS, B2_ROAD, limit=POST_LIMIT)
b2_post_over = r2(b2_val - POST_LIMIT)
b2_post_som = round(b2_duty * RATE)
_, b2_kur_duty, _ = customs(B2_GOODS, B2_ROAD)
assert b2_kur_duty == 0
add("2026-10-16-0900", rubric="#boj", title="Pochta yoki kuryer: bir xil buyurtma — boshqa boj",
    caption=f"""📮 <b>Bir xil buyurtma: pochtada {fmt(b2_post_som + b2_fee)} so'm, kuryerda — 0</b>

Bojsiz norma kanalga qarab ikki xil:
• <b>Pochta</b> orqali — oyiga <b>{uzn(POST_LIMIT)} $</b>
• <b>Kuryer</b> orqali — oyiga <b>{uzn(LIMIT)} $</b>

🧮 <b>Misol:</b> tovarlar <b>{uzn(B2_GOODS)} $</b>, yo'l harajati {uzn(B2_ROAD)} $

📮 <b>Pochta orqali</b> — tovar 100 $ dan oshdi, BKO rasmiylashtiriladi
• Bojxona qiymati (tovar + yo'l): {uzn(B2_GOODS)} + {uzn(B2_ROAD)} = {uzn(b2_val)} $
• Boj: ({uzn(b2_val)} − {uzn(POST_LIMIT)}) × 30 % = <b>{uzn(b2_duty)} $</b> ≈ {fmt(b2_post_som)} so'm
• 1 ta BKO uchun yig'im — <b>{fmt(b2_fee)} so'm</b>
• Jami: <b>{fmt(b2_post_som + b2_fee)} so'm</b>

🚚 <b>Kuryer orqali</b>
• Tovar {uzn(B2_GOODS)} $ < {uzn(LIMIT)} $ — norma ichida, yo'l hisobga olinmaydi, <b>boj yo'q</b> ✅

💡 <b>Qoida:</b> tovarlar 100 $ dan qimmat bo'lsa — yetkazish usulini oldindan tanlang. Do'kon o'zi pochta bilan jo'natsa, norma 100 $ ekanini unutmang.

📄 Asos: VM 244-son, 19.04.2025; PQ-4508, 3-band; VM 55-son — lex.uz
📲 <a href="{{{{APP_URL}}}}">Ikkala variantni ilovada solishtiring</a>

""" + FOOT + "#boj",
    prompt=cover_prompt("#boj", "Pochta yoki kuryer?",
        "two identical cardboard parcels side by side: the left one on a classic postal mailbox with a small amber coin stack beside it, the right one on a small courier delivery van with a green check mark badge.",
        sub="Norma: 100 $ va 200 $", accent="emerald green (#059669)"),
    sources=[LEX_VM244, LEX_PQ4508, LEX_VM55, SPOT_RATE],
    notes="Normalar: pochta 100 $/oy, kuryer 200 $/oy (VM 244, BRIEF.md). Muallif qoidasi: tovar normadan oshsa — BKO, bojxona qiymati = tovar + yo'l. Minimal 3 $/kg qo'llanmadi. "
          f"Hisob: ({B2_GOODS} + {B2_ROAD} − 100) × 30 % = {b2_duty} $ × {RATE} = {b2_post_som} so'm + BKO {b2_fee}.")

# ============ #obraz — aniq tovarlar (BRIEF.md → #obraz) ============
# (do'kon, nom uz, rang uz, narx, eski narx, url, og'irlik kg, rasm uchun tavsif)
def obraz(pid, title, emoji, headline, sub, items, palette, person, cut_word, notes_extra=""):
    total = r2(sum(x[3] for x in items))
    full = r2(sum(x[4] or x[3] for x in items))
    kg = round(sum(x[6] for x in items), 2)
    sh = ship(kg)
    value, duty, fee = customs(total, sh)
    stores = " + ".join(dict.fromkeys(x[0] for x in items)).replace("&", "&amp;")
    lines = "\n".join(f'{NUM[i]} <a href="{x[5]}">{x[1]}</a>, {x[2]} — <b>{usd(x[3])}</b>' + (f" <s>{usd(x[4])}</s>" if x[4] else "")
                      for i, x in enumerate(items))
    duty_line = (f"• Boj — (tovar + yo'l {usd(value)} − 200) × 30 % = {usd(duty)} + BKO yig'imi {fmt(fee)} so'm\n" if duty
                 else "• Boj — yo'q (tovarlar 200 $ normaga sig'adi)\n")
    caption = (f"{emoji} <b>Tayyor obraz: {headline}</b>\n<i>{sub} · 5 element · {stores} (AQSh)</i>\n\n{lines}\n\n"
               f"🛒 <b>Tovarlar: {usd(total)}</b>" + (f" (aksiyasiz {usd(full)})" if full != total else "") +
               (" — normadan oshadi\n\n" if duty else " — 200 $ normaga sig'adi, boj yo'q\n\n") +
               f"📦 <b>Toshkentgacha</b>\n• Yetkazish — ~{usd(sh)} (≈{uzn(kg, 1)} kg)\n{duty_line}• Toshkent bo'ylab — ~$3\n"
               f"• <b>Jami ≈ {fmt(som(total + sh + duty + 3) + fee)} so'm</b>\n\n"
               f"⚠️ Aksiya tugasa summa oshadi — to'lashdan oldin savatni tekshiring.\n\n"
               f"💡 H&amp;M AQSh sayti faqat AQSh ichiga yetkazadi — kuryerning AQShdagi ombor manzilidan foydalaning.\n\n"
               f"<i>Narxlar {PRICE_DATE} holatiga.</i>\n" + FOOT + "#obraz")
    add(pid, rubric="#obraz", title=title, caption=caption,
        prompt=outfit_prompt(cut_word, [x[7] for x in items], palette, f"5 element · {usd(total)}", person=person),
        product_url=items[0][5],
        sources=[{"label": f"{x[0]} US — {x[1]}", "url": x[5]} for x in items] + [SPOT_COURIER, SPOT_RATE],
        notes="TASDIQLASHDAN OLDIN: 5 ta havolani brauzerda oching — narx, rang va o'lcham bor-yo'qligini tekshiring "
              "(H&M sayti Claude muhitidan ochilmadi, narxlar qidiruv natijalaridan). " + notes_extra +
              " RASM: ChatGPT'ga 5 ta tovar suratini (do'kon sahifasidan) ham biriktiring — kiyimlar aynan o'xshash chiqadi. "
              f"Og'irliklar taxminiy (≈{kg} kg). Tovarlar {total} $ — " + ("normadan oshadi: bojxona qiymati = tovar + yo'l = " + str(value) + " $." if duty else "norma ichida, yo'l qo'shilmaydi."))


OUTFIT_W = [
    ("H&M", "Qisqa trench palto", "bej", 44.99, None, "https://www2.hm.com/en_us/productpage.1259401001.html", 0.75,
     "a hip-length beige double-breasted trench coat in unlined cotton twill with notched lapels, worn open over the sweater"),
    ("H&M", "Trikotaj sviter", "krem", 24.99, None, "https://www2.hm.com/en_us/productpage.0983240042.html", 0.55,
     "a loose-fit cream knit sweater in a soft wool-blend yarn with a round neckline, long sleeves and ribbed cuffs and hem"),
    ("H&M", "Keng jinsi (ultra high)", "ko'k", 34.99, None, "https://www2.hm.com/en_us/productpage.1308275008.html", 0.65,
     "mid-blue rigid cotton denim jeans with an extra-high waist and wide straight legs falling to the top of the foot"),
    ("H&M", "Loafer", "to'q jigarrang", 29.99, 39.99, "https://www2.hm.com/en_us/productpage.1293532001.html", 0.75,
     "dark brown flat loafers with a soft suede-like finish, moccasin seam, penny-keeper strap and a low heel"),
    ("H&M", "Katta sharf", "to'q jigarrang", 17.99, None, "https://www2.hm.com/en_us/productpage.1244826007.html", 0.30,
     "a large cozy dark brown scarf in soft lightly brushed woven fabric with frayed edges, loosely wrapped around the neck"),
]
OUTFIT_KID = [
    ("H&M", "Suv o'tkazmaydigan kurtka", "xaki yashil", 29.99, None, "https://www2.hm.com/en_us/productpage.1232402001.html", 0.60,
     "a muted khaki-green water-repellent quilted puffer jacket with a zip front, hood and flap patch pockets"),
    ("H&M", "Vafli paxta svitshot", "kulrang melanj", 19.99, None, "https://www2.hm.com/en_us/productpage.1237528001.html", 0.30,
     "a regular-fit grey melange long-sleeve sweatshirt in waffle-textured cotton with a ribbed round neckline, cuffs and hem"),
    ("H&M", "Paxta kargo shim", "to'q bej", 32.99, None, "https://www2.hm.com/en_us/productpage.1073178002.html", 0.40,
     "relaxed-fit dark beige cotton cargo pants with straight legs, an elasticated waistband and flap pockets on the legs"),
    ("H&M", "Krossovka", "oq / bej", 13.99, None, "https://www2.hm.com/en_us/productpage.0982528013.html", 0.50,
     "low-profile white-and-beige faux suede kids' sneakers with a hook-and-loop strap and rubber soles"),
    ("H&M", "Jun aralash shapka", "bej", 11.99, 17.99, "https://www2.hm.com/en_us/productpage.1232240002.html", 0.10,
     "a beige rib-knit wool beanie with a fold-over cuff"),
]

# ============ CHORSHANBA 14-oktabr ============
obraz("2026-10-14-1400", "Ayollar: kuzgi dam olish obrazi", "🧥", "kuzgi dam olish kuni uchun", "Ayollar uchun",
      OUTFIT_W, "beige, cream, denim blue, dark brown", "a young woman in her late twenties, natural look, neat shoulder-length hair",
      "Kuzgi dam olish kuni",
      "Loafer — aksiya narxida ($29.99, odatda $39.99); trench palto ba'zi mamlakatlarda sotuvdan chiqqan — AQShda borligini tekshiring.")

# ============ SHANBA 17-oktabr ============
obraz("2026-10-17-1400", "Bolalar: kuzgi maktab obrazi", "🎒", "maktab uchun kuzgi kiyim", "Bola uchun, 6–8 yosh",
      OUTFIT_KID, "khaki green, grey, beige, white", "a cheerful boy about seven years old, short hair, natural smile",
      "Kuzgi maktab obrazi",
      "Kurtka va krossovkada 6–8 yosh (122–128 sm) o'lchami borligini tekshiring; shapka aksiya narxida ($11.99, odatda $17.99). "
      "O'lcham tanlash — seshanba #olcham postida.")

# ============ DUSHANBA 12-oktabr — #dokon ============
add("2026-10-12-1400", rubric="#dokon", title="AliExpress — O'zbekistonga to'g'ridan-to'g'ri",
    caption="""🛍 <b>AliExpress: to'g'ridan-to'g'ri, so'mda to'lab</b>

Xitoy marketpleysi O'zbekistonga <b>to'g'ridan-to'g'ri</b> yetkazadi — AQShdagi kabi ombor manzili kerak emas.

✅ <b>Qulayliklari</b>
• <b>Uzcard va Humo</b> bilan to'lov, summa so'mda (2023-yil dekabridan)
• Xitoy — O'zbekiston to'g'ridan-to'g'ri reyslari: o'rtacha <b>~14 kun</b>
• <b>Uzum Market topshirish punktlari</b>: buyurtmada xaritadan punkt tanlanadi, SMS-kod bilan olinadi
• Xaridor himoyasi: tovar kelmasa yoki tavsifga mos bo'lmasa — buyurtma sahifasidan nizo (dispute) ochiladi

⚠️ <b>E'tibor bering</b>
• Punktga yetkazish faqat «Pickup point» belgisi bor sotuvchilarda
• Tovarni tekshirmasdan <b>«Qabul qildim»</b> tugmasini bosmang — pul sotuvchiga o'tadi
• Mashhur brend juda arzon bo'lsa — nusxa bo'lishi mumkin
• Muddat va to'lov shartlari o'zgarib turadi — ilovada tekshiring

🛃 Bojxona: oylik norma pochta orqali — <b>100 $</b>, kuryer orqali — <b>200 $</b> (tovar narxi bo'yicha).

📲 <a href="{{APP_URL}}">Buyurtmangiz normasini ilovada hisoblang</a>

""" + FOOT + "#dokon",
    prompt=cover_prompt("#dokon", "AliExpress: to'g'ridan-to'g'ri",
        "a smartphone showing a generic shopping app with a red-orange header (no logo), a small airplane flying along a dotted arc from a tiny pagoda-style landmark toward a small parcel locker with an indigo pin, and two plain bank cards beside the phone.",
        sub="So'mda to'lov · ~14 kun · topshirish punkti", accent="orange (#F97316)"),
    sources=[{"label": "kun.uz — AliExpress to'g'ridan-to'g'ri yetkazish, Uzcard/Humo, 21.12.2023", "url": "https://kun.uz/en/64857911"},
             {"label": "spot.uz — AliExpress Uzcard va Humo, 21.12.2023", "url": "https://www.spot.uz/oz/2023/12/21/aliexpress-uzcard-humo/"},
             {"label": "spot.uz — AliExpress va Uzum topshirish punktlari, 25.04.2023", "url": "https://www.spot.uz/oz/2023/04/25/aliexpress-to-uzum/"},
             {"label": "AliExpress — to'lov usullari", "url": "https://aliexpress.ru/gid/payment_methods"},
             LEX_VM244],
    notes="Yetkazish muddati (~14 kun), Uzcard/Humo va Uzum punktlari bo'yicha manbalar 2023-yilniki — 2025–26 yangilanishi topilmadi; ilovada tekshiring. "
          "AliExpress posilkalari pochta yoki kuryer kanalida kelishi aniqlanmadi — shuning uchun ikkala norma ko'rsatildi. Nizo muddatlari ilovada.")

# ============ JUMA 16-oktabr — #topilma ============
TB_PRICE, TB_KG = 129.00, 1.0
tb_ship = ship(TB_KG)
tb_value = r2(TB_PRICE + tb_ship)
add("2026-10-16-1400", rubric="#topilma", title="Aylanuvchi pichoq charxlagich (Tumbler)",
    caption=f"""🔪 <b>Pichoqni charxlash uchun tosh kerak emas — uni «dumalatasiz»</b>

<b>Tumbler Rolling Knife Sharpener</b> — magnitli blok pichoqni aniq <b>15° yoki 20°</b> burchakda ushlab turadi. Siz esa g'altakni tig' bo'ylab dumalatasiz: bir uchidagi olmos disk charxlaydi, ikkinchisidagi po'lat disk tig'ni tekislaydi.

💡 <b>Nega qiziq:</b> charxlash tosh bilan ishlashni o'rganish shart emas — burchak doim bir xil. Motor ham, batareya ham yo'q.

🛒 <a href="https://www.tumblerware.com/products/tumbler-rolling-knife-sharpener">Tumbler rasmiy do'koni (AQSh)</a> — <b>{money(TB_PRICE)}</b> (aksiyada arzonroq bo'lishi mumkin)

📦 <b>Toshkentgacha</b>
• Tovar — {money(TB_PRICE)}
• AQShdan yetkazish — ~{money(tb_ship)}
• Toshkent bo'ylab — ~$3
• <b>Jami ≈ {fmt(som(TB_PRICE + tb_ship + 3))} so'm</b>

✅ <b>Olib kira olasizmi?</b> Ha. Batareyasiz oddiy oshxona asbobi, cheklangan ro'yxatlarda yo'q. Narxi {money(TB_PRICE)} — kuryer normasi 200 $ dan kam, boj yo'q.

⚠️ Amazon'da arzon nusxalari ko'p — rasmiy do'kondan oling.

Siz pichoqni nima bilan charxlaysiz? 👇

📄 Asos: VM 244-son, 19.04.2025 — lex.uz
""" + FOOT + "#topilma",
    prompt=cover_prompt("#topilma", "Pichoqni «dumalatib» charxlang",
        "a chef's knife held by a small wooden magnetic block at an angle on a kitchen board, and a cylindrical metal roller with a sparkling diamond disc on one end rolling along the blade edge, with subtle motion arcs.",
        sub="Bunday narsa borligini bilarmidingiz?", accent="aqua (#22D3EE)"),
    product_url="https://www.tumblerware.com/products/tumbler-rolling-knife-sharpener",
    sources=[{"label": "Tumbler — Rolling Knife Sharpener (rasmiy)", "url": "https://www.tumblerware.com/products/tumbler-rolling-knife-sharpener"},
             {"label": "The Gadgeteer — Tumbler sharh, 29.01.2025", "url": "https://the-gadgeteer.com/2025/01/29/tumbler-original-rolling-knife-sharpener-review-are-diamonds-a-knifes-best-friend/"},
             {"label": "Tumbler — qo'llanma", "url": "https://tumblerware.com/pages/instructions"},
             LEX_VM244, SPOT_COURIER, SPOT_RATE],
    notes="TASDIQLASHDAN OLDIN: rasmiy sahifada narxni tekshiring — odatda $129, aksiyada ~$98 (Claude muhitidan sayt ochilmadi). "
          "Og'irlik qadoq bilan taxminan 1 kg. Mahsulot 2022-yilda chiqqan, 2024–25 da mashhur bo'ldi. Do'kon AQSh ichiga yetkazadi — kuryerning AQShdagi ombor manzili kerak. "
          "RASM: ChatGPT'ga do'kon sahifasidagi surat biriktirilsa aniqroq chiqadi.")

# ============ #narx — chegirmalar (narxlar qidiruv natijalaridan, 11.10.2026) ============
NOTE_CHECK = "TASDIQLASHDAN OLDIN: AQSh narxi va O'zbekistondagi narxni saytlarda tekshiring (Claude muhitidan do'konlar ochilmadi, narxlar qidiruv natijalaridan). "

posts.append(deal("2026-10-12-2000", title="DualSense — PS5 geympadi", emoji="🎮",
    headline="PS5 geympadi DualSense — $59", hook="Sony DualSense simsiz geympadi (Chroma Teal):",
    store="Amazon", country="AQSh", pnew=59.00, pold=79.99, weight=0.6,
    uz_store="Asaxiy", uz_price=1029000, uz_note="oq rang",
    url="https://www.amazon.com/s?k=DualSense+Chroma+Teal",
    note_lines=["🎨 Toshkentda solishtiruv oq rang bo'yicha — Chroma Teal rangini bu yerda topish qiyin."],
    card_title="Sony DualSense",
    notes=NOTE_CHECK + "Slickdeals: $59 (sahifa 02.10.2026 yangilangan, iyunda e'lon qilingan) — chegirma hali amaldami, tekshiring. Eski narx $79.99 — maxsus rang uchun taxmin. "
          "Toshkent: Asaxiy 1 029 000 (oq), Mediapark 1 160 000, Olcha 960 000 (sotuvda yo'q).",
    sources=[{"label": "Slickdeals — DualSense Chroma Teal $59", "url": "https://slickdeals.net/f/19595892-playstation-dualsense-wireless-controller-chroma-teal-for-ps5-pc-mac-mobile-59"},
             {"label": "Asaxiy — Sony DualSense (oq)", "url": "https://asaxiy.uz/ru/product/geympad-sony-dualsense-besprovodnoy-dlya-playstation-5-belyy"},
             SPOT_RATE]))

posts.append(deal("2026-10-13-2000", title="OneBlade 360 Face — halol hisob: Toshkentda arzon", emoji="🤔",
    headline="Chegirma bor, foyda yo'q: Philips OneBlade 360", hook="Philips OneBlade 360 Face trimmeri Walmart'da:",
    store="Walmart", country="AQSh", pnew=39.96, pold=49.99, weight=0.35,
    uz_store="Texnomart", uz_price=499000, uz_note="QP2724/23",
    url="https://www.walmart.com/ip/seort/1218599001", honest=True,
    mid_line="❌ <b>Xulosa: Toshkentdan oling.</b> Yetkazish qo'shilgach AQSh narxi qimmat chiqadi, ustiga rasmiy kafolat ham bo'lmaydi.",
    note_lines=["💡 Arzon tovarda yetkazish (kamida 1 kg tarifi) foydani yeb qo'yadi — doim yakuniy narxni solishtiring."],
    card_title="Philips OneBlade 360 Face",
    notes=NOTE_CHECK + "AQSh narxi ($39.96 Walmart) 2026-yil o'rtasidagi — oktabr chegirmasi tasdiqlanmagan; eski narx $49.99 taxmin. "
          "Toshkent: Texnomart QP2724/23 (EU versiya) 463 000–499 000. Post ataylab «qimmat» xulosasi bilan.",
    sources=[{"label": "Slickdeals — OneBlade 360 Face QP2724/70 $39.96 (Walmart)", "url": "https://slickdeals.net/f/19635750-39-96-fs-walmart-get-8-wmt-cash-philips-norelco-wet-dry-oneblade-360-face-hybrid-electric-trimmer-and-shaver-qp2724-70"},
             {"label": "Texnomart — Philips trimmerlari", "url": "https://texnomart.uz/katalog/trimmery-philips/"},
             SPOT_RATE]))

posts.append(deal("2026-10-14-2000", title="Instax Mini 12 — to'plam", emoji="📸",
    headline="Instax Mini 12 to'plami — $89.95", hook="Fujifilm Instax Mini 12 lahzali fotoapparat to'plami:",
    store="Amazon", country="AQSh", pnew=89.95, pold=105.95, weight=0.9,
    uz_store="Olcha", uz_price=1543300, uz_note="faqat kamera",
    url="https://www.amazon.com/dp/B0BWNZCL1T",
    note_lines=["🎞 Amazon to'plamida kassetalar va aksessuarlar ham bor — Toshkent narxi faqat kamera uchun."],
    card_title="Fujifilm Instax Mini 12",
    notes=NOTE_CHECK + "ASIN B0BWNZCL1T Kanada ma'lumotidan — AQSh Amazon'da tekshiring (to'plam yoki faqat kamera). Manba: PCMag/Digg 07.10.2026. "
          "Toshkent: Olcha 1 543 300, Uzum 1 549 000, Asaxiy 1 309 000–2 109 000 (rangga qarab).",
    sources=[{"label": "PCMag (Digg) — Instax Mini 12 kit $89.95, 07.10.2026", "url": "https://digg.com/tech/lmn7icre"},
             {"label": "Olcha — Instax Mini 12", "url": "https://olcha.uz/ru/product/view/fotoapparat-momentalnoi-pecati-fujifilm-instax-mini-12-1"},
             SPOT_RATE]))

posts.append(deal("2026-10-15-2000", title="LEGO 42197 — halol hisob: yolg'iz olmang", emoji="🧱",
    headline="LEGO Technic 42197 — $5.99, lekin…", hook="LEGO Technic ekskavator-yuklagich (42197, 104 detal):",
    store="Amazon", country="AQSh", pnew=5.99, pold=9.99, weight=0.2,
    uz_store="Texnomart", uz_price=210000, uz_note="xuddi shu to'plam",
    url="https://www.amazon.com/s?k=LEGO+42197+Backhoe+Loader", honest=True,
    mid_line="💡 <b>Yolg'iz buyurtma qilmang.</b> Yetkazish (kamida 1 kg tarifi) tovarning o'zidan qimmat. Boshqa posilka bilan birga oling — shunda u deyarli tovar narxida keladi.",
    note_lines=[],
    card_title="LEGO Technic 42197",
    notes=NOTE_CHECK + "Slickdeals/9to5Toys: $5.99 (odatda $9.99) — chegirma 07.10 atrofida. ASIN topilmadi — havola Amazon qidiruvi. Texnomart narxi katalogdan (tovar sahifasi topilmadi).",
    sources=[{"label": "9to5Toys — Fall Prime Day LEGO deals, 07.10.2026", "url": "https://9to5toys.com/2026/10/07/lego-building-set-deals/"},
             {"label": "Texnomart — LEGO katalogi", "url": "https://texnomart.uz/katalog/lego/"},
             SPOT_RATE]))

posts.append(deal("2026-10-16-2000", title="🏆 AirPods Pro 3", emoji="🏆",
    headline="Haftaning eng yaxshi chegirmasi: AirPods Pro 3", hook="Shovqin bostirishli Apple AirPods Pro 3:",
    store="Amazon", country="AQSh", pnew=179.00, pold=249.00, weight=0.3,
    uz_store="iSpace", uz_price=3999000, uz_note="MFHP4",
    url="https://www.amazon.com/dp/B0FQFB8FMG", badge="HAFTA TOP",
    note_lines=["⏱ Narx $179–199 oralig'ida o'zgarib turibdi — to'lashdan oldin tekshiring."],
    card_title="AirPods Pro 3",
    notes=NOTE_CHECK + "9to5Toys 10.10.2026: Amazon $179–199, Walmart $179 (11.10 gacha). ASIN B0FQFB8FMG (MFHP4LL/A) camelcamelcamel orqali. Toshkent: iSpace va Texnomart 3 999 000.",
    sources=[{"label": "9to5Toys — this weekend's best Apple deals, 10.10.2026", "url": "https://9to5toys.com/2026/10/10/this-weeks-best-apple-deals-3/"},
             {"label": "iSpace — AirPods Pro 3", "url": "https://ispace.uz/en/product/airpods-pro-3-mfhp4ze-a"},
             SPOT_RATE]))

posts.append(deal("2026-10-17-2000", title="Kindle Paperwhite Signature 32 GB", emoji="📚",
    headline="Kindle Paperwhite Signature — $169.99", hook="Kindle Paperwhite Signature Edition 32 GB (2024):",
    store="Amazon", country="AQSh", pnew=169.99, pold=249.99, weight=0.45,
    uz_store="Uzum", uz_price=3680000, uz_note="32 GB, 2024",
    url="https://www.amazon.com/dp/B0CFPLP3YL",
    note_lines=["💡 Simsiz zaryadlash, avtomatik yorug'lik va suvdan himoya — Paperwhite'ning eng to'liq versiyasi."],
    card_title="Kindle Paperwhite Signature",
    notes=NOTE_CHECK + "Uzum narxi (3 680 000) «o'xshash tovarlar» blokidan — ishonch past; Toshkentda ko'proq 2021-yil modeli sotiladi (Uzum 2 945 000–3 100 000, sotuvda yo'q). "
          "ASIN B0CFPLP3YL UK sotuvchidan — AQSh Amazon'da tekshiring. Manba: The eBook Reader, 05.10.2026.",
    sources=[{"label": "The eBook Reader — Kindle chegirmalari, 05.10.2026", "url": "https://blog.the-ebook-reader.com/2026/10/05/kindle-scribes-and-previous-gen-kindles-on-sale-up-to-160-off/"},
             {"label": "Uzum — Kindle", "url": "https://uzum.uz/ru/product/elektronnaya-kniga-kindle-kids-7-821057"},
             SPOT_RATE]))

posts.append(deal("2026-10-18-2000", title="Apple Watch SE 3 — normaga sig'adi", emoji="⌚",
    headline="Apple Watch SE 3 — $199, boj yo'q", hook="Apple Watch SE 3 GPS, 40 mm:",
    store="Amazon", country="AQSh", pnew=199.00, pold=249.00, weight=0.4,
    uz_store="iSpace", uz_price=4299000, uz_note="Midnight, 40 mm",
    url="https://www.amazon.com/s?k=Apple+Watch+SE+3+GPS+40mm",
    note_lines=["💡 Narxi 200 $ normadan atigi 1 $ kam — boj yo'q. Shu oyda boshqa posilka kutayotgan bo'lsangiz, uni keyingi oyga qoldiring."],
    card_title="Apple Watch SE 3",
    notes=NOTE_CHECK + "9to5Toys 07.10.2026: $199 (Prime Day) — keyin narxlar qaytayotgani aytilgan, hali amaldami tekshiring. ASIN topilmadi — havola Amazon qidiruvi. "
          "Toshkent: iSpace 4 299 000 (Midnight 40 mm), Olcha 4 038 000, Texnomart 4 399 000–4 900 000. Tovar 199 $ ≤ 200 — yo'l qo'shilmaydi, boj yo'q (muallif qoidasi).",
    sources=[{"label": "9to5Toys — Apple Watch from $199, 07.10.2026", "url": "https://9to5toys.com/2026/10/07/current-gen-apple-watch-199-fall-prime-day/"},
             {"label": "iSpace — Apple Watch SE 3", "url": "https://ispace.uz/en/category/apple-watch-se-3"},
             LEX_PQ4508, LEX_VM55, SPOT_RATE]))

# ============ YAKSHANBA 18-oktabr — #digest ============
add("2026-10-18-0900", rubric="#digest", title="Hafta yakuni — 5 ta post",
    caption="""🗂 <b>Hafta yakuni: eng foydali 5 ta post</b>

1️⃣ <a href="{{LINK:2026-10-12-0900}}">Normadan biroz oshdingizmi?</a> — 5 $ ortiqcha uchun yuz minglab so'm to'lamaslik yo'li
2️⃣ <a href="{{LINK:2026-10-13-0900}}">Dori va vitamin: qancha mumkin</a> — pul emas, dona hisoblanadi
3️⃣ <a href="{{LINK:2026-10-14-0900}}">Yo'l harajati normaga qo'shiladimi?</a> — 200 $ gacha yo'q
4️⃣ <a href="{{LINK:2026-10-15-1400}}">Hajmiy og'irlik</a> — 1 kg kurtka nega 10 kg bo'lib chiqadi
5️⃣ <a href="{{LINK:2026-10-16-2000}}">AirPods Pro 3</a> — haftaning eng katta tejashi

🏷 Hafta chegirmalari: DualSense, Instax Mini 12, LEGO 42197, Kindle Paperwhite, Apple Watch SE 3.

Saqlab qo'ying va do'stlaringizga ulashing — ularga ham kerak bo'ladi 📌

""" + FOOT + "#digest",
    prompt=cover_prompt("#digest", "Hafta yakuni",
        "five small rounded cards stacked in a gentle fan, each with a tiny icon (balance scale, pill bottle, delivery truck, oversized box, earbuds), with a bookmark ribbon in indigo.",
        sub="Eng foydali 5 ta post", accent="amber (#F59E0B)"),
    sources=[])
# ------------------------------------------------------------------ yozish va tekshirish
# --rework=ID,ID — faqat shu qoralamalarni (draft / needs_input) qayta yozadi
REWORK = {x for arg in sys.argv if arg.startswith("--rework=") for x in arg.split("=", 1)[1].split(",") if x}
problems = []
for p in posts:
    p.setdefault("scheduled_at", f"{p['id'][:10]}T{p['id'][11:13]}:{p['id'][13:15]}:00+05:00")
    p.setdefault("status", "draft")
    n = vislen(p["caption"])
    p_flag = "OK" if n <= 1024 else "UZUN!"
    if n > 1024:
        problems.append((p["id"], n))
    target = OUT / f"{p['id']}.json"
    if REWORK and p["id"] not in REWORK:
        continue
    if REWORK and target.exists():
        cur = json.loads(target.read_text(encoding="utf-8"))
        allowed = ("draft", "needs_input") + (("approved",) if "--allow-approved" in sys.argv else ())
        if cur.get("status") not in allowed:
            print(f"{p['id']}  {cur.get('status')} — qayta yozilmadi")
            continue
        # Panel maydonlari saqlanadi: holat, rasm va h.k. (faqat matn, prompt, manbalar yangilanadi)
        for k in ("status", "image", "message_id", "published_at", "published_by", "error", "publish_now"):
            if k in cur:
                p[k] = cur[k]
    if target.exists() and "--force" not in sys.argv and not REWORK:
        print(f"{p['id']}  mavjud — tegilmadi (panelda tasdiqlangan bo'lishi mumkin)")
        continue
    target.write_text(json.dumps(p, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{p['id']}  {p['rubric']:10} {n:5}  {p_flag}  {p['title']}")

print(f"\n{len(posts)} ta post yozildi.")
if problems:
    print("1024 dan uzun:", problems)
