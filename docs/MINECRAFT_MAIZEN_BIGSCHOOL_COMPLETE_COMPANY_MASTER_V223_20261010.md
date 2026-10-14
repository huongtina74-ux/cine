# CINEFACTORY – CÔNG TY SẢN XUẤT MINECRAFT: MASTER PLAYBOOK v223
Ngày: 10/10/2026 · Trạng thái: RESEARCH + PIPELINE PLANNING, CHƯA PHẢI PHIM HOÀN THIỆN.

## A. Phương pháp và phạm vi (cần phân biệt ngay)

Nghiên cứu **cách tổ chức loại nội dung**, KHÔNG sao chép JJ/Mikey, tên thương hiệu, skin riêng, cảnh, lời thoại, nhạc, thumbnail hay render của Maizen/BigSchool. Có hai tuyến:
- **MAIZEN-STYLE: SCRIPTED_MINECRAFT_GAMEPLAY**: trải nghiệm Minecraft thật, có thể đạo diễn, thu hình game và nói chuyện giữa hai nhân vật gốc; có gameplay, mô-đun xây dựng, câu đố, thử thách và camera thật. Phải có Minecraft runtime/ghi hình thật; Blender-render không được gắn nhãn gameplay Minecraft thật.
- **BIGSCHOOL-STYLE: AUTHORED_VOXEL_3D_ANIMATION**: phim hoạt hình 3D voxel được dựng bằng Blender, tính cách và câu chuyện gốc, rig + acting + camera + Foley, có thể tạo compilation từ những tập do công ty sở hữu. Không phụ thuộc game runtime nếu là phim hoạt hình được tự sáng tác.

Mô hình đúng cho công ty không phải chọn «AI nào làm cả video», mà là **scene director phân công từng shot**, asset pipeline riêng, kỹ thuật kiểm tra bằng media thật, rồi phục hồi các lỗi dựa trên nguyên nhân. 26 phòng ban đã có trong source, 28 bước dưới đây được chuẩn hóa JSON để không bỏ qua.

## B. Video nghiên cứu ưu tiên và kết luận THỰC SỰ có bằng chứng

| ID | Kênh/video gốc | Dữ liệu kiểm tra bên ngoài | Vì sao chọn nghiên cứu | Chưa chứng minh |
|---|---|---|---|---|
| M01 | Maizen – [Mikey and JJ Choose the Right Hole in Minecraft](https://www.youtube.com/watch?v=ZmT0ITUGUII) | YouTube metadata công khai: xuất bản 28/08/2026, tại lượt truy xuất ghi khoảng 2.65 triệu views. Chỉ mục khác ghi 28:05 (cần xác minh bằng player). | Mô hình lựa chọn A/B → nguy hiểm/phần thưởng → câu chuyện liên tục. | Chưa xem toàn bộ footage, soundtrack, shot count, rig/mod, nền tảng edit, retention, RPM. |
| M02 | Maizen – [Built a House inside BED in Minecraft](https://www.youtube.com/watch?v=zhPBXzHsLuo) | YouTube chính thức 15/10/2025, tại lượt truy xuất ghi khoảng 16.85 triệu views. Mô tả: ẩn náu trong nhà đối thủ và tìm kim cương bị lấy. | Mục tiêu rõ → bí mật → nguy cơ bị phát hiện → giải quyết. | Chưa xác minh duration và từng thao tác Minecraft, camera/capture cụ thể. |
| B01 | BigSchool – [Season 3 All Episode - Minecraft Animation](https://www.youtube.com/watch?v=X09yxFuKLAs) | YouTube chính thức 18/08/2020, metadata lượt truy xuất ~135.24 triệu views. Chỉ mục phụ báo 1:09:34. Mô tả video có 7 chương. | Cách tổ chức sitcom/chuyện cảm xúc và compilation thành phim dài. | Chưa xem bất kỳ đoạn chương nào với frame/sound đã giải mã, chưa biết chính xác phần mềm sản xuất. |

**7 chương BigSchool chỉ mới xác minh từ phần mô tả**:
1. 00:00:01 – Baby Zombie was Homeless
2. 00:10:48 – Funny Zombie Family
3. 00:21:48 – Poor Skeleton Girl
4. 00:32:58 – Fight Diamond Bandits
5. 00:46:03 – Rescue Baby Zombie from Piggy
6. 00:57:05 – Ziczac Game
7. 01:08:07 – Can Knockdown

Không được coi timestamp chương từ description là đã quan sát được động tác/nhịp cắt/camera. Nghiên cứu dữ liệu 2026 cần so sánh BigSchool giai đoạn 2020–22 với hướng video ngắn 2023–26; **không dùng thành tích compilation cũ để chứng minh dễ thắng long-form năm 2026**.

**Lệnh nghiên cứu video khi có nguồn hợp pháp:** lấy video được phép xem, kiểm tra tồn tại toàn bộ video+audio; ghi thời gian start/end, mục tiêu cảnh, chuyển động, vị trí camera, góc quay, âm thanh/nhạc/VO, phương án phối cảnh, cơ chế gameplay thật/hình 3D, nhịp cắt, cao trào, kết thúc; lưu bằng chứng. Gán OBSERVED chỉ cho những hình/âm đã thực sự kiểm tra, còn lại PUBLIC_METADATA / HYPOTHESIS / NOT_VERIFIED. So sánh cả video kém thành công để tránh ngộ nhận.

## C. 26 PHÒNG BAN – phân công đầy đủ

1. **STUDIO_MANAGEMENT**: Tổng giám đốc phê duyệt dự án, ngân sách, lịch, release/rollback.
2. **INTELLIGENCE**: Kiểm tra tuổi kênh, video từ 8 phút, tốc độ view, mẫu yếu, xu hướng, lợi nhuận chỉ từ dữ liệu cho phép.
3. **EVIDENCE**: Sưu tầm URL, bản xem hợp pháp, soundtrack, media hash và bảng timestamp.
4. **CREATIVE_STRATEGY**: Định vị khán giả tiếng Anh, lời hứa của series, tách kênh phù hợp.
5. **PLANNING**: Tiến độ và critical path, năng lực GPU, ước lượng shot và chi phí.
6. **WRITERS_ROOM**: Kịch bản mới có hook, xung đột, diễn tiến, payoff, bí mật cuối.
7. **SCRIPT_LOGIC**: Continuity đạo cụ/động cơ/cơ chế luật game và mốc thời gian.
8. **DIRECTION**: Phê duyệt storyboard, diễn xuất, camera coverage và chất lượng kể chuyện.
9. **PERFORMANCE**: Voice/expressions/rig acting, viseme, cảm xúc, động tác đáng tin.
10. **CINEMATOGRAPHY**: Wide/medium/close, góc trục 180°, blocking, ống kính, chuyển động, chiếu sáng.
11. **PRODUCTION_DESIGN**: Art bible, thiết kế trường học, hang, nhà bí mật, texture, màu.
12. **ASSETS**: Model/skin 64×64 gốc, UV, rig, character registry, world, mobs/props với quyền thương mại.
13. **TECHNICAL_DIRECTION**: Phân cảnh real gameplay và hoạt hình dựng; chọn backend/chất lượng/VRAM.
14. **PRODUCTION**: Thu game gốc hoặc render Blender, lấy dailies/hash/version, sửa từng shot.
15. **GENERATIVE_MEDIA**: AI storyboard/plate/effect tùy trường hợp, miễn phí local trước; cloud có duyệt chi phí.
16. **VFX**: Contact/shadow/particle/lighting/comp chỉ phục vụ câu chuyện.
17. **EDITORIAL**: Animatic, EDL, chương, nhịp, cắt, chuyển cảnh, phụ đề, export.
18. **AUDIO**: Diễn viên giọng thật/TTS có phép, Foley, nhạc/SFX gốc, mixing, loudness.
19. **COLOR**: Quản lý màu phim, match nhân vật qua góc, tránh flicker.
20. **QC**: Review hình/âm từng shot, continuity, hiệu ứng, lỗi/return-to-scene; ký nghiệm thu.
21. **RIGHTS**: Minecraft Fan Usage, fan Maizen điều kiện, nhạc/giọng/asset, YouTube inauthentic content.
22. **PACKAGING**: Thumbnail, title, description, chapters, subtitles, CTR hypothesis.
23. **ANALYTICS**: Chỉ từ dữ liệu tài khoản tự sở hữu mới tính retention/CTR/RPM; public reference chỉ có public views.
24. **RND**: So sánh Blender4.5, real Minecraft capture, Blockbench, ComfyUI, âm thanh và MCP an toàn.
25. **RD_KNOWLEDGE**: RCA, skill/eval, quy tắc và test cập nhật sau bằng chứng.
26. **OPERATIONS**: Persistent worker, queue/GPU, retry, log, backup/restore, crash-resume, release.

## D. 28 BƯỚC BẮT BUỘC CỦA CÔNG TY (từng bước có output và cổng chặn trong JSON)

### Phase 1 — Nghiên cứu ngách và video
**G01 Intelligence**: Xác minh ba video (kênh chính thức, upload, length, views as-of, tình huống cũ/mới, đối chứng video yếu). Output: `candidate_video_ranking.json`. **Chưa PASS** vì dữ liệu bên ngoài và mẫu đối chứng chưa đầy đủ.

**G02 Evidence**: Lấy quyền truy cập video/audio thật; giải mã/xem từng phần đầy đủ; ghi timecode và link/source + bản chứng thực. Output: `full_video_audio_evidence.json`. Không được tự điền OBSERVED nếu không có media.

**G03 Intelligence + Direction/Edit**: Xây bảng cạnh tranh: hook 0-30s, trạng thái nhân vật, diễn tiến goal/stakes, mỗi reveal, cut rate, camera, props, camera in-game vs dựng 3D, âm thanh/chapter, cliffhanger. So sánh M01/M02/B01 cùng mẫu yếu.

**G04 Creative Strategy**: Chấm 5 yếu tố traffic, tiềm năng monetization, bền vững, khó cạnh tranh, khả năng automation và quyền. Yêu cầu bằng chứng kênh mới 0–30 ngày **hai video khác nhau ≥8 phút, mỗi video ≥1M trong 14 ngày** nếu muốn khẳng định breakout; hiện chưa có.

### Phase 2 — Duyệt nguyên tắc và kịch bản
**G05 Studio Management**: Chủ dự án phê duyệt hai lane, tách kênh nếu khác audience promise, chọn 45s pilot trước 8–18min, không chi trả model/API.

**G06 Writers Room**: 10 câu chuyện mới độc lập; chọn 1 story có objective/twist; không kể lại video Maizen/BigSchool, không dùng tên/skin JJ, Mikey, các bản render nguyên gốc kênh khác.

**G07 Script Logic**: Episode beats có cause-effect, chủ thể/hành động, kiểm tra vật thể xuất/biến mất, thời gian, teleport, Minecraft physics và luật thử thách.

### Phase 3 — Preproduction
**G08 Director**: Bản storyboard/animatic locked có số shot, camera, audio cue và thời gian ước tính; review đọc hiểu trên điện thoại.
**G09 Production Design**: Tạo world original, layout nhà/trường/hang/đồ vật, palette và định hướng ánh sáng.
**G10 Assets**: Hai nhân vật original 64×64 UV + layer 3D, IK/FK khớp vai/khuỷu/cổ tay/hông/chân, rig expression, sockets, mob props; manifest/version/license.
**G11 Performance**: Thư viện diễn xuất có body mechanics walk/run/turn/stop/recoil/reaction/grab, bước chân, eye/brow/mouth viseme; cast voice theo lứa tuổi và quyền.
**G12 Cinematography**: Wide/medium/close/OTS, trục camera, shot geography, lighting cue, preview multi-camera theo intent.
**G13 R&D**: Cùng một cảnh khó benchmark existing Blender 4.5, Eevee/Cycles có kiểm soát, audio/editor; Blockbench glTF, Mineways, MCprep, Mine-imator chỉ khi license+compatibility được kiểm tra; Comfy/Higgsfield chỉ khi chứng minh có giá trị.
**G14 Rights**: Approve asset, texture, nhạc, diễn viên, mod, world, TTS và game use policy; kiểm tra nhu cầu voice clone và brand confusion.
**G15 Planning/Ops**: Kiểm tra capacity 3060 12GB, 1080p24, shots, parallel CPU/GPU, cảnh hỏng/lặp lại và chi phí mỗi giây phim đạt QC.

### Phase 4 — Sản xuất thật
**G16 Technical Direction**: Mỗi shot phải định nghĩa `AUTHORED_3D` hoặc `REAL_GAME_CAPTURE`. Không trộn hai hình thức rồi tuyên bố game thật khi footage là Blender.
**G17 Production**: Animatic → blocking → character/body keyframes → face/props → background/light → camera → first dailies → beauty render hoặc record game+sound thật → media receipts.
**G18 Generative Media**: AI dùng riêng concept/background/VFX nếu đủ quyền và giữ identity; mặc định local, không trả credits.
**G19 VFX**: World particles, prop contact, light reveal, compositing, masking, camera physics; không vá lỗi diễn xuất cơ bản bằng upscale.

### Phase 5 — Hậu kỳ
**G20 Audio**: Script/VO/foley/music, lipsync+reaction cues, kiểm tra peak/clipping/mono/mobile và giấy phép.
**G21 Editorial**: Mỗi scene có lý do kể chuyện, pacing thử trước 8 phút, xuất timeline deterministic, không kéo dài vô nghĩa.
**G22 Color**: Color match, 3D shader skin consistency, light temperature across cuts, check display SDR/mobile.

### Phase 6 — QC, phát hành và học hỏi
**G23 QC**: Independent full-video+sound inspection, visual/acting/camera/continuity, original rights, 1080p24 >30s pilot thực; chưa qua thì BLOCK.
**G24 Operations**: Re-render shot lỗi chứ không redo cả episode; receipts, SHA, cost/VRAM, backup/resume, ensure nothing silently skipped.
**G25 Packaging**: Hai title/thumbnail variants trung thực, tên nhân vật gốc, mô tả tiếng Anh, chapter, subtitle và attribution.
**G26 Studio Management**: Duyệt phát hành sau rights/QC/phim hoàn chỉnh. Không auto-upload.
**G27 Analytics**: Kênh mình có số 24h/7d/14d, retention, CTR, RPM nếu được cung cấp thực; không lấy con số tưởng tượng.
**G28 R&D Knowledge**: RCA video/scene lỗi, thay đổi skill/camera/rig/lighting/acting rules theo phiên bản, có negative-control tests để không lặp lại.

## E. 6 tập ORIGINAL cần sản xuất / ý tưởng theo thứ tự

### Lane 1 – MAIZEN-STYLE, game thật
- **MAI01: We Built a Secret Base Beneath a Waterfall** (12–18 phút): hai nhân vật của chúng ta phát hiện lối vào sau thác, xây căn cứ bí mật, va nguy hiểm, đổi cách sinh tồn và mở ra bí ẩn tiếp theo. Mở đầu: dấu lạ sau thác ở 0–15s. Cần đúng Minecraft runtime, world/maps và recording/camera, logic interactive đúng thật.
- **MAI02: Which Portal Leads to the Lost Village?** (12–20 phút): cơ chế 2-3 lựa chọn với hậu quả thật/logic nội tại được thiết kế riêng; giữ lời hứa cuối mỗi thử thách.
- **MAI03: The Tiny House Has a Giant Secret** (12–18 phút): thế giới ẩn bên trong ngôi nhà, các thử thách giải cứu và kết có đảo ngược tình huống.

### Lane 2 – BIGSCHOOL-STYLE, hoạt hình original
- **BIG01: The Lost Lantern** (45 giây R&D): đã có storyboard v222 10 shot, hai nhân vật Nova/Pip ở làng/hang; đây là **mục tiêu phải render**, chưa có media.
- **BIG02: The Quiet Student and the Broken Robot** (8–12 phút): tình bạn và lòng tốt trong ngôi trường voxel với robot hỏng; nhiều emotional-acting shot; tạo động lực tái sử dụng lớp học và actor rig.
- **BIG03: The Villager Who Could Control Weather** (8–12 phút): năng lực thời tiết gây hậu quả rồi phải sửa; thử nghiệm VFX và cốt truyện 3 hồi, giữ 3D character continuity.

Maizen-style là **cảm hứng về cơ chế nội dung** chứ không sử dụng nhân vật/tên chính thức. Nếu sau này muốn làm fan content JJ/Mikey, phải kiểm tra riêng điều kiện Maizen, tránh gây hiểu nhầm official và mở lại rights gate. Hướng IP gốc giảm rủi ro thương hiệu.

## F. Chỉ số nghiệm thu cần biết trước khi nâng lên 8–18 phút

- Quality: nhân vật dễ nhận biết từ cả 3 góc, texture 64x64 sắc nét, đạo cụ chạm tay đúng, acting có anticipation/follow-through và footplant, face viseme, bối cảnh đủ depth, 3+ camera coverage có chủ đích, thoại/foley/music khớp và không clip.
- Technical: 1920×1080@24fps min cho pilot, encode H264/AAC, actual decoded full video/audio, SHA provenance và original commercial rights.
- Story: câu chuyện gốc 45s phải có opening/context/problem/action/reversal/payoff, có thể kể lại với người xem không cần biết Minecraft.
- Operations: đo output thực `accepted_finished_seconds / wall_clock_hours`, lỗi bị trả, peak VRAM, GPU busy, số lần re-render, cost per accepted minute, log renderer reset/recovery.
- Initial KPI giả thuyết: chỉ mở rộng longform nếu pilot 45s qua hard gates và đáp ứng lịch sản xuất có căn cứ; **không đưa target USD/CTR/RPM là kết quả đã xác minh**.

## G. Tài liệu nguồn cốt lõi và pháp lý (đọc nguyên bản trước khi tải hoặc dùng asset)

- Maizen right-hole metadata: https://www.youtube.com/watch?v=ZmT0ITUGUII
- Maizen hidden-BED metadata: https://www.youtube.com/watch?v=zhPBXzHsLuo
- BigSchool Season 3 với chapter markers: https://www.youtube.com/watch?v=X09yxFuKLAs
- Blender Studio Minecraft animation workshop: https://studio.blender.org/training/minecraft-animation-workshop/
- Blockbench model/edit/texture/animation guide: https://learn.microsoft.com/en-us/minecraft/creator/documents/blockbench
- Blockbench glTF for Blender rendering: https://blockbench.net/wiki/guides/export-formats/
- Mineways world export: https://erich666.github.io/Mineways/mineways.html
- Minecraft official policy: https://www.minecraft.net/en-us/usage-guidelines
- Maizen fan IP policy: https://maizen.com/usage-guidelines/
- YouTube inauthentic content policy: https://support.google.com/youtube/answer/1311392

## H. Chức năng sử dụng ngay trong CineFactory v223

```powershell
python -m cinefactory.cli minecraft-company-roadmap
python -m cinefactory.cli minecraft-company-roadmap --lane AUTHORED_VOXEL_3D_ANIMATION --phase PREPRO
python -m cinefactory.cli minecraft-company-roadmap --lane SCRIPTED_MINECRAFT_GAMEPLAY --phase RESEARCH
python -m cinefactory.cli minecraft-company-roadmap --lane AUTHORED_VOXEL_3D_ANIMATION --blockers-only
python -m cinefactory.cli minecraft-production-research
python -m cinefactory.cli niche-technology-plan --minor-niche minecraft_school_comedy
```

Claude Code project MCP adds **`minecraft_company_roadmap`** and **`minecraft_next_approved_step`** (after owner approves pending `cinefactory-studio`), enabling it to ask exactly what department produces next, with mandatory receipts and blocking conditions.

### STATUS thực
- Whole-company research and 28-step task plans registered with real source metadata.
- Actual full video/audio competitor breakdown: **NOT VERIFIED**.
- 45s real media: **NOT PRODUCED**.
- Maizen-game actual in-game capture: **NOT QUALIFIED**.
- 2s historical original Blender video is real, but fails 12 art gates.
- No third-party software, cloud model, paid MCP automatically used/installed, no upload, no production release.
