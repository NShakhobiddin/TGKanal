# «AI darslar» kanali — kontent brifi

Bu hujjat `/ai-hafta` buyrug'i va haftalik post tayyorlaydigan seanslar uchun. Post yozishdan oldin to'liq o'qing.
Kanal nomi hozircha ishchi nom — muallif o'zgartirsa: `channels.json` (`name`) va `channels/ai/settings.json` (`channel_id`).

## Kanal haqida
- **Auditoriya:** davlat idoralari xodimlari. Birinchi o'quvchilar — bojxonadagi hamkasblar (kichik pilot).
- **Maqsad:** AI dan faqat savol-javob uchun emas, ish vazifasini bajarish uchun foydalanishni o'rgatish: fayl tahlili, hujjat yaratish, solishtirish, izlanish, avtomatlashtirish.
- **Model:** avval bepul, keyin pullik chuqur modullar. Hozir hamma narsa bepul.
- **Muallif:** Shakhobiddin — bojxona xodimi va AI bo'yicha amaliyotchi. Kanal **shaxsiy loyiha**: idora nomidan gapirmaydi, real xizmat hujjatlari va ichki ma'lumot ishlatilmaydi.
- Pochtachi kanalidan (repo ildizi) butunlay alohida: boshqa auditoriya, boshqa uslub, boshqa qoidalar.

## Asosiy qoida (muallif talabi)
1. **Har postda bitta yangi bilim** — o'quvchi oldin bilmagan narsa. «AI 7 ish qiladi» kabi umumiy gap post emas.
2. **Har postda «Olib keting»** — o'sha kuni ishlatsa bo'ladigan narsa: mashq fayli, so'rovlar zanjiri, shablon, nazorat kartochkasi.
3. **To'liq ish usuli:** o'quvchi postni o'qib, 10 daqiqada o'zi takrorlay olsin va ishga yaroqli natija olsin. Bitta so'rov emas — qadamlar va har qadamning *sababi*.
4. **Asbobni emas, vazifani o'rgating:** «ChatGPT nima» emas, «500 qatorli reestrdan 10 daqiqada ma'lumotnoma».

`tools/ai_lib.py` 1- va 2-bandni majburlaydi: `new` (yangi bilim) yoki `take` (olib keting) bo'lmasa post yozilmaydi.

## Haftalik ritm
Har hafta — **bitta imkoniyat** (`calendar.json`), dushanbadan jumagacha 5 ta post, vaqti — `settings.json` → `post_time`.
Butun hafta **bitta mashq to'plami** ustida ishlaydi: dushanba kuni berilgan fayl keyingi darslarda ham ishlatiladi.

| Kun | Rukn | Teg | Vazifasi |
|---|---|---|---|
| Dushanba | Hafta sinovi | `#sinov` | Vazifa va mashq fayli: «qo'lda qancha vaqt ketadi?». Qiziqtiradi, ulashiladi |
| Seshanba | Dars | `#dars` | Qadam-baqadam usul: 4–6 so'rov, har birining sababi. Sinov javoblari spoyler ostida |
| Chorshanba | Ustalik | `#ustalik` | Shu imkoniyatning kam biladigan tomoni, ishdagi boshqa vaziyat |
| Payshanba | Ehtiyot bo'ling | `#ehtiyot` | Qayerda adashadi va qanday tekshiriladi. Nazorat savollari |
| Juma | Bonus | `#bonus` | Shu hafta mahorati shaxsiy hayotda: byudjet, sog'liq, oila, rivojlanish |

Oylik postlar (keyin qo'shiladi): `#mundarija` (oy boshida, mahkamlanadi), `#savol` (izohlardagi savollarga javob), `#natija` (o'quvchi natijasi), `#elon`.

## Post tuzilishi
```
{emoji} <b>Sarlavha</b>

Vaziyat (1–3 jumla) → qadamlar: <b>N-qadam</b> + <pre>so'rov</pre> + <i>Nega:</i> sababi
🔑 Javoblar — <tg-spoiler>…</tg-spoiler> ostida (o'quvchi avval o'zi sinab ko'radi)

💡 <b>Bugungi yangi bilim:</b> …
🎁 <b>Olib keting:</b> …

➖➖➖
{{CHANNEL}}  #rukn
```
- **So'rovlar `<pre>` ichida** — Telegramda bosilsa nusxalanadi. Bir qatorli savollar — `<code>`.
- **Javoblar spoyler ostida** — raqamlar mashq faylidan skriptda hisoblanadi.
- Matn ≤ 1024 belgi bo'lsa rasm bilan bitta xabar bo'lib chiqadi; uzunroq bo'lsa (dars postlari) — rasm, keyin matn. 4096 dan oshmasin: oshsa ikki postga bo'ling.
- Biriktirilgan fayllar postdan keyin alohida xabar bo'lib chiqadi — matnda «keyingi xabarda» deb yozing.

## Uslub
- O'zbek lotin, «siz», hurmat bilan va aniq. Rasmiyatchiliksiz, lekin jiddiy: o'quvchi — band mutaxassis.
- Qisqa xatboshi, bitta post — bitta fikr. Emoji — faqat bo'lim belgisi sifatida, har xatboshida emas.
- Atamalar: so'rov (prompt), yordamchi (assistant), fayl yuklash, kod bilan hisoblash, tarif. Inglizcha atama birinchi marta qavsda beriladi.
- Maqtov va va'da yo'q («inqilob», «5 daqiqada mutaxassis bo'ling»). Faqat ko'rsatib bo'ladigan natija.
- Misol vaziyatlar idora hayotidan: ma'lumotnoma, reestr, inventarizatsiya, murojaatlar, yig'ilish bayoni, taqdimot.

## Xavfsizlik va halollik qoidalari — buzilmaydi
- **Xizmat ma'lumoti AI ga kiritilmaydi.** Har bir amaliy postda eslatma bo'lsin: xizmatda foydalanish uchun hujjatlar, ichki yozishmalar, fuqarolarning shaxsiy ma'lumotlari yuklanmaydi. Muqobil yo'l ko'rsatiladi: ustun nomlari + o'ylab topilgan 2–3 qator berib, formula yoki makros so'rash (hisob o'z kompyuterida bajariladi).
- **Mashq fayllari faqat o'ylab topilgan** va fayl ichida shunday deb yozilgan. Haqiqiy idora, shaxs, hujjat raqami yo'q. Odam o'rniga kod (`F-10482`), idora — «Namuna agentligi».
- **Vositalar reklama qilinmaydi.** Imkoniyat kamida 2–3 vositada ko'rsatiladi (ChatGPT, Claude, Gemini va h.k.), bittasi «eng yaxshi» deyilmaydi.
- **Bepul/pullik holati tez o'zgaradi.** Har hafta rasmiy yordam sahifasidan tekshiriladi, sana bilan `sources` ga yoziladi (`CHECKED`). Tasdiqlanmagan narsa `notes` da «o'zingiz sinab ko'ring» deb belgilanadi. Aniq limit raqami postga faqat rasmiy sahifada bo'lsa qo'yiladi.
- **AI xato qiladi** — har hafta payshanba posti shunga bag'ishlangan. «AI to'g'ri hisoblaydi» emas, «qanday tekshiriladi».
- **Sog'liq (bonus):** AI tashxis qo'ymaydi, dori tayinlamaydi — faqat tushunish va shifokorga savol tayyorlash. **Moliya:** maslahat emas, o'z ma'lumotini ko'rish usuli.
- **Shaxsiy fayl yuklashdan oldin** karta raqami, F.I.Sh., hisob raqami, pasport ma'lumoti o'chiriladi — bonus postlarida eslatiladi.
- Qonunchilikka havola kerak bo'lsa — faqat lex.uz (hujjat turi, raqami, sanasi, bandi), Pochtachi brifidagi kabi.

## Aniqlik
- **Raqamlar qo'lda yozilmaydi.** Postdagi har bir son haftalik skriptda mashq ma'lumotidan hisoblanadi (`A[...]`, `INV[...]`).
- Skript oxirida javoblar chiqadi. Push'dan oldin fayllarni **mustaqil qayta hisoblab** tekshiring (pandas bilan fayldan o'qib) — post, spoyler va kartochkadagi raqamlar mos kelsin.
- Mashq fayliga yashirilgan «muammolar» tasodifga bog'liq bo'lmasin: aniq son bilan beriladi va `assert` bilan tekshiriladi.

## Rasm: kartochka avtomatik chiziladi
Rasmni AI generator emas, **kod chizadi** (`tools/ai_lib.py` → `Card`, Pillow, 1080×1350): o'zbekcha matn buzilmaydi, uslub har doim bir xil. Rasm `images/<id>-auto.png` ga yoziladi, postda `image_auto: true`.
Muallif panelda boshqa rasm yuklasa — `image_auto` o'chadi va generator unga tegmaydi. Har postda ixtiyoriy GPT prompti ham bor (`scene`).

**Uslub — «blanka»:** qog'oz rangidagi fon, to'q siyoh, bitta rang — rukn «muhri». Tepada rukn va «N-HAFTA · k/5», pastda «OLIB KETING».
Shriftlar (`tools/fonts/`, OFL): Bricolage Grotesque — sarlavha, Instrument Sans — matn, JetBrains Mono — so'rov, ma'lumot, kirill yozuv.

| Rukn | Rang | Odatiy kartochka |
|---|---|---|
| `#sinov` | ko'k `#2F5BEA` | `stats` — katta raqamlar + nuqtalar matritsasi (har nuqta — bir qator) |
| `#dars` | yashil `#0B8457` | `chain` — qadamlar zanjiri |
| `#ustalik` | binafsha `#6D3FD0` | `pairs` — ikki ro'yxat va bog'lovchi chiziqlar; yoki `prompt` |
| `#ehtiyot` | qizil `#D7263D` | `checks` — tuzoq va nazorat savoli |
| `#bonus` | sariq-to'q `#D97706` | `bars` — ustunlar + yirik xulosa |

Boshqa turlar: `bullets` (oddiy ro'yxat), `prompt` (terminal uslubidagi so'rov). Yangi tur kerak bo'lsa — `Card` ga `body_…` usuli qo'shiladi.
Qoidalar: kartochkada **ko'pi bilan ~25 so'z**; sarlavha 2–3 qatorga sig'sin; raqam va misollar haqiqiy mashq faylidan; boshqa dastur interfeysiga o'xshatilgan soxta skrinshot chizilmaydi. Chizgandan keyin **rasmni ochib ko'ring** — matn chetga chiqmagan, ustma-ust tushmagan bo'lsin.

## Mashq fayllari
- Joyi: `channels/ai/files/hNN/` (`W.file(...)`). Nomlar: lotin harflari, raqam, `_ - .`.
- Fayl **faqat yo'q bo'lsa** yaratiladi (qayta yaratish: `--force-files`). Ma'lumot `stable_seed` bilan — har safar bir xil.
- Excel: Arial, sarlavha qatori, birinchi qatorda «o'quv mashqi, o'ylab topilgan» yozuvi.
- Formulali fayl (shablon) openpyxl'dan keyin hisoblangan qiymatsiz chiqadi — LibreOffice bilan qayta hisoblating yoki Excelda ochib saqlang, aks holda Telegram ko'rinishida va AI vositalarida formulalar bo'sh ko'rinadi.
- Fayllar kichik bo'lsin (odatda < 1 MB; Telegram bot chegarasi 50 MB).

## Post JSON — Pochtachidan farqi
Umumiy maydonlar — repo `CLAUDE.md` da. Qo'shimcha:
```json
{"attachments": [{"file": "files/h01/murojaatlar_2025.xlsx", "caption": "Telegram HTML", "name": "ixtiyoriy nom"}],
 "image": "2026-10-12-0830-auto.png", "image_auto": true, "long_ok": true, "week": 1}
```
- `attachments` — postdan keyin hujjat qilib yuboriladi (javob sifatida). Yuborilgach har biriga `message_id` yoziladi; xato bo'lsa 3 marta qayta uriniladi (`attach_error`).
- `{{CHANNEL}}` — kanal manzili (`settings.json` → `channel_id`, `@nom`). Yopiq kanalda (`-100…`) bo'sh qoladi.
- `long_ok` — matn 1024 dan uzun bo'lishi ataylab (tekshiruv ogohlantirmaydi).
- `prompt` bo'sh bo'lishi mumkin (kartochka avtomatik).

## Sozlamalar — `channels/ai/settings.json`
| Kalit | Nima |
|---|---|
| `channel_id` | Kanal manzili: `@nom` (ochiq) yoki `-100…` (yopiq). **Bo'sh bo'lsa — hech narsa joylanmaydi** |
| `post_time` | Post vaqti, Toshkent (`08:30`) |
| `late_grace_hours` | Necha soat kechikkan post hali joylanadi |
| `rubrics` | Ruxsat etilgan ruknlar (tekshiruv uchun) |

`admin_id`, `admin_username`, `panel_url` — asosiy `settings.json` dan olinadi. Bot — Pochtachi bilan bitta (`TELEGRAM_BOT_TOKEN`); u yangi kanalda ham admin bo'lishi kerak.

## 12 haftalik reja
`calendar.json` — har hafta: mavzu (imkoniyat), bonus, holat. 1-hafta tayyor: `tools/ai_week_01.py` — keyingi haftalar uchun namuna.
