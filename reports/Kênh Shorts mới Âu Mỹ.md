# Kênh Shorts 15 ngày chưa chạm trăm triệu

Trả lời thẳng: quét 2.360 kênh bằng YouTube Data API và đối chiếu bảng xếp hạng vidIQ, Tubefilter, NoxInfluencer ngày 13/11/2026 **không tìm thấy kênh Shorts nào lập trong 15 ngày qua, nhắm Mỹ hoặc châu Âu, mà đã có ≥100 triệu view** (OBSERVED-API + OBSERVED-vidIQ). Kênh ≤15 ngày lớn nhất ở nhóm Mỹ/EU là **Copycat Cuties: 76,0 triệu view sau 12 ngày, nội dung em bé AI** (OBSERVED-API). Trên toàn cầu chỉ có 2 kênh ≤15 ngày vượt 100 triệu, đều ngoài Mỹ/EU: Rô Tới Chơi (Việt Nam, 117,7 triệu) và CuddlePop (Ấn Độ, tiếng Anh, em bé AI, 116,9 triệu, gần như nhờ một video duy nhất). **Không kênh ≤15 ngày nào ở bất kỳ đâu chạm 1 tỷ.** Nới tuổi kênh lên 27–36 ngày thì dải "vài trăm triệu đến một tỷ" mới xuất hiện, với năm kênh: hai kênh GTA6 tiêu đề tiếng Trung nhưng đặt quốc gia Mỹ (1,08 tỷ và 463 triệu), GlowStrike (253 triệu, có dấu hiệu quảng cáo trả tiền), Te Cuento Blox (192 triệu, truyện kiểu Roblox tiếng Tây Ban Nha) và LumaRein (181 triệu, phễu affiliate đồ cưỡi ngựa). CINE không nên chép nguyên kênh nào trong năm kênh này: GTA/Rockstar và Roblox là IP của người khác, còn hai kênh Canada là mô hình bán hàng chứ không phải mô hình nội dung. Thứ đáng mang về là **định dạng "thị trấn có một luật lạ"**: Te Cuento Blox đạt trung vị 1,73 triệu view mỗi video và đang tăng khoảng 11 triệu view mỗi ngày, còn bản tiếng Việt Rô Tới Chơi đạt 117,7 triệu trong 14 ngày. CINE có thể làm lại định dạng này bằng tiếng Anh với dàn nhân vật khối do mình tự tạo. Tiền từ Shorts vẫn nhỏ, nên các kênh này chứng minh khả năng được phân phối, chưa chứng minh doanh thu.

*Nhãn số liệu dùng trong báo cáo:*

- **OBSERVED-API**: đọc bằng YouTube Data API v3 trên máy của chủ kênh ngày 13/11/2026, khoảng 19:00 giờ Việt Nam.
- **OBSERVED-vidIQ / Tubefilter**: con số trang tracker hiển thị, kèm ngày cập nhật của trang.
- **INFERRED**: phép tính hoặc suy luận của người viết.
- **ESTIMATED**: ước tính có giả định đi kèm.
- **VENDOR CLAIM**: số do công ty bán dịch vụ hoặc MCN công bố.

Dữ liệu thô nằm trong thư mục [new_channel_hunt_2026-11-13](research/new_channel_hunt_2026-11-13/).

## Ở mốc 15 ngày, Mỹ và châu Âu dừng ở 76 triệu view

**Phạm vi quét.** Bốn lượt quét API trong ngày gom được **2.360 kênh khác nhau**, trong đó **51 kênh lập ≤15 ngày** (OBSERVED-API, [channels_merged.json](research/new_channel_hunt_2026-11-13/channels_merged.json)). Trong 51 kênh này, **18 kênh có ≥10 triệu view, 2 kênh có ≥100 triệu và 0 kênh có ≥1 tỷ**. Mẫu này đã lệch về phía kênh thắng, vì search.list được sắp theo lượt xem, nên tỷ lệ thật trong toàn bộ kênh mới còn thấp hơn nhiều (INFERRED). Bảng dưới liệt kê các kênh ≤15 ngày lớn nhất. Tuổi kênh tính từ `channels.snippet.publishedAt`.

| Kênh | Tuổi | Quốc gia đặt | View kênh | Video | Sub | Video lớn nhất | Nội dung |
|---|---|---|---|---|---|---|---|
| Rô Tới Chơi | 14 ngày | VN | 117,7 triệu | 33 | 152K | 5,5 triệu | Truyện tiếng Việt 2–3 phút, "Thị trấn mỗi ngày chỉ được nói mười từ" |
| CuddlePop | 10 ngày | IN | 116,9 triệu | 6 | 39K | 120 triệu | Em bé AI giống thật |
| **Copycat Cuties** | 12 ngày | **US** | **76,0 triệu** | 80 | 21,7K | 22,9 triệu | Em bé AI "bắt chước" |
| Baby Bo | 15 ngày | US | 52,9 triệu | 20 | 50,7K | 27,9 triệu | Em bé AI |
| WonderSnapp | 13 ngày | trống | 39,8 triệu | 7 | 16,5K | 23,0 triệu | Em bé AI |
| Old Guy Energy | 11 ngày | ES (tiếng Anh) | 29,2 triệu | 7 | 6,8K | 10,4 triệu | Ông bà và em bé AI; trung vị 1,85 triệu/video |
| Rycroft Willians | 14 ngày | trống | 28,9 triệu | 25 | 13,5K | 12,4 triệu | Em bé AI |
| Baby Bloom | 7 ngày | US | 24,4 triệu | 5 | 7,0K | 26,3 triệu | Em bé AI |
| Ghibli Tales | 9 ngày | trống | 21,6 triệu | 8 | 37K | 21,7 triệu | Vườn tược AI mượn tên và phong cách Ghibli |
| Casper Cat | 10 ngày | trống | 21,5 triệu | 6 | 57,4K | 8,2 triệu | Phim tình cảm mèo AI |
| **Tekto Explains** | 13 ngày | CY (thấy trong feed Mỹ) | 16,7 triệu | 13 | 30,5K | 16,2 triệu | Giải thích 3D "How To Build a Nuclear Bunker" |
| VEXOMORPH | 11 ngày | US | 15,3 triệu | 19 | 11,9K | 6,0 triệu | Xe biến hình |

*Nguồn: OBSERVED-API. Ở CuddlePop và Baby Bloom, video lớn nhất nhiều hơn tổng view kênh vì hai con số được đọc bằng hai lệnh gọi ở hai thời điểm khác nhau (INFERRED).*

**Thành phần của nhóm đầu bảng.** Tám trong mười hai kênh là em bé hoặc động vật AI giống thật. Cách các kênh đạt con số cũng khác nhau:

- **CuddlePop** gần như chỉ dựa vào một video 120 triệu view, tức là trúng một lần chứ chưa thành kênh.
- **Rô Tới Chơi** thì ngược lại: video lớn nhất chỉ chiếm khoảng 5% tổng view, vì 5,5 triệu chia cho 117,7 triệu (INFERRED). Kênh này thắng đều trên cả 33 video.
- **Tekto Explains** là kênh đáng chú ý nhất cho CINE: like/view 2,16% và 2.630 bình luận, cho thấy khán giả tương tác thật (OBSERVED-API).
- **GOPLUS** đã bị loại khỏi danh sách. Kênh này có 254 triệu view sau 24 ngày, nhưng like 0,00% và chỉ 7 bình luận trên một video 87 triệu view: đó là quảng cáo ứng dụng tìm phòng, không phải kênh nội dung (OBSERVED-API).

**Tracker cũng không thấy kênh nào khớp.** Danh sách "fastest growing" của vidIQ cho 11 quốc gia (US, GB, DE, FR, ES, IT, NL, PL, SE, CA, AU) **không có kênh nào lập từ 29/10 trở đi với ≥100 triệu view**. Ở DE, FR, IT, PL, SE và GB, các dòng trông như kênh mới đều dưới khoảng 35 triệu view, ví dụ "Unhinged" (DE) 33,8 triệu và "John Ranking" (SE) 33,68 triệu (OBSERVED-vidIQ, [vidIQ US](https://vidiq.com/youtube-stats/top/country/us/fastest-growing-youtube-channels/), [vidIQ DE](https://vidiq.com/youtube-stats/top/country/de/fastest-growing-youtube-channels/)).

**Bảng xếp hạng mostPopular cũng vậy.** 14 khu vực Mỹ/EU trả về 1.792 video, chủ yếu là kênh "Topic" âm nhạc tự động và các creator lâu năm. Kênh không phải "Topic" trẻ nhất là FrabyESP (Tây Ban Nha, 15 ngày, 33,3 triệu) (OBSERVED-API, [mostpopular_us_eu.json](research/new_channel_hunt_2026-11-13/mostpopular_us_eu.json)).

## Nới lên 27–36 ngày, năm kênh vào dải trăm triệu đến tỷ

Năm ứng viên từ vidIQ đã được kiểm lại bằng API: `channels.list forHandle`, 50 video gần nhất qua `playlistItems`, và thống kê qua `videos.list`. Ngày lập kênh trên API khớp với ngày "Joined" vidIQ hiển thị.

**Cách đọc các cột trong bảng:**

- **Trung vị** và **tỷ trọng video top** đo độ đều: trung vị cao cùng tỷ trọng thấp nghĩa là kênh thắng lặp lại.
- **Tốc độ gần đây** lấy hiệu giữa số vidIQ (ngày ghi kèm) và số API tối 13/11. Hai nguồn đo ở hai thời điểm, nên đây là ước lượng thô (INFERRED).

| Kênh | Lập ngày (tuổi) | Quốc gia đặt | View (API 13/11) | Video | Sub | Trung vị/50 video gần nhất | Video top chiếm | Video ≥1 triệu trong 50 | Like/view | Tốc độ gần đây |
|---|---|---|---|---|---|---|---|---|---|---|
| GTA6-罪恶都市 | 14/10 (30 ngày) | US | **1.077.063.775** | 115 | 544K | 1,18 triệu | 17% | 28 | 0,88% | khoảng 7,9 triệu/ngày trong 13 ngày gần nhất, so với trung bình 35,9 triệu/ngày cả đời kênh |
| GTA6 (@gta6-w7m) | 14/10 (30 ngày) | US | **462.850.321** | 123 | 506K | 645K | 54% | 19 | 1,50% | +93,5 triệu trong 7 ngày, khoảng 13,4 triệu/ngày |
| GlowStrike | 08/10 (36 ngày) | CA | **253.151.259** | 54 | 117K | 129K | 70% (top 3: 94%) | 8 | 0,38% | +14,6 triệu trong 9 ngày, khoảng 1,6 triệu/ngày |
| **Te Cuento Blox** | 10/10 (34 ngày) | ES | **191.635.563** | 97 | 205K | **1,73 triệu** | **8%** | **38** | 1,85% | **+43,7 triệu trong 4 ngày, khoảng 10,9 triệu/ngày** |
| LumaRein | 17/10 (27 ngày) | CA | **180.517.905** | 72 | 128K | 178K | 25% (top 3: 64%) | 11 | 0,67% | +40,8 triệu trong 9 ngày, khoảng 4,5 triệu/ngày |

*Nguồn:*

- *Các cột số liệu kênh và video: OBSERVED-API, [tracker_candidates_verify.json](research/new_channel_hunt_2026-11-13/tracker_candidates_verify.json).*
- *Mốc vidIQ để tính tốc độ: OBSERVED-vidIQ, [GTA6-罪恶都市](https://vidiq.com/youtube-stats/channel/@gta6-%E7%BD%AA%E6%81%B6%E9%83%BD%E5%B8%82/), [GTA6](https://vidiq.com/youtube-stats/channel/@gta6-w7m/) (369,4 triệu ngày 6/11), [GlowStrike](https://vidiq.com/youtube-stats/channel/@glowstrikeshop/) (238,6 triệu ngày 4/11), [Te Cuento Blox](https://vidiq.com/youtube-stats/channel/@tecuentoblox/) (147,9 triệu ngày 9/11), [LumaRein](https://vidiq.com/youtube-stats/channel/@lumarein/) (139,7 triệu ngày 4/11).*
- *Cột tốc độ gần đây và tỷ lệ phần trăm: INFERRED.*

### Hai kênh GTA6: lượng view thật nhưng là IP của Rockstar và có dấu hiệu chạy theo cụm

**Nội dung.** Cả hai kênh đăng clip 29–59 giây gắn nhãn GTA6:

- **GTA6-罪恶都市:** 36 trong 50 video không có thẻ ngôn ngữ, tiêu đề chỉ có hashtag "#gta #gta6 #shorts". Video lớn nhất trong 50 video gần nhất đạt 17,2 triệu.
- **@gta6-w7m:** tiêu đề tiếng Trung kể chuyện nhỏ, ví dụ "小狗该如何选择？" (chú chó nên chọn thế nào?, 57,5 triệu) và "露西娅被欺负" (Lucia bị bắt nạt) (OBSERVED-API).

**View có vẻ tự nhiên.** Like/view gần như không đổi giữa video lớn nhất (0,89%) và phần còn lại (0,86%). Không có video nào phình bất thường so với mặt bằng, nên lượng view trông giống phân phối thuật toán tự nhiên hơn là quảng cáo (INFERRED).

**Đà tăng đang giảm.** 50 video gần nhất, đăng từ 31/10 đến 12/11, chỉ cộng lại khoảng 103 triệu. Như vậy khoảng 974 triệu view đến từ 65 video đầu, và vidIQ ghi nhận hai video 85,4 triệu và 82,1 triệu đăng ngày 16/10 và 25/10. Đỉnh của kênh rơi vào hai tuần đầu (INFERRED).

**Dấu hiệu cùng một chủ.** Hai kênh được tạo cùng ngày 14/10/2026, lúc **11:09:14 và 11:50:47 UTC**, cách nhau 41 phút (OBSERVED-API). Rất có thể chúng cùng một người vận hành hoặc cùng một mạng kênh (INFERRED). Kiểu mạng kênh dùng chung khuôn này đúng là thứ hệ thống nghiên cứu cắt kênh theo cụm của Google nhắm tới: hệ thống đó được báo cáo đã cắt 50.000 cụm gồm 130.000 kênh trong sáu tháng ([Fstoppers](https://fstoppers.com/artificial-intelligence/how-google-machine-terminated-130000-ai-slop-youtube-channels-six-months-903645)).

**Nguồn gốc khán giả chưa rõ.** Quốc gia "US" là thông tin chủ kênh tự khai, trong khi tiêu đề tiếng Trung cho thấy người vận hành khó có thể ở Mỹ.

**Nguồn gốc hình ảnh chưa rõ.** Chưa biết đây là trailer cắt lại, bản mod hay hình AI. Cần một người xem trực tiếp trên YouTube, vì quy tắc CINE cấm tải video của bên thứ ba.

**Với CINE: không làm.** Lý do là IP Rockstar/Take-Two cùng rủi ro nội dung tái sử dụng. Bài học đáng giữ là thời điểm: sức kéo của một sự kiện văn hóa lớn, không phải bản thân IP.

### Te Cuento Blox: kênh đều nhất và là định dạng duy nhất đáng học

**Nội dung.** Cả 50 video gần nhất đều là truyện tiếng Tây Ban Nha (es-419), thời lượng trung vị **123 giây**. Tiêu đề lặp một khung cố định:

- "En este pueblo, solo puedes decir 'NO' UNA vez en la vida…" (9,5 triệu)
- "En este pueblo, todos tienen un SUPERPODER… ¡pero solo UNA vez!" (8,4 triệu)
- "En este pueblo, si dices '¡ME LO PIDO!'… ¡es TUYO para siempre!" (8,3 triệu)

(OBSERVED-API)

**Độ đều.** Trong 50 video, **38 video vượt 1 triệu view, chỉ 1 video dưới 100K**, và video lớn nhất chỉ chiếm 8% tổng view. Like/view nằm trong khoảng 1,73–1,87% ở cả video top lẫn phần còn lại (OBSERVED-API). Đây là hình mẫu của lượng view tự nhiên: không có video nào bị đẩy bất thường, và kênh thắng nhờ khung truyện chứ không nhờ một cú may (INFERRED).

**Tốc độ.** Kênh đăng khoảng 2,9 video mỗi ngày (97 video trong 34 ngày). Từ ngày 9/11 đến tối 13/11, kênh tăng từ 83 lên 97 video và từ 165K lên 205K sub (OBSERVED-vidIQ → OBSERVED-API). Đà đang tăng chứ không giảm.

**Chuyển đổi view thành sub.** Te Cuento Blox cần khoảng 935 view cho mỗi sub. Hai kênh Canada cần khoảng 2.160 (GlowStrike) và 1.410 (LumaRein) (INFERRED, sub API đã làm tròn 3 chữ số).

**Với CINE.** Hình ảnh mang phong cách avatar Roblox, nên không làm theo phần hình. Tây Ban Nha có cả một cụm kênh truyện Roblox: Foline studio lập tháng 7/2026, có 91 triệu view (OBSERVED-vidIQ, [Foline studio](https://vidiq.com/youtube-stats/channel/@folinestudio/)). **Khung "thị trấn có một luật" thì không thuộc IP của ai**, và đó là phần CINE nên lấy (xem phần dưới).

### GlowStrike và LumaRein: phễu bán hàng, một kênh có dấu hiệu quảng cáo rõ

**GlowStrike.** Kênh đăng clip sản phẩm 11–15 giây, không có lời, chú thích "Link in bio! ⚡️🤩". Một video duy nhất có **176,6 triệu view với like chỉ 0,37%**. Ba video đầu chiếm 94% tổng view, trong khi 22 trong 50 video dưới 100K (OBSERVED-API).

Kiểu phân bố này khớp với dấu hiệu quảng cáo trả tiền:

- View quảng cáo được cộng vào view công khai ngay khi quảng cáo Shorts bắt đầu phát ([YouTube Help 2991785](https://support.google.com/youtube/answer/2991785?hl=en), [Google Ads Help](http://support.google.com/google-ads/answer/2375431?hl=en&ref_topic=10513217)).
- Người xem trả tiền hiếm khi bấm like hoặc đăng ký.

Không chứng minh được bằng API, vì API không có trường "view từ quảng cáo". Kết luận ở mức INFERRED: **khả năng cao là có quảng cáo**.

**LumaRein.** Kênh đăng clip đồ cưỡi ngựa 14 giây với câu kêu gọi "Comment 'Horse' if you need these for your horse… #usa". Ba video 18,6–25,9 triệu view được đăng sát nhau trong ba ngày 24–26/10, còn 22 trong 50 video dưới 100K (OBSERVED-API). Đây là phễu "bình luận từ khóa để nhận link" kiểu ManyChat (INFERRED). Có thể có một phần quảng cáo, nhưng like 0,53–0,78% không thấp bất thường như GlowStrike.

**Với CINE: không làm cả hai kênh.** Doanh thu của chúng đến từ bán hàng hoặc hoa hồng chứ không phải AdSense. Clip nhiều khả năng lấy từ nhà cung cấp (INFERRED), và không có nhân vật hay IP gốc nào để tích lũy.

## Kênh trăm triệu sau 15 ngày hiếm vì cả thuật toán lẫn công cụ đo

**Tỷ lệ nền rất thấp.** Một nghiên cứu theo dõi **475 kênh Shorts mới ở Nhật** cho thấy trung vị tổng view chỉ khoảng **26 nghìn**, và **không kênh nào chạm 20 triệu** ([Zenn, 3/11/2026](https://zenn.dev/acerola_jp/articles/youtube-shorts-new-channel-hit-rate?locale=en)). So với mức nền đó, 100 triệu view trong 15 ngày là ngoại lệ cực đoan. Ngay trong mẫu đã lọc sẵn kênh thắng của CINE, chỉ 2 trong 51 kênh ≤15 ngày làm được (OBSERVED-API).

**Kiểu "tỷ view trong vài tuần" thuộc về giai đoạn 2025.** Khi đó các kênh AI rác đạt 1–2 tỷ view trong vài tháng. Ví dụ Bandar Apna Dost có 2,07 tỷ view, và Kapwing ước tính kênh này thu khoảng 4,25 triệu USD mỗi năm, nhưng đó là ước tính của Kapwing dựa trên Social Blade ([Kapwing](https://www.kapwing.com/blog/ai-slop-report-the-global-rise-of-low-quality-ai-videos/)). Sau đó YouTube siết dần:

- **Tháng 1/2026:** xóa hoặc xóa sạch nội dung của 16 trong 100 kênh AI rác hàng đầu theo danh sách Kapwing ([The Verge](https://www.theverge.com/news/869684/youtube-top-ai-channels-removed-kapwing)).
- **16/7/2026:** chia nội dung "không chân thực" thành ba nhóm không được kiếm tiền. Nhóm 1 là nội dung chung chung, lặp lại hoặc theo khuôn mẫu. Nhóm 2 là nội dung gây khó chịu hoặc thao túng cảm xúc. Nhóm 3 là persona AI nói về chủ đề nhạy cảm ([TechCrunch](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/)).

**Những kênh tỷ view năm 2026 hầu hết là kênh cũ đổi hướng**, nên trông như kênh mới trên bảng tăng trưởng. API xác nhận:

- **SASHA SHOW** lập năm 2022, có 1,74 tỷ view, và cả 50 video gần nhất đều đăng từ 3/9/2026 (OBSERVED-API).
- **Lucan Pevidor** lập năm 2021, có 18,5 tỷ view (OBSERVED-API).

vidIQ còn cho thấy thêm các kênh tỷ view nhưng không mới:

- YamalXeo lập 7/2026, có 1,89 tỷ view.
- GreenBroRants (Mỹ) lập 10/2025, có 1,12 tỷ view.
- Haaland - KPOP (Mỹ) lập 1/2026, có 665 triệu view.
- **OddFrame** (Úc) lập 11/2025, có 256 triệu view từ các Short giải thích Thế chiến 2 và kỹ thuật. Đây là bằng chứng rằng dòng giải thích của CINE cũng lên được hàng trăm triệu, nhưng mất cả năm chứ không phải 15 ngày (OBSERVED-vidIQ, [OddFrame](https://vidiq.com/youtube-stats/channel/@oddframefilms67/), [YamalXeo](https://vidiq.com/youtube-stats/channel/@yamalxeo/), [GreenBroRants](https://vidiq.com/youtube-stats/channel/@greenbrorants/)).

**Cách đếm view mới làm tổng view phình lên.** Từ **24/8/2026**, view được tính ngay khi video bắt đầu phát, kể cả tự động phát ([Channels resource](https://developers.google.com/youtube/data/reference/rest/v3/channels)). Một bên bán dịch vụ đo được like/view của kênh trung vị giảm 41% sau thay đổi này (VENDOR CLAIM, [SociaVault](https://sociavault.com/blog/youtube-data-api-quota-2026)). Hệ quả là "100 triệu view" tháng 11/2026 không so ngang được với 100 triệu năm 2025, và ngưỡng like/view dùng để soi quảng cáo phải so với trung vị cùng đợt quét chứ không dùng số cố định (INFERRED).

### Công cụ nào cũng có điểm mù

**search.list là công cụ lấy mẫu, không phải danh bạ:**

- Google cảnh báo rằng sắp xếp khác "relevance", nhất là khi kèm `publishedAfter`, "might result in a smaller or incomplete result set" ([search.list reference](https://developers.google.com/youtube/data/reference/rest/v3/search/list)).
- `regionCode` chỉ có nghĩa là video **xem được** ở quốc gia đó, không phải creator ở đó.
- `videoDuration=short` nghĩa là dưới 4 phút, không đồng nghĩa với Shorts.
- Hai nghiên cứu kiểm toán độc lập thấy kết quả bị ngẫu nhiên hóa, lệch về video mới và video phổ biến, và không lặp lại được giữa các lần gọi ([Efstratiou, IMC 2025](https://arxiv.org/abs/2506.04422); [Rieder và cộng sự 2025](https://arxiv.org/html/2506.11727v2)).
- Nghiên cứu Nhật ở trên cũng ghi nhận rằng tìm theo "video mới đăng" chủ yếu trả về kênh cũ.

**Tracker cũng có giới hạn riêng:**

- vidIQ chỉ đưa một kênh vào danh sách sau khi đã có ảnh chụp số liệu ban đầu và đủ lọt top 100. Một kênh lập sau 29/10 có thể chưa xuất hiện dù đã lớn ([vidIQ fastest growing](https://vidiq.com/youtube-stats/top/fastest-growing-youtube-channels/)).
- Quốc gia trên mọi tracker là quốc gia chủ kênh tự khai.
- Social Blade và Playboard bị proxy chặn từ môi trường làm việc, nên **chưa đo được**.
- `chart=mostPopular` từ 21/7/2025 chỉ còn Music, Movies và Gaming ([Revision History](https://developers.google.com/youtube/v3/revision_history?authuser=1)). Vì vậy nó gần như vô dụng để săn kênh Shorts mới ngoài âm nhạc và game, và kết quả quét hôm nay khớp đúng như vậy.

### Cách đã quét và giới hạn quota

Bốn script chạy trên máy của chủ kênh. Key đọc từ `.env` và không in ra.

| Script | Đầu vào | Kết quả | Chi phí ghi trong log |
|---|---|---|---|
| `cf_new_channel_hunt.py` | 24 từ khóa tiếng Anh, mỗi từ chạy dạng Shorts và dạng mọi độ dài; kèm dữ liệu xuất từ Tube Atlas | 2.259 video, 1.504 kênh | khoảng 4.877 unit |
| `cf_mega_new_channel_hunt.py` | Feed theo khu vực, không có từ khóa, cho 14 nước (US, IN, BR, ID, MX, PH, GB, DE, JP, KR, VN, TH, EG, PK); kèm 20 từ khóa chung | 1.250 video, 967 kênh | khoảng 3.845 unit |
| `cf_us_eu_new_channel_deep.py` | Feed khu vực CA, AU, FR, ES, IT, NL, PL, SE, BE; kéo 50 video gần nhất của 45 kênh đầu | | khoảng 997 unit |
| `cf_mostpopular_us_eu.py` | `chart=mostPopular` cho 14 khu vực Mỹ/EU | 1.792 video | 90 unit |

Sau khi gộp, mọi kênh đều qua `channels.list` để lấy `publishedAt`, quốc gia, view và sub (OBSERVED, [own_api_data](../research_notes/Kênh%20Shorts%20mới%20Âu%20Mỹ/own_api_data.md)).

**Quy tắc quota từ 1/6/2026:**

- search.list có **xô quota riêng, mặc định 100 lệnh gọi mỗi ngày, mỗi lệnh tốn 1**. Mỗi trang kết quả thêm tính là một lệnh.
- Các endpoint khác dùng chung 10.000 unit.
- Quota reset lúc nửa đêm giờ Thái Bình Dương, tức **15:00 giờ Việt Nam** khi đang áp dụng giờ PST ([Quota Calculator](https://developers.google.com/youtube/data/determine_quota_cost)).

**Log hôm nay ghi sai cách tính.** Các script vẫn tính mỗi lệnh search là 100 unit theo quy tắc trước tháng 6. Vì thế con số "khoảng 9.800 trên 10.000 unit" trong log bị thổi phồng. Ràng buộc thật hôm nay là **khoảng 95 trên 100 lệnh search** đã dùng (INFERRED từ số lệnh của từng lượt chạy). Sửa cách tính này là việc của pipeline-engineer, làm trên một nhánh riêng kèm pytest.

## "Thị trấn có một luật lạ" là định dạng đáng mang về nhất

**Hai ngôn ngữ, hai thị trường, cùng một khung.** Định dạng này xuất hiện độc lập ở hai nơi:

- **Te Cuento Blox (Tây Ban Nha):** "En este pueblo…", 192 triệu view sau 34 ngày, trung vị 1,73 triệu mỗi video.
- **Rô Tới Chơi (Việt Nam):** "Thị trấn mỗi ngày chỉ được nói mười từ", 117,7 triệu view sau 14 ngày, 33 video, video top chỉ chiếm khoảng 5% (OBSERVED-API).

Khi cùng một khung thắng ở hai thị trường không liên quan, khả năng cao sức hút nằm ở khung truyện chứ không ở hình ảnh hay ngôn ngữ (INFERRED).

**Vì sao khung này hiệu quả (INFERRED).** Tiêu đề đã chứa sẵn một luật và cái giá phải trả. Người xem lập tức tự hỏi "nếu là mình thì sao?" và ở lại để xem nhân vật lách luật thế nào. Mỗi tập chỉ cần một luật mới, nên ý tưởng gần như vô tận, rẻ để nghĩ, mà vẫn có cấu trúc nhân quả thật: luật → vi phạm → hậu quả → cú ngoặt.

**Đề xuất cho CINE.** Làm một bản **tiếng Anh, IP gốc, dàn nhân vật khối của CINE dựng trong Blender 4.5**, dài 90–150 giây theo trung vị của Te Cuento Blox. Luật phải do CINE tự nghĩ, không lấy luật của họ. Hai ví dụ minh họa, chưa thẩm định: "In this town, every lie turns one hair blue", "In this town, you pay for bread with a memory".

**Hai rủi ro cần chặn trước:**

- **Nhóm 1 "theo khuôn mẫu" của chính sách 16/7/2026.** Mỗi tập phải là một câu chuyện viết thật, có nhân vật quen thuộc và diễn biến mới, chứ không phải tiêu đề thay chữ trên cùng một mạch truyện.
- **Phân loại "Made for Kids"** nếu hình ảnh khối quá trẻ con.

**Các định dạng Mỹ/EU khác tương thích với CINE.** Lượt quét sâu 50 video gần nhất của các kênh Mỹ/EU ≤30 ngày cho thấy những kênh hợp năng lực CINE có hai đặc điểm chung: tỷ trọng video top thấp và like khoảng 2–4%. Như vậy là thắng lặp lại, khán giả thật (INFERRED từ OBSERVED-API, [us_eu_deep.json](research/new_channel_hunt_2026-11-13/us_eu_deep.json)).

| Định dạng | Kênh bằng chứng (tuổi, view, chỉ số) | Vì sao hợp CINE |
|---|---|---|
| Giải thích phát minh / "what to do if" / "how to build" | Stumblework Studios (19 ngày, 3,1 triệu, **18,6K sub, like 4,06%**, "You Just Invented the Sewing Machine"); ¿Qué hacer si…? (15 ngày, 27,1 triệu, trung vị 382K); Tekto Explains (13 ngày, 16,7 triệu, like 2,16%) | Hợp Blender 3D, không lỗi thời, dẫn được sang phim tài liệu dài 10–20 phút |
| Hợp nhất tới "Final Form" | Endform TV (DE, 22 ngày, 6,3 triệu); Memeland (23 ngày, 31,6 triệu); Super Balls 3000 (FR, 21 ngày, 5,5 triệu) | Chuỗi khối hợp nhất dễ dựng hàng loạt, đổi chủ đề liên tục |
| Dàn nhân vật khối thi đấu | Mochi & Pals (29 ngày, 9,8 triệu, trung vị 204K, top 29%) | Dàn nhân vật gốc kiểu Minecraft, đúng lane S1 |
| Truyện kinh dị siêu ngắn có mối đe dọa đếm ngược | lulu fah stories (27 ngày, 46 triệu, **319K sub**, like 2,8%, "The Snowman MOVED Closer Every NIGHT") | Kinh dị Minecraft với nhân vật gốc; chuyển đổi sub rất tốt, khoảng 144 view mỗi sub (INFERRED) |

**Vì sao chỉ số "view mỗi sub" quan trọng.** Kênh có dàn nhân vật lặp lại chuyển đổi khán giả tốt gấp mười đến vài chục lần kênh clip ẩn danh:

| Kênh | Loại | View cần cho mỗi sub (INFERRED) |
|---|---|---|
| Crazyfunnybloxx | Có dàn nhân vật | khoảng 98 |
| lulu fah stories | Có dàn nhân vật | khoảng 144 |
| GTA6-罪恶都市 | Clip ẩn danh | khoảng 1.980 |
| Copycat Cuties | Clip ẩn danh | khoảng 3.500 |

Đó là lý do khung "thị trấn có luật lạ" nên đi cùng một dàn nhân vật cố định chứ không đứng riêng.

### Tiền thật sự nhỏ hơn con số view gợi ý

**RPM Shorts.** Theo dữ liệu Analytics của 274 kênh do một MCN công bố, Shorts trả khoảng **0,328 USD cho 1.000 view với khán giả Mỹ**, còn phần lớn ngách chỉ khoảng **0,07–0,20 USD** (VENDOR CLAIM, [AIR Media-Tech](https://air.io/en/air-data-findings/youtube-shorts-rpm-vs-long-form-how-much-do-shorts-earn-in-2026)). Một bên khác ghi nhận chỉ 45,7% view công khai là view "engaged" được tính tiền (VENDOR CLAIM, [MilX](https://milx.app/en/cases/how-much-do-youtube-shorts-pay-to-successful-creators)).

**Ước tính cho 100 triệu view.** Gộp hai con số trên, 100 triệu view công khai mang về khoảng **3.000–33.000 USD** sau khi đã vào YPP. Khoảng rộng vì phụ thuộc tỷ lệ view engaged và cơ cấu quốc gia của khán giả (ESTIMATED). Để so sánh: SASHA SHOW có khoảng 640 triệu view trong 28 ngày, nhưng vidIQ mô hình hóa doanh thu quảng cáo chỉ khoảng 17.000 USD (OBSERVED-vidIQ, [vidIQ](https://vidiq.com/youtube-stats/channel/@sashashowbro/about/)).

**Ngưỡng YPP từ 1/2/2027:**

- Kênh mới cần **1.000 sub cộng 20 triệu view Shorts hợp lệ trong 90 ngày**, hoặc 8.000 giờ xem trong 365 ngày.
- Để tiếp tục nhận tiền từ quỹ Shorts, kênh phải **duy trì 10 triệu view Shorts trong 90 ngày gần nhất**.
- Creator nhận 45% quỹ Shorts, so với 55% ở video dài.

([YouTube Blog](https://blog.youtube/news-and-events/youTube-partner-program-updates-2027-new-opportunities-earn), [YouTube Help 12843009](https://support.google.com/youtube/answer/12843009), [Newsshooter](https://www.newsshooter.com/2026/08/10/youtube-updates-its-partner-program))

**Rủi ro ở bước xét duyệt.** Một kênh em bé AI có thể vượt ngưỡng view rất nhanh, nhưng vẫn phải qua xét duyệt thủ công theo ba nhóm chính sách tháng 7/2026. Thêm vào đó, từ 27/5/2026 YouTube tự gắn nhãn AI cho video giống thật mà creator không tự khai ([YouTube Blog](http://blog.youtube/news-and-events/improving-ai-labels-viewers-creators)).

**Với CINE**, Shorts là phễu kéo khán giả. Tiền nằm ở video dài, ở Shopping và ở thương hiệu có nhân vật (INFERRED).

## Kế hoạch chạy API sau 15:00 ngày mai

**Mục tiêu.** Chạy lại đúng câu hỏi của chủ kênh, lấy mốc ngày chạy trừ 15 ngày. Song song, đo tốc độ 24 giờ của các ứng viên đã biết. Ngân sách là 100 lệnh search, 10.000 unit cho các endpoint khác, và xô `videos.batchGetStats` riêng 10.000 unit ([Revision History](https://developers.google.com/youtube/v3/revision_history)). Lệnh search đầu tiên phải tự kiểm tra xem search không có `q` kèm `order=viewCount` và `publishedAfter` có còn trả kết quả không. Mọi lệnh gọi phải ghi lại tham số, số item trả về và trạng thái `nextPageToken`.

| Bước | Lệnh gọi | Số lệnh | Quota |
|---|---|---|---|
| 0 | Kéo lại `channels.list` cho khoảng 110 kênh đã biết (51 kênh ≤15 ngày, 5 kênh trong cửa sổ, 45 kênh Mỹ/EU sâu, kênh đối chứng), rồi `playlistItems` 50 video cho khoảng 20 kênh đầu → tốc độ 24 giờ | 3 + 20 | khoảng 23 unit |
| 1 | search.list, không `q`, `type=video`, `videoDuration=short`, `order=viewCount`, `publishedAfter=ngày chạy−15`, `maxResults=50` × khu vực US, GB, IE, DE, FR, ES, IT, NL, PL, SE, CA, AU (ghép `relevanceLanguage` tương ứng), trang 1–2 | khoảng 24 | 24 lệnh search |
| 2 | Chia cửa sổ thời gian 0–5, 5–10, 10–15 ngày cho US/en, GB/en, ES/es, trang 1 | 9 | 9 lệnh search |
| 3 | Họ từ khóa định dạng × US/en, trang 1: "in this town", "only once in your life", "en este pueblo", "you just invented", "what to do if", "how to build", "final form", "who can build", "moved closer every night", "#gta6", "link in bio", "comment to get the link"… | khoảng 35 | 35 lệnh search |
| 4 | Dự phòng: kiểm tiêu đề trùng (tiêu đề đặt trong ngoặc kép), từ khóa mới nảy ra từ bước 1–3 | khoảng 25 | 25 lệnh search |
| 5 | `videos.list` cho mọi ID (50 mỗi lệnh), rồi `channels.list` cho mọi channelId mới | khoảng 150 | khoảng 150 unit |
| 6 | Playlist UUSH/UU cho các kênh qua vòng lọc: ngày đăng video đầu tiên, tỷ lệ Shorts, view từng video | ≤300 | ≤300 unit |
| 7 | Nguồn ngoài API: danh sách vidIQ fastest-growing cho US, CA, GB, ES; Tubefilter tuần; quy về handle bằng `forHandle` | — | khoảng 20 unit |

**Quy tắc giữ kênh hạng A** (khớp đúng câu hỏi của chủ kênh). Kênh phải đạt tất cả điều kiện sau:

- `publishedAt` trong vòng 15 ngày tính đến ngày chạy.
- Video đầu tiên cũng nằm trong 15 ngày đó, để loại kênh cũ được mua lại hoặc hồi sinh.
- View kênh ≥100 triệu.
- Có ít nhất 80% video trong mẫu dài ≤180 giây hoặc nằm trong playlist UUSH.
- Có bằng chứng Mỹ/EU: quốc gia đặt thuộc US/EU/CA/AU, cộng với ngôn ngữ âm thanh hoặc tiêu đề phương Tây.
- Không bị gắn cờ quảng cáo hoặc re-upload.

**Hạng B (theo dõi):** kênh ≤15 ngày đạt ≥10 triệu view, hoặc kênh ≤36 ngày đạt ≥100 triệu.

**Danh sách riêng (không tính là kênh mới):** kênh cũ đổi hướng như SASHA SHOW, và kênh "Topic" âm nhạc.

**Dấu hiệu nghi bị đẩy bằng quảng cáo.** Các dấu hiệu dưới đây được suy ra từ chính sách tính view của Google, và không dấu hiệu nào đủ để kết luận một mình (INFERRED):

| Dấu hiệu | Ngưỡng đề xuất | Ví dụ hôm nay |
|---|---|---|
| Like/view so với trung vị cùng đợt quét | dưới một nửa trung vị; dưới 0,1% coi như chắc chắn | GOPLUS 0,00%; GlowStrike 0,37% trên video 176,6 triệu |
| Video top chiếm tổng view | trên 50% và top 3 trên 80% | GlowStrike 70% và 94% |
| Phân bố hai cực | có video ≥10 triệu nhưng ≥40% video dưới 100K | GlowStrike, LumaRein (22/50 video dưới 100K) |
| View mỗi sub | trên khoảng 2.000 | GlowStrike khoảng 2.160 |
| Kênh thương hiệu hoặc ứng dụng | "Link in bio", tên sản phẩm, ứng dụng | GlowStrike, GOPLUS |
| Không xuất hiện trên bảng xếp hạng quốc gia | video hàng chục triệu nhưng vắng mặt trên Playboard, trends24 | Charts loại view quảng cáo ([YouTube Help 7239739](https://support.google.com/youtube/answer/7239739?hl=en)) |
| Cụm kênh | nhiều kênh lập cách nhau vài phút, cùng khuôn | hai kênh GTA6 lập cách nhau 41 phút |

## Những quyết định chủ kênh cần chốt

Theo quy tắc CINE, các lựa chọn dưới đây thuộc về chủ kênh. Người viết chỉ đề xuất (INFERRED). Mỗi quyết định nên được ghi bằng `python tools/cf_decision.py add ...`.

| Quyết định | Lựa chọn | Đề xuất |
|---|---|---|
| Định nghĩa "kênh mới trăm triệu" cho các lượt quét tiếp theo | (a) giữ nghiêm ≤15 ngày và ≥100 triệu; (b) thêm hạng B (≤15 ngày ≥10 triệu, ≤36 ngày ≥100 triệu) | (b): hạng A rất có thể vẫn trả về 0 kênh |
| Có thử định dạng "thị trấn có một luật lạ" tiếng Anh, IP gốc không | thử 5–10 Short 90–150 giây bằng dàn nhân vật khối / chưa | Thử; showrunner viết luật gốc, qc-reviewer kiểm rủi ro "khuôn mẫu" và Made for Kids |
| Loại hẳn em bé AI, affiliate "comment để nhận link", IP GTA/Roblox | loại / giữ để theo dõi | Loại khỏi danh sách sản xuất; vẫn đo để làm mốc thị trường |
| Chia 100 lệnh search ngày mai | săn kênh rộng / tập trung từ khóa định dạng | Khoảng 33 rộng, 35 định dạng, 25 dự phòng như bảng trên |
| Quốc gia "US" nhưng tiêu đề tiếng Trung có tính là Mỹ không | tính / không | Không tính là kênh Mỹ/EU nếu không có ngôn ngữ phương Tây |

## Kết luận

Câu hỏi "kênh 15 ngày, trăm triệu đến tỷ view ở Mỹ/EU" hôm nay có đáp án là **không có**, và đáp án đó vẫn có giá trị. Nó cho thấy những con số hàng trăm triệu ở kênh mới phần lớn đến từ ba nguồn mà CINE không nên dựa vào: một video trúng may, quảng cáo trả tiền, hoặc mạng kênh vận hành theo cụm trên IP của người khác. Chỉ số đáng theo dõi không phải tổng view mà là **trung vị mỗi video, tỷ trọng video top và số view cần cho mỗi sub**. Theo ba chỉ số đó, Te Cuento Blox với 192 triệu view là kênh mạnh hơn GlowStrike với 253 triệu, và lulu fah stories với 46 triệu đáng học hơn Copycat Cuties với 76 triệu.

Với KPI "số phút thành phẩm được duyệt mỗi tuần", một khung truyện lặp được như "thị trấn có một luật lạ", đi cùng dàn nhân vật khối của CINE, là con đường ngắn nhất để biến tín hiệu thị trường thành sản lượng hằng ngày. Lượt quét sau 15:00 ngày mai, cùng lần kiểm lại vidIQ khoảng ngày 20/11, sẽ cho biết Te Cuento Blox có giữ được đà khoảng 11 triệu view/ngày và có kênh Mỹ/EU nào lập sau 29/10 vượt ngưỡng hay không. Nếu vẫn không có, nên coi đó là kết quả đo được chứ không phải lỗi phương pháp.
