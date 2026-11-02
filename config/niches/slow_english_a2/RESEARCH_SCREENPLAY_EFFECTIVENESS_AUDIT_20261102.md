# CINE Slow English A2 / Bell & Leaf — Audit thực chất Research → Screenplay
**Ngày kiểm tra:** 2026-11-02 · **Đối tượng:** CINE Windows hiện hữu trên DESKTOP-HJE6A6D · **Không tạo repo/CineFactory khác**

## Kết luận có bằng chứng

**Logic đồ thị: PASS. Chất lượng nghiên cứu/kịch bản tự động end-to-end: NOT PROVEN.** Không đồng nhất `21 SKILL.md`, `CI PASS` hay `HANDOFF_RECORDED` với câu chuyện hay, nguồn đáng tin, người học A2 hiểu bài, hoặc phim đã sẵn sàng sản xuất.

- 21 vai trò gốc trong `config/story_factory/a2_bell_leaf_skill_graph.json`, 38 cạnh, 27 đầu ra chuyên môn duy nhất; không thấy output specialist bị hai chủ sở hữu trùng nhau; S09 anthology tắt mặc định.
- CINE Master `cf_a2_master_skill.py` xác định vai trò tiếp theo, kiểm tra upstream handoff SHA-256. `cf_a2_claude_agent.py` thực sự gọi tài khoản Claude Code với no tools, cấp đầu vào từ các vai trò upstream trực tiếp và Canon Bell & Leaf. `story-skills` có 18 kỹ năng tham khảo ánh xạ, phần trích kỹ thuật giới hạn và kiểm tra commit. `youtube-niche-finder` hiện vẫn chưa kết nối runtime.
- Tập thử thực tế `bell_leaf_integration_pilot_20261030`: có R01, R04, R05 + ba SHA receipt, nhưng chỉ có 5 nguồn metadata ngày 2026-10-22 thuộc **ADJACENT_SLOW_ENGLISH**; 0 đối thủ Magical Witch Family trực tiếp và 0 nội dung video nghe/xem thực. R05 ghi rõ `status: BLOCKED`. Không có bằng chứng retention, transcript timestamp, AV beat hay mẫu bình luận được xác minh. Không được nói đã tìm được viral formula.
- Sau sửa: Master `next` trả về `BLOCKED_RESEARCH_QUALITY` và lý do cụ thể, thay vì `STAGE_QC_GATE` gây hiểu nhầm. `cf_script_factory.py advance --stage research` cũng từ chối khi chưa đủ độ sâu nguồn.

## Các vấn đề căn nguyên đã kiểm toán

| Mức độ | Vấn đề | Bằng chứng | Trạng thái |
| --- | --- | --- | --- |
| P0 | Metadata-only bị ghi receipt là hoàn tất Research | R05 thực tế nói BLOCKED, Master từng báo STAGE_QC_GATE | **Đã sửa: strict research gate** |
| P0 | 21 role outputs không hoàn toàn khớp 8 factory-stage outputs | 27 role artifacts + **14 additional stage artifacts**; không thấy adapter sản xuất độc lập bao phủ tất cả | **Đã sửa phần trạng thái**: STAGE_ASSEMBLY_REQUIRED nêu thiếu file; chưa viết đầy đủ stage synthesizer |
| P0 | Thiếu nguồn video trực tiếp, AV, timecodes, follower/retention và cohort phù hợp | Pilot 5 nguồn metadata adjacent; không có 2 DIRECT_MAGICAL_FAMILY | **BLOCKED**, không khai giả có |
| P1 | `writer_executor_v1.py` / `script_factory_bridge.py` là đường **audio_storytelling_seniors**, không phải Bell & Leaf | Audio bridge buộc mode ORIGINAL_FICTION/COZY_FICTION và podcast-only; explicit rejection mode A2 | Đã cô lập theo mode, không dùng sai; không xóa |
| P1 | Nội dung downstream phụ thuộc SHA/upstream text, nhưng chưa có máy kiểm tra giá trị *ngữ nghĩa* từng claim được sử dụng trong beat/story/dialogue | Đồ thị đảm bảo thứ tự file, không chứng minh ý tưởng thực sự học từ bằng chứng | Cần trace IDs EV→INSIGHT→OPPORTUNITY→CONCEPT→SCENE/BEAT→REVIEW |
| P1 | Review CLI nhận `--actor` dạng chuỗi, không xác thực danh tính độc lập hoặc kết quả người học A2 thực | `cf_script_factory.advance()` và review JSON; không có xác thực reviewer ngoài tên | Cần reviewer proof độc lập, chống tự ký, A2 listening sample đo thật |
| P1 | Story Skills được đưa vào Claude prompt như *craft guidance*, chưa đo kết quả tốt hơn so với không dùng | `cf_a2_external_craft.py`: read-only intro excerpts, không chạy repo CLI | Cần A/B rubric định lượng |
| P1 | Missing content-review intake: agent CLI no tools không tự xem/nghe video | `cf_a2_claude_agent.py --tools ''`, nguồn phụ thuộc được chuẩn bị trước | Cần AV capture/transcript/timecode pipeline hợp lệ |
| P1 | Kịch bản gốc có file `screenplay.fountain` và file `script.md` riêng, chưa bảo đảm nội dung tương đương | S08 role vs stage contract, thiếu auto conversion/attestation | Cần output normalization với hash và scene count |
| P2 | 21 vai trò chuyên môn có thể gây lặp ý nếu không giới hạn quyền sở hữu nội dung, không đo thời lượng và rubric | roles r05/r06/s03/s04/s05/s06/s11 đều cùng phân tích hook, pacing, emotion ở độ hạt khác nhau | Chuẩn hóa trách nhiệm, đo tác động, không đơn giản xóa kỹ năng |

### 14 đầu ra bổ sung chưa có một owner role trực tiếp
1. Research: `01_research/evidence.json`
2. Insights: `02_insights/audience_insights.json`
3. Concepts: `03_concepts/portfolio.json`
4. Story: `04_story/story_dna.json`
5. Outline: `05_outline/beat_sheet.json`
6. Script: `06_script/script.md`
7–11. Review: `07_review/a2_review.json`, `canon_review.json`, `creative_review.json`, `compliance_review.json`, `timed_read.json`
12–14. Final: `08_final/audio_handoff.json`, `final_script.md`, `shot_handoff.json`

Một số là **bản tổng hợp hợp lý** hoặc chữ ký QC của người duyệt, không phải skill chồng chéo; nhưng phải có actor/assembler và không cho PASS khi file bị thiếu.

## Điều kiện nghiệm thu hiệu quả, không chỉ đếm skill

1. **Research**: Cohort trực tiếp tách cohort gần kề, URL/timestamp/method từng nguồn, nguồn mới và ngày quan sát, phân tích nội dung AV thật có timecode, so sánh baseline *cùng kênh*, ý kiến phản bác và giải thích yếu tố confounder. Research gate mới đặt tối thiểu 2 direct verified records và ít nhất một tuyên bố nội dung video được xem; vẫn bắt buộc kiểm duyệt độc lập vì metadata/khai báo modality không chứng minh đã xem thực. Nếu đúng ngách không có đối thủ trực tiếp, cần quy trình phê duyệt fallback research bằng bằng chứng thực — **không được tùy tiện đổi adjacent thành direct**.
2. **Insight → Story**: Mỗi hypothesis có EV IDs, nội dung cụ thể từ timestamp/quote, confidence và counterexample. Các ý tưởng Bell & Leaf phải độc lập với truyện đối thủ; EV học kỹ thuật kể chuyện chứ không copy nhân vật/tình huống cụ thể.
3. **Concept → Canon → Outline**: ≥5 phương án thực sự khác nhau, showrunner chọn 1; Juno/Lia/Bubu/Bix tính cách nhất quán; Veylora clue thực; cause-effect setup/payoff; không phải 6 mini-story rời rạc; có mục tiêu + bất ngờ + giải quyết vấn đề địa phương.
4. **Screenplay**: 30–50 phút đo bằng table read thật, screenplay Fountain đầy đủ cảnh/diễn xuất/thoại; no narrator, lời thoại A2 rõ tự nhiên. File script.md/final_script.md nếu tồn tại phải chứng minh cùng nội dung được duyệt; không chỉ vượt 1.200 ký tự.
5. **Independent Review**: adversarial Story Doctor, Canon, A2 learner comprehension có bằng chứng, originality/rights, measurable revisions và quyền phê duyệt của người thật.
6. **Effectiveness**: chạy pilot ≥1 tập qua tất cả stage với bằng chứng thật; so sánh *with/without* Story Skills trên rubric plot logic, hook, novel surprise, dialogue A2, character differentiation, continuity, duration; sau xuất bản mới dùng retention/CTR thực để đánh giá hiệu quả thương mại.

## Phân biệt hoàn thành sau cập nhật

- PASS: đồ thị phụ thuộc, thực thi 3 role research đã chạy với Claude Code, source hash, reject missing/metadata evidence, stage assembly visibility, A2 Director preflight code.
- NOT PROVEN: nghiên cứu AV sâu tự động, cấu trúc kịch bản 40 phút thật, nghiệp vụ reviewer, KPI YouTube hoặc video xuất bản.
- NO PERMISSION: Không coi CI, model nhận một nguồn hay số lượng file là creative approval. Không đổi thiết kế nhân vật nguồn hoặc tạo project/repo khác.

**Code kiểm tra:** `python tools/cf_a2_research_quality.py --project-dir data/script_factory/projects/bell_leaf_integration_pilot_20261030`; `python tools/cf_a2_master_skill.py next --id bell_leaf_integration_pilot_20261030`.

**Tính trung thực:** gate kiểm tra consistency/provenance fields, không tự xem video, không thể xác minh một model nói đã xem AV là đúng nếu không có evidence/bằng chứng tách biệt.
