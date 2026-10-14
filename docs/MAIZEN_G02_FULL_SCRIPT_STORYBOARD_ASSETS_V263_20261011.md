# CineFactory v263 — G02 recheck, 14-minute production screenplay, full storyboard & original voxel assets
Ngày: 11/10/2026. Dự án: `MAI01_WATERFALL` — **Nova & Pip: The Secret Below the Waterfall**.

## Kết luận trạng thái có bằng chứng

**Mục tiêu kỹ thuật và tiền kỳ đã thực hiện:**
- **11/11** cửa sổ nguồn bị gắn cờ v262 được mở lại trên video YouTube gốc bằng Chrome, **tốc độ 1×**. Tất cả 11 âm thanh Opus thu lại đều decode PASS, hash khớp, thu thêm 142 ảnh (các cửa sổ ngắn cuối video có ít ảnh hơn). Tổng âm thanh thu lại ~4,433,557 bytes. Bằng chứng ở `.tools/maizen_1x_window_recheck_v263/`.
- Tổng hồ sơ kiểm định G02: 3 video gốc, 95 file âm thanh từ lượt phát trước đều decode được, **120 cửa sổ ≤30 giây**, 463 ảnh mẫu trước đó, 11 cửa sổ được bổ sung bằng ảnh dày hơn và audio gốc 1×.
- Kịch bản nguyên bản **14:00 = 840 giây, 21 beat, 82 shot liên tiếp không trùng/chồng thời gian**. Mỗi shot có thời gian, địa điểm, động tác, camera, lời thoại tiếng Anh hoặc beat không thoại, âm thanh dự kiến, tham chiếu assets và trạng thái continuity. Gắn phiên bản nguồn; không cho phép chỉnh bản gốc v243 âm thầm.
- Storyboard **đủ 82 shot trên toàn bộ 14 phút**, mỗi shot có PNG 1280×720 và SVG chỉnh sửa được, manifest liên kết timecode/camera/scene/asset. Đồng thời giữ 9 khung thử nghiệm đầu đã sửa ở v262 và bảy contact-sheet xem nhanh.
- **27 asset 3D nguyên bản** ở dạng OBJ+MTL (109 bộ phận, 872 vertices), gồm hai nhân vật voxel mẫu NOVA/PIP, waterfall/river ridge, bridge, map, stone crossing, cửa mật mã, hidden falsewall, crystal, valve, reset panel, drain, relief-channel, hatch, grate, hook, tools, props. Tất cả tên asset được 82 shot tham chiếu đã kiểm tra có trong manifest. Gói ZIP importable đối chiếu CRC/tệp đọc PASS.

**Điều TUYỆT ĐỐI chưa hoàn tất và không được đánh tráo:**
- **G02 = BLOCKED_INDEPENDENT_1X_NATIVE_AV_SEMANTIC_SIGNOFF**. Bằng chứng kỹ thuật source 1×, hash, audio decode, ảnh, subtitle **không tương đương** một người/đơn vị kiểm duyệt độc lập đã xem liên tục chuyển động và nghe trọn vẹn lời thoại, tiếng động, nhạc của cả 3 video. 120 cửa sổ vẫn cần đối chiếu chi tiết bằng audio/video và chữ ký người kiểm định đủ điều kiện. Không tự cấp giấy nghiệm thu G02.
- Storyboard là **bản phác nguyên bản cho đạo diễn**, không phải frame dựng phim, animatic có chuyển động, footage hay render.
- 27 OBJ là **3D static blockout** để mở trong Blender/Blockbench/3D editor tương thích, không phải nhân vật đã rig, biểu cảm/lip sync, UV texture chuyên nghiệp, cảnh đã ánh sáng/render hoặc asset thương mại đã duyệt similarity/legal QC.
- Kịch bản là **bản nháp đầy đủ theo thời gian để editorial review**, chưa qua thu giọng thật, rehearsal, script lock hay nghiệm thu phim. Cần test giọng/nhịp ở tốc độ tự nhiên và điều chỉnh thoại trước 3D animation.
- Quyền dùng runtime Minecraft và mọi bộ âm thanh/đồ họa ngoài asset nguyên bản **chưa chứng thực**. Không sử dụng nhân vật/giọng/skin/logo Maizen, JJ & Mikey, Spider-Man, Pokémon, hình ảnh hay file phim đối thủ trong sản phẩm.
- G16–G28 **HOLD**, chưa render video 45 giây hay 14 phút, chưa upload, chưa trả credits API.

## Tài liệu/hồ sơ có thể dùng ngay trên máy
Đường dẫn repo:
`C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6`

| Hạng mục | Đường dẫn dưới root |
|---|---|
| **Bộ tiền kỳ đầy đủ ZIP** | `data/verification/v263_maizen_full_story_assets/nova_pip_full_14min_preproduction_v263.zip` |
| Kịch bản đọc bình thường | `data/verification/v263_maizen_full_story_assets/nova_pip_14min_screenplay.md` |
| Kịch bản shot-by-shot có trạng thái | `data/verification/v263_maizen_full_story_assets/nova_pip_14min_shooting_script.json` |
| EDL cho phòng dựng | `data/verification/v263_maizen_full_story_assets/nova_pip_shot_edl.csv` |
| Storyboard đủ 82 khung & SVG | `data/verification/v263_maizen_full_story_assets/storyboard_full_82_editable.json` và thư mục `storyboard_full/` |
| Storyboard 9 shot pilot 45s | `data/verification/v263_maizen_full_story_assets/storyboard_9shots_editable.json` |
| 27 asset OBJ/MTL | `data/verification/v263_maizen_full_story_assets/original_voxel_asset_registry.json`, thư mục `meshes/` |
| Bảng G02 cho kiểm định viên độc lập | `data/verification/v263_maizen_full_story_assets/g02_independent_review_worklist.md` |
| Bằng chứng 11 bản audio thu ở tốc độ 1× | `.tools/maizen_1x_window_recheck_v263/` (**giữ private; không gói vào ZIP**) |

## Công đoạn tiếp theo để đạt điều kiện triển khai phim

1. **G02:** Cử người độc lập kiểm định toàn bộ 3 phim gốc ở tốc độ tự nhiên, hoàn thiện 120 phiếu nghe–nhìn theo timecode và xác nhận chi tiết thoại, diễn biến, camera, FX, nhạc; nếu thiếu bằng chứng, không ký. Bộ máy đã thu lại 11/11 đoạn kỹ thuật; hoạt động kiểm định vẫn chưa đạt.
2. **Writers/Director:** Duyệt bản screenplay 82 shot, thu voice scratch nguyên bản để test nhịp thực tế, chỉnh thoại, chuyển storyboard SVG sang animatic 45 giây có motion và audio; tránh nghĩ 82 bảng tĩnh là phim.
3. **Assets/Technology:** Dựa trên 27 blockout, thực hiện rig + emotions + sound/event sockets, UV/texture, world/gameplay runtime hợp lệ, QA camera/continuity; benchmark cảnh giống nhau bằng Blender worker vs runtime gameplay; đo accepted-seconds/hour và VRAM, chưa giả hiệu năng.
4. **Owner approval & QC:** Chỉ sau bằng chứng G02, quyền asset/runtime, script-lock và media gate mới cho phép render/đăng nội dung.

## Quy tắc vận hành dài hạn
Nhánh A/B/C/D tiếp tục quét đối thủ cũ/mới và video outlier hàng ngày. Các kết luận ngành phải có nguồn, thời điểm, mức tin cậy; giả thuyết trend ngắn hạn không tự trở thành production rules. **Không chấm đạt G02 vì test kỹ thuật PASS hoặc vì đã tạo tệp.**
