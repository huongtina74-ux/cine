# CINEFACTORY — MASTER PLAN HỢP NHẤT RESEARCH INTELLIGENCE
Ngày: 09/10/2026 | Trạng thái: **PHASED IMPLEMENTATION / NOT PRODUCTION CERTIFIED**

## I. Mục tiêu và ranh giới trách nhiệm

**Một công ty, một bộ bằng chứng chuẩn, một quyết định hiện hành.** Không tạo một bộ scanner thứ hai cạnh tranh với Company Youtube.

| Thành phần | Trách nhiệm duy nhất | Không được làm |
|---|---|---|
| Company Youtube | Khám phá thị trường, keyword, kênh, catalog, risk, snapshot và báo cáo nghiên cứu gốc | Tự phê duyệt ngách vào sản xuất |
| Market Bridge (CineFactory) | Đọc snapshot Company, kiểm tra cấu trúc, nguồn, ngày, điều kiện; chuyển thành case duy nhất | Thay dữ liệu nguồn hoặc tự gọi URL thiếu xác minh là VERIFIED |
| CineCouncil | Đưa nhiệm vụ cho chuyên gia đúng ngách, bắt phản biện, kiểm tra chứng cứ, xuất **một** quyết định có phiên bản | Lấy đa số phiếu để xóa bằng chứng phản đối |
| Owner Gate | Người sở hữu duyệt ngách; áp dụng chính **validator** hiện có trong Company Youtube | Tự động coi review của agent là chủ sở hữu đã duyệt |
| Niche Research Pod | Theo dõi ngách đã duyệt: đối thủ lớn, đối thủ mới, video 0–15 ngày, công thức sản xuất | Trộn dữ liệu từ hai ngách hoặc kích hoạt chi phí khi chưa được cấp quyền |
| CineFactory Production | Biến thí nghiệm đã được duyệt thành video nguyên bản; giữ lineage từ video đến kế hoạch cảnh | Sao chép tác phẩm tham chiếu |
| Analytics & QA | Đo dữ liệu video sở hữu, QC và kinh tế; truyền kết quả vào CineCouncil | Đọc nhầm Analytics đối thủ từ metadata công khai |
| Learning Registry | Chỉ nhận cải tiến có thí nghiệm đạt ngưỡng, phê duyệt, phiên bản và khả năng rollback | Tự sửa quy tắc production dựa trên 1 viral video |

**Nguồn quyền lực chuẩn:** Company Youtube giữ workflow discovery canonical. CineCouncil nắm quyết định nghiên cứu sau tích hợp. Chủ sở hữu là quyền cuối cùng để thử nghiệm/sản xuất. Một `niche_id + format_key` chỉ có một Research Pod.

## II. Nhánh 1 — nghiên cứu và báo cáo mỗi ngày

### A. Khám phá rộng
Duy trì hai luồng độc lập: keyword-led và channel-led. Không lọc bỏ tín hiệu yếu khỏi audit gốc. Bao phủ nhiều thị trường RPM cao (US/CA/UK/AU và các thị trường phù hợp); ưu tiên tiếng Anh. Ghi mỗi thị trường và mức coverage thật sự, không tuyên bố quét toàn bộ YouTube.

### B. Năm gate bắt buộc để đủ điều kiện đề xuất
1. **Novelty**: đối chiếu danh sách ngách hiện có; nếu ngách cũ, phải có format_key mới với phân tích sự khác biệt đủ rõ. Cờ khẳng định đơn lẻ không đủ.
2. **New channel breakout**: một kênh có bằng chứng ngày tạo từ 0–30 ngày tại thời điểm quan sát và **ít nhất hai video ID khác nhau** đạt >=1.000.000 views/video; video dài >=480s, không Shorts, không live, ngày đăng hợp lệ, URL trùng ID.
3. **Evergreen**: hai kênh trưởng thành độc lập (mặc định đã tồn tại >=365 ngày), mỗi kênh có video trong 90 ngày gần nhất đạt >=100.000 view. Đây là ngưỡng kiểm tra tối thiểu, không chứng minh nhu cầu mãi bền.
4. **Business**: mô hình dự báo chi phí/RPM/views/phân phối/khả năng duyệt YPP, có kịch bản thu nhập >=2.000 USD/tháng, tách giả định và số liệu đo thực tế. Mức 100k–1M USD/tháng chỉ là trường hợp scale rất xa, tuyệt đối không cam kết.
5. **Entry**: ít nhất một kênh mới độc lập có traction hữu hình, phân tích saturation và chính sách; tăng mức tin cậy nếu có nhiều case độc lập.

Trạng thái: **WATCHLIST** khi thiếu chứng cứ; **AUDIT_READY** khi năm gate cấu trúc đều đạt nhưng còn cần kiểm tra tính xác thực; **OWNER_REVIEW** chỉ sau review độc lập; **APPROVED** chỉ sau gate và owner event hợp lệ.

**Không suy ra video đạt 1M trong 14 ngày từ số view hiện tại.** Muốn claim tốc độ bùng nổ phải có snapshot lịch sử chứng minh thời điểm vượt mốc.

### C. Báo cáo ngày phải có
Thời điểm quét, nguồn/hạn chế/quota, coverage thực, ứng viên mới, ngách đã có/format khác, kênh/video-ID, ngày lập, ngày đăng, thời lượng, view và thời gian đo, nguồn evergreen, newcomer, mô hình RPM, originality/policy/copyright, confidence, blocked reasons, ưu tiên nghiên cứu tiếp. Ngày không có ứng viên đủ bằng chứng: báo cáo **không có ứng viên xác minh**, không bịa đủ 5 ngách.

### D. Vận hành và quan sát
Quy trình nền chưa được triển khai ở Phase P0. Khi xây scheduler: job idempotent; snapshot bất biến; giới hạn chi phí/call; theo dõi run-id, nguồn đã truy cập, lỗi, retries với backoff; health-alert nếu scan không chạy; owner summary vào giờ người dùng chọn. Task ChatGPT đang có chỉ là báo cáo riêng, không được coi là cron địa phương.

## III. Nhánh 2 — Research Pod liên tục sau khi chủ sở hữu duyệt

**Phê duyệt**: kiểm tra chính `Company Youtube/scripts/validate_promotion_gate.py`, request đúng WATCHLIST→TEST_WITH_10_VIDEOS, sự kiện owner đính kèm hash của bridge và gate. Event file chưa có xác thực danh tính bằng OAuth/UI — chưa được ghi là đã giải quyết bảo mật.

Ngay khi được kích hoạt hợp lệ, Research Pod có **sáu loại công việc**:
1. Market discovery vẫn theo dõi gate 0–30 ngày / 2 video triệu view.
2. Leader watch: kênh lớn lâu năm, video phổ biến toàn lịch sử, upload mới, outlier tương đối với phân phối theo tuổi video (không chỉ views/subscribers).
3. Newcomer watch: kênh 0–30 ngày mới gia nhập cùng format, tối thiểu 2 video triệu view nếu gọi là strict winner.
4. Fresh viral watch: keyword, video được đăng 0–15 ngày; view velocity từ repeated snapshots, trend-age, copycat/saturation risk.
5. Multimodal video review: câu chuyện, logic, hook, hành động, biểu cảm, camera, cut, sound, thumbnail và SEO, có timestamp và mức chắc chắn.
6. Owned feedback: CineFactory scene/timeline/QC/thumbnail/title version → CSV/OAuth của đúng video và đúng kênh → retention, CTR, watch time, RPM thực tế khi có.

**Mỗi ngách có luật chuyên môn riêng** nhưng cùng hợp đồng nguồn/ý kiến/quyết định: Minecraft/Roblox/Long Slide ưu tiên narrative/animation/visual; ASMR/rain ưu tiên audio/comfort; narration ưu tiên story/voice.

## IV. Giao thức nhiều phòng ban: phản biện, không hòa giải giả

Research, Story, Visual, Audio, Packaging, Growth, QA cùng sử dụng một issue_id/question và một evidence registry.
- Vòng 1: ý kiến độc lập; VERIFIED/SUPPORT, OPPOSE, UNKNOWN đều đòi nguồn rõ ràng.
- Vòng 2: QA + ít nhất một phòng khác phải phản biện chéo ngay cả khi cùng đồng ý.
- Trọng tài có quy tắc xác định: phản đối chưa giải quyết -> BLOCK; cùng file nhưng hai người nói -> SINGLE_SOURCE; nguồn bị sửa -> BLOCK; đủ chứng cứ -> SUPPORTED_FOR_TEST, KHÔNG tự cấp quyền production.
- Lịch sử quyết định phiên bản hóa. Decision hiện hành ghi ở duy nhất case.json.
- Trích dẫn và kiểm tra file **không chứng minh tính đúng ngữ nghĩa**; phải có benchmark và/hoặc xác nhận bằng thực tế.

## V. Mốc triển khai kỹ thuật và tiêu chuẩn nghiệm thu

| Mốc | Ưu tiên | Hạng mục / nghiệm thu | Trạng thái 09/10/2026 |
|---|---|---|---|
| **P0.1** | BLOCKER | Chốt Company Youtube là scanner canonical, kiểm thử import snapshot read-only và bảo toàn source-hash | **Đã viết + unit test** |
| **P0.2** | BLOCKER | Strict gate, video ID/URL, age, >=8 phút, >=2M x 2 video, evergreen independent, novelty, entry, revenue scenario; UNKNOWN fail closed | **Đã viết + unit test**, chưa đánh giá với scan live mới |
| **P0.3** | BLOCKER | Owner gate reuse validator + owner-event hash; pod idempotent, không đụng Company repo | **Đã viết + unit test**, chưa tích hợp nút Duyệt thực |
| **P0.4** | BLOCKER | Chạy 2 suite regression, compileall, commit không thay đổi luồng cũ | Phải làm trước khi đóng phase |
| **P1** | P0 tiếp theo | Canonical owner runner đầu ra snapshot theo schema, daily scheduler, rerun/idempotency, coverage dashboard, cảnh báo thiếu dữ liệu | **Chưa xây scheduler vận hành** |
| **P2.1** | NEXT | Research Pod watch: leader/newcomer/0-15d fresh; age-cohort outlier; VPH phải có 2 snapshot thực và nguồn hash | **Đã có bộ phân tích thủ công snapshot + unit/E2E; thiếu collector/scheduler/alert đang chạy** |
| **P2.2** | NEXT | Owner UI authenticated approval, RBAC, audit trail, provenance signing | **Chưa tích hợp** |
| **P3** | NEXT | PySceneDetect/Whisper/vision agent chỉ sau A/B benchmark; transcript, event detection, scene coverage; QA evidence | **Có local sampling và Claude mocked; chưa benchmark multimodal video thật** |
| **P4** | NEXT | Owned Analytics API OAuth hoặc CSV watcher có quyền, đúng channel/video/report window, retention/cost/cause analysis | **CSV import có; tự sync chưa có** |
| **P5** | LAST | Learning experiment engine: registered treatment/control, age-matched metrics, minimum lift, approval, rule version/rollback, drift evaluation | **Mới có proposal, chưa auto-learning production certified** |

**Mốc P0 không có nghĩa toàn công ty chuyên nghiệp.** Hoàn thành P0 chỉ chứng minh hợp đồng tích hợp và fail-closed; phải chạy real-world end-to-end để nâng trạng thái.

## VI. Rủi ro chuyên nghiệp cần chặn ngay

1. Metadata không thể chứng minh CTR, retention, RPM, nguồn đề xuất của đối thủ.
2. Người cung cấp CSV có thể gắn "VERIFIED" sai: bridge chỉ đánh dấu AUDIT_READY, không tự duyệt; nguồn REVIEWED có thể bị giả nếu không xác thực danh tính reviewer.
3. Hai video 1M không chứng minh khả năng RPM cao, được bật kiếm tiền hay tăng trưởng 2–3 tháng; YPP và monetization phải kiểm tra riêng.
4. Search / yt-dlp/YouTubeJS có thể lỗi hoặc thay đổi điều khoản; mỗi sensor ghi health và không lách giới hạn truy cập.
5. Chỉ số view/cắt cảnh được tính trước khi phát hành không phải retention người xem. Học từ Analytics cần đủ volume, so sánh đúng tuổi video, niche, thị trường.
6. Cùng 1 nguồn được 5 agents xác nhận cũng chỉ là **1 nguồn**, không phải năm xác minh.
7. Thumbnail/format nên học nguyên tắc chung, không đạo nhái video hay asset cụ thể.
8. Chỉ nên thêm tool AI sau khi đo precision/recall so với ground truth, latency, VRAM peak, costs và chính sách bản quyền.
9. Cả hai repo phải có lịch sử phiên bản, run manifests, artifacts immutable, integration regression và rollback path.
10. Phần scheduler/giám sát từ xa không được giả định tồn tại chỉ vì có task định kỳ trong ChatGPT.

## VII. Quy trình kiểm tra bản P0 (chưa quét Internet)

```powershell
cd "C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6"
python -m pytest tests\test_company_cine_bridge.py -q
python -m pytest tests -q
python -m cinefactory.research_intelligence bridge-import --help
python -m cinefactory.research_intelligence pod-activate --help
cd "C:\Users\ADMIN\Downloads\Company Youtube"
python scripts\run_all_validators.py
```

Import thật sau khi có file snapshot mới và reviewer packet thực, không dùng demo/test fixture làm bằng chứng thắng:

```powershell
python -m cinefactory.research_intelligence bridge-import --company-root "C:\Users\ADMIN\Downloads\Company Youtube" --channels "C:\...\niche_radar_channel_snapshot.csv" --videos "C:\...\niche_radar_video_snapshot.csv" --output "D:\CineResearch\cases\snapshot.json" --niche "Minecraft animation" --format-key "new-original-format" --review-json "D:\CineResearch\review.json"
```

**Trạng thái hiện tại không tự động tạo một Pod thật:** vì cần request canonical đã thông qua gate, owner approval event có kiểm tra revision, và bản snapshot thực còn mới. Kích hoạt bằng file template không được coi là chủ sở hữu đã duyệt.

## VIII. Nguyên tắc đóng dự án (Professional Operational)

Chỉ đánh dấu **PROFESSIONAL_OPERATIONAL** khi chạy ít nhất một tuần thực trên nhiều ngách: scan đầy đủ mỗi ngày; bản ghi không trùng và có health; approved pod theo dõi ba nhóm đối thủ; đa phương thức xem được video có quyền nghiên cứu; video CineFactory xuất bản gắn revision; Analytics nhập/đồng bộ đúng video; CineCouncil ra kết luận có kiểm soát; thử nghiệm mang lại dữ liệu mới; failover, restore, permissions, copyright, budget và security đều đã kiểm tra. Tỉ lệ PASS unit test đơn thuần không đủ.


## IX. Manual competitor intelligence (new in P0/P2)

The new `pod-watch` command analyzes previously imported Company Youtube snapshots. It classifies million-subscriber leaders, 0–30 day newcomers, freshly uploaded 0–15 day videos with at least 1 million views, and age-cohort outliers. It computes genuine views per hour only from two measurements.

Command example (paths are placeholders):

```powershell
python -m cinefactory.research_intelligence pod-watch --pod "D:\CineResearch\pods\sample\pod.json" --current-bridge "D:\CineResearch\runs\oct09\bridge.json" --previous-bridge "D:\CineResearch\runs\oct08\bridge.json" --output "D:\CineResearch\reports\watch.json"
```

Snapshots referenced by each imported bridge MUST be immutable per-run files; replacing a shared daily CSV invalidates the prior bridge's hash. The process does not yet run automatically or claim complete market coverage.
