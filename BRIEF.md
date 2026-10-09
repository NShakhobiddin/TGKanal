# Pochtachi kanali — kontent brifi

> Bu brif faqat Pochtachi kanali uchun. Ikkinchi kanal — «AI darslar» — qoidalari: `channels/ai/BRIEF.md`.

Bu hujjat har kuni ishga tushadigan avtomatik seanslar uchun. Post tayyorlashdan oldin shuni o'qing.

## Kanal haqida
- Nomi: **Pochtachi** — @Pochtam_shopo
- Auditoriya: chet el internet do'konlaridan buyurtma qiladigan o'zbekistonliklar (yangi boshlovchi ham, tajribali xaridor ham)
- Muallif: Shakhobiddin — 6 yil bojxona postida xalqaro jo'natmalar bo'yicha ishlagan mutaxassis. Kanal uning ekspertligiga tayanadi, shuning uchun **noaniq ma'lumot berish mumkin emas**.
- Kanalning maqsadi: obunachini Telegram WebApp'ga (ilova) va murakkab holatlarda pullik maslahatga olib borish.

## Voronka va CTA qoidasi
1. **Kanal** (bepul) — ishonch quradi
2. **Ilova** (bepul, o'z-o'ziga xizmat) — standart holatni hal qiladi
3. **Pullik maslahat** — istisno holatlar (ushlanib qolgan jo'natma, kutilmagan boj, optom partiya)

Qoida: **bitta postda bitta CTA.** 7 ta postdan 5 tasi ilovaga, 1 tasi chaqiriqsiz, 1 tasi pullik xizmatga.
Pullik taklif faqat `#keys` yoki `#boj` postidan keyin. **Chegirma postidan keyin hech qachon sotmang.**

## Rubrikalar va hashtaglar
| Tag | Format | Chastota |
|---|---|---|
| `#narx` | Chetdanmi yoki Uzumdanmi? — narx solishtiruvi | har kuni 20:00 |
| `#obraz` | Tayyor obraz — 5 element, turli do'konlardan | chor, shan 14:00 |
| `#topilma` | Noyob va yangi tovarlar — «bunday narsa borligini bilmagansiz» | juma 14:00 |
| `#keys` | Keys — jo'natma nega ushlanib qoldi (amaliyotdagi tipik holat) | payshanba 09:00 |
| `#boj` | Boj hisobi — qadamma-qadam misol | haftada 2 |
| `#taqiq` | Olib kirib bo'lmaydigan tovarlar | haftada 1 |
| `#dokon` | Do'kon sharhi | haftada 1 |
| `#kuryer` | Kuryerlik solishtiruvi | haftada 1 |
| `#olcham` | O'lcham qo'llanmasi | haftada 1 |
| `#savol` | Obunachi savoli | haftada 2 |
| `#firibgar` | Firibgarlikdan saqlaning | oyiga 2 |
| `#flesh` | Tez o'tadigan chegirma | chiqqanda |
| `#digest` | Hafta yakuni — 5 ta post | yakshanba 09:00 |

## Haftalik jadval (Toshkent vaqti)
| Kun | 09:00 | 14:00 | 20:00 |
|---|---|---|---|
| Dushanba | `#boj` | `#dokon` | `#narx` |
| Seshanba | `#taqiq` | `#olcham` | `#narx` |
| Chorshanba | `#savol` | `#obraz` | `#narx` |
| Payshanba | `#keys` | `#kuryer` | `#narx` |
| Juma | `#boj` | `#topilma` | `#narx` (haftaning eng yaxshisi) |
| Shanba | `#savol` | `#obraz` | `#narx` |
| Yakshanba | `#digest` | `#firibgar` | `#narx` |

## Asosiy format: `#narx` chegirma posti
Majburiy 5 element:
1. Tovar nomi va do'kon (havola bilan)
2. Chegirma foizi, eski va yangi narx
3. **O'zbekistondagi narx** — Uzum Market / Asaxiy / Olcha / Texnomart / Mediapark / Idea / OLX
4. **Chetdan olib kelish umumiy tannarxi**: tovar + yetkazish + bojxona to'lovi
5. Aniq xulosa: qancha tejaladi. **Agar chetdan qimmatroq bo'lsa — buni ochiq yozing.** Bu ishonch beradi.

## `#obraz` formati
5 element (ustki kiyim · ko'ylak/futbolka · shim · poyabzal · aksessuar), har biri: do'kon, narx $, havola.
Jami summa + Toshkentga yetkazilgan so'mdagi narx + O'zbekistondagi shunga o'xshash to'plam narxi.
**Kalit fishka: har bir obraz 200 $ bojsiz limitiga sig'diriladi** — bu bojxona bilimini ko'rsatadi va formatni takrorlanmas qiladi.

**Aniq tovarlar (muallif talabi):**
- Har bir element — **aniq bitta tovar**: do'konning tovar sahifasi havolasi (kategoriya sahifasi emas), tovarning to'liq nomi, rangi, artikuli (bo'lsa) va shu sahifadagi narx. Fetch qilib tekshirilgan tovarlar afzal (H&M, Uniqlo).
- Tovar sahifasini ochib tasdiqlay olmasang — o'sha tovarni qo'yma, boshqasini top.
- `sources` da har 5 tovarning sahifasi bo'lsin; `notes` da har biri uchun rang va o'lcham eslatmasi.

**Rasm — kiyib turgan odam:** bitta tayyor rasm: odam (model) **aynan shu 5 ta tovarni** kiyib turibdi — to'liq bo'y, tabiiy poza, toza fon. Promptda har bir kiyim do'kon sahifasidagidek aniq tasvirlanadi (rang, mato, bichim, tafsilotlar), yonida 1–5 raqamli kichik belgilar. `notes` ga yoz: «ChatGPT'ga 5 ta tovar suratini (do'kon sahifasidan) ham biriktiring — kiyimlar aynan o'xshash chiqadi».

## `#topilma` formati — noyob va yangi tovarlar
Maqsad: qiziqish uyg'otish va ulashilish. Bu rubrika sotmaydi — kanalga yangi odam olib keladi.

Majburiy 5 element:
1. **Tovar va nima qilishi** — bir-ikki jumlada, ortiqcha texnik tafsilotsiz
2. **Nega qiziq** — qanday muammoni hal qiladi yoki nimasi g'ayrioddiy
3. **Qayerdan olinadi** — do'kon va havola, narxi dollarda
4. **Toshkentga yetkazilgan to'liq narxi** — tovar + yetkazish + boj, so'mda
5. **«Olib kira olasizmi?»** — bojxona filtri: bu tovarni O'zbekistonga kiritish mumkinmi, cheklov bormi, ruxsatnoma kerakmi (lex.uz dagi hujjatga tayanib)

5-band bu rubrikaning kaliti. Boshqa kanallar «qiziq gadjet» ni ko'rsatadi, lekin uni haqiqatan olib kirish mumkinmi — aytmaydi. Ko'p qiziqarli tovarlar aynan shu joyda taqiladi: ratsiya, lazer, dron, elektroshok, quvvat banki chegarasi, ba'zi BADlar, tibbiy asboblar.

Aylanma yo'nalishlar: yangi chiqqan gadjet · kundalik hayotni osonlashtiradigan mayda ixtiro · faqat bitta davlatda sotiladigan tovar · kasb yoki hobbi uchun maxsus asbob · bolalar uchun noyob narsa · kollektsion va limited edition · «bu qanchaga tushadi?» — qimmat eksklyuziv tovar.

Tovar topish manbalari: Yanko Design, Stuff.tv, TechRadar, Tom's Guide, Dezeen, The Gadgeteer, CES va IFA yangiliklari.

## Kuzatiladigan do'konlar
- Xitoy: Taobao, Pinduoduo, AliExpress, Poizon
- AQSh: Amazon, eBay, Walmart, Best Buy
- Turkiya: Trendyol, Hepsiburada, LC Waikiki
- Kiyim/kosmetika: SHEIN, ASOS, Zara, Sephora, iHerb
- Kiyim (fetch qilinadigan, tekshirilgan): H&M (www2.hm.com/en_us), Uniqlo (uniqlo.com/us/en)

## Uslub
- O'zbek lotin, do'stona, emoji bilan (lekin ortiqcha emas)
- Qisqa xatboshilar, Telegram HTML teglari: `<b>`, `<i>`, `<u>`, `<s>`, `<code>`, `<a href="">`
- Post oxirida: `➖➖➖` va `@Pochtam_shopo` + rubrika hashtagi
- Affiliate/referal linklar **hozircha yo'q** — toza havolalar
- Caption cheklovi: `card` bo'lsa ≤ 1024 belgi, bo'lmasa ≤ 4096

## Manba qoidasi — QONUNCHILIK (muallif talabi)
- **Qonunchilik hujjatlari faqat lex.uz dan olinadi.** Har bir norma, stavka, taqiq yoki muddat — hujjatning turi, raqami, sanasi va bandi bilan.
- **Qo'shimcha manba: aeroinfo.uz** — «Toshkent-AERO» IBK ning tezkor yo'riqnomasi (aeroport, pochta, mobil qurilmalar, valyuta, kalkulyator).
- gazeta.uz, spot.uz, kun.uz, daryo.uz — **faqat yangilikni topish uchun.** Huquqiy asos sifatida keltirilmaydi. Yangilikda uchragan har bir norma lex.uz dagi asl matn bilan solishtiriladi; mos kelmasa — lex.uz ustun.
- Postdagi manba ko'rinishi: `Asos: Prezident Farmoni PF-174, 27.08.2026, 8-band (lex.uz)`
- lex.uz da ochilmasa yoki tasdiqlanmasa — postga **qo'yilmaydi**, hisobotda «lex.uz da tasdiqlanmadi» deb yoziladi.

## Aniqlik qoidalari
- Har bir raqam manbadan olinishi kerak. Taxminiy hisob bo'lsa — "taxminan" deb yozing.
- Valyuta kursi — Markaziy bank (cbu.uz), `state/rate.json` dan avtomatik (GitHub Actions `rate.yml`, 6 soatda bir). Postda sanasini ko'rsating.
- `#keys` postlarida **ism, jo'natma raqami, aniq sana yoki tanib olish mumkin bo'lgan tafsilot bo'lmasin** — faqat mexanika. Bu kasbiy va huquqiy talab.
- `#keys` keyslarini Claude **o'zi tuzadi** (muallif talabi, 2026-10): bojxona amaliyotida tez-tez uchraydigan vaziyatlar asosida — realistik tovar, qiymat, kanal (pochta/kuryer), muammo va yechim. Har norma lex.uz dan (hujjat, raqam, sana, band), raqamlar generator skriptida hisoblanadi. Muayyan odam yoki voqea deb ko'rsatilmaydi — post oxirida: `<i>Holat bojxona amaliyotidagi tipik vaziyatlar asosida tuzilgan.</i>` Mavzular takrorlanmasin (oxirgi postlarni ko'r). Muallif real holat yuborsa — o'sha ustun.
- Natijani va'da qilmang ("bojni albatta kamaytiraman" deb yozmang).

## Tekshirilgan bojxona faktlari (2026-oktabr holatiga)

### Bojsiz normalar
- Pochta jo'natmalari: oyiga **100 $** gacha bojsiz
- Kuryerlik jo'natmalari: oyiga **200 $** gacha bojsiz (avval choragiga 1000 $ edi)
- Norma **kalendar oy** bo'yicha hisoblanadi, bitta jo'natmaga emas — oydagi barcha jo'natmalar jamlanadi
- Oy **rasmiylashtirilgan sana** bo'yicha belgilanadi (buyurtma yoki kelish sanasi emas) — muallif tasdiqlagan
- **Bojxona qiymati = tovar narxi + yetkazish (yo'l) harajati** — norma ham, boj ham shu summadan hisoblanadi — muallif tasdiqlagan (05.10.2026). Masalan, $182.77 lik kiyim + $28.50 yetkazish = $211.27 → normadan oshadi
- **Boj hisobi (kanal usuli):** normadan ortig'i × 30 %, lekin posilkaning 1 kg i uchun kamida 3 $ (`duty_usd()` generatorda). **`#obraz` da 3 $/kg minimal hisoblanmaydi** — faqat normadan oshgan qismning 30 % i (muallif ko'rsatmasi). Boj to'lansa — **1 ta BKO (bojxona kirim orderi) uchun yig'im: BHM ning 25 %** = 110 000 so'm (VM 55-son, 31.01.2025; BHM 440 000 so'm, 01.09.2026 dan) — lex.uz da qayta tekshirilmagan, muallif so'rovi bilan qo'shildi
- **Alkogol va tamaki pochta/kuryer orqali TAQIQLANGAN** (VM 244, 1-ilova «a» izohi, VM 154-son 09.04.2026 tahriri). Miqdoriy normalar (alkogol 2 l, sigaret 200 dona) faqat yo'lovchi bagaji uchun.
- BAD: 10 xil nomgacha, jami 3 kg, **har nomdan 1 qadoq** (VM 244, 1-ilova)
- Dori vositalari: 10 xil nomgacha, har biridan 5 qadoqgacha (VM 191-son, 08.06.2016, Nizom 5-band)
- 21 yoshgacha — alkogol va tamaki mumkin emas
- **Asos:** VM 2025-yil 19-apreldagi 244-son qarori, 2025-yil 1-maydan kuchda — https://lex.uz/uz/docs/-7484114

### Yagona bojxona to'lovi (normadan ortiq qism uchun)
- **Hozir (2026-yil oxirigacha): 30 %**, lekin 1 kg uchun kamida **3 $** — normadan ortiq qismning bojxona qiymatidan
  - Asos: Prezident qarori PQ-4508, 07.11.2019, 3-band — https://lex.uz/uz/docs/-4585742
  - ⚠️ Eslatma: lex.uz da hozir 3-bandning PF-174 tahriri (20 %) ko'rsatilmoqda; 30 % / 3 $ li oldingi tahrir lex.uz da qayta tasdiqlanmagan — muallif tasdiqlaguncha «hozirgi stavka 30 %» deb yozish mumkin, lekin manbada PQ-4508 ni tahrir sanasisiz keltirmang.
- **2027-yil 1-yanvardan: 20 %**, lekin 1 kg uchun kamida **2 $**
  - Asos: Prezident Farmoni **PF-174, 27.08.2026, 8-band** — https://lex.uz/uz/docs/-8444993
  - Matn: «2027-yil 1-yanvardan boshlab yagona bojxona toʻlovi stavkasi tovarning bojxona qiymatidan 20 foiz, lekin har bir kilogrammi uchun 2 AQSH dollaridan kam boʻlmagan miqdorda belgilansin.»
- **2027-yil 1-iyundan:** jismoniy shaxslar notijorat maqsadda olib o'tadigan tovarlar bo'yicha yagona bojxona to'lovi **bojxona yig'imlaridan kam bo'lsa — yig'imlar undirilmaydi** (ya'ni boj kichik bo'lsa, undan katta rasmiylashtirish yig'imi olinmaydi)
  - Asos: PF-174, 3-band «g» kichik bandi
- **Amaliy xulosa:** normadan ancha oshadigan qimmat tovarni yanvargacha kutish ortiqcha qiymatning 10 % ini tejaydi.

### Boshqa
- 2025-yil 6-noyabrdagi 700-son VM qarori bilan pochta/kuryerlik jo'natmalari uchun "qizil–sariq–yashil" yo'laklar joriy etilgan — postga qo'yishdan oldin lex.uz da tekshiring
- Telefon: UzIMEI ro'yxatdan o'tkazish — ulanishdan keyin 30 kun ichida 88 000 so'm, keyin 110 000 so'm — lex.uz da tekshirilmagan, postga qo'yishdan oldin tasdiqlang
- Kurs: `state/rate.json` (cbu.uz dan avtomatik) — qo'lda yozilmaydi

## Yetkazib beruvchilar narxi (2026-iyul, Spot.uz)
AQSh: Meest 7,70–9,50 $/kg · Turon Express 10 $ · Boxette 11 $ (eks. 3–9 kun, ekonom 9–16) · Globbing 12 $ dan
Xitoy: Green Post 5,50 $/kg dan (3–30 kun) · Jana Post 0,61 $/100 g
Ko'p yo'nalishli: Yumecs 4,40–20 $/kg (RU, TR, CN, KR, AE, US, MY)
Toshkent bo'ylab yetkazish alohida: 2–6,70 $

## Panel (2026-oktabrdan asosiy usul — serversiz, GitHub'da)
- Ma'lumotlar repo'si **`NShakhobiddin/TGKanal`** (ochiq) — postlar `posts/<id>.json`, rasmlar `images/`, sozlamalar `settings.json`. Muallif kompyuterida: `C:\Users\Abc\Documents\Pochtachi\TGKanal\` (Claude Code buyruqlari: `/ornat`, `/hafta`, `/yangila`, `/holat`).
- Panel: **https://nshakhobiddin.github.io/TGKanal/** (TGKanal repo'sidan GitHub Pages; postlarni GitHub tokeni bilan o'qiydi/yozadi).
- GitHub Actions (`publish.yml`) har 5 daqiqada (Toshkent 08:00–23:55; GitHub kechiktirishi mumkin — tashqi jadval: README) tasdiqlangan postlarni kanalga joylaydi; «Hozir joylash», «Menga sinov», «Ulanishni tekshirish» ham shu orqali. Bot tokeni — GitHub secret `TELEGRAM_BOT_TOKEN`.
- Post maydonlari: id, rubric, title, scheduled_at, caption (Telegram HTML), prompt (GPT Image 2), product_url, notes, sources[{label,url}], status (draft | needs_input | approved | published | failed | overdue), image, message_id.
- Muallif rasmni ChatGPT'da chizadi, panelga yuklaydi, tasdiqlaydi — jadval bo'yicha chiqadi.
- Tokenlar: `{{APP_URL}}`, `{{CONSULT_URL}}` (settings.json da bo'sh bo'lsa qator yashiriladi), `<a href="{{LINK:<post_id>}}">` — joylangan postga havola.
- Caption rasm bilan ≤ 1024 belgi (ko'rinadigan matn).
- Yangi postlar: Claude Code'da `/hafta` (repo'ga yozadi). Cowork'dan: device_bash bilan `~/mnt/Pochtachi/TGKanal/posts/` ga JSON yozib, muallifga Claude Code'da `/yangila` ni bosishni ayting (Cowork bulutidan GitHub'ga yozib bo'lmaydi). Mavjud postni qayta yozmang.
- Eski kompyuter paneli (`panel\`, `pochtachi-panel\`) ishlatilmaydi.

## Texnik: post qanday yetkaziladi (eski usul)

`api.telegram.org` Claude bulutidan bloklangan, GitHub'ga yozish ham bloklangan (faqat o'qish ishlaydi). Ishlaydigan yo'l:

1. Claude post JSON faylini Shakhobiddin kompyuteridagi navbat papkasiga yozadi:
   `C:\Users\Abc\Documents\Pochtachi\queue\` — device_bash ichida `~/mnt/Pochtachi/queue/`
2. O'sha kompyuterda ishlaydigan `pochtachi_bot.py` uni o'qiydi, `product_url` dan `og:image` orqali tovar rasmini yuklaydi, `card.py` bilan chegirma kartochkasini chizadi.
3. Bot draftni Shakhobiddinning shaxsiy chatiga tugmalar bilan yuboradi: ✅ Joylash / ✏️ Tahrirlash / 🔄 Qayta chizish / ❌ Bekor.
4. Tasdiqdan keyin kanalga chiqadi, fayl `posted/` ga ko'chadi.

Bot faylni post vaqtidan ~45 daqiqa oldin ko'radi va o'shanda draft yuboradi.

**Agar device asboblari mavjud bo'lmasa** (rejalashtirilgan seans kompyuterga bog'lanmagan bo'lsa, kompyuter o'chiq bo'lsa yoki desktop ilova yopiq bo'lsa): postni `project_write` bilan `claude/navbat/<id>.json` yo'liga yozing (`present_to_user: true`) va javobda post matnini to'liq chiqaring.

### Post JSON sxemasi
```json
{
  "id": "2026-10-09-1400",
  "type": "deal | info | customs | courier",
  "scheduled_at": "2026-10-09T14:00:00+05:00",
  "caption": "Telegram HTML matni",
  "product_url": "https://...",
  "image_url": null,
  "card": {
    "store": "AliExpress",
    "country": "Xitoy",
    "title": "Tovar nomi",
    "discount": 42,
    "price_old": "$118",
    "price_new": "$68",
    "uz_price": 1290000,
    "uz_source": "Uzum Market",
    "import_total": 940000
  }
}
```
`card` = `null` bo'lsa post rasmsiz, faqat matn bo'lib chiqadi.

## Ma'lum cheklovlar
- WebFetch AliExpress, Amazon va Uzum **qidiruv va tovar** sahifalarini o'qiy olmaydi (JS yoki robots.txt). Ishlaydi: lex.uz, aeroinfo.uz, gazeta.uz, spot.uz, texnomart.uz, olcha.uz, hm.com, uniqlo.com, yankodesign.com, stuff.tv, macrumors, 9to5toys va shunga o'xshash nashrlar, WebSearch snippetlari.
- lex.uz da hujjatning eski tahririni (`?ONDATE=`) ochish har doim ham ishlamaydi — joriy tahrir va tahrir izohlariga tayaning.
- Rasm yuklab olish bulutdan bloklangan — rasmni bot o'zi `og:image` orqali oladi.
- Jonli narxni tekshirishning eng ishonchli yo'li: WebSearch snippetlari, keyin Shakhobiddinning tasdig'i.

## To'liq strategiya
Kanal strategiyasi (voronka, rubrikalar, 30 kunlik ishga tushirish rejasi, monetizatsiya, 30 ta post g'oyasi):
https://claude.ai/code/artifact/4773d8b9-8982-4e4b-a7fd-ebbae7c5a6f8
