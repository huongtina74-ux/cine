# CineFactory v242 — NGHIÊN CỨU HÌNH ẢNH VÀ ÂM THANH GỐC MAIZEN TOÀN TẬP

**Ngày:** 11/10/2026.
**Video:** [Mikey and JJ Choose the Right Hole in Minecraft](https://www.youtube.com/watch?v=ZmT0ITUGUII), 28:04.
**Phạm vi đã thực hiện:** phát toàn bộ timeline hình ảnh bằng Chrome (45 lượt phát liên tục theo mốc, có giao nhau); kiểm tra 153 khung hình mẫu; **thu âm thanh gốc trong trình duyệt từ 00:00 đến 28:04** bằng MediaRecorder/HTML5 `captureStream` theo 45 đoạn chồng lấn và một đoạn bổ sung đầu video; mỗi đoạn có tệp tiếng riêng và thời gian phát. Whisper `openai/whisper-tiny.en` chạy CPU local nhận dạng **45/45 đoạn**, khoảng **4.575 từ chưa hiệu đính**. Phân tích hình và lời nói đã được đối chiếu với timeline. **Không phát sinh credits API cho lần làm này.**

**Ranh giới bằng chứng:** Không có video MP4 đầy đủ được tải về. Chúng ta có bằng chứng phát hình qua browser và mẫu khung hình (không phải đánh giá thủ công từng frame). Tiếng nói đã được giải mã và ASR toàn bộ đoạn âm thanh, nhưng **Whisper có thể nhầm từ/tên**, không thể tự nó đánh giá chính xác toàn bộ nhạc, Foley, mức mix, bản quyền hay cảm xúc giọng nói. Chưa có giám khảo độc lập nghe kiểm chứng từng giây và bản phân tích từng khoảng <=30s theo tiêu chuẩn v227; **G02 STRICT = BLOCKED**. Đây chỉ là **1/3 video Maizen cần nghiên cứu**.

## I. Diễn biến nghe–nhìn theo 7 vòng

| Thời gian | Hình ảnh thực tế đã kiểm tra | Kịch bản/lời thoại nhận dạng từ tiếng gốc (tóm tắt, không trích dài) | Kỹ thuật kể chuyện suy ra |
|---|---|---|---|
| 00:00–03:35 | Hai đường ống TNT–Diamond lớn, đầu tiên góc camera thấy hai nhân vật; sau đó POV Minecraft/HUD. TNT nổ lộ rương đồ, phía kim cương xuất hiện sinh vật tấn công | Ngay mở đầu có giới thiệu **mỗi cặp chỉ một đường đúng**. Nhân vật tin Diamond chắc chắn an toàn hơn TNT, khoe vật phẩm, rồi bất ngờ trước nguy hiểm ở phòng kim cương | Luật rõ trong thoại -> lựa chọn có lập luận -> đảo kỳ vọng -> phần thưởng hoặc hình phạt. Lời thoại cài sẵn quan niệm sai |
| 03:36–07:05 | Hai đường nước–dung nham với sân parkour song song; có thuyền trong rương, một bên đi bằng thuyền | Mikey viện dẫn lần TNT trước để cho rằng **lựa chọn trông nguy hiểm có thể lại đúng**, nên chọn dung nham. Hai nhân vật trao đổi về sân chơi giống nhau nhưng khả năng dùng vật phẩm khác nhau | Logic của cảnh sau được nối từ cảnh trước bằng đối thoại. Đây không phải thử thách rời rạc |
| 07:06–10:23 | Slime và Honey, phòng khóa, chìa khóa/các khối tương tác, ong tấn công | Một nhân vật nghi ngờ mật ong thơm là mồi nhử, bên còn lại tìm chìa để mở cửa, nhận ra có bẫy từ vật phẩm/đàn ong | Đổi loại thử thách từ vượt địa hình sang khám phá/bí mật/giải đố, giúp tránh lặp nhịp |
| 10:24–12:43 | Hai ống 5/6, biểu thức 3+2, bẫy đá, cần gạt và cửa | Nhân vật diễn giải bài toán cực đơn giản rồi phản ứng khi cần gạt làm xuất hiện đá/bẫy; kết quả và cửa thoát là phần thưởng | Khán giả biết đáp án trước -> hồi hộp xem người sai bị phạt |
| 12:44–15:29 | Mutant Zombie–Silverfish, sinh vật có kích thước khác dự đoán | Người chơi dựa vào tên sinh vật để đoán độ nguy hiểm. Mutant Zombie xuất hiện nhỏ và dễ tiêu diệt; Silverfish lại khổng lồ, khiến nhân vật hoảng hốt | Đảo ngược tỷ lệ/thông thường; hài kịch từ tự tin chuyển thành sợ hãi |
| 15:30–18:00 | Android–iPhone, showroom điện thoại và sinh vật linh vật xanh | Nhân vật chọn loại điện thoại quen thuộc; phía được kỳ vọng có phần thưởng, phía khác gặp mối nguy và phải tìm cách thoát | Đổi chủ đề vật phẩm để tăng tính mới lạ; cần xem kỹ bản quyền biểu tượng/thương hiệu |
| 18:01–27:50 | Hai lựa chọn DANGER/SAFE, rương chênh lệch; sân đấu với đồng hồ, khu xây dựng chia hai phía, căn cứ trắng bảo mật với laser/lava/turrets và căn cứ đất/tơ nhện; boss tấn công lần lượt | Thoại đầu tiên **đánh lừa bằng chữ SAFE/DANGER**. Sau khi phát hiện đồ bảo mật mạnh/yếu, nhân vật giới thiệu từng bước xây nhà bí mật, hàng rào laser, màn lava, turrets. Đếm ngược ép phải chuẩn bị nhanh; khi boss xuất hiện, thoại chuyển thành dự đoán, cảnh báo, hoảng loạn, phản ứng từng lớp phòng thủ rồi ăn mừng | **Cao trào dài, nhiều tầng:** tiền đề bất bình đẳng -> chuẩn bị -> giới thiệu tài nguyên -> đếm ngược/montage -> quái tấn công căn cứ yếu -> thử hàng phòng ngự mạnh -> kết cục. Đồng hồ 15 phút trong thế giới phim được rút xuống vài phút video nhờ dựng/điều chỉnh thời gian (cơ chế cụ thể chưa xác minh) |
| 27:51–28:04 | Outro 2D xanh, Maizen mascot và gợi ý theo dõi | Có lời kêu gọi like/subscribe, mạng xã hội và video tiếp theo | Brand package cố định, đóng vòng chuyển người xem sang video khác |

**Lưu ý:** Bảng là **phân tích một tập cụ thể**, không chứng minh mọi video Maizen có đúng bảy vòng hay cùng nguyên tắc dựng.

## II. Kết quả âm thanh bổ sung mà xem ảnh không thấy

1. **Đối thoại tạo nguyên nhân và hậu quả.** Maizen không chỉ cho người xem thấy TNT và kim cương; nhân vật phát biểu tin rằng kim cương là lựa chọn an toàn. Vòng lava áp dụng lại (sai) kết luận từ vòng trước. Vì thế từng thử thách kết nối nhau bằng logic nhân vật.
2. **Ngôn ngữ phản ứng có nhịp dày.** Đoạn tiếng có rất nhiều câu hỏi ngắn, lời gọi tên, bày tỏ ngạc nhiên, sợ hãi, khoe tiến độ và bình luận đối thủ. Đây là bản nhận dạng giọng nói, chưa đo tốc độ/hài hòa tiếng nói hoàn chỉnh.
3. **Voice-led tutorial trong đoạn xây nhà.** Nhân vật nói rõ định làm gì và tại sao: giấu lối vào, dựng laser, điều khiển màn dung nham bằng cần gạt và dùng tháp bắn. Lời giải thích hỗ trợ khán giả theo dõi chuỗi dựng nhanh.
4. **Nhịp âm thanh cao trào dựa vào phản ứng liên tục.** Ở phần boss, lời nói báo động khi căn cứ yếu thất bại; sau đó tường thuật việc laser cản boss, kích hoạt dung nham, dùng tháp bắn và ăn mừng. Kết hợp hình đã xem tạo mô hình kể chuyện thử từng lớp phòng ngự.
5. **Audio hậu kỳ vẫn là ẩn số.** Chưa xác định chính xác ai lồng tiếng, có bản Nhật gốc hay không, phần nào ghi cùng cảnh hay đọc sau, nhạc/SFX lấy từ thư viện nào, mix LUFS ra sao. Không tuyên bố đã xác nhận lời thoại gốc từng chữ hoặc Foley theo từng giây.

## III. Bóc tách công đoạn dành cho CineFactory

| Công đoạn | Yêu cầu công ty học theo *nguyên lý*, không sao chép |
|---|---|
| **Research** | Với mọi video đối thủ, phát/nghe từ đầu đến cuối, chốt diễn biến hình, tiếng, cao trào, khoảng trống evidence và thay đổi giữa nhiều tập. Không suy cách sản xuất từ thumbnail hoặc 10s |
| **Script Room** | Viết luật thử thách rõ, đối thoại nhân vật có tư duy khác nhau, mục tiêu, chọn sai, hệ quả và sự nối tiếp giữa các vòng; sáng tạo nguyên bản |
| **Production Design** | Xây thư viện set modular: sảnh chọn đường, cặp phòng đối xứng, vật phẩm mở khóa, bẫy, arena, timer và boss hệ thống; asset/quyền sử dụng có chứng cứ |
| **Character & Acting** | Hai nhân vật có cá tính ổn định; dàn dựng thời điểm đối thoại, đi/chạy, ngạc nhiên, thất bại, giơ vật phẩm, phản ứng theo camera. Không mượn nguyên JJ/Mikey |
| **Technical Director** | Chọn giữa **Minecraft world được dàn dựng bằng command/mod và camera**, **CGI voxel tự dựng**, **hybrid** theo shot. Các khung hình HUD cho thấy game-style staging nhưng **không chứng minh chính xác mod/server/editor/bot hoặc Blender của Maizen** |
| **Audio & Editorial** | Viết thoại đi cùng nhịp hành động, ưu tiên rõ giọng từng nhân vật, đối thoại hình thành nhân quả, captions lớn đồng bộ, SFX hợp từng tác động, nhạc cường độ theo stakes, montage xây dựng rút ngắn thời gian và giữ tính logic |
| **QC** | Kiểm tra phim tham chiếu cả hình và tiếng, sau đó kiểm tra phim CineFactory thật từ đầu đến hết: liên tục hành động, câu thoại/camera đúng shot, đạo cụ không mất, bản quyền, mix, decode, tốc độ sản xuất, vòng sửa lỗi |

## IV. Kết luận có bằng chứng và kết luận còn bị chặn

**Được hỗ trợ bởi video gốc và lời thoại ASR:** Format là chương trình Minecraft-world có kịch bản/chủ ý dàn dựng rõ rệt; có thử thách hai lựa chọn, hai nhân vật phản ứng bằng lời, camera POV và thi thoảng 3rd-person, set riêng, các cơ chế có hậu quả, montage xây dựng và cao trào boss. Cách kể chuyện **lời thoại dẫn nguyên nhân**, không thể làm bằng công thức hai người chơi ngẫu nhiên và thu nguyên màn hình.

**Không được hỗ trợ:** Tên game version, Forge/Fabric, Mineflayer, ReplayMod, command block chính xác, mod quái cụ thể, Blender/Mine-imator/Unreal, phương pháp lip-sync, công nghệ làm boss, chính xác đội Maizen quay dựng, hay tỷ lệ footage 3D ngoài game. Những thứ đó vẫn là **HYPOTHESIS**.

**Cổng nghiên cứu G02 v227:** CHƯA PASS do chưa có kiểm toán nghe/nhìn đầy đủ theo cửa sổ 30s, đánh giá SFX/nhạc độc lập và hai video Maizen khác chưa qua chuẩn. Không cấp phép G03+ hoặc sản xuất dựa trên kết luận vendor cụ thể.

## V. Tệp nội bộ

- Bằng chứng machine-readable đã lọc: `config/niches/minecraft/maizen_original_browser_audio_evidence_v242.json`.
- Bản kiểm tra có hash/độ phủ (Git ignored): `.tools/maizen_audio_full_v239/maizen_audio_audit_v242.json`.
- Audio Opus nguyên bản từ browser và các bản ASR/tiếng nói theo từng đoạn trong `.tools/maizen_audio_full_v239/`, **không commit dữ liệu video/âm thanh bên thứ ba vào Git**.
- Hình đã phát/chụp theo timeline: `docs/MAIZEN_ORIGINAL_BROWSER_FULL_TIMELINE_STUDY_V237_20261011.md`.
