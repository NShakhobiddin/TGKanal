---
description: Jadval ishlayaptimi, xatolar, postlar holati va GitHub limitlari
---

Pochtachi tizimining holatini tekshir (hech narsani o'zgartirmasdan):

1. `git pull --rebase origin main` (lokal o'zgarish bo'lsa — faqat `git fetch` va `origin/main` dan o'qi).
2. **Jadval:** `gh run list --workflow publish.yml -L 15 --json status,conclusion,displayTitle,createdAt,event`. Oxirgi muvaffaqiyatli jadval ishi qachon bo'lgan? Ketma-ket xatolar bormi? Xato bo'lsa — `gh run view <id> --log-failed` dan sababini top. Jadval o'chirilganmi: `gh workflow view publish.yml` (disabled bo'lsa — `gh workflow enable publish.yml` ni taklif qil, o'zing yoqma).
3. **Postlar:** `posts/*.json` dan holatlar soni (draft, needs_input, approved, published, failed, overdue). Alohida ro'yxat:
   - keyingi 24 soatda chiqishi kerak, lekin rasmsiz yoki tasdiqlanmagan postlar
   - `failed` (xato matni bilan) va `overdue` postlar
   - `publish_now: true` turib qolgan postlar
4. **Telegram:** `state/health.json` — oxirgi tekshiruv sanasi, bot, kanal, post huquqi, admin ID.
5. **Limitlar:** repo hajmi `gh repo view --json diskUsage -q .diskUsage` (KB). Yopiq repo uchun bepul Actions — oyiga 2000 daqiqa; jadval oyiga ~1000 daqiqa ishlatadi. `gh api /users/$(gh api user -q .login)/settings/billing/actions` ishlasa — sarflangan daqiqalarni ko'rsat (ishlamasa o'tkazib yubor).
6. **Panel:** `settings.json` → `panel_url`; `curl -s -o /dev/null -w "%{http_code}" <panel_url>` → 200 bo'lishi kerak.

Natijani qisqa jadval qilib ber: jadval ishlari, postlar holati, diqqat talab qiladigan postlar, limitlar. Muammo bo'lsa — sababini va yechimini taklif qil, muallif ruxsatisiz hech narsani o'zgartirma.
