# CINE / Bell & Leaf — Kiểm tra kho 1.000 tập và độ đầy đủ nghiên cứu
Ngày kiểm: 2026-11-07. Phạm vi: slow_english_a2 / magical_witch_family_stories / Bell & Leaf. Trạng thái: FACTUAL AUDIT, NOT PRODUCTION PASS.

## I. Đã nằm trong CINE
- Story: bốn nguyên văn chủ sở hữu 07/11/2026 lưu local trong data/story/bell_leaf/owner_sources_private/20261107/ (gitignored, có cả secret showrunner). Bản công khai dùng Writers' Room Canon Contract, SOP, Conflict Register và visual/voice manifest riêng; không công khai bản secret.
- GitHub main trước audit có 4-file Canon contract/skill/checkpoint qua PR #19 và #20 (commit 9f9ca31).
- Research: config/niches/slow_english_a2/research.yaml khai báo đúng family A2 và tách competitor cohort. config/niches/slow_english_a2/RESEARCH_TO_SCRIPT_INTEGRATION.md có 21 role, 38 dependency, 27 role artifacts. CINE đã có code research intelligence và audit/quality tests.
- Trên máy có data/research/raw/2026-10-15_slow_english_a2.json và danh sách channels TSV cùng ngày: quan sát kênh Slow English chung, chưa phải bằng chứng một cohort Magical Witch Family Stories A2 trực tiếp đầy đủ.

## II. Vừa nhập vào development registry (public, proposal only)
- docs/story/bell_leaf/slates/BELL_LEAF_1000_EPISODE_INDEX_PROPOSAL_20261107.csv = 1000 mã BL-0001..BL-1000, metadata cơ bản, status NOT_SCREENPLAY.
- docs/story/bell_leaf/slates/BELL_LEAF_1000_EPISODE_DEVELOPMENT_SLATE_UNAPPROVED_20261107.md = 1000 thẻ tập được tạo ở lượt trước, đánh dấu UNAPPROVED; không được dùng làm 1000 full screenplay.
- Đội biên kịch bắt buộc chạy tools/bell_leaf/episode_uniqueness_gate.py trước khi tạo/khóa tập mới; cả kết quả tự động và reviewer thủ công phải lưu cùng từng tập.

## III. Kết quả script/data audit thực tế
Chạy trên Windows isolated Git worktree: python tools/bell_leaf/episode_uniqueness_gate.py audit --out data/story/bell_leaf/episode_novelty_audit.json.
- 1.000 thẻ; 1.000 title chuẩn hóa khác nhau — chỉ chứng minh title không trùng.
- HOOK: 999 thẻ có hook được tách bằng nhãn; 937 hook khác nhau; 84 thẻ nằm trong nhóm hook lặp exact.
- GOAL: 99/1000 có mục tiêu riêng ở trường có nhãn đó; 901 không đạt điều kiện trích xuất mục tiêu tường minh.
- CONFLICT: 100/1000 có trường xung đột explicit; 900 thiếu field hoặc không phân tách được; KHÔNG có nghĩa những tập ấy hoàn toàn không có xung đột, mà là dữ liệu chưa đủ rõ cho QC.
- RESOLUTION: 999 bản ghi, 260 cách diễn đạt khác nhau, 860 tập thuộc nhóm mô tả giải pháp lặp exact.
- TWIST/DƯ ÂM: 899 bản ghi, chỉ 9 mẫu diễn đạt; 899 thuộc nhóm lặp exact. Một dư âm được mô tả không đồng nghĩa với một tình tiết twist khác biệt.
- CONTINUITY_DELTA: 899 thẻ cùng một đoạn boilerplate (không phải 899 thẻ có cùng toàn bộ kịch bản).
- Kết luận audit: REVIEW_REQUIRED, KHÔNG phải PASS; cần đề cương chi tiết có cause/goal/conflict/reversal/payoff và ledger hậu quả riêng trước khi viết screenplay. Không được lặp một công thức chỉ bằng cách đổi nhân vật/world.

## IV. Hiện trạng nghiên cứu: khác với "đã kết nối toàn bộ"
Chạy tools/cf_niche.py audit slow_english_a2 trên bản local active: 55% NOT READY, research section 17%; 0 competitor rows trong dataset đích mà kiểm định đọc, 0 nghiên cứu outlier chuyên sâu, 0 viewer quotes trong dataset đích. Đây là **generic niche audit**; không có nghĩa mọi JSON raw hoặc mọi báo cáo nghiên cứu CINE hoàn toàn rỗng. Báo cáo 2026-11-02 RESEARCH_SCREENPLAY_EFFECTIVENESS_AUDIT_20261102.md đã xác định pilot có 5 metadata adjacent, 0 direct magical-family competitors, 0 video content thật đã phân tích có timecode; do đó các bước research sâu vẫn BLOCKED.
Không giả vờ có research đầy đủ hoặc retention thực tế. Trước khi duyệt idea dựa trên đối thủ, phải có provenance thực: peer cohort chính xác, URL, ngày, views/as-of, AV/trang transcript có timecode, điểm khác biệt, originality/rights review, reviewer chứng thực. Parent Slow English benchmark chỉ dùng kèm nhãn ADJACENT, không làm baseline cùng ngách.

## V. Ngăn lặp qua toàn bộ quy trình
1. Giai đoạn outline: tra 1000 đề xuất và danh sách tất cả các screenplay đã duyệt, không chỉ 20 tập gần nhất; bắt buộc điền hook, character goal, real obstacle, conflict, surprise, physical resolution, lasting consequence.
2. Chạy episode_uniqueness_gate.py check --candidate PATH_TO_PITCH.json. BLOCKED phải sửa; MANUAL_NOVELTY_REVIEW_REQUIRED vẫn cần human editorial signoff.
3. Story editor đánh giá lexical và similarity CỐT TRUYỆN: hoán đổi tên nhân vật, thế giới, nghề nghiệp, màu sắc không đủ là tác phẩm mới. So thêm động cơ, tình huống, quy luật phép, clue/trail/reveal, hành vi và cái giá giải quyết. Chứng cứ không đủ -> HOLD.
4. Sau khi viết screenplay: đọc so sánh đoạn thoại, scenes, staging, blocking và các beats trùng. Tách story creative QC khỏi ảnh/voice/Muse/YouTube. Lưu receipt + actor độc lập, không tự nhận approval.
5. Tập được duyệt mới cập nhật continuity ledger. Các bản đề xuất chưa duyệt không được nâng thành canon fact; chỉ đề xuất thay đổi những nơi user cho phép.

## VI. Điều CHƯA THỂ tuyên bố
- Chưa có 1.000 full screenplays 40–50 phút độc lập, chưa có 1.000 báo cáo sáng tác unique được editor ký thật.
- Chưa có dataset đối thủ/direct AV và viewer retention xác minh đầy đủ cho Bell & Leaf; chưa có analytics thực từng tập.
- Uniqueness tool là deterministic lexical/template guard. Nó có thể tìm dấu hiệu trùng nhưng KHÔNG chứng minh hai kịch bản không trùng về mặt ngữ nghĩa hoặc vi phạm bản quyền. Muốn bảo đảm chất lượng phải có con người và evidence đúng.
- Phiên bản hiện có đưa quy định vào Claude skill/SOP và cung cấp CLI gate độc lập; chưa chứng minh mọi agent/runtime hiện hữu trong legacy EXE gọi gate này trước EVERY pipeline stage. Bắt buộc kiểm thực nghiệm E2E riêng.
