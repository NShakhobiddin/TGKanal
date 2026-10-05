---
description: Keyingi hafta uchun 21 ta post tayyorlash (izlanish + matn + rasm promptlari)
argument-hint: [dushanba sanasi, masalan 2026-10-12]
---

Pochtachi kanali uchun keyingi haftaning 21 ta postini tayyorla. Boshlanish sanasi: $ARGUMENTS (bo'sh bo'lsa — `posts/` dagi eng oxirgi `scheduled_at` dan keyingi dushanba).

## 0. Yangilab ol
`git pull --rebase origin main` — panelda tasdiqlangan/joylangan holatlar kelsin.

## 1. Qoidalarni o'qi
`BRIEF.md` ni to'liq o'qi: rubrikalar, haftalik jadval (har kun 09:00 / 14:00 / 20:00), har rubrika formati, uslub, aniqlik qoidalari va tekshirilgan bojxona faktlari. `CLAUDE.md` dagi oltin qoidalarga amal qil. Oxirgi 2 haftaning postlarini (`posts/`) ko'r — tovar va mavzular takrorlanmasin.

## 2. Izlan
- **Kurs:** `state/rate.json` — Markaziy bank (cbu.uz), `rate.yml` avtomatik yangilaydi. Eskirgan bo'lsa: `gh workflow run rate.yml`, so'ng `git pull`.
- **#narx (7 ta):** amaldagi chegirmalar (9to5toys, macrumors, tomsguide, techradar, slickdeals va h.k.) + O'zbekistondagi xuddi shu model narxi (texnomart.uz, olcha.uz `/ru/` sahifalari, asaxiy.uz, ispace.uz, uzum.uz). Yengil (≈1 kg gacha) va oylik normaga sig'adigan tovarlarni afzal ko'r; bittasi normadan oshib, boj bilan ham foydali bo'lishi mumkin. Chetdan olish arzimasa — buni ochiq yozadigan halol post ham yaxshi. AQSh 120V maishiy texnikasini tanlama.
- **Qonunchilik:** faqat lex.uz (hujjat turi, raqami, sanasi, bandi) yoki aeroinfo.uz. Yangilik saytlari faqat xabarni topish uchun.
- **#keys:** keysni o'zing tuz — bojxona amaliyotidagi tipik vaziyat (BRIEF.md → Aniqlik qoidalari): realistik tovar va qiymat, muammo, yechim qadamlari, lex.uz asosi. Ism, raqam, sana yo'q; oxirida «tipik vaziyatlar asosida tuzilgan» izohi. Status — `draft`.
- **#obraz:** har 5 element — aniq tovar sahifasi (kategoriya emas): nomi, rangi, narxi sahifadan tekshirilgan. Rasm prompti — `outfit_prompt()`: odam aynan shu kiyimlarni kiyib turibdi; har kiyimni sahifadagidek aniq tasvirla.
- Topa olmagan yoki tasdiqlay olmagan narsangni yozib bor — postga qo'yma.

Ko'p manbali izlanishni tezlashtirish uchun parallel subagentlardan foydalanishing mumkin (elektronika chegirmalari, maishiy/bolalar chegirmalari, lex.uz faktlari, obraz va topilma).

## 3. Postlarni yarat
- `tools/` dagi eng oxirgi `build_week_*.py` ni nusxa qilib `tools/build_week_<YYYY_MM_DD>.py` yarat: `RATE`, `RATE_TXT`, sanalar va postlarni yangila. Yordamchi funksiyalarni (`deal()`, `cover_prompt()`, `outfit_prompt()`, `ship()`, `som()`) qayta ishlat — **raqamlarni qo'lda yozma**.
- Skript **faqat yangi** fayllarni yozsin: `posts/<id>.json` allaqachon bo'lsa — tegma (u panelda tasdiqlangan yoki rasm yuklangan bo'lishi mumkin).
- Har post: Telegram HTML caption (rasm bilan ≤ 1024 belgi), GPT Image 2 prompti (chegirmada — biriktirilgan tovar surati bilan kartochka; boshqalarida — muqova), `product_url`, `sources`, `notes`.
- Yakshanba `#digest` da `{{LINK:<post_id>}}` havolalari bilan haftaning 5 ta eng foydali postini ko'rsat.
- Skriptni ishga tushir, so'ng `python tools/check_posts.py posts`. Xatolarni tuzat.

## 4. Muallifga ko'rsat
Qisqa jadval: kun, vaqt, rubrika, sarlavha, asosiy raqam (masalan «tejash 779 000 so'm»). Alohida: tasdiqlab bo'lmagan narsalar va muallifdan kerakli ma'lumot. So'ra: «GitHub'ga yuboraymi?»

## 5. Yuborish
«Ha» desa — `/yangila` qadamlarini bajar (commit: «<sana> haftasi postlari»). Postlar panelda darhol ko'rinadi; muallif rasm yuklab tasdiqlaydi.
