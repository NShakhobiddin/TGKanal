---
description: Birinchi marta o'rnatish — GitHub repo, bot tokeni, onlayn panel (server va domen kerak emas)
---

Pochtachi tizimini GitHub'da ishga tushir. Server ham, domen ham kerak emas:
- **yopiq repo `pochtachi`** — postlar, rasmlar, sozlamalar; GitHub Actions jadval bo'yicha Telegram'ga joylaydi
- **ochiq repo `pochtachi-panel`** — faqat panel sahifasi (GitHub Pages): `https://<login>.github.io/pochtachi-panel/`

Muallif bilan o'zbekcha, qisqa gaplash. Har bosqich oxirida bir qatorda nima qilinganini ayt. Muallif o'zi bajarishi kerak bo'lgan ish bo'lsa (brauzerda kirish, token yaratish) — aniq qadamni ber va kut. **Bot tokeni yoki GitHub tokenini hech qachon ekranga chiqarma va chatda so'rama.**

## 0. Talablar
Tekshir: `git --version`, `gh --version`, `gh auth status`.
- `git` yo'q: `winget install --id Git.Git`; `gh` yo'q: `winget install --id GitHub.cli` (so'ng terminalni qayta oching).
- Kirilmagan bo'lsa muallif o'zi bajarsin: `gh auth login` (GitHub.com → HTTPS → brauzer orqali).
- Workflow fayllarini yuborish uchun ruxsat: `gh auth refresh -h github.com -s workflow` (muallif brauzerda tasdiqlaydi).
Hammasi tayyor bo'lmaguncha davom etma.

## 1. Login va sozlamalar
`LOGIN=$(gh api user -q .login)`. `settings.json` dagi `ui_repo` ni `<LOGIN>/pochtachi-panel`, `panel_url` ni `https://<login kichik harfda>.github.io/pochtachi-panel/` ga moslab qo'y.

## 2. Eski paneldan ma'lumot (bo'lsa)
`..\panel\data\posts` yoki `..\pochtachi-panel\data\posts` mavjud bo'lsa, ulardagi postlarni `posts/` dagilar bilan solishtir: holati `draft` dan farq qiladigan (tasdiqlangan, joylangan) yoki `image` maydoni bor postlarni ko'chir, rasmlarini `..\<papka>\data\images\` dan `images/` ga nusxala. `admin_id` (`data/runtime.json` yoki `config.json` da) bo'lsa — `settings.json` ga yoz. Nimani ko'chirganingni sanab ber.

## 3. Yopiq repo
1. `git status` — `config.json`, `.env`, token yoki kalit fayllari ro'yxatda yo'qligiga ishonch hosil qil (`.gitignore`).
2. `python tools/check_posts.py posts` — xato bo'lmasin.
3. Repo yo'q bo'lsa: `git init -b main` → `git add -A` → `git commit -m "Pochtachi — birinchi o'rnatish"` → `gh repo create pochtachi --private --source . --remote origin --push`.

## 4. Bot tokeni → GitHub secret
Tokenni `..\config.json`, `..\panel\config.json` yoki `..\pochtachi-panel\config.json` dan (`bot_token`) ekranga chiqarmasdan uzat:
```
python -c "import json;print(json.load(open(r'..\panel\config.json',encoding='utf-8'))['bot_token'],end='')" | gh secret set TELEGRAM_BOT_TOKEN
```
Hech qaysi faylda bo'lmasa — muallif o'zi terminalda `gh secret set TELEGRAM_BOT_TOKEN` ni ishga tushirib tokenni kiritsin (ekranda ko'rinmaydi).

## 5. Ochiq panel repo va GitHub Pages
1. `gh repo view <LOGIN>/pochtachi-panel --json visibility,isEmpty` — repo bor va **yopiq** bo'lsa yoki ichida eski fayllar (`app.py` va h.k.) bo'lsa, to'xta va muallifdan so'ra: o'chirib qayta yaratish yoki boshqa nom (`pochtachi-ui`) tanlash. Nomni o'zgartirsang `settings.json` ni ham yangila.
2. Yo'q bo'lsa: `gh repo create pochtachi-panel --public --description "Pochtachi kontent paneli — faqat sahifa, ma'lumotlar yo'q"`.
3. `python tools/sync_ui.py` — sahifani yuboradi.
4. Pages: `gh api -X POST repos/<LOGIN>/pochtachi-panel/pages -f "source[branch]=main" -f "source[path]=/"` (409 «already enabled» — joyida).
5. 1–2 daqiqadan keyin `curl -s -o /dev/null -w "%{http_code}" <panel_url>` → `200`.
6. `settings.json` o'zgargan bo'lsa — commit («sozlamalar») va push.

## 6. Telegram ulanishini tekshirish
1. Muallifga ayt: Telegram'da botga `/start` yozsin (sinov xabarlari sizga kelishi uchun) va bot kanalda admin, «Post joylash» huquqi bilan bo'lsin.
2. `gh workflow run publish.yml -f mode=health -f req=ornat`, keyin `gh run watch --exit-status $(gh run list --workflow publish.yml -L 1 --json databaseId -q '.[0].databaseId')`.
3. `git pull` → `state/health.json` ni o'qib natijani jadval qilib ber (bot, kanal, post huquqi, admin ID). Muammo bo'lsa — sababini va yechimini ayt.

## 7. Panel uchun token (muallif brauzerda o'zi qiladi)
Qadamlarni ber, tokenni chatga yozmasligini ayt:
1. https://github.com/settings/personal-access-tokens/new
2. Nomi `pochtachi-panel`, muddati 1 yil
3. Repository access → **Only select repositories** → `pochtachi`
4. Permissions → Repository permissions: **Contents — Read and write**, **Actions — Read and write**
5. Generate → nusxalash → panelni ochish (`panel_url`) → repo `<LOGIN>/pochtachi`, tokenni qo'yib «Kirish»

## 8. Yakun
Muallifga qisqa ayt:
- Panel manzili (`panel_url`) — telefonda ham ochiladi; token shu brauzerda saqlanadi
- Postlar jadval bo'yicha **har 30 daqiqada** tekshiriladi (09:00 dagi post odatda 09:05–09:25 oralig'ida chiqadi); aniq vaqt kerak bo'lsa — «🚀 Hozir joylash»
- **Kompyuterdagi eski panelni yopsin** (`ISHGA_TUSHIRISH.bat` oynasi) — ikkalasi ishlasa post ikki marta chiqadi. Eski `panel` va `pochtachi-panel` papkalari endi kerak emas
- Keyingi buyruqlar: `/hafta`, `/yangila`, `/holat`
