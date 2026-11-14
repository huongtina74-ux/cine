# Algrow: kênh và video trending ngách AUDIO (truyện / lịch sử / khoa học kể bằng giọng), cách làm như ngày 13/11 (14/11/2026)

## Cách làm (OBSERVED)

**Nguồn:** phiên Algrow đã đăng nhập của owner, chỉ đọc, qua chính API mà trang Algrow dùng.

- **Channel Trends** (`/longform-channels`, ngôn ngữ English):
  - 28 từ khoá audio. Lọc ≤30 ngày, lấy hết các trang:
    - history for sleep, boring history, sleep history documentary, ancient history for sleep, medieval history;
    - sleep story, bedtime stories for adults, sleep stories for grown ups, cozy sleep stories;
    - fantasy lore for sleep, mythology for sleep;
    - space for sleep, science for sleep, universe documentary;
    - revenge story, family drama story, senior stories, inheritance story, karma story, betrayal story;
    - audio story, true story narration, reddit stories, audiobook, audio drama;
    - old west stories, ww2 stories, audio.
  - 6 ngách Algrow: stories_drama, history, relaxation_ambient, education_science, true_crime, horror_paranormal.
    - Lượt 1: kênh "≤30 ngày", sắp theo view 24h, tối đa 300 kênh mỗi ngách.
    - Lượt 2: kênh mọi tuổi, top 100 theo view 24h.
  - Tổng cộng **2.659 kênh**.
  - Tuổi kênh của Algrow = thời gian kể từ video đầu tiên (`first_upload_date`). Bảng quét 30 → 1 ngày bên dưới đếm theo trường này.
- **Viral Videos** (`/api/viral-videos`, longform, English), cùng 28 từ khoá, 2 bộ lọc:
  - *new*: ≥10K view, đăng ≤21 ngày, kênh ≤30 ngày (giống bộ lọc hôm qua);
  - *trend*: ≥100K view, đăng ≤14 ngày, kênh mọi tuổi.
  - Tổng **218 video**.
- **Kiểm tuổi thật:**
  - 74 kênh nổi bật nhất được kiểm ngày tạo kênh bằng dòng "Đã tham gia" trên trang About YouTube. File: `verified_channel_ages.json`.
  - Lần này không dùng `channels.list`, vì Blender bridge trên PC đang tắt, mà khoá API chỉ nằm trên PC.

**Giới hạn:**
- Ngách lớn (stories_drama có **1.816 kênh ≤30 ngày**, history 466, education_science 449) chỉ lấy được 300 kênh đầu theo view 24h. Số đếm dưới đây là **trong mẫu đã lấy**, không phải toàn bộ Algrow.
- Tìm theo từ khoá là tìm theo độ giống. Từ "audio" trả về chủ yếu băng ghi âm ATC (không lưu) hoặc tai nạn máy bay, nên đã loại khỏi kết luận.

## Phát hiện số 1: "kênh mới" của Algrow chỉ đúng một nửa (OBSERVED)

Trong 74 kênh Algrow coi là ≤30 ngày và đang lên mạnh:

| Tuổi thật (trang About) | Số kênh |
|---|---|
| ≤30 ngày | **37** |
| 31–60 ngày | 21 |
| >60 ngày (tài khoản cũ) | 16 |

**Ví dụ tài khoản cũ:**

| Kênh | Tuổi thật |
|---|---|
| The Battle Blueprint | 4.673 ngày |
| The Boring Hobbit | 3.032 ngày |
| Arven | 2.393 ngày |
| NightProtocol | 1.911 ngày |
| Mike after Midnight | 1.870 ngày |
| Aliens Uncovered | 1.544 ngày |
| Final Sight | 851 ngày |
| Mama's Truths | 492 ngày |
| Nameless Wild West | 99 ngày (Algrow ghi 14 ngày) |

Kết luận giống hôm qua: **mọi "kênh mới" của Algrow phải kiểm lại ngày tạo** trước khi coi là đối thủ mới.

## Quét tuổi 30 → 1 (Algrow, theo video đầu tiên; mẫu 2.058 kênh ≤30 ngày)

| ≤30 | ≤25 | ≤20 | ≤15 | ≤10 | ≤7 | ≤5 | ≤3 | ≤2 | ≤1 |
|---|---|---|---|---|---|---|---|---|---|
| 2.058 | 1.556 | 1.026 | 585 | 282 | 126 | 63 | 19 | 8 | 0 |

**Theo nhóm ngách audio**
- Chỉ tính kênh ≤30 ngày (Algrow) có view 48h ≥20K, hoặc kênh cũ có view 24h ≥30K.
- Nhóm được phân bằng ngách con của Algrow cộng tiêu đề (INFERRED).

| Nhóm | Kênh ≤30 ngày | Tổng view 24h | Trung vị view/video | Số kênh ≥100K view/48h | Có kiếm tiền (Algrow) |
|---|---|---|---|---|---|
| Truyện gia đình / báo thù / người già (Senior Family Drama) | 269 | 6,42M | 6,7K | 27 | 35 |
| Truyện tình cảm tỷ phú / mafia | 230 | 7,98M | 11,2K | 41 | 34 |
| Lịch sử / chiến tranh | 299 | 6,61M | 13,1K | 27 | 35 |
| Khoa học / "What if" | 249 | 5,74M | 12,3K | 22 | 38 |
| Án mạng / kinh dị kể chuyện | 210 | 6,13M | 13,4K | 23 | 34 |
| **Ru ngủ** (tên, ngách con hoặc tiêu đề có "for/to sleep", "bedtime", "fall asleep", "boring history") | **25 khớp từ** (soát tay 14 kênh đầu: chỉ **7** đúng dạng ru ngủ) | — | — | 0 kênh ru ngủ đúng dạng | — |

**Đọc bảng** (INFERRED):
- Truyện gia đình/báo thù và tình cảm có **nhiều kênh mới nhất**, nhưng trung vị view mỗi video thấp nhất (6–11K). Nghĩa là đông, cạnh tranh gắt, chỉ vài kênh thắng lớn.
- Mảng **"for sleep" rất ít kênh mới**: 25 kênh tìm thấy, so với vài trăm ở các nhóm khác. Đây là khoảng trống.

## Bảng A: kênh mới THẬT (≤30 ngày theo About) khớp ngách audio của Afanta

Số liệu là OBSERVED từ Algrow và YouTube lúc 14/11. "View 48h" là lượt xem toàn kênh trong 48 giờ.

### A1. Senior Family Drama / Quiet Justice (khớp kênh "Senior Family Drama")

| Kênh | Tuổi thật | Sub | Số video | View 48h | Video lớn nhất | Độ dài |
|---|---|---|---|---|---|---|
| **Henry Whitmore Stories** | 23 ngày | 1,39K | 6 | **696K** | "He Took Her $20 Tip. The Woman She Defended Later Gave Her $500,000." 808K | 25 phút |
| **Heartland Payback** | 12 ngày | 2,8K | **25** | 543K | "20 Years Later, My Parents Asked To Retire In My Lake House…" 97K | 41 phút |
| Hopeforge Studios | 17 ngày | 4,48K | 6 | 239K | "Exhausted Single Mom Fell Asleep Holding Her Termination Letter — He Was the CEO" **1,42M** | 24 phút |
| Aged Dad Revenge | 24 ngày | 2,25K | 32 | 176K | "My Son Said 'We'd Only Be in the Way!' When I Told Him About My Brain Tumor…" 42K | 34 phút |
| Deep Reddit Drama | 25 ngày | 2,14K | 31 | 172K | "10 Years Later, I Bought Grandpa Hearing Aids…" 224K | 34 phút |
| Grandpa's Golden Years | 12 ngày | 622 | 24 | 164K | "She Said I Wasn't Boyfriend Material…" 37K | 22 phút |
| Untold Hearts | 25 ngày | 4,83K | 8 | 146K | "Classmates Invited Her to the 20-Year Reunion to Laugh at Her…" 590K | 30 phút |
| DAD'S FINAL SAY | 27 ngày | **11,1K** | 29 | 143K | "I Checked Into My Own Hotel. The Clerk Charged Me $1,400 and Said: 'Grandpa…'" 214K | **107 phút** |
| Reddit Wild Tales | 25 ngày | 1,2K | 25 | 143K | "14 Years Later, Mom Came To My Work For Grandpa's Checks…" 84K | 34 phút |
| Kate Villon | 15 ngày | 875 | 11 | 200K | "Everyone Laughed at Her Mountain of Firewood — Until Winter Came" 224K | 38 phút |
| Clara Whitmore | 29 ngày | 1,51K | 23 | 150K | "'Nobody Bids on the Plain One'—The Whole Town Laughed…" 107K | 80 phút |
| Noxavaryn | 23 ngày | 3,23K | 17 | 173K | "His Wife Kicked Him Out. Her Boss Married Him That Same Day." 83K | 125 phút |

**Tham khảo, vừa quá 30 ngày hoặc tài khoản cũ:**
- Nameless Wild West:
  - tạo 99 ngày, 5,6K sub, chỉ 2 video;
  - "Outlaws Were Hanging the Old Widow Over $70… Unaware Her 2 Sons Are the Most Feared…" **1,55M**, outlier **114×**, 32 phút.
- Velvet Drama Cinema (44 ngày): 600K.
- Ember Gold Cinema (44 ngày): 274K.
- Victory Stories (35 ngày): 672K.

### A2. Lịch sử: kể chuyện tài liệu và "for sleep" (khớp "History for Sleep")

| Kênh | Tuổi thật | Sub | View 48h | Video lớn nhất | Độ dài |
|---|---|---|---|---|---|
| **Civil War Fine Print** | **7 ngày** | 3,94K | **638K** | "The Pictures of Lincoln's Death You Weren't Supposed to See" **1,06M** | 15 phút |
| Okeanos History | 24 ngày | 5,2K | 367K | "The Real Reason Canada Never Became Part of the United States" 298K | 31 phút |
| The War They Filmed | 23 ngày | 4,06K | 315K | "The Battle of Tarawa 1943 in Real Color…" 851K | 27 phút |
| Never Invaded | 13 ngày | 1,87K | 90K | "The Real Reason Mao Never Invaded Taiwan…" 71K | **61 phút** |
| Life on the Front | 29 ngày | 1,84K | — | "Your Life as a German POW in America (1943–1946)" 87K; "Your Life at Bastogne" 76K | 21–24 phút |
| Your POV | 22 ngày | 162 | — | "Your Day As a WW1 Soldier" 76K, outlier 16× | 18 phút |
| Dynamic Maps | 20 ngày | 598 | — | "D-Day to Victory in Europe, Every Day – Real Voices" 58K | 13 phút |

**Ru ngủ lịch sử đúng nghĩa (mới ≤60 ngày):**
- **The Night Caravan:** 32 ngày, 1,56K sub. "How Did the Inuit Survive the Arctic Winter in Igloos? | History for Sleep", **157 phút**.
- **Rome Retold:** 38 ngày. "Why Weren't Roman Soldiers Afraid to Sleep Near Their Enemies?" 223K, 36 phút.
- Gone Medieval: 59 ngày, có vẻ là kênh của một podcast lịch sử có sẵn (INFERRED). "Hussite Wars" 289K, 57 phút.

**Kênh cũ đang thắng ở mảng này:**
- **ChatHistoryCompilations:** 240K sub. "Go To Sleep While I Teach You History Facts for Two Hours" **3,5M**, 125 phút.
- Ziro History: "The ENTIRE History of Greek Mythology in 55 minutes" 116K.

### A3. Khoa học / vũ trụ ru ngủ (khớp "Space Science for Sleep")

| Kênh | Tuổi thật | Sub | View 48h | Video lớn nhất | Độ dài |
|---|---|---|---|---|---|
| **Dozeology** | 24 ngày | **8,15K** | 83K | "Gold Isn't From Earth… So Where Did It Actually Come From?" **439K** | **129 phút** |
| Beyond The Graph – Physics | 15 ngày | 1,94K | 89K | "What Happens When Electrons Are Forced Into Protons?" 79K | 21 phút |
| SleepyGovernance | **6 ngày** | **7,32K** | 29K | "Captain Amelia \| A Quiet Treasure Planet Essay for Sleep (8 Hours)" | **8 giờ** (lore phim Disney, có vướng IP) |
| Mistletoe & Moonlight | 32 ngày | 571 | 13K | "A Quiet Night Before Christmas in a Victorian English Home \| Cozy Sleep Story" | 65 phút |

**Kênh cũ làm mẫu:**
- **Sleepy Science:** 85,6K sub. "You Wake Up One Billion Years From Now" 265K, 146 phút.
- Jeremy Bearimy: "6 Hours of 'What IF' Videos to Fall Asleep to" 336K.
- Candlewick Tales: 3,36K sub. "Miss Wren's Bookshop Stays Up Late | A Cosy Victorian Sleep Story for Grown Ups" 132K.
- Kênh lớn: Stephen Dalton Sleep Stories (329K sub), Get Sleepy (734K sub).

### A4. Sách nói phạm vi công cộng

**Serotina:**
- 148 ngày, 9,91K sub, Algrow ghi có kiếm tiền.
- Video:
  - "On the Tranquillity of Mind — Seneca | Audiobook" 227K;
  - "The Ego and the Id — Freud" 100K;
  - "Twilight of the Idols — Nietzsche" 96K;
  - "Tao Te Ching" 76K.
- Đọc nguyên văn tác phẩm đã hết bản quyền, video dài 80–200 phút.

## Bảng B: video trending (≤14 ngày, ≥100K, đúng chất "kể bằng giọng")

| Video | Kênh (sub) | View | Ngày đăng | Độ dài | Outlier |
|---|---|---|---|---|---|
| Outlaws Were Hanging the Old Widow Over $70… | Nameless Wild West (5,5K) | 1,55M | 07/11 | 32 phút | 114× |
| Outlaws Humiliated the Old Rancher Over $100… | Nameless Wild West | 503K | 31/10 | 31 phút | 43× |
| Betrayed While Pregnant — She Left Everything Behind… Abandoned… | Mowing HOUSE (59K) | 512K | 02/11 | 43 phút | 7,5× |
| 6 Hours of "What IF" Videos to Fall Asleep to | Jeremy Bearimy (55K) | 336K | 06/11 | 356 phút | 2,2× |
| Eleanor Janega Explains The Medieval Hussite Wars | Gone Medieval (13K) | 289K | 29/10 | 57 phút | 2,9× |
| Horrors of Being a Cowboy in 1880 | Paul McAllister (123K) | 231K | 02/11 | 56 phút | 6,2× |
| On the Tranquillity of Mind — Seneca \| Audiobook | Serotina (9,8K) | 227K | 30/10 | 81 phút | 7,1× |
| He Pushed His Wife Into the Grand Canyon. Karma Struck Minutes Later. | Last Moments (149K) | 179K | 03/11 | 29 phút | 1,2× |
| What Happened to Haile Selassie's Body After He Was Overthrown? \| History For Sleep | tài khoản 693 ngày (1,4K) | 143K | 30/10 | 51 phút | 2,0× |
| 11 BRUTAL Old West PUNISHMENTS… | Discovery in English (2,6K) | 134K | 01/11 | 31 phút | 54× |
| 2 Hours Of Most Disturbing UFO Sightings \| Lore To Fall Asleep To | 50M Videos (2M) | 125K | 08/11 | 125 phút | 2,0× |
| German Female POWs Couldn't Believe What American Soldiers Did: True WW2 Story | Battlefield Untold (1K, tài khoản 2020) | 120K | 31/10 | 8 phút | 54× |
| The ENTIRE History of Greek Mythology in 55 minutes | Ziro History (27K) | 116K | 05/11 | 55 phút | 3,2× |

Các video trending lớn khác (Smosh Pit, Kallmekris đọc Reddit, 2,5–3,3M) là kênh lớn có người dẫn thật. Không dùng làm chuẩn cho kênh mới.

## Nguyên tắc rút ra (quy tắc D, INFERRED từ bảng A–B)

**Dài hạn (L):**
- **L1. Ru ngủ = dài.** Kênh thắng mảng "for sleep" làm video 2–8 giờ, chủ đề không lỗi thời: sự thật lịch sử, vũ trụ, truyện ấm cúng thời Victoria. Ví dụ: ChatHistoryCompilations 125 phút / 3,5M; Sleepy Science 146 phút; Dozeology 129 phút.
- **L2. Truyện người già / gia đình theo công thức cố định:**
  - "[N] Years Later, [người thân] Asked/Begged… [cú lật]".
  - "[Kẻ có quyền] Mocked/Charged… Grandpa/Widow… Unaware…".
  - Ngôi thứ nhất là ông bố hoặc ông nội, dài 25–110 phút.
- **L3. Lịch sử kiểu "The Real Reason X Never Y"** và "Your Life as [người thường] in [sự kiện]": nhiều kênh mới cùng thắng (Okeanos, State Dossiers, Never Invaded, Life on the Front, Your POV).

**Ngắn hạn (S, thấy lần đầu 14/11):**
- **S1.** Miền Tây: góa phụ hoặc ông chủ trại bị làm nhục, "unaware her 2 sons…" (1,55M).
- **S2.** Sinh tồn mùa đông nơi biên cương: "Everyone laughed at her firewood…" (Kate Villon, 15 ngày).
- **S3.** Ảnh và phim màu Nội chiến Mỹ, Thế chiến 2 (Civil War Fine Print 7 ngày, 1,06M; The War They Filmed).
- **S4.** Tuyển tập "What if… to fall asleep to" 6 giờ.

## Rủi ro thấy được (OBSERVED + INFERRED)

- **Sản xuất hàng loạt:**
  - Heartland Payback: 25 video trong 12 ngày.
  - Grandpa's Golden Years: 24 video trong 12 ngày.
  - Mia Period Drama: 79 video trong 32 ngày.
  - Đây đúng là kiểu YouTube nhắm tới với chính sách "inauthentic / mass-produced". Afanta không nên đua số lượng.
- **IP và nội dung tái sử dụng:**
  - Lore phim của người khác: SleepyGovernance (Treasure Planet), Midnight Marvel, The Boring Hobbit.
  - Kênh dùng bodycam hoặc phim thẩm vấn của cảnh sát (Miranda, CASEVEX, Hushed Case).
- **Mảng Senior Family Drama đã đông** (269 kênh mới trong mẫu). Phải khác biệt bằng chất lượng truyện, không bằng số lượng.

## Đề xuất cho Afanta (INFERRED, owner quyết)

1. **Space Science for Sleep: ưu tiên 1.**
   - Có kênh mới thắng thật: Dozeology, 24 ngày, 8,15K sub, video 129 phút đạt 439K.
   - Rất ít đối thủ mới: 25 kênh khớp từ "for sleep" trong toàn mẫu, soát tay chỉ khoảng 7 kênh đúng dạng ru ngủ.
   - Nội dung khoa học kiểm chứng được, rủi ro bản quyền thấp, khớp quy tắc claims ledger đã có trong Afanta.
2. **Senior Family Drama / Quiet Justice: làm, nhưng theo hướng chất lượng.**
   - Nhu cầu đã được chứng minh: hơn 10 kênh mới thật đạt 140–700K view mỗi 48 giờ.
   - Đi 1 video/ngày trở xuống, cốt truyện gốc, giọng đọc nhiều vai.
   - Dùng công thức L2 và chủ đề ngắn hạn S1–S2: miền Tây, góa phụ, mùa đông.
3. **History for Sleep: lai hai dạng.**
   - Bản 15–60 phút theo công thức L3 để kéo view.
   - Bản ghép 2–3 giờ "to fall asleep to" từ chính các tập đã làm, như ChatHistoryCompilations.
4. **Thử thêm:** sách nói phạm vi công cộng (mẫu Serotina). Chi phí kịch bản gần bằng 0, nhưng cần kiểm bản dịch đã hết bản quyền.

Dữ liệu tuổi kênh: `verified_channel_ages.json`. Số liệu kênh và video lấy trực tiếp từ API Algrow lúc 12:00–12:40 ICT, 14/11/2026.

---

## Bổ sung 13:10: tab "Trending now" (`/viral/trending`), lượt quét ban đầu chưa có

**Cách làm (OBSERVED):**
- API `/api/viral-videos/trending` với `kind` = `formats` (công thức tiêu đề) và `subjects` (chủ đề).
- Sắp xếp `rising`, cửa sổ 7 ngày, tối đa 20 mục mỗi lần gọi.
- Chạy 26 tổ hợp ngách và ngách con:
  - relaxation_ambient: chung; sleep stories; history sleep; sleep facts; sleep compilations; bible sleep stories; audiobooks; bedtime stories.
  - stories_drama: chung; family drama; revenge stories; family betrayal; family revenge; life stories; emotional stories; family stories.
  - history: chung; world war ii; american history; ancient history; historical mysteries.
  - education_science: space science; space exploration; space discoveries; astronomy; cosmology.
- Mỗi tổ hợp có đủ 2 kiểu, tổng 52 lần gọi.
- "Tăng %" là `change_pct` của Algrow, so tuần này với tuần trước.
- "View 7 ngày" là tổng view theo ngày của các video thuộc công thức hoặc chủ đề đó.

**Quy mô ngách con theo Algrow** (view/ngày, tuần này):

| Ngách | Ngách con và view mỗi ngày |
|---|---|
| stories_drama | family drama 6,15M · revenge stories 4,08M · family betrayal 2,31M · reddit stories 1,71M · life stories 1,65M · family revenge 0,67M |
| relaxation_ambient | sleep stories 363K · **history sleep 122K** · sleep facts 102K · bible sleep stories 39K · audiobooks 31K · bedtime stories 28K |
| education_science | space exploration 855K · space science 720K · space discoveries 621K · astronomy 480K · cosmology 375K |
| history | world war ii 3,46M · military history 1,03M · historical mysteries 724K · american history 575K · ancient history 512K |

### Công thức tiêu đề đang lên (formats)

| Ngách | Công thức | Tăng % | Số kênh | View 7 ngày | Video mẫu (kênh, view, ngày) |
|---|---|---|---|---|---|
| Sleep | "[DURATION] of [TOPIC] to Help You Sleep" | +135% | 11 | 57K | "7 Hours Of MCU Lore To Help You Sleep" (Midnight Marvel, 280K, 04/10) |
| Sleep | "Fall Asleep To The Entire Story Of [STORY]" | +159% | 10 | 37K | "Fall Asleep To The Entire History Of Middle Earth" (Mordoze, 337K) |
| Sleep | "The Entire [FRANCHISE] Timeline to Fall Asleep to" | +680% | 5 | 27K | Midnight Marvel, 1,05M (tháng 4) |
| Sleep | "[N] Hours of [CONTENT] You Won't Forget — No Ads \| for Sleep" | +897% | 2 | 19K | "7 HOURS of Horror Stories…" (Stories – Midnight Dread, 41K) |
| Sleep facts | "The Most Relaxing [FACTS] About [TOPIC] to Fall Asleep to" | — | 2 | 9K | Sleepy Science, "…Facts About Cats…" 382K |
| Family betrayal | "[DURATION] Later My [RELATION] Asked to Retire in My [PROPERTY]…" | **+1.083%** | 2 | 123K | Heartland Payback (kênh tạo 12 ngày) 97K |
| Family drama | "They Said 'He Can't Hear You' While I Talked to My Comatose [FAMILY]…" | **+1.082%** | 2 | 74K | Dad's Revenge Stories, 493K |
| Family betrayal | "My [FAMILY] Kicked Me Out at [AGE] Then the [AUTHORITY] Locked the Door" | +68% | 3 | 92K | QUIET POWER, 170K |
| Family revenge | "'Pack Your Bags and Get Out' My [RELATIVE] Yelled at [OCCASION]…" | mới | 2 | 37K | Dad's Revenge Tales, 35K |
| Stories (chung) | "The [PERSON] Disguised His [RELATIVE] to Test His [PARTNER]…" | +676% | 3 | **1,40M** | Silent Vengeance 2026, 1,46M (06/11) |
| History | "The Real Reason [LEADER] Never Invaded [COUNTRY]" | +85% | 10 | **1,74M** | State Dossiers, "…Hitler Never Invaded Turkey" 453K |
| History | "How Every [SUBJECT] Died" | +306% | 33 | 1,37M | Mr. Discovery, "How Every Greek Villain Died" 1,17M |
| History | "The Entire Story of [SUBJECT] in [DURATION]" | +186% | 45 | 966K | Archive in Minutes, "…SS in 16 Minutes" 678K |
| Ancient history | "How [PEOPLE] Built [SHELTER] to Survive [THREAT]" | +618% | 2 | 35K | ZENO, 103K |
| Space | "Why It's Impossible to [ACTION]" | +505% | 4 | 690K | What If, "…go above and below the Solar System" 579K |
| Space | "What [PEOPLE] Experienced While Sleeping on the [PLACE]…" | +1.127% | 2 | 45K | Deep Space News, 101K |
| Space | "What Would Happen During a Journey to [PLACE]" | mới | 2 | 74K | **Sleep On Science**, "…Journey to Alpha Centauri?" 74K (11/11) |

### Chủ đề đang lên (subjects) liên quan audio

**Lịch sử:**

| Chủ đề | Tăng % | Số kênh | View 7 ngày | Video mẫu |
|---|---|---|---|---|
| Abraham Lincoln | +532% | 30 | 1,24M | Civil War Fine Print 1,06M; "Why Lincoln's Coffin Was Opened 36 Years After His Death" 109K |
| Vietnam War | +307% | 56 | 1,57M | — |
| Stonehenge | +274% | 37 | 2,90M | — |
| Battle of Midway | +288% | 15 | 474K | The War They Filmed 450K |
| Douglas MacArthur | +398% | 9 | 340K | — |
| Dyatlov Pass | +130% | — | 625K | — |
| Bronze Age | +121% | — | — | "ASMR Historian – A Short Introduction to the Bronze Age \| Human Voiced, No Ads" 42K |

**Vũ trụ:**

| Chủ đề | Tăng % | Số kênh | View 7 ngày |
|---|---|---|---|
| Jupiter | +4.324% | 5 | 489K |
| Solar System | +1.019% | 9 | 592K |
| Io | +230% | — | — |
| NASA | +342% | — | — |
| Alpha Centauri | +279% | — | — |
| James Webb (astronomy) | +1.023% | — | — |
| TON 618 | — | — | — |

Video mẫu cho TON 618: **Sleep On Astrophysics**, "The True Scale of TON 618…" 62K.

**Gia đình:**
- Thanksgiving xuất hiện ở 36 kênh family drama (+230%) và 18 kênh family revenge (+108%). Ví dụ: "My Son-in-Law Kicked My Chair Away At Thanksgiving Dinner…" 86K.
- Reddit trong family betrayal: +1.541%, 542K.
- Christmas: +76%.

**Ru ngủ:**
- Ireland +139%: "Crossing Ireland by Train | Sleep Story **Narrated by Cillian Murphy**" (kênh Boring History For Sleep, 193K).
  - Tiêu đề dùng tên một diễn viên thật. Rất có thể là giọng AI giả người thật (INFERRED) → **không bắt chước**.
- Reddit +sleep: "3 Hours Of Reddit Relationship Drama To Sleep To At 1AM" 523K.
- MrBallen sleep edition, Carl Jung: đang giảm (–43%, –49%).

### Thêm vào kết luận (INFERRED)

1. **Mùa lễ là chủ đề ngắn hạn mạnh nhất cho Senior Family Drama** (S5):
   - Thanksgiving (26/11) đang lên ở cả family drama lẫn family revenge, Christmas đang bắt đầu lên.
   - Afanta nên ra tập Thanksgiving trước 26/11 và tập Christmas trước 15/12.
2. **Công thức tiêu đề gia đình đang +1.000%:**
   - "[N] Years Later, My [Relation] Asked to Retire in My [Property]";
   - "They Said 'He Can't Hear You'… Comatose…";
   - "Pack Your Bags and Get Out…".

   Chỉ mượn **khung câu**, cốt truyện phải gốc.
3. **Space Science for Sleep:**
   - Đối thủ cùng dạng mới xuất hiện: Sleep On Science, Sleep On Astrophysics, Dozeology.
   - Chủ đề đang nóng: Jupiter/Io, Hệ Mặt Trời "nhìn từ trên", hành trình tới Alpha Centauri, TON 618.
   - Cửa vẫn mở nhưng cần vào sớm.
4. **History for Sleep:**
   - Ngách con "history sleep" có 122K view/ngày, nhỏ nhưng đang có. Ngách cha history rất lớn (WW2 3,46M view/ngày).
   - Công thức an toàn để kéo view:
     - "The Real Reason [X] Never [Y]" (10 kênh, 1,74M view/7 ngày);
     - "The Entire Story of [X] in [N] Minutes" (45 kênh);
     - "How Every [X] Died" (33 kênh).
   - Sau đó ghép thành bản 2–3 giờ "to fall asleep to".
5. **Không làm:** lore phim hoặc thương hiệu của người khác (MCU, Middle Earth, Cyberpunk), giọng giả người nổi tiếng, clip tổng hợp của streamer.
