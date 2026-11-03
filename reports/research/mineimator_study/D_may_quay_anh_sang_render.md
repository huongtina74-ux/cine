# Mine-imator 2.0.x — Sổ học Nhóm D: Máy quay, ánh sáng, khói/sương, hạt (particles), render đẹp

Ngày: 2026-11-03 · Người soạn: subagent nhóm D (Claude)
Nguồn: bảng phụ đề YouTube (đa số là ASR tự động tiếng Anh). Mình mở trang watch của từng video trong tab Chrome riêng, mở bảng transcript rồi đọc bằng JavaScript chỉ đọc. Đã đọc **hết toàn bộ** 17 video. Không tải video, không tải file, không gọi API trả phí.
Đối chiếu thêm: mã nguồn Mine-imator 2.0.2 có sẵn trên máy ở `/home/claude/mineimator-src` (`macros.gml`: `mineimator_version "2.0.2"`), và baseline hiện tại của mình ở `tools/mineimator/binbo_thu01/build.py` + `template.miproject`.

**Quy ước nhãn (theo CLAUDE.md):**
- `[videoId mm:ss]`: dẫn nguồn. Mốc thời gian là đầu đoạn phụ đề gần nhất **trước** câu được dẫn, sai số khoảng ±15 giây vì mình gộp mốc theo bước 15 giây.
- **OBSERVED**: điều video nói hoặc làm (có dẫn nguồn), hoặc điều mình thấy trực tiếp trong file/mã nguồn (ghi rõ file).
- **(INFERRED)**: suy luận của mình, video không nói.
- **(ASR?)**: con số hoặc tên mà ASR có thể nghe sai.

**Cảnh báo phiên bản (quan trọng):**
- **Quay trên 2.0 (chắc chắn hoặc rất có thể):** eMMrm, WvOSN, rXsly, Y0gQ, TbTv, uCPv, B9fF, MlXA (2.0 pre-release 5), A5Aw. WC2g quay trên **2.0 Community Build**.
- **Có vẻ quay trên Mine-imator 1.x (INFERRED):** Q7H7, Hj4a, EW0S, UqoG, x_j0. Lý do: các video này nhắc "sunlight range", "follow camera", "bleed light", "glowing block brightness", "spotlight buffer gigantic", và mẹo "contrast 100 / brightness 50".
  - OBSERVED: `project_save_background.gml` của bản 2.0.2 **không có** trường sunlight range hay follow camera.
  - OBSERVED: BeinBian nói mẹo contrast 100 / brightness 50 "đã lỗi thời từ thời 1.2.9" `[TbTvGzYP5N8 4:39]`.
- Nguyên lý ánh sáng và ngôn ngữ máy quay của các video 1.x vẫn dùng được. Nhưng phải dịch sang tên trường của 2.0, và **không chép số** của các video đó vào project 2.0 khi chưa thử.
- **Light groups** (WC2g) không có trong mã nguồn 2.0.2 trên máy. OBSERVED: `grep light_group` không ra kết quả. Coi như tính năng riêng của Community Build. Chưa kiểm chứng trên máy CINE.

---

## 1. Bảng video nhóm D

| # | id | Tiêu đề | Kênh | Độ dài | Lượt xem | Transcript |
|---|---|---|---|---|---|---|
| 1 | eMMrm-tL7mc | How to Use the Camera - Part 6 - Mine-imator 2 Tutorial | AnxiousCynic | 14:39 | 21,556 | Có (399 seg) |
| 2 | WvOSNln0DWY | Mine-imator Tutorial - How To Use Multiple Cameras, Part 16 | AnxiousCynic | 5:08 | 63,063 | Có (135 seg) |
| 3 | rXslyG9nB-w | Mine-imator Tutorial - How To Use The Camera, Part 15 | AnxiousCynic | 16:43 | 28,037 | Có (900 seg; DOM bị lặp đôi, nội dung thật khoảng 450 seg) |
| 4 | M0-5McNt8tE | Camera Psychology! ~ The ULTIMATE Tool For Animation! | SharpWind | 17:15 | 12,901 | Có (1010 seg) |
| 5 | xGsGfdu-2-Q | The Most IMPORTANT Animation Tutorial!! ~ CAMERA LANGUAGE | SharpWind | 13:42 | 3,850 | Có (750 seg) |
| 6 | Y0gQWA4rW0g | Lighting and Glow - Mine-imator 2 Tutorial | AnxiousCynic | 13:27 | 25,082 | Có (760 seg) |
| 7 | TbTvGzYP5N8 | LIGHTING - Mine Imator 2.0.0 Tutorial (FINALLY) | BeinBian | 24:17 | 88,439 | Có (1246 seg) |
| 8 | Q7H78ANxC94 | 9 Tips to Spice up Your LIGHTING in Mine Imator! | SharpWind | 14:13 | 41,147 | Có (1002 seg), có vẻ 1.x |
| 9 | Hj4a1avlL9o | How to Make PRO Lighting in Mine-Imator!! Night / Day Lighting + Movie set Lighting! | SharpWind | 21:54 | 15,654 | Có (1006 seg), 1.x |
| 10 | EW0STx0lxKw | LIGHTING ~ A Mine Imator Tutorial! | SharpWind | 13:23 | 31,856 | Có (798 seg), 1.x |
| 11 | UqoGPnNgcQ4 | INDOOR LIGHTING - Mine Imator Tutorial! | SharpWind | 17:31 | 6,585 | Có (904 seg), 1.x |
| 12 | x_j0jA-QtBQ | Realistic Fog! ~ A Mine Imator Tutorial! | SharpWind | 5:12 | 15,757 | Có (286 seg), 1.x |
| 13 | uCPv8ce6dOI | How to Use Particles - Part 5 - Mine-imator 2 Tutorial | AnxiousCynic | 17:15 | 21,051 | Có (930 seg) |
| 14 | A5AwqxkPV5I | Tutorial Render Realistis - Mine-imator 2.0 Advanced Mode | Dzakyane | 7:19 | 2,420 | Có caption nhưng **chỉ là lời bài hát nền / [Music]**, không có lời hướng dẫn. Mình dùng **mô tả video** (tiếng Indonesia, có chương mục). |
| 15 | WC2gTLI34kc | Rimlight Tutorial - Mine imator 2.0 CB! (Plus Light Groups) | ThoqriMC | 7:45 | 3,410 | Có (59 seg, ASR, nói không chuẩn) |
| 16 | MlXA7M8J5-0 | How to make light edges in Mine-imator 2.0 | Meisner studio | 1:33 | 40,471 | Có (22 seg; chữ chú thích do tác giả gõ, không phải lời nói) |
| 17 | B9fFyYfRURw | Enchanted Items, Armor, & More! - Mine-imator 2 Tutorial | AnxiousCynic | 4:54 | 25,802 | Có (272 seg); hầu như không liên quan máy quay/ánh sáng |

Độ dài và lượt xem là OBSERVED, lấy từ `ytInitialPlayerResponse.videoDetails` lúc đọc (2026-11-03).
Không có video nào n=0 cần chờ retry: cả 17 video đều mở được transcript ngay lần đầu.

---

## 2. MÁY QUAY

### 2.1 Thiết lập camera và tên trường

**FOV (Field of view)**
- FOV giống ống kính tele/góc rộng. Mặc định 45. Tác giả "cho phim điện ảnh thì không nên vượt 45 nhiều"; anh thường để **30–35** cho nhiều shot, tùy shot `[eMMrm-tL7mc 0:40]`.
- Key `.miproject`: `CAM_FOV`. OBSERVED trong `tl_value_default.gml`: mặc định 45.

**Thu hẹp FOV và lùi máy ra xa**
- Đạo diễn thường dùng FOV nhỏ và đặt máy xa. Cách này cho cảm giác gần gũi, nhân vật "quan trọng, có điều trong đầu". FOV rộng làm khán giả không thấy gần, chỉ hợp để cho thấy vùng rộng `[xGsGfdu-2-Q 7:23]`.
- Demo: camera 45° lùi ra sau với FOV nhỏ hơn thì nhân vật trở nên quan trọng `[M0-5McNt8tE 7:47]`.

**Cách tạo camera**
- Vào workbench chọn camera. Có tùy chọn "spawn objects near the camera / copy work camera into new cameras".
- Trong cửa sổ xem trước: chuột phải giữ + WASD; giữ Shift để đi chậm, Space để đi nhanh `[rXslyG9nB-w 0:31]`.

**Depth of field (DOF)**
- Phải bật Depth of field thì mới thấy mờ hậu cảnh `[eMMrm-tL7mc 1:18]`.
- **Depth** = khoảng cách đến điểm lấy nét. **Focal range / Range** = độ dày vùng nét. Ví dụ Range 10 thì hầu hết cảnh bị mờ `[eMMrm-tL7mc 1:18]`.
- **Fade size** = độ chuyển dần từ nét sang mờ. Để 0 thì mặt phẳng nét rất mỏng; 15 thì chuyển rất gắt, hợp cảnh tí hon hoặc giả lập tele `[eMMrm-tL7mc 2:00]`.
- **Blur size** = độ mờ tối đa `[eMMrm-tL7mc 2:44]`.
- Key và mặc định (OBSERVED, `tl_value_default.gml`): `CAM_DOF` (bật/tắt), `CAM_DOF_DEPTH`, `CAM_DOF_RANGE` (200), `CAM_DOF_FADE_SIZE` (100), `CAM_DOF_BLUR_SIZE` (0.01).

**Quy tắc DOF**
- Shot tele (FOV hẹp) thì cho DOF nông. Shot rộng thì Range khoảng 260, đừng nông quá `[rXslyG9nB-w 5:19–6:37]`.
- Fade size mặc định 100. Tác giả dùng 100–1000; 1000 cho shot rộng rất mềm `[rXslyG9nB-w 6:37]`.
- Bộ số ví dụ chép sang keyframe kế tiếp: "40, 10 và 50" (thứ tự trường chưa rõ, ASR?) `[rXslyG9nB-w 8:15]`.
- **Mọi thông số camera lưu theo từng keyframe.** Nên chỉnh xong shot rồi mới tạo keyframe tiếp theo, để giá trị được chép theo `[rXslyG9nB-w 7:43]`.
- "Rack focus": về cuối shot tăng Range/Fade để hậu cảnh vào nét `[rXslyG9nB-w 8:47]`.

**DOF blur size trong Render settings**
- Mặc định 2%. Tác giả thích để thấp và tinh tế: "đừng làm quá nếu chưa biết mình làm gì" `[rXslyG9nB-w 9:47]`.

**Cách lấy nét nhanh của BeinBian**
- Bước 1: đẩy blur size lên max 10, Fade size 2, Range khoảng 80.
- Bước 2: chỉnh Depth cho đến khi thấy rõ đường cắt nét đi qua nhân vật.
- Bước 3: hạ blur về khoảng 1 và tăng lại Fade size `[TbTvGzYP5N8 12:58–13:34]`.
- Mình chưa xác định được thang đo trong file giữa "blur 10" trên UI và giá trị lưu (mặc định 0.01). Có thể UI hiển thị theo %. Chưa đo.

**Aperture (blades, blade angle)**
- Thông số hình dạng bokeh. Tác giả nói chưa rõ ảnh hưởng trong MI `[eMMrm-tL7mc 3:02]`.
- Key: `CAM_BLADE_AMOUNT`, `CAM_BLADE_ANGLE`.

**Light management (trên camera)**
- **Tone mapper:**
  - Reinhard: mềm hơn, contrast thấp hơn `[eMMrm-tL7mc 3:44]`.
  - "Academy (ACES)": tương phản và bão hòa hơn `[TbTvGzYP5N8 2:48]`.
- **Exposure** (đẩy lên 3 thì sáng hẳn) và **Gamma** (để 1 thì nhìn khác) `[eMMrm-tL7mc 4:12]`.
- BeinBian: Gamma cao làm bóng mềm hơn, thấp làm bóng sâu và kịch tính hơn. Anh thích ACES `[TbTvGzYP5N8 2:33–3:51]`.
- Key: `CAM_LIGHT_MANAGEMENT`, `CAM_TONEMAPPER`, `CAM_EXPOSURE` (mặc định 1), `CAM_GAMMA` (2.2).
- Thứ tự lựa chọn trong file ngôn ngữ (OBSERVED, `english.milanguage`): none / reinhard / aces. Suy ra giá trị 0/1/2 (INFERRED, chưa thử).

**Rotate around point (quỹ đạo quanh một điểm)**
- Bật lên thì có góc **XY**, góc **Z**, **distance** (khoảng cách), và tùy chọn "look at rotation point". Tắt "look at" thì làm được các cú dolly lạ `[eMMrm-tL7mc 4:28]`.
- Dùng khi đi tuyến tính từ A sang B làm máy lướt sát mặt nhân vật `[rXslyG9nB-w 10:36]`.
- Cách làm:
  - Bật tùy chọn này trên **cả hai** keyframe (vì nó keyframe được) `[rXslyG9nB-w 11:44]`.
  - Animate XY (ví dụ 180° để vòng ra trước mặt) và Z.
  - Đường xanh nhạt trên gizmo là khoảng cách; kéo gizmo thì dời cả máy lẫn tâm `[rXslyG9nB-w 12:00–13:02]`.
  - Tăng distance ở frame giữa để máy không lướt sát `[rXslyG9nB-w 14:36]`.
  - Keyframe của shot sau có thể tắt orbit `[rXslyG9nB-w 15:22]`.
- Key: `CAM_ROTATE`, `CAM_ROTATE_ANGLE_XY`, `CAM_ROTATE_ANGLE_Z`, `CAM_ROTATE_DISTANCE` (mặc định 100).

**Camera shake**
- Hai chế độ: **Positional** (dịch vị trí) và **Rotational** (xoay; giống động đất). Tác giả thích Rotational `[eMMrm-tL7mc 5:28–6:14]`.
- Strength và Speed chỉnh riêng từng trục.
- Keyframe được: ví dụ tại frame 60 giảm speed X, tăng Z lên 300%, thì độ rung thay đổi dần tới key đó. Đây là "cách dễ nhất để thêm rung" `[eMMrm-tL7mc 6:14–7:01]`.
- Key: `CAM_SHAKE`, `CAM_SHAKE_MODE`, `CAM_SHAKE_STRENGTH_X/Y/Z`, `CAM_SHAKE_SPEED_X/Y/Z` (mặc định đều 1).
- Video **không đưa con số strength cụ thể** nào cho cảnh "nhẹ".

**Hiệu ứng ống kính khác** `[eMMrm-tL7mc 7:10–13:52]`. Key OBSERVED trong mã nguồn, mặc định trong ngoặc:
- **DOF anamorphic ratio, Edge highlight, Highlight boost, Boost threshold:** boost giúp nắng "gắt thật"; threshold chọn chỉ mây được boost.
- **Color fringe:** tách RGB, kiểu VHS.
  - BeinBian để chromatic aberration blur rất nhỏ, khoảng 2–3 `[TbTvGzYP5N8 20:46]`.
  - SharpWind để fringe khoảng 6% cho cảnh horror `[EW0STx0lxKw 9:40]`.
- **Bloom:** threshold, radius, intensity, anamorphic ratio. Key: `CAM_BLOOM`, `CAM_BLOOM_THRESHOLD` (.85), `CAM_BLOOM_INTENSITY` (.4), `CAM_BLOOM_RADIUS` (1), `CAM_BLOOM_RATIO`, `CAM_BLOOM_BLEND`.
- **Lens dirt:** cần texture. Key: `CAM_LENS_DIRT*`.
- **Color correction:** contrast, brightness, saturation (0 = đen trắng), vibrance, color burn. Key: `CAM_COLOR_CORRECTION`, `CAM_CONTRAST` (0), `CAM_BRIGHTNESS` (0), `CAM_SATURATION` (1), `CAM_VIBRANCE` (0), `CAM_COLOR_BURN` (trắng).
- **Film grain:** strength, saturation, size; hạt to "nhìn rất tệ". Key: `CAM_GRAIN*`.
- **Vignette:** radius, softness, strength, color. Màu đỏ/xanh dùng để biểu cảm. Key: `CAM_VIGNETTE*`.
- **Chromatic aberration và Distort:** blur amount, distort RGB, zoom, distort amount, repeat image. Key: `CAM_CA*`, `CAM_DISTORT*`.
- **Lưu ý ổn định:** Mine-imator **crash 2 lần** khi tác giả chỉnh các hiệu ứng này `[eMMrm-tL7mc 2:56, 10:38]`. Nên lưu thường xuyên (INFERRED).

### 2.2 Cắt cảnh và nhiều camera

**Cách chính: 1 camera + transition "instant"**
- Đổi góc mà không đặt instant thì máy "bay xuyên cảnh". Kể cả hai key chỉ cách 1 frame, khán giả vẫn thấy lỗi `[rXslyG9nB-w 2:39–3:12]`.
- Cách đúng: đặt transition của keyframe **cuối shot** thành **Instant**. Máy đứng yên cho tới key tiếp theo rồi "nhảy" sang. "Mỗi lần cắt góc, hãy dùng instant" `[rXslyG9nB-w 3:27–4:00]`.
- Hai góc đều chuyển động vẫn cắt mượt với nhau được. Key đầu shot có thể dùng ease in/out để máy khởi động và dừng chậm `[rXslyG9nB-w 4:15–4:47]`.
- Hiện tác giả **chỉ dùng 1 camera** cho mọi phim. Cách nhiều camera chỉ còn là tùy chọn `[WvOSNln0DWY 0:15]`.

**Nhiều camera**
- Đặt tên Camera A/B `[WvOSNln0DWY 0:46]`.
- "Active camera" là camera mà MI dùng để render. Khi đang chọn một camera, viewport hiện "Selected camera". Bỏ chọn hết mới thấy đúng camera sẽ render `[WvOSNln0DWY 1:47, 4:10]`.
- Cắt: tại frame chuyển (ví dụ 70), camera A key **Visible = off**, camera B key **Visible = on**. Cắt về thì đảo lại. "Toggle visibility và chồng keyframe" `[WvOSNln0DWY 2:19–4:10]`. Key: `VISIBLE`.
- Tác giả *nghĩ* camera spawn gần nhất sẽ thành active, nhưng không chắc `[WvOSNln0DWY 2:02]`.

**So với pipeline của mình**
- OBSERVED: `build.py` đã đi đúng cách chính: 1 camera, mỗi shot gồm key đầu `easeinoutsine` và key cuối `instant` (`K(cam,e,'instant',...)`).
- Không cần chuyển sang nhiều camera.

### 2.3 Ngôn ngữ và tâm lý máy quay (SharpWind)

**Hướng nhân vật so với camera** ("coi camera là khán giả") `[M0-5McNt8tE 2:49–4:55]`
- **Chính diện:** kết nối thân mật, tin tưởng.
- **Hơi xoay:** vẫn thân mật nhưng bớt can dự.
- **Nghiêng hẳn (profile):** xa cách, nhân vật đang chìm trong suy nghĩ, khán giả tò mò.
- **3/4 quay lưng:** "quay lưng với ta", mặt tối của nhân vật; hợp trước một quyết định lớn.
- **Quay lưng 180°:** cắt đứt liên hệ.
- **Tay hướng vào camera** = đang chú ý. **Tay khép vào trong** = khép kín, thiếu tự tin. **Tay mở** = vui, cởi mở.
- Chi tiết vi mô như cỡ đồng tử cũng quan trọng `[M0-5McNt8tE 5:10]`.

**Cỡ cảnh ("plans")**: 4 nhóm `[M0-5McNt8tE 5:41–6:44]` `[xGsGfdu-2-Q 1:36–3:27]`
- **Wide/Total:** cho thấy bối cảnh, đặt nhân vật vào nơi chốn, mở đầu cảnh hoặc đến nơi mới.
- **Medium:** cho thấy nhân vật đang làm gì. "American plan" cắt ngang gối.
- **Close:** phản ứng, cảm xúc trên mặt.
- **Detail:** thông tin không được bỏ lỡ (ví dụ mắt đang giận). **Ngắn, chỉ khoảng 1–2 giây.** **Đừng lạm dụng**, kẻo mất giá trị `[xGsGfdu-2-Q 2:55–3:27]`.

**Góc máy** `[M0-5McNt8tE 7:01–7:47]` `[xGsGfdu-2-Q 3:27–4:47]`
- **Ngang mắt:** trung tính.
- **Từ dưới lên:** nhân vật mạnh, cao thượng, quan trọng.
- **Từ trên xuống:** nhân vật nhỏ bé, đáng xấu hổ, không quan trọng.
- **Bird's view:** góc nhìn tổng thể, khách quan.
- **Frog's view:** nhân vật như "chúa tể", khán giả thấy mình nhỏ bé.
- **Dutch tilt (nghiêng):** có điều gì đó không ổn. Nghiêng *trong lúc quay* thì càng bất an.

**Chuyển động máy** `[M0-5McNt8tE 11:30–14:07]` `[xGsGfdu-2-Q 4:47–7:08]`
- SharpWind: "mình hiếm khi dùng máy đứng yên". Máy chuyển động kéo khán giả vào cảnh.
- **Handheld** (giả máy cầm tay): khán giả thấy gần và thấu cảm hơn.
- **Pan:** hé lộ dần, tạo chờ đợi.
- **Move in** (dolly vào, *không* đổi FOV): gây tò mò.
- **Move out:** muốn tránh xa, rợn.
- **Dolly-zoom** (tăng FOV và đẩy máy lại gần; nhân vật giữ nguyên cỡ, hậu cảnh méo): "cú đánh cảm xúc". Kết hợp tilt thì thành sốc.
- **Crane/dynamic camera:** quay vòng quanh hành động, hợp cảnh đánh nhau. "Với cảnh thường thì vô nghĩa".

**Bố cục**
- **Rule of thirds** (MI có lưới gợi ý). Chỉ cần đặt *gần* đường, không cần trúng hẳn `[M0-5McNt8tE 9:05–10:10]`.
- **Central composition** cho đối tượng chính. **Đừng cắt nửa đối tượng** như nhà bị cắt đôi. Đường chân trời đặt trên đường 1/3 dưới `[M0-5McNt8tE 10:10–11:14]`.
- BeinBian liệt kê thêm `[TbTvGzYP5N8 6:28–11:57]`:
  - Symmetry và frame-within-frame.
  - Diagonals/triangles tạo năng lượng.
  - Breaking the pattern.
  - Filling the frame (kèm DOF nông).
  - Negative space tạo cảm giác cô độc.
  - **Rule of space:** chừa khoảng trống theo hướng nhân vật đi hoặc nhìn; trái→phải đọc tự nhiên.
  - Balancing elements, golden ratio.
  - Context qua lớp tiền, trung, hậu cảnh.

**Định dạng, fps, màu, phơi sáng** `[xGsGfdu-2-Q 8:40–11:32]`
- Khuyên giữ **16:9**. 2.35 là CinemaScope.
- **25 hoặc 30 fps** "cho cảm giác điện ảnh, không phải 60".
- Ảnh sáng thì ấm và vui, ảnh tối thì ngược lại. Cảnh tối kiểu Hollywood luôn có **viền sáng (outline/rim)** quanh nhân vật. Cảnh tối "gần như bất khả trong MI trừ khi làm sáng hơn".
- Giữ white balance đẹp; sửa ở hậu kỳ nếu cần.

**Màu và độ tương phản theo cảm xúc** `[M0-5McNt8tE 14:23–16:13]`
- Ấm và sáng = vui, "thời xưa tươi đẹp". Lạnh = mùa đông, buồn. Tối = không sự sống, bão. Contrast thấp = mềm, tự nhiên, vui. Contrast cao = gắt, tối.
- Color correction **contrast 15 là quá nhiều, 6 vẫn quá, anh dùng khoảng 3**: "các thông số này rất nhạy". Thang lưu trong file chưa rõ; mặc định `CAM_CONTRAST`=0 (INFERRED: có thể là 0.03).

**Bắn về phía nguồn sáng / phía bóng**
- Đặt máy để thấy mặt ở phía bị khuất sáng = cảm giác điện ảnh `[Q7H78ANxC94 5:29–5:44]`.

**Mỗi khung hình phải "đẹp như hình nền"**
- Mỗi lần đổi camera đều phải đạt chất lượng wallpaper `[Q7H78ANxC94 7:51]`.

**Điều transcript KHÔNG nói** (mình không bịa)
- Không video nào nói về **quy tắc 180°**, **over-the-shoulder** theo tên, **shot–reverse shot**, hay **độ dài shot chuẩn** (ngoài "detail 1–2 giây").
- Các quy tắc đó ở mục 4 là **(INFERRED)** theo kiến thức điện ảnh phổ thông.

---

## 3. ÁNH SÁNG VÀ KHÔNG KHÍ

### 3.1 Loại đèn và thông số

**Point light và Spotlight**
- Point phát mọi hướng. Spot chỉ một hướng và **tốn RAM ít hơn**. SharpWind dùng spot trừ khi nguồn sáng nằm giữa hình `[EW0STx0lxKw 1:21]`. "Point light lag" `[UqoGPnNgcQ4 3:45]` (video 1.x).
- AnxiousCynic (2.0) dùng point cho đèn trong nhà và spot cho trăng ngoài cửa sổ `[Y0gQWA4rW0g 1:18, 6:59]`.
- Kiểu timeline (OBSERVED, `app_startup_lists.gml`): `"pointlight"`, `"spotlight"`, `"particles"`.

**Key đèn** (OBSERVED, `tl_value_default.gml`)

| Key | Mặc định | Ghi chú |
|---|---|---|
| `LIGHT_COLOR` | trắng | |
| `LIGHT_STRENGTH` | 1 | = 100% (INFERRED) |
| `LIGHT_SPECULAR_STRENGTH` | 1 | |
| `LIGHT_SIZE` | 2 | |
| `LIGHT_RANGE` | 250 | đơn vị pixel |
| `LIGHT_FADE_SIZE` | 0.5 | = 50% |
| `LIGHT_SPOT_RADIUS` | 50 | |
| `LIGHT_SPOT_SHARPNESS` | 0.5 | |

**Đơn vị:** 1 block = 16 đơn vị. Range 16 thì ánh sáng chỉ đi được 1 block `[UqoGPnNgcQ4 1:54]`.

**Size → độ mềm của bóng**
- Size 0 cho bóng sắc. Size càng lớn bóng càng mềm. AnxiousCynic chọn **2** `[Y0gQWA4rW0g 2:37]`.
- Trăng: size **4** để bóng mềm hơn ("trăng ở rất xa") `[Y0gQWA4rW0g 8:03]`.
- Light edges: size **≤ 32**, fade size max `[MlXA7M8J5-0 0:53]`.

**Các đèn cộng dồn lên nhau**
- Có thể chồng nhiều đèn khác màu, khác range để tạo "lớp ánh sáng" thật hơn `[UqoGPnNgcQ4 2:26–2:57]`.

**Render shadows và cast shadows**
- Khối phát sáng (đèn redstone) phải **tắt cast shadows**, nếu không nó chặn chính ánh sáng của mình. Đèn để **Render shadows = on** (mặc định) cho thật `[Y0gQWA4rW0g 1:34]`.
- Có thể tắt shadows trên một đèn fill để tránh bóng chồng chéo `[Y0gQWA4rW0g 5:40]`.
- "Glow không đổ bóng" `[Q7H78ANxC94 9:54]`.

**Emissive và Glow**
- Material **Emissive** khoảng **125%** làm khối sáng hơn nhưng **không phát ra ánh sáng thật**. Phải thêm đèn `[Y0gQWA4rW0g 1:01]`.
- Appearance > **Glow** trên khối đèn `[Y0gQWA4rW0g 9:04]`.
- Render settings > Glow: bật **secondary glow**.
  - Glow chính: radius khoảng **1200** (ASR? có thể là 1200%), intensity khoảng **125**.
  - Secondary: radius khoảng **10%**, intensity khoảng **35–40%**.
  - Kết quả: quầng sáng xung quanh và lõi sáng gắt `[Y0gQWA4rW0g 9:50–11:09]`.
  - Template mình đang để `render_glow_radius`=1, `render_glow_intensity`=1. Thang UI ↔ file chưa đo.

### 3.2 Bố trí đèn kiểu điện ảnh

**3 điểm**
- **Key** (đèn chính). **Fill** đặt phía đối diện, cường độ thấp hơn, làm mềm bóng của key. **Back** đặt sau lưng để tách nhân vật khỏi nền và tạo chiều sâu `[TbTvGzYP5N8 5:25]`.
- AnxiousCynic: "tối thiểu nên có 3 nguồn sáng" `[Y0gQWA4rW0g 3:23]`.

**Tỉ lệ (SharpWind, 1.x)**
- Key khoảng 3/4 cường độ tối đa. Fill bằng **1/4–1/2**, "khoảng một nửa key". Ví dụ key 250 thì fill 125 `[Hj4a1avlL9o 7:54–8:24]`.
- Fill đặt **sát camera**, fade 100, mềm và khuếch tán `[Hj4a1avlL9o 7:54–8:40]` `[EW0STx0lxKw 2:22]`.

**Backlight**
- Theo công thức thì back = 333, nhưng "trong Mine-imator backlight gần như vô dụng" ở setup đó `[Hj4a1avlL9o 10:36–12:07]`.
- Ngoài trời có thể dùng nó như phản chiếu bầu trời `[EW0STx0lxKw 3:24]`.

**4–5 điểm ngoài trời**
- Thêm **background light** chiếu nền, cùng phía với key. Nhân bản thêm vài đèn nền từ hướng khác, màu thấp hơn, đóng vai "fill thứ hai cho nền" `[EW0STx0lxKw 2:53–3:40]`.

**Environmental lighting**
- Chỉnh đèn riêng cho từng shot rất tốn công. Nên đặt đèn sao cho mọi góc máy đều đẹp `[EW0STx0lxKw 4:56–5:28]`.
- Nhưng SharpWind vẫn khuyên "đặt lại đèn 3/4 cho từng shot thì đẹp hơn" `[EW0STx0lxKw 12:31]`.

**Đơn giản nhất (2 đèn)**
- **Mặt trời làm key** cộng **1 spotlight làm fill** để khuếch tán bóng, tăng sunlight strength. "Chỉ 2 đèn đã đẹp hơn hẳn" `[EW0STx0lxKw 7:00–7:32]`.

**Motivated light**
- Nguồn sáng thấy trong hình (lửa trại, đèn) kèm **một spotlight thật sự chiếu lên nhân vật** từ hướng nguồn đó. Đây là mẹo Hollywood `[Q7H78ANxC94 4:26–5:14]`.
- Có thể thêm spot từ trên để khuếch tán bóng, và spot xanh phía kia giả ánh trăng `[Q7H78ANxC94 5:14]`.

**Tương phản màu**
- Dùng cặp bổ túc: cam/xanh, đỏ/lục, tím/vàng. Ví dụ ánh trăng lạnh ở nền, ánh ấm trên nhân vật, thì mắt hướng vào nhân vật `[Q7H78ANxC94 6:02–7:05]`.

**Ánh sáng nảy (bounce)**
- Đèn màu cạnh bề mặt màu (hoa, tường, thảm) `[Q7H78ANxC94 7:05]`.
- Đèn yếu cùng màu với ánh sáng ngoài cửa, đặt trên trần giả ánh phản `[UqoGPnNgcQ4 14:32–15:37]`.
- Spot đặt trên sàn chiếu ngược lên tường, hơi xanh `[UqoGPnNgcQ4 8:25]`.

**Bóng mềm kiểu PCSS**
- Vài spotlight đặt cạnh nhau, lệch nhẹ, mỗi cái yếu bớt vì các đèn cộng dồn `[UqoGPnNgcQ4 6:22–7:53]` `[EW0STx0lxKw 6:13]`.

**"Mọi mặt đều được chiếu, nhưng độ sáng khác nhau"**
- Tạo sự đa dạng `[EW0STx0lxKw 12:31]` `[EW0STx0lxKw 2:22]`.

**Rim light và viền sáng**
- **Subsurface scattering** trên nhân vật tự tạo viền sáng:
  - AnxiousCynic giữ subsurface **1** để có "light bleed / edge rim" `[Y0gQWA4rW0g 3:07]`.
  - BeinBian: radius **1** thì có rim; **0.1** cho rim mỏng; lớn hơn thì ánh sáng thấm vào nhiều `[TbTvGzYP5N8 14:05–14:35]`.
  - ThoqriMC dùng khoảng **1.4–1.5** `[WC2gTLI34kc 3:08]`.
  - Meisner: ánh sáng chỉ "xuyên" sang mặt kia khi **radius > 1**, nên dùng **1–2** `[MlXA7M8J5-0 0:35]`.
  - Key: `SUBSURFACE`, `SUBSURFACE_RADIUS_RED/GREEN/BLUE`, `SUBSURFACE_COLOR`.
- **Đèn sau lưng nhân vật**, chiếu vào mép (spot `[WC2gTLI34kc 2:36]`, point `[MlXA7M8J5-0 0:19]`). Giảm ánh sáng môi trường để rim nổi `[WC2gTLI34kc 1:51]`. Meisner: "Day on is not suitable" (bật ban ngày thì không hợp) `[MlXA7M8J5-0 0:00]`.
- **Render > subsurface highlight** điều khiển độ sáng mép: ThoqriMC dùng khoảng **10**; 100 quá mạnh `[WC2gTLI34kc 4:16–4:49]`. Template mình có `render_subsurface_highlight`=0 (OBSERVED).
- **Subsurface samples:** viền mỏng thì **1** là đủ; viền mềm thì tăng samples, nhưng **> 64 vô ích** `[MlXA7M8J5-0 0:35–0:53]`. Template có `render_subsurface_samples`=0 (OBSERVED).
- Đèn thứ hai mạnh hơn, phía đối diện (ánh trăng), để **tách nhân vật khỏi nền** `[Q7H78ANxC94 11:42]`.
- **Light groups** (chỉ có trên CB): đèn rim chỉ tác động lên nhân vật cùng group, mặt đất không bị ảnh hưởng `[WC2gTLI34kc 5:20–6:43]`. Không có trong 2.0.2 (OBSERVED: grep).

### 3.3 Môi trường: mặt trời, ambient, sương mù, trời

**Sunlight strength**
- BeinBian luôn để **200** thay cho 100 vì thích nguồn sáng mạnh `[TbTvGzYP5N8 13:50]`.
- Key `sunlight_strength` / `BG_SUNLIGHT_STRENGTH`. Template hiện 1 (INFERRED: 1 = 100%, nên 200% → 2).

**Sunlight angle = độ mờ của bóng**
- 0.076 rất sắc. BeinBian để **0.4–0.5** `[TbTvGzYP5N8 14:35]`. Template hiện `sunlight_angle` 0.526 (OBSERVED), đã gần dải này.

**Xoay mặt trời để chọn góc**
- `[TbTvGzYP5N8 13:50]`. Nghiêng mặt trời nhẹ cho bóng trên nhà "động" hơn `[Q7H78ANxC94 8:52]`.
- Mặt trời phải khớp hướng key light; nếu không, nhân vật "trông buồn cười" `[Hj4a1avlL9o 6:17]`.

**Màu nắng**
- Ban ngày: **hơi cam** cho ấm và tự nhiên, thay vì trắng tinh `[Hj4a1avlL9o 1:41]`.
- BeinBian dùng nắng xanh hoặc trắng cho theme xanh `[TbTvGzYP5N8 15:07]`.

**Ambient color = màu của bóng**
- "Muốn vùng tối có màu gì thì chọn ambient màu đó" `[TbTvGzYP5N8 15:07]`.
- **Xanh đậm khử bão hòa** cho cảm giác có khí quyển `[Hj4a1avlL9o 2:12]`.
- Bóng ngoài đời hơi xanh: tối muộn thì xanh đậm, ban ngày xanh nhạt; "đừng biến mọi thứ thành xanh" `[UqoGPnNgcQ4 15:52–16:23]`.

**Fog**
- **Fog distance** = điểm mà từ đó không thấy gì nữa. **Fog size** = bề rộng vùng chuyển từ không sương sang sương đặc `[Hj4a1avlL9o 4:01–5:12]`.
- Để **distance cao, size lớn** cho sương rất dần `[Q7H78ANxC94 5:44]`.
- Đừng để thế giới trông "bị cắt cụt": tăng distance và size để vẫn thấy cây ở xa `[TbTvGzYP5N8 15:37–16:09]`.
- Màu sương: xanh trắng cho sương buổi sáng `[Hj4a1avlL9o 4:01]`; hoặc màu gần với màu cảnh `[x_j0jA-QtBQ 2:19]`.
- "Dùng fog đi, tin mình" `[Q7H78ANxC94 5:44]`.
- Key: `fog_show`, `fog_distance`, `fog_size`, `fog_height`, `fog_color_custom`, `fog_color` (OBSERVED trong template/mã nguồn).

**Cảnh sương dày**
- Sương khuếch tán ánh sáng nên không được có bóng rõ: **nắng xám, ambient xám** (giữ chút xanh) `[x_j0jA-QtBQ 3:24]`.

**Sương "thật" bằng mặt phẳng phát sáng**
- Cube dẹt dán texture nhiễu (turbulence), bật Glow + "only render glow", rải nhiều lớp `[x_j0jA-QtBQ 1:19–3:08]`.
- Giới hạn: máy xuống dưới mặt phẳng thì mất lớp; phải chỉnh theo từng shot `[x_j0jA-QtBQ 4:12]`.
- Tác giả tải texture từ Google. **Mình không làm vậy.** Nếu dùng, tự sinh noise PNG bằng Python (INFERRED).

**Bầu trời và mây**
- Có thể nâng độ cao mây `[Hj4a1avlL9o 3:00]`.
- Làm trời sáng hơn để bloom bắt vào `[TbTvGzYP5N8 16:09]`.
- Sphere đảo mặt trong (inverted) dán texture trời, custom rotation point 0, scale phủ toàn cảnh, tắt fog/shadows/SSAO trên nó, tắt clouds `[Q7H78ANxC94 2:38]` `[Hj4a1avlL9o 13:13]`. A5Aw gắn sphere/cube trời **vào camera** (theo mô tả).
- Mây "khối" bằng các cube texture mây trong suốt, render depth giảm dần ra xa, tới **-4** `[Hj4a1avlL9o 16:39–18:32]`.
- **Lưu ý:** texture trời và mây phải là tài sản của mình (luật IP của CineFactory).

**Biome và màu cỏ, lá, nước**
- Biome đổi màu cỏ `[Hj4a1avlL9o 1:25]` `[TbTvGzYP5N8 12:28]`.
- Custom biome: đổi màu nước, cỏ, lá theo mood `[TbTvGzYP5N8 21:19]`.

**Phóng to cảnh**
- Scale cả scenery và nhân vật lên để lỗi ánh sáng và glow viền ít lộ `[Hj4a1avlL9o 2:44, 20:41]` `[EW0STx0lxKw 5:43]` (video 1.x; chưa kiểm chứng trên 2.0).

### 3.4 Render settings

**Bật Custom**
- Cả AnxiousCynic và BeinBian đều vào Project properties > Render settings > **Custom** rồi mới chỉnh `[Y0gQWA4rW0g 9:19]` `[WC2gTLI34kc 0:58]`. A5Aw cũng vậy (mô tả 0:05).
- Template của mình có `"render_settings": "performance"` (OBSERVED). Trong mã nguồn, `render_default` = "performance".
- **Chưa đo** việc khi để "performance" thì Mine-imator có bỏ qua các giá trị trong khối `render` của file hay không. **Cần thử** bằng cách đặt "custom" rồi so render (INFERRED, ưu tiên cao).

**Ambient occlusion (SSAO)**
- Tạo bóng mềm ở chỗ các vật giao nhau; chỉnh intensity/radius `[TbTvGzYP5N8 0:42]`.
- Tăng **power**, giảm **radius** thì có cạnh tối sắc giữa các block, rất đẹp cho nội thất `[UqoGPnNgcQ4 13:43]`.
- Chỉnh theo từng shot `[TbTvGzYP5N8 18:40]`.
- SSAO có tạo vệt trên mặt đất, "nhưng không có nó thì xấu, phải bật" `[Hj4a1avlL9o 21:11]`.

**Indirect lighting**
- Ánh sáng nảy, chỉnh strength. AnxiousCynic thử 400%, thấy khác biệt rất nhỏ `[Y0gQWA4rW0g 9:34]`.
- BeinBian "thường **tắt**" `[TbTvGzYP5N8 19:12]`.

**Reflections, PBR**
- Metallic và roughness `[TbTvGzYP5N8 1:45]`.
- BeinBian giảm roughness scenery và nhân vật (khoảng 90) cho thêm sắc độ `[TbTvGzYP5N8 16:25]`.
- Material map làm **mất subsurface**, nên anh tắt `[TbTvGzYP5N8 17:37]`.

**Anti-aliasing**
- "Lý tưởng khoảng 100" `[TbTvGzYP5N8 2:17]`. BeinBian "không bao giờ đụng" `[TbTvGzYP5N8 19:27]`.

**Light management dạng preset**
- Không có preset dùng mãi được, phải chỉnh theo từng dự án `[TbTvGzYP5N8 4:07]`.
- Nếu buộc phải có: **Exposure 2, Gamma 1** `[TbTvGzYP5N8 4:55]`.
- Quy trình riêng của anh: **ACES, Exposure 2, Gamma 2.2** `[TbTvGzYP5N8 12:28]`.
- Hai bộ số này mâu thuẫn nhau. Phải thử bằng render.

**Samples và shadow buffer**
- Mặc định 24 samples với buffer point/spot nhỏ thì có đường răng cưa. **75 samples với buffer very big/big** thì mượt và sạch hơn, nhưng thời gian render tăng rõ `[Y0gQWA4rW0g 11:24–13:14]`.
- Buffer spot/point **very big** sửa được bóng lạ trên mặt `[Q7H78ANxC94 12:12]`.
- Khi đang dựng thì để buffer nhỏ cho đỡ lag; lúc export thì trả về lớn `[EW0STx0lxKw 3:55]`.
- Template hiện tại (OBSERVED): `render_samples` 24, `render_shadows_sun_buffer_size` 2048, `render_shadows_spot_buffer_size` 512, `render_shadows_point_buffer_size` 256.

**Đồ họa "realistic" rất nặng**
- Samples cao rất tốn thời gian. A5Aw "chỉ khuyên dùng cho ảnh tĩnh" (mô tả, chương 7:15).

**Hậu kỳ trong MI**
- **Bloom:** đặt cực đoan trước (threshold thấp) rồi dịu dần; chủ yếu cho trời phát sáng; radius cao, intensity thấp, hơi pha xanh `[TbTvGzYP5N8 18:09]`.
- **Color burn** nhuộm màu, nhưng cẩn thận vì nó ảnh hưởng contrast `[TbTvGzYP5N8 19:27]`.
- **Vignette** để tạo điểm nhìn `[TbTvGzYP5N8 20:15]`.
- **Thử nhiều phiên bản grading:** keyframe camera với transition **instant** để A/B nhiều bản (gamma 1 so với khác) theo thời gian thực `[TbTvGzYP5N8 22:19]`.

**FPS**
- SharpWind khuyên 25 hoặc 30 `[xGsGfdu-2-Q 10:30]`. Pipeline mình đang 24 (OBSERVED, `build.py` `FPS=24`). Giữ 24 trừ khi owner quyết khác.

### 3.5 Particles (hạt) — AnxiousCynic Part 5

- **Tạo:** Workbench > Particle spawner > **presets** (snow, fire, ...) có xem trước `[uCPv8ce6dOI 0:00]`.
- **Particle editor:** mở qua Project properties > Library > particle spawner > "Open particle editor". Lỡ đóng cửa sổ thì mở lại từ Library `[uCPv8ce6dOI 0:46, 5:47]`.
- **Phải bấm Play mới thấy hạt.**
- **Spawn in region:** hộp vùng sinh, kéo lên cao cho tuyết rơi. Region còn có kiểu **path** `[uCPv8ce6dOI 1:01, 6:35]`.
- **Bounding box "ground":**
  - Destroy khi va chạm, khi hết animation, khi vượt số lượng (**mặc định 2000/phút**), hoặc sau một thời gian `[uCPv8ce6dOI 1:32]`.
  - **Bounce** 2 thì hạt nảy lên. Offset Z của box (15, 32 px) `[uCPv8ce6dOI 2:38–4:10]`.
- **Constant vs Burst:** burst ví dụ 1500 hạt bung ra một lần `[uCPv8ce6dOI 6:03]`.
- **Sprite:** template có sẵn (glitter, heart, ...) hoặc sprite sheet `[uCPv8ce6dOI 2:38, 7:40–9:45]`.
  - Frame start/end (ví dụ 128–135), frame size (32×32 cho explosion), animation speed (5 → 10 fps).
  - Một hệ có thể gồm nhiều sprite (smoke + fire).
- **Rotation:** sprite angle random 0–360. **Scale:** template 0.75 rồi đổi −0.375 theo thời gian; có thể cho lớn dần `[uCPv8ce6dOI 9:45–10:47]`.
- **Trajectory:** launch speed theo X/Y/Z (ví dụ X +50, Z +30, Y 0). Multiply/add force theo thời gian ra khói ống bị gió thổi `[uCPv8ce6dOI 10:47–12:42]`.
- **Color:** trắng → xám đậm, "mix color gradually" sang xanh; mix time 4 hoặc 2 `[uCPv8ce6dOI 12:58–13:44]`.
- **Orbit attractor:** keyframe được trên spawner, chọn object làm tâm hút, force khoảng 10 là mạnh `[uCPv8ce6dOI 14:01–15:35]`.
- **Keyframe điều khiển:** spawn particles / freeze simulation / clear particles. Ví dụ frame 80 clear, 150 spawn, 190 freeze ra hiệu ứng "bullet time" `[uCPv8ce6dOI 15:50–16:51]`.
- **Export/Import preset** (file preset trong thư mục particles) để dùng lại `[uCPv8ce6dOI 4:26–5:13]`.
- **Đom đóm không cần hệ hạt:** cube phát sáng tí hon (scale khoảng 0.9) rải tay `[Q7H78ANxC94 12:59–13:31]`.

**Hiệu ứng phép thuật rẻ:** enchantment glint trên item `[B9fFyYfRURw 0:40–1:50]`
- Appearance > Enchantment glint: texture, scale (5 thì thành mảng to), speed (10%–500%), strength. Tự động chuyển động.
- Có thể dùng cho hiệu ứng khác ngoài enchant.
- **Inherit pose** cho đám đông nhảy đồng bộ bằng 1 keyframe `[B9fFyYfRURw 1:55]`. Thuộc nhóm hoạt hình hơn là nhóm D.

### 3.6 Checklist có số

**A. Ngày ngoài trời** (ghép từ TbTv 2.0, Hj4a/EW0S 1.x)
- [ ] Render settings = **Custom** (TbTv, Y0gQ).
- [ ] Biome hợp cảnh (TbTv 12:28).
- [ ] Light management: **ACES**, **Exposure 2**, **Gamma 2.2** (TbTv 12:28). Phương án B: Exposure 2, Gamma 1 (TbTv 4:55).
- [ ] **Sunlight strength 200%** (TbTv 13:50). Màu nắng **hơi cam** (Hj4a 1:41).
- [ ] **Sunlight angle 0.4–0.5** (TbTv 14:35).
- [ ] **Ambient xanh đậm khử bão hòa** (Hj4a 2:12).
- [ ] Mặt trời làm key, thêm **1 spot fill mềm sát camera** (fade 100%, sharpness 0, khoảng 50% key) (EW0S 7:00, Hj4a 7:54).
- [ ] Nhân vật: **subsurface radius khoảng 1** cho rim (TbTv 14:20). Roughness khoảng 0.9 (TbTv 16:58).
- [ ] **Fog: distance cao, size lớn**, màu xanh nhạt; không để cảnh bị cắt cụt (Q7H7 5:44, TbTv 15:37).
- [ ] **SSAO on**, chỉnh theo shot. **Indirect off** (hoặc thử). AA mặc định.
- [ ] **Bloom nhẹ** cho trời: threshold thấp, radius cao, intensity thấp (TbTv 18:09).
- [ ] Color correction **contrast khoảng 3** (thang UI), vignette nhẹ (M0-5 16:13, TbTv 20:15).
- [ ] Final: **samples khoảng 75**, buffer **lớn** (Y0gQ 11:57).

**B. Đêm** (cả 3 video SharpWind đều nói "đừng dùng đêm mặc định của MI")
- [ ] **Giữ cài đặt ngày, đổi màu** (Q7H7 2:06).
  - **Sunlight = xanh đậm sáng / indigo khử bão hòa** (Q7H7 2:22, Hj4a 12:55, EW0S 7:49).
  - **Ambient gần đen, ánh xanh**, bão hòa hơn một chút (Hj4a 12:40, Q7H7 2:22).
- [ ] Trời đêm: sphere đảo mặt dán texture (của mình), clouds off, **fog on** với màu sáng hơn trời một chút (Hj4a 14:33).
- [ ] Vẫn phải **đọc rõ được mọi thứ**: thêm spot lớn mềm làm fill (fade 100%, radius lớn, sharpness 0) (Hj4a 15:22). Fill và back hơi xanh (EW0S 8:06).
- [ ] Contrast quá thấp thì YouTube nén xấu thêm (Q7H7 2:38). Cảnh tối phải có **rim/viền** quanh nhân vật (xGsG 10:00).

**C. Trong nhà ấm cúng** (UqoG 1.x + Y0gQ 2.0)
- [ ] **Sunlight color đen** (mặt trời không can thiệp) (UqoG 3:12). Hoặc dựng cảnh đêm như AnxiousCynic (Y0gQ 0:00).
- [ ] **Ambient xanh đậm** cho chiều tối, xanh nhạt hơn cho ban ngày (UqoG 3:29, 15:52).
- [ ] **Ánh sáng cửa sổ:** spotlight chiếu qua cửa sổ.
  - **Spot radius max, fade size 100%, sharpness 0** (UqoG 4:33).
  - Màu: xanh đậm cho chiều tối; thêm 1 bản gần trắng, range ngắn hơn.
  - **2–4 spot lệch nhẹ** cho bóng mềm (UqoG 6:22–7:53).
- [ ] **Đèn/đuốc:** point light đặt trong ngọn lửa, **cast shadows của khối = off** (UqoG 11:05, Y0gQ 1:34).
  - **Lớp ánh sáng:** cam đậm range **100**, cam sáng **72**, vàng **43**, trắng **14**; tăng fade size cho mượt (UqoG 12:37–13:10).
  - Hoặc 1 point màu cam vàng khớp texture, **size 2** (Y0gQ 2:07–2:52).
- [ ] **Fill:** point thứ hai, strength **khoảng 50%**, range vừa chạm nhân vật, ví dụ khoảng 80, fade cao (Y0gQ 4:54–6:27).
- [ ] Khối đèn: **emissive khoảng 125%**, **Glow on**; render glow + secondary glow (Y0gQ 1:01, 9:50).
- [ ] **SSAO power cao, radius thấp** (UqoG 13:43). Indirect tùy chọn (Y0gQ 9:34).
- [ ] Ấm trong nhà, lạnh ngoài cửa = tương phản màu (Q7H7 6:34).
- [ ] Dưới 4 đèn thì tốt; "càng ít đèn càng tốt" vì thời gian render (Y0gQ 7:32).

---

## 4. Áp dụng cho Bin & Bo

### 4.1 So với baseline `build.py` / `template.miproject` (OBSERVED → khuyến nghị)

| Mục | Hiện tại (OBSERVED) | Tutorial nói | Đề xuất (INFERRED, cần render thử) |
|---|---|---|---|
| Cắt cảnh | 1 camera, key cuối shot `instant` | Đúng cách AnxiousCynic khuyên `[rXslyG9nB-w 3:27]` | Giữ nguyên |
| FOV | 38–50 (wide 50/48, medium 42–44, CU 38) | 30–35 cho nhiều shot `[eMMrm 0:40]`; FOV hẹp và lùi máy `[xGsG 7:23]` | Wide 40–45, medium 32–35, OTS 30, CU 24–28 |
| Chuyển động | Mỗi shot có đẩy nhẹ (key đầu → key cuối gần hơn) | "Hiếm khi đứng yên" `[xGsG 4:47]`; move in = tò mò `[M0-5 12:01]` | Giữ; push-in 10–20% khoảng cách cho câu thoại quan trọng |
| DOF | Không có key `CAM_DOF` | DOF tinh tế cho medium/CU `[rXsly 9:47]` `[TbTv 12:58]` | Bật ở OTS/CU, blur thấp |
| `render_settings` | "performance" | Mọi người chuyển sang Custom | **Đổi "custom" rồi so render** (ưu tiên) |
| `render_samples` | 24 | 75 cho bản cuối `[Y0gQ 11:57]` | Nháp 24, final 64–75; **thời gian render chưa đo** trên RTX 3060 |
| Shadow buffer spot/point | 512/256 | big/very big `[Y0gQ 11:41]` `[Q7H7 12:12]` | Tăng khi có spot/point |
| Tone mapper / exposure / gamma | 0 / 1 / 2.2 | ACES + exposure 2 `[TbTv 12:28]` | Thử ACES (2?) + exposure 1.3–2 (A/B) |
| Sunlight | strength 1, angle 0.526, màu #FFF7E4 | 200%, angle 0.4–0.5, hơi cam | strength 1.6–2, angle 0.45, màu kem ấm |
| Ambient | #66708C (xanh xám) | Xanh đậm khử bão hòa | Giữ hoặc #5C6688 |
| Fog | show, distance 10000, size 2000 | Distance cao, size lớn | Giữ; thử size 4000 nếu cảnh có chiều sâu |
| Subsurface nhân vật | chưa đặt `SUBSURFACE` (INFERRED: mặc định 0) | radius khoảng 1 cho rim `[TbTv 14:20]` | Đặt khoảng 1 cho Bin/Bo/Zu; **render_subsurface_samples** > 0 (Meisner: 1 cho viền mảnh) |
| Glow | `render_glow` true | OK | Giữ |
| FPS | 24 | 25/30 `[xGsG 10:30]` | Giữ 24 cho tới khi owner quyết |

### 4.2 Shot list mẫu cho tập thoại 1–3 phút

**Hệ trục giả định (INFERRED)**
- Bin đứng ở (0,0); Bo ở (48,0), cách nhau 3 block, nhìn nhau theo trục X. Zu (scale 0.6) ở (24,-20).
- Mặt đất z=0, mắt nhân vật lớn khoảng z 27 (`build.py` cũng nhắm z 27 cho mặt Bin), mắt Zu khoảng z 17.
- **Đường hành động (line of action) = trục X.** **Mọi camera đặt bên y<0** (quy tắc 180°, INFERRED): Bin luôn ở bên trái màn hình, Bo bên phải.
- Hướng quay của nhân vật dùng ROT_Z theo quy ước đã đo trong `build.py`. Comment code ghi "characters use the opposite" so với camera, nên **kiểm tra lại dấu** trước khi viết.

**Cách tính hướng camera**
- Camera tính bằng hàm `look()` có sẵn trong `build.py`: ROT_Z = atan2(dx,dy), ROT_X = −atan2(dz, ngang).
- Hướng nhìn theo (sin t, cos t) với ROT_Z = t; +ROT_X thì nhìn xuống.
- Cột "cao khung" = 2·d·tan(FOV/2), **giả định CAM_FOV là FOV dọc** (INFERRED, chưa kiểm chứng; kiểm bằng 1 render thử).

| Shot | Dùng khi | POS_X | POS_Y | POS_Z | ROT_X | ROT_Z | CAM_FOV | Khoảng cách | Cao khung | Độ dài (INFERRED) |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 WIDE establishing | Mở cảnh hoặc đổi địa điểm `[xGsG 2:08]` | 24 | -170 | 44 | 8.0 | 0.0 | 45 | 172 | 142 (khoảng 9 block) | 3–5 s, push-in nhẹ |
| S2 MEDIUM two-shot (cắt gối) | Hành động, cả hai nói qua lại `[M0-5 6:13]` | 24 | -95 | 30 | 4.8 | 0.0 | 35 | 95 | 60 | 3–6 s |
| S3 OTS → Bin (sau vai Bo) | Bin nói; giữ trục | 62 | -16 | 31 | 3.6 | -75.5 | 30 | 64 | 34 | theo câu thoại, 2–5 s |
| S4 OTS → Bo (sau vai Bin) | Bo nói (shot ngược) | -14 | -16 | 31 | 3.6 | 75.5 | 30 | 64 | 34 | theo câu thoại, 2–5 s |
| S5 CU Bin 3/4 trước | Cảm xúc, phản ứng `[xGsG 2:40]` | 28 | -28 | 27 | 0.0 | -45.0 | 26 | 40 | 18 (đầu+vai) | 1.5–3 s |
| S6 CU Bo 3/4 trước | Phản ứng Bo | 20 | -28 | 27 | 0.0 | 45.0 | 26 | 40 | 18 | 1.5–3 s |
| S7 CU Zu ngang mắt Zu | Zu nói hoặc phản ứng. **Ngang mắt** để Zu không "nhỏ bé, đáng xấu hổ" `[M0-5 7:16]` | 24 | -58 | 17 | 0.0 | 0.0 | 28 | 38 | 19 | 1.5–3 s |
| S8 PUSH-IN kết thúc S5 | Câu thoại "điểm nhấn": key đầu = S5, key cuối = dưới | 22 | -22 | 27 | 0.0 | -45.0 | 26 | 31 | 14 | 2–3 s, `easeinoutsine` |
| S9 LOW-ANGLE hero Bin | Khoảnh khắc chiến thắng hoặc tự tin `[xGsG 3:44]` | 14 | -34 | 12 | -20.8 | -22.4 | 32 | 39 | 22 | 1.5–2.5 s |
| S10 DETAIL insert | Đồ vật hoặc manh mối quan trọng | tùy vật | | | | | 20–24 | 20–30 | | **1–2 s** `[xGsG 2:55]`, ≤ 2 lần/tập |

Toàn bộ số trong bảng là **INFERRED**, tính bằng `look()` ở hệ trục giả định trên. Chỉ áp các cỡ shot, ý nghĩa góc máy và độ dài detail là có dẫn nguồn.

**Nhịp cắt cho tập 1–3 phút (INFERRED, transcript không đưa số)**
- **0–5 s:** S1 (hoặc S2 nếu đã biết bối cảnh), push-in nhẹ.
- **Thoại:** luân phiên S3/S4 theo người nói. **Cắt ngay đầu câu thoại mới** (hoặc 4–6 frame trước, để nghe người nói trước khi thấy). Chèn S5/S6 cho câu cảm xúc, S7 khi Zu phản ứng.
- **Mỗi 20–30 s:** quay lại S2 để "thở" và nhắc vị trí không gian.
- **Cao trào:** S8 (push-in) hoặc S9 (góc thấp).
- **Kết:** S1 lùi nhẹ (move out). Không dùng move out "rợn" cho cảnh vui; chỉ lùi chậm, ánh sáng ấm.
- **Độ dài shot trung bình khoảng 2.5–4 s.** Baseline `build.py` là 1.8–4.3 s (55–102 frame ở 24 fps), mình giữ dải này.

**Tránh với kênh kids/family (INFERRED, từ M0-5/xGsG)**
- Dutch tilt nghiêng động.
- Move out + tilt (kiểu horror).
- Frog's view cho nhân vật xấu đáng sợ.
- Vignette đỏ.
- Nếu dùng dolly-zoom thì chỉ cho khoảnh khắc "wow" hài hước, ≤ 1 lần/tập.

**Rung máy nhẹ cho va chạm hoặc nhảy**
- `CAM_SHAKE` true, `CAM_SHAKE_MODE` = rotational (tác giả thích rotational `[eMMrm 6:12]`; giá trị enum chưa kiểm).
- Bật/tắt bằng keyframe trong 6–10 frame. Strength nhỏ (thử 0.2–0.4) (INFERRED).

**Mẫu keyframe một cú cắt (ghi vào `.miproject`)**
```
"<f_start_S3>": {"POS_X":62,"POS_Y":-16,"POS_Z":31,"ROT_X":3.6,"ROT_Z":-75.5,"CAM_FOV":30,"TRANSITION":"easeinoutsine"},
"<f_end_S3>":   {"POS_X":60,"POS_Y":-14,"POS_Z":31,"ROT_X":3.6,"ROT_Z":-75.5,"CAM_FOV":30,"TRANSITION":"instant"},
"<f_start_S4>": {"POS_X":-14,"POS_Y":-16,"POS_Z":31,"ROT_X":3.6,"ROT_Z":75.5,"CAM_FOV":30,"TRANSITION":"easeinoutsine"}
```

**Nhắc lại các quy ước file**
- OBSERVED: keyframe chỉ lưu giá trị khác mặc định. `build.py` đã carry state qua `K()`.
- DOF (tùy chọn) ở OTS/CU, tất cả là INFERRED: `"CAM_DOF":true,"CAM_DOF_DEPTH":<khoảng cách tới mắt nhân vật nói, ví dụ 64>,"CAM_DOF_RANGE":40,"CAM_DOF_FADE_SIZE":100`. `CAM_DOF_BLUR_SIZE` để thấp. Do mọi trường camera lưu theo keyframe, **phải lặp lại DOF ở cả key đầu và key cuối shot** `[rXsly 7:43]`.

### 4.3 Công thức ánh sáng A: ngoài trời ban ngày thân thiện

Ghi vào `background` / `render` / camera. Mọi giá trị là **INFERRED** từ mục 3.6A; thang đo đánh dấu "?" chưa kiểm.
```
project.render_settings: "custom"                      # thử; template đang "performance"
background:
  sunlight_strength: 1.8          # ~180% (TbTv dùng 200%; thang 1=100%?)
  sunlight_angle: 0.45            # bóng hơi mềm (TbTv 0.4–0.5)
  sunlight_color: "#FFEBD0"       # kem/cam nhẹ (Hj4a: hơi cam)
  ambient_color: "#5C6688"        # xanh khử bão hòa = màu bóng
  sky_color: "#86B4FF"            # trời sáng hơn một chút cho bloom
  fog_show: true; fog_sky: true; fog_color_custom: true; fog_color: "#BFD6FF"
  fog_distance: 10000; fog_size: 4000      # xa và rất dần (Q7H7)
  sky_clouds_show: true
  sky_time: <xoay sao cho nắng chéo 45° từ trước-bên camera>   # cần thử; tutorial không cho số
render:
  render_samples: 24 (nháp) / 64–75 (final)
  render_ssao: true; render_ssao_radius: 12; render_ssao_power: 1   # chỉnh theo shot
  render_shadows: true; render_shadows_sun_buffer_size: 4096 (final)
  render_indirect: false
  render_glow: true
  render_subsurface_samples: 8?   # rim mềm; Meisner: 1 cho viền mảnh, >64 vô ích
  render_subsurface_highlight: true?/strength ~0.1?   # ThoqriMC 10 (thang UI)
  tonemapper: 2? (ACES)  exposure: 1.3–2  gamma: 2.2      # A/B bằng keyframe camera instant (TbTv 22:19)
nhân vật (body parts): SUBSURFACE ~1 (radius R/G/B ~1), ROUGHNESS ~0.9
camera (mỗi key):  CAM_COLOR_CORRECTION true, CAM_CONTRAST ~0.03?, CAM_SATURATION 1.05,
                   CAM_BLOOM true, CAM_BLOOM_THRESHOLD ~0.75, CAM_BLOOM_INTENSITY ~0.25, CAM_BLOOM_RADIUS ~1.5,
                   CAM_VIGNETTE true, CAM_VIGNETTE_STRENGTH ~0.3, CAM_VIGNETTE_SOFTNESS 0.5
đèn bổ sung: 1 spotlight FILL gần camera chính:
  LIGHT_COLOR "#DDE6FF", LIGHT_STRENGTH 0.5, LIGHT_SPOT_RADIUS 80, LIGHT_SPOT_SHARPNESS 0,
  LIGHT_FADE_SIZE 1.0, LIGHT_RANGE 300, render shadows off (tránh bóng kép)
```

### 4.4 Công thức ánh sáng B: phòng ấm cúng buổi tối

Mọi giá trị là **INFERRED** từ mục 3.6C.
```
background:
  sunlight_color: "#000000"  (hoặc sunlight_strength 0)   # UqoG 3:12
  ambient_color: "#2A3352"   # xanh đậm = bóng chiều tối (UqoG 3:29)
  fog_show: false (trong nhà) hoặc giữ xa
đèn cửa sổ (2 spotlight lệch ~8 đơn vị, chiếu xiên qua cửa sổ vào sàn):
  LIGHT_COLOR "#6F86C8" (xanh tối) + bản thứ hai "#E8EEFF" range ngắn hơn
  LIGHT_STRENGTH 0.4 mỗi cái, LIGHT_SPOT_RADIUS 85, LIGHT_SPOT_SHARPNESS 0, LIGHT_FADE_SIZE 1.0, LIGHT_SIZE 4
đèn bàn / lò sưởi (point lights cùng tâm trong ngọn lửa; khối đèn: shadows off, EMISSIVE ~1.25, Glow on):
  lớp 1  LIGHT_COLOR "#C2561A"  LIGHT_RANGE 100  LIGHT_STRENGTH 0.8
  lớp 2  LIGHT_COLOR "#F08A2E"  LIGHT_RANGE 72   LIGHT_STRENGTH 0.6
  lớp 3  LIGHT_COLOR "#FFC860"  LIGHT_RANGE 43   LIGHT_STRENGTH 0.5
  lớp 4  LIGHT_COLOR "#FFF4E0"  LIGHT_RANGE 14   LIGHT_STRENGTH 0.4
  LIGHT_SIZE 2, LIGHT_FADE_SIZE ~0.8                       # range theo UqoG 12:37; strength là của mình
fill mặt: 1 point "#FFD9A8", LIGHT_STRENGTH 0.5, LIGHT_RANGE 80, LIGHT_FADE_SIZE 0.9, shadows off  (Y0gQ 4:54–6:27)
render: SSAO power cao (1.5–2), radius thấp (6–8) cho cạnh block sắc (UqoG 13:43); glow + secondary glow;
        samples 64–75 final; spot/point buffer lớn (1024/512+)
nhân vật: SUBSURFACE ~1 (rim ấm phía đèn, xanh phía cửa sổ = tương phản màu, Q7H7 6:02)
camera: ACES?, exposure ~1.2–1.5, vignette nhẹ; KHÔNG bloom mạnh (dễ chói)
giới hạn: ≤ 6–7 đèn tổng (Y0gQ 7:32 khuyên ít đèn vì thời gian render)
```

### 4.5 Việc cần đo trước khi tin công thức

Chưa đo cái nào. Mỗi mục làm 1 render 1 frame trên máy CINE.
1. `render_settings` "performance" và "custom": các giá trị trong khối `render` có được áp không?
2. `CAM_FOV` là FOV dọc hay ngang: đặt 1 block 16 đơn vị ở khoảng cách đã biết rồi đo.
3. Giá trị enum `tonemapper`/`CAM_TONEMAPPER` (0/1/2) và `CAM_SHAKE_MODE`.
4. Thang lưu của sunlight_strength (1 = 100%?), contrast, glow radius, subsurface highlight.
5. Thời gian render 75 samples so với 24 samples, 1080p, trên RTX 3060 (ghi vào `data/production_ledger.jsonl`).
6. Subsurface 1 có thực sự cho rim trên skin 64×64 của Bin/Bo không, khi ánh sáng từ sau lưng.
