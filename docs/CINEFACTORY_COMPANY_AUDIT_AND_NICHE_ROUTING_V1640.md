# CINEFACTORY OS v1.6.40 — Kiểm toán thực trạng toàn công ty và cách ly nghiên cứu theo ngách

**Ngày kiểm tra:** 2026-10-09 (máy Windows DESKTOP-HJE6A6D).  
**Repository gốc:** `C:\Users\ADMIN\Downloads\CineFactory_Autonomous_Build\cinefactory-os-v1.6\cinefactory-os-v1.6`.  
**Git:** branch `studio/v1.6.6-universal-company`, HEAD `44e1f5f`; working tree có nhiều thay đổi cũ; không reset, không commit, không deploy.  
**Bằng chứng máy đọc trực tiếp:** `data/research/youtube_breakout/company_structure_audit_v200.json`.

## I. Phân biệt giữa cấu trúc và hoạt động thực tế

- 26 `DepartmentId` được đặt tên. **Chỉ 15** trong `DEFAULT_DEPARTMENTS` có đặc tả đầy đủ mission/knowledge/skills/tool/read/write/QC. Một `RD_KNOWLEDGE` được kế thừa từ RND, thành **16** khi khởi tạo registry. Những bộ phận còn lại chủ yếu xuất hiện trong workflow, module chuyên ngành hoặc quyền quyết định; không có chứng cứ 26 agent độc lập đang chủ động làm việc.
- **11 công năng quản trị cấp công ty** `CompanyFunctionRegistry`: Executive Strategy, Finance/Investment, Legal/Business Affairs, People/Talent/Training, Marketing/Publicity, Procurement/Vendor, Risk/Internal Audit, YouTube Growth & SEO, Data Analytics, Technology Platform, Knowledge R&D.
- **30 stage handler được đăng ký** bởi `FilmCompanyHandlers(...).registry()` trên `build_context(root)` hiện tại.
- Workflow animation chuyên nghiệp có **32 stage**, còn thiếu **EVIDENCE** và **VOICE_PREP** là required nhưng không có handler mặc định. EVIDENCE cố ý fail-closed (không âm thầm xác minh thông tin); VOICE_PREP được đăng ký có điều kiện khi TTS/voice được cấu hình. Workflow gameplay (cũng 32 stage trên blueprint) thiếu EVIDENCE nếu yêu cầu fact-check.
- `FilmHandlerConfig.production_mode` **mặc định = slate**, `allow_diagnostic_slate=True`. Đây là chế độ tạo/kiểm tra slate chẩn đoán không thay thế điều kiện nghiệm thu video thật. Phần mã không mặc định chứng minh rằng một nút sản xuất media thật đã chạy được.
- Studio runtime `build_studio_kernel` có registry/sổ tri thức/blackboard/chỉ huy/QA/công cụ/handoff/sự cố/rule/tracing; đây là framework chứ không phải nhân viên AI 24/7.

## II. Sơ đồ quản trị — 11 phòng ban cấp công ty

| Bộ phận | Chức năng chính | Quyền/quyết định quan trọng |
|---|---|---|
| Chiến lược điều hành | Danh mục ngách, đánh giá cơ hội, phân bổ nguồn lực | GREENLIGHT danh mục |
| Tài chính/đầu tư | Kế hoạch ngân sách, GPU/chi phí/đơn vị video đã duyệt | BUDGET & ECONOMICS |
| Pháp lý/quyền | Giấy phép phần mềm, model, assets, giọng nói, âm nhạc, quyền thương mại | RIGHTS CLEARANCE |
| Nhân sự/đào tạo | Chuẩn vai trò, kỹ năng, kiểm tra năng lực, gap | ROLE & SKILL READINESS |
| Marketing/PR | Định vị thương hiệu, chiến dịch và phát hành | BRAND/RELEASE ALIGNMENT |
| Mua sắm/vendor | So sánh tool, hợp đồng dịch vụ, lock-in, phương án thay thế | PROCUREMENT CLEARANCE |
| Kiểm toán nội bộ | Kiểm soát traceability, rủi ro hệ thống, continuity | INTERNAL CONTROL |
| YouTube Growth & SEO | Khán giả, tìm kiếm, bao bì thumbnail/title, retention giả thuyết | DISCOVERY & PACKAGING |
| Phân tích dữ liệu | Chất lượng data, định nghĩa view/growth/CTR, attribution | DATA QUALITY |
| Công nghệ nền tảng | GPU/CPU, worker, hàng đợi, lưu trữ, log, SLO và sao lưu | PLATFORM READINESS |
| Tri thức/R&D | Nguồn chính thống, paper/repo, thử nghiệm, quảng bá tool sau QC | KNOWLEDGE PROMOTION |

**Trạng thái:** hồ sơ vai trò, policy, authority và phần module có thật. Điều này **không** đảm bảo mỗi bộ phận có AI agent, dữ liệu đầu vào, chi phí và workflow production đã được chứng minh.

## III. 26 vai trò/phòng ban Studio (15 có đặc tả chuyên nghiệp mặc định)

| Vai trò | Chức năng công ty thực hiện hoặc mô tả | Trạng thái trong source |
|---|---|---|
| STUDIO_MANAGEMENT | Điều phối, phê duyệt dự án và xuất bản | Có owner/gate, chưa có spec kiểu `DEFAULT_DEPARTMENTS` |
| INTELLIGENCE | Nghiên cứu thị trường/đối thủ/ngách/định dạng/video | Có spec và handler; video đầy đủ chưa tự xem được |
| EVIDENCE | Fact-check, độ tin cậy, claim/source/đối chiếu | Có spec, **required handler mặc định thiếu** |
| CREATIVE_STRATEGY | Positioning, USP, format DNA, series bible | Có spec và handler |
| PLANNING | Lập chiến lược sản xuất, resource, fallback, chọn tool | Có spec và handler |
| WRITERS_ROOM | Original plot/beat/storyboard script/lời thoại | Có spec và handler |
| SCRIPT_LOGIC | Kiểm tra causality, state, character continuity | Có spec và handler |
| DIRECTION | Cảm xúc, mục đích scene, blocking, đạo diễn | Có spec và handler |
| PERFORMANCE | Diễn xuất, gaze, gesture, emotion, reaction timing | Có spec và handler |
| CINEMATOGRAPHY | Shot book, lens, camera, lighting, eyeline | Có spec và handler |
| PRODUCTION_DESIGN | Original visual bible, nhân vật/đạo cụ/cảnh/materials | Có spec và handler |
| ASSETS | Rig, world, props, skin, nguồn asset, quản trị reuse | Có owner ASSET_BUILD, chưa có spec độc lập |
| TECHNICAL_DIRECTION | Chọn backend, GPU/VRAM, preflight, sản xuất scene | Có spec và handler |
| PRODUCTION | Animation/render/gameplay/capture chạy worker | Có handler có điều kiện; chất lượng mỗi ngách chưa certified |
| GENERATIVE_MEDIA | Image/video generation khi phù hợp | Có enum/capability, chưa có spec chuyên biệt mặc định |
| VFX | Hiệu ứng, compositing | Có enum nhưng chưa có spec độc lập mặc định |
| EDITORIAL | EDL, nhịp dựng, continuity, rough/final cuts | Có spec và handler |
| AUDIO | Original voice/TTS, Foley, SFX, music, mix/master | Có spec và handler; voice prep phụ thuộc cấu hình |
| COLOR | Color pipeline, grading, look consistency | Owner FINISHING; chưa có default spec độc lập |
| QC | Kỹ thuật/hình/âm thanh/nội dung/continuity/rights | Có spec và handler |
| RIGHTS | Bản quyền, content originality, phê duyệt assets | Có authority/corporate function, không có core dept spec riêng |
| PACKAGING | Thumbnail, title, description, release/SEO | Có owner/handler; chưa có spec mặc định |
| ANALYTICS | YouTube hiệu quả, retention/CTR/quan sát/học tập | Có stage/management function; chưa có spec mặc định |
| RND | Công cụ/repo/paper, benchmark, skill, regression | Có spec |
| RD_KNOWLEDGE | Tri thức R&D, rule học tập versioned | Spec kế thừa RND |
| OPERATIONS | Resource scheduling, queue, failure recovery | Có scheduler/service/module, chưa có spec mặc định |

## IV. Pipeline end-to-end (ví dụ Animation, 32 stage)

Nhóm A — Đầu tư và nghiên cứu: **PROJECT_INTAKE → PORTFOLIO_GREENLIGHT → INTELLIGENCE → EVIDENCE → CORPORATE_PREFLIGHT**.

Nhóm B — Sáng tạo: **CREATIVE_STRATEGY → CREATIVE_DEVELOPMENT → PLANNING → WRITING → STORY_ARCHITECTURE → SCRIPT_REVIEW → LOGIC → DIRECTOR_TREATMENT → DIRECTION**.

Nhóm C — Thiết kế và tiền kỳ: **PERFORMANCE → PRODUCTION_DESIGN → CINEMATOGRAPHY → STORYBOARD_EDITORIAL → CRAFT_EXECUTION_DESIGN → LAYOUT_TECHVIS → CREATIVE_REVIEW → ASSET_BUILD → VOICE_PREP → PREVIS**.

Nhóm D — Sản xuất & nghiệm thu: **TECHNICAL_DIRECTION → PRODUCTION → EDITORIAL → AUDIO → FINISHING → FINAL_QC → PACKAGING → ANALYTICS_LEARNING**.

Các stage tham chiếu metadata/gates trong `cinefactory/studio/company.py`, thực thi qua `cinefactory/studio/company_runner.py` và `cinefactory/studio/company_handlers.py`. Mã có cơ chế ledger, resume, fail-closed khi không có handler và repair tickets. **Không nên suy ra toàn bộ pipeline đã xuất video thương mại liên tục chỉ từ sự tồn tại của 30 handler**.

## V. Các ngách thực tế — 3 lớp không trùng nhau

**7 ngách `ACTIVE_CORE` có thư mục config:** minecraft, roblox_animation, long_slices_game, asmr_sleep_hands_objects, audio_storytelling_seniors, fishing_silent, rain_sleep_white_noise.

**13 bản thiết kế `NICHE_BLUEPRINTS`:** các ngách trên cộng preschool_3d_musical (kiểu hoạt hình 3D có nhạc nguyên bản), animal_animation, gta_gameplay, ai_family_drama, 2d_cartoon, daily_english.

**14 format tìm kiếm:** tách Minecraft thành `minecraft_gameplay` (Maizen) và `minecraft_animation` (BigSchool), cộng 12 nhóm format còn lại.

**Lỗ hổng quan trọng:** tất cả 7 `config/niches/<id>/competitors.yaml` chứa các danh sách rỗng, đồng thời `NicheRegistry` của 7 ngách chưa có competitor, keyword, approved recipes/rules. Những video lịch sử đã quét nằm trong SQLite chứ chưa đủ chứng cứ để biến thành `competitor_ready` thật. Không tự điền nguồn thô vào `competitors.yaml` bởi `NicheConfigStore.readiness()` sẽ coi **bất kỳ dữ liệu không rỗng** là tín hiệu ready, không yêu cầu độc lập kiểm chứng chất lượng; như vậy có nguy cơ greenlight sai.

## VI. Sửa thật trong v1.6.40 — per-niche source routing

- `cinefactory/studio/niche_competitor_guard_v200.py`: 14 format, ánh xạ 13 blueprint, kiểm tra biểu thức ngữ nghĩa tối thiểu từ title và định dạng, từ chối tutorial, sai ngách, mơ hồ, trộn Minecraft gameplay/animation; ngách không có bằng chứng được trả UNKNOWN, không lấy video ngách khác vào.
- `cinefactory/studio/daily_youtube_breakout_v199.py`: tích hợp gate trước khi ingest vào SQLite/auto-follow; metadata title chỉ tạo **research candidate**, tuyệt đối không tạo verified rival/production approval.
- `scripts/run_daily_cinefactory_youtube_v199.py`: tạo hồ sơ JSON riêng trong `data/research/youtube_breakout/niches/<niche_id>/source_runN.json`, báo cáo Markdown phân chia theo ngách và Claude Code JSON packet cũng chia theo 13 ngách.
- `tests/test_niche_competitor_guard_v200.py` và `tests/test_daily_youtube_breakout_v199.py`: xác nhận 14 format và cách ly các kết quả cross-format.
- Thử live thực 2026-10-09: 14 queries, 20 metadata fetch, **2** title-screened candidates, **4** cách ly vì không chứng minh đúng ngách, **2** nguồn lỗi. 13 hồ sơ trên disk. Đây là **source-limited title admission**, chưa phải computer vision phân loại 100% chính xác, chưa xem video đầy đủ, chưa chứng minh mọi video hot.

## VII. Khả năng phần mềm đang có thật

- Blender 4.5.14 LTS, FFmpeg 7.1, Python và Node/npm hiện có. Blender render video thật, nhưng benchmark v196 chỉ 2 giây/480x270; pilot v197 2 giây/960x540 chưa đủ chuẩn nghệ thuật và còn 12 blockers.
- Thư mục `.tools/ComfyUI` tồn tại, chưa chứng minh được workflow video/weights/VRAM/giấy phép output.
- Godot, OpenToonz, OBS (PATH), LMMS, Audacity không xuất hiện trong kiểm tra PATH; đó không phải bằng chứng toàn hệ điều hành không cài.
- Claude Code 2.1.220 cài, nhưng phiên Remote shell `claude auth status` không cho thấy kết nối hợp lệ. Không có Claude agent đang tự đọc packet, suy luận và trả công việc vào CineFactory hàng ngày.
- Windows Task Scheduler `CineFactory-Daily-YouTube-Research` trạng thái Ready, 08:00 ngày tiếp theo, LogonType Interactive. Chạy 14 lane query, giới hạn 20 metadata/ngày; không phải cloud 24/7.

## VIII. Ưu tiên nâng cấp thực

**P0 — Người chủ R&D ngách:** Từng `niche_id` phải có own seed channels/format fingerprint/negative examples, đối thủ lớn & kênh mới, chính sách search/retention, source freshness; mỗi video được xét như một format riêng. `competitors.yaml` chỉ được greenlight sau khi qua video/rights/quality review, không chỉ nonempty.

**P0 — Đóng khoảng cách 13 blueprint vs 7 registry:** Thêm 6 ngách vào `NicheRegistry` ở trạng thái `INCUBATING`, tạo đủ SOP và fixtures, không tự kích hoạt sản xuất khi chưa phê duyệt.

**P0 — Thực sự học video:** Fetch và xem nội dung hợp lệ khi accessible hoặc bằng authorized provider; không biến storyboard sparse thành nghe tiếng, biết animation/rig/timing. Bổ sung transcript/shot/character/angle annotations có nguồn đầy đủ, no copying.

**P0 — Gắn Claude Code thật:** Xác thực tài khoản hợp lệ dưới quyền người dùng và chính sách ngân sách rồi mới bật headless review, output JSON hợp lệ, tranh luận đa phòng ban, source audit, no execution/free arbitrary copy. File handoff không thay thế AI chạy.

**P0 — Đóng required stage handler gaps:** EVIDENCE không thể fail-closed mãi nếu công ty cần sản xuất thực; phải có source-verification handler đúng quyền, không auto-assert true. VOICE_PREP cho Animation phải thử voice/scene config thật.

**P0 — Chứng minh đúng tool/video:** Minecraft gameplay Minecraft runtime + capture; Minecraft animated story Blockbench/Blender/asset+rig+camera; Long Slide game simulation; preschool musical original 3D organic rig+music+cơ chế child-safety. Actual VRAM/cost per accepted minute/human quality gates bắt buộc.

**P1 — Vòng lặp tăng trưởng:** Theo dõi view delta theo ngày, source/creator age, title/thumb experimentation cho video gốc, authorized channel Analytics CTR/retention và feedback để chọn thử nghiệm kế tiếp. Không bảo đảm triệu view.

**Không có phần mềm nào bảo đảm video hot hay hàng triệu lượt xem.** Tài liệu này kiểm toán hiện trạng thật, không chứng nhận công ty đã đạt chất lượng Disney hoặc tự tạo phim toàn diện.


## Kết quả nghiệm thu cuối, 2026-10-09

- Full regression **1005 / 1005 PASS, 0 failed, 143.40s**, log `data/research/youtube_breakout/logs/regression_v200.txt`.
- Biên dịch `python -m compileall -q cinefactory scripts tests`: PASS. Tracked diff check PASS.
- Bộ kiểm thử chuyên biệt v200 và v199: **62 / 62 PASS**.
- Live source validation: 14 format queries, 20 detailed watch metadata checks, **2** format-qualified title-level Minecraft gameplay leads, **4** quarantined not format-evidenced, **2** source failures; actual multimedia review on this scan = NONE. 13 separate per-niche JSON reports saved (including empty research evidence).
- Machine inspection via Windows: Task Scheduler task Ready, scheduled 2026-10-10 08:00 +07:00, its LastRunTime is the default 1999-11-30 sentinel so this specific new Windows task has not independently run itself yet; preceding successful scans were triggered manually. No listener was found for configured API port 8765. One CineFactory-related Python process appeared but its runtime functionality has not been certified by this inspection.
- Git commit remained `44e1f5f`, branch `studio/v1.6.6-universal-company`; existing dirty worktree retained. No commit, reset, clean, deployment, paid LLM call, channel publishing or automatic production promotion.
