---
description: «AI darslar» kanali uchun keyingi haftaning 5 ta postini tayyorlash (mashq fayllari + kartochkalar)
argument-hint: [hafta raqami] [dushanba sanasi, masalan 2 2026-10-19]
---

«AI darslar» kanali (`channels/ai/`) uchun bir haftalik to'plamni tayyorla: 5 ta post (dushanba–juma), mashq fayllari va kartochka rasmlari. Argumentlar: $ARGUMENTS
- Hafta raqami berilmasa — `channels/ai/calendar.json` dagi birinchi `"holat": "reja"` hafta.
- Sana berilmasa — `channels/ai/posts/` dagi eng oxirgi `scheduled_at` dan keyingi dushanba.

Bu Pochtachi `/hafta` sidan alohida buyruq: boshqa papka, boshqa brif, boshqa generator.

## 0. Yangilab ol
`git pull --rebase origin main`.

## 1. Qoidalarni o'qi
- `channels/ai/BRIEF.md` — to'liq: asosiy qoida (har postda yangi bilim + «Olib keting»), haftalik ritm, post tuzilishi, xavfsizlik qoidalari, kartochka turlari.
- `channels/ai/calendar.json` — shu haftaning mavzusi (imkoniyat) va bonusi.
- `tools/ai_week_01.py` — namuna: ma'lumot generatori, javoblarni hisoblash, 5 ta post. `tools/ai_lib.py` boshidagi izoh — `Week`, `W.file`, `W.post`, kartochka turlari.
- Oldingi haftalar postlari (`channels/ai/posts/`) — mavzu va misollar takrorlanmasin, o'tilgan narsaga tayanish mumkin.

## 2. Izlan
- Hafta mavzusidagi imkoniyat **bugun** qaysi vositalarda bor (kamida 2–3 ta: ChatGPT, Claude, Gemini va h.k.) va bepul tarifda ishlaydimi — faqat rasmiy yordam sahifalaridan. Sanasi bilan `sources` ga (`CHECKED`). Tasdiqlanmagani — `notes` ga «o'zingiz sinab ko'ring».
- Imkoniyatni o'zing sinab ko'r: mashq faylida so'rovlar zanjiri haqiqatan natija beradimi, qayerda adashadi (payshanba posti uchun material).
- O'quvchi bilmagan narsa nima? Har post uchun bitta «yangi bilim»ni oldindan yozib ol. Umumiy gap chiqsa — chuqurlashtir.

## 3. Haftani loyihala
Bitta mashq to'plami — butun hafta shu ustida:
| Kun | Rukn | Nima |
|---|---|---|
| Dushanba | `#sinov` | Vaziyat + mashq fayli + «qo'lda sinab ko'ring» |
| Seshanba | `#dars` | 4–6 qadamli usul, har qadamda `pre()` so'rov va sababi; sinov javoblari spoyler ostida |
| Chorshanba | `#ustalik` | Shu imkoniyatning boshqa qo'llanilishi yoki kam biladigan tomoni |
| Payshanba | `#ehtiyot` | Qayerda adashadi + nazorat savollari |
| Juma | `#bonus` | `calendar.json` dagi bonus — shaxsiy hayotda, namunaviy fayl bilan |

Mashq fayli: o'ylab topilgan, idora hayotiga yaqin, ichida ataylab qo'yilgan «topilma»lar (aniq son bilan, `assert` bilan tekshirilgan).

## 4. Skriptni yoz
- `tools/ai_week_01.py` ni nusxa qilib `tools/ai_week_<NN>.py` yarat. `Week(N, start="<dushanba>", theme="…")`, `CHECKED` sanasini yangila.
- Ma'lumot `random.Random(stable_seed("hNN", "nom"))` bilan — har safar bir xil chiqsin.
- **Raqamlarni qo'lda yozma** — post, spoyler va kartochkadagi har bir son ma'lumotdan hisoblansin.
- Har post: `head`, `body`, `new` (yangi bilim), `take` (olib keting), `card` (kartochka), kerak bo'lsa `attach`, `notes`, `sources`, `scene` (ixtiyoriy AI rasm uchun).
- Kerak bo'lsa: `pip install pillow openpyxl`.

## 5. Yarat va tekshir
1. `python tools/ai_week_<NN>.py` — fayllar, postlar, kartochkalar. Skript mavjud postga tegmaydi (qoralamani qayta yozish: `--rework`).
2. `python tools/check_posts.py` — xato bo'lmasin.
3. **Kartochkalarni och va ko'r** (`channels/ai/images/*-auto.png`): matn chetga chiqmagan, ustma-ust tushmagan, sarlavha chiroyli bo'lingan bo'lsin. Yomon bo'lsa — `card` dagi `title` ni qisqartir va `--rework`.
4. **Fayllarni mustaqil qayta hisobla** (pandas bilan fayldan o'qib): skript chiqargan javoblar bilan mos kelsin.
5. Formulali fayl bo'lsa — LibreOffice bilan qayta hisoblat yoki muallifga «Excelda bir ochib saqlang» deb ayt.

## 6. Muallifga ko'rsat
Qisqa jadval: kun, rukn, sarlavha, yangi bilim, olib ketadigani. Alohida: tasdiqlab bo'lmagan narsalar. Kartochkalarni ko'rsat. So'ra: «GitHub'ga yuboraymi?»

## 7. Yuborish
«Ha» desa: `calendar.json` da shu haftaga `"holat": "tayyor"` va `"skript"` yoz, so'ng `/yangila` qadamlari (commit: «AI darslar: N-hafta»). Postlar panelning «AI darslar» oynasida ko'rinadi: muallif ko'rib chiqadi, tasdiqlaydi — jadval bo'yicha chiqadi.

## Boshqa haftaga ko'chirish
`python tools/ai_week_<NN>.py --start=2026-10-26` — shu haftaning eski qoralamalari o'chiriladi, yangi sanalar bilan qayta yoziladi. Tasdiqlangan yoki joylangan postlarga tegilmaydi.
