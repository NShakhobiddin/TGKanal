---
description: O'zgarishlarni tekshirib GitHub'ga yuborish — panel va jadval o'zi yangilanadi
argument-hint: [qisqa izoh]
---

Pochtachi repo'sini yangila. Izoh: $ARGUMENTS

Qadamlar (har birini bajar, natijani qisqa ayt):

1. **Avval tortib ol.** `git pull --rebase origin main` — panel va bot doim commit qilib turadi (tasdiq, rasm, joylandi). Lokal o'zgarishlar bo'lsa `git stash` → pull → `git stash pop`. Post faylida to'qnashuv bo'lsa: `status`, `image`, `message_id`, `published_at`, `published_by`, `error`, `publish_now` maydonlari **GitHub'dagi holatda** qoladi, faqat matn maydonlari (caption, prompt, title, notes, sources) lokaldan olinadi.
2. **Tekshiruv.** `python tools/check_posts.py` (hamma kanal: Pochtachi va `channels/ai`). XATO bo'lsa — tuzat yoki to'xtab muallifga ayt. Ogohlantirishlarni qisqacha sanab o't.
3. **Joylangan postlar.** `git diff --cached` va `git diff` da `"status": "published"` bo'lgan post o'zgargan bo'lsa — o'sha o'zgarishni bekor qil (kanaldagi post o'zgarmaydi) va muallifga ayt.
4. **Maxfiylar.** `git status --porcelain` da `config.json`, `.env`, kalit yoki token o'xshash fayl bo'lsa — TO'XTA. Hech qachon commit qilma.
5. **Commit va push.** `git add -A`, xabar: muallif izohi yoki bir qatorda o'zbekcha mazmun («12–18-oktabr postlari qo'shildi»). `panel:` yoki `bot:` bilan boshlama. O'zgarish bo'lmasa — «Yangilanadigan narsa yo'q» deb to'xta. `git push origin main` (rad etilsa — 1-qadamni takrorla).
6. **Panel sahifasi.** `ui/index.html` o'zgargan bo'lsa — push'dan keyin `pages.yml` uni o'zi joylaydi (`gh run list --workflow pages.yml -L 1` bilan tekshir). `settings.json` da `ui_repo` to'ldirilgan bo'lsa (alohida panel repo) — `python tools/sync_ui.py`.
7. **Tekshiruv natijasi.** `posts/`, `channels/` yoki `tools/` o'zgargan bo'lsa: `gh run watch --exit-status $(gh run list --workflow check.yml -L 1 --json databaseId -q '.[0].databaseId')`. Xato bo'lsa `gh run view --log-failed` → tuzat → qayta push (eng ko'pi 2 marta).
8. **Yakun.** 1–2 qator: nima yangilandi, panel manzili (`settings.json` → `panel_url`).
