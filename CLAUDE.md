# Pochtachi — Claude Code uchun loyiha qo'llanmasi

Bu repo **@Pochtam_shopo** Telegram kanalining kontent tizimi. Muallif — Shakhobiddin (6 yil bojxona postida xalqaro jo'natmalar bo'yicha ishlagan). Muloqot tili — **o'zbek (lotin)**, qisqa va aniq.

**Server ham, domen ham yo'q.** Hammasi GitHub'da:

```
Claude Code ──git push──▶ repo «TGKanal» (postlar, rasmlar, settings.json)
                              ▲  ▲                     │ GitHub Actions: har 30 daqiqada
     panel (brauzer) ─GitHub API─┘  └─ bot: commit      ▼ tools/publish.py ──▶ Telegram kanal
     https://nshakhobiddin.github.io/TGKanal/  ◀── GitHub Pages (pages.yml: faqat ui/index.html)
```

## Tuzilma
| Yo'l | Nima |
|---|---|
| `posts/<id>.json` | Postlar. Panel ham, bot ham, Claude Code ham shu fayllarni o'zgartiradi |
| `images/` | Panelda yuklangan rasmlar (JPEG'ga siqiladi) |
| `settings.json` | `channel_id`, `admin_username`, `admin_id` (bot o'zi topadi), `app_url`, `consult_url`, `late_grace_hours`, `ui_repo`, `panel_url`. **Maxfiy narsa yo'q** |
| `state/` | Bot natijalari: `health.json`, `last_test.json`, `reminder.json` |
| `ui/index.html` | Panel sahifasi. Push qilinsa `.github/workflows/pages.yml` uni GitHub Pages'ga o'zi joylaydi |
| `tools/publish.py` | Telegram'ga joylovchi (Actions ichida; faqat standart kutubxona) |
| `tools/check_posts.py` | Post fayllarini tekshirish |
| `tools/build_week_*.py` | Haftalik postlar generatori (raqamlar skriptda hisoblanadi) |
| `.github/workflows/publish.yml` | Jadval (`5,35 3-18 * * *` UTC = Toshkent 08:05–23:35) + paneldan chaqiriladigan `test` / `health` |
| `.github/workflows/pages.yml` | Panelni GitHub Pages'ga joylaydi (`ui/**` o'zgarganda) |
| `.github/workflows/check.yml` | Claude Code yuborgan postlarni tekshiradi (`panel:` / `bot:` commitlari o'tkazib yuboriladi) |
| `BRIEF.md` | **Kontent qoidalari** — rubrikalar, jadval, uslub, tekshirilgan bojxona faktlari. Post yozishdan oldin albatta o'qing |

Maxfiylar faqat GitHub secrets'da: `TELEGRAM_BOT_TOKEN`. Panel tokeni (fine-grained PAT) faqat muallif brauzerida.

## Oltin qoidalar
1. **Avval `git pull --rebase`.** Panel va bot doim commit qiladi. Post faylida to'qnashuv bo'lsa — holat maydonlari (`status`, `image`, `message_id`, `published_at`, `published_by`, `error`, `publish_now`) GitHub'dagidek qoladi.
2. **Maxfiylar git'ga tushmaydi:** `config.json`, `.env`, kalitlar, tokenlar. Bot tokeni chatga, log'ga yoki faylga chiqarilmasin.
3. **Joylangan (`published`) postni o'zgartirmang.** Mavjud postni qayta generatsiya qilmang — generator faqat yangi fayllarni yozadi.
4. **Qonunchilik faqat lex.uz dan** (qo'shimcha manba — aeroinfo.uz). Hujjat turi, raqami, sanasi, bandi bilan. Tasdiqlanmagan norma postga qo'yilmaydi.
5. **Raqamlar qo'lda yozilmaydi** — generator skriptida hisoblanadi. Kurs har safar CBU'dan (spot.uz/oz/currency) yangilanadi.
6. **`#keys` keyslarini o'ylab topmang** — material muallifdan keladi. Bo'lmasa `status: "needs_input"` bilan shablon.
7. Rasm bilan caption **≤ 1024** ko'rinadigan belgi.
8. Commit xabarini `panel:` yoki `bot:` bilan boshlamang (ular tekshiruvdan o'tkazib yuboriladi).
9. Kanalga faqat GitHub Actions joylaydi. Eski kompyuter paneli (`..\panel`, `..\pochtachi-panel`) ishlatilmaydi — ishga tushirmang.

## Post JSON
```json
{"id":"2026-10-12-2000","rubric":"#narx","title":"Panel uchun qisqa nom",
 "scheduled_at":"2026-10-12T20:00:00+05:00","caption":"Telegram HTML","prompt":"GPT Image 2 prompti",
 "product_url":"https://...","notes":"faqat muallif uchun eslatma","sources":[{"label":"...","url":"..."}],
 "status":"draft"}
```
Holatlar: `draft` → (rasm) → `approved` → bot → `published`; `needs_input`, `failed` (+`error`), `overdue` (2 soatdan ko'p kechikdi). `publish_now: true` — paneldagi «Hozir joylash».
Tokenlar: `{{APP_URL}}`, `{{CONSULT_URL}}` (settings.json da bo'sh bo'lsa qator yashiriladi), `<a href="{{LINK:<post_id>}}">matn</a>` — joylangan postga havola.

## Buyruqlar
- `/ornat` — birinchi marta: repo'lar, bot tokeni secret'ga, GitHub Pages, ulanish tekshiruvi
- `/yangila [izoh]` — tekshirib GitHub'ga yuborish (kerak bo'lsa panel sahifasini ham)
- `/hafta [sana]` — keyingi hafta uchun 21 ta post
- `/holat` — jadval ishlari, xatolar, postlar holati, limitlar

## Foydali buyruqlar
- Qo'lda jadval: `gh workflow run publish.yml`
- Ulanish tekshiruvi: `gh workflow run publish.yml -f mode=health -f req=cli`
- Oxirgi ishlar: `gh run list --workflow publish.yml -L 10`
- Lokal sinov (Telegram'siz): `NO_GIT=1 TG_API_BASE=http://127.0.0.1:8901 TELEGRAM_BOT_TOKEN=x MODE=due python tools/publish.py`
