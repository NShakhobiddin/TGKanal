# Pochtachi

@Pochtachi_shopo kanali uchun kontent tizimi. **Server va domen kerak emas** — hammasi bepul GitHub'da ishlaydi:

- **Panel** — `https://<login>.github.io/pochtachi-panel/`: postlar Telegramdagidek ko'rinadi, rasm prompti, rasm yuklash, tasdiqlash. Telefonda ham ochiladi.
- **Jadval** — GitHub Actions har 30 daqiqada tasdiqlangan postlarni kanalga joylaydi (Toshkent 08:05–23:35).
- **Postlar va rasmlar** — yopiq repo'da; bot tokeni — GitHub secret'da.

## Claude Code bilan ishlash

Papkani Claude Code'da oching va buyruq yozing:

| Buyruq | Nima qiladi |
|---|---|
| `/ornat` | **Birinchi marta.** Repo'larni yaratadi, bot tokenini secret'ga qo'yadi, panelni GitHub Pages'da yoqadi, Telegram ulanishini tekshiradi |
| `/hafta` | Keyingi hafta uchun 21 ta post tayyorlaydi, ko'rsatadi, «ha» desangiz yuboradi |
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
- **Limit:** yopiq repo uchun oyiga 2000 bepul daqiqa; jadval ~1000 daqiqa ishlatadi.
- **Token muddati:** panel tokeni 1 yil. Tugasa panel «Token yaroqsiz» deydi — yangisini yarating.
- **Bir vaqtda bitta joylovchi:** kompyuterdagi eski panelni (`ISHGA_TUSHIRISH.bat`) ishga tushirmang.

## Sozlamalar — `settings.json`
| Kalit | Nima |
|---|---|
| `channel_id` | `@Pochtachi_shopo` |
| `admin_username` | `ShNormamatov` — ID'ni avtomatik topish uchun (botga `/start` yozing) |
| `admin_id` | Bot o'zi yozadi |
| `app_url` | Ilova havolasi; bo'sh bo'lsa «ilovada hisoblang» qatori yashiriladi |
| `consult_url` | Pullik maslahat havolasi; bo'sh bo'lsa yashiriladi |
| `late_grace_hours` | Necha soat kechikkan postni hali ham joylash (2) |
| `ui_repo`, `panel_url` | Ochiq panel repo va manzili |

Bot tokeni bu yerda **yo'q** — u GitHub → Settings → Secrets → `TELEGRAM_BOT_TOKEN`.
