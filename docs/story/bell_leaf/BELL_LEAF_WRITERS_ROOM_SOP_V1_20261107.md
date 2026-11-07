# CINE BELL & LEAF — QUY TRÌNH PHÒNG BIÊN KỊCH / EPISODE WRITER SOP V1
Version: 2026-11-07. Thuộc niche slow_english_a2, series Bell & Leaf ONLY. Áp dụng cho AI writer, story editor, showrunner, director, dialogue/A2 reviewer, script supervisor, research, asset & production QC. Không nhập rule từ ngách audio/senior hay A2 generic.

## A. Điểm vào DUY NHẤT
1. Đọc docs/story/bell_leaf/BELL_LEAF_WRITERS_ROOM_CANON_CONTRACT_V1_20261107.md.
2. Đọc config/niches/slow_english_a2/bell_leaf_writer_contract_v1.json và docs/story/bell_leaf/BELL_LEAF_OWNER_SOURCE_CONFLICT_REGISTER_20261107.md.
3. Đọc story hiện hành docs/story/bell_leaf/BELL_LEAF_CANON_CURRENT.md CHỈ khi không mâu thuẫn với nguồn chủ sở hữu đã chốt; ưu tiên bản nguồn trong data/story/bell_leaf/owner_sources_private/20261107 trên máy owner. Không có bốn nguồn ở môi trường GitHub clone = không được tự suy diễn phần riêng tư; bảo lưu REVIEW_REQUIRED.
4. Với ảnh/voice, truy manifest khóa ảnh v2 (nếu có dữ liệu và SHA), voice registry thật (0 master approved khi chưa duyệt). Không gán ảnh/giọng bằng tên na ná.
5. Đọc continuation ledger của tập trước; nếu chưa có ledger thì draft trong trạng thái CONTINUITY_PENDING, không ghi như bản chính thức.

## B. Phân vai và luồng duyệt
- RESEARCH: ghi quan sát đối thủ có URL/ngày/view/source, tách OBSERVED vs INFERRED; không nhập nhân vật/plot của đối thủ vào sáng tác. Thiếu research không được bịa số liệu.
- SHOWRUNNER: đặt season arc, nêu bí mật/reveal levels có quyền, duyệt mục tiêu EP và phạm vi khác biệt. Chỉ showrunner được xem nguồn spoiler private trên máy owner; không gửi toàn bộ vào API/provider prompt.
- STORY EDITOR: kiểm tra nhân quả, foreshadow/payoff, tinh thần bộ phim, biến đổi nhân vật, variety, continuity.
- WRITER: viết bản gốc tiếng Anh A2 có hành động và cảm xúc; tạo treatment, outline, full screenplay, dialog, shot cards bằng các gate.
- SCRIPT SUPERVISOR: kiểm nhật ký thế giới/quan hệ/nhân vật/thời gian/đồ vật; không hợp thức hóa một plot hole bằng câu thoại.
- A2 DIALOGUE EDITOR: kiểm tính tự nhiên, phát âm, tốc độ, cụm từ quen thuộc, ngữ cảnh dễ hiểu, ngôn ngữ gần gũi; tránh câu dài văn học hoặc thoại như sách giáo khoa.
- DIRECTOR/ASSET/QC: chuyển shot thành một take 10s, chứng minh Canon/source tags và locations, chỉ tiếp tục nếu đủ tài sản được duyệt.

## C. Pipeline 12 bước và gate
01. EP PITCH: tiêu đề làm việc, loại bối cảnh old/new/earth/mixed, khán giả biết gì, hook đầu 45s, main goal, 1 câu pay-off, continuity impact.
02. SOURCE CROSSWALK: liên kết tối thiểu 3 rule IDs từ owner canon, kiểm route, trigger, Earth ecology, các nhân vật/timeline, tình trạng villain knowledge. Mâu thuẫn -> BLOCKED_OWNER_DECISION_REQUIRED.
03. EPISODE VARIETY: so với 10–20 tập gần nhất: POV, thế giới, genre, conflict, emotion, twist, đối thủ, vật thể, ending. Không tái diễn "Orin gọi -> portal -> rescue -> ASH-BELL".
04. STORY CONFERENCE: ít nhất 2 phương án giải quyết xung đột và cái giá thật; có tư duy độc lập của người dân địa phương, không "phép mạnh nhất xuất hiện" ngoài luật.
05. TREATMENT 2–5 trang: mở đầu, động cơ, hành động, major turns, midpoint deception có chứng cứ, escalation, climax, emotional close, series clue optional.
06. BEAT OUTLINE ~45–46 phút: 0:00–0:45 hook; 0:45–6:30 mục tiêu; 6:30–14:00 thử nghiệm; 14:00–23:00 đảo chiều có gieo mầm; 23:00–32:00 cái giá/khủng hoảng; 32:00–41:00 giải quyết chủ động; 41:00–46:00 payoff/dư âm. Gợi ý chứ không ép phút y hệt. Mọi phút có action/agency, không padding.
07. SCREENPLAY: screenplay tiếng Anh General American A2 40–50 phút với từng scene ID, INT/EXT, nơi, thời gian, continuity state, action observable, speaker tag, dialogue, emotion/acting/SFX cue. Không đánh đồng treatment với screenplay.
08. SCRIPT DOCTOR: lập bảng setup/payoff, 3 câu hỏi nhân quả (tại sao bây giờ, tại sao nhân vật này, vì sao phương án khác không hoạt động), 2 lần đọc độc lập, chống tình tiết tiện lợi.
09. A2 LISTEN & LEGAL: kiểm câu A2, tuổi giọng, tên đọc rõ, không mô phỏng thoại/nhân vật đối thủ; nhạc/giọng/nhân vật phụ phải đủ quyền và được duyệt.
10. SHOT BREAKDOWN: 1 shot = 10 giây liên tục, kế hoạch 24fps 240 frames, lens/camera motivated, frame0, movement thực, action rõ, micro-expression, blocking, source active tags. Tổng số shot thực phải dựa trên runtime; 45 phút xấp xỉ 270 shot CHỈ NẾU mọi shot 10s; không tuyên bố đã dựng.
11. FLOW + MUSE: hai pack tách biệt. EXACT mỗi shot là 1 DÒNG duy nhất, sau mỗi shot 1 dòng TRỐNG; có "ACTIVE TAGS FOR THIS SHOT: [..]" kể cả [] và không upload refs khi []. Flow 16:9 SINGLE image, neutral D55, no yellow cast/no grid/no captions/no unknown faces; Muse 10s animated character performance + authorized speech & lip sync + SFX, no fake digital zoom-only shot. FULL và COMPACT 2500 chars là hai bản phục vụ mục đích khác nhau.
12. RELEASE GATES: story approved != images approved != voice approved != Muse true I2V approved != public upload approved. Sha-bound refs, source WAV cues, frames, motion, mouth and face checks, reviewer sign-off; fake FFmpeg test chỉ chứng minh container kỹ thuật, không chốt QC.

## D. Yêu cầu đầu ra bắt buộc cho MỖI tập
- PROJECT_ID: slow_english_a2 / SERIES_ID: bell_leaf / EP_ID (unique).
- SOURCE_CANON_VERSION & hashes; auth status for 4 owner docs (local refs must exist to claim FULL_SOURCE_VERIFIED).
- Episode pitch & reason viewers care; conflict and specific non-magic alternative blocked by causal evidence.
- Exactly who is speaking and which approved speaker tag; relationship, information state, location & gate state.
- Writer's beat sheet (time/goal/action/obstacle/reversal/evidence); full English screenplay with scene IDs and duration estimate.
- Visual shot list, 10s per shot with active tags, approved references + optional empty tags for landscapes; no group reference for per-character first-frame.
- Setup/payoff ledger with real clues and later payoffs; continuity delta + rolling mysteries/rescues/world state.
- Art/voice/rights blockers enumerated separately; do not invent APPROVED.
- Two reviewer records (story logic / A2 naturalness); owner approval for any Canon deviation.
- Public/no-spoiler export distinct from private authorized showrunner notes.

## E. Mẫu thẻ SCENE / SHOT
EP: BL-EP####; SCENE: SC-###; TIME: relative; LOCATION_ID: approved or PENDING; WORLD_STATUS: OLD/NEW/EARTH; GATE_PATH: STATION/BUBU/NO_GATE; PHYSICAL CAUSE OF ENTRY/EXIT: ...; CHARACTERS: [official tags]; PRIOR_KNOWLEDGE: ...; AFTER_KNOWLEDGE: ...; GOAL: ...; OBSTACLE: ...; ACTION VISIBLE: ...; EMOTION/COMEDY: ...; SPEAKER_TAG: ...; GENERAL AMERICAN A2 LINE: ...; CLUE/SETUP: ...; PAYOFF: ...; NEW FACT/DELTA: ...; IMAGE_REF_SHA: ...; AUDIO_REF_SHA: ...; CANON_RULE_IDS: ...; SOURCE_APPROVAL: ... .
A shot without enough approved source assets can be storyboarded as TEXT but must remain ASSET_BLOCKED and not distributed as valid production prompt.

## F. Cảnh báo cần kiểm riêng
- Evan's initial awareness: do not depict him knowingly operating magic before a scripted and approved reveal.
- Bubu is not a free teleport, cannot rescue hundreds at once, has one necklace bell plus permanent spiral tail sparkle.
- Do not show Orin instant-calling from any realm without a valid resonance route. A signal is not a physical passage.
- Earth fixed station does not predate Orin/Mara; no compulsory personal bell.
- Environmental magic specialization cannot heal the fundamental living current by itself.
- Do not confuse original slow English / generic A2 packages with this Bell & Leaf source and analytics baseline.
- Do not use 36 world candidates or new Aila/Tali/unnamed antagonist faces as if owner-approved asset refs.
- Do not leak private villain identity or final solution into GitHub/public prompts.
- Do not mass-produce 1,000 episodes from a single repeated template; approve one pilot first.

## G. Quy trình đề xuất sửa Canon
Tạo Change Request có: exact source quote, old rule, new rule, reason, affected EP/characters/assets, potential retcon, 2 independent reviews, explicit owner confirmation, decision ID. Không có owner confirmation = NO_CANON_MUTATION. Sau duyệt mới thay asset/scene/shot hashes và kiểm lại continuity. Gửi bản trước/sau để owner nhìn rõ.
