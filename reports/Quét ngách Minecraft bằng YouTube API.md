# Shorts mở cửa, phim sinh tồn kiếm tiền

**Theo dữ liệu YouTube Data API chính thức (US, tiếng Anh, chụp ngày 2026-11-03), chỉ có một làn video dài mà kênh mới làm IP gốc đã thật sự phá được: phim sinh tồn có kịch bản kèm mối đe dọa.** Dạng phổ biến nhất là "100 ngày trong dịch zombie" hoặc "có thứ gì đó đang săn tôi". Ví dụ rõ nhất là **Day Zero**: kênh tạo ngày 2026-10-05, video dài đầu tiên dài 52 phút đạt **1,89M view, gấp 136 lần số subs**. Ví dụ thứ hai là **Kit vs The End**: kênh 37 ngày tuổi, bản "Full Movie" 73 phút đạt **673K view, gấp 69 lần subs và 34 lần trung vị của kênh** (OBSERVED). Còn để kênh mới được nhìn thấy thì phải dùng Shorts. Trong 7 ngày, Shorts chiếm **87% lượt xem** của mẫu, và kênh dưới 12 tháng tuổi làm ra 34% số Shorts vượt 100K view. Với video dài, con số này chỉ là 11%, và kênh dưới 90 ngày tuổi chỉ chiếm 2% (OBSERVED). Nhưng Shorts chỉ trả khoảng 3–14% RPM của video dài (OWNER), nên tính theo doanh thu quy đổi, video dài vẫn chiếm 52–83% (INFERRED). Phép thử khắt khe của chủ kênh (kênh 0–30 ngày tuổi có từ 2 video dài 1M trở lên) **không kênh nào đạt** trong ảnh chụp này. Day Zero gần nhất, còn thiếu đúng một video dài 1M. Phần lớn các vụ "kênh mới bùng nổ" trông hấp dẫn đều dựa vào nhân vật của người khác. Ví dụ là JJ & Mikey (Maizen) và Verity: chúng có mặt trong 85–88% số Shorts vượt 100K của nhóm hoạt hình và lựa chọn trẻ em (OBSERVED). Studio không được dùng các nhân vật này. Bù lại có một tin tốt: ở mức trung vị, Shorts IP gốc đạt **355K view/ngày**, so với 307K của Shorts dùng nhân vật người khác (OBSERVED). Nghĩa là quy tắc chỉ dùng IP gốc gần như không làm studio mất gì. Đề xuất của báo cáo: làm ngay một series sinh tồn dịch zombie cho Bin, Bo và Zu, mỗi tập 10–12 phút, cứ 4 tập thì gộp thành "Full Movie" 45–50 phút. Song song, chạy 3 kiểu Shorts gốc làm phễu: thi đấu mini, cải trang/xâm nhập, và thí nghiệm cơ chế game. Ngày mai cần đo lại tốc độ tăng 24 giờ của các ứng viên chính.

> **Quy ước nhãn và phạm vi.** Nhãn theo CLAUDE.md:
>
> - **OBSERVED**: đếm từ file dữ liệu API hoặc các CSV dẫn xuất từ file đó.
> - **INFERRED**: lập luận của báo cáo này.
> - **OWNER**: chủ kênh đã nói hoặc đã quyết.
>
> Nguồn dữ liệu là một lần chạy YouTube Data API v3 lúc 19:00–19:05 UTC ngày 2026-11-03, chỉ đọc, dùng 9.111 đơn vị quota:
>
> - 84 lần gọi `search.list` với 66 từ khoá ngắn, dài và liên quan, lọc 7 ngày. Có 18 từ khoá lõi chạy thêm cửa sổ 15 ngày.
> - Kết quả: 2.827 video, 1.958 kênh, và 11.408 video upload của 308 kênh ([api_dataset.md](<../research_notes/Quét ngách Minecraft bằng YouTube API/api_dataset.md>)).
> - Chụp lần hai lúc 19:16 UTC cho 795 video để đo tốc độ, dùng thêm 16 đơn vị.
>
> Mọi đường dẫn `data/…` dưới đây trỏ tới `research_notes/Quét ngách Minecraft bằng YouTube API/data/`. Báo cáo này không xem video nào. Mọi nhận định về nhịp dựng, diễn xuất hay âm thanh đều là giả thuyết, cần qua cổng `competitor-complete-study`.

## Bản đồ 20 ngách con: Shorts áp đảo lượt xem, video dài nắm tiền

Để trả lời "ngách nào chen vào được", trước hết cần định nghĩa ngách bằng nội dung, không bằng từ khoá. Bộ phân loại gắn mỗi video vào một trong 20 ngách con. Việc gắn dùng ba lớp: luật theo thứ tự trên tiêu đề, luật riêng cho các kênh chỉ làm một định dạng, và một cờ "IP bên thứ ba" chỉ xét tiêu đề. **717 video được đọc tay**, chiếm 78,5% lượt xem tiếng Anh trong 7 ngày. Sau khi lọc ngôn ngữ và bỏ video không phải Minecraft, tập phân tích 7 ngày còn **1.486 video tiếng Anh: 1.068 Shorts (≤180 giây) và 418 video dài** (OBSERVED, [derived_A_videos_tagged.csv](<../research_notes/Quét ngách Minecraft bằng YouTube API/data/derived_A_videos_tagged.csv>)). Bảng dưới gộp định nghĩa nội dung với các số đo quan trọng nhất. Các ngách được xếp theo mức phù hợp với Bin, Bo và Zu (INFERRED), không theo lượt xem.

Chú thích cột (OBSERVED, [derived_A_niche_metrics_7d.csv](<../research_notes/Quét ngách Minecraft bằng YouTube API/data/derived_A_niche_metrics_7d.csv>)):

- **"View 7 ngày"** là tổng view Shorts / tổng view video dài.
- **"Trung vị dài"** là view trung vị của video dài trong ngách.
- **"Kênh mới"** là tỷ lệ video ≥100K đến từ kênh ≤12 tháng tuổi, viết theo dạng Shorts / dài.
- **"IP gốc"** là tỷ lệ video ≥100K không có nhân vật bên thứ ba trong tiêu đề.

| Ngách con (mã) | Định nghĩa nội dung | View 7 ngày (Shorts / dài) | Trung vị dài | Kênh mới (Shorts / dài) | IP gốc | Đánh giá cho Bin/Bo/Zu (INFERRED) |
|---|---|---|---|---|---|---|
| Sinh tồn có kịch bản (SURV100) | "100 days", "I survived", chuỗi hardcore, "THE MOVIE"/[FULL MOVIE] | 1,1M / 7,7M | 47K | 50% / 0% (7 ngày); có ca kênh mới ở cửa sổ 15 ngày | 63% | **Làn chính:** hợp cấu trúc kịch bản, đúng làn OWNER "Day 1 → Day 100" |
| Kinh dị dạng gameplay (HOR_PLAY) | Mod kinh dị, thử "scary myths", seed ma, roleplay nhà ma, "something on my farm…" | 5,1M / 14,2M | 41K | 46% / 5% | 91% | **Lớp vỏ đóng gói** cho làn chính và làn bí ẩn |
| Thử thách "Minecraft but…" (CHALL_BUT) | "Minecraft but…", lucky block, one block/chunk, "beating Minecraft with X mod" | 34,4M / 8,2M | 18K | 7% / 21% | 88% | Phụ: dùng như "luật chơi" trong truyện |
| Hài kịch hoạt hình (SKIT_COMEDY) | Skit hoạt hình không mã hoá trẻ em (BlobbyClips, PumpBrine, Wablo) | 87,3M / 1,4M | 86K | 27% / 25% | 46% | **Phễu Shorts tốt nhất** cho pipeline hoạt hình |
| Hoạt hình truyện trẻ em (KIDS_ANIM_STORY) | Truyện nhân vật (fan JJ/Mikey, "No one helped…", truyện buồn, Monster School, gia đình/em bé) | 97,8M / 4,7M | 362K | 56% / 29% | 14% | Bẫy: 86% hit dùng IP Maizen, rủi ro MFK cao nhất |
| Lựa chọn/đố (KIDS_CHOICE_PUZZLE) | "1 or 2", đoán, chọn cửa, thử thách cầu/mê cung, "who will win", "help X" | 109,5M / 0,35M | — | 33% / — | 13% | Tránh làm làn chính; chỉ mượn dạng "who can X fastest" |
| Meme/clip (MEMES_CLIPS) | Meme gameplay, clip, edit, "X the SOUND", "try not to laugh" | 130,8M / ~0 | — | 28% / — | 74% | Phễu phụ; không có tiền từ video dài |
| Build/mẹo xây (BUILD) | Hướng dẫn xây, mẹo, farm, redstone | 33,5M / 2,5M | 44K | 26% / 43% | 90% | Phụ: chỉ khi build phục vụ truyện |
| Mẹo/cơ chế/tin (FACTS_TIPS_NEWS) | "Why do…", cơ chế, tin update | 12,4M / 0,4M | 3K | 31% (kênh ≤90 ngày: 31%) | 100% | **Làn thử OWNER** "thí nghiệm dị thường" ở dạng Shorts |
| Mô phỏng/chiến tranh người chơi (SIM_WAR) | "1.000/10.000 players simulate…", civilization | 0 / 15,3M | 170K | — / 17% | 100% | Loại: cần server hàng nghìn người thật |
| Manhunt/PvP | Speedrunner vs hunters, PvP, trốn tìm | 3,6M / 4,9M | 8K | 44% / 20% | 84% | Loại cho video dài: cần người chơi thật |
| SMP | Chuỗi SMP, clip streamer (Unstable/Donut SMP, 2b2t) | 21,0M / 5,1M | 51K | 43% / 0% | 42% | Loại: cần cá nhân streamer |
| Kinh dị hư cấu (HOR_FIC) | Found footage, analog horror, ARG, creepypasta, Broken Script | 0,17M / 1,5M | **2,8K** | — / 0% | 100% | Giữ chất bí ẩn trong truyện, **không** dùng nhãn này trên tiêu đề |
| Đồ ăn/lần đầu (FOOD_FIRST) | Ăn uống, "first time" | 3,4M / 0,5M | — (n=4) | 0% | 50% | Cầu gần như bằng 0 trong mẫu |

Ba điểm trong bảng làm thay đổi kết luận của báo cáo RPM ngày 2026-11-03. Điểm thứ nhất, **cầu kinh dị nằm ở khung gameplay, không ở nhãn thể loại**. Kinh dị gameplay có trung vị video dài 41K và 20 video vượt 100K trong 7 ngày. Kinh dị hư cấu chỉ có trung vị 2,8K và 4 video vượt 100K, cả 4 đều từ kênh lớn như Bionic (8,9M subs) và BeckBroJack (5,5M) (OBSERVED). Vì vậy làn "vũ trụ kinh dị-bí ẩn" mà OWNER chọn làm làn chính vẫn đứng được, với điều kiện tiêu đề đọc như phim sinh tồn hay gameplay ma ám, không đọc như "ARG/found footage" (INFERRED). Điểm thứ hai, **"đồ ăn lần đầu" không có cầu**. Ngách này chỉ có 4 video trong 7 ngày, và video dẫn đầu là "I Tried Every Minecraft Food!" của Nolan, một kênh 3,55M subs ([video](https://www.youtube.com/watch?v=41cbKN_LHXA)) (OBSERVED). Nguyên tắc S5 "Baby Zombie Zu Tries PIZZA for the First Time" trong file nguyên tắc nên hạ xuống mức "theo dõi" (INFERRED). Điểm thứ ba, **tiền nằm ở video dài dù view nằm ở Shorts**. Quy đổi Shorts theo tỷ lệ RPM 3–14% của OWNER, cầu tương đương video dài là 106–170M. Trong đó video dài chiếm 52–83%, và các ngách nặng nhất sau quy đổi là roleplay gameplay (18,3M), mô phỏng (15,3M) và kinh dị gameplay (14,7M) (INFERRED, [derived_A_rpm_weighted_demand.csv](<../research_notes/Quét ngách Minecraft bằng YouTube API/data/derived_A_rpm_weighted_demand.csv>)).

Ở đầu các từ khoá rộng là thị trường Shorts hàng triệu view. Với từ khoá "minecraft" trong 7 ngày, cả 50 kết quả đều trên 1M view, trung vị 3,50M, và 78% có độ dài ≤3 phút. Từ khoá dài thì nhỏ hơn hẳn: "minecraft 100 days" có trung vị 164K và chỉ 8% là Shorts, "minecraft analog horror" 32K, "minecraft found footage" 367 (OBSERVED, [search_hits.csv](<../research_notes/Quét ngách Minecraft bằng YouTube API/data/search_hits.csv>)). Một phần nguyên nhân là kết quả từ khoá dài lẫn video độn ít view (INFERRED). Video dài lớn nhất 7 ngày là [10,000 Player Minecraft War: Nether VS Overworld](https://www.youtube.com/watch?v=bHxLy6Qza3M) của Parrot, kênh 4,45M subs: **7,2M view sau 2,1 ngày**. Shorts lớn nhất là [This feels like a scene from interstellar](https://www.youtube.com/watch?v=Jl-KVNhnMjo) của lowkiMC, kênh 98K subs: **18,9M view sau 2,8 ngày** (OBSERVED).

## Kênh mới trong kết quả tìm kiếm: nhiều ở Shorts, hiếm ở video dài

Cột "kênh mới" ở bảng trên che mất một sự thật. **Nếu bỏ hết video dùng IP bên thứ ba, hoạt hình trẻ em chỉ còn 12 Shorts vượt 100K trong 7 ngày, giảm từ 81. Nhưng 11/12 video còn lại đến từ kênh ≤12 tháng tuổi** (OBSERVED). Nói cách khác, hoạt hình IP gốc đang *thiếu người làm* hơn là *thiếu người xem*. Mười hai hit mỗi tuần là trần thực tế, không phải 81 (INFERRED). Bảng sau chọn các kênh mới tiêu biểu xuất hiện trong kết quả tìm kiếm, tất cả đều không dùng IP bên thứ ba trong tiêu đề, kèm ngách và định dạng của từng kênh (OBSERVED, [A_niches_leaders_outliers.md](<../research_notes/Quét ngách Minecraft bằng YouTube API/A_niches_leaders_outliers.md>) mục Q3).

| Kênh (tuổi kênh, subs) | Ngách / định dạng | Video | View, tuổi video | ÷subs | ÷trung vị kênh |
|---|---|---|---|---|---|
| Mochi & Pals (19 ngày, 1,1K) | Lựa chọn/thi đấu mini, Short 16 giây | [Who can dig down the fastest?](https://www.youtube.com/watch?v=nf9oZPSqhjE) | 1,42M, 2,3 ngày | 1.344× | 28× |
| CHIRAG FACTO (11 ngày, 26K) | Hài hoạt hình Steve, Short 35 giây | [Slither Run with Steve](https://www.youtube.com/watch?v=xel-UZ5bf1s) | 2,62M, 2,2 ngày | 101× | 13,5× |
| Verity Verifies MC (9 ngày, 1,8K) | Mẹo cơ chế, Short ~50 giây | [How To Use Copper Golems Perfectly...](https://www.youtube.com/watch?v=3U2_rB7SrZ0) | 1,35M, 5,4 ngày | 754× | 56× |
| parsamehrj (30 ngày, 1,1K) | Build/farm, Short | [I Built a Farm in Minecraft That Automatically Collects…](https://www.youtube.com/watch?v=njGzqtWPgAk) | 828K, 6,0 ngày | 767× | 45× |
| SohilXCraft (33 ngày, 347) | Hài hoạt hình mob, Short | [Minecraft Villagers vs Pillagers](https://www.youtube.com/watch?v=B_xrdABjn48) | 254K, 4,2 ngày | 732× | 206× |
| Mob Academy (33 ngày, 369) | Hoạt hình Monster School, Short | [Monster School: Trick or Treat](https://www.youtube.com/watch?v=RhoKbtVwLXc) | 114K, 4,7 ngày | 309× | 43× |
| Whitye (88 ngày, 138K) | Mẹo/điểm yếu mob, Short | [Minecraft Mobs Weaknesses !](https://www.youtube.com/watch?v=7D8-j8lFu2s) | 2,5M, 4,0 ngày | 18,5× | 33× |
| Wablo (114 ngày, 254K) | Hài hoạt hình, Short | [Creator just wanted to do his job](https://www.youtube.com/watch?v=BJ1XeW9_6rE) | 4,3M, 4,9 ngày | 17× | 2,3× |
| melZerry (319 ngày, 26K) | Cơ chế/vật lý lạ, Short | [Water can build PRESSURE in minecraft??](https://www.youtube.com/watch?v=5dwJxih_if8) | 4,3M, 4,7 ngày | 165× | 32× |
| **Kit vs The End** (37 ngày, 9,7K) | **Sinh tồn có kịch bản, dài 73 phút** | [Zombie Outbreak: 100 Days Trapped On A Zombie Cruise Ship… (Full Movie)](https://www.youtube.com/watch?v=xdj5PL0t61k) | 673K, 10 ngày | 69× | 34× |
| **Day Zero** (29 ngày, 13,9K) | **Sinh tồn có kịch bản, dài 40 phút** | [I Survived 100 Days in a DEADLY OUTBREAK](https://www.youtube.com/watch?v=eAqPRLb9JQg) | 370K, 11 ngày | 27× | — |
| **SirCloaked** (346 ngày, 141K) | **Kinh dị gameplay, dài 18 phút** | [Something On My Farm Wants Me Dead...](https://www.youtube.com/watch?v=VYFy1FN7-tk) | 956K, 8,2 ngày | 6,8× | 2,2× |
| **Clooless Gaming** (347 ngày, 318K) | **Kinh dị/thử thách mod, dài 59 phút** | [Beating Minecraft With The Phobia Mod](https://www.youtube.com/watch?v=fHGRgKgIbAU) | 1,21M, 5,9 ngày | 3,8× | 2,5× |

Bốn dòng in đậm là toàn bộ bằng chứng "kênh trẻ phá được bằng video dài IP gốc" trong 15 ngày, và cả bốn đều là **sinh tồn hoặc kinh dị có mối đe dọa cụ thể** (OBSERVED). Bốn ca chỉ là bằng chứng rằng việc này *làm được*, chưa đủ để ước một *tỷ lệ thành công* (INFERRED). Cũng cần trừ hao vì "kênh ≤12 tháng tuổi" đếm dư người mới thật. Nhiều kênh trông như mới thực chất là kênh phụ của creator lớn: CashMovies (của Cash), Niz unseen, BionicTV, Joeysaf Clips, zedarextra. API không cho biết chủ sở hữu kênh, nên chưa kiểm được (INFERRED). Ở Shorts, các kênh vài trăm đến vài nghìn subs đạt 100K–1,4M bằng ý tưởng gốc là đủ nhiều. Shorts là động cơ khám phá thực tế cho Bin, Bo và Zu (INFERRED).

## Người dẫn đầu mỗi ngách và các outlier của họ lặp cùng một công thức

Hầu hết ngách con do một hoặc hai kênh nắm 25–50% lượt xem 7 ngày. Trong 116 suất "top leader", chỉ 15 suất là kênh ≤12 tháng tuổi. Ngoài nhóm trẻ em và nhóm dùng IP, các suất đó đều là kênh Shorts (OBSERVED, [derived_A_leaders_by_niche.csv](<../research_notes/Quét ngách Minecraft bằng YouTube API/data/derived_A_leaders_by_niche.csv>)). Bảng dưới liệt kê kênh dẫn đầu của các ngách liên quan tới studio. Cột "Outlier gần đây" lấy video ≤30 ngày tuổi có view ≥3 lần trung vị cùng định dạng của kênh, hoặc ≥ số subs. Cột "Bùng nổ 5 ngày đầu" lấy video 0,5–5 ngày tuổi có view ≥2 lần trung vị, hoặc có view/ngày ≥3 lần nhịp thường của kênh (OBSERVED, [derived_A_leader_outliers_30d.csv](<../research_notes/Quét ngách Minecraft bằng YouTube API/data/derived_A_leader_outliers_30d.csv>), [derived_A_explosive_first5d.csv](<../research_notes/Quét ngách Minecraft bằng YouTube API/data/derived_A_explosive_first5d.csv>)).

| Ngách | Kênh dẫn đầu (thị phần 7 ngày, subs) | Outlier gần đây / bùng nổ 5 ngày đầu |
|---|---|---|
| Sinh tồn có kịch bản | Ryguyrocky (7%, 3,9M), Luke TheNotable (7%, 4,9M) | [I Survived 100 Days as a Necromancer](https://www.youtube.com/watch?v=--0KP-bA0p4) 621K sau 3,3 ngày; chưa có trung vị kênh (không lấy danh sách upload) |
| Kinh dị gameplay | ProBoiz 95 (32%, 9,4M), Clooless Gaming (6%, 318K) | [Testing Trending Minecraft Scary Myths…](https://www.youtube.com/watch?v=ls0FQdzVxko) 6,3M sau 6,2 ngày; Clooless [Beating Minecraft With The Disabilities Mod](https://www.youtube.com/watch?v=QZ-cOjajyYg) 821K sau 1,9 ngày, tốc độ gấp 13 lần nhịp thường của kênh |
| Roleplay gameplay | Cash (15%, 11,8M), Karry Kraft (10%, 1,8M), Aphmau (9%) | Karry Kraft [This Scary Tree Monster Destroyed Our World](https://www.youtube.com/watch?v=TFHP1mPdKrY) 1,6M; Aphmau [The VAMPIRE LORD KIDNAPPED Me: The MOVIE!](https://www.youtube.com/watch?v=81tl9y0wt7w) 901K sau 2,9 ngày |
| Thử thách | Joeysaf (28%, 489K), Beppo (8%, 2,4M) | Joeysaf [Minecraft But Every Basic Rule Is Reversed](https://www.youtube.com/watch?v=gNosQvKuGLA) 6,9M = 14× subs; Beppo [Achievement = 1 Block](https://www.youtube.com/watch?v=Sv78gB7zi_E) 3,5M |
| Hài hoạt hình | PumpBrine (47%, 100K), BlobbyClips (13%, 2,8M), Wablo (10%, 254K) | PumpBrine "Smartest Player VS Dr Donut" 12,5M = 40× trung vị; BlobbyClips [When Mobs Get Smart!](https://www.youtube.com/watch?v=4O-1iZb1Wz4) 50,1M; Wablo [There is an imposter in my house](https://www.youtube.com/watch?v=BIp5kzK-axs) 16,1M |
| Hoạt hình trẻ em | Cheesy Animation (10%), Minoku, Mikey Crazy, tất cả là fan JJ | [No One Helped Evil JJ…](https://www.youtube.com/watch?v=Rwx6b2ngh5w) 10,2M; ca IP gốc: OLD Legends 360 [Herobrine Sir's Death](https://www.youtube.com/watch?v=lBgA2rtLaug) 264K = 192× trung vị |
| Build | wykull (13%, 253K), melZerry (12%, 26K) | wykull [Making a REALISTIC Basketball Hoop](https://www.youtube.com/watch?v=L5U1hAWXUDs) 14,3M = 23× trung vị; melZerry [RING WORLD](https://www.youtube.com/watch?v=1BZ9WsSCVUs) 4,9M = 36× |
| Mẹo/cơ chế | Whitye (20%, 138K), camman18 (17%, 11,4M) | Whitye [sleep on a BED and a STRAW BED at the same time](https://www.youtube.com/watch?v=NSnW6uoocuI) 1,9M = 25× trung vị |
| Kinh dị hư cấu | Bionic (39%, 8,9M), BeckBroJack | [3 idiots vs The Broken Script](https://www.youtube.com/watch?v=25tihyuEO6g) 633K; ca nhỏ: noblevox [Interrogating Parrot (found footage)](https://www.youtube.com/watch?v=TprsWvdq7Zs) 219K = 501× trung vị |

Điểm chung của các outlier ở kênh dẫn đầu là **một tiền đề được đánh số và lặp lại**, không phải ý tưởng đứng riêng lẻ. PumpBrine chạy "Smartest Player VS …" từ Part 2 tới Part 38. Joeysaf chạy "Minecraft But …". wykull chạy "REALISTIC … in Minecraft". Wablo làm hai phiên bản "There is an imposter in my house" (OBSERVED tiêu đề, INFERRED quy luật). Các vụ bùng nổ 5 ngày đầu mạnh nhất đều thuộc về tài khoản nhỏ hoặc trẻ. Tiêu biểu là lowkiMC (gấp 565 lần trung vị), SohilXCraft (206×) và Mob Academy (43×). Tỷ số "view/ngày so với nhịp thường" bị phóng đại ở kênh tí hon: nhịp thường chỉ 25–165 view/ngày thì video 100K nào cũng thành ×500+. Vì vậy, khi ra quyết định phải đọc cùng lúc ÷trung vị, ÷subs và view tuyệt đối (INFERRED). Có một lỗ hổng lớn: **78/116 suất leader không có danh sách upload**, nên trung vị video dài của Parrot, ProBoiz 95, Cash, Aphmau, Ryguyrocky và Karry Kraft **chưa đo được**. Đây là việc đầu tiên cần làm ở lần đo tới.

## Không kênh 0–30 ngày nào đạt 2 video dài 1M, nhưng năm định dạng lặp lại

Chạy đúng luật OWNER (kênh tạo ≤30 ngày, có ≥2 video dài >3 phút mỗi video ≥1M) trên tập gộp upload ∪ kết quả tìm kiếm, tổng 13.622 video, cho kết quả **0 kênh** (OBSERVED, [B_new_competitors.md](<../research_notes/Quét ngách Minecraft bằng YouTube API/B_new_competitors.md>)). Mẫu có 77 kênh 0–30 ngày tuổi, 59 trong số đó là kênh tiếng Anh. 20 kênh có video ≥100K, 7 kênh có video ≥1M, nhưng **chỉ 1 kênh có video dài ≥1M**. Mở rộng sang toàn bộ kênh tiếng Anh ≤365 ngày: 113 kênh có Short ≥1M, chỉ 17 kênh có video dài ≥1M, và 8 kênh có từ 2 video dài 1M trở lên (OBSERVED). Ngày tạo kênh lấy từ trường `publishedAt` của API, chưa đối chiếu ngày "Joined" trên trang About như luật B yêu cầu. Kênh bị đổi tên hoặc dùng lại có thể trông cũ hoặc mới sai lệch.

| Kênh (tạo ngày, tuổi, subs) | Video lớn nhất | View | ÷subs | View/ngày | IP |
|---|---|---|---|---|---|
| **Day Zero** ([kênh](https://www.youtube.com/channel/UCU9XwWmgsDdGRHXjrE0ewmQ); 2026-10-05, 29 ngày, 13,9K) | [I Survived 100 Days in a REALISTIC APOCALYPSE](https://www.youtube.com/watch?v=crnpqkov3ps), 52:00 | 1.894.197 | 136× | 70.270 | Gốc (modpack, map có ghi nguồn) |
| | [I Survived 100 Days in a DEADLY OUTBREAK](https://www.youtube.com/watch?v=eAqPRLb9JQg), 40:30 | 370.330 | 27× | 33.477 | Gốc |
| Banazen Craft ([kênh](https://www.youtube.com/channel/UCK0DXOEQLQ_YkP2x1jddjsw); 2026-10-25, 9,5 ngày, 4,3K) | [JJ and Mikey Grow SECRET VERITY from Seeds](https://www.youtube.com/watch?v=uah6ikSydJ8), 15:15 | 394.077 sau 2,25 ngày | 92× | 175.134 | Fan Maizen + Verity |
| Ziggy Blox ([kênh](https://www.youtube.com/channel/UCVFgxz89Ond56851oZHAcrg); 2026-10-10, 24 ngày, 61,1K) | [I Fooled a Million Zombies 😱](https://www.youtube.com/watch?v=vH0pd4SomN8), 2:21; thêm 5 video khác ≥1M | 9.357.584 | 153× | 703.963 | Gốc (POV + mob Mojang) |
| Erzxck ([kênh](https://www.youtube.com/channel/UCDCDdtu2ldfNCJJfrLEqRWw); 2026-10-12, 22 ngày, 17,3K) | [Minecraft Verity Match The Block Game](https://www.youtube.com/watch?v=31tzZ_Y3n4c), 1:15 | 12.072.020 | 698× | 1.023.115 | Verity (bên thứ ba) |
| CHIRAG FACTO (2026-10-23, 11 ngày, 26K) | [Slither Run with Steve](https://www.youtube.com/watch?v=xel-UZ5bf1s), 0:35 | 2.623.353 | 101× | 1.194.885 | Steve/Alex; có dấu hiệu nhồi tag |
| Verity Verifies MC (2026-10-25, 9 ngày, 1,8K) | [How To Breed Horses Perfectly...](https://www.youtube.com/watch?v=K7xFyRmxoB0), 0:53 | 1.669.935 | 933× | 374.495 | Chỉ mượn tên |
| Mochi & Pals ([kênh](https://www.youtube.com/channel/UC8BAM9FulzAucO3ENpk-yqA); 2026-10-15, 20 ngày, 1,1K) | [Who can dig down the fastest?](https://www.youtube.com/watch?v=nf9oZPSqhjE), 0:16 | 1.424.438 | 1.344× | 631.528 | Gốc (Mochi, Pickles, Bubbles) |

**Day Zero là ứng viên gần nhất và cũng là ca tự nhiên nhất.** Video 1,89M có 1,25% lượt thích và 766 bình luận. Phần mô tả ghi rõ "cinematic story-telling ... may contain planned events" và có ghi nguồn map Planet Minecraft (OBSERVED). Với tốc độ 33K view/ngày, video thứ hai cần khoảng 19 ngày nữa để chạm 1M nếu tốc độ giữ nguyên. Thực tế view thường giảm nhanh hơn, nên đây là ước tính lạc quan (INFERRED). Banazen Craft có vận tốc thô cao nhất, nhưng là kênh fan Maizen. Ở nhóm 31–180 ngày, các video dài 1M+ đáng nghi hoặc mượn IP. EvanavE có VOD dài 3–4 giờ với 1,14M view nhưng chỉ 0,05% lượt thích. MineBraintor có "vertical live" 982K view nhưng ẩn lượt thích và 0 bình luận. Đây là bất thường do bề mặt phân phối (trang live), nên **loại khỏi mọi trung vị chuẩn** (INFERRED từ tỷ lệ tương tác OBSERVED). Một lưu ý về Kit vs The End: tag ghi "stickman", nên video này có thể không render bằng Minecraft dù tìm kiếm Minecraft trả về nó. Cấu trúc sinh tồn của nó vẫn học được (INFERRED).

Các video triệu view của kênh mới gom về **năm định dạng lặp lại**. Nhãn "IP gốc" ở đây là phân loại tay từ tiêu đề và mô tả (OBSERVED văn bản, INFERRED phân loại).

1. **Sinh tồn điện ảnh 100 ngày.** Dài 40–73 phút. Tiêu đề kiểu "I Survived 100 Days in a [TÍNH TỪ VIẾT HOA] [mối đe dọa]", có thể thêm một luật sống còn: "One Sound And They Find You".
2. **Truyện mini góc nhìn thứ nhất, cải trang/xâm nhập.** Dài 2–2,5 phút. Ví dụ "I Fooled / Pretended / Crashed / Snuck…" của Ziggy Blox. Mô tả nêu luật kèm hình phạt hài: "any human found before sunrise becomes the Zombie King's butler forever".
3. **Shorts game show cho nhân vật.** Dài 15–100 giây. Ví dụ "Who can X fastest?", "Match the Block".
4. **Shorts mẹo kiểu "How To X Perfectly..."** dài khoảng 50 giây, thường gắn với mob mới của bản vanilla như Copper Golem.
5. **Phiêu lưu bộ đôi kiểu Maizen.** Dài 10–21 phút, gồm hai bạn, một em gái và một quái vật.

Trong 6 kênh tiếng Anh ≤30 ngày có video 1M+, **5 kênh dùng nhân vật gốc hoặc chỉ dùng nhân vật Mojang**. Thứ chúng mượn là *định dạng*, không phải nhân vật. Erzxck là bài học ngược lại: cùng một trò chơi, kênh chỉ đạt 8–40K view với nhân vật "Squishy". Sau khi đổi sang nhân vật Verity dễ nhận diện từ ngày 2026-10-20, view vọt lên 300K–12,07M (OBSERVED). Bài học cho Bin, Bo và Zu là sức nhận diện nhân vật kéo Shorts. Vì vậy dàn nhân vật phải nhất quán về hình và được lặp lại nhiều, chứ không phải đi mượn (INFERRED).

**Watchlist cập nhật có 32 kênh** ([watchlist_2026-11-04.csv](<../research_notes/Quét ngách Minecraft bằng YouTube API/data/watchlist_2026-11-04.csv>)), chia ba nhóm:

- **13 kênh cũ.** Chỉ 8 kênh xuất hiện trong mẫu API, và chỉ Ligabka với JJ Cartoons có danh sách upload.
- **8 kênh mới (trạng thái `new`):** Day Zero, Banazen Craft, Ziggy Blox, Erzxck, CHIRAG FACTO, Verity Verifies MC, Mochi & Pals, SlivaCraft.
- **11 kênh thêm vì đang có outlier (trạng thái `old`):** Mikey & JJ Verse, Cody Toon, Wablo, Kit vs The End, Chase Liminal, imKaiL00L, Spoke, Bench Animation, Gamity, cùng MineBraintor và EvanavE (hai kênh này bị gắn cờ nghi ngờ).

Theo luật OWNER, kênh vào danh sách rồi sẽ được theo dõi như đối thủ cũ (OWNER, [minecraft_story_rules.md](<../config/research/minecraft_story_rules.md>)). Ba luật đó được cụ thể hoá thành ngưỡng đo như sau (INFERRED):

- **R1:** view ≥10× subs và ≥500K.
- **R2:** video ≤15 ngày, ≥3× trung vị cùng định dạng, và ≥300K.
- **R3:** video ≤5 ngày, và hoặc ≥100K view/ngày kèm ≥2× trung vị, hoặc ≥5× trung vị kèm ≥100K view.

Trên các kênh >30 ngày tuổi, 45 video dài tiếng Anh đạt ít nhất một luật. Các ca đáng chú ý gồm Cubeee với compilation 54 phút (2,20M sau 7 ngày, 44× subs), [Poolrooms - The Snake Lady](https://www.youtube.com/watch?v=VRrWXv1S1M4) của Chase Liminal (2,05M, 123× subs) và [Horror Minecraft, but Drops are Guns](https://www.youtube.com/watch?v=H6yj4XbkHhk) của imKaiL00L (2,96M, 5,3× trung vị) (OBSERVED). Luật R1 đứng riêng thì quá lỏng với kênh nhỏ: 205/231 kênh có lịch sử upload có ít nhất một video đạt luật nào đó. Vì vậy R1 nên luôn đi kèm ngưỡng view tuyệt đối (INFERRED).

## 547 video 1M+ trong 15 ngày: phần lớn đang chậm lại, video dài giảm tốc chậm hơn

Sau khi lọc ngôn ngữ và bỏ video không phải Minecraft, mẫu còn **547 video ≤15 ngày tuổi có ≥1M view. Có 496 Shorts từ 209 kênh, trung vị 2,13M view và 333K view/ngày. Có 51 video dài từ 36 kênh, trung vị 1,74M và 203K view/ngày.** 49/51 video dài thuộc kênh ≥100K subs (OBSERVED, [derived_C_1m_le15d_en_minecraft.csv](<../research_notes/Quét ngách Minecraft bằng YouTube API/data/derived_C_1m_le15d_en_minecraft.csv>)). Với kênh nhỏ (<100K subs), có **157 Shorts 1M+ từ 89 kênh, tất cả đều ≥10× subs, trung vị 76,7×**. Cũng nhóm kênh đó chỉ có **2 video dài 1M+**: một compilation JJ & Mikey và bài bình luận "Dream Cheated Every World Record" của MrMangoHands (3,34M view trên 3K subs, khoảng 1.325×). Tức là một kênh nhỏ đạt 1M trong 15 ngày gần như chắc chắn là nhờ Shorts (OBSERVED).

Tốc độ được đo bằng hai lần chụp cách nhau trung vị 15,9 phút (11,5–16,4 phút). Đây là ảnh chụp "tốc độ ngay lúc này", chưa phải đường cong theo ngày. Kết quả chính là phần lớn đang suy giảm. Shorts trung vị chạy ở **0,16 lần** tốc độ trung bình cả đời, video dài ở **0,37 lần**. Chỉ 19 Shorts và 3 video dài còn đang tăng tốc (OBSERVED). Tính theo tuổi video, Shorts mất phần lớn tốc độ trong khoảng 2 ngày: tỷ số còn 0,44 lần ở ngày 1–2 và 0,08 lần ở ngày 10–15. Video dài giảm chậm khoảng một nửa: 0,80 lần ở ngày 1–2 và 0,35 lần ở ngày 10–15 (OBSERVED). Kit vs The End ở ngày thứ 10 vẫn giữ **0,90 lần** tốc độ trung bình cả đời, trong khi Ziggy Blox "I Fooled a Million Zombies" ở ngày 13 chỉ còn 0,03 lần (OBSERVED, [derived_C_snapshot2_growth.csv](<../research_notes/Quét ngách Minecraft bằng YouTube API/data/derived_C_snapshot2_growth.csv>)). Từ đó có thể suy ra Shorts mua sự chú ý trong 48 giờ, còn video dài mới tích luỹ thành tài sản (INFERRED).

| Đang tăng nhanh nhất (view/giờ giữa hai lần chụp) | Kênh, subs | View, tuổi | ×subs | Tốc độ, ×trung bình cả đời | IP |
|---|---|---|---|---|---|
| [Who Will ADOPT JJ Kitten?!](https://www.youtube.com/watch?v=glwTiwUdhJo) | XOXU MINECRAFT, 14K | 1,29M, 0,5 ngày | 90× | 175K/giờ, ×1,46 | JJ (bên thứ ba) |
| [Smartest Player VS Dr Donut Part 29](https://www.youtube.com/watch?v=ChumXJor8EA) | PumpBrine, 100K | 3,51M, 1,2 ngày | 35× | 140K/giờ, ×1,18 | Death Note, DrDonut |
| [10,000 Player Minecraft War](https://www.youtube.com/watch?v=bHxLy6Qza3M) | Parrot, 4,45M | 7,22M, 2,1 ngày | 1,6× | 103K/giờ, ×0,71 | Gốc |
| [Cushion in water](https://www.youtube.com/watch?v=IGiveq3olJU) | CheezyChez, 1,08M | 2,47M, 1,3 ngày | 2,3× | 89K/giờ, ×1,15 | Gốc |
| [DUMB the SOUND](https://www.youtube.com/watch?v=LKdjKUER3aY) | zedarGG, 232K | 3,39M, 6,2 ngày | 15× | 57K/giờ, ×2,50 | Gốc |
| [Minecraft game play with animation](https://www.youtube.com/watch?v=UiRv3wqFuIs) | Mrjunaid Short, 14K (kênh 41 ngày) | 2,39M, 3,3 ngày | 172× | 47K/giờ, ×1,57 | Gốc |
| [Bro Crafted Netherite Armor 💀](https://www.youtube.com/watch?v=ow9qGwMrSTk) | Mine Mythos, 16K | 3,25M, 7,0 ngày | 204× | 34K/giờ, ×1,76 | Gốc |
| [I destroyed BULLIES on my School's SMP...](https://www.youtube.com/watch?v=c47f1Gojteg) (dài) | RedishPlays, 8K | 175K, 5,1 ngày | 23× | 5K/giờ, ×3,26 | Gốc |

Khi gom tiêu đề, Shorts 1M+ tập trung vào bốn kiểu chính:

- **Meme cảm xúc kèm emoji:** 155 video, trung vị 355K/ngày.
- **"X vs Y / ai thắng":** 51 video.
- **Truyện gia đình/buồn:** 48 video, 60% dùng IP bên thứ ba.
- **Sinh tồn/thử thách:** 39 video.

Một số mẫu có tỷ lệ IP bên thứ ba thấp mà bội số lại cao: "Minecraft but…" (8% bên thứ ba), mod/vật phẩm mạnh (11% bên thứ ba, bội số trung vị 24×), và "then vs now/update" (bội số trung vị 34×). Shorts 1M+ có độ dài trung vị **37 giây**, khoảng giữa 18–60 giây. Video dài 1M+ trải đều từ 10 tới hơn 60 phút, gồm 13 video 20–30 phút và 14 video 30–60 phút (OBSERVED, [derived_C_pattern_summary.csv](<../research_notes/Quét ngách Minecraft bằng YouTube API/data/derived_C_pattern_summary.csv>)). Năm kênh BlobbyClips, Stonecraft Studios, PumpBrine, camman18 và Joeysaf chiếm 22% số Shorts 1M+. Vì vậy, một Short viral đơn lẻ trên kênh 1–10K subs không chứng minh kênh làm lại được (59 ca rơi vào nhóm ≥100× subs). Bằng chứng xu hướng tốt hơn là **kênh có từ 3 hit trở lên trong 15 ngày**, ví dụ Mikey Crazy, Ziggy Blox, Mine Mythos, MaizCr, melZerry (INFERRED).

## Vòng nghiên cứu hằng ngày và hai tầng nguyên tắc thành công

Quy trình dưới đây biến bốn luật A–D của OWNER thành một lần chạy API mỗi ngày (khung OWNER, chi tiết INFERRED). Ngân sách quota tính theo bảng giá chính thức: `search.list` tốn 100 đơn vị, các lệnh `list` khác tốn 1 đơn vị cho mỗi 50 ID ([Google quota cost table](https://developers.google.com/youtube/v3/determine_quota_cost)). Lần chạy hôm qua tự đặt trần 9.300 đơn vị. Nên chạy cùng giờ mỗi ngày, khoảng 19:00 UTC (02:00 giờ Việt Nam), để Δ 24 giờ so sánh được với nhau.

| Bước | Việc làm (chỉ API chính thức, chỉ đọc) | Quota ước tính | Kết quả và ngưỡng |
|---|---|---|---|
| 1. Chụp lại | `videos.list` cho mọi video đang theo dõi (795 ID hôm nay, cộng các video mới vào danh sách) | ~16–25 | Δ view 24 giờ, view/ngày, tỷ số tăng tốc; đánh dấu "tăng tốc" khi ≥1,25× và Δ >1K |
| 2. Watchlist (luật A + B) | `playlistItems` + `videos.list` cho 32 kênh | ~64 | R1/R2/R3 cho từng kênh; ghi outlier mới |
| 3. Trung vị leader còn thiếu | Lấy upload cho các leader chưa có trung vị (luân phiên khoảng 40 kênh/ngày, tổng 78 suất còn thiếu) | ~80 | Trung vị video dài thật cho Parrot, ProBoiz 95, Cash, Karry Kraft… |
| 4. Quét bùng nổ (luật C) | Khoảng 50 lệnh `search.list` (7 ngày): 18 từ khoá lõi + từ khoá theo làn của studio + 5 từ khoá xoay vòng lấy từ n-gram tiêu đề hôm trước; khoảng 10 lệnh cửa sổ 15 ngày | ~6.000 | Danh sách video 0–15 ngày ≥1M, kênh nhỏ ≥10× subs |
| 5. Kênh mới (luật B) | `channels.list` cho mọi kênh mới xuất hiện; lọc kênh ≤30 ngày tuổi; kiểm tay ngày "Joined" trên About | ~40 | Kênh ≤30 ngày có ≥2 video dài ≥1M → thêm vào watchlist; ứng viên gần đạt → trạng thái "theo dõi" |
| 6. Tổng hợp | `cf_research_stats.py` (trung vị, outlier); cập nhật `minecraft_story_principles.md`; ghi quyết định bằng `cf_decision.py` | 0 | Một báo cáo ngày với 3 đề xuất cho showrunner |

Tổng khoảng **6.300 đơn vị mỗi ngày**, còn dư để xử lý lỗi (INFERRED). Có ba quy ước cần giữ cố định giữa các ngày để số liệu so sánh được (INFERRED):

- Giữ nguyên bộ lọc ngôn ngữ. Video được coi là tiếng Anh khi audio/metadata bắt đầu bằng `en` hoặc để trống, tiêu đề không có chữ ngoài hệ Latin, và có ít hơn 2 từ chức năng của ngôn ngữ khác.
- Loại livestream replay khỏi các trung vị chuẩn.
- Đánh dấu kênh phụ của creator lớn sau khi kiểm tay.

Từ dữ liệu này rút ra hai tầng nguyên tắc. **Nguyên tắc dài hạn** là những gì đúng trên ít nhất 3 kênh độc lập, có từ trước năm 2026 và ít phụ thuộc IP bên thứ ba (INFERRED, từ bằng chứng OBSERVED đã dẫn). Thứ nhất, *mỗi tiêu đề bán một luật chơi hoặc mối đe dọa kèm một con số*. Ví dụ: "100 Days", "Achievement = 1 Block", "10,000 Players", "One Sound And They Find You". Thứ hai, *tiền đề thắng được đánh số và làm tiếp ngay*, giống PumpBrine, Joeysaf, wykull. Serial Shorts dạng "Part N" có trung vị 555K view/ngày. Thứ ba, *video dài giảm tốc chậm gấp đôi Shorts* (0,37 lần so với 0,16 lần), nên video dài là tài sản, còn Shorts là kênh tiếp cận. Thứ tư, *kinh dị đóng gói như gameplay hoặc sinh tồn, không dán nhãn thể loại* (trung vị 41K so với 2,8K). Thứ năm, *compilation hoặc "Full Movie" tạo thêm phút xem rẻ*. Ví dụ: Cubeee 54 phút đạt 2,20M; Kit vs The End 73 phút; [Jerry The Dog [FULL MOVIE]](https://www.youtube.com/watch?v=Ed74ounoOhc) của LookOut2DD đạt 2,73M. Cách này đóng góp trực tiếp vào KPI "số phút thành phẩm được duyệt mỗi tuần". Thứ sáu, *sức nhận diện nhân vật kéo Shorts*, như ca Erzxck. Nhưng IP gốc không bị thiệt ở mức trung vị. Thứ bảy, *thước đo chuẩn là trung vị ngách và kênh lặp lại được hit, không phải video đỉnh*.

**Nguyên tắc ngắn hạn** là các trend có ngày bắt đầu và cần đổi trạng thái liên tục. Bảng dưới ghi "lần đầu thấy" theo upload sớm nhất trong mẫu. Mẫu chỉ có tối đa 50 upload mỗi kênh, nên ngày thật có thể sớm hơn (OBSERVED ngày, INFERRED trạng thái). Mọi trend trong bảng đều "lần cuối thấy" ngày 2026-11-03.

| Trend | Lần đầu thấy | Bằng chứng | Trạng thái và mức phù hợp |
|---|---|---|---|
| Dịch zombie/tận thế, sinh tồn trong không gian kín | ≤2026-10-07 | Day Zero 1,89M; Kit vs The End 673K; Maizen [SURVIVING in BUS During ZOMBIE APOCALYPSE](https://www.youtube.com/watch?v=UH1HSIN4L20) 4,9M; Clooless [Modded Zombie Apocalypse](https://www.youtube.com/watch?v=n06Hx1wLgfY) 883K | **Đang nóng · dùng được** |
| POV cải trang/xâm nhập đám đông quái vật | 2026-10-21 | Ziggy Blox có 6 video ≥1M trong 24 ngày | Đang nóng · dùng được |
| Thi đấu mini cho dàn nhân vật nhỏ ("Who can X fastest?") | ≤2026-11-01 | Mochi & Pals 1.344×; Tg Jamal 188× | Đang nóng · dùng được |
| Tính năng vanilla mới (Copper Golem, đồ đồng, snow bricks) | chưa xác định | Verity Verifies MC 1,35M; Midmysticx [NEVER build FULLY out of COPPER](https://www.youtube.com/watch?v=_EDGsXxTqIA) 3,3M; camman18 [SNOW BRICKS HAVE BEEN ADDED](https://www.youtube.com/watch?v=wuMmOolFhqA) 2,2M | Đang nóng · dùng được; lặp lại theo mỗi game drop |
| Hoài niệm "Before Google"/"Beta players" | 2026-09-12 | Mine Mythos [Minecraft Before Google 💀](https://www.youtube.com/watch?v=VPpYNzsYCPg) 8,2M (516×) | Theo dõi · dùng được |
| "[TÍNH TỪ] the SOUND" | 2026-09-19 | zedarGG 3,39M, đang tăng tốc ×2,5; 5 kênh | Theo dõi · meme, vòng đời ngắn |
| "Smartest Player VS Dr Donut Part N" | 2026-09-15 | PumpBrine 19 hit; 86% số upload kiểu này nằm trong 15 ngày gần nhất | Đang nóng · **tránh** (Death Note + creator thật) |
| Dark/Evil JJ, "No One Helped JJ…" | 2026-09-15 | [No One Helped Dark JJ…](https://www.youtube.com/watch?v=9Klhof7JJIw) 13,8M | Đang nóng · chỉ học công thức "không ai giúp → cứu" |
| "1 or 2: JJ … Reaction", Kpop Head Trap Challenge | 2026-10-17/18 | Stonecraft Studios; darix 8,0M | Đang nóng · tránh (IP bên thứ ba) |
| Làn sóng Verity, Jerry the Wolf | 2026-06-21 / 2026-08-31 | 703 upload có Verity trong mẫu; [nguồn gốc Verity](https://trending.knowyourmeme.com/editorials/guides/what-is-verity-the-viral-minecraft-horror-arg-web-series-and-its-me-its-verity-memes-explained) | Đã ~5 tháng · tránh |
| Halloween | mùa vụ | Tiêu đề Halloween đầy rẫy trong tháng 10 | **Hết hạn sau 2026-10-31**; mùa tiếp theo (Lễ Tạ ơn/Giáng sinh) chưa có bằng chứng, cần quét |

Để đi trước trend, cần đo hai thứ. Thứ nhất là *ngày lần đầu thấy* của một mẫu tiêu đề trên ≥3 kênh độc lập. Thứ hai là *tỷ số tăng tốc* giữa các lần chụp. Một mẫu IP gốc xuất hiện trên 3 kênh nhỏ trong vòng 7 ngày, có video ≥1,25× tốc độ cả đời, là tín hiệu nên làm ngay. Trend dựa vào nhân vật người khác thì chỉ học cấu trúc (INFERRED).

## Những gì ảnh chụp này không nói được

Dữ liệu là một ảnh chụp được xếp hạng, không phải một cuộc tổng điều tra. Có chín giới hạn cần nhớ (OBSERVED, [api_dataset.md](<../research_notes/Quét ngách Minecraft bằng YouTube API/api_dataset.md>)):

1. **Mỗi truy vấn chỉ trả một trang tối đa 50 video**, do YouTube xếp hạng. 11/84 truy vấn trả về ít hơn 50, và 2.373/2.827 video chỉ do một từ khoá tìm ra.
2. **Nhóm video 7–15 ngày tuổi bị lấy mẫu thiếu**, vì chỉ có 18 từ khoá chạy cửa sổ 15 ngày.
3. **Bộ lọc `relevanceLanguage=en` và `regionCode=US` bị rò rỉ.** Có 728 video audio không phải tiếng Anh. 1.009 video để trống trường audio, nên "US/tiếng Anh" ở đây nghĩa là *nói tiếng Anh*, không phải khán giả Mỹ.
4. **Subs công khai bị làm tròn** tới 3 chữ số có nghĩa ([RivalIQ](https://help.rivaliq.com/en/articles/9788197-why-youtube-subscriber-counts-are-rounded)), nên bội số view/subs của kênh 1–3K subs khá thô.
5. **"Shorts" được định nghĩa là ≤180 giây**, vì API không có cờ Shorts ([Tubefilter](https://www.tubefilter.com/2024/10/03/youtube-shorts-three-minutes-max-length-redesign-trends-templates/)). Video dài ≤3 phút bị xếp nhầm thành Shorts.
6. **Đo tốc độ chỉ có 16 phút giữa hai lần chụp, chưa có Δ 24 giờ.** Video 1,89M của Day Zero không nằm trong lần chụp thứ hai.
7. **Ngày tạo kênh là `publishedAt`**, chưa đối chiếu ngày "Joined" trên trang About. Kênh phụ của creator lớn chưa được loại.
8. **Phân loại ngách là regex kèm một phần kiểm tay. Tỷ lệ lỗi phân loại chưa đo.** Cờ IP chỉ xét tiêu đề, nên tỷ lệ phụ thuộc IP là cận dưới.
9. **Không có retention, CTR, nguồn traffic, tuổi khán giả hay RPM.** Cờ `made_for_kids` chỉ bật ở 3/2.827 video, và đó là khai báo của người đăng, không phải số đo khán giả.

Hệ quả là các bảng xếp hạng ngách ở trên đọc được *hướng*, nhưng chưa đọc được *xác suất thành công*. Với video dài, bằng chứng cho kênh mới chỉ gồm 4 ca (INFERRED).

## Khuyến nghị: series dịch zombie trước, ba kiểu Shorts gốc làm phễu

**Nên làm trước làn sinh tồn có kịch bản, đóng gói như kinh dị gameplay, ở chế độ Not Made for Kids với giọng "creepy-cute" (đáng yêu pha rờn rợn)** (INFERRED từ các số OBSERVED đã dẫn). Làn này có nhiều bằng chứng nhất cho kênh mới làm IP gốc: Day Zero, Kit vs The End, SirCloaked và Clooless. Nó khớp với làn phụ "Day 1 → Day 100" của OWNER. Mạch bí ẩn của làn chính OWNER có thể chạy xuyên suốt series. Về độ dài, nên làm theo đường Kit vs The End vì hợp năng lực một GPU RTX 3060: tập lẻ 10–12 phút (trung vị video dài của Kit là 10:45), cứ 4 tập gộp thành "Full Movie" 45–50 phút, thay vì làm thẳng một video 50 phút như Day Zero. Song song, chạy ba kiểu Shorts IP gốc (15–60 giây, khớp trung vị 37 giây của Shorts 1M+) làm phễu và làm phép thử sức hút của nhân vật. Nhịp đề xuất là một tập dài mỗi tuần và 3–5 Shorts mỗi tuần. Các kênh dài thắng đăng 1 video mỗi 3–16 ngày, nên nhịp này đủ cạnh tranh (OBSERVED nhịp đăng, INFERRED mức sản lượng). Cần tránh: dùng mọi tên JJ/Mikey/Verity/Dr Donut/Jerry/Kpop trong tiêu đề hoặc tag, dùng nhãn "ARG/found footage" trên tiêu đề, nhồi tag kiểu CHIRAG FACTO, và đổ thời gian vào các ngách cần người chơi thật (mô phỏng, manhunt, SMP).

Có một điểm **cần OWNER quyết**, báo cáo không quyết thay. File `minecraft_story_principles.md` hiện mô tả Bin, Bo và Zu là "family brand for children" (thương hiệu gia đình cho trẻ em). Báo cáo RPM ngày 2026-11-03 và dữ liệu hôm nay lại nghiêng về giọng teen, Not MFK. Hai hướng này cho RPM chênh khoảng 80–85% (INFERRED trong báo cáo RPM), nên cần ghi quyết định bằng `python tools/cf_decision.py add …` trước khi viết kịch bản.

Năm concept dưới đây là đề xuất INFERRED cho showrunner. Không concept nào dùng nhân vật, tên, kịch bản hay hình ảnh của đối thủ.

| # | Concept (tiêu đề tiếng Anh cho thị trường US) | Định dạng | Học công thức từ (OBSERVED) | Đo thành công bằng |
|---|---|---|---|---|
| 1 | **"We Survived 100 Days in a Zombie Outbreak… But Our Little Brother IS a Zombie"**. Bin và Bo giấu baby zombie Zu trong thành phố bị dịch. Luật sống còn: "If the horde hears Zu cry, they find us". Có bộ đếm ngày, tập 1 là Day 1–25. | Dài 10–12 phút × 4 tập → "FULL MOVIE" 45–50 phút | Day Zero (luật và bộ đếm ngày), Kit vs The End (luật trong tiêu đề, gộp season), Maizen bus 4,9M | View 5 ngày và 28 ngày so với trung vị ngách (sinh tồn 47K, kinh dị gameplay 41K); % thời lượng xem |
| 2 | **"Something Is Following Our Village Every Night…"**. Truyện bí ẩn: dấu chân, đồ vật biến mất, bẫy camera. Tập này hé dần một sinh vật gốc của vũ trụ Bin-Bo-Zu. | Dài 18–22 phút (Pilot B của làn bí ẩn) | SirCloaked "Something On My Farm Wants Me Dead..." 956K; Karry Kraft [We Found GIANT SCARY FOOTPRINTS](https://www.youtube.com/watch?v=r1EUU26jrTM) 1,98M; CloudyDreamzs [There's an Angel Hiding in My World...](https://www.youtube.com/watch?v=Z8VHxBP6CII) 552K (24×) | So với concept 1 theo luật Pilot A/B của báo cáo RPM |
| 3 | **"Who can dig down the fastest? 🧱"**. Bin, Bo, Zu, mỗi nhân vật một cách riêng; đánh số Part 1, 2, 3… | Short 15–20 giây, 3 lần mỗi tuần | Mochi & Pals 1,42M (1.344×); serial "Part N" 555K/ngày | Nhân vật nào được bình luận và thả tim nhiều nhất → dùng nhân vật đó làm vai chính thumbnail |
| 4 | **"Bo Pretended to Be a Zombie to Get Zu Back 😱"**. POV cải trang lẻn vào đám zombie, có hạn giờ trước bình minh. Đóng vai trailer cho concept 1. | Short 45–60 giây (bản dài 2–2,5 phút nếu Short tốt) | Ziggy Blox "I Fooled a Million Zombies" 9,36M | Lượt chuyển sang video dài, subs từ Short |
| 5 | **"What Happens If a Baby Zombie Meets a Copper Golem??"**. Thí nghiệm cơ chế thật quay trên Java, Zu là "đối tượng thử". Phải kiểm chứng cơ chế trước khi viết lời. | Short 30–50 giây (làn thử OWNER "thí nghiệm dị thường") | melZerry "Water can build PRESSURE??" 4,3M (165×); Verity Verifies MC copper golem 1,35M; Whitye 2,5M | View ÷ trung vị kênh; tái dùng mỗi game drop |

**Việc cần đo lại ngày mai (2026-11-04/05, quota mới)**, theo thứ tự ưu tiên (INFERRED):

1. Chụp lại 795 video đã theo dõi, cộng hai video của Day Zero và ba video của Banazen Craft (~17 đơn vị). Mục tiêu là có Δ 24 giờ thật. Câu hỏi cụ thể cần trả lời:
   - Kit vs The End có giữ ≥0,8× tốc độ không?
   - Video thứ hai của Day Zero còn bao nhiêu ngày nữa thì chạm 1M?
   - Banazen Craft có vượt 1M không? Nếu có, đây là ca đầu tiên đạt luật B, dù là IP fan.
   - Mochi & Pals và Ziggy Blox có ra thêm hit không, hay chỉ là một cú may?
2. Lấy upload của khoảng 40 leader còn thiếu trung vị (~80 đơn vị). Ưu tiên kênh dẫn đầu làn sinh tồn và kinh dị: Ryguyrocky, Luke TheNotable, ProBoiz 95, Karry Kraft, Junkeyy.
3. Lấy upload của 5 kênh trong watchlist chưa có số mới: BigSchool, GameToons, Mine Block, Class Monster School, DL Minecraft (~10 đơn vị).
4. Chạy khoảng 15 truy vấn mới (~1.500 đơn vị) cho làn của studio: "minecraft zombie outbreak 100 days", "minecraft full movie survival", "something is following me minecraft", "minecraft disguise zombie", "who can dig fastest minecraft", "copper golem minecraft", "baby zombie minecraft", và từ khoá mùa vụ Lễ Tạ ơn/Giáng sinh.
5. Kiểm tay ngày "Joined" trên trang About của 8 kênh `new`.
6. Mở cổng `competitor-complete-study` cho video 1,89M của Day Zero và bản 73 phút của Kit vs The End, trước khi khẳng định bất cứ điều gì về nhịp dựng hay cách kể.

Cuối cùng, main session nên làm hai việc. Một là đồng bộ `config/research/minecraft_story_watchlist.txt` từ file CSV 32 kênh. Hai là cập nhật file nguyên tắc: thêm nguyên tắc dài hạn "kinh dị đóng gói như gameplay", hạ S5 (đồ ăn lần đầu) xuống "theo dõi", và chuyển S6 (Halloween) sang "hết hạn".

## Kết luận

Hôm qua câu hỏi còn là "ngách nào". Dữ liệu API hôm nay cho thấy với một kênh mới, câu hỏi đúng là "**định dạng nào trong ngách đó**". Ở cùng một ngách kinh dị, khung gameplay hay sinh tồn có trung vị video dài cao gấp khoảng 15 lần nhãn "found footage" (41K so với 2,8K). Ở cùng một ngách hoạt hình, gần chín phần mười Shorts vượt 100K của nhóm trẻ em dùng nhân vật người khác. Nhưng khi bỏ các video đó đi, phần IP gốc còn lại gần như do kênh mới nắm hết (11/12 video). Với studio, điều này có nghĩa là lợi thế không nằm ở việc chọn đúng một trend, mà ở một **công thức bền**: luật chơi kèm con số trong tiêu đề, tiền đề được đánh số để làm tiếp, video dài gộp thành "Full Movie". Ráp công thức đó vào một dàn nhân vật nhất quán, còn trend ngắn hạn chỉ đóng vai chất liệu bối cảnh.

Điều chưa biết lớn nhất là đường cong theo ngày. Mọi số "đang bùng nổ" hiện chỉ dựa trên 16 phút giữa hai lần chụp. Chỉ khi có Δ 24 giờ của Kit vs The End và Day Zero mới biết làn video dài sinh tồn là đường tăng trưởng đều hay một chuỗi đỉnh rời rạc. Câu trả lời đó quyết định nên đầu tư bao nhiêu giờ render cho tập 1 của series dịch zombie.
