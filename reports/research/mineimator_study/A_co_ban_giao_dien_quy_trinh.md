# Mine-imator 2.0.x — Sổ học Nhóm A: Giao diện, cơ bản, quy trình, render/export, mẹo chung

Ngày: 2026-11-03 · Người soạn: subagent nhóm A (Claude) · Nguồn: phụ đề YouTube (ASR tự động, tiếng Anh) do job trích xuất trong Chrome đọc ra (`window.RES[id].text`), đọc đầy đủ từng video bằng JavaScript chỉ đọc. Lượt 2 (cùng ngày): 4 video còn lại được đọc trong tab Chrome riêng, qua panel transcript của YouTube và storyboard i.ytimg.com. Không tải video và không gọi API trả phí.

**Quy ước nhãn (theo CLAUDE.md):**
- `[videoId mm:ss]`: dẫn nguồn. Mốc thời gian là đầu đoạn phụ đề gần nhất **trước** câu được dẫn, sai số khoảng ±20 giây vì mình gộp mốc theo bước khoảng 20 giây.
- **OBSERVED**: điều video nói hoặc làm, được dẫn nguồn.
- **(INFERRED)**: suy luận của mình, video không nói.
- Phụ đề là ASR nên có lỗi nghe. Tên phím và số liệu mà ASR có thể nghe sai được đánh dấu **(ASR?)**.
- Tên menu và trường giữ nguyên tiếng Anh như người nói trong video. Nếu người nói chỉ tả ("click this button"), mình ghi theo mô tả.

**Cảnh báo phiên bản:** một số video SharpWind (xH9t, YHDs, G4KS, 2Klm, 0ZBm, Bt53) và BNE7 có vẻ quay trên Mine-imator 1.x vì nhắc "SSAO range", "background tab", "ticks" (INFERRED). Nguyên lý vẫn dùng được, nhưng tên trường trong 2.0 có thể khác. Video 2.0 chắc chắn gồm JBIn, Vn0z, pjrA, nOz, PHTP, TcNS, a91b, QhMY.

---

## 1. Bảng video nhóm A

| # | id | Tiêu đề | Kênh | Độ dài | Lượt xem | Transcript |
|---|---|---|---|---|---|---|
| 1 | JBIn_WC4jSY | Mine-imator 2: Interface and New Features | AnxiousCynic | 14:40 | 144,979 | Có (734 seg) |
| 2 | Vn0zjTO4dWY | How To Make Minecraft Animation - Part 1 - Mine-imator 2 Tutorial | AnxiousCynic | 20:07 | 57,149 | Có (1126 seg) |
| 3 | pjrAmdnpffA | How To Import Minecraft Worlds and Build A Scene - Part 2 | AnxiousCynic | 12:15 | 46,762 | Có (672 seg; đọc lại từ panel transcript YouTube ở lượt 2) |
| 4 | nOz-trT5m9U | Mine-imator: Noob to Pro in Under 14 Minutes! | AnxiousCynic | 13:34 | 76,121 | Có (880 seg) |
| 5 | PHTPcUdK84I | Full guide to Mine-imator 2.0 | The Ultimine Studios | 39:41 | 10,190 | Có (315 seg) |
| 6 | TcNSoStA0Js | How to use Mine-imator 2.0.2: Beginner's Guide, Part 1 | Tywa Animation | 15:07 | 2,012 | Có (114 seg) |
| 7 | a91bOwulnw8 | Render Settings & How to Export Your Animation - Part 7 | AnxiousCynic | 16:31 | 35,334 | Có (928 seg) |
| 8 | BNE7CsRE79o | Mine-imator Tutorial - How to Animate: Keyframes & Transitions, Part 4 | AnxiousCynic | 13:53 | 99,051 | Có (762 seg) |
| 9 | 8OVe4NGOdv4 | How to make your animation LOOK GOOD in MINE-IMATOR 2.0! | Ishaan Animationz | 1:30 | 11,928 | Có caption nhưng **chỉ có [Music]**, không có lời. Mô tả: "kinda like a lighting tutorial (but not that helpful)". Không trích được nội dung. |
| 10 | QhMY2ac0nOk | Every Mine Imator Tutorial of 2025 | Prrok | 18:23 | 9,768 | Có (137 seg) |
| 11 | 4e_xp4QTAUU | The 12 principles of Mine-imator, Part 1 | NatuAnimates | 18:07 | 7,566 | Có (808 seg) |
| 12 | xH9t-hLVWhY | 18 USEFUL Mine Imator Tips Everyone Should Know! | SharpWind | 13:52 | 34,395 | Có (702 seg) |
| 13 | YHDs-CdYgEc | 11 USEFUL Tips for ANY Mine Imator User! | SharpWind | 8:23 | 15,723 | Có (440 seg) |
| 14 | G4KSYcJmdk8 | Do's and Don'ts ~ 11 Mine Imator Tips | SharpWind | 5:32 | 19,853 | Có (330 seg) |
| 15 | 2Klmj7x8IvI | Top 6 Mistakes Beginner Mine-Imator Animators Make! | SharpWind | 8:04 | 13,285 | Có (464 seg) |
| 16 | 0ZBmiugjgLg | Professional Mine Imator Tips! Tips That will Make you a Pro! | SharpWind | 8:43 | 53,460 | Có (456 seg) |
| 17 | Bt53B-WZfTw | How PARENTING Works!! The Rigger's Secret! ~ Mine Imator | SharpWind | 12:41 | 7,454 | Có (594 seg; lượt 2). Có thể là bản 1.x (INFERRED) |
| 18 | ieV5yGq7-hI | Easiest Way to Animate: Stop Motion - Mine-imator Tutorial | AnxiousCynic | 14:58 | 23,646 | Có (716 seg; lượt 2) |
| 19 | eYJK2OnzQ0Y | Create Popular Minecraft Animation Shorts in Mine-Imator | Anvey | 1:09:29 | 33,937 | **Không có transcript** (video không có captions). Dùng mục lục chương trong mô tả + 13 tấm storyboard L3 (M16, M18, M20, M21, M23, M25, M27, M29, M31, M33, M35, M39, M45; mỗi ô = 10 s) |

Số liệu độ dài và lượt xem là OBSERVED: video 1–16 lấy từ `RES[id].len/views`; video 3, 17, 18, 19 lấy từ `ytInitialPlayerResponse.videoDetails` ở lượt 2 (2026-11-03).

---

## 2. Ghi chú theo chủ đề

### 2.1 Cài đặt, mode, giao diện

- **Tải đúng bản.** Trang mineimator.com mặc định đưa bản cũ 1.2.9. Muốn bản 2.0 mới nhất thì vào forum, mục *Modding discussion*, thread **"Mine-imator 2.0 Continuation Build"** (community build). Lý do: developer gốc (Nimi) đã nghỉ. [Vn0zjTO4dWY 0:20–1:01] [nOz-trT5m9U 0:20]
- Giải nén zip bằng chuột phải → *Extract all*. Nếu Windows cảnh báo SmartScreen thì chọn *More info* → *Run anyway*; người nói bảo bản tải từ nguồn chính thức là an toàn. [nOz-trT5m9U 0:41]
- PHTP dùng **2.0.2** và nói thêm **Community Build 1.0.0** có nhiều tính năng nhất, nhưng là bản không chính thức và Windows cảnh báo, nên "tải tùy rủi ro". [PHTPcUdK84I 1:24, 35:03–35:52]
- **Simple mode → Advanced mode.** Lần đầu mở, app ở *Simple mode*. Bấm dòng chữ "Simple mode enabled" ở góc trên phải → link tới mineimator.com/upgrade → chọn donate hoặc *not donate* → *Get key* → dán key → *Upgrade* → *Enable*. Key miễn phí. Advanced mode mở khóa custom render settings và nhiều tính năng khác. [nOz-trT5m9U 1:02–1:23] [Vn0zjTO4dWY 1:22–1:43] [JBIn_WC4jSY 0:23–1:54]
- Chưa upgrade thì **không tắt được watermark** khi export. [a91bOwulnw8 15:09–15:29]
- **Edit > Preferences** (cấu hình AnxiousCynic khuyên):
  - Bỏ tick **"Copy work camera into new cameras"** để camera mới luôn spawn ở gốc 0. [JBIn_WC4jSY ~3:00] [Vn0zjTO4dWY 7:40]
  - *Interface*: theme Dark/Darker, accent color tùy chọn; **Compact panels**, **Compact timeline lists** để tiết kiệm chỗ. [JBIn_WC4jSY ~4:00] [Vn0zjTO4dWY 8:01–8:42] [PHTPcUdK84I 2:41]
  - ⚠️ Bật *Compact panels* làm menu Transitions tràn ra ngoài màn hình, nên tắt đi nếu gặp lỗi này. [JBIn_WC4jSY 12:49]
  - **"Z is up"**: trục Z là trục lên xuống. Chú ý: từ đây X/Y/Z trong video phụ thuộc lựa chọn này. TcNS dùng mặc định Y-up (Y xanh lá, Z xanh dương, X đỏ). [Vn0zjTO4dWY 8:42–9:03] [TcNSoStA0Js 2:36]
  - *Separate tool modes*: tách riêng move/rotate/scale. [JBIn_WC4jSY ~5:00]
  - *Controls*: Move speed = 1, slow modifier mặc định **0.25**. AnxiousCynic chỉnh xuống **0.15** [JBIn_WC4jSY ~5:30]; ở Vn0z ASR nghe thành "1.5" (ASR?) [Vn0zjTO4dWY 9:25–9:45].
  - *Unlimited values*: bỏ giới hạn giá trị. PHTP khuyên bật nhưng phải cẩn thận. AnxiousCynic không dùng. [PHTPcUdK84I 38:13–38:36] [JBIn_WC4jSY ~3:30]
- **Điều hướng viewport:**
  - Giữ chuột trái + kéo: orbit.
  - Giữ chuột phải: nhìn kiểu FPS. Trong lúc giữ chuột phải: **W/A/S/D** di chuyển, **E/Q** lên/xuống (ASR nghe "C/Q", "F/Q"), **Shift** chậm, **Space** nhanh.
  - **Shift + chuột trái**: pan. **Lăn chuột**: zoom. **R** (hoặc chuột phải + R) đưa camera về vị trí đầu.
  - Có "legend" phím tắt ở đáy cửa sổ.
  - [nOz-trT5m9U 1:44–2:06] [Vn0zjTO4dWY 6:16–7:20] [PHTPcUdK84I 3:04–3:34] [TcNSoStA0Js 0:22–1:27]
- **Hotkey gizmo:** **G** move, **R** rotate, **S** scale, **B** bend. Có nút copy/paste tọa độ cạnh từng nhóm transform. [PHTPcUdK84I 6:46–7:30] [TcNSoStA0Js 3:21]
- **Nút góc trên phải viewport:**
  - Gizmo on/off; **Aspect ratio** (khung đúng tỉ lệ render); **Grid overlay**, chia 1/3, chỉnh được số đường.
  - **Particles** on/off cho nhẹ máy.
  - **Flat / Shaded / Rendered**. Rendered nặng; góc dưới trái hiện số sample đang tích lũy và FPS.
  - **Secondary viewport** hiện active camera.
  - [JBIn_WC4jSY 7:59–8:41] [Vn0zjTO4dWY 4:33–5:56]
- **Pop-out cửa sổ:** nút ở timeline tách timeline thành cửa sổ riêng để kéo sang màn hình thứ 2. Camera view cũng tách được. [JBIn_WC4jSY 11:25–12:26] [PHTPcUdK84I 13:30]
- **Ô số nhận phép tính**, ví dụ gõ `10*2` → 20. [JBIn_WC4jSY 10:44]
- **Chuột phải lên một trường → Reset value / Reset all values.** Reset all values đưa object về gốc 0. [JBIn_WC4jSY ~7:00] [Vn0zjTO4dWY 10:27] [TcNSoStA0Js 2:56]

### 2.2 Project setup: tempo, resolution, FPS

- **Tempo = FPS của timeline.** Mặc định là **24**. AnxiousCynic đặt **30**, để 60 nếu xuất 60 fps. Mục tiêu là **1 frame timeline = 1 frame output**. [Vn0zjTO4dWY 2:05–2:28] [nOz-trT5m9U 1:23–1:44] [JBIn_WC4jSY ~1:50]
- **Resolution** đặt bằng độ phân giải output, ví dụ **1080p**. [Vn0zjTO4dWY 2:28–2:50]
- Tempo/FPS timeline phải khớp FPS export để tránh frame trung gian. Nếu lệch, cú cắt camera "instant" có thể lộ **1 frame thừa** không mong muốn. [PHTPcUdK84I 13:03–13:30]
- *View* cho phép đổi hiển thị thời gian giây ↔ frame. [PHTPcUdK84I 13:03]
- Project settings: tên, tác giả, mô tả, nơi lưu, định dạng ảnh/video mặc định. [PHTPcUdK84I 34:17]
- Lỗi phổ biến của người mới là "nhân vật chạy siêu tốc" vì không hiểu render/tempo. [2Klmj7x8IvI 2:05]
- QhMY nói đặt tempo "about 7" cho idle [QhMY2ac0nOk 8:41] và "tempo at one" trước khi chỉnh render [QhMY2ac0nOk 9:28]. Hai con số này không có giải thích. ⚠️ **Không áp dụng** (ASR? hoặc mẹo xem chậm).

### 2.3 Timeline, keyframe, transition/easing

**Tạo, xóa, sửa keyframe**
- **Auto-key:** thay đổi bất kỳ thông số nào sẽ tự tạo keyframe tại vị trí timeline cursor. [nOz-trT5m9U 6:53] [TcNSoStA0Js 6:36] [BNE7CsRE79o 0:20]
- **Tạo key thủ công:** double-click vào timeline hoặc **Ctrl+Q**. Ctrl+Q tạo key **giống hệt key trước**, dùng để giữ pose và có thể làm cho mọi part đang chọn cùng lúc. [nOz-trT5m9U 6:53] [TcNSoStA0Js 11:43]
- **Mẹo "base pose key":**
  - Chọn hết body parts (kéo box qua danh sách timeline) → trong tab Keyframe tick/untick **Visible**. Cách này tạo key ở mọi part mà không đổi pose. [BNE7CsRE79o 1:01–1:42]
  - Cách khác: chuột phải lên một trường → reset. Thao tác này cũng tạo key. [BNE7CsRE79o 0:40]
- **Sửa thông số:**
  - Thay đổi áp vào **key đang được chọn** (key màu trắng).
  - Muốn auto-key tại cursor thì **bỏ chọn mọi key**.
  - [TcNSoStA0Js 8:51–9:14] [nOz-trT5m9U 6:53]
- **Chọn nhiều, xóa:**
  - Kéo box để chọn nhiều key. **Shift-click** chọn thêm, **Ctrl-click** bỏ bớt.
  - Xóa bằng phím **Delete**. PHTP nói "Ctrl R" (ASR?).
  - [nOz-trT5m9U 6:33] [BNE7CsRE79o 0:40] [PHTPcUdK84I 11:55] [TcNSoStA0Js 6:59]
- **Copy/paste key:**
  - **Ctrl+C**, rồi trỏ chuột vào frame đích và **Ctrl+V**: key dán theo vị trí chuột.
  - Nút "paste" thì dán tại cursor.
  - Dùng để lặp động tác (vẫy tay, đấm 2 lần).
  - [BNE7CsRE79o 2:44–3:26] [TcNSoStA0Js 9:34] [PHTPcUdK84I 11:55]
- **Hold (giữ pose trước khi chuyển động):** copy key đầu, dán ở frame bắt đầu chuyển động. Nếu không có key giữ, nội suy sẽ chạy ngay từ frame 0. Đây là "lỗi kinh điển của người mới". [BNE7CsRE79o 2:23–3:46] [TcNSoStA0Js 9:55–10:18]

**Timing**
- **Timing = khoảng cách giữa 2 key.** Gần nhau thì nhanh, xa nhau thì chậm.
- Ví dụ ở tempo 30: 30 frame = 1 s, 15 frame = 0.5 s. Ở tempo 24: so sánh 5/10/52 frame.
- Biên độ lớn trong cùng số frame sẽ trông nhanh hơn.
- [nOz-trT5m9U 7:13] [BNE7CsRE79o 3:46–4:15, 5:35, 8:21–8:42] [TcNSoStA0Js 7:25–7:48]

**Transitions** (chọn key → tab Keyframe → Transition, hoặc chuột phải → *Transitions*)
- **Linear** là mặc định và trông "robot". Chỉ dùng giữa một chuỗi hành động rất nhanh. [BNE7CsRE79o 5:35] [G4KSYcJmdk8 4:34–4:54] [2Klmj7x8IvI 6:12]
- **Instant** giữ giá trị rồi nhảy luôn. Dùng cho **cắt camera** và **đổi item hoặc texture theo key**. [BNE7CsRE79o 6:17–6:38] [nOz-trT5m9U 6:13–6:33]
- **Ease in** = khởi đầu chậm. **Ease out** = kết thúc chậm. **Ease in-out** = chậm cả hai đầu.
  - Có nhiều biến thể: quadratic, …, "back" (QhMY dùng "back ease in and out").
  - Easing "bóp" thời gian, nên phải giãn hoặc dồn lại key.
  - [BNE7CsRE79o 6:38–8:21] [2Klmj7x8IvI 6:54–7:15] [QhMY2ac0nOk 7:34–8:20]
- Chọn easing theo vật lý: bóng **rơi** dùng ease in (tăng tốc), bóng **nảy lên** dùng ease out. [0ZBmiugjgLg 4:29–4:49]
- ⚠️ **Key mới thừa hưởng transition của key trước**, nên phải kiểm tra lại mỗi lần. [BNE7CsRE79o 9:03–9:46]
- Đổi transition cho nhiều key: box-select rồi đổi một lần. Key phải đang được chọn, nếu không thì đổi không có tác dụng. [nOz-trT5m9U 6:33] [QhMY2ac0nOk 5:19]
- **Bezier transition (2.0):** có đồ thị và tay nắm để vẽ curve tùy biến. [JBIn_WC4jSY 12:49–13:31] [PHTPcUdK84I 13:53–14:21]
- "Không có transition nào tốt nhất", phải thử theo từng động tác. [BNE7CsRE79o 10:46]

**Quy trình "stop motion" của AnxiousCynic (ieV5yGq7-hI):** người nói gọi đây là cách dễ nhất để có kết quả đẹp.
1. Tạo walk cycle tự động → **xóa bớt key**, chỉ giữ key pose; căn thẳng key tay (bỏ offset); thêm key cho head. Các pose cách nhau **15 frame**. [ieV5yGq7-hI 0:48–1:28]
2. Thêm passing pose: chân trước **bend 40°** ở giữa bước. Tất cả transition = **linear**. [ieV5yGq7-hI 1:49–2:10]
3. Chọn mọi part, cứ **~3–4 frame** bấm **Ctrl+Q** để chèn key, không cần đều tuyệt đối. [ieV5yGq7-hI 2:31–2:51]
4. Chọn hết key → chuột phải → *Transition* → **Instant**, cho ra chuyển động giật kiểu stop motion. [ieV5yGq7-hI 2:51–3:13]
5. Root có thể giữ linear mượt (trượt đều) hoặc cũng làm stepped. [ieV5yGq7-hI 3:33–4:16]
6. **Loop:** xóa pose cuối (trùng pose đầu), copy cả bộ, dán nối tiếp. [ieV5yGq7-hI 4:16–4:58]
7. ⭐ **Export keyframes:** chọn key → chuột phải → **Export keyframes** → đặt tên, lưu file. Ở project khác: *File → Import asset* để nạp lại bộ key, tạo thư viện động tác dùng lại. [ieV5yGq7-hI 4:58–5:20]

Ví dụ "chạy tới, bật nhảy, đập chuông":
- Block pose **bỏ qua timing**: pose lấy đà (anticipation), bật lên (người ưỡn), vỗ, tiếp đất bằng chân trước, impact, recovery (pose 0). Pose cách nhau ~5 frame, tất cả linear. [ieV5yGq7-hI 5:40–11:37]
- Play để chốt timing ở dạng linear. [ieV5yGq7-hI 11:57–12:39]
- Chèn key: **dày hơn ở đoạn nhanh** (bật nhảy), thưa hơn ở đoạn chậm, rồi chuyển sang Instant. Kết quả có cảm giác "deliberate/polished". [ieV5yGq7-hI 12:39–14:03]

**Điều khiển playback**
- **Space** play/stop. Có nút nhảy key trước/sau và ±1 frame. [BNE7CsRE79o 3:26] [JBIn_WC4jSY 13:10]
- Zoom timeline bằng **Ctrl + lăn chuột** (BNE7 chỉ nói "lăn chuột"). Scroll ngang bằng **Shift + lăn chuột**. **Nhấn giữ chuột giữa** để kéo timeline. [PHTPcUdK84I 12:19–12:39] [BNE7CsRE79o 9:03, 9:46] [YHDs-CdYgEc 1:11]
- **Vùng lặp:**
  - Chuột phải + kéo trên thước timeline để tạo selection region, kết hợp nút **Loop/Repeat**. Chuột phải chỗ khác để bỏ.
  - Region này cũng dùng để **render một đoạn**.
  - [BNE7CsRE79o 11:28–12:52] [xH9t-hLVWhY 5:37] [TcNSoStA0Js 14:42]
- **Time markers** có màu và tên. Ẩn hiện qua *View* → display time markers. [PHTPcUdK84I 12:19]
- Nút đồng hồ thêm interval lines. [PHTPcUdK84I 13:30]

**Tự động hóa chuyển động**
- **Walk/run cycle tự động:**
  - Tạo 2 key ở **root** của nhân vật, đủ xa nhau → chuột phải key đầu → **Create walk cycle** (có cả run cycle).
  - Dời root về phía trước ở key 2.
  - Muốn đi ngắn hơn: xóa bớt một bộ key bước và dồn key lại.
  - [nOz-trT5m9U 7:33–7:55] [PHTPcUdK84I 13:30–13:53]
  - PHTP cho rằng auto walk "đã lỗi thời", nên tự làm rồi **tái dùng như "universal movement"**. [PHTPcUdK84I 37:48–38:13]
- **Sửa trượt chân:** dời key cuối của root ra xa hơn cho tới khi chân bám đất. [xH9t-hLVWhY 1:05–1:27] [2Klmj7x8IvI 1:02] [G4KSYcJmdk8 0:46]

**Pose bằng số** (QhMY, quy ước trục của họ, số nguyên văn)
- Run pose: right leg pos Z 3, rot X −20; left leg rot X 20; body rot X 10; left hand pos Y −1, rot X −40, pos Z 1; right hand rot X 40, pos Z −1, pos Y −0.5.
- Frame 10: đảo trái ↔ phải. Frame 5 (passing): chân sau rot X 40, pos Y 1, Z 3; body pos Y 0.5; tay −1; head rot X 0, pos Y 0.5. Copy-paste 10 frame đầu để lặp.
- [QhMY2ac0nOk 5:43–7:34]
- Idle "thở": ở frame 10, tay pos Y −1.5, body pos Y −0.5, head pos Y −0.5, rồi copy-paste. Transition quadratic hoặc back ease in-out. [QhMY2ac0nOk 7:58–8:41]

### 2.4 Parenting, folder, hierarchy

- Model nhân vật là cây phân cấp: body chứa head và arms, nên xoay body thì con đi theo. **Shift-click** để chọn nhiều part và xoay cùng lúc. [TcNSoStA0Js 4:34–5:52]
- **Parent bằng kéo-thả:**
  - Kéo object (ví dụ item hoặc sword) trong timeline list lên part đích (ví dụ tay phải).
  - Object "biến mất" vì tọa độ chuyển sang tương đối với cha. Cách sửa: **reset transform về 0**.
  - Có thể parent qua menu "Parent" trong properties.
  - [nOz-trT5m9U 5:32–5:53]
- **Item:** tạo item → đặt **custom rotation point** trong item properties để cầm tự nhiên. [nOz-trT5m9U 5:12]
- **Armor:** special block "armor" → parent vào Steve → *Hierarchy* → bật **Pose** (inherit pose) để giáp theo dáng. *Appearance* → **Enchantment glint**. [nOz-trT5m9U 12:44–13:05]
- **Folder:**
  - Tạo bằng **Ctrl+F** (PHTP), dùng để nhóm, expand/collapse, hide/lock.
  - Thẻ màu và bộ lọc theo màu. "Ghost" để ẩn tạm.
  - [PHTPcUdK84I 10:22–11:11]
- **Lưu/nhập object:** nút save object; **Ctrl+E** mở file explorer để chèn object đã lưu. Đây là cách tái dùng rig và prop. [PHTPcUdK84I 11:11]
- **Duplicate:** **Ctrl+D** hoặc chuột phải → Duplicate. Bản duplicate là **instance** dùng chung tài nguyên Library (1 Steve trong Library, 2 "dude" trong timeline). [Vn0zjTO4dWY 3:31–4:13] [PHTPcUdK84I 10:22]
- **Chuyển vị trí sang folder sau khi đã đặt:** bấm nút copy tọa độ của object → đặt object về 0 → chọn folder → paste. [YHDs-CdYgEc 4:18–4:39]
- **Folder để tách trục chuyển động (arc):**
  - Nhân vật/vật đi ngang (linear) ở timeline của chính nó; **folder** đi lên xuống với key giữa nâng cao, ease out ở key đầu, ease in ở key cuối. Kết quả là đường cong parabol.
  - Dùng cho nhảy, bóng nảy, vấp ngã, và cả nhún nhảy của chu kỳ chạy.
  - [2Klmj7x8IvI 3:07–3:48] [0ZBmiugjgLg 5:10–5:30] [xH9t-hLVWhY 1:48–2:30]
- **Squash & stretch:** đặt nhân vật vào folder để scale cả khối, đồng thời giữ thể tích (cao thì gầy). [4e_xp4QTAUU 0:42–2:10] [0ZBmiugjgLg 1:03–1:24]
- **Sleeve/phụ kiện trên tay bend:** trong *Hierarchy/inherit* bỏ tick phần "lower half" để phụ kiện bám nửa trên của tay. Gom vào folder "sleeve" và khóa vào upper arm. [xH9t-hLVWhY 9:04–9:26]
- Ẩn (*hide*) và khóa (*lock*) object trong timeline list để tránh click nhầm. [PHTPcUdK84I 10:22] [TcNSoStA0Js 11:01]
- **Cơ chế parent** (SharpWind, Bt53B-WZfTw; có thể là bản 1.x, tên trường 2.0 có thể khác):
  - Parent bằng *Hierarchy → Parent* (chọn object) hoặc **kéo-thả** object lên object cha. [Bt53B-WZfTw 0:25]
  - Sau khi parent, **tọa độ con tính tương đối với cha**. Ví dụ con cách gốc 100, cha cách gốc 50: con nhảy ra chỗ khác, nên phải trừ 50 hoặc đặt 0 để nằm đúng tâm cha. [Bt53B-WZfTw 0:46–1:28]
  - **Các ô "Inherit"** trên object con: position, rotation, scale, rotation point, alpha, color, visibility, bend (khóa vào *lower half* hoặc *upper half* của part bend), texture. [Bt53B-WZfTw 1:28–5:42]
    - Tắt *inherit rotation* thì con đi theo cha nhưng không xoay.
    - Tắt *inherit scale* thì con không phóng to theo.
    - *Inherit scale* tính theo **phần trăm** kích thước cha, nên khó chỉnh tay. [Bt53B-WZfTw 2:10–4:19, 10:13–10:35]
  - Khóa phụ kiện vào **lower half** của tay thì khi bend, phụ kiện đi như đang cầm. Ví dụ lông mày/chi tiết mặt làm bằng part "body" + inherit color để tránh glitch. [Bt53B-WZfTw 4:40–5:21]
  - **Một object màu ẩn điều khiển màu cả rig:** mọi part bật *inherit color* từ một object nhỏ ẩn, đổi một chỗ là đổi cả rig. Không xâu chuỗi inherit color qua nhiều cấp có màu riêng vì màu sẽ "loạn". [Bt53B-WZfTw 6:23–8:50]
  - **Folder lồng nhau theo chức năng** ("scale", "rotation") để mỗi phép biến đổi có pivot riêng, tắt inherit không cần thiết. Rotation point của folder lúc quay "có vẻ lỗi"; cách lách: dời object chính về 0. [Bt53B-WZfTw 9:11–12:07]
  - Mẹo overlap: con **tắt inherit position**, giữ rotation, gắn transition mượt, tạo chuyển động trễ mượt hơn key tay. [Bt53B-WZfTw 5:42–6:23]

### 2.5 Workbench (crafting table): các loại object

- **Danh mục:**
  - Character (mọi mob và biến thể; player slim/wide; skin từ file hoặc theo tên tài khoản Minecraft).
  - Character part. Special model (model từ **Model Bench**). Item (3D, quay về camera, hover, spin).
  - Scenery, Block, Special block (chest, armor…).
  - Shapes: cube, cone, cylinder, sphere, surface/plane. Text (font 3D). Path. Camera.
  - Particle spawner. Light source: point / spot (directional). Audio track. Environment timeline.
  - [JBIn_WC4jSY 1:54] [PHTPcUdK84I 3:43–6:38] [nOz-trT5m9U 2:06]
- Object spawn ra **dính theo con trỏ**, click trái để đặt. [nOz-trT5m9U 2:06] [TcNSoStA0Js 1:53]
- **Back faces mặc định tắt.** Bật lại ở root → properties → *Appearance* → **Show back faces**. [JBIn_WC4jSY ~2:40]
- **Bend tool** chỉ có trên part bend được (tay 1 trục, áo choàng 3 trục). **Sharp bends** cho kiểu Minecraft. [JBIn_WC4jSY 7:15] [PHTPcUdK84I 7:30–7:45]
- **Snapping (nam châm):** đặt giá trị **16** để di chuyển theo từng block (1 block = 16 đơn vị/pixel). [nOz-trT5m9U 4:09–4:29] [PHTPcUdK84I 7:58] [PHTPcUdK84I 11:11–11:35]
- **Custom rotation point:** ví dụ cửa xoay theo bản lề, block vấp ngã (rotation point 8, nâng 8). [PHTPcUdK84I 8:17–8:25] [xH9t-hLVWhY 10:51–11:12]
- **Materials (2.0):** color, alpha/opacity, brightness, mix color.
  - *Surface*: roughness (giảm thì phản chiếu), metallic, emissive.
  - *Subsurface*: radius, color.
  - [JBIn_WC4jSY 7:37–9:02] [PHTPcUdK84I 8:25–9:52]
- **Appearance khác:**
  - Glow (+ "glow from texture", màu glow keyframe được), cast shadows, wind, texture blur, fog.
  - **Render depth** dùng để khoét lỗ hoặc xuyên thấu.
  - Visibility "only in render / only in project".
  - [PHTPcUdK84I 21:22–23:18]
- **Path:**
  - *Add point*, rồi duplicate điểm. **Connect ends** để thành vòng kín; *Detail* chỉnh độ mượt.
  - Gán vào nhân vật qua **Constraints → Follow path**, đưa vị trí về 0, keyframe **Offset** từ key 1 tới key 2. Thêm run cycle.
  - Path còn tạo được shape 3D (độ dày, texture length…).
  - Camera cũng follow path được để có chuyển động mượt.
  - [nOz-trT5m9U 9:38–10:49] [PHTPcUdK84I 14:42–15:30, 29:37] [JBIn_WC4jSY 9:23–9:44]
- **IK (2.0):**
  - **Inverse kinematics** chỉ cho tay và chân. Target nên là object **không nằm trong folder**. Có *angle target* (hướng khuỷu) và độ bám.
  - Community build thêm **look-at** (đầu nhìn theo object) và copy position/rotation/scale/bend; tất cả keyframe được.
  - [JBIn_WC4jSY 9:44–10:24] [PHTPcUdK84I 15:30–16:12, 35:52–36:40]
- **Item slot đổi theo key:** *Custom item slot* gán vào key. Đặt transition **Instant** để item đổi thẳng thay vì "lướt" qua item sheet. Item còn có **texture sequence** để làm texture động. [nOz-trT5m9U 6:13–6:33] [PHTPcUdK84I 16:12–16:34]
- **Particles:**
  - Preset (ví dụ *huge smoke* trên campfire). *Library* → **particle editor** để chỉnh scale và mọi thông số.
  - Có thể keyframe: spawn on/off, **freeze**, clear, attractor.
  - Dùng freeze để làm hiệu ứng "dừng thời gian".
  - [nOz-trT5m9U 8:36–9:18] [PHTPcUdK84I 16:58–20:30] [xH9t-hLVWhY 0:44–1:05]
- **Audio track:** chọn file. Mine-imator **không có sẵn âm thanh game**. Chỉnh volume, cắt đầu/đuôi. [PHTPcUdK84I 26:04–26:26]
- **Library / Resources:**
  - Library đổi model gốc của object.
  - Resources: export base resource pack texture để retexture; nạp texture pack (ví dụ "Bare Bones" cho phong cách trailer Mojang).
  - Đổi setting render như liquid waves thì phải **Resources → reload resource**.
  - [nOz-trT5m9U 2:46] [PHTPcUdK84I 25:19–26:04] [QhMY2ac0nOk 13:30–13:58] [a91bOwulnw8 11:39–12:21]
- **Rig:** **không sửa rig gốc**. Tạo project mới → *import asset* → sửa trên bản copy. [G4KSYcJmdk8 0:25–0:46]

### 2.6 Nhập world, scenery, environment

**Từ pjrAmdnpffA (Part 2: Import world và dựng scene), đọc đủ transcript:**
- *Workbench → Scenery* có hai đường:
  - Pre-made assets: nút **Browse**, gồm rooms, sets, city block, dungeon, buildings, cây (ví dụ big oak).
  - **Import from world**.
  - [pjrAmdnpffA 0:00–0:20, 7:36–8:16]
- **Phiên bản world:** lúc quay, Mine-imator **chưa hỗ trợ save 1.20.1**. Màn hình loading của Mine-imator liệt kê các version asset được hỗ trợ. World không hỗ trợ sẽ mở ra **trống trơn**. [pjrAmdnpffA 0:20–1:02]
- **Bedrock world** phải convert sang Java mới import được. [pjrAmdnpffA 6:55–7:16]
- **Trình import:**
  - Điều khiển giống viewport chính: chuột trái orbit, chuột phải nhìn, WASD, Q/E lên xuống.
  - Click **một lần rồi thả** (không giữ), rê để kéo hộp, click lần nữa để chốt. Kéo cạnh đang highlight để nới hoặc thu.
  - Nút preset **small/medium…** đặt sẵn hộp ở giữa để chỉnh tiếp.
  - [pjrAmdnpffA 1:02–2:25]
- **Import selection:** popup kiểu "24 blocks were found that can be animated" (cửa, cổng, lever, giường).
  - **Yes**: mỗi block là một timeline con animate được.
  - **No**: tất cả gộp thành một khối, project nhẹ hơn.
  - [pjrAmdnpffA 2:25–3:50]
- *Create* → đặt vào scene → **reset vị trí về 0**. [pjrAmdnpffA 2:46–3:08]
- ⚠️ **Scenery đã import là MỘT model, không sửa từng block được** (trừ block animatable). Muốn bỏ block thì phải import lại có lọc. [pjrAmdnpffA 3:50–4:10]
- **Xóa sạch scenery:** xóa khỏi **Library** *và* **Resources**. Nếu còn trong Resources thì scenery vẫn nằm trong project và vẫn hiện ở dropdown import. [pjrAmdnpffA 4:30–4:50]
- **Icon bánh răng "Change world settings":**
  - *Unload regions far away*: tắt đi nếu cần lấy vùng xa vị trí người chơi.
  - **Enable block filter** → *Filter mode*: **Remove** hoặc **Keep**. Gõ tên block (ví dụ Cactus) → bấm mũi tên đưa sang "filtered blocks". Lọc được nhiều block cùng lúc.
  - [pjrAmdnpffA 5:11–6:35]
- **Dựng scene ngay trong Mine-imator:**
  - *Workbench → Block* (ví dụ grass block, oak planks).
  - Trong *Library*, block có **Repeat X/Y/Z** để lát thành tường hoặc sàn.
  - [pjrAmdnpffA 8:36–9:39]
- **Template trong Library:**
  - **Create timeline from template** = thêm một **instance**; sửa template thì mọi instance đổi theo.
  - **Duplicate template** = tạo object riêng để chỉnh khác (ví dụ Repeat X=2).
  - Library hiện số instance (0 = chưa dùng trên timeline).
  - [pjrAmdnpffA 10:00–11:44]

**Từ các video khác:**

- **Import from world:**
  - *Workbench → Scenery → Import from world* → chọn save → đổi *Dimension* (Nether/End) nếu cần.
  - Click trái một lần, rê chuột để chọn vùng, hoặc dùng nút preset box. Kéo mặt hộp để chỉnh kích thước.
  - Có nút nhảy tới vị trí người chơi.
  - [nOz-trT5m9U 2:46–3:28] [PHTPcUdK84I 4:53–5:17]
- **Block filter** (icon bánh răng): *remove* hoặc *isolate* block, ví dụ bỏ wall torch → *Import selection*. [nOz-trT5m9U 3:28–3:48]
- **Animatable blocks** (cửa, lever) hiện popup hỏi giữ hay không. Giữ nhiều sẽ **làm chậm** app. Danh sách block nằm trong dropdown của scenery timeline. [nOz-trT5m9U 3:48–4:09]
- Option giữ vùng đã import trong project kể cả khi world gốc bị xóa; có thể áp texture pack khi import. *Browse* để mở file scenery có sẵn hoặc tải từ ngoài. [PHTPcUdK84I 5:09–5:26] [nOz-trT5m9U 2:59–3:07]
- Thư viện block **không cập nhật theo Minecraft mới nhất**. [QhMY2ac0nOk 1:14]
- **Environment tab:**
  - **Time of day**, **Rotate** (hướng mặt trời).
  - **Sun strength**: 150% đẹp, 200% hơi gắt; QhMY dùng 200–300%.
  - **Sun angle** (angular diameter): 0 = bóng sắc nhất, tăng lên thì bóng mềm.
  - [Vn0zjTO4dWY 12:49–14:15] [QhMY2ac0nOk 2:06–3:18, 9:28]
- **Sky:** Minecraft/custom (ảnh, skybox, sphere), sun/moon texture, **moon phase**. [Vn0zjTO4dWY 14:35–14:55] [PHTPcUdK84I 23:43]
- **Clouds:** normal/**faded**/flat. Thông số: speed (100%, 25%, 300%), offset, height, size, thickness, color. [Vn0zjTO4dWY 15:16–16:39]
- **Ground:** đổi block (ví dụ nước → đại dương) hoặc tắt. QhMY tắt ground khi đã có scenery. [Vn0zjTO4dWY 16:59–17:19] [QhMY2ac0nOk 2:06]
- **Biome** chỉnh màu cỏ, lá, nước (tạo được biome tùy biến). Màu sky, cloud, sunlight, ambient/shadow, night và màu sunrise/sunset. [PHTPcUdK84I 24:07–24:31]
- **Fog:** sky fog, color, **distance** (ví dụ 10000) và **fade size**; kéo fog lại gần để tạo chiều sâu. [Vn0zjTO4dWY 17:41–18:02] [QhMY2ac0nOk 3:18]
- **Wind:** speed, strength. Tắt wind để có "look vanilla" không shader. [Vn0zjTO4dWY 18:22–19:23] [a91bOwulnw8 11:19]
- **Animate environment:** thêm **Environment timeline** (object) rồi keyframe. Thay đổi trong tab Environment sẽ ghi vào key tại cursor. [nOz-trT5m9U 4:51–5:12] [PHTPcUdK84I 25:19]
- **Công thức ánh sáng ngày/đêm** (SharpWind):
  - **Ngày:** sunlight hơi vàng (ngả đỏ khi hoàng hôn), ambient **xanh dương nhạt khử bão hòa**.
  - **Đêm:** giữ cảnh "ngày", sunlight xanh nhạt khử bão hòa, ambient tối hơn, tắt clouds, dùng **sphere khổng lồ inverted** với texture trời sao, cast shadows **off**. Thêm spotlight để cảnh đủ sáng.
  - [xH9t-hLVWhY 10:09–10:51] [2Klmj7x8IvI 4:49–5:56]
- **Công thức "cherry biome đẹp"** (QhMY):
  - Ground off, sun angle 0, time **10:28**, render preset *Extreme*.
  - AO strength >100%, clouds faded, sky xanh hơn, **ambient tint theo màu chủ đạo** (hồng cho cherry), fog gần, sunlight cam, strength 200%.
  - [QhMY2ac0nOk 2:06–3:18]
- **Đừng để lộ mép schematic.** Xoay camera hoặc đặt prop che. [G4KSYcJmdk8 3:30–3:52]

### 2.7 Camera

- Workbench → **Camera**. Có cửa sổ preview riêng; đóng thì mở lại bằng nút góc trên phải viewport. Giữ chuột phải trong viewport camera để lái kiểu FPS, và thay đổi này được keyframe. [nOz-trT5m9U 8:12–8:36] [Vn0zjTO4dWY 5:56–6:59]
- Mỗi camera có **resolution riêng** (ví dụ FHD 1080p) và **FOV**. [PHTPcUdK84I 27:41] [QhMY2ac0nOk 3:47]
- **Hiệu ứng camera:**
  - Depth of field, bloom/glow, lens dirt, color correction (contrast, brightness, saturation, vibrance), tint, film grain, vignette, chromatic aberration, distortion.
  - Rotate-around-point (orbit), camera shake, tone mapping ("light management").
  - [PHTPcUdK84I 27:41–29:37] [nOz-trT5m9U 8:36]
- **Preset camera "đẹp"** (QhMY, số nguyên văn):
  - FOV **30**, aperture ~**5**, Light management **"Academy"** (ACES?), exposure 2.
  - DOF focus range **433** (hoặc 200–500), tăng fade size.
  - Contrast +1–6%, brightness +1–4%, saturation **106%**, vibrance +1–7%, bloom ít.
  - [QhMY2ac0nOk 3:47–4:09, 10:15–11:04]
- **Camera shake thủ công:** tại điểm va chạm, cứ **mỗi 2 frame** dịch camera một chút, biên độ giảm dần về 0. [YHDs-CdYgEc 2:56–3:16]
- Tone mapper trong render settings có tác dụng toàn cục, tiện khi nhiều camera để "None". [a91bOwulnw8 9:38–9:58] (người nói không chắc)
- **Staging:** khung rộng cho cảnh nhiều hành động; nhân vật nhìn/quay về đâu thì người xem nhìn về đó. [0ZBmiugjgLg 2:26–3:07]

### 2.8 Render settings và export

- **Render settings → preset → Custom** để mở toàn bộ thông số. Preset: performance/balanced/extreme… [a91bOwulnw8 0:00–0:20] [nOz-trT5m9U 11:21] [PHTPcUdK84I 30:24]
- **Render distance:** giảm để render nhanh (chỉ giữ quanh camera). Scene size mặc định "3000". [a91bOwulnw8 0:20–0:42] [PHTPcUdK84I 30:24]
- **Samples:**
  - Viewport khi play chỉ dùng 1 sample; khi render, mỗi frame được tích đủ N sample.
  - **50–100 là đủ** [nOz-trT5m9U 11:42]. **~75** cho kết quả tốt, cao hơn ít cải thiện [a91bOwulnw8 1:03].
  - Thời gian ~15 (phút?) cho ~2.5 (phút?) animation ở 75 samples, số bị ASR cắt (ASR?) [a91bOwulnw8 1:23].
- **Ambient occlusion:** mặc định hơi đậm; AnxiousCynic dùng radius **~9**, strength **~60%** [a91bOwulnw8 2:06–2:26]. SharpWind (1.x) dùng radius 23, power 110 [xH9t-hLVWhY 12:17].
- **Shadows / light buffers:**
  - Sun buffer *Big* → *Very big/Gigantic*; spot/point tăng nếu có đèn.
  - SharpWind: sun gigantic, spot gigantic, point big, nhưng tốn RAM.
  - [a91bOwulnw8 2:26–3:09] [xH9t-hLVWhY 12:39]
- **Subsurface scattering:**
  - Đặt ở *material của object* (radius mặc định 0). Cỏ/scenery 5–10; Steve 1–2 cho viền sáng.
  - QhMY khuyên **0.2** cho nhân vật để tạo "rim light" khi đặt spotlight phía sau ban đêm; chỉ hiện ở preset Extreme.
  - Sunlight mạnh thì SSS càng rõ.
  - [a91bOwulnw8 3:29–6:15] [QhMY2ac0nOk 4:32, 13:58–14:22]
- **Indirect lighting:** bật, precision **100%**, strength có thể 200%. [nOz-trT5m9U 12:03] [a91bOwulnw8 6:36–6:56]
- **Reflections:** precision cao, thickness ~**1.5**. Object cần metallic cao/roughness thấp. **Default water reflections** cho nước phản chiếu. [a91bOwulnw8 7:16–8:16, 12:21–13:05]
- **Glow + secondary glow.** Object cần bật Glow trong properties. [nOz-trT5m9U 11:21, 12:03] [a91bOwulnw8 8:36]
- **Anti-aliasing 100** là đủ; cao hơn bị mờ. [a91bOwulnw8 8:57]
- **Bend style:** *Blocky* (khuyên) hoặc *Realistic*. Các mục khác: opaque leaves, liquid waves. [a91bOwulnw8 9:58–11:19] [PHTPcUdK84I 32:22]
- **Render image:** *Render → Render image*: chọn định dạng, **remove background** (PNG trong suốt), include hidden objects, high quality, watermark. [nOz-trT5m9U 12:24] [PHTPcUdK84I 33:02–33:51]
- **Render animation:** *Render → Render animation*:
  - Frame size; format **MP4/MOV/WMV** hoặc **PNG sequence**; **Video quality = Best**; frame rate **24/30/60**.
  - **Include audio** (không áp dụng cho PNG), include hidden objects, high quality rendering, watermark (tắt được sau khi upgrade) → *Save*.
  - [a91bOwulnw8 13:46–15:49] [PHTPcUdK84I 33:51–34:17]
- ⭐ **Dùng PNG sequence cho video dài:**
  - Nếu app crash ở frame 2000, chỉ cần đặt loop region từ 2000 tới cuối rồi render tiếp. MP4 crash giữa chừng có thể hỏng file.
  - Clip ngắn thì MP4 vẫn ổn.
  - [a91bOwulnw8 13:46–14:48]
- **Render một đoạn:** chọn region trên timeline. [BNE7CsRE79o 12:52] [PHTPcUdK84I 33:51]
- **Ctrl+S thường xuyên.** App có crash. [a91bOwulnw8 5:32] [PHTPcUdK84I 34:17, 38:36]

### 2.9 Thói quen quy trình

- **Tự diễn động tác** trước khi animate. [TcNSoStA0Js 7:48] [4e_xp4QTAUU 5:41]
- **Liên tục play từ frame 0** bằng Space để soát timing. [TcNSoStA0Js 8:11] [2Klmj7x8IvI 2:26] [0ZBmiugjgLg 6:51]
- Animate theo **pose-to-pose**: block các pose chính trước, sau đó thêm overlap và easing. [0ZBmiugjgLg 3:07] [4e_xp4QTAUU 11:09]
- Giảm tempo tạm thời để soi arc. [4e_xp4QTAUU 7:24]
- Dùng loop region để soi lại từng đoạn. [BNE7CsRE79o 11:48–12:52]
- Đặt tên object rõ ràng ("dude"), gom folder, gắn màu, khóa object nền. [Vn0zjTO4dWY 3:10] [PHTPcUdK84I 10:22–11:11]
- **Tái dùng chuyển động** ("universal movements"): lưu keyframe hoặc object, áp cho nhiều nhân vật. [PHTPcUdK84I 37:48–38:59] [PHTPcUdK84I 11:55] (nút save keys)
- **Giảm số asset/texture** (gộp texture atlas) để project nhẹ. [G4KSYcJmdk8 2:50–3:10]
- Tắt particles và dùng Flat/Shaded khi animate; chỉ bật Rendered khi chỉnh ánh sáng. [Vn0zjTO4dWY 5:14] [nOz-trT5m9U 4:29]
- **Quy trình làm Shorts 1 giờ (Anvey, eYJK2OnzQ0Y).** Video **không có lời và transcript**. Dữ liệu dưới đây lấy từ mục lục chương (OBSERVED) và từ quan sát storyboard 320×180, độ chính xác thấp, nên mọi mô tả hình là (INFERRED từ ảnh).
  - **Chương (OBSERVED):**
    - 0:09 Software; 0:40 Configure textures & world in Minecraft; 1:08 Searching good place; **1:24 Animation script**; 1:32 Preparing world (trong Minecraft).
    - 4:33 Opening Mine-Imator; 5:13 License key; **5:49 Project resolution & FPS**; 6:17 World import; 8:09–8:22 Resource pack import (cả pack ngoài); 9:04 World position.
    - 9:49 Time of day; 12:15 Fog (density & color); **13:42 Creating camera**; 18:44 Creating characters; 21:36 Subsurface; 22:38 Starting animation; **24:11 Lighting characters**; **30:55 Animation workflow** (dài ~24 phút).
    - 54:45 Particles; 56:33 Particle textures; 57:25 Seed for particles; 58:40 Star effect in sky; **1:04:13 Camera shake**; 1:08:14 Saving; 1:08:42 Render animation settings; 1:09:14 Final result.
  - **Quan sát storyboard (INFERRED từ ảnh):**
    - Camera preview ở viewport phụ là khung **dọc 9:16** suốt video (Shorts).
    - 24:00–28:20: tạo point light; nhiều đèn đặt quanh nhân vật đang T-pose (chiếu sáng riêng nhân vật).
    - 30:00–35:50: lần lượt pose iron golem, villager, player. Camera preview chuyển **close-up nhân vật A rồi close-up nhân vật B**, có lưới 1/3 (shot/reverse-shot).
    - 37:30–44:50: villager bị hất bay ngang, camera bám theo lên trời; player vung tay/đấm; timeline đầy chấm key.
    - 46:30–53:50: iron golem tiến tới, vung tay ném; có lúc chọn một vùng timeline (dải xám) để play lặp đoạn.
    - 58:30–59:50: đặt hình ngôi sao 4 cánh trên trời (star effect).
    - 67:30–68:50: viewport chính chuyển sang góc camera dọc để duyệt lại các shot, cuối cùng mở hộp thoại render.
  - **Bài học** (INFERRED): viết kịch bản trước, chuẩn bị map trong Minecraft rồi mới import; ánh sáng riêng cho nhân vật; chia shot bằng các góc camera close-up luân phiên; gag vật lý (hất bay) + camera shake là xương sống của Shorts.
- Phong cách được khuyên dùng là **kiểu "Mojang trailer"** vì đơn giản, mang tính biểu tượng, dễ học. Phong cách 2017 dùng nhiều bend và diễn cảm. [QhMY2ac0nOk 14:46–17:59]

### 2.10 Lỗi người mới hay mắc

1. **Trượt chân** khi đi hoặc chạy. [2Klmj7x8IvI 1:02] [G4KSYcJmdk8 0:46] [xH9t-hLVWhY 1:05]
2. **Timing**: quá nhanh, quá chậm, hoặc không đều. Sửa bằng cách play thật rồi dời key. [2Klmj7x8IvI 1:45–2:26]
3. **Không có arc**: nhảy theo hình tam giác. [2Klmj7x8IvI 2:46]
4. **Pose**: trọng tâm ra ngoài chân đỡ; không dùng xoay Z của "spine". [2Klmj7x8IvI 3:48–4:49]
5. **Ánh sáng mặc định** chỉ có một nguồn, bóng gắt. [2Klmj7x8IvI 4:49] [G4KSYcJmdk8 2:10–2:50]
6. **Toàn linear.** [2Klmj7x8IvI 6:12] [G4KSYcJmdk8 4:34]
7. **Quên key giữ** nên chuyển động bắt đầu ngay từ frame 0. [TcNSoStA0Js 9:55] [BNE7CsRE79o 2:23]
8. **Nhân vật đứng im** hoặc **đứng thẳng đơ** kiểu pose mặc định. [G4KSYcJmdk8 1:28, 3:10] [YHDs-CdYgEc 7:27]
9. **Over-edit màu/hiệu ứng.** [G4KSYcJmdk8 1:49–2:10]
10. **Lệch phong cách**: skin HD + item thô, texture khác độ phân giải. [G4KSYcJmdk8 3:52–4:34]
11. **Z-fighting** giữa 2 chân. Sửa: scale cả hai chân **0.999** mọi trục. [TcNSoStA0Js 8:31]
12. **Back faces** tắt nên mặt sau vô hình. [JBIn_WC4jSY ~2:40]
13. Làm **nội dung chất lượng thấp** kiểu Monster School. "Quality over quantity". [G4KSYcJmdk8 1:07]

### 2.11 Mẹo nâng cao

- **12 nguyên lý trong Mine-imator:**
  - **Squash & stretch**: giữ thể tích. [4e_xp4QTAUU 0:42–3:14]
  - **Anticipation**: lấy đà trước khi đấm/đá/chạy. Lấy đà càng lâu thì khởi động càng nhanh. [4e_xp4QTAUU 3:34–6:23] [0ZBmiugjgLg 1:47–2:26]
  - **Arcs**. [4e_xp4QTAUU 6:44–9:07]
  - **Overlapping action**: torso là cha; **đẩy key của tay/đầu trễ 1–2 frame** so với body. [4e_xp4QTAUU 11:29–12:51] [0ZBmiugjgLg 3:27–4:07]
  - **Follow-through**: sau va chạm còn trôi thêm một chút. [4e_xp4QTAUU 13:35–17:11]
  - **Secondary action**: đầu quay khi đi; phải tinh tế. [0ZBmiugjgLg 5:58–6:31]
  - **Appeal**: đồng tử to, cười, màu sáng cho nhân vật dễ thương. [0ZBmiugjgLg 7:52]
- **Overlap dạng chuỗi** (tentacle, đuôi): các part khóa nối nhau; mỗi hàng key **trễ thêm 2 tick**. [YHDs-CdYgEc 6:03–6:46]
- **Onion skin/afterimage:** duplicate nhân vật, lùi mọi key 1 frame, alpha **25%**, render depth +1 cho mỗi lớp. [YHDs-CdYgEc 0:30–0:50]
- **Đèn lửa nhiều lớp** (đuốc/hang):
  - Point light ngoài cùng màu tối (range ~200), lớp vàng (~150), lõi trắng.
  - Bắn súng: 3 đèn cam/vàng/trắng, cường độ 0→400→0.
  - [YHDs-CdYgEc 1:33–2:56]
- **Point light ấm cho cảnh:** màu cam-vàng, range ~250, tăng fade size; tắt *render shadows* nếu muốn sáng thoáng. [QhMY2ac0nOk 11:29–11:54] [nOz-trT5m9U 11:00]
- **Đèn trong vật phát sáng** (đèn bí ngô): vật **tắt cast shadows**, rồi bật **Glow**. [nOz-trT5m9U 11:00–11:21]
- **Render depth trick:** tạo lỗ giả dưới đất (surface alpha 1% và render depth <0, cube inverted thấp hơn). [xH9t-hLVWhY 6:41–7:43] [PHTPcUdK84I 21:45–22:10]
- **Mây volumetric:** cube inverted + texture mây, nhiều lớp với render depth giảm dần. [xH9t-hLVWhY 3:52–4:35]
- **Dưới nước:** mặt nước + inverted cube + fog cùng màu + bong bóng. [xH9t-hLVWhY 4:35–5:16]
- **Soft shadow (PCSS):** sun color đen + nhiều spotlight. [xH9t-hLVWhY 6:20–6:41]
- **Light group** (Community Build): đèn chỉ chiếu một nhóm object. Spot light **chiếu được ảnh** (gobo). [PHTPcUdK84I 36:40–37:25]
- **Invert faces** để làm mắt lõm hoặc lỗ. [PHTPcUdK84I 25:41]
- **Material maps (PBR) từ texture pack.** [PHTPcUdK84I 32:42–33:02]

---

## 3. Áp dụng cho Bin & Bo (tập thoại/truyện 1–3 phút)

### 3.1 Top 10 kỹ thuật, xếp theo giá trị

1. **Khóa project: tempo 30 (hoặc 24) = FPS export, resolution 1920×1080, Advanced mode.** Đây là nền cho mọi timing.
   - Mọi cú cắt camera "Instant" sạch khi tempo khớp FPS. [Vn0zjTO4dWY 2:05–2:50] [PHTPcUdK84I 13:03–13:30]
2. **Idle động liên tục cho Bin, Bo, Zu** (thở, nhún nhẹ, đầu xoay): nhân vật không bao giờ đứng im.
   - Dùng công thức key ở frame 0/10/20 với ease in-out rồi copy-paste lặp. [G4KSYcJmdk8 1:28] [YHDs-CdYgEc 7:27] [QhMY2ac0nOk 7:58–8:41]
   - (INFERRED) Với thoại, idle là 70% thời lượng màn hình, nên đây là kỹ thuật có ROI cao nhất.
3. **Pose-to-pose + key giữ (hold) + Ctrl+Q.**
   - Block pose cho mỗi câu thoại; giữ pose bằng key trùng; dùng **Instant** để đổi biểu cảm hoặc texture tức thì. [BNE7CsRE79o 2:23–3:46] [TcNSoStA0Js 11:43]
4. **Easing đúng (ease in-out mặc định, tránh linear) + kiểm tra transition kế thừa.** [BNE7CsRE79o 6:38–9:46] [2Klmj7x8IvI 6:12]
5. **Overlap 1–2 frame** (đầu/tay trễ sau body) **+ anticipation trước cử chỉ lớn.** Biến cử chỉ thoại từ "robot" thành sống động. [4e_xp4QTAUU 11:29–12:51] [0ZBmiugjgLg 1:47]
6. **Camera: nhiều camera và cắt bằng Instant; FOV hẹp (~30) + DOF cho close-up thoại.**
   - Staging: nhân vật nhìn về chỗ khán giả cần nhìn. [BNE7CsRE79o 6:17] [QhMY2ac0nOk 3:47] [0ZBmiugjgLg 2:26]
   - Không video nào trong nhóm A dạy shot/reverse-shot bằng lời. Storyboard của Anvey cho thấy camera luân phiên close-up hai nhân vật trong khung dọc [eYJK2OnzQ0Y ~34:30–35:50] (INFERRED từ ảnh).
7. **Ánh sáng tùy biến thay vì mặc định:**
   - Sun hơi vàng, ambient xanh nhạt khử bão hòa, sun strength ~150%, AO nhẹ (radius ~9, 60%), thêm 1 spot/point fill.
   - Lưu thành **file project mẫu** cho cả series. [2Klmj7x8IvI 4:49–5:56] [a91bOwulnw8 2:06] [Vn0zjTO4dWY 13:54]
8. **Folder tách trục cho nhảy/ngã/nảy** (comedy beat của Zu): ngang linear ở nhân vật, dọc eased ở folder. [2Klmj7x8IvI 3:07–3:48] [0ZBmiugjgLg 5:10]
9. **Render pipeline:** Custom preset, samples 50–100, indirect lighting 100%, AA 100, Blocky bends → **PNG sequence** (chống crash, render tiếp được từ frame lỗi) → ghép âm thanh ngoài. [a91bOwulnw8 13:46–14:48] [nOz-trT5m9U 11:42]
10. **Tái dùng rig, prop, động tác:**
    - Rig gốc giữ nguyên, sửa bản copy qua *import asset*.
    - Lưu object bằng save, chèn lại bằng **Ctrl+E**.
    - Duplicate instance cho vai quần chúng.
    - Xây thư viện "universal movements" (đi, gật, chỉ tay, vẫy) bằng **Export keyframes → Import asset**.
    - Đổi màu cả rig qua một object màu ẩn (inherit color).
    - [G4KSYcJmdk8 0:25] [PHTPcUdK84I 11:11, 37:48] [Vn0zjTO4dWY 3:31] [ieV5yGq7-hI 4:58–5:20] [Bt53B-WZfTw 6:23–8:50]

Bổ sung đáng cân nhắc: **phong cách stop motion** (key mỗi 3–4 frame + Instant) giúp hành động hài của Zu trông "có chủ đích" mà không cần chỉnh easing tỉ mỉ [ieV5yGq7-hI 2:31–3:13, 13:43–14:03]. (INFERRED) Nhưng với cảnh thoại dài, kiểu này có thể bị giật nên chỉ hợp cho beat hành động. Thêm: **audio track trong project** để căn nhịp thoại (import file, trim đầu/đuôi) [PHTPcUdK84I 26:04–26:26], và **camera shake 2 frame** cho beat hài [YHDs-CdYgEc 2:56].

### 3.2 Phân loại: sửa được bằng JSON `.miproject` hay phải dùng GUI

Toàn bộ mục này là **(INFERRED)**: không video nào trong nhóm A mở file .miproject. Tên khóa (POS_X, ROT_Z, TEXTURE_OBJ, TRANSITION, CAM_FOV…) lấy theo brief của owner. Trước khi chạy hàng loạt cần đo bằng một file thật (mở trong GUI, sửa 1 key bằng script, mở lại xác nhận).

| Kỹ thuật | JSON được? | Ghi chú |
|---|---|---|
| Tempo, resolution project | Có khả năng (khóa project-level) | Cần xác nhận tên khóa trong file thật |
| Idle / thở (key POS_Y, ROT_X lặp) | **Có**: sinh key theo chu kỳ, TRANSITION = ease-in-out | Rất hợp để script hóa |
| Pose-to-pose, hold key, copy-paste key | **Có**: nhân bản key với cùng giá trị ở frame mới | Thay thế Ctrl+Q/Ctrl+C/V |
| Instant cho đổi biểu cảm / item / texture | **Có**: TRANSITION="instant" + TEXTURE_OBJ (hoặc item slot) | Cách đổi mặt/miệng khi thoại |
| Đổi easing hàng loạt, tránh linear | **Có**: ghi TRANSITION cho từng key | Tránh bẫy "kế thừa transition" của GUI |
| Overlap 1–2 frame | **Có**: dịch frame của key part con thêm +1 hoặc +2 | Hậu xử lý tự động |
| Camera cut, FOV, vị trí camera | **Có**: CAM_FOV, POS/ROT của camera, TRANSITION instant | Bố cục khung hình đầu vẫn nên kiểm bằng GUI |
| Camera shake | **Có**: nhiễu nhỏ mỗi 2 frame, biên độ giảm dần | |
| Folder tách trục (arc) | Một phần: key thì sinh được, còn tạo folder và parent nên làm trong GUI hoặc trong template | |
| Walk cycle tự động | **GUI** (chuột phải → Create walk cycle); có thể sinh key thủ công bằng script nếu biết pose | |
| Stop-motion hóa (chèn key mỗi 3–4 frame + Instant) | **Có**: lấy mẫu giá trị nội suy linear ở mỗi bước N frame, ghi TRANSITION instant | Cần tự tính nội suy (INFERRED) |
| Thư viện động tác (Export keyframes / Import asset) | GUI xuất/nhập; định dạng file key **chưa đo**, có thể là JSON (INFERRED) | Nên kiểm tra file export đầu tiên |
| Repeat X/Y/Z block, template instance | Thuộc tính Library, có thể nằm trong JSON (chưa đo) | Dựng set đơn giản không cần world |
| Import world / scenery, block filter | **GUI** (trình import world) | |
| Tạo object mới, parent bằng kéo-thả, Hierarchy → Pose | **GUI** (an toàn hơn); JSON có thể có khóa parent nhưng chưa đo | |
| Environment, lighting, render settings | Một phần: keyframe Environment timeline có thể có; preset render nên chỉnh bằng GUI rồi lưu project mẫu | |
| Particle editor, path points, IK target | **GUI** (chưa đo cấu trúc) | |
| Render / export (PNG seq, MP4, include audio) | **GUI** (*Render → Render animation*); chưa thấy video nào nói về CLI render | Rủi ro lớn nhất cho tự động hóa: chưa có cách render headless được đo |

(INFERRED) Quy trình đề xuất: dựng **template project** trong GUI gồm set, ánh sáng, các camera, rig Bin/Bo/Zu trong folder, render preset. Sau đó script JSON sinh key (idle, pose, camera cut, biểu cảm, overlap). Mở GUI để soát và render PNG sequence. Ghép VO/nhạc ở `cf_auto_edit.py`.

---

## 4. Giới hạn và việc còn mở

- Lượt 2 (tab riêng, mở panel transcript YouTube): đã đọc đủ pjrAmdnpffA, Bt53B-WZfTw, ieV5yGq7-hI.
- eYJK2OnzQ0Y **không có captions**. Chỉ dựa vào mục lục chương và 13/30 tấm storyboard (lấy mẫu cách quãng M16–M45, ô 10 s, ảnh 320×180). Không đọc được giá trị số trên panel, nên các thông số camera, ánh sáng, render của video này là **not measured**.
- 8OVe4NGOdv4 không có lời nói; nội dung "lighting" của nó **not measured**.
- Mọi mốc thời gian sai số khoảng ±20 s. Phụ đề là ASR, nên phím tắt E/Q và "Ctrl R" xóa cần kiểm lại trong app.
- Chưa đo trên máy CINE: Mine-imator chưa cài, cấu trúc .miproject chưa xác minh, thời gian render thực tế chưa đo.
