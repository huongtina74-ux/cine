# CINE / Bell & Leaf — Memory Hub v1 (2026-11-08)

**Mục tiêu:** Không còn phụ thuộc vào “ChatGPT nhớ chuyện gì”. Mỗi lần CINE viết, kiểm duyệt hay sản xuất, agent phải **nạp đúng nguồn** của series, tập, cảnh, shot, character/location Bible và đúng các Skills hiện có. Các tài liệu gốc không bị sao chép thành nhiều bản Canon.

## Năm tầng, mỗi tầng một nguồn chuẩn

| Lớp | Nguồn dữ liệu thực tế | Vai trò |
|---|---|---|
| 1. Series / showrunner | `docs/story/bell_leaf/BELL_LEAF_CANON_CURRENT.md`, owner contract, bản gốc bí mật cục bộ | Luật thế giới, hồi phục phép, tuyến dài hạn và bí mật chỉ showrunner đọc |
| 2. Nhân vật | `config/niches/slow_english_a2/CHARACTER_VISUAL_CANON_LOCK_CURRENT.json`, `VOICE_BIBLE_CURRENT.md` | Tags, khuôn mặt/cơ thể từ ảnh chủ, vai trò/tri thức, voices riêng |
| 3. Địa điểm / đạo cụ | `config/niches/slow_english_a2/OWNER_VISUAL_REFERENCE_BIBLE_20261108.json` + `cine-bellfern-location-multiview-lock` | Ảnh nguồn, SHA, góc đã có, quy tắc hình học, góc còn thiếu |
| 4. Tập / continuity | `EPISODE_STORY_MEMORY_INDEX_V1.json`, `EP001_STORY_V2_CONTINUITY_LOCK.json`, treatment 30 cảnh | 30 tình tiết đã xảy ra, trạng thái đầu/cuối, bí ẩn chưa giải, chống lặp |
| 5. Cảnh và shot | EP001 v2 `scene_cards` và `EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json` | Scene có 9 slot; shot có *cast thực sự xuất hiện*, ảnh mặt/hero và bối cảnh. V1.1 shot binding là **DRAFT** cần đối chiếu lại với v2 |

**Chỉ mục trung tâm (link, không sao chép Canon):** `config/series/bell_leaf/memory_manifest_v1.json`.

**Công cụ nạp bộ nhớ:** `tools/bell_leaf/story_memory_resolver.py`.

**Skill vào cửa:** `.claude/skills/cine-bell-leaf-memory-hub/SKILL.md` và `.agents/skills/cine-bell-leaf-memory-hub/SKILL.md`.

## Cách dùng thực tế

Từ thư mục gốc CineFactory (Windows), chỉ xác minh cấu trúc trước khi viết:

```powershell
python tools/bell_leaf/story_memory_resolver.py --episode BL-0001 --stage story --verify
python tools/bell_leaf/story_memory_resolver.py --episode BL-0001 --stage image --shot S001 --verify
```

Nạp toàn bộ 30 cảnh, Canon, trạng thái và các luật chống lặp cho người viết:

```powershell
python tools/bell_leaf/story_memory_resolver.py --episode BL-0001 --stage story --out data/story_quality/BL0001_story_context_draft.json
```

Nạp ngữ cảnh shot S001, chỉ nhân vật **BIX + MARA**, không lấy tất cả 6 nhân vật thuộc SC-001:

```powershell
python tools/bell_leaf/story_memory_resolver.py --episode BL-0001 --stage image --shot S001 --out data/story_quality/BL0001_S001_image_context_draft.json
```

Bắt đầu viết tập mới dựa trên những gì đã xảy ra trong tập trước:

```powershell
python tools/bell_leaf/story_memory_resolver.py --episode BL-0002 --stage next --out data/story_quality/BL0002_previous_story_context_draft.json
```

Công cụ từ chối ghi đè file context đã có. Tạo tên mới cho lần chạy tiếp theo hoặc chuyển phiên bản cũ sang kho lưu trữ có kiểm soát.

## Những quy tắc bắt buộc

1. **Không dùng Story Bible v4.8 để thay thế 4 văn bản chủ sở hữu mới hơn.** Bộ bí mật phản diện giữ trên máy, không phát tán vào GitHub/ảnh/video/prompts. Public context chỉ có tóm tắt được phép dùng.
2. **EP001 v2 là nguồn nội dung 30 cảnh**, nhưng chưa được duyệt đầy đủ 270 shot v2. Bản quay 270 shot v1.1 là lịch sử, không được lấy làm script sản xuất cuối.
3. **Tập sau kế thừa trạng thái đã xảy ra:** Evan/Arthur/Rose chưa biết phép, Elara và em gái Aila còn mất tích, trạm Earth offline, tín hiệu đá xanh không có tọa độ/cổng mở.
4. **Chống lặp:** kiểm tra 30 sự kiện EP001 và những điều đã được giải quyết. Không “đổi tên vali đồng, thay vải lanh thành vật khác” rồi kể lại cùng một vấn đề như tập mới. EP003 nháp “Aila's Flying Suitcase” phải làm lại xung đột.
5. **Nhân vật:** chín nhân vật chính có asset nguồn; Aila chưa được duyệt face/WAV; không có quyền tự gán mặt tùy tiện. Bix không có chuông; Bubu có chính xác một chuông vàng và đuôi xoắn tím luôn lấp lánh.
6. **Bối cảnh:** ảnh đơn nguồn có SHA không tự chứng minh các góc reverse/360 độ; không thay vị trí cửa sổ/tủ/bàn; không mirror một góc thành góc ngược.
7. **Không duyệt tự động:** bộ nhớ thành công chỉ cho thấy dữ liệu đúng phiên bản và có nguồn. Approval kịch bản, mặt nhân vật sau gen, lip-sync, cuối tập phải có reviewer/owner thật.
8. **Những bản hợp lệ chưa lưu:** yêu cầu `--stage next` chỉ trả lại trạng thái tập trước để viết pitch, **không khởi tạo hay tự duyệt** tập mới. Muốn đưa tập mới vào index/ledger phải làm theo `docs/CINE_STORY_QUALITY_CONTINUITY_MEMORY_20261108.md`.

## Giao ước Skills

- Research/insights: `cine-per-niche-radar`, `cine-story-insight-transfer`, chỉ dùng nghiên cứu ngách con đúng.
- Story/script: `cine-bell-leaf-writers-room`, `cine-story-quality-memory`, `cine-script-factory` và independent story doctor.
- Image: `cine-bell-leaf-stylized-3d-prompt-director` cùng bộ khóa địa điểm đa góc.
- Video: `cine-a2-muse-reference-anchoring` sau khi ảnh first-frame đã QC, kiểm tra hình động 10 giây thật.

**Cảnh báo GitHub:** Checkout công khai có thể thiếu một số Skills chưa đồng bộ và các PNG Canon private. Resolver sẽ liệt kê `SKILL_FILE_MISSING`, `OWNER_*_MEDIA_UNAVAILABLE_OR_SHA_DRIFT`, `MULTIVIEW_NOT_APPROVED`; không được coi là production PASS. Máy Windows có PNG đúng SHA nhưng vẫn phải xét mặt trong video và approval.

**Không thay thế:** CINE Script Factory 8 giai đoạn, owner ledger append-only, character/room Bibles, và các Skills chuyên khoa. Memory Hub chỉ là *cửa truy xuất* tự động có thể kiểm tra, không phải một “bộ nhớ thứ hai” song song.
