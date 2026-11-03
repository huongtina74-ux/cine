# CẨM NANG MINE-IMATOR cho kênh Bin, Bo & Zu

Ngày soạn: 2026-11-03. Người soạn: Claude (subagent). Người đọc: owner.
Phần mềm: Mine-imator 2.0.2 Full, trên PC Windows có RTX 3060. Kênh kể chuyện gốc cho trẻ em và gia đình.

**Nguồn.** Cẩm nang này gộp từ 5 sổ học trong thư mục này:
- A: giao diện và quy trình
- B: chuyển động cơ thể
- C: khuôn mặt, cảm xúc, lời thoại
- D: máy quay, ánh sáng, render
- E: khóa học Hindi classToon và greenscreen

Các sổ được viết từ transcript đầy đủ của khoảng 80 video. Cẩm nang cũng đối chiếu với code của mình ở `tools/mineimator/binbo_thu02/`, gồm `build.py`, `faces.py`, `prep.py`, `tts.py`, `mix.py`, `skins.py` và `template.miproject`.

**Quy ước nhãn**
- `[videoId mm:ss]`: dẫn nguồn, giữ nguyên từ sổ học. Mốc thời gian có thể lệch ±15–20 s. Phụ đề là ASR nên có thể nghe sai.
- Câu có dẫn nguồn là **OBSERVED**, tức video nói hoặc làm như vậy. Câu ghi "(OBSERVED code)" là điều mình thấy trực tiếp trong file của repo.
- **(INFERRED)**: suy luận, video không nói.
- **(CHƯA ĐO)**: phải render thử trên máy CINE mới được tin.
- **(OWNER)**: owner đã nói.

**Lưu ý phiên bản.** Một số video của SharpWind, cùng Q7H7, Hj4a, EW0S, UqoG và x_j0, có vẻ quay trên bản 1.x. Nguyên lý vẫn dùng được, nhưng **đừng chép số** của các video này vào 2.0.2 khi chưa thử (sổ A và D, phần đầu).

---

## 1. TL;DR: 12 quy tắc quan trọng nhất

1. **Khóa project trước khi làm.** Tempo phải bằng FPS xuất; pipeline đang dùng 24 (OBSERVED code). Độ phân giải 1920×1080. Nếu tempo lệch FPS xuất, cú cắt "instant" sẽ lộ một frame thừa. [PHTPcUdK84I 13:03] [Vn0zjTO4dWY 2:05]
2. **Đặt key gốc ở frame 0 cho mọi part, và đặt key giữ trước mỗi động tác.** Thiếu key giữ thì nội suy chạy ngay từ frame 0. Đây là "lỗi kinh điển" của người mới. [BNE7CsRE79o 2:23] [w3HKHvnhSiI 4:27]
3. **Không để nhân vật đứng im dù chỉ một frame.** Cho thở hoặc lắc rất nhẹ, khoảng 20 tick một key, dùng ease in/out. [aMTNQBzSGA8 1:36] [QRwM5E7NVaA 5:37]
4. **Cử chỉ dùng ease in/out, không dùng linear.** Key mới thừa hưởng transition của key trước, nên phải kiểm lại. Riêng chân trong walk cycle thì để linear. [BNE7CsRE79o 9:03] [2Klmj7x8IvI 6:12] [NU0fAvOgEv0 13:09]
5. **Overlap theo thứ tự thân → đầu → tay.** Thân đi trước, đầu trễ hơn, tay trễ nhất. Đừng đặt key đầu cùng frame với key thân. [IyUfooxLmGE 6:53] [QRwM5E7NVaA 5:07]
6. **Khi nhìn hoặc quay về phía ai, mắt và đầu dẫn trước, thân theo sau.** Tới nơi thì cho lùi lại một chút (settle). [aMTNQBzSGA8 3:13, 6:02]
7. **Chống trượt chân.** Chân và quãng di chuyển phải cùng linear (hoặc cùng ease). Sải chân phải khớp quãng đường root đi được. [BmWf6dR4kks 3:22] [w3HKHvnhSiI 30:40]
8. **Mặt dựng bằng skin không mặt cộng các bộ phận mặt riêng.** Các bộ phận parent vào head, đặt lệch khoảng +0.01 trước mặt đầu để tránh z-fight, và tắt cast shadows. [puXk5_aVtvY 2:10] [kaw2sRFgdjg 1:06] [QMqEW2Vqa10 12:31]
9. **Lip-sync:**
   - đặt key ở chỗ nguyên âm nghe rõ nhất, độ mở miệng theo âm lượng;
   - hai âm mở liền nhau thì không khép miệng ở giữa;
   - chớp mắt ngay trước khi nói.
   [jGvOjgVfN_A 3:19, 10:37, 12:15] [QRwM5E7NVaA 7:21]
10. **Cắt cảnh bằng 1 camera, key cuối mỗi shot đặt Instant.** Camera hiếm khi đứng yên hẳn. [rXslyG9nB-w 3:27] [xGsGfdu-2-Q 4:47]
11. **Không dùng ánh sáng mặc định.** Tối thiểu có key và fill: mặt trời cộng 1 spot fill là đủ. Nắng hơi cam, ambient xanh khử bão hòa. [Y0gQWA4rW0g 3:23] [EW0STx0lxKw 7:00] [Hj4a1avlL9o 1:41, 2:12]
12. **Render:** chọn Custom, samples khoảng 75 (50–100 là đủ), xuất PNG sequence cho video dài, và Ctrl+S thường xuyên vì app có crash. [a91bOwulnw8 1:03, 13:46] [nOz-trT5m9U 11:42] [eMMrm-tL7mc 2:56]

---

## 2. Quy trình một tập phim, từ đầu đến cuối

Ở pipeline CINE, **Python viết `.miproject`**, còn Mine-imator chỉ để soát và render (OBSERVED code, README). Mỗi bước dưới đây ghi cả cách làm GUI lẫn phần code đã lo.

### 2.1 Setup (làm một lần, lưu thành project mẫu)
- [ ] Dùng bản Full 2.0.2 hợp lệ (OWNER). Chưa upgrade thì không tắt được watermark. [a91bOwulnw8 15:09] [z7n9RRn_Po8 1:12–1:52]
- [ ] **Edit > Preferences:**
  - bỏ tick "Copy work camera into new cameras" [JBIn_WC4jSY ~3:00];
  - nếu menu Transitions tràn ra ngoài màn hình thì tắt *Compact panels* [JBIn_WC4jSY 12:49];
  - bật *Compact timeline lists* khi có nhiều nhân vật [QNeOpaw6K9I 27:19–35:45].
- [ ] Lựa chọn **"Z is up"** quyết định ý nghĩa X/Y/Z trong từng video [Vn0zjTO4dWY 8:42]. Trong file, `build.py` dùng POS_Z làm chiều cao (OBSERVED code).
- [ ] **Project properties:**
  - Tempo **24**: classToon khuyên 24 vì 30 bắt đầu lag [QNeOpaw6K9I 14:09]; SharpWind khuyên 25/30 [xGsGfdu-2-Q 10:30]. Giữ 24 cho tới khi owner quyết khác.
  - Size 1920×1080. Code đã đặt `tempo=24`, `video_width/height` (OBSERVED code).
- [ ] Lúc animate: viewport để Flat/Shaded và tắt particles. Chỉ bật Rendered khi chỉnh ánh sáng. [Vn0zjTO4dWY 5:14]
- [ ] Lưu một **project mẫu cho cả series** gồm set, ánh sáng, camera, render preset. [2Klmj7x8IvI 4:49–5:56] (INFERRED: `template.miproject` chính là chỗ này.)
- [ ] Bấm **Ctrl+S** sau mỗi thao tác lớn. Tác giả bị crash 2 lần khi chỉnh hiệu ứng camera. [a91bOwulnw8 5:32] [eMMrm-tL7mc 2:56, 10:38]

### 2.2 Bối cảnh
- [ ] **Cách 1, tự dựng trong Mine-imator:** *Workbench → Block*, rồi vào Library đặt **Repeat X/Y/Z** để lát tường và sàn. [pjrAmdnpffA 8:36–9:39]
  - Bật snap **16** (1 block = 16 đơn vị) để block khít nhau. [nOz-trT5m9U 4:09] [mU4aMjfMqTs 9:56–15:52]
- [ ] **Cách 2, import world do mình tự xây** trong Minecraft Java:
  - Vào game, đứng sẵn ở chỗ cần lấy, vì importer mở đúng vị trí người chơi. [06Rt_KB-oh4 1:09–3:26]
  - World phải đúng phiên bản Mine-imator hỗ trợ; nếu không, world mở ra trống trơn. [pjrAmdnpffA 0:20–1:02]
  - World Bedrock phải convert sang Java trước. [pjrAmdnpffA 6:55]
- [ ] Khi có popup "N blocks can be animated":
  - chọn **No** nếu không cần mở cửa hay rương, cho project nhẹ;
  - chọn **Yes** nếu cảnh cần mở cửa.
  [pjrAmdnpffA 2:25–3:50] [nOz-trT5m9U 3:48]
- [ ] Dùng **Block filter → Remove** để bỏ cỏ cao hoặc đuốc tường. [pjrAmdnpffA 5:11–6:35] [06Rt_KB-oh4 3:26–5:36]
- [ ] Sau khi tạo, đưa vị trí về 0. Scenery là **một model** nên không sửa được từng block. Muốn xóa hẳn thì xóa ở cả **Library lẫn Resources**. [pjrAmdnpffA 2:46, 3:50, 4:30]
- [ ] Đừng để lộ mép schematic: xoay camera hoặc đặt prop che. [G4KSYcJmdk8 3:30]
- [ ] **Environment:**
  - tắt ground khi đã có scenery [QhMY2ac0nOk 2:06];
  - fog để distance cao, size lớn, đừng để thế giới trông bị "cắt cụt" [Q7H78ANxC94 5:44] [TbTvGzYP5N8 15:37];
  - gió vừa đủ cho cỏ lá đung đưa [06Rt_KB-oh4 13:28];
  - chọn biome theo mood [TbTvGzYP5N8 21:19].
- [ ] **Xoay mặt trời** sao cho bóng đẹp đúng chỗ nhân vật sẽ đứng. [06Rt_KB-oh4 13:28]

### 2.3 Nhân vật và khuôn mặt
- [ ] **Skin gốc tự vẽ.** `skins.py` tạo skin 64×64 cho Bin, Bo, Zu; `prep.py` xóa mắt và miệng thành **skin không mặt** (OBSERVED code). Video yêu cầu skin "không có mặt" cho mọi kiểu face rig. [puXk5_aVtvY 2:10] [eSVLFPCLBZk 5:17]
- [ ] **Face rig 4 lớp:** eyes, pupils, brows, mouth là 4 surface có texture, parent vào `head`. Mỗi lớp là một kênh keyframe riêng nên cảm xúc và lip-sync cộng dồn được, không phải nhân bản skin. (OBSERVED code; phương pháp D [Un_RU3KwleY 3:33–5:00] [OGLkFs2mXtg 1:11])
  - Khoảng cách trước tâm đầu: eyes 4.02, mouth 4.025, pupils 4.035, brows 4.045 (OBSERVED code). Video dùng 4.01. [kaw2sRFgdjg 1:06–1:17]
  - `shadows=False`, `ssao=False` trên các lớp mặt, đúng như [QMqEW2Vqa10 12:31] (OBSERVED code).
  - Texture: PNG 32×32 tự vẽ trong `faces.py`, phủ toàn mặt trước 8×8 (OBSERVED code). Có 8 trạng thái mắt, 3 cỡ con ngươi, 6 kiểu mày, 13 khẩu hình.
- [ ] Chi tiết **lông mày không được scale khi chớp mắt.** Rig của video phải tắt inherit scale [kaw2sRFgdjg 8:06]. Rig của mình chớp bằng đổi texture nên không gặp lỗi này (INFERRED).
- [ ] Zu đang scale 0.6, đầu 1.25 (OBSERVED code). Các lớp mặt là con của head nên scale theo, khỏi bù tay (INFERRED; video cảnh báo rig A phải bù tay [puXk5_aVtvY 8:28]).
- [ ] **Bảng cảm xúc rút gọn** [BbcV5uGm0jM] [0OuknDnKE-E]. Luật chung: con ngươi **co lại** khi có cảm xúc tiêu cực [BbcV5uGm0jM 4:53–5:57]; "chỉ cười bằng miệng thì trông kỳ", mắt và mày cũng phải phản ứng [0OuknDnKE-E 0:47].

| Cảm xúc | Mày | Mắt / con ngươi | Miệng | Thân |
|---|---|---|---|---|
| Vui | nâng lên | mở, con ngươi to | cười | thẳng, tay mở |
| Buồn | đầu trong nâng, cả mày thấp | nhìn xuống | hơi xuống | cúi, khép, quay đi |
| Giận | kéo vào giữa và xuống | nheo, con ngươi chạm mép trên | khép, cong xuống | cúi, khoanh tay |
| Sợ | rất cao | mở to, con ngươi co nhỏ | tròn, mở | ngả ra xa, đầu vẫn nhìn vật đáng sợ |
| Ngạc nhiên | nâng | mở to | mở "whoa" | chân dang, tay giơ |
| Nghĩ | gần thẳng | con ngươi nhìn xa | khép hoặc hé | thả lỏng |
| Tò mò | một bên vào, một bên nâng | nhìn điểm quan tâm | — | nghiêng tới |

- [ ] **Không sửa rig gốc.** Sửa trên bản copy qua *Import asset*. [G4KSYcJmdk8 0:25]
- [ ] Nếu hai chân bị z-fighting, scale cả hai chân 0.999 mọi trục. [TcNSoStA0Js 8:31]

### 2.4 Blocking (pose-to-pose)
- [ ] **Tự diễn động tác** trước khi animate. [TcNSoStA0Js 7:48] [QRwM5E7NVaA 13:29]
- [ ] **Thoại trước, hình sau.** Code đặt `START` của từng câu theo độ dài wav (OBSERVED code).
- [ ] **Key gốc và key giữ:**
  - GUI: chọn mọi part rồi bấm **Ctrl+Q** (hoặc tick/untick Visible) [BNE7CsRE79o 1:01–1:42] [NU0fAvOgEv0 1:04].
  - Code: hàm `K()` cùng `flush()` mang state từ key trước sang (OBSERVED code).
- [ ] **Timing là khoảng cách giữa hai key.** Ở 24 fps, 24 frame = 1 s. [BNE7CsRE79o 3:46] [w3HKHvnhSiI 1:31]
- [ ] **Bẫy GUI:** nếu đang chọn một key thì chỉnh sửa sẽ ghi vào key đó. Bỏ chọn trước khi chỉnh. [NU0fAvOgEv0 2:22] [0N4zaeMgQvA 17:35]
- [ ] **Walk 4 pose** [NU0fAvOgEv0 7:57–17:07]:
  - các pose: contact → passing (gập gối chân đang đưa) → contact ngược → passing;
  - thân twist **±5°**, đầu dip **±4°**;
  - bob: **−1** ở contact, **0** ở passing;
  - chân để linear, tay để ease.
  - Code thu02 hiện chỉ có chân/tay **±16° mỗi 6 frame** và thân **±3°** (OBSERVED code). Chưa có pose passing, chưa có bob và dip đầu.
- [ ] **Sải chân xấp xỉ 2·12·sin(a)** (INFERRED, sổ B 3.3). ±16° cho khoảng 6.6 đơn vị mỗi 6 frame. Bin đi 120→35 trong 72 frame, khoảng 7.1 đơn vị mỗi 6 frame (INFERRED). Hai số này gần khớp nhau, nhưng phải đo bằng contact sheet.
- [ ] **Quay tại chỗ 90°:** mất 20–22 tick. Thân và chân trụ phải cùng transition, cùng frame. Bàn chân trụ xoay ngược để đứng yên trên đất. [M-upI7h19kw 7:22–10:01]
- [ ] **Dừng có settle:** hạ người, gập gối, ease out. "Thà lún nhẹ còn hơn trượt." [VdJh-vTewJY 16:48–17:20]
- [ ] **Nhảy:** có anticipation (hạ người trước). Lên dùng ease out, xuống dùng ease in, đặt trên một folder hoặc timeline riêng; trục ngang để linear. [DO3d7Rh3e0E 1:49, 6:32] [I1CGhhEcOc4 1:22–2:55]
  - Code: Zu nhảy dùng `easeoutquad` khi lên, `easeinquad` khi xuống (OBSERVED code).
- [ ] **Đưa hoặc nhận đồ:** dùng hai bản item, một bản parent vào tay. Đổi **Visible trong cùng một frame**. [Vjcc_vau-u8 0:49–2:40] [mU4aMjfMqTs 16:05–25:30]
- [ ] Cảnh khó làm sạch chân thì **giấu chân bằng khung hình**. [M-upI7h19kw 12:09]

### 2.5 Splining (làm mượt)
- [ ] **Chọn transition:**
  - ease in/out là mặc định;
  - `easeinoutcubic` cho động tác "có lực" [VdJh-vTewJY 11:40];
  - sine cho cảm giác thư thái [aMTNQBzSGA8 6:18];
  - Instant cho cắt cảnh và đổi texture [BNE7CsRE79o 6:17].
- [ ] Easing theo vật lý: vật **rơi** dùng ease in, vật **bật lên** dùng ease out. [0ZBmiugjgLg 4:29]
- [ ] **Mức overlap:**
  - cử chỉ: tay và đầu trễ **1–2 frame** so với thân [4e_xp4QTAUU 11:29];
  - idle: đầu trễ khoảng **10 frame** [aMTNQBzSGA8 2:22];
  - khi chạy: tay chỉ trễ 1 tick [BmWf6dR4kks 14:15].
- [ ] **Follow-through:** sau va chạm, vật còn trôi thêm một chút. [4e_xp4QTAUU 13:35]
- [ ] **Xem lại:** tạo vùng loop (chuột phải + kéo trên thước timeline, rồi bật Repeat). Luôn play lại từ frame 0. [BNE7CsRE79o 11:28] [2Klmj7x8IvI 2:26]
- [ ] **Beat hành động hài của Zu** có thể làm kiểu stop-motion: key mỗi 3–4 frame, tất cả Instant. [ieV5yGq7-hI 2:31–3:13] (INFERRED: không dùng cho thoại dài.)
- [ ] **Hai nguồn mâu thuẫn về curve tùy biến:** bản 2.0 có **Bezier transition** [JBIn_WC4jSY 12:49], còn SharpWind (có lẽ trên 1.x) nói không có custom curve [I1CGhhEcOc4 12:16]. Ưu tiên nguồn quay trên 2.0.

### 2.6 Hội thoại và lip-sync
- [ ] **Thứ tự làm:** thân → đầu → mặt → tay → chân. [QRwM5E7NVaA 1:09]
- [ ] **Audio:**
  - Trong GUI có thể import audio để thấy waveform [jGvOjgVfN_A 1:40–2:54].
  - Pipeline của mình: `tts.py` (Kokoro, Apache-2.0) ghi wav và **envelope RMS mỗi frame ở 24 fps** (OBSERVED code).
- [ ] **Key miệng:**
  - ở đỉnh nguyên âm [jGvOjgVfN_A 3:19];
  - âm nhỏ thì mở nhỏ [10:37, 12:04];
  - hai âm mở liền nhau thì không khép [12:15];
  - im lặng thì khép [6:16].
  - Code: cứ **3 frame** lấy max envelope, chia mức theo ngưỡng **0.12 / 0.38 / 0.70** của đỉnh câu thành 4 mức (đóng, 1, 2, 3). Họ khẩu hình theo cảm xúc: open, grin, wail. Chỉ ghi key khi khẩu hình đổi (OBSERVED code).
- [ ] **Đổi texture miệng thì dùng Instant.** [Un_RU3KwleY 4:36–5:00] Code đặt mọi key lớp mặt là `instant` (OBSERVED code).
- [ ] **Chớp mắt:**
  - một lần trước mỗi câu [QRwM5E7NVaA 7:21];
  - thêm khoảng mỗi 64 frame ±10/14;
  - mỗi lần chớp đi qua half → closed → half → mở trong 4 frame (OBSERVED code).
- [ ] **Người nói:**
  - đầu không bao giờ đứng yên [QRwM5E7NVaA 5:37];
  - giữa hai cụm thoại có chuyển động lấp [2:53];
  - từ nhấn: anticipation, rồi cú chính ease-in, rồi key hãm ease-out [3:12–4:15];
  - tay đi vòng cung nhờ key giữa [11:14].
- [ ] **Người nghe:** không video nào dạy riêng. Đề xuất (INFERRED, sổ C 4.5): nhìn người nói, trễ 4–6 frame; gật nhẹ ở cuối cụm câu; phản ứng cảm xúc 6–10 frame sau từ khóa.
- [ ] **Chi phí làm tay:** 6 s thoại mất hơn 1 giờ [QRwM5E7NVaA 18:04]; 5 s lip-sync mất 1.5 giờ [jGvOjgVfN_A 17:18]. Đây là lý do code hóa phần này (INFERRED).

### 2.7 Máy quay
- [ ] **Một camera cho cả tập.** Key đầu shot dùng ease, key cuối shot dùng **Instant**. Không đặt Instant thì máy "bay xuyên cảnh", kể cả khi hai key chỉ cách 1 frame. [rXslyG9nB-w 2:39–4:47]
  - Code: 6 shot, key đầu `easeinoutsine`, key cuối `instant`, mỗi shot push-in nhẹ (OBSERVED code). Pytest yêu cầu ít nhất 5 cú cắt.
- [ ] **Mọi thông số camera lưu theo keyframe.** Bật DOF thì phải lặp lại ở cả key đầu lẫn key cuối của shot. [rXslyG9nB-w 7:43]
- [ ] **FOV:** mặc định 45; tác giả hay dùng **30–35** [eMMrm-tL7mc 0:40]. FOV hẹp kết hợp máy ở xa cho cảm giác gần gũi [xGsGfdu-2-Q 7:23].
  - Code đang dùng 28–44 (OBSERVED code).
  - Đề xuất (INFERRED, sổ D 4.1): wide 40–45, medium 32–35, close-up 24–28.
- [ ] **Cỡ cảnh:**
  - Wide: mở cảnh, giới thiệu nơi chốn.
  - Medium: cho thấy nhân vật đang làm gì.
  - Close: phản ứng và cảm xúc.
  - Detail: **1–2 s**, đừng lạm dụng.
  [M0-5McNt8tE 5:41–6:44] [xGsGfdu-2-Q 1:36–3:27]
- [ ] **Góc máy:** ngang mắt là trung tính; quay từ dưới lên cho nhân vật mạnh; từ trên xuống cho nhân vật nhỏ bé, đáng xấu hổ. Vì vậy **quay Zu ngang tầm mắt Zu** (INFERRED). [M0-5McNt8tE 7:01–7:47]
- [ ] **Bố cục:**
  - rule of thirds, chỉ cần gần đường 1/3 [M0-5McNt8tE 9:05];
  - chừa khoảng trống theo hướng nhân vật nhìn [TbTvGzYP5N8 6:28–11:57];
  - giữ khung 16:9 [xGsGfdu-2-Q 8:40].
- [ ] **Chuyển động:** move-in tạo tò mò [M0-5McNt8tE 12:01]. Rung máy thủ công: mỗi 2 frame dịch máy một chút, biên độ giảm dần [YHDs-CdYgEc 2:56]. Hoặc dùng `CAM_SHAKE` kiểu Rotational [eMMrm-tL7mc 5:28].
- [ ] Với kênh trẻ em, tránh dutch tilt động, move-out kèm tilt kiểu kinh dị, và vignette đỏ (INFERRED, sổ D 4.2).
- [ ] Các quy tắc **180°, OTS, shot/reverse-shot không có trong transcript nào.** Chúng là kiến thức điện ảnh phổ thông (INFERRED, sổ D 2.3).

### 2.8 Ánh sáng
- [ ] **Render settings phải để Custom** [Y0gQWA4rW0g 9:19]. Template đang là `"performance"` (OBSERVED code). Chưa biết khi để performance thì khối `render` trong file có được áp hay không (CHƯA ĐO).
- [ ] **Ngoài trời ban ngày:**
  - sun strength **150–200%** [Vn0zjTO4dWY 12:49] [TbTvGzYP5N8 13:50];
  - sun angle **0.4–0.5** cho bóng hơi mềm [TbTvGzYP5N8 14:35]; template đang là 0.526 (OBSERVED code);
  - màu nắng hơi cam [Hj4a1avlL9o 1:41];
  - **ambient là màu của bóng**, dùng xanh khử bão hòa [TbTvGzYP5N8 15:07] [Hj4a1avlL9o 2:12];
  - hướng mặt trời phải khớp key light [Hj4a1avlL9o 6:17].
- [ ] **Hai đèn là đủ đẹp:** mặt trời làm key, thêm 1 spot fill đặt sát camera. Fill khoảng ½ key, fade 100%, sharpness 0. [EW0STx0lxKw 7:00–7:32] [Hj4a1avlL9o 7:54–8:40]
- [ ] **Rim light:** subsurface radius **khoảng 1** trên nhân vật [TbTvGzYP5N8 14:05] [Y0gQWA4rW0g 3:07]. Render subsurface samples phải lớn hơn 0; trên 64 thì vô ích [MlXA7M8J5-0 0:35]. Template đang là 0 (OBSERVED code).
- [ ] **Đèn có lý do (motivated):**
  - nguồn sáng nhìn thấy trong hình phải kèm một đèn thật chiếu lên nhân vật [Q7H78ANxC94 4:26];
  - khối phát sáng thì **tắt cast shadows**, rồi thêm point light [Y0gQWA4rW0g 1:01–1:34];
  - đuốc mặc định **không chiếu sáng** [pWm7NPNQu-A 0:55].
- [ ] **Đêm:** giữ cài đặt ngày, chỉ đổi màu (nắng xanh indigo, ambient gần đen). Không dùng đêm mặc định. Cảnh tối phải có viền sáng quanh nhân vật. [Q7H78ANxC94 2:06–2:22] [xGsGfdu-2-Q 10:00]
- [ ] **Trong nhà ấm cúng:**
  - đèn lửa nhiều lớp, range **100 / 72 / 43 / 14** từ cam đậm tới trắng [UqoGPnNgcQ4 12:37];
  - tổng số đèn càng ít càng tốt, tốt nhất dưới 4 [Y0gQWA4rW0g 7:32].
- [ ] **Color correction:** contrast khoảng **3** (thang UI; 6 đã là quá) [M0-5McNt8tE 16:13]. Đừng chỉnh màu quá tay [G4KSYcJmdk8 1:49].
- [ ] **Tone mapping, hai nguồn mâu thuẫn:**
  - "ACES, exposure 2, gamma 2.2" [TbTvGzYP5N8 12:28];
  - "exposure 2, gamma 1" [TbTvGzYP5N8 4:55].
  - So A/B bằng keyframe camera Instant [TbTvGzYP5N8 22:19]. Code giữ template: tonemapper 0, exposure 1, gamma 2.2 (OBSERVED code).

### 2.9 Render và xuất
- [ ] Preset **Custom**:
  - samples **24 cho nháp, khoảng 75 cho bản cuối** [a91bOwulnw8 1:03] [Y0gQWA4rW0g 11:24–13:14];
  - AO radius khoảng 9, strength khoảng 60% [a91bOwulnw8 2:06];
  - AA 100 [a91bOwulnw8 8:57];
  - Bend style **Blocky** [a91bOwulnw8 9:58].
- [ ] **Shadow buffer:** để nhỏ khi đang dựng, tăng lên big/very big khi render cuối [EW0STx0lxKw 3:55] [Q7H78ANxC94 12:12]. Template hiện là sun 2048, spot 512, point 256 (OBSERVED code).
- [ ] **Render → Render animation:**
  - 1080p, 24 fps, Video quality = Best;
  - tắt watermark;
  - không cần *Include audio*, vì tiếng được mix ngoài bằng `mix.py` (OBSERVED code, README).
  [a91bOwulnw8 13:46–15:49]
- [ ] **Video dài thì xuất PNG sequence.** Nếu crash, chỉ cần đặt region từ frame lỗi rồi render tiếp. MP4 crash giữa chừng có thể hỏng cả file. [a91bOwulnw8 13:46–14:48]
- [ ] Mine-imator **không xuất được video nền trong suốt** [lJgyzoZUQw0 3:31]. Muốn ghép thì dùng *Render image* với *Remove background* [nOz-trT5m9U 12:24].
- [ ] **Thao tác GUI:** Mine-imator bỏ qua click nhanh. Phải nhấn giữ khoảng 0.3 s rồi mới thả (OBSERVED, README thu01). Render chỉ làm được qua GUI; chưa có cách render headless nào được đo.
- [ ] GPU RTX 3060: mỗi lần chỉ chạy **một job nặng** (CLAUDE.md).

### 2.10 Hậu kỳ
- [ ] `mix.py` (OBSERVED code):
  - trộn voice, SFX từ `sfxkit` và nhạc nền tự tổng hợp;
  - duck nhạc khi có thoại;
  - loudnorm **−14 LUFS**, TP −1.5;
  - sau đó mux lên MP4 bằng ffmpeg.
- [ ] "Âm thanh quan trọng ngang hình ảnh" và che được lỗi hình. [jGvOjgVfN_A 7:42–8:14]
- [ ] Phụ đề làm bằng SRT ở bước auto-edit, không dựng chữ 3D (INFERRED, sổ E 3.1). Chữ 3D chỉ dùng cho tiêu đề tập. [aEWOF7xeYII 2:24]
- [ ] Cảnh tối có contrast thấp sẽ bị YouTube nén xấu thêm. [Q7H78ANxC94 2:38]
- [ ] Sau đó theo vòng CINE: `cf_qc.py` (contact sheet) → `cf_policy_check.py` → HANDOFF. Owner tự upload bản private.

---

## 3. Bảng tự động hóa: JSON (`.miproject`) hay bấm GUI?

✅ = `binbo_thu02/build.py` đã làm (OBSERVED code). `pytest tests/test_mineimator_scene.py` cho kết quả **6 passed** (OBSERVED, chạy 2026-11-03). Pytest chỉ kiểm tính nhất quán của JSON, **không phải ảnh render**.

| Kỹ thuật | JSON hay GUI | Bằng chứng | thu02 |
|---|---|---|---|
| Tempo, kích thước video, region | JSON (`project.tempo`, `video_width/height`, `timeline.region_*`) | OBSERVED code | ✅ |
| Key POS/ROT/SCA cho nhân vật và part | JSON | OBSERVED code | ✅ |
| Transition (linear, instant, ease…) | JSON (`TRANSITION`) | OBSERVED code; tên `easeinoutcubic`/`bounce` chưa render thử | ✅ (quad, sine, back, instant) |
| Key giữ, carry state, chỉ lưu giá trị khác 0 | JSON (`K()` + `flush()`) | OBSERVED code, README | ✅ |
| Overlap: lệch key part con +1/+2 frame | JSON | sổ A 3.2 (INFERRED) | một phần (blink và idle lệch pha giữa 3 nhân vật; chưa có overlap đầu/tay) |
| Idle thở | JSON | [aMTNQBzSGA8 1:36] | ✅ (chỉ body ROT_X mỗi 24 frame; chưa có đầu và tay) |
| Walk-in, sải khớp quãng đường | JSON | [NU0fAvOgEv0 13:09] [BmWf6dR4kks 3:22] | ✅ (±16°, chưa có passing, bob, dip) |
| Quay người 90°, look-at, settle | JSON | sổ B 3.2, 3.4 (code mẫu, INFERRED) | ❌ |
| Nhảy với ease out/in | JSON | [I1CGhhEcOc4 1:53] | ✅ (Zu nhảy) |
| Skin gốc + skin không mặt | JSON (`resources` type `skin`) + PNG | OBSERVED code | ✅ |
| Lớp mặt: surface parent vào head, tắt shadows/ssao | JSON (`type:'surface'`, `parent`, `inherit`) | OBSERVED code; pytest kiểm parent = head | ✅ |
| Đổi texture theo key (mắt, mày, miệng, con ngươi) | JSON (`TEXTURE_OBJ` + `instant`) | [QNeOpaw6K9I 25:15] [Un_RU3KwleY 4:36] | ✅ |
| Lip-sync theo âm lượng | JSON từ envelope | [jGvOjgVfN_A 10:37] | ✅ (3 mức × 3 họ) |
| Chớp mắt trước câu và định kỳ | JSON | [QRwM5E7NVaA 7:21] | ✅ |
| Hướng nhìn của con ngươi | JSON (POS của lớp pupils) | sổ C 4.3 | ✅ (theo preset biểu cảm) |
| Viseme theo phoneme (O/OO/W) | JSON nếu có timing phoneme | sổ C 4.4 | ❌ (CHƯA ĐO: Kokoro có xuất timing không) |
| Cắt camera Instant, FOV, push-in | JSON (`CAM_FOV`, POS/ROT) | OBSERVED code | ✅ |
| DOF, bloom, color correction, vignette, shake | JSON (`CAM_DOF*`, `CAM_BLOOM*`, `CAM_SHAKE*`…) | tên khóa OBSERVED trong mã nguồn (sổ D); thang đo CHƯA ĐO | ❌ |
| Background tĩnh (sun, ambient, fog, biome, wind) | JSON (khối `background`) | OBSERVED template | ✅ chép nguyên template, chưa tinh chỉnh |
| Render settings (samples, SSAO, buffer, glow, tonemapper) | JSON (khối `render`) | OBSERVED template; hiệu lực khi `performance` CHƯA ĐO | ✅ chép nguyên template |
| Subsurface trên nhân vật (`SUBSURFACE*`) | JSON (INFERRED) | tên khóa trong sổ D | ❌ |
| Point/spot light (`LIGHT_*`) | JSON có thể được | kiểu timeline `pointlight`/`spotlight` OBSERVED trong mã nguồn; cấu trúc timeline CHƯA ĐO | ❌ |
| Visible on/off (swap đạo cụ, ẩn chữ) | JSON (`VISIBLE`?) | sổ D ghi theo mã nguồn; sổ C/E coi là chưa đo | ❌ |
| Folder (tách trục arc, gravity) | JSON khi đã biết `type` | template **không có** folder (OBSERVED, sổ C 4.0) | ❌ |
| Animate environment (ngày → đêm) | JSON khi đã biết loại timeline | CHƯA ĐO | ❌ |
| Text 3D | JSON sau khi có mẫu GUI (INFERRED) | [aEWOF7xeYII 3:48] | ❌ |
| Particle (preset + editor) | **GUI trước**, rồi chép khối JSON làm mẫu | [uCPv8ce6dOI] [v1OYnJFLzXQ] | ❌ |
| IK, path, constraint | **GUI** (cấu trúc JSON chưa biết) | [eEtFSQGXi_I] [NMRHDtSkehw] | ❌ |
| Walk/run cycle tự động | **GUI** (chuột phải → Create walk cycle) | [nOz-trT5m9U 7:33]; có trên 2.0.2 không thì CHƯA ĐO | không cần (code tự sinh) |
| Export/Import keyframes (thư viện động tác) | GUI; định dạng file CHƯA ĐO | [ieV5yGq7-hI 4:58] [w3HKHvnhSiI 28:09] | không cần (hàm Python thay thế) |
| Import world, block filter | **GUI** | [pjrAmdnpffA] [06Rt_KB-oh4] | ❌ (set hiện tại là ground mặc định) |
| Render animation / render image / bỏ nền | **GUI** | [a91bOwulnw8 13:46] | GUI, nhấn giữ 0.3 s |
| Âm thanh: VO, SFX, nhạc, LUFS | ngoài Mine-imator (Python + ffmpeg) | OBSERVED code (`tts.py`, `mix.py`) | ✅ |
| Gán chuỗi ảnh greenscreen vào texture theo frame | JSON làm được bước tẻ nhạt này (INFERRED) | [lJgyzoZUQw0 5:27] | ❌ (ưu tiên thấp) |

**Việc chặn đầu tiên cho mọi ô ❌ có chữ "CHƯA ĐO"** (sổ C 4.6, E 3.2):
1. Trong GUI 2.0.2, tạo một project nhỏ gồm: 1 folder, 1 cube, 1 point light, 1 spot light, 1 key Visible off, 1 Background timeline (key ngày → đêm), 1 particle, 1 text 3D, và subsurface trên một nhân vật.
2. Lưu project lại.
3. Diff với `template.miproject` để lấy tên khóa thật.

**Lưu ý file (OBSERVED):** `binbo_thu02/README.md` hiện là **bản chép của thu01**: tiêu đề "test scene 01", mô tả đổi skin `TEXTURE_OBJ` trên body. README này chưa mô tả face rig 4 lớp, `faces.py` hay `prep.py`. Nên cập nhật.

---

## 4. Lỗi người mới hay mắc và cách sửa

| # | Lỗi | Dấu hiệu | Cách sửa | Nguồn |
|---|---|---|---|---|
| 1 | Trượt chân | chân lướt trên đất | chân và root cùng linear, sải khớp quãng đường; dời key cuối của root | [2Klmj7x8IvI 1:02] [BmWf6dR4kks 3:22] [xH9t-hLVWhY 1:05] |
| 2 | Quên key giữ | động tác chạy từ frame 0 | copy key tĩnh, dán ở frame bắt đầu động tác | [BNE7CsRE79o 2:23] [w3HKHvnhSiI 4:27] |
| 3 | Mọi thứ đều linear | trông như robot | ease in/out; linear chỉ cho chân và chuỗi động tác rất nhanh | [2Klmj7x8IvI 6:12] [G4KSYcJmdk8 4:34] |
| 4 | Transition bị kế thừa | key mới mang easing lạ | box-select rồi đặt lại transition | [BNE7CsRE79o 9:03] |
| 5 | Sửa trong lúc đang chọn key | ghi đè key cũ, hoặc tạo key thừa | bỏ chọn mọi key; đặt marker đúng lên key cần sửa | [NU0fAvOgEv0 2:22] [0N4zaeMgQvA 17:35] |
| 6 | Nhân vật đứng im hoặc đứng thẳng đơ | trông như tượng | idle thở, lắc nhẹ; tay hơi mở ra, không để toàn 0 | [G4KSYcJmdk8 1:28] [VdJh-vTewJY 15:58] |
| 7 | Nhảy hình tam giác | không có cung | tách trục: ngang linear, folder lên xuống có ease | [2Klmj7x8IvI 2:46] [IyUfooxLmGE 0:46] |
| 8 | Ease out rồi ease in trên cùng một timeline | vật "kẹt trong thạch" giữa không trung | dùng folder "gravity" riêng | [I1CGhhEcOc4 0:36–1:06] |
| 9 | Pose mất thăng bằng | sắp ngã | trọng tâm nằm trên vùng bàn chân chạm đất; kiểm cả nhìn trước lẫn nhìn ngang | [2Klmj7x8IvI 3:48] [I1CGhhEcOc4 3:26] |
| 10 | Chỉ cười bằng miệng | mặt vô hồn | mắt, mày, con ngươi cùng phản ứng | [0OuknDnKE-E 0:47] |
| 11 | Lông mày scale theo khi chớp mắt | mày co giãn | đưa mày ra ngoài folder mắt hoặc tắt inherit scale (thu02 đổi texture nên không gặp) | [kaw2sRFgdjg 8:06] |
| 12 | Parent sau khi đã dời object | object bay ra xa | parent trước rồi mới dời, hoặc reset vị trí về 0 | [wKxWrICAC-E 1:02] [nOz-trT5m9U 5:32] |
| 13 | Z-fighting | nhấp nháy ở chân hoặc lớp mặt | scale chân 0.999; đẩy lớp mặt thêm 0.01 | [TcNSoStA0Js 8:31] [kaw2sRFgdjg 1:06] |
| 14 | Mặt sau vô hình | thấy xuyên qua object | bật *Show back faces* | [JBIn_WC4jSY ~2:40] |
| 15 | Đổi góc máy không dùng Instant | máy bay xuyên cảnh | key cuối shot đặt Instant | [rXslyG9nB-w 2:39–3:27] |
| 16 | Tempo lệch FPS xuất | lộ 1 frame thừa ở chỗ cắt | tempo = FPS xuất | [PHTPcUdK84I 13:03] |
| 17 | Ánh sáng mặc định | một nguồn, bóng gắt | key + fill, ambient màu, Custom render | [2Klmj7x8IvI 4:49] [G4KSYcJmdk8 2:10] |
| 18 | Chỉnh màu hoặc hiệu ứng quá tay | ảnh gắt, rẻ tiền | contrast khoảng 3, bloom nhẹ | [G4KSYcJmdk8 1:49] [M0-5McNt8tE 16:13] |
| 19 | Lệch phong cách | skin HD cạnh item thô | đồng bộ độ phân giải texture | [G4KSYcJmdk8 3:52] |
| 20 | Lạm dụng shot detail | mất giá trị nhấn | 1–2 s mỗi lần, dùng ít | [xGsGfdu-2-Q 2:55] |
| 21 | Item hoặc đòn bẩy lơ lửng | vật "bay" | key mặc định của bản dưới đất phải Invisible | [mU4aMjfMqTs 40:48] |
| 22 | Mây hoặc gió bật/tắt bị giật | nhảy giá trị | đây là công tắc, không nội suy; dán key mặc định trước 1 frame | [rE7B5reAPg0 15:19] |
| 23 | World sai phiên bản | import ra trống trơn hoặc mất block | dùng world đúng phiên bản được hỗ trợ | [pjrAmdnpffA 0:20] [06Rt_KB-oh4 11:36] |
| 24 | Xóa scenery chưa sạch | vẫn còn trong project | xóa ở cả Library lẫn Resources | [pjrAmdnpffA 4:30] |
| 25 | Render MP4 một mạch cho video dài | crash làm hỏng file | xuất PNG sequence, render tiếp theo region | [a91bOwulnw8 13:46] |
| 26 | DOF hoặc glow "không thấy" | viewport không đổi | các hiệu ứng này chỉ hiện ở chế độ Rendered | [0N4zaeMgQvA 23:42] [QNeOpaw6K9I 23:03] |
| 27 | Nội dung số lượng, chất lượng thấp kiểu "Monster School" | — | "Quality over quantity" | [G4KSYcJmdk8 1:07] |
| 28 | (pipeline) Root timeline trùng `parent_tree_index` | nhân vật biến mất khỏi cây | mỗi root một chỉ số riêng (pytest có kiểm) | OBSERVED README, test |

---

## 5. Điều KHÔNG được làm (bản quyền, IP, an toàn kênh)

1. **Không tải rig, face rig, skin, texture hay mouth pack của người khác** khi không có **giấy phép văn bản rõ ràng**. Không mô tả video nào có giấy phép như vậy (OBSERVED, sổ C mục 1):
   - SharpWind Face Rig 2.0: chỉ có lời nói "nhắc tên tôi, tôi không kiện" [puXk5_aVtvY 11:01].
   - AN Rig [gVMo4SJ4oyE].
   - Rig 2D của AnxiousCynic: chỉ bán qua Patreon [QMqEW2Vqa10].
   - Mouth pack trên Google Drive: chính tác giả dùng texture của người khác [Un_RU3KwleY 2:07].
   - File của ArdeeLIVE [wKxWrICAC-E].
   - ZAMination Rig [iRJQGJ3rE3A].
   - Asset trên Discord của Subh [OGLkFs2mXtg] [0OuknDnKE-E].
   - Rig "Opaque V1" [WRgtbdkLYf8].
   - Video của SaGa_XQ ghi CC-BY, nhưng đó là giấy phép **của video**, không cấp quyền dùng rig [g0nPs43L3CI].
   - → Chỉ học **kỹ thuật**. Mọi PNG mặt đều do `faces.py` tự vẽ.
2. **Không dùng TLauncher** hay launcher lậu để lấy world. [06Rt_KB-oh4 12:00]
   - Chỉ import world tự xây trên **Minecraft Java chính chủ**. Owner đã quyết mua Java Edition (OWNER, ghi chú dự án).
3. **Không lấy PNG trên Google.** Áp dụng cho biểu cảm khuôn mặt [OGLkFs2mXtg 0:30], sprite sheet hạt [v1OYnJFLzXQ 31:50], texture sương/mây/trời [x_j0jA-QtBQ 1:19].
   - → Tự vẽ hoặc tự sinh bằng Python (sổ D 3.3; INFERRED).
4. **Không tải skin theo username** của người khác (*Download from Minecraft user*). [w3HKHvnhSiI 0:44]
   - → Chỉ dùng skin gốc từ `skins.py`.
5. **Không import world, map hay schematic của người khác.** Không đưa nhân vật, skin, thế giới hay kịch bản của kênh đối thủ vào phim (CLAUDE.md, luật Original IP).
6. **Âm thanh:**
   - Mine-imator không có sẵn âm thanh game [PHTPcUdK84I 26:04].
   - Không cắt audio từ phim thương mại. ZAMination dùng audio của *The Mask* [iRJQGJ3rE3A].
   - Giọng nói dùng Kokoro (Apache-2.0). SFX và nhạc do `sfxkit` và `mix.py` tự tổng hợp (OBSERVED code).
   - **Nhạc Minecraft/Mojang chỉ dùng track nằm trong danh sách Creator-Safe chính thức.** Đây là luật trong brief của owner, không có trong 5 sổ học; phải kiểm danh sách chính thức trước mỗi lần dùng.
7. **Không dùng resource pack hay texture pack của bên thứ ba** nếu chưa kiểm giấy phép. Ví dụ "Bare Bones" được nhắc trong [QhMY2ac0nOk 13:30] (INFERRED: chưa rõ điều khoản).
8. **Không cần Community Build.** Đó là bản không chính thức, Windows còn cảnh báo khi chạy [PHTPcUdK84I 35:03]. Tính năng light groups chỉ có ở bản CB (sổ D, grep mã nguồn 2.0.2).
9. **Không làm theo ngữ pháp kinh dị** cho kênh trẻ em: dutch tilt động, move-out kèm tilt, vignette đỏ, góc frog nhìn lên nhân vật đáng sợ (INFERRED, sổ D 4.2).
10. **Không upload hay publish, không gọi API hoặc MCP tốn credit** khi chưa có owner (CLAUDE.md, cf_guard).

---

## 6. Top 10 video nên xem lại bằng mắt

Các sổ học chỉ đọc transcript. Những video dưới đây có thông tin **chỉ thấy bằng hình**, hoặc có số liệu ASR nghe chưa chắc.

| # | Video | Vì sao phải xem bằng mắt |
|---|---|---|
| 1 | [QRwM5E7NVaA](https://www.youtube.com/watch?v=QRwM5E7NVaA): SharpWind, Conversational Motion | Đây là mẫu chính cho diễn xuất hội thoại. Video không đọc số biên độ đầu, thân, tay nên phải xem nhịp nhấn từ và cung tay. |
| 2 | [jGvOjgVfN_A](https://www.youtube.com/watch?v=jGvOjgVfN_A): SharpWind, Lipsync | Xem miệng mở to hay nhỏ ra sao theo âm lượng, và vị trí key so với đỉnh âm, để chỉnh ngưỡng 0.12/0.38/0.70 của mình. |
| 3 | [Un_RU3KwleY](https://www.youtube.com/watch?v=Un_RU3KwleY): AnxiousCynic, Lip Sync bằng texture | Cùng phương pháp D với thu02. Xem cỡ surface miệng (scale 0.5) và độ lệch +0.01 khi camera ở xa. Chỉ xem, **không tải pack**. |
| 4 | [BbcV5uGm0jM](https://www.youtube.com/watch?v=BbcV5uGm0jM): SharpWind, Emotions | Bảng cảm xúc ở mục 2.3 chỉ có chữ. Cần xem dáng thân và vị trí con ngươi để vẽ lại PNG mắt và mày. |
| 5 | [aMTNQBzSGA8](https://www.youtube.com/watch?v=aMTNQBzSGA8): SharpWind, Improved Idle | Video chỉ nói "minimal". Cần thấy biên độ thật để đặt idle cho đầu và tay (thu02 mới có thân). |
| 6 | [NU0fAvOgEv0](https://www.youtube.com/watch?v=NU0fAvOgEv0): AnxiousCynic, Walk Cycle Part 3 | Đối chiếu bảng walk 4 pose: góc gối ở pose passing, bob −1. Góc chân và tay không được đọc thành tiếng. |
| 7 | [rXslyG9nB-w](https://www.youtube.com/watch?v=rXslyG9nB-w): AnxiousCynic, Camera Part 15 | Bộ số DOF "40, 10 và 50" có thể ASR nghe sai. Xem cách cắt Instant và rotate-around-point trên panel. |
| 8 | [TbTvGzYP5N8](https://www.youtube.com/watch?v=TbTvGzYP5N8): BeinBian, Lighting 2.0.0 | Nguồn ánh sáng chính cho 2.0. Có hai bộ exposure/gamma mâu thuẫn, và thang UI so với giá trị trong file chưa rõ. |
| 9 | [a91bOwulnw8](https://www.youtube.com/watch?v=a91bOwulnw8): AnxiousCynic, Render Settings Part 7 | Xác nhận tên trường render trong 2.0. Số thời gian render ở 75 samples bị ASR cắt. |
| 10 | [eYJK2OnzQ0Y](https://www.youtube.com/watch?v=eYJK2OnzQ0Y): Anvey, Shorts 1 giờ | **Không có transcript.** Sổ A chỉ có chương mục và 13 ảnh storyboard. Các chương "Lighting characters" (24:11) và "Animation workflow" (30:55) chỉ học được bằng mắt. |

Nếu còn thời gian, xem thêm:
- [M-upI7h19kw](https://www.youtube.com/watch?v=M-upI7h19kw): cách giữ bàn chân trụ khi quay người.
- [Y0gQWA4rW0g](https://www.youtube.com/watch?v=Y0gQWA4rW0g): số glow "1200" có thể ASR nghe sai.

---

## 7. Những điểm CHƯA ĐO (cần render thử để xác nhận)

Đo trên máy CINE. Ghi kết quả vào README của thu02, và ghi thời gian vào `data/production_ledger.jsonl`.

1. **thu02 chưa có bằng chứng render.** Trong repo chỉ có pytest kiểm JSON (6 passed). Chưa thấy ảnh hay receipt nào. Có một chú thích "head-local +Y = forward … measured" nằm trong code (OBSERVED code), nhưng không có ảnh đi kèm.
2. **Các lớp mặt hiển thị có đúng không:**
   - texture 32×32 có lật ngang hay dọc không;
   - SCA 0.5 có phủ đúng mặt 8×8 không;
   - lệch 4.02–4.045 có bị z-fight hay "nổi" khi camera ở xa không [Un_RU3KwleY 3:04];
   - mắt và mày của Zu có lệch không khi đầu scale 1.25.
3. **`render_settings: "performance"`** so với `"custom"`: khối `render` trong file có được áp không.
4. **Thời gian render** 1080p ở 24 và ở 75 samples trên RTX 3060. Hiện là "not measured".
5. **Thang đo trong file so với UI:**
   - sunlight_strength (1 = 100%?);
   - CAM_CONTRAST ("3" trên UI có phải 0.03 trong file?);
   - glow radius;
   - subsurface highlight;
   - DOF blur (UI 10 so với mặc định 0.01 trong file).
6. **`CAM_FOV` là FOV dọc hay ngang.** Đặt một block 16 đơn vị ở khoảng cách đã biết rồi đo.
7. **Giá trị enum:** `tonemapper`/`CAM_TONEMAPPER` (0/1/2?) và `CAM_SHAKE_MODE`.
8. **Dấu và trục trên part:**
   - ROT_Z và ROT_Y của đầu và thân;
   - `BEND_ANGLE_X` ở gối và khuỷu.
   - README chỉ mới chốt ROT_Z của root và ROT_X của part.
9. **Tên khóa và kiểu timeline:** `VISIBLE`, `ALPHA`, folder, point/spot light, Background timeline, particle, text. Đo bằng project mẫu ở cuối mục 3.
10. **Trượt chân của walk-in thu02:**
    - sải ±16° so với tốc độ root (INFERRED gần khớp);
    - đoạn 72→82 root dùng `easeoutquad` trong khi chân vẫn linear tới frame 78. Theo [BmWf6dR4kks 3:22] đoạn này có thể trượt.
    - Kiểm bằng contact sheet.
11. **Subsurface khoảng 1** có tạo rim trên skin 64×64 khi đèn đặt sau lưng không.
12. Tên transition `easeinoutcubic` và `easeoutbounce` có chạy trong render không. Pytest chỉ kiểm tên theo một mẫu đặt tên.
13. Bản 2.0.2 có **Create walk cycle** không. Nguồn 2.0 nói có [nOz-trT5m9U 7:33]; bản pre-release của classToon thì không [w3HKHvnhSiI 11:43].
14. Định dạng file **Export keyframes** (.miframes?), và code có tự sinh được file này không.
15. Kokoro có xuất **timing phoneme** được không, để dùng viseme O/OO/W.
16. Đặt key miệng sớm 1 frame trước đỉnh âm có đẹp hơn không. Đây là quy ước hoạt hình, **không có trong transcript**.
17. Chuỗi PNG từ *Render image + Remove background* có alpha sạch để ghép bằng FFmpeg không.
18. Có cách **render không qua GUI** không. Hiện chưa biết cách nào.
19. Phím E/Q (lên/xuống) và "Ctrl R" để xóa key có đúng không, vì đều nghe từ ASR (sổ A 4).
