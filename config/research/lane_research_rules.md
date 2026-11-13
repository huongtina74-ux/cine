# Vòng nghiên cứu đối thủ không ngừng cho các ngách đã chốt (OWNER, 14/11/2026)

Nguồn: tin nhắn owner 14/11/2026 01:08 (VN). Áp dụng cho **mọi ngách đã chốt** trong `config/research/locked_lanes.json`. Đây là bản mở rộng của `config/research/minecraft_story_rules.md` (OWNER 03/11), giữ nguyên tinh thần.

## Ngách đã chốt (OWNER 14/11/2026)

| Mã | Ngách | Định dạng | Watchlist | Nguyên tắc |
|---|---|---|---|---|
| MC-L1 | Minecraft: phim sinh tồn kịch bản "100 Days" / FULL MOVIE (chính) | Long 40–90 phút | `watchlists/mc_survival_movie.txt` | `reports/research/principles/mc_survival_movie.md` |
| MC-L2 | Minecraft: kinh dị sinh tồn với thực thể gốc (phụ, cùng vũ trụ) | Long 20–30 phút + FULL MOVIE | `watchlists/mc_original_horror.txt` | `…/principles/mc_original_horror.md` |
| MC-S1 | Minecraft Shorts: dàn nhân vật gốc thi đấu "Who can…?" | Shorts | `watchlists/mc_shorts_whocan.txt` | `…/principles/mc_shorts_whocan.md` |
| MC-S2 | Minecraft Shorts: mô phỏng vật lý/satisfying Blender với mascot gốc | Shorts | `watchlists/mc_shorts_physics.txt` | `…/principles/mc_shorts_physics.md` |
| X-S1 | Shorts ngoài Minecraft: giải thích 3D "How it works / How to build X" | Shorts | `watchlists/explainer3d_shorts.txt` | `…/principles/explainer3d_shorts.md` |

MC-S1/S2 chạy trên kênh Shorts Minecraft riêng ("Lab"), không trộn vào kênh long-form (INFERRED, theo D-9276ec58). X-S1 dẫn người xem sang kênh dài "3D history & engineering".

## A. Đối thủ dẫn đầu (đã có trong watchlist) — nghiên cứu mỗi ngày
Tìm kênh dẫn đầu **đúng ngách con**. Với mỗi kênh, nghiên cứu:
1. Video phổ biến nhất.
2. Video mới nhất.
3. **Video vượt trội so với chính kênh**, nếu thoả một trong các điều kiện:
   - đăng ≤30 ngày và view ≥3× trung vị cùng định dạng của kênh;
   - view gấp nhiều lần sub (≥5×; càng 10× / 30× / 100× càng mạnh);
   - **bùng nổ trong 5 ngày đầu**: ≤5 ngày tuổi mà view đã ≥2× trung vị cùng định dạng (ngưỡng vận hành, INFERRED — owner có thể chỉnh).

Với mỗi video vượt trội, trả lời: **vì sao nó thắng, cốt lõi ở đâu** (lời hứa ở tiêu đề, thumbnail, hook 5–30 giây đầu, mối đe doạ/xung đột, nhân vật, độ dài, cấu trúc, cảm xúc), rồi rút ra **"bản lề"** để ta áp dụng bằng nội dung gốc.

## B. Đối thủ mới — tìm mỗi ngày
- Kênh thành lập **0–30 ngày**. **Bắt buộc xác minh ngày tạo** bằng API `channels.list snippet.publishedAt` hoặc dòng "Đã tham gia" trên trang About. **Không tin "channel age" của Algrow/Tube Atlas** vì Algrow đo từ video đầu tiên.
- Ngưỡng chuẩn:
  - Ngách long-form: có **≥2 video dài (≥8 phút) đạt ≥1M view**.
  - Ngách Shorts: có **≥2 Shorts đạt ≥1M view**.
- Nghiên cứu từng video triệu view của kênh đó, rồi **ghi kênh vào watchlist** với role `new`.
- Nếu không kênh nào đạt chuẩn: ghi ứng viên gần nhất vào báo cáo. Kênh nào mạnh (view ≫ sub) thì vẫn có thể thêm, ghi rõ "chưa đạt chuẩn B".
- **Ngày hôm sau, role `new` → `leader`.** Từ đó kênh theo luật đối thủ cũ:
  - video có view gấp nhiều lần sub → nghiên cứu;
  - video ≤15 ngày có view vượt trội so với các video khác của kênh → nghiên cứu;
  - video bùng nổ trong 5 ngày đầu → nghiên cứu.

## C. Video đang bùng nổ
- Tìm bằng **nhiều từ khoá đúng định dạng** (`keywords` của từng ngách trong `locked_lanes.json`; mở rộng thêm từ tiêu đề của video thắng mỗi ngày).
- Ưu tiên video **0–15 ngày đạt ≥1M view**, kiểm tra **tốc độ tăng** (view/ngày; so với lần chụp hôm trước để biết đang tăng tốc hay giảm tốc).
- Video triệu view đến từ **kênh nhỏ** càng tốt. **View/sub gấp vài lần → vài chục → hàng trăm lần = tín hiệu trend.**

## D. Mỗi ngày: học và rút nguyên tắc
- Cập nhật file nguyên tắc của từng ngách, giữ hai phần:
  - **Nguyên tắc dài hạn** (cố định, dùng lặp lại). Chỉ nâng một xu hướng lên đây khi nó còn đúng ≥4 tuần.
  - **Nguyên tắc ngắn hạn / trend** (có thể đổi). Mỗi mục ghi: ngày thấy lần đầu, lần cuối, bằng chứng, trạng thái (`hot` / `watching` / `declining` / `expired`). Hết hạn sau 3 vòng không thấy lại.
- Mục tiêu: tạo video bùng nổ view, và **đi trước trend** (bắt trend khi mới có 1–3 kênh nhỏ thắng).
- Mỗi ngày thêm đối thủ mới dựa trên nghiên cứu ngách hôm đó.

## Đầu ra mỗi ngày
- `reports/research/<YYYY-MM-DD>_lanes_daily.md` (tiếng Việt). Mỗi ngách gồm:
  - thay đổi so với hôm trước;
  - video vượt trội + "vì sao thắng / bản lề";
  - đối thủ mới;
  - trend bắt đầu/kết thúc;
  - 1–3 ý tưởng gốc.
- Cập nhật 5 watchlist + 5 file nguyên tắc.
- Ghi 1 dòng vào `python tools/cf_decision.py add …` (label OBSERVED).
- Chạy `python -m pytest tests/test_locked_lanes.py -q` trước khi commit.

## Giới hạn (bất biến)
- **Dữ liệu được dùng:**
  - API chính thức YouTube Data v3: key chỉ ở `.env` trên PC owner, không bao giờ in/log/copy.
  - Algrow/Tube Atlas của owner, chỉ đọc.
  - Trang công khai, đọc với tốc độ người.
- **Quota:** tối đa ~90 lần `search.list`/ngày cho cả 5 ngách.
- **Không tải video.** Tiêu đề/thumbnail không phải là "đã xem video". Kết luận về nhịp dựng, diễn xuất, âm thanh cần cổng `competitor-complete-study`.
- **Chỉ học công thức.** Không chép nhân vật, tên, kịch bản, nhạc, footage của người khác (JJ/Mikey, Verity, Siren Head, Cave Dweller…).
- **Gắn nhãn mọi con số:** OBSERVED (kèm ngày) / INFERRED / ESTIMATED.
