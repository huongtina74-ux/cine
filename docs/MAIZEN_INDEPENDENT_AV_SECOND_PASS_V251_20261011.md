# CineFactory v251 — Kiểm tra nghe–nhìn lần hai, độc lập đường xử lý nguồn, hai video Maizen

Ngày 11/10/2026. Nguồn gốc vẫn là hai video YouTube Maizen công khai đã được phát đầy đủ trong Chrome ở v248:

- `zhPBXzHsLuo` — **Built a House inside BED in Minecraft**; đúng video xác nhận từ browser, **18:36.601**, đã phát 30/30 khoảng 38 giây, lấy mẫu hình và tiếng.
- `oX6Azwe5QLg` — **Minecraft, But Item Drops Are Multiplied Every Time!!**; đúng video xác nhận từ browser, **17:10.741**, đã phát 28/28 khoảng 38 giây, lấy mẫu hình và tiếng.

## 1. Độc lập như thế nào, và giới hạn trung thực

**Không** chỉ đọc lại mô tả vidIQ hoặc dùng lại thông tin từ bản báo cáo v248 làm chứng cứ duy nhất. Trong lượt v249–v251:

1. **Đường kiểm toán thứ hai:** Mỗi đoạn audio Opus thu trực tiếp qua YouTube Chrome được giải mã một lần nữa bằng FFmpeg ra **PCM**, điều chỉnh về tốc độ gốc từ trình duyệt 2×. Tệp nào sai SHA-256 hoặc giải mã lỗi bị đánh dấu; đo mức năng lượng âm, tính liên tục **từng giây của source**.
2. Chia **73 khoảng không lớn hơn 30 giây** (38 House + 35 Multiplier). Mỗi khoảng phải có ít nhất **2 ảnh chụp nguồn thực tế**, đầy đủ các ô dữ liệu tiếng theo giây, thời gian gốc và đoạn Whisper hiện có để đối chiếu ý nghĩa sơ bộ. 19 contact sheets được mở và kiểm tra trực quan trực tiếp trong lượt này.
3. Ban đầu phát hiện 3 vị trí chất lượng thấp: hình ở phút 11:30–12:00 House, tiếng đoạn kết ở 18:36 House, tiếng khoảng 11:22 Multiplier. **Mở lại chính video gốc trên Chrome, thu hình và tiếng ở tốc độ 1×**, giữ riêng Opus, ảnh, nguồn, thời gian bắt đầu–kết thúc và SHA256. Sau đó chạy lại toàn bộ kiểm tra PCM/gaps.
4. Lượt xác minh âm thanh thứ hai dùng mô hình **MIT AudioSet AST** miễn phí, chạy **cục bộ** để phân loại nhạc, tiếng nói, các gợi ý sự kiện **trong một mẫu tối đa 10 giây ở giữa mỗi khoảng 30 giây**. AudioSet tự động chỉ là một bằng chứng bổ trợ, hoàn toàn không thể thay thế con người nghe xuyên suốt từng tiếng nổ, nhạc, Foley hay kiểm định bản quyền.

**Điểm khác nhau giữa "độc lập xử lý" và "giám khảo độc lập":** Phần mềm kiểm tra mới có code/decoder/model khác và các lần Chrome mở lại độc lập. Nhưng chưa có **người kiểm định thứ hai độc lập nghe toàn bộ âm thanh gốc trong 35 phút 47 giây và xem liên tục mọi chuyển động từng giây**; chưa có file video gốc đầy đủ (không thu gom hay tải trái phép), cũng chưa có ký nhận auditor. Do đó đây là **SECOND-PASS MECHANICAL + SAMPLED VISUAL/SPEECH REVIEW, KHÔNG PHẢI STRICT v227 G02 PASS**.

## 2. Các phép đo source-bounded độc lập

| Tiêu chí | House inside BED | Item Drops |
|---|---:|---:|
| Thời lượng gốc | 1116,601 s | 1030,741 s |
| Chrome first-party playback | 30/30 khoảng | 28/28 khoảng |
| Chrome Opus nguồn giải mã lại PCM | 30/30 | 28/28 |
| Khoảng nghe–nhìn không vượt 30 giây | 38/38 | 35/35 |
| Giây có PCM đã giải mã sau các source-native repair | 1117/1117 ô | 1031/1031 ô |
| Ảnh gốc theo thời gian đã kiểm tra, kể cả lần phát vá | **157** | **132** |
| Khoảng ít hơn 2 ảnh gốc | **0** | **0** |
| Lỗi checksum audio, decode, sound coverage | **0** | **0** |
| Contact-sheet đánh số phục vụ đọc trực quan | **10** | **9** |
| Đã có transcript Whisper từ source sound (tự động, chưa sửa đúng từng chữ) | 30/30 | 28/28 |
| AudioSet AST kiểm tra đoạn 10 giây giữa từng khoảng 30 giây | 38/38 | 35/35 |
| AST suy đoán có nhạc (score > 0,10) | 34/38 | 32/35 |
| AST suy đoán có lời nói (score > 0,10) | 37/38 | 35/35 |
| File film nguyên bản + kiểm toán độc lập toàn bộ Foley/song/music | **Chưa có** | **Chưa có** |

Việc đánh dấu PCM coverage không đồng nghĩa máy "hiểu từng giây" hay biết bản nhạc có bản quyền: đó chỉ là bảo đảm tín hiệu nguồn thật hiện diện. Ảnh tĩnh theo khoảng thời gian không tương đương xem mọi frame/actor motion.

## 3. House inside BED — Quan sát nghe–nhìn xuyên suốt (hình ảnh và thoại tự động được đối chiếu)

| Mốc | Nội dung thực tế đã kiểm tra | Kỹ thuật kể chuyện có bằng chứng |
|---|---|---|
| 00:00–02:00 | Nhà gỗ khổng lồ; thiết bị thu nhỏ hai nhân vật; camera từ ngoài nhà xuống ngang tầm nhân vật bé tí; lối đột nhập gần chân tường và giường | Khởi đầu từ vụ nhân vật **Buu** lấy trộm tiền, hai người trả đũa bằng sống lén trong nhà. Phụ đề ghi Buu, Whisper có đoạn chép sai thành Boo |
| 02:00–06:30 | Thể tích rỗng màu đỏ trong giường có thể xây; sau khi di chuyển các món từ phòng khác, xây phòng khách, cửa sổ, phòng tắm, bếp | Tạo quy mô **tí hon – khổng lồ** thật sự trong góc nhìn nhân vật; mục đích thực dụng được giải thích trước mỗi giai đoạn |
| 06:30–08:30 | Ra lấy lương thực ở nông trại rồi quay về trồng luống có nước, đèn và cây trong base | Nhu cầu ăn uống dẫn tới nhiệm vụ phụ và quy trình cung cấp tài nguyên có logic không gian |
| 08:30–11:30 | Hệ thống băng + quạt, dispenser tên, đòn bẩy điều khiển, thiết bị phản xạ có xanh lá, cửa sổ quan sát; cắt chữ **NIGHT** | Các giải pháp **được giới thiệu trước khi vấn đề xảy ra**, chuẩn bị cho các lần kiểm tra sau |
| 11:30–14:05 | Chủ nhà trở về; nghe vị trí rương kim cương cất sau kệ sách, khám phá đoạn passage sau kệ, mở chest lớn trong phòng phủ kim cương | Thông tin thoại Buu vô tình để lộ là đầu mối để đòi lại tài sản; câu chuyện quay về mục tiêu ban đầu |
| 14:05–16:00 | Buu phát hiện dấu hiệu bất thường, rót dung nham gây cháy, thermometer trong base hiển thị nhiệt độ tăng | Vấn đề đã được dự đoán, cơ chế làm lạnh xuất hiện sau khi tác hại rõ ràng |
| 16:00–18:23 | Băng/fan làm mát; tên bắn trả; Buu dùng launcher, máy phản xạ hoạt động; vụ nổ làm hư phòng nhưng căn cứ sống sót | **Ba cấp nguy cơ tăng dần** dùng lần lượt các hệ thống chuẩn bị trước, không phải chuỗi bẫy rời rạc |
| 18:23–18:36,6 | Outro 2D xanh có linh vật và gợi ý video tiếp theo | Module hậu kỳ tách khỏi footage voxel-world |

**Không thể kết luận:** Mod thu nhỏ nào, cách mở cửa giường, bản gốc game được ghi hình thế nào, ai điều khiển camera, có Blender/Mine-imator/Unreal không, asset/voice của đối thủ có bản quyền sử dụng ra sao. Các tên trên chỉ là đối tượng quan sát, không phải mô tả mã nguồn.

## 4. Item Drops — Quan sát nghe–nhìn xuyên suốt

| Mốc | Nội dung thực tế đã kiểm tra | Kỹ thuật kể chuyện có bằng chứng |
|---|---|---|
| 00:00–02:00 | Dùng công cụ cầm trên tay để nhân vật phẩm rơi từ lúa mì/cát/gỗ, kiểm tra hotbar, chế tạo đồ ăn, đến khu cổng lava | Công cụ được **thử ngay** trên tài nguyên quen thuộc để khán giả biết lợi ích mà không cần giải thích dài |
| 02:00–05:00 | Vàng, obsidian và desert pyramid; gỡ pressure plate TNT, thu TNT nhiều, chest đồ vật | Bẫy/địa hình cũ trở thành cơ hội khai thác khi có quy tắc mới |
| 05:00–08:00 | Chế đồ sắt, quái vật, TNT có tường obsidian bảo vệ, mở ra hang lớn có dung nham, tìm kim cương | Tài nguyên vô tận **không xóa hết nguy hiểm**, tạo những khoảnh khắc sai sót và sửa |
| 08:00–10:30 | Kim cương rơi thành đống khổng lồ, craft giáp/kiếm, quả táo vàng, chuẩn bị bước đi tiếp | Tiến triển nhận biết được bằng chính UI/inventory/đồ đeo nhân vật |
| 10:30–12:20 | Tạo cổng Nether lớn, đánh Blaze, theo Enderman để lấy Ender Pearl và Blaze Rod | Nguồn khó không được nhân trực tiếp trong logic đang sử dụng; buộc phải thu item mẫu |
| **12:20–13:00** | **Sửa báo cáo cũ:** Đặt Blaze Rod + Ender Pearl trong **chest rồi nhân khối chest có đồ bên trong**; chế Blaze Powder / Eyes of Ender | "Vật phẩm không nhân trực tiếp" không phải ngõ cụt. Kịch bản có **giải pháp đi đường vòng** thông qua vật chứa được nhân, giữ câu chuyện tiến triển |
| 13:00–16:20 | End portal, Iron Golems tấn công Ender Dragon; poison/phép khiến golem không đủ hiệu quả, dựng giàn obsidian và TNT nhiều đợt | Tình huống thay đổi chiến thuật **từ lính hỗ trợ sang bẫy TNT**, không thắng dễ sau lần đầu |
| 16:20–17:10,7 | Boss chết, trứng rồng xuất hiện rồi biến mất, tổng kết công cụ và outro 2D | Thắng mục tiêu Minecraft dài hạn với một tiền đề tài nguyên, không chỉ thu gom vô nghĩa |

**Không thể kết luận:** datapack, Forge/Fabric/mod nào, plugin item duplication, lệnh server, rig animations hay thuật toán camerawork. Hình ảnh có HUD thực, nhưng không chứng minh hoàn toàn mọi cảnh được quay từ game hay không có CGI.

## 5. Điều CineFactory nên thay đổi

**Research:** Kết luận format từ quan sát hết film + nghe thoại/audio gốc + kiểm tra mechanic consistency, không dùng metadata/vidIQ text làm tương đương. Phân biệt per-film và channel-wide. 73 đoạn 30s có trace, screenshot & PCM checker. Bản dự đoán sự kiện tiếng không phải giám khảo thứ hai.

**Script Room:** Không ép cả ba phim theo một công thức 7 vòng. Hai format mới cho thấy cơ chế **Plant → Test → Escalate → Payoff** và **Rule → Constraint → Workaround → New Rule Application → Boss Payoff**. Với phim gốc MAI01_WATERFALL, viết cơ chế van chống ngập được chuẩn bị trước và được test thật cuối phim; dấu hiệu bản đồ/cửa/máy bơm phải có lúc payoff cụ thể.

**Production Design / Acting:** Thiết kế world scale/subworld rõ; trò chơi có hàng trăm item/inventory transitions; hai vai phải đối thoại và phản ứng ăn khớp camera POV/hạ góc nhìn, không teleport prop vô lý.

**Technical Director:** Cảnh game stage/dùng Minecraft runtime, Blender-authored CG, hybrid vẫn là candidate. Test bằng footage thật/hoàn chỉnh sau G02, không khẳng định Maizen dùng công nghệ nào. Video có thương hiệu/logo của đối thủ **không được sử dụng nguyên bản**.

**Audio/Editorial:** Nội dung thoại đã nhận dạng trên full timeline, nhưng nhạc và SFX mới chỉ có PCM+AudioSet sample; cần kiểm tra bản quyền, mixing, FX-source chính xác và voice acting của chính video CineFactory trước khi ra mắt.

**Quality Control:** Sau máy tự đọc toàn bộ nguồn/hồ sơ 30s, vẫn cần **một reviewer độc lập thực sự** xem chuyển động và nghe nội dung gốc từng khoảng; xác nhận không nhầm timeline source với semantics. G02 vẫn bị chặn theo `maizen_full_video_gate_v227.py`, không nâng production/publish chỉ vì 73/73 ô sound coverage.

## 6. Tệp bằng chứng thực

- `config/niches/minecraft/maizen_two_reference_second_pass_v251.json`: nội dung và kết luận từng video, bằng chứng/corrected finding, chuyển tiếp cho 26 phòng ban.
- `cinefactory/studio/maizen_second_pass_av_v251.py`: kiểm tra nhận dạng nguồn, không ảnh giả, 30s window, SHA, phần audio model và trạng thái G02 thật.
- `python -m cinefactory.cli maizen-independent-av`: kết quả có thể tra trực tiếp.
- Source audio và hình ở **Git-ignored** `.tools/maizen_two_full_av_v244/{video_id}/`.
- `independent_pcm_30second_qc_v249.json`: chứng cứ âm thanh giải mã lại và 73 cửa sổ.
- `independent_av_qc_30s_contact_sheets/windows_XX.jpg`: 19 bảng ảnh mẫu đã kiểm tra (10 House + 9 Multiplier).
- `qc_*.json` và `qc_*.webm`: 3 lần quay lại thật ở tốc độ nguồn 1× (sửa các điểm thiếu).
- `ast_audio_event_30s_v250.json`: xác suất dự đoán AudioSet mẫu 10s mỗi window; SFX/music đầy đủ vẫn PENDING.
- **Không** commit audio, video hay phụ đề dài có bản quyền của Maizen.
