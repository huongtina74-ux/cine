# Minecraft: kênh thành công vs kênh thất bại → chọn ngách kiếm tiền (2026-11-12)

Owner hỏi: "xem các kênh thành công và các kênh thất bại … ngách nào thực sự nên làm kiếm được nhiều tiền".
Phạm vi: chỉ Minecraft, long-form, faceless, tiếng Anh, IP gốc (theo khoá phạm vi và quyết định OWNER D-b75c6be8).
Đây là đề xuất (PROPOSED), owner chưa duyệt.

## 1. Cách đo (để không bị thiên lệch chỉ nhìn kênh thắng)
- Mẫu: tìm kiếm YouTube trên trình duyệt của owner lúc 2026-11-11 ~17:20Z. Có 7 ngách con × 6 truy vấn "minecraft …".
  Dùng bộ lọc **"Hôm nay"** (2 trang) và "Tuần này" (1 trang). Lọc "Hôm nay" kéo cả kênh có 0–50 view, nên **kênh thất bại có mặt trong mẫu**.
  Ta được 803 kênh, đều lấy qua `channels.list` (17 unit API, `enrich_meta.json`).
  Lọc tiêu đề tiếng Anh, có nội dung Minecraft, sub công khai còn 582 kênh. Loại tiếp 7 kênh spin-off của người nổi tiếng hoặc kênh lồng tiếng lại, còn **575 kênh**.
- Mọi số liệu đều đo một lần (OBSERVED), trừ chỗ ghi INFERRED/AGG-EST.
  - "Thất bại" = <1K sub, tức chưa đủ điều kiện YPP. "Thắng" = ≥10K sub.
  - Tuổi kênh = ngày tạo kênh. Kênh tạo trước khi vào ngách có thể làm số liệu lệch.
- Phân loại định dạng của 40 kênh thắng: dựa trên **tiêu đề và thời lượng 5 video mới nhất** trên trang /videos. Mức bằng chứng là METADATA_ONLY: không xem, không nghe.
- Giới hạn của cách đo:
  - Kết quả tìm kiếm xếp theo mức liên quan, kể cả với lọc "Hôm nay".
  - Mỗi ô có n nhỏ, nên kèm khoảng tin cậy Wilson 95%.
  - Một kênh có thể rơi vào nhiều ngách.
  - Không có retention, CTR hay RPM thật của các kênh này.
- Mã nguồn: `reports/research/success_failure_2026-11-12/sf_study.py`. Kết quả: `sf_study.md`, `sf_study.json`, `sf_channels.json`.

## 2. Kết quả: tỉ lệ thành công của kênh MỚI (≤365 ngày, có video ≥8 phút)

Thống kê theo **mọi người đang đăng**:

| Ngách | Kênh mới | Thất bại <1K | ≥10K | Kênh 1–3 năm ≥10K | Video mới ≤48h: median view |
|---|---|---|---|---|---|
| Horror (mod/story) | 13 | 7 (54%) | 3 (23%, CI 8–50%) | 7/12 | 2,984 |
| Survival / 100 days | 16 | 8 (50%) | 3 (19%, CI 7–43%) | 8/16 | 904 |
| Challenge "Minecraft but" | 7 | 4 (57%) | 2 (29%) | 6/10 | 10,910 |
| Machinima / animation | 5 | 1 | 2 (40%) | 6/6 | 6,611 |
| Mystery / ARG | 10 | 9 (90%) | 1 (10%) | 4/10 | 339 |
| Engineering / redstone | 2 | 2 | 0 | 0/2 | 554 |
| Lore / history | 9 | 7 (78%) | 0 (CI 0–30%) | 3/5 | 453 |

Toàn bộ kênh mới (gộp, không trùng): **60 kênh. 22 kênh đạt ≥1K, 9 kênh ≥10K (15%, CI 8–26%), 1 kênh ≥100K.**

Lọc thêm "kênh có chất lượng sản xuất". Đây là proxy INFERRED: kênh không đăng ký ở nước RPM thấp, và video mẫu dài ≥15 phút. Kết quả:

| Ngách | Kênh mới chất lượng | ≥1K | ≥10K |
|---|---|---|---|
| Survival | 7 | **6** | 2 (Day Zero, McDoubleAA) |
| Horror | 5 | 3 | 2 (ENFINITY, Dooy) |
| Challenge | 4 | 3 | 2 (imKaiL00L, More Doodle) |
| Mystery | 4 | 0 | 0 |
| Lore | 4 | 2 | 0 |
| Machinima | 2 | 1 | 0 |

## 3. Kênh thắng khác kênh thua ở đâu (long-form, kênh ≤3 năm, 116 kênh không trùng)

| | Thắng ≥10K (n=39) | Giữa 1K–10K (n=25) | Thua <1K (n=52) |
|---|---|---|---|
| Số video (median) | 71 | 41 | 27 |
| Video/tuần | 1.1 | 1.3 | 1.3 |
| Độ dài video mẫu (median) | 23 phút; 12 kênh có video ≥60 phút | 19 phút | 15 phút |
| Đăng ký ở IN/PH/VN/BD/PK/ID/BR/NP | 2 | 7 | 21 |
| View/video trọn đời (median) | **110,389** | 11,543 | **576** |

Trong từng ngách (OBSERVED):
- Survival: kênh thắng đăng **0.6 video/tuần, video dài 88 phút**. Kênh thua đăng 1.1/tuần, 16 phút.
- Horror: kênh thắng 19 phút; kênh thua 11 phút. Video mẫu của kênh thua có median **15 view**.
- Đăng nhiều không cứu được kênh:
  - RAGNOX GAMING: 171 video, 44 sub.
  - SAMSON: 80 video, 7 sub.
  - Zaydragnetic: 184 video, 51 sub.
  - MinecraftUSAMEDIA: 209 video, 233 sub.

INFERRED: kênh thắng bán **một ý tưởng rõ trong tiêu đề** và đầu tư vào **video dài, ít mà chất**. Kênh thua đăng gameplay thô, 8–15 phút, tiêu đề chung chung.

## 4. Kênh thắng thực sự làm gì
Dựa trên tiêu đề và thời lượng 5 video mới nhất (METADATA_ONLY).

**Horror story có thể làm bằng IP gốc**
- Syllo: tạo 2025-02, 107K sub. Video kiểu "Something In The Desert Is Trying To Kill Me…" dài 14–18 phút, cộng một "FULL MOVIE" 55 phút; 106K–416K view.
- Nefloq: tạo 2025-08, 60.9K sub. "Something Is WATCHING You" 48 phút, "FULL MOVIE" 2h13 (110K view).
- ENFINITY: tạo 2026-03, 18.8K sub. Tự làm thực thể và mod ("I Made a Wendigo…" 63K, werewolf mod 146K), video 25–40 phút.
- Jemario: tạo 2026-08, 45K sub. Review horror mod bằng giọng hài, 12–24 phút. Thành công nhờ **giọng và tính cách**, khó thay bằng giọng AI.
- Rủi ro IP trong ngách: TIMS (Siren Head, Cartoon Cat) và Pepper ("Cat in the Hat.EXE") dùng sinh vật hoặc nhân vật của người khác. Ta **không** làm theo.

**Survival "kịch bản sinh tồn" dài**
- Day Zero: tạo 2026-10, chỉ 2 video ("100 Days in a REALISTIC APOCALYPSE" 52 phút **2M view**; "DEADLY OUTBREAK" 40 phút 432K).
- McDoubleAA: tạo 2026-05, 15 video, 76.5K sub. "1,000 Days Hardcore [FULL MOVIE]" 4h39 814K; Backrooms 129K.
- BlakeCraft: tạo 2026-04, 4.8K sub. "100 Days as a GHILLIE Sniper in a Zombie Apocalypse" 3h57, 325K view.
- KnightMC: tạo 2026-04, 4K sub. "500 Days LOST AT SEA" 3h37, 197K view.
- Hạn chế: mỗi video cần 10–40 giờ chơi. Các kênh thường dừng ở khoảng 4–5K sub khi chỉ đạt 20–50K view mỗi video.

**Challenge thắng lớn nhất trong cả mẫu**
- imKaiL00L: tạo 2026-04, **249K sub, trung bình 463K view/video**. Video "Minecraft but … Horror Mobs Evolve" dài 24–33 phút, có mod tùy biến, có giọng dẫn.
- Các kênh challenge thắng khác chủ yếu nhắm khán giả nhỏ tuổi hoặc dùng IP: Gara, Teddy and Freddy (Lord Verity, Dexter), Drift ("BABY … ON ONE CHUNK"), More Doodle (2.5–3h "pranked my friends").

**Machinima: các kênh thắng đều dùng IP của người khác**
- Knoxy (4.75M sub), Neo ("MAIZEN: JJ & Mikey"), Zenichi and Sister (JJ), my MONSTER SCHOOL (Lord Verity/Sonic), MCJesterYT (Spiderman), Steve Muk (BABY JJ).
- Mac & Ollie thực chất là "Minecraft X Civilization: The Movie", tức mô phỏng nhiều người chơi, không phải machinima.
- Kết luận: không có kênh machinima IP gốc nào thắng trong mẫu. Lặp lại kết luận của audit 2026-11-11.

**Lore**
- Các kênh thắng mới (Macery, Frado Minecraft) đều kể lore của **Unstable SMP**, một SMP của creator khác. Nội dung phụ thuộc kênh khác và có rủi ro bản quyền/commentary.
- Kênh lore mới 9/9 chưa đạt 10K.

**Mystery, Engineering**
- Mystery: kênh mới 9/10 thất bại. LQvos (595K) là kênh tạo 2024.
- Engineering: kênh mới 0/2. Ngách này cần chuyên môn redstone thật.

## 5. Mô hình tiền (INFERRED, chỉ dùng để xếp hạng, không phải dự báo)
Công thức: tỉ lệ kênh ở mỗi dải sub × median view/tháng của dải đó × RPM AGG-EST. Dải <1K tính $0 vì chưa đủ YPP.

| Ngách (kênh ≤3 năm) | Dải 10K–100K: view/tháng | Dải ≥100K: view/tháng | RPM AGG-EST | Kỳ vọng $/tháng/kênh |
|---|---|---|---|---|
| Horror (n=25) | 291K | 2.8M (2 kênh) | $1.5–3.5 | $495–1,155 |
| Survival (n=32) | 260K | – (0 kênh) | $2–4 | $236–472 |
| Challenge (n=17) | 214K | 4.2M (4 kênh, nhiều kênh nhắm trẻ em/IP) | $2–4 | $2,088–4,177 |
| Machinima (n=11) | 417K | 6.2M (IP Maizen/JJ) | $0.5–2 | $958–3,832 (**loại vì IP**) |
| Mystery (n=20) | 183K | 10.9M (LQvos, Pepper) | $0.7–3.6 | $782–4,020 (xổ số: kênh mới 1/10) |
| Lore (n=14) | 153K | – | $3–6 | $251–502 |
| Engineering (n=4) | – | – | $2–5 | $29–73 |

Đọc bảng:
- Số kỳ vọng phụ thuộc rất nhiều vào vài kênh lớn.
- Machinima, challenge-trẻ em và mystery có số cao nhờ IP, nhờ khán giả trẻ (Made for Kids làm RPM giảm thật, kids RPM đo được là $0.33), hoặc nhờ kênh cũ.
- Khi bỏ IP và khán giả trẻ, **horror và survival là hai ngách duy nhất vừa có kênh mới thắng thật bằng nội dung gốc, vừa có khán giả teen/người lớn.**
  - Survival: sàn cao hơn (6/7 kênh mới chất lượng đạt ≥1K).
  - Horror: trần cao hơn (dải ≥100K có 2.8M view/tháng).
- Video 40–60 phút tạo nhiều mid-roll và nhiều giờ xem. Điều này giúp đạt mốc YPP 8,000 giờ (áp dụng cho kênh mới từ 2027-02-01) nhanh hơn (INFERRED).

## 6. Lựa chọn (PROPOSED, chờ owner duyệt)

**Ngách chính: Survival kịch bản kinh dị/tận thế với thực thể gốc ("100 Days in a [mối đe dọa gốc]").**
- Gộp hai ngách có bằng chứng tốt nhất:
  - Tiêu đề và cấu trúc của survival, như Day Zero ("I Survived 100 Days in a DEADLY OUTBREAK") và BlakeCraft.
  - Lực căng của horror story, như Syllo/Nefloq ("Something Is Watching Me…").
- Hình thức: phim sinh tồn 40–55 phút, gameplay Minecraft vanilla, datapack/mod tự viết để tạo sự kiện và thực thể **gốc**. Có lời dẫn và phụ đề.
- Lý do:
  - Có nhiều kênh mới thắng nhất bằng IP gốc: Day Zero, McDoubleAA, BlakeCraft, KnightMC, Syllo, Nefloq, ENFINITY.
  - Khán giả không phải trẻ em.
  - Video dài kiếm nhiều tiền mỗi view và gom giờ xem nhanh.

**Nhịp phụ (rẻ hơn, đều đặn): tập horror story 15–25 phút** kiểu "Something In The Desert Is Trying To Kill Me…". Cùng thế giới và thực thể với phim dài; 3–4 tập ghép thành "FULL MOVIE" 1–2 giờ.

**Để sau (cần giọng dẫn có cá tính): "Minecraft but [luật kinh dị]"** theo mô hình imKaiL00L. Repo đã có skill minecraft-modding nên ta làm được mod. Nhưng thành công của định dạng này phụ thuộc giọng dẫn và thường là chơi nhiều người.

**Không làm:**
- Machinima: kênh thắng đều dùng IP JJ/Maizen/Verity.
- Challenge kiểu NOOB vs PRO hay BABY ONE CHUNK: khán giả trẻ em, RPM thấp, hay dùng IP.
- Mystery/ARG: kênh mới 9/10 thất bại.
- Lore: kênh mới 0/9 đạt 10K; kênh thắng sống nhờ drama SMP của người khác.
- Engineering: cần chuyên môn sâu, kênh mới 0/2.

**Tránh lặp lại kênh thua:**
- Không đăng gameplay thô 8–15 phút hằng ngày.
- Không đặt tiêu đề chung chung.
- Không dùng sinh vật hay nhân vật của người khác (Siren Head, Cartoon Cat, Cat in the Hat, Verity, JJ).
- Đặt 1 video/tuần làm trần, không phải mức sàn.

**Ngưỡng thử nghiệm đề xuất (owner quyết định):**
- 6 video đầu (2 phim dài + 4 tập).
- Mục tiêu: ít nhất 1 video ≥10K view trong 28 ngày, và median ≥1K.
- Nếu 6 video đều <1K: đổi concept hoặc thumbnail trước khi sản xuất thêm.

## 7. Thay đổi so với đề xuất trước
- D-9d98f3c9 (horror chính, survival dự phòng) được **tinh chỉnh**, không đảo ngược. Hai ngách được gộp thành một định dạng.
- Phim dài kiểu survival là "sản phẩm tiền", tập horror ngắn là "nhịp đăng".
- Bằng chứng mới nằm ở mục 2–3: tỉ lệ thất bại của kênh mới, sàn của survival, và việc mọi kênh machinima thắng đều dùng IP.
