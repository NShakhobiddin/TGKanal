# Pochtachi

@Pochtam_shopo kanali uchun kontent tizimi. **Server va domen kerak emas** — hammasi bepul GitHub'da ishlaydi:

- **Panel** — `https://nshakhobiddin.github.io/TGKanal/` (shu repo'dan, GitHub Pages): postlar Telegramdagidek ko'rinadi, rasm prompti, rasm yuklash, tasdiqlash. Telefonda ham ochiladi.
- **Jadval** — GitHub Actions har 5 daqiqada tasdiqlangan postlarni kanalga joylaydi (Toshkent 08:00–23:55). GitHub bepul jadvalni kechiktirishi mumkin — aniq vaqt uchun pastdagi «Tashqi jadval» ni sozlang.
- **Postlar va rasmlar** — `NShakhobiddin/TGKanal` repo'sida; bot tokeni — GitHub secret'da.

## Ikkinchi kanal — «AI darslar»
Shu repo ichida ikkinchi kanal yuritiladi: davlat idorasi xodimlariga AI imkoniyatlarini o'rgatadigan o'quv kanali. Hammasi `channels/ai/` papkasida, panelda — alohida oyna (yuqoridagi tugma yoki `https://nshakhobiddin.github.io/TGKanal/#ai`).

- **Haftada 5 post** (dushanba–juma, 08:30): sinov → dars → ustalik → ehtiyot bo'ling → bonus. Har postda bitta yangi bilim va «Olib keting».
- **Rasm tayyor keladi:** kartochkani generator o'zi chizadi — ChatGPT'da rasm chizdirish shart emas. Xohlasangiz panelda boshqasiga almashtirasiz.
- **Mashq fayllari** (Excel va h.k.) postdan keyin alohida xabar bo'lib chiqadi.
- **Ishga tushirish (bir marta):** kanal yarating → botni (@Pochtachiyordamchibot) kanalga admin qiling («Post joylash» huquqi bilan) → `channels/ai/settings.json` da `channel_id` ga kanal manzilini yozing (`@nom`, yopiq kanal bo'lsa `-100…`) → `/yangila` → panelning «AI darslar» oynasida «🔌 Ulanishni tekshirish».
- **Izohlar:** postlarda «javobingizni izohda yozing» deyiladi — kanalga muhokama guruhini ulang (Telegram: kanal → Tahrirlash → Muhokama).
- **Ish tartibi:** `/ai-hafta` → panelda 5 ta postni ko'rib chiqasiz → «📨 Menga sinov» → «✅ Tasdiqlash». Post 08:30 da o'zi chiqadi.
- `channel_id` bo'sh turgan paytda bu kanalga hech narsa joylanmaydi — Pochtachi odatdagidek ishlayveradi.
- Kanal nomini o'zgartirish: `channels.json` → `name`.

## Claude Code bilan ishlash

Papkani Claude Code'da oching va buyruq yozing:

| Buyruq | Nima qiladi |
|---|---|
| `/ornat` | **Birinchi marta.** Repo'larni yaratadi, bot tokenini secret'ga qo'yadi, panelni GitHub Pages'da yoqadi, Telegram ulanishini tekshiradi |
| `/hafta` | Pochtachi: keyingi hafta uchun 21 ta post tayyorlaydi, ko'rsatadi, «ha» desangiz yuboradi |
| `/ai-hafta` | «AI darslar»: keyingi haftaning 5 ta posti, mashq fayllari va kartochkalari |
| `/yangila` | **Asosiy «belgi».** O'zgarishlarni tekshiradi va GitHub'ga yuboradi — panel va jadval o'zi yangilanadi |
| `/holat` | Jadval ishlayaptimi, xatolar, qaysi postlar rasm yoki tasdiq kutyapti |

Izoh qo'shish mumkin: `/yangila tugma rangi o'zgardi`, `/hafta 2026-10-12`.

## /ornat uchun nima kerak
1. **GitHub akkaunt** (sizda bor: NShakhobiddin)
2. **git** va **gh** dasturlari — `/ornat` yo'q bo'lsa o'rnatishni ko'rsatadi
3. Brauzerda bir marta: `gh auth login` va panel uchun token yaratish (`/ornat` qadamma-qadam ko'rsatadi)

## Panelda ish tartibi
1. **🎨 Rasm prompti** → nusxalang (chegirma postida avval tovar suratini do'kon sahifasidan saqlang)
2. ChatGPT'da rasm chizdiring
3. Panelga yuklang: postni bosib **Ctrl+V**, yoki faylni tashlang (PNG avtomatik JPEG'ga siqiladi)
4. **📨 Menga sinov** → 20–60 soniyada Telegram'da o'zingizga keladi
5. **✅ Tasdiqlash** — jadval bo'yicha chiqadi; **🚀 Hozir joylash** — ~1 daqiqada

Har kuni ertalab bot sizga shu kuni tayyor bo'lmagan postlar ro'yxatini yuboradi.

## Bilish kerak
- **Vaqt aniqligi:** 09:00 dagi post odatda 09:05–09:25 da chiqadi (GitHub jadvali kechikishi mumkin). 2 soatdan ko'p kechiksa — «Vaqti o'tdi» bo'ladi va bot sizga yozadi.
- **Limit:** TGKanal ochiq repo — GitHub Actions daqiqalari cheklanmagan. Repo yopiq qilinsa: oyiga 2000 bepul daqiqa, jadval ~1000 daqiqa ishlatadi.
- **Token muddati:** panel tokeni 1 yil. Tugasa panel «Token yaroqsiz» deydi — yangisini yarating.
- **Bir vaqtda bitta joylovchi:** kompyuterdagi eski panelni (`ISHGA_TUSHIRISH.bat`) ishga tushirmang.

## Sozlamalar — `settings.json`
| Kalit | Nima |
|---|---|
| `channel_id` | `@Pochtam_shopo` |
| `admin_username` | `ShNormamatov` — ID'ni avtomatik topish uchun (botga `/start` yozing) |
| `admin_id` | Bot o'zi yozadi |
| `app_url` | Ilova havolasi; bo'sh bo'lsa «ilovada hisoblang» qatori yashiriladi |
| `consult_url` | Pullik maslahat havolasi; bo'sh bo'lsa yashiriladi |
| `late_grace_hours` | Necha soat kechikkan postni hali ham joylash (2) |
| `ui_repo`, `panel_url` | `ui_repo` bo'sh — panel shu repo'dan chiqadi (`pages.yml`); `panel_url` — panel manzili |

Bot tokeni bu yerda **yo'q** — u GitHub → Settings → Secrets → `TELEGRAM_BOT_TOKEN`.

## Tashqi jadval — post aniq vaqtida chiqishi uchun
GitHub bepul jadvali (`schedule`) yuklama paytida soatlab kechikadi yoki ishga tushmay qoladi. Ishonchli yo'l — tashqi bepul xizmat (cron-job.org) har 5 daqiqada `publish.yml` ni chaqiradi:

1. **Token (faqat jadval uchun):** https://github.com/settings/personal-access-tokens/new → nomi `tgkanal-cron`, muddati 1 yil → Only select repositories → `TGKanal` → Repository permissions → **Actions: Read and write** (boshqa hech narsa) → Generate.
2. **cron-job.org** → ro'yxatdan o'ting → Create cronjob:
   - URL: `https://api.github.com/repos/NShakhobiddin/TGKanal/actions/workflows/publish.yml/dispatches`
   - Schedule: every 5 minutes (Asia/Tashkent, 08:00–23:59)
   - Advanced → Request method: **POST**
   - Headers: `Authorization: Bearer <token>`, `Accept: application/vnd.github+json`, `X-GitHub-Api-Version: 2022-11-28`
   - Request body: `{"ref":"main","inputs":{"mode":"due"}}`
3. «Test run» → javob **204** bo'lsa — ishlayapti (GitHub → Actions'da yangi «due» ishi paydo bo'ladi).

Ikkala jadval bir vaqtda ishlasa ham post ikki marta chiqmaydi: joylovchi ishlar navbat bilan bajariladi (`concurrency: publish`).
