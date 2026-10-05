# -*- coding: utf-8 -*-
"""5–11-oktabr 2026 haftasi uchun 21 ta postni yaratadi (data/posts/*.json).
Barcha narx hisob-kitoblari shu yerda bajariladi — matnga qo'lda raqam yozilmaydi."""

import html
import json
import sys
import math
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "posts"
OUT.mkdir(parents=True, exist_ok=True)

RATE = 11772.95            # CBU, 03.10.2026 (05.10.2026 gacha amalda)
RATE_TXT = "1 $ = 11 772,95 so'm (03.10.2026)"
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
    duty = round(max(0.0, pnew - LIMIT) * DUTY, 2)
    total_usd = pnew + sh + duty
    total = som(total_usd)
    save = int(round((uz_price - total) / 1000.0)) * 1000
    pct = round(save / uz_price * 100)
    disc = round((pold - pnew) / pold * 100)

    duty_line = (f"• Bojxona — <b>0 so'm</b> (200 $ normadan past)" if duty == 0
                 else f"• Yagona bojxona to'lovi — ({money(pnew)} − 200) × 30 % = <b>{money(duty)}</b>")
    w_txt = f"~{str(weight).replace('.', ',')} kg"
    ship_txt = f"~{money(round(sh))}" + (f" ({w_txt})" if weight >= 1 else "")

    parts = [f"{emoji} <b>{headline}</b>", "", f"{hook} {money(pold)} → <b>{money(pnew)}</b> (−{disc}%).", ""]
    parts += ["💰 <b>Chetdan olib kelish</b>" + (" — boj bilan ham" if duty else ""),
              f"• Tovar — {money(pnew)}", f"• AQShdan yetkazish — {ship_txt}", duty_line,
              f"• <b>Jami ≈ {fmt(total)} so'm</b>", "",
              f"🇺🇿 <b>Toshkentda:</b> {uz_store} — {fmt(uz_price)} so'm" + (f" ({uz_note})" if uz_note else ""), ""]
    if honest:
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
        bottom_label="FARQ" if honest else "TEJAYSIZ", bottom_value=f"{fmt(save)} so'm",
        bottom_color="amber (#D97706)" if honest else "green (#059669)")

    calc = (f"Hisob: tovar {money(pnew)} + yetkazish ~{money(sh)} + boj {money(duty)} = {money(round(total_usd, 2))} "
            f"× {RATE} = {fmt(total)} so'm. Tejash: {fmt(uz_price)} − {fmt(total)} = {fmt(save)} so'm ({pct}%).")
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
SPOT_RATE = {"label": "Markaziy bank kursi, 03.10.2026 (spot.uz)", "url": "https://www.spot.uz/oz/currency/"}
SPOT_COURIER = {"label": "Yetkazib beruvchilar narxi, 16.07.2026 (spot.uz)", "url": "https://www.spot.uz/oz/2026/07/16/delivery"}

# ============ DUSHANBA 5-oktabr ============
add("2026-10-05-0900", rubric="#boj", title="Boj 2027-yildan 20 % ga tushadi",
    caption="""🛃 <b>Boj 2027-yildan arzonlashadi: 30 % → 20 %</b>

Prezident Farmoni bilan jismoniy shaxslar uchun yagona bojxona to'lovi pasaytirildi. Bu bojsiz normadan oshgan tovarlarga tegishli.

📌 <b>Nima o'zgaradi</b>
• Hozir: <b>30 %</b>, lekin 1 kg uchun kamida <b>3 $</b>
• <b>2027-yil 1-yanvardan:</b> <b>20 %</b>, lekin 1 kg uchun kamida <b>2 $</b>
• <b>2027-yil 1-iyundan:</b> yagona to'lov bojxona yig'imlaridan kam bo'lsa, yig'im undirilmaydi

🧮 <b>Misol:</b> kuryer orqali 500 $ lik tovar. Oylik norma — 200 $, ortiqcha qism — 300 $.
• Hozir: 300 × 30 % = <b>90 $</b>
• Yanvardan: 300 × 20 % = <b>60 $</b>

💡 Qimmat xaridni (telefon, noutbuk) shoshilmasangiz yanvargacha kutish mantiqli.

📄 Asos: PF-174, 27.08.2026 (V bo'lim 8-band, 3-band «g»); PQ-4508, 07.11.2019, 3-band — lex.uz
📲 <a href="{{APP_URL}}">Bojingizni ilovada hisoblang</a>

""" + FOOT + "#boj",
    prompt=cover_prompt("#boj", "Boj 2027-yildan arzonlashadi",
        "a matte cardboard parcel box with an indigo shipping label, and next to it a large 3D percent sign with a soft downward arrow; a small desk calendar page shows the number 1.",
        sub="30 % → 20 %", accent="emerald green (#059669)"),
    sources=[LEX_PF174, LEX_PQ4508],
    notes="Matn PF-174 asl matni bilan solishtirilgan (lex.uz). 30 %/3 $ — PQ-4508 ning 2019-yil tahriri.")

add("2026-10-05-1400", rubric="#dokon", title="iHerb — O'zbekistonga to'g'ridan-to'g'ri",
    caption="""🛍 <b>iHerb O'zbekistonga to'g'ridan-to'g'ri yetkazadi</b>

Vitamin, BAD, sport ozuqasi va kosmetika do'koni. Ekspeditor kerak emas — buyurtma uyingizgacha keladi.

✅ <b>Afzalliklari</b>
• Yetkazuvchi — <b>Meest</b>, to'liq kuzatuv bilan
• <b>30 $ dan</b> yuqori buyurtmaga yetkazish bepul (vaqtinchalik aksiya)
• Visa va Mastercard bilan to'lov

⚠️ <b>Bilib qo'ying</b>
• Meest cheklovi: bitta posilka <b>185 $</b> va <b>11 kg</b> gacha
• BAD normasi: <b>10 xil nomgacha</b>, jami <b>3 kg</b>, har nomdan <b>1 qadoq</b>
• Kuryer uchun oylik bojsiz norma — <b>200 $</b>, oydagi barcha posilkalar qo'shib hisoblanadi

💡 Savatni 185 $ dan oshirmang va bir xil mahsulotdan 2 ta olmang.

🔗 <a href="https://www.iherb.com/shipping/uz">iHerb: O'zbekistonga yetkazish shartlari</a>
📲 <a href="{{APP_URL}}">Boshqa do'konlar — ilovada</a>

📄 BAD normasi: VM 244-son qarori, 1-ilova (lex.uz)
""" + FOOT + "#dokon",
    prompt=cover_prompt("#dokon", "iHerb O'zbekistonga yetkazadi",
        "an open matte cardboard parcel box with three supplement bottles (white with indigo caps) and a small green leaf peeking out; a thin dotted route line arcs from the box to a tiny location pin.",
        sub="Ekspeditorsiz, to'g'ridan-to'g'ri", accent="leaf green (#16A34A)"),
    sources=[{"label": "iHerb — Uzbekistan shipping", "url": "https://www.iherb.com/shipping/uz"}, LEX_VM244],
    notes="iHerb sahifasida boj matni noaniq yozilgan («month calendar quarter») — biz VM 244 dagi oylik 200 $ normaga tayandik. "
          "Uzcard/Humo bilan to'lov tekshirilmagan — postda faqat Visa/Mastercard yozildi.")

posts.append(deal("2026-10-05-2000", title="Apple Pencil Pro", emoji="✏️",
    headline="Apple Pencil Pro — Amazonda $99", hook="Apple'ning eng yangi qalami chegirmada:",
    store="Amazon", country="AQSh", pnew=99.00, pold=129.00, weight=0.15,
    uz_store="iSpace", uz_price=2059900, uz_note=None,
    url="https://www.amazon.com/dp/B0D3J71RM7",
    note_lines=["⚠️ Faqat iPad Pro (M4), iPad Air (M2) va yangilari bilan ishlaydi — iPad modelingizni tekshiring.",
                "Amazon'dan olinganda O'zbekistonda rasmiy kafolat bo'lmaydi."],
    card_title="Apple Pencil Pro",
    notes="Narxlar 29.09–03.10 holatiga (Amazon October Prime Day). Chiqishdan oldin bir qarab chiqing.",
    sources=[{"label": "NBC Select — October Prime Day Apple deals, 29.09.2026",
              "url": "https://www.nbcnews.com/select/shopping/october-prime-day-2026-apple-deals-rcna600311"},
             {"label": "iSpace — Apple Pencil Pro", "url": "https://ispace.uz/en/product/apple-for-ipad-pro-13-inch-m4-ipad-pro-11-inch-m4-ipad-air-13-inch-m2-ipad-air-11-inch-m2-whiteapple-pencil-pro-mx2d3qn-a"},
             SPOT_RATE]))

# ============ SESHANBA 6-oktabr ============
add("2026-10-06-0900", rubric="#taqiq", title="Buni buyurtma qilmang — 7 ta taqiq",
    caption="""🚫 <b>Buni chetdan buyurtma qilmang — posilka qaytadi</b>

Ko'pchilik bilmay oladi, keyin bojxonada ushlanib qoladi:

1️⃣ <b>Elektron sigaret, vape va suyuqliklari</b> — olib kirish taqiqlangan (O'RQ-844, 37-modda)
2️⃣ <b>Lazer ko'rsatkich</b> — taqiqlangan (VM 50-son, 20.02.2013)
3️⃣ <b>Dron</b> — ruxsatnomasiz taqiqlangan (VM 658-son, 2-band; VM 801-son)
4️⃣ <b>Ratsiya</b> — EMMM ruxsatnomasi kerak (VM 801-son, Nizom 98-band)
5️⃣ <b>Elektroshok</b> — pochtada taqiqlangan; olib kirish faqat IIV ruxsati bilan (O'RQ-550, 15-modda)
6️⃣ <b>Urug', ko'chat, meva va sabzavot</b> — xalqaro pochtada taqiqlangan
7️⃣ <b>Alkogol va tamaki</b> — pochta va kuryer orqali taqiqlangan (VM 244-son, 1-ilova)

💡 Alohida qadoqlangan litiy batareyalar ham pochtada qabul qilinmaydi — batareya qurilma ichida bo'lishi kerak.

📄 6-band va batareya — Pochta aloqasi xizmatlarini ko'rsatish qoidalari, 3-ilova. Barcha hujjatlar lex.uz'da.
📲 <a href="{{APP_URL}}">Tovaringizni ilovada tekshiring</a>

""" + FOOT + "#taqiq",
    prompt=cover_prompt("#taqiq", "Buni buyurtma qilmang",
        "an open matte cardboard parcel box; floating above it a small vape pen, a laser pointer, a mini drone and a walkie-talkie, all in matte grey, with a bold crimson prohibition circle (circle with a diagonal bar) in front of them.",
        sub="Posilka bojxonada qaytadi", accent="crimson (#E11D48)"),
    sources=[{"label": "O'RQ-844, 24.05.2023 — 37-modda (lex.uz)", "url": "https://lex.uz/uz/docs/-6472100"},
             {"label": "VM 50-son, 20.02.2013 — lazer ko'rsatkichlar (lex.uz)", "url": "https://lex.uz/uz/docs/-2135969"},
             {"label": "VM 658-son, 15.11.2022 — dronlar (lex.uz)", "url": "https://lex.uz/uz/docs/-6284990"},
             {"label": "VM 801-son, 22.12.2020 — Nizom 98-band, 4-ilova (lex.uz)", "url": "https://lex.uz/uz/docs/-5179158"},
             {"label": "O'RQ-550, 29.07.2019 — Qurol to'g'risida, 15-modda (lex.uz)", "url": "https://lex.uz/uz/docs/-4445288"},
             {"label": "Pochta aloqasi xizmatlarini ko'rsatish qoidalari, 3-ilova (lex.uz)", "url": "https://lex.uz/uz/docs/-1772402"},
             {"label": "VM 244-son, 1-ilova «a» izohi (VM 154-son, 09.04.2026 tahriri) (lex.uz)", "url": "https://lex.uz/uz/docs/-7484114"},
             {"label": "aeroinfo.uz — pochta bo'limi", "url": "https://aeroinfo.uz/#/post/4"}],
    notes="Ratsiya istisnosi (5 Vt gacha, 26965–27860 kGs) joy yetmagani uchun yozilmadi — kerak bo'lsa izohda javob bering.")

add("2026-10-06-1400", rubric="#olcham", title="O'lchamda adashmaslik usuli",
    caption="""📏 <b>O'lchamda adashmaslikning ishonchli usuli</b>

Chetdan kiyim-poyabzal qaytarish qimmat. Shuning uchun «odatda 42 kiyaman» degan taxmin emas, <b>santimetr</b> bilan ishlang.

👟 <b>Poyabzal</b>
1. Qog'ozga turing, tovon va eng uzun barmoq uchini belgilang
2. Oraliqni santimetrda o'lchang — bu oyoq uzunligi
3. Do'konning o'z jadvalidan <b>sm</b> ustunini toping, 0,5–1 sm zaxira qo'shing

👕 <b>Kiyim</b>
• O'zingizga yaxshi tushgan kiyimni tekis yoyib, ko'krak kengligi va uzunligini o'lchang
• Do'kon jadvalidagi tovar o'lchamlari bilan solishtiring

⚠️ Xitoy do'konlarida o'lchamlar ko'pincha 1–2 pog'ona kichik bo'ladi — harfga (M, L) emas, santimetrga qarang.

📊 Taxminiy moslik (erkaklar poyabzali): 26 sm ≈ EU 41 ≈ US 8 · 27 sm ≈ EU 42 ≈ US 9 · 28 sm ≈ EU 43–44 ≈ US 10. Brendga qarab farq qiladi.

📲 <a href="{{APP_URL}}">O'lcham qo'llanmalari — ilovada</a>

""" + FOOT + "#olcham",
    prompt=cover_prompt("#olcham", "O'lchamda adashmang",
        "a bare foot outline drawn on a white sheet of paper with a yellow-and-indigo measuring tape along it, a pencil, and a neat sneaker beside it.",
        sub="Santimetr bilan o'lchang", accent="warm yellow (#F59E0B)"),
    sources=[],
    notes="Moslik jadvali taxminiy — postda shunday deb yozilgan.")

posts.append(deal("2026-10-06-2000", title="Beats Solo 4", emoji="🎧",
    headline="Beats Solo 4 — Amazonda $149.95", hook="Yangi avlod quloqchinlari chegirmada:",
    store="Amazon", country="AQSh", pnew=149.95, pold=199.95, weight=0.6,
    uz_store="Asaxiy", uz_price=2289000, uz_note="pushti rang",
    url="https://www.amazon.com/dp/B0CZPLV566",
    note_lines=["⚠️ Narx 200 $ normaga yaqin. Shu oyda boshqa posilka kutayotgan bo'lsangiz, ikkinchisi bojga tushishi mumkin."],
    card_title="Beats Solo 4",
    notes="Asaxiy narxi pushti rang uchun, Amazon — qora (Matte Black). Model bir xil.",
    sources=[{"label": "Consequence — October Prime Day headphone deals, 01.10.2026",
              "url": "https://consequence.net/2026/10/best-october-prime-day-headphone-deals-2026/"},
             {"label": "Asaxiy — Beats Solo 4", "url": "https://asaxiy.uz/product/besprovodnye-naushniki-beats-solo-4-pink"},
             SPOT_RATE]))

# ============ CHORSHANBA 7-oktabr ============
add("2026-10-07-0900", rubric="#savol", title="Bir oyda ikkita posilka",
    caption="""❓ <b>Savol: «Bir oyda ikkita posilka keldi, ikkalasi ham 200 $ dan arzon. Nega boj so'rashyapti?»</b>

Chunki bojsiz norma <b>bitta posilkaga emas, butun oyga</b> beriladi.

📌 Kuryer orqali — oyiga <b>200 $</b>, pochta orqali — oyiga <b>100 $</b>. Kalendar oy davomidagi barcha jo'natmalar qo'shib hisoblanadi — <b>rasmiylashtirilgan sana</b> bo'yicha, buyurtma sanasi emas.

🧮 <b>Misol (kuryer):</b>
• 1-posilka — 150 $ → norma ichida
• 2-posilka — 120 $ → normadan qolgani 50 $, ortiqcha <b>70 $</b>
• Yagona bojxona to'lovi: 70 × 30 % = <b>21 $</b> (≈ """ + fmt(som(21)) + """ so'm)

💡 <b>Qanday tejash mumkin:</b> katta xaridni ikkiga bo'ling — posilkalar turli kalendar oylarida rasmiylashtirilsin.

📄 Asos: VM 244-son qarori, 19.04.2025; PQ-4508, 3-band — lex.uz
📲 <a href="{{APP_URL}}">Oylik normangizni ilovada hisoblang</a>

""" + FOOT + "#savol",
    prompt=cover_prompt("#savol", "Bir oyda 2 ta posilka",
        "two matte cardboard parcel boxes side by side, one slightly bigger, with a small desk calendar between them and a soft indigo plus sign hovering above.",
        sub="Norma oyga beriladi", accent="amber (#F59E0B)"),
    sources=[LEX_VM244, LEX_PQ4508],
    notes="Norma rasmiylashtirilgan sana bo'yicha hisoblanadi (muallif tasdiqladi).")

add("2026-10-07-1400", rubric="#obraz", title="Ayollar: kuzgi ofis obrazi",
    caption="""👗 <b>Tayyor obraz: kuzgi ofis uslubi</b>
<i>Ayollar uchun · 5 element · bitta do'kondan (H&amp;M, AQSh)</i>

1️⃣ Car Coat palto — <b>$59.99</b>
2️⃣ Turtleneck sviter — <b>$14.99</b> <s>$19.99</s>
3️⃣ Keng shim (wide-leg) — <b>$23.99</b> <s>$29.99</s>
4️⃣ Poshnali botilon — <b>$49.99</b>
5️⃣ To'rtburchak sumka — <b>$24.99</b>

🛒 <b>Tovarlar: $173.95</b> — 200 $ normaga sig'adi, boj yo'q (yetkazish haqi hisobga kirmaydi)

📦 <b>Toshkentgacha</b>
• Yetkazish — ~$34 (≈3,6 kg)
• Toshkent bo'ylab — ~$3
• <b>Jami ≈ """ + fmt(som(173.95 + 34.20 + 3)) + """ so'm</b>

💡 H&amp;M AQSh sayti faqat AQSh ichiga yetkazadi — ekspeditorning AQShdagi manzilidan foydalaning. Ombor savdo solig'i yo'q shtatda (masalan, Delaver) bo'lsa, narxga soliq qo'shilmaydi.

🔗 <a href="https://www2.hm.com/en_us/women/products/jackets-coats.html">Palto</a> · <a href="https://www2.hm.com/en_us/women/products/cardigans-sweaters.html">Sviter</a> · <a href="https://www2.hm.com/en_us/women/products/trousers.html">Shim</a> · <a href="https://www2.hm.com/en_us/women/products/shoes.html">Botilon</a> · <a href="https://www2.hm.com/en_us/women/products/accessories/bags.html">Sumka</a>

<i>Narxlar 03.10.2026 holatiga.</i>
""" + FOOT + "#obraz",
    prompt=outfit_prompt("Kuzgi ofis uslubi", [
        "a camel-beige single-breasted car coat, laid flat",
        "a cream ribbed turtleneck sweater, neatly folded",
        "black wide-leg dress trousers, folded",
        "a pair of black heeled ankle boots, three-quarter angle",
        "a small black rectangular shoulder bag"],
        "camel, cream, black", "5 element · 1 do'kon · $173.95"),
    sources=[{"label": "H&M US — women's jackets & coats", "url": "https://www2.hm.com/en_us/women/products/jackets-coats.html"},
             {"label": "H&M US — sweaters", "url": "https://www2.hm.com/en_us/women/products/cardigans-sweaters.html"},
             {"label": "H&M US — trousers", "url": "https://www2.hm.com/en_us/women/products/trousers.html"},
             {"label": "H&M US — shoes", "url": "https://www2.hm.com/en_us/women/products/shoes.html"},
             {"label": "H&M US — bags", "url": "https://www2.hm.com/en_us/women/products/accessories/bags.html"},
             {"label": "H&M US — shipping (faqat AQSh)", "url": "https://www2.hm.com/en_us/customer-service/shipping-and-delivery.html"},
             SPOT_COURIER],
    notes="Og'irliklar taxminiy (jami ≈3,6 kg), yetkazish 9,50 $/kg. Narx rang va o'lchamga qarab o'zgarishi mumkin. "
          "Hisob: 173.95 + 34.20 + 3 = 211.15 $.")

posts.append(deal("2026-10-07-2000", title="LEGO 31134 — 4 ta to'plam", emoji="🚀",
    headline="LEGO kosmik shattl — 4 ta to'plam $26", hook="LEGO Creator 31134 (3 tasi 1 da) 4 talik to'plamda:",
    store="Amazon", country="AQSh", pnew=26.00, pold=41.00, weight=0.8,
    uz_store="Texnomart", uz_price=880000, uz_note="4 × 220 000",
    url="https://www.amazon.com/dp/B0FPPP8CXF",
    note_lines=["🎁 Tug'ilgan kunlar uchun tayyor sovg'a: 4 bolaga 4 ta to'plam, bitta posilkada."],
    card_title="LEGO Creator 31134 — 4 ta",
    notes="Texnomart'da 1 dona 220 000 so'm (bir xil to'plam raqami). Amazon 4-talik ASIN — 9to5toys havolasidan.",
    sources=[{"label": "9to5toys — early Prime Day LEGO, 30.09.2026",
              "url": "https://9to5toys.com/2026/09/30/early-prime-day-lego-sets-star-wars-marvel-technic-city-disney-super-mario-more/"},
             {"label": "Texnomart — LEGO 31134", "url": "https://texnomart.uz/product/detail/359803/"},
             SPOT_RATE]))

# ============ PAYSHANBA 8-oktabr ============
# #keys — Claude tuzgan tipik holat (BRIEF.md → Aniqlik qoidalari). Narxlar — misol uchun.
KEYS_ITEMS = [("Omega-3, 120 kapsula", 2, 21.50), ("D3 vitamini, 5000 IU", 1, 9.90), ("Magniy glitsinat", 1, 16.40)]
keys_packs = sum(n for _, n, _ in KEYS_ITEMS)
keys_total = round(sum(n * pr for _, n, pr in KEYS_ITEMS), 2)
add("2026-10-08-0900", rubric="#keys", title="Keys: iHerb — 2 ta bir xil BAD",
    caption="""🔍 <b>Keys: «2 ta oling — arzonroq» aksiyasi posilkani to'xtatdi</b>

📦 <b>Nima keldi:</b> kuryer orqali iHerb buyurtmasi — """ + str(keys_packs) + """ qadoq BAD, jami <b>""" + usd(keys_total) + """</b>:
""" + "\n".join(f"• {name} — {n} ta" for name, n, _ in KEYS_ITEMS) + """

Summa 200 $ normadan ancha kam, lekin posilka to'xtadi.

⛔ <b>Muammo:</b> BAD uchun miqdoriy norma bor — <b>10 xil nomgacha, jami 3 kg gacha, har nomdan 1 qadoq</b>. Omega-3 dan 2 ta — ikkinchisi normadan tashqarida. Bu yerda pul emas, <b>dona</b> hisoblanadi.

🛠 <b>Qanday hal qilindi:</b> xaridor kuryer kompaniyasi orqali bojxona talabini aniqladi. Ortiqcha qadoq bo'yicha alohida qaror kutildi — jo'natma bir necha kun kechikdi.

✅ <b>Xulosa:</b> BAD'da «2 ta oling» aksiyalariga aldanmang — bir nomdan bitta qadoq. To'lashdan oldin savatni sanang.

📄 Asos: VM 244-son qarori, 19.04.2025, 1-ilova — lex.uz

Posilkangiz to'xtab qoldimi? Vaziyatingizni ko'rib chiqib, yo'l ko'rsataman 👇
💬 <a href="{{CONSULT_URL}}">Maslahat olish</a>

<i>Holat bojxona amaliyotidagi tipik vaziyatlar asosida tuzilgan.</i>
""" + FOOT + "#keys",
    prompt=cover_prompt("#keys", "«2 ta oling» aksiyasi posilkani to'xtatdi",
        "a matte cardboard parcel opened on a customs inspection counter, showing several supplement bottles inside; two identical bottles stand side by side outside the box, one of them marked with a small amber warning tag, and a large indigo magnifying glass hovers over them.",
        sub="BAD: har nomdan 1 qadoq", accent="amber (#F59E0B)"),
    sources=[LEX_VM244],
    notes="Keysni Claude tuzdi (tipik holat, real voqea emas). Narxlar misol uchun. "
          "Tekshiring: «Qanday hal qilindi» qatoridagi amaliyot (ortiqcha qadoq bo'yicha qaror va kechikish) sizning tajribangizga mos kelsinmi — kerak bo'lsa tahrir qiling. "
          "Norma: BAD 10 xil nomgacha, jami 3 kg, har nomdan 1 qadoq (VM 244, 1-ilova — BRIEF.md).")

add("2026-10-08-1400", rubric="#kuryer", title="Qaysi kuryer qancha — 2026",
    caption="""🚚 <b>Chetdan tovar keltirish: qaysi xizmat qancha?</b>
<i>1 kg uchun narxlar, 2026-yil iyul holatiga</i>

🇺🇸 <b>AQShdan</b>
• Meest — 7,70–9,50 $
• Turon Express — 10 $
• Boxette — 11 $ (ekspress 3–9 kun, ekonom 9–16 kun)
• Globbing — 12 $ dan

🇨🇳 <b>Xitoydan</b>
• Green Post — 5,50 $ dan (3–30 kun)
• Jana Post — 0,61 $ / 100 g (≈ 6,10 $/kg)

🌍 <b>Ko'p yo'nalishli</b>
• Yumecs — 4,40–20 $ (Rossiya, Turkiya, Xitoy, Koreya, Dubay, AQSh, Malayziya)

💡 <b>Tanlashdan oldin</b>
1. Toshkent bo'ylab yetkazish ko'pincha alohida — 2–6,70 $
2. Hajmli, lekin yengil tovarga hajmiy og'irlik qo'llanadi — narx oshadi
3. Bir nechta buyurtmani omborda birlashtiring (konsolidatsiya)

📄 Manba: Spot.uz, 16.07.2026. Buyurtmadan oldin narxni xizmatning o'zidan tekshiring.
📲 <a href="{{APP_URL}}">Kuryerlarni ilovada solishtiring</a>

""" + FOOT + "#kuryer",
    prompt=cover_prompt("#kuryer", "Qaysi kuryer arzon?",
        "a stylized matte white globe with indigo continents; three glowing indigo arcs curve from different sides and converge on one point, with tiny parcel boxes travelling along the arcs, plus a small delivery van and a paper airplane below.",
        sub="1 kg narxlari, 2026", accent="sky blue (#38BDF8)"),
    sources=[SPOT_COURIER],
    notes="Iyul narxlari — kuryerlardan yangilangan narx olsangiz, almashtiring.")

posts.append(deal("2026-10-08-2000", title="Belkin Qi2 25W zaryadlovchi", emoji="🔋",
    headline="Belkin Qi2 2-in-1 zaryadlovchi — $42.99", hook="iPhone va AirPods uchun yig'iladigan magnitli stansiya:",
    store="Amazon", country="AQSh", pnew=42.99, pold=60.00, weight=0.5,
    uz_store="iSpace", uz_price=1000000, uz_note="aksiyada, odatda 1 329 900",
    url="https://www.amazon.com/dp/B0FMBFVD34",
    note_lines=["⚠️ Bu narx faqat Amazon Prime a'zolari uchun.",
                "Komplektdagi adapter AQSh vilkasi bilan — o'tkazgich kerak; yorlig'ida 100–240V yozilganini tekshiring."],
    card_title="Belkin UltraCharge 2-in-1 Qi2 25W",
    notes="iSpace modeli WIZ039 — shu zaryadlovchining mintaqaviy versiyasi.",
    sources=[{"label": "9to5toys — Belkin 25W foldable, 01.10.2026",
              "url": "https://9to5toys.com/2026/10/01/belkin-25w-foldable-magsafe-charging-station-prime-day/"},
             {"label": "iSpace — Belkin WIZ039", "url": "https://ispace.uz/en/product/belkin-wireless-charger-25-w-black-wiz039kqbk"},
             SPOT_RATE]))

# ============ JUMA 9-oktabr ============
# Bojxona yig'imi: 1 ta BKO (bojxona kirim orderi) uchun BHM ning 25 % i (VM 55-son, 31.01.2025); BHM 01.09.2026 dan 440 000 so'm
BHM = 440000
_boj_fee = round(BHM * 0.25)
add("2026-10-09-0900", rubric="#boj", title="Boj qanday hisoblanadi — 5 qadam",
    caption="""🧮 <b>Boj qanday hisoblanadi: 5 qadam</b>

Misol: kuryer orqali <b>700 $</b> lik noutbuk, og'irligi 2,5 kg. Shu oyda boshqa posilka yo'q. Yetkazish narxi hisobga kirmaydi — faqat tovar narxi olinadi.

1️⃣ <b>Normani ayiring.</b> Kuryer uchun oylik norma — 200 $. Ortiqcha qism: 700 − 200 = <b>500 $</b>
2️⃣ <b>Foizni qo'llang.</b> Yagona bojxona to'lovi — 30 %: 500 × 30 % = <b>150 $</b>
3️⃣ <b>Minimalni tekshiring.</b> 1 kg uchun kamida 3 $: 2,5 × 3 = 7,5 $. Foiz bo'yicha summa katta — <b>150 $</b> to'lanadi
4️⃣ <b>So'mga o'giring:</b> 150 × """ + f"{RATE:,.2f}".replace(",", " ").replace(".", ",") + """ ≈ <b>""" + fmt(som(150)) + """ so'm</b>
5️⃣ <b>Yig'imni qo'shing.</b> 1 ta BKO (bojxona kirim orderi) uchun — BHM ning 25 %: """ + fmt(BHM) + """ × 25 % = <b>""" + fmt(_boj_fee) + """ so'm</b>

💰 <b>Jami: ≈ """ + fmt(som(150) + _boj_fee) + """ so'm</b>

📅 2027-yil 1-yanvardan stavka 20 %: 500 × 20 % = <b>100 $</b> — 50 $ tejaladi.

⚠️ Hisob taxminiy: yakuniy summani bojxona organi tovarning bojxona qiymati asosida belgilaydi.

📄 Asos: PQ-4508, 3-band; PF-174, V bo'lim 8-band; VM 244-son; VM 55-son, 31.01.2025 — lex.uz
💬 <a href="{{CONSULT_URL}}">Murakkab holat bo'lsa — maslahat oling</a>

""" + FOOT + "#boj",
    prompt=cover_prompt("#boj", "Boj qanday hisoblanadi",
        "a matte white calculator next to a closed laptop resting on a cardboard parcel; five small numbered indigo steps (1, 2, 3, 4, 5) rise like a staircase beside them.",
        sub="5 qadamda", accent="emerald green (#059669)"),
    sources=[LEX_PQ4508, LEX_PF174, LEX_VM244,
             {"label": "VM 55-son qarori, 31.01.2025 — bojxona yig'imlari stavkalari (lex.uz)", "url": "https://lex.uz/uz/docs/-7357270"},
             {"label": "Bojxona yig'imlari stavkalari — gazeta.uz, 03.02.2025 (yangilik)", "url": "https://www.gazeta.uz/oz/2025/02/03/customs-duties/"},
             {"label": "BHM 440 000 so'm, 01.09.2026 dan — gazeta.uz, 23.06.2026 (yangilik)", "url": "https://www.gazeta.uz/oz/2026/06/23/ish-haqi-nafaqalar/"},
             SPOT_RATE],
    notes="Yetkazish narxi bojxona qiymatiga kirmaydi — hisob tovar narxi bo'yicha (muallif tasdiqladi). "
          "5-QADAM LEX.UZ DA TASDIQLANMADI (lex.uz Claude muhitidan ochilmadi): 1 ta BKO uchun yig'im — BHM ning 25 % (muallif so'rovi, stavka qidiruv natijalaridan) "
          "va BHM 440 000 so'm — yangilik saytlaridan. Tasdiqlashdan oldin VM 55-son qarorida tekshiring.")

# #topilma — Uni Kuru Toga Dive (unibrands.co, AQSh rasmiy do'koni, $99.99)
_kt_price = 99.99
_kt_ship = ship(0.2)
_kt_local = 3.0
add("2026-10-09-1400", rubric="#topilma", title="O'zi yozadigan qalam (Kuru Toga Dive)",
    caption=f"""✏️ <b>Bu qalamni hech qachon bosmaysiz</b>

Yaponiyaning Uni kompaniyasi <b>Kuru Toga Dive</b> mexanik qalamini chiqargan. Qopqog'ini ochishingiz bilan grifel o'zi chiqadi. Yozayotganda u o'zi uzayadi va har chiziqda biroz aylanib, uchi doim o'tkir qoladi. Grifel qancha chiqishini 5 pog'onada sozlaysiz.

💡 <b>Nega qiziq:</b> batareya ham, elektronika ham yo'q — hammasi mexanika. Qopqoq magnit bilan «chiq» etib yopiladi.

🛒 <a href="https://www.unibrands.co/products/kuru-toga-dive">Uni rasmiy do'koni (AQSh)</a> — <b>{money(_kt_price)}</b>

📦 <b>Toshkentgacha</b>
• Tovar — {money(_kt_price)}
• AQShdan yetkazish — ~{money(_kt_ship)}
• Toshkent bo'ylab — ~$3
• <b>Jami ≈ {fmt(som(_kt_price + _kt_ship + _kt_local))} so'm</b>

✅ <b>Olib kira olasizmi?</b> Ha. Batareyasiz oddiy kantselyariya, cheklangan ro'yxatlarda yo'q. Narxi kuryer normasidan (oyiga 200 $) kam — boj yo'q. Pochta orqali norma 100 $: qalam sig'adi, lekin shu oyda boshqa posilka bo'lmasin.

Siz shunday qalam bilan yozarmidingiz? 👇

📄 Asos: VM 244-son, 19.04.2025 — lex.uz
""" + FOOT + "#topilma",
    prompt=cover_prompt("#topilma", "Bu qalamni hech qachon bosmaysiz",
        "a sleek glossy deep-blue premium mechanical pencil lying diagonally with its magnetic cap removed beside it; a fine graphite tip writes a thin elegant line on a sheet of paper, with a few subtle motion arcs showing the lead slowly rotating.",
        sub="Bunday narsa borligini bilarmidingiz?", accent="aqua (#22D3EE)"),
    product_url="https://www.unibrands.co/products/kuru-toga-dive",
    sources=[{"label": "Uni (unibrands.co) — KURU TOGA DIVE, $99.99", "url": "https://www.unibrands.co/products/kuru-toga-dive"},
             {"label": "JetPens — Uni Kuru Toga Dive", "url": "https://www.jetpens.com/Uni-Kuru-Toga-Dive-Mechanical-Pencils/ct/6971"},
             LEX_VM244, SPOT_COURIER, SPOT_RATE],
    notes="TASDIQLASHDAN OLDIN: unibrands.co sahifasini oching — narx ($99.99) va rang (Abyss Blue, Aurora Purple) Claude muhitidan ochilmadi, qidiruv natijalaridan olingan. "
          "Do'kon AQSh ichiga yetkazadi — ekspeditor manzili kerak. Og'irlik qadoq bilan taxminan 0,2 kg. "
          "RASM: ChatGPT'ga do'kon sahifasidagi qalam suratini biriktiring.")

posts.append(deal("2026-10-09-2000", title="🏆 Braun Series 9 PRO+ (boj bilan ham foydali)", emoji="🏆",
    headline="Haftaning eng yaxshi chegirmasi: Braun Series 9 PRO+",
    hook="Tozalash stansiyali flagman soqol olish mashinasi:",
    store="Amazon", country="AQSh", pnew=349.99, pold=449.99, weight=1.5,
    uz_store="Olcha", uz_price=7320000, uz_note="9597cc, Yevropa versiyasi",
    url="https://www.amazon.com/dp/B0FGLF3SDT",
    mid_line="💡 Farq katta bo'lsa, normadan oshgan tovar ham boj bilan birga foydali chiqadi.",
    note_lines=["⚠️ Vilka AQSh standartida (A turi) — o'tkazgich kerak. Zaryadlovchi yorlig'ida 100–240V yozilganini tekshiring."],
    card_title="Braun Series 9 PRO+", badge="HAFTA TOP",
    notes="AQSh modeli 9660cc, O'zbekistondagi — 9597cc (Yevropa versiyasi, xuddi shu seriya). Minimal to'lov tekshiruvi: 1,5 kg × 3 $ = 4,5 $ < 45 $.",
    sources=[{"label": "Popular Science — early Prime Big Deal Days, 29.09.2026",
              "url": "https://www.popsci.com/gear/early-prime-big-deal-days-sale-dyson-ninja-roomba/"},
             {"label": "Olcha — Braun Series 9 Pro+ 9597cc", "url": "https://olcha.uz/ru/product/view/elektrobritva-braun-series-9-pro-9597cc"},
             LEX_PQ4508, SPOT_RATE]))

# ============ SHANBA 10-oktabr ============
# #savol — iPhone 17 Pro Max 256 GB, aniq hisob (muallif so'rovi: bojxona qiymatiga 10 $ yo'l harajati + 1 BKO yig'imi)
def uzn(x, dec=2):
    """O'zbekcha son: 1 009; 302,70"""
    s = f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")
    return s[:-3] if dec and s.endswith(",00") else s
IP_PRICE = 1199.00          # Apple AQSh, 256 GB, savdo solig'isiz
IP_ROAD = 10.00             # yo'l harajati — bojxona qiymatiga qo'shiladi
IP_KG = 0.5                 # qadoq bilan, taxminan
IP_UZIMEI = round(BHM * 0.20)
ip_value = IP_PRICE + IP_ROAD
ip_over = ip_value - LIMIT
ip_duty = round(ip_over * DUTY, 2)
ip_min = round(IP_KG * 3, 2)
ip_duty_som = round(ip_duty * RATE)
ip_state = ip_duty_som + _boj_fee + IP_UZIMEI
ip_full = round((IP_PRICE + IP_ROAD) * RATE) + ip_state
ip_duty27 = round(ip_over * 0.20, 2)
add("2026-10-10-0900", rubric="#savol", title="iPhone 17 Pro Max — aniq hisob",
    caption=f"""❓ <b>Savol: «iPhone 17 Pro Max'ni AQShdan posilkada olsam, qancha to'layman?»</b>

Misol: <b>iPhone 17 Pro Max, 256 GB</b> — Apple AQSh narxi <b>{uzn(IP_PRICE)} $</b>. Kuryer orqali, shu oyda boshqa posilka yo'q.

1️⃣ <b>Bojxona qiymati</b> (telefon + yo'l harajati): {uzn(IP_PRICE)} + {uzn(IP_ROAD)} = <b>{uzn(ip_value)} $</b>
2️⃣ <b>Normadan ortig'i:</b> {uzn(ip_value)} − {uzn(LIMIT)} = <b>{uzn(ip_over)} $</b>
3️⃣ <b>Yagona bojxona to'lovi 30 %:</b> {uzn(ip_over)} × 30 % = <b>{uzn(ip_duty)} $</b>
(kamida 3 $/kg: {uzn(IP_KG)} × 3 = {uzn(ip_min)} $ — foiz bo'yicha summa katta)
→ {uzn(ip_duty)} × {uzn(RATE)} = <b>{fmt(ip_duty_som)} so'm</b>
4️⃣ <b>1 ta BKO uchun yig'im</b> (BHM ning 25 %): <b>{fmt(_boj_fee)} so'm</b>
5️⃣ <b>UzIMEI</b> (30 kun ichida): <b>{fmt(IP_UZIMEI)} so'm</b>

💰 <b>To'lovlar jami: {fmt(ip_state)} so'm</b>
📱 <b>Hammasi (telefon + yo'l + to'lovlar): ≈ {fmt(round(ip_full, -3))} so'm</b>

📅 2027-yil 1-yanvardan stavka 20 %: {uzn(ip_over)} × 20 % = {uzn(ip_duty27)} $ — ≈ {fmt(som(ip_duty - ip_duty27))} so'm kam.

⚠️ AQSh savdo solig'i (shtatga qarab 0–10 %) hisobga olinmagan. Yakuniy summani bojxona organi belgilaydi.

📄 Asos: PQ-4508, 3-band; VM 244-son; VM 55-son, 31.01.2025; VM 778-son, 6-ilova — lex.uz
📲 <a href="{{{{APP_URL}}}}">Telefon bojini ilovada hisoblang</a>

""" + FOOT + "#savol",
    prompt=cover_prompt("#savol", "iPhone 17 Pro Max: qancha to'laysiz?",
        "a premium smartphone with a large triple-camera block lying in an open matte cardboard parcel box, a small receipt slip with a few calculation lines next to it, and a tiny indigo tag reading IMEI hanging from the box.",
        sub="Boj + yig'im + UzIMEI — aniq hisob", accent="sky blue (#38BDF8)"),
    sources=[{"label": "iPhone 17 Pro Max 256 GB — $1,199 (AQSh, soliqsiz)", "url": "https://applepricehunt.com/us/iphone-17-pro-max-256gb-silver"},
             LEX_PQ4508, LEX_VM244,
             {"label": "VM 55-son qarori, 31.01.2025 — bojxona yig'imlari stavkalari (lex.uz)", "url": "https://lex.uz/uz/docs/-7357270"},
             {"label": "VM 778-son, 17.09.2019 — 6-ilova (lex.uz)", "url": "https://lex.uz/uz/docs/-4517458"},
             {"label": "PF-115, 23.06.2026 — BHM 440 000 so'm (lex.uz)", "url": "https://lex.uz/uz/docs/-8283656"},
             SPOT_RATE],
    notes="Muallif so'rovi: bojxona qiymatiga 10 $ yo'l harajati qo'shildi va 1 ta BKO yig'imi (BHM 25 % = 110 000) hisoblandi. "
          f"Hisob: ({uzn(IP_PRICE)} + {uzn(IP_ROAD)} − 200) × 30 % = {uzn(ip_duty)} $ × {RATE} = {ip_duty_som} so'm; + {_boj_fee} BKO + {IP_UZIMEI} UzIMEI = {ip_state} so'm. "
          f"Telefon bilan: ({uzn(IP_PRICE)} + {uzn(IP_ROAD)}) × kurs + to'lovlar = {ip_full} so'm. "
          "Apple narxi ($1 199) qidiruv natijalaridan — apple.com da tekshiring. Og'irlik qadoq bilan ≈0,5 kg (minimal to'lov tekshiruvi uchun). "
          "UzIMEI: BHM 440 000 × 20 % = 88 000; 30 kundan keyin × 25 % = 110 000.")

# #obraz — aniq tovarlar (BRIEF.md → #obraz). (do'kon, nom uz, rang uz, narx, eski narx, url, og'irlik kg, rasm uchun tavsif)
OUTFIT_MEN = [
    ("Uniqlo", "PUFFTECH yengil kurtka", "zaytun", 79.90, None, "https://www.uniqlo.com/us/en/products/E479755-000/00", 0.45,
     "a lightweight olive-green quilted puffer jacket with a matte nylon shell, horizontal baffles, stand collar and a hidden front zip under a snap placket, regular hip-length cut, worn open"),
    ("H&M", "Yupqa trikotaj sviter", "bej melanj", 27.99, 42.99, "https://www2.hm.com/en_us/productpage.1172256004.html", 0.35,
     "a soft beige melange fine-knit crew-neck sweater with long sleeves and ribbed neckline, cuffs and hem, regular fit"),
    ("H&M", "Slim-fit paxta chinos", "to'q kulrang", 29.99, None, "https://www2.hm.com/en_us/productpage.1248348007.html", 0.50,
     "dark charcoal-grey slim-fit stretch cotton twill chinos with a tapered leg, diagonal side pockets and a clean flat front"),
    ("H&M", "Chelsi etik", "to'q jigarrang", 29.99, 59.99, "https://www2.hm.com/en_us/productpage.1308844002.html", 1.30,
     "dark chocolate-brown suede-look Chelsea boots with elasticated side panels, a pull loop at the back, rounded toe and a low dark rubber sole"),
    ("Uniqlo", "HEATTECH to'qima shapka", "to'q kulrang", 14.90, None, "https://www.uniqlo.com/us/en/products/E478303-000/00", 0.08,
     "a dark charcoal-grey rib-knit beanie with a snug fold-over cuff"),
]
om_total = round(sum(x[3] for x in OUTFIT_MEN), 2)
om_full = round(sum(x[4] or x[3] for x in OUTFIT_MEN), 2)
om_kg = round(sum(x[6] for x in OUTFIT_MEN), 2)
om_ship = ship(om_kg)
om_local = 3.0
NUM = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
add("2026-10-10-1400", rubric="#obraz", title="Erkaklar: sovuq kunlar obrazi",
    caption="""🧥 <b>Tayyor obraz: sovuq kunlar uchun</b>
<i>Erkaklar uchun · 5 element · Uniqlo + H&amp;M (AQSh)</i>

""" + "\n".join(f'{NUM[i]} <a href="{x[5]}">{x[0].replace("&", "&amp;")} — {x[1]}</a>, {x[2]} — <b>{usd(x[3])}</b>'
                 + (f" <s>{usd(x[4])}</s>" if x[4] else "") for i, x in enumerate(OUTFIT_MEN)) + """

🛒 <b>Tovarlar: """ + usd(om_total) + """</b> (aksiyasiz """ + usd(om_full) + """) — 200 $ normaga sig'adi, boj yo'q

📦 <b>Toshkentgacha</b>
• Yetkazish — ~""" + usd(om_ship) + """ (≈""" + f"{om_kg:.1f}".replace(".", ",") + """ kg)
• Toshkent bo'ylab — ~$3
• <b>Jami ≈ """ + fmt(som(om_total + om_ship + om_local)) + """ so'm</b>

⚠️ Aksiya tugasa summa normadan oshishi mumkin — to'lashdan oldin savatni tekshiring.

💡 Ikkala do'kon ham faqat AQSh ichiga yetkazadi — ekspeditorning AQShdagi manzilidan foydalaning.

<i>Narxlar 05.10.2026 holatiga.</i>
""" + FOOT + "#obraz",
    prompt=outfit_prompt("Sovuq kunlar uchun", [x[7] for x in OUTFIT_MEN],
        "olive, beige, charcoal, dark brown", "5 element · 2 do'kon · " + usd(om_total),
        person="a young man in his late twenties, short dark hair, neat light stubble, calm confident expression"),
    product_url=OUTFIT_MEN[0][5],
    sources=[{"label": f"{x[0]} US — {x[1]}", "url": x[5]} for x in OUTFIT_MEN] + [SPOT_COURIER, SPOT_RATE],
    notes="TASDIQLASHDAN OLDIN: 5 ta havolani brauzerda oching — narx, rang va o'lcham bor-yo'qligini tekshiring "
          "(Uniqlo va H&M saytlari Claude muhitidan ochilmadi, narxlar qidiruv natijalaridan olingan). "
          "Shapka narxi ($14.90) va kurtkaning zaytun rangi AQSh saytida tasdiqlanmagan. Sviter va etik — aksiya narxida. "
          "RASM: ChatGPT'ga 5 ta tovar suratini (do'kon sahifasidan) ham biriktiring — kiyimlar aynan o'xshash chiqadi. "
          f"Og'irliklar taxminiy (jami ≈{om_kg} kg). Hisob: {om_total} + {om_ship} + {om_local} = {round(om_total + om_ship + om_local, 2)} $.")

posts.append(deal("2026-10-10-2000", title="AirTag 2 — 4 talik to'plam", emoji="📍",
    headline="AirTag 2 to'rt talik to'plam — $89", hook="Kalit, sumka va chamadon uchun yangi avlod AirTag:",
    store="Amazon", country="AQSh", pnew=89.00, pold=99.00, weight=0.2,
    uz_store="iSpace", uz_price=1719600, uz_note="4 × 429 900",
    url="https://www.amazon.com/dp/B0GJTXVN9Z",
    note_lines=["⚠️ Faqat iPhone bilan ishlaydi. iSpace'da 4 talik to'plam hozir sotuvda yo'q — solishtiruv 4 ta alohida AirTag bo'yicha."],
    card_title="Apple AirTag 2 — 4 ta",
    notes="iSpace 4-talik to'plam narxi 1 459 900 so'm (sotuvda yo'q). Unga nisbatan tejash kamroq — kerak bo'lsa matnni moslang.",
    sources=[{"label": "9to5toys — AirTag 2 best price, 01.10.2026",
              "url": "https://9to5toys.com/2026/10/01/single-2026-apple-airtag-2-amazon-best-price/"},
             {"label": "MacRumors — AirTag 2 4-pack, 23.09.2026", "url": "https://www.macrumors.com/2026/09/23/airtag-2-4-pack-hits-79-99/"},
             {"label": "iSpace — AirTag 4-pack", "url": "https://ispace.uz/en/product/apple-airtag-4-pack-model-a2937-mfea4ze-a"},
             SPOT_RATE]))

# ============ YAKSHANBA 11-oktabr ============
add("2026-10-11-0900", rubric="#digest", title="Hafta yakuni — 5 ta post",
    caption="""🗂 <b>Hafta yakuni: eng foydali 5 ta post</b>

1️⃣ <a href="{{LINK:2026-10-05-0900}}">Boj 2027-yildan 30 % dan 20 % ga tushadi</a> — qimmat xaridni yanvargacha kutish arziydimi
2️⃣ <a href="{{LINK:2026-10-06-0900}}">Buni buyurtma qilmang</a> — vape, lazer, dron va yana 4 ta taqiq
3️⃣ <a href="{{LINK:2026-10-07-0900}}">Bir oyda ikkita posilka</a> — norma nega oyga beriladi
4️⃣ <a href="{{LINK:2026-10-09-0900}}">Boj qanday hisoblanadi</a> — noutbuk misolida 4 qadam
5️⃣ <a href="{{LINK:2026-10-09-2000}}">Braun Series 9 PRO+</a> — boj bilan ham 2,5 mln so'm tejash

🏷 Hafta chegirmalari: Apple Pencil Pro, Beats Solo 4, LEGO 31134, Belkin Qi2, AirTag 2.

Saqlab qo'ying va do'stlaringizga ulashing — ularga ham kerak bo'ladi 📌

""" + FOOT + "#digest",
    prompt=cover_prompt("#digest", "Hafta yakuni",
        "five small rounded cards stacked in a gentle fan, each with a tiny icon (percent sign, prohibition circle, two parcels, calculator, trophy), with a bookmark ribbon in indigo.",
        sub="Eng foydali 5 ta post", accent="amber (#F59E0B)"),
    notes="Havolalar postlar kanalga chiqqandan keyin avtomatik qo'yiladi (joylanmagan post — havolasiz matn).")

add("2026-10-11-1400", rubric="#firibgar", title="Bojxona nomidan firibgarlik",
    caption="""⚠️ <b>«Posilkangiz bojxonada ushlandi, to'lov qiling» — bu firibgarlik</b>

So'nggi oylarda bojxona nomidan aldash holatlari ko'paydi. Uchta real sxema:

1️⃣ <b>Qo'ng'iroq yoki xabar:</b> «posilka keldi, boj to'lang». Sun'iy intellekt bilan yasalgan soxta yorliq ko'rsatiladi, SMS-kod so'raladi. (Bojxona qo'mitasi ogohlantirishi, 16.02.2026)
2️⃣ <b>Soxta kanallar:</b> «Musodara qilingan tovarlar», «Bojxona admini». Pul begona kartaga o'tkaziladi, keyin sizni bloklashadi. (IIV, 08.01.2026)
3️⃣ <b>«Bojxona orqali arzon tovar»:</b> avval kichik oldindan to'lov, to'liq to'lovdan keyin — blok. Mart oyida 5 kishi ushlangan. (26.03.2026)

✅ <b>Esda tuting</b>
• Bojxona shaxsiy kartaga pul so'ramaydi
• Rasmiy xabar pochta operatori yoki litsenziyali kuryerdan keladi — messenjerdagi notanish akkauntdan emas
• SMS-kodni hech kimga bermang, notanish havolani ochmang

Shubhali xabar oldingizmi? Izohda yozing — tekshirib beramiz 👇

""" + FOOT + "#firibgar",
    prompt=cover_prompt("#firibgar", "Bu firibgarlik!",
        "a smartphone showing an anonymous chat bubble with a parcel icon, a fishing hook dangling toward the screen, and a bold amber warning triangle with an exclamation mark in front.",
        sub="Bojxona kartaga pul so'ramaydi", accent="amber (#F59E0B)"),
    sources=[{"label": "Bojxona qo'mitasi ogohlantirishi, 16.02.2026 (vaib.uz)",
              "url": "https://vaib.uz/2026/02/16/vam-posylka-iz-za-graniczy-tamozhnya-predupredila-o-novoj-sheme-moshennikov/"},
             {"label": "IIV — soxta «bojxona» akkauntlari, 08.01.2026 (spot.uz)", "url": "https://www.spot.uz/ru/2026/01/08/customs-fake"},
             {"label": "Bojxona xodimi qiyofasidagi guruh ushlandi, 26.03.2026 (podrobno.uz)",
              "url": "https://podrobno.uz/cat/proisshestviya/v-uzbekistane-zaderzhali-gruppu-moshennikov-vydavavshikh-sebya-za-sotrudnikov-tamozhni/"}])

posts.append(deal("2026-10-11-2000", title="Sony WH-CH720N — halol hisob: arzimaydi", emoji="🤔",
    headline="Chegirma katta, foyda kichik: Sony WH-CH720N",
    hook="Shovqin bostirishli quloqchin Amazon'da:",
    store="Amazon", country="AQSh", pnew=98.00, pold=179.99, weight=0.5,
    uz_store="Asaxiy", uz_price=1309000, uz_note="oq rang",
    url=None, honest=True, badge="SOLISHTIRUV",
    note_lines=["❌ <b>Xulosa: chetdan olish arzimaydi.</b> Bir necha hafta kutasiz, rasmiy kafolat bo'lmaydi, oylik normaning yarmini band qilasiz — shu farq uchun. Toshkentdan oling.",
                "💡 Katta foiz hali katta tejash degani emas. Doim yakuniy narxni solishtiring."],
    card_title="Sony WH-CH720N",
    notes="Eski narx $179.99 — maqoladagi raqam, Amazon'da tekshirib oling. Post ataylab «arzimaydi» xulosasi bilan — kanalga ishonch beradi.",
    sources=[{"label": "Consequence — October Prime Day headphone deals, 01.10.2026",
              "url": "https://consequence.net/2026/10/best-october-prime-day-headphone-deals-2026/"},
             {"label": "Asaxiy — Sony WH-CH720N", "url": "https://asaxiy.uz/uz/product/besprovodnye-naushniki-sony-wh-ch720n-white"},
             SPOT_RATE]))

# Sony: Amazon havolasi bo'lmagan postga ham rasm uchun do'kon sahifasi
for p in posts:
    if p["id"] == "2026-10-11-2000":
        p["product_url"] = "https://www.amazon.com/dp/B0BS1QCFHX"

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
    if REWORK and target.exists() and json.loads(target.read_text(encoding="utf-8")).get("status") not in ("draft", "needs_input"):
        print(f"{p['id']}  tasdiqlangan/joylangan — qayta yozilmadi")
        continue
    if target.exists() and "--force" not in sys.argv and not REWORK:
        print(f"{p['id']}  mavjud — tegilmadi (panelda tasdiqlangan bo'lishi mumkin)")
        continue
    target.write_text(json.dumps(p, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{p['id']}  {p['rubric']:10} {n:5}  {p_flag}  {p['title']}")

print(f"\n{len(posts)} ta post yozildi.")
if problems:
    print("1024 dan uzun:", problems)
