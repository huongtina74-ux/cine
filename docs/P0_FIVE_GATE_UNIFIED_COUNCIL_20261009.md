# CineFactory P0 — Five-Gate Unified Evidence & CineCouncil
Ngày 09/10/2026 | Trạng thái: CODED + REGRESSION TESTED + ARCHIVED DATA VALIDATED; NOT PRODUCTION-OPERATIONAL.

## Nguyên tắc bất biến

**Một dữ liệu nguồn, một hồ sơ ngách/revision, một quyết định CineCouncil.** Không phát triển scanner thứ hai. Company Youtube vẫn là collector canonical; `breakout_proof.py` là gate kiểm chứng breakout duy nhất; `known_niches.json` là registry định dạng đã có; `council.py` / `case_controller.py` là trọng tài duy nhất, không xuất kết luận trùng nhau từ agent riêng lẻ.

Các nguồn đầu vào cần phân biệt:
- `official_artifact.json` lấy từ một lần thu thập metadata có nguồn rõ ràng (hoặc offline fixture khi test). File hash không chứng minh tính xác thực API. **Không chấp nhận source đã cũ >48h để đề xuất cơ hội mới.**
- `official_breakout_audit.json` do chính breakout_proof tạo ra. Bộ hợp nhất **tự tính lại** toàn bộ breakout để phát hiện báo cáo bị sửa.
- `review.json` là nội dung chuyên gia cần xác nhận. `reviewed_by` là khai báo chưa xác thực bằng danh tính; hệ thống không coi nó là sự thật đã chứng nhận.

## Luồng tác nghiệp

1. Company Youtube thu thập keyword/kênh/video theo hai nhánh; P0 public prescreen chỉ sàng lọc, P0 targeted official verifier xác minh chính xác các ID.
2. `five-gate-review-prep` tạo tệp mẫu `MANUAL_REVIEW_REQUIRED`: liệt kê kênh breakout có trong source, nguồn đối thủ lâu năm có >=100k view trong 90 ngày, kênh mới khác có video >=100k view trong 30 ngày. Tất cả `topic_fit` đều `UNKNOWN` cho đến khi xem video/ngách thực tế.
3. Chuyên gia rà soát và điền `niche`, `format_key`, sự khác biệt, đánh giá nội dung theo video ID, lựa chọn 2 kênh trưởng thành độc lập, chọn một kênh mới độc lập, và kịch bản RPM/chi phí/khối lượng sản xuất. Không được tự gán `REVIEWED` nếu chưa nghiên cứu nguồn.
4. `five-gate-dossier` soát:
   - G1 **novelty**: đối chiếu known_niches + format; khác biệt do reviewer phân tích, không tự suy từ tên.
   - G2 **breakout**: exact source + 0–30 ngày + 2 video ID long-form 8 phút ≥1M + video và ngày tạo hợp lệ, cùng ngách theo review.
   - G3 **evergreen**: 2 channel ID độc lập ≥365 ngày, video cùng ngách, đăng 0–90 ngày và ≥100k views từng video.
   - G4 **business**: giả định RPM/lượt xem/tháng/chi phí cố định/chi phí một video/số video; tính downside 50%, base 100%, upside 150%. Base profit phải ≥2.000 USD/tháng để đánh dấu **SCENARIO_DOCUMENTED_NOT_PROVEN**. Không chứng minh RPM thực, doanh thu thực hay điều kiện bật kiếm tiền.
   - G5 **entry**: ít nhất một kênh **khác breakout winner**, 0–30 ngày, video cùng ngách 0–30 ngày có ≥100k views.
5. Ghi dấu hiệu `full movie`, `Hindi/English dubbed`, `full episode`… từ **tất cả witness**, kể cả khi chưa có topic-review. Bắt buộc `RIGHTS_REVIEW_HOLD` nếu xuất hiện; đây là heuristic rủi ro, không tự kết tội vi phạm bản quyền.
6. Ghi `dossier.json`, `audit_recomputed.json`, `council_issue.json`, `council_evidence_registry.json`, `council_tasks.json` trong **một thư mục case**; tất cả có hash nguồn và revision. Các phòng ban sử dụng cùng issue_id và registry.
7. Khi có **ý kiến thật** đã xác nhận bằng file, chạy `five-gate-council-finalize`. Lệnh **tái sử dụng `consolidate_case`**; phản đối chưa giải quyết → không được cho thử nghiệm. `case.json` ở thư mục gốc là trạng thái hiện hành; con `council/case.json` là bằng chứng xử lý phòng ban. **Luôn production_permission=false** vì chưa có xác thực owner approval.
8. Chỉ sau khi có owner UI và quyền phê duyệt bảo mật mới kích hoạt Research Pod & production; không sửa Company scripts hoặc xuất bản video từ các lệnh nói trên.

## Kết quả chạy thực tế ngày 09/10/2026

Tập dữ liệu lịch sử `us_broad_niche_discovery_2026-07-03_v2` được kiểm tra theo cùng hợp đồng:
- Metadata đã ghi nhận một kênh có 2 video long-form triệu view vào **03/07/2026**, không phải cơ hội mới hôm nay.
- Review template: 1 breakout witness, **0** mature competitor đủ điều kiện tự liệt kê, 2 independent newcomer candidates (từ data snapshot, **chưa kết luận cùng ngách**).
- Dossier: `RIGHTS_REVIEW_HOLD`; các gate chưa đủ review độc lập không được nâng thành đầu tư khả thi.
- Council chạy **không có ý kiến** (JSON `[]`) trả `INSUFFICIENT_REVIEW`. Current case là `GATES_OR_RIGHTS_HOLD`, `production_permission=false`. **Không giả lập đồng thuận**.
- File: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\historical_review_template.json`
- File: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\historical_five_gate_output_v2\case.json`
- Không có live October source đầy đủ năm gate được chứng nhận trong lần này.

## Lệnh sử dụng

Tại repository `C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6`:

```powershell
python -m cinefactory.research_intelligence five-gate-review-prep --official-artifact "C:\...\raw\official_api_integrated_scan.json" --breakout-audit "C:\...\strict_breakout_audit.json" --output "C:\CineResearch\case\review_template.json"
# Biên tập dựa trên nguồn và kiểm chứng nội dung, lưu thành review.json
python -m cinefactory.research_intelligence five-gate-dossier --official-artifact "C:\...\raw\official_api_integrated_scan.json" --breakout-audit "C:\...\strict_breakout_audit.json" --review "C:\CineResearch\case\review.json" --output-dir "C:\CineResearch\case"
# Sau phản biện thật, opinions.json gồm các ý kiến initial/rebuttal theo hợp đồng council.py
python -m cinefactory.research_intelligence five-gate-council-finalize --case-dir "C:\CineResearch\case" --opinions "C:\CineResearch\case\opinions.json"
```

Không đưa API key vào argument/log/file; nguồn input cần thuộc phiên scan thật với kiểm tra thời điểm và integrity.

## Nghiệm thu đã có

- Gate chính xác với synthetic official-formatted fixtures; kiểm tra 2 kênh mature và một new entrant khác biệt; giả định doanh thu sau chi phí.
- Kiểm tra source-hash, báo cáo breakout bị chỉnh sửa, nguồn lịch sử, thay đổi reviewer file, trùng video giữa kênh, video trước ngày lập kênh, rủi ro bản quyền.
- Reuse CineCouncil arbitration với lập luận trống/trái chiều → fail closed, không duyệt.
- End-to-end offline trên snapshot thật lịch sử: `RIGHTS_REVIEW_HOLD` và `GATES_OR_RIGHTS_HOLD`.
- Chỉ số test regression là bằng chứng mã hoạt động trên fixture/snapshot, **không chứng minh nghiên cứu tự động có độ chính xác cao trên toàn YouTube**.

## Còn thiếu để P0 thực sự chuyên nghiệp

1. Scanner canonical phải hoàn thành thực tế và thu thập ổn định hàng ngày ở US/en rồi mở rộng thị trường RPM cao theo coverage thật.
2. Exact official metadata cho shortlisted IDs khi có API key hoặc nguồn tương đương được xác minh độc lập; hiện no-key path chưa thể chứng minh exact age, views và ownership 100%.
3. Phòng nghiên cứu ngách thực sự phân loại video/format bằng AI đa phương thức và rà soát con người; lưu evidence timestamp và phản biện chất lượng trước khi đánh dấu semantic fit.
4. Tự bổ sung channel/video evidence lịch sử và mature evergreen khi thiếu; không chỉ hiển thị `0` hoặc copy từ niche khác.
5. Quyền sở hữu reviewer / owner approval, provenance với chữ ký và kho immutable ngoài local filesystem; ngăn manual review giả.
6. Benchmark precision/recall, false positives, độ mới, chi phí/nguồn, drift, crash/restore liên tục nhiều ngày.
7. Cần liên kết daily run tới task queue và notification: hiện template/dossier/council gọi thủ công, **không có tự động tranh luận Claude**.

**Quyết định:** P0 có thêm lớp kiểm chứng năm gate thống nhất, nhưng trạng thái vẫn PARTIAL. Không chạy chiến dịch đa kênh dựa trên một trường hợp breakout thiếu evergreen, rights hoặc economics.
