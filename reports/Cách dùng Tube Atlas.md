# Dùng Tube Atlas như máy cào dữ liệu

**Tube Atlas (tubeatlas.com) là một phần mềm desktop mua đứt chạy trên Windows/Mac, có 12 công cụ. Nó trích dữ liệu YouTube và Google ngay từ máy của bạn vào các bảng lọc được. Nó không phải kho ngách hay máy tìm outlier như TubeLab, 1of10 hay NexLev.** Học nó đúng cách nghĩa là học một vòng làm việc: gõ từ khoá hạt giống, xem xu hướng, thu video và kênh vào bảng, lọc/sắp xếp bằng tay, phân tích tag, tiêu đề và bình luận, rồi lưu hoặc xuất ra. Không có cột "outlier score", không có lọc RPM ngách, không có cờ faceless. Những thứ đó studio phải tự tính bằng `tools/cf_research_stats.py`. Giá là **$47 một lần với coupon TUBE20 (niêm yết $67), không có bản dùng thử, được hoàn tiền trong 30 ngày** (OBSERVED, trang bán hàng) ([tubeatlas.com](https://tubeatlas.com/)). Theo lịch sử phiên bản của nhà sản xuất, bản mới nhất là **1.0.6.7, phát hành ngày 12/11/2026** (OBSERVED). Bài review SaaSPic ngày 5/11/2026 ghi "1.0.6.6, không có bản nào từ tháng 4". Lịch sử của nhà sản xuất mới hơn nên được ưu tiên ([AppBreed version history](https://appbreed.com/apps/api/app-download.php?aid=26)). Còn một "Tube Atlas" thứ hai: repo mã nguồn mở `quyenmanhnguyen/tube-atlas-oss` (Streamlit + YouTube Data API + DeepSeek). Repo này có Outlier Finder thật, nhưng đã ngừng phát triển từ 29/4/2026 và có những phần vi phạm luật studio. **Owner cần xác nhận mình đang nói về cái nào.** Giáo trình này dạy cả hai, bản trả phí trước. Với CINE, chỉ nên dùng nhóm công cụ **đọc dữ liệu** (Keywords, Trends, Videos, Browse & Extract, Channels, Comments, Tag/Title Analyzer). Downloader, Content Spinner, quy trình "clone" bằng transcript, trích email/số điện thoại, Video Cloner và Grok Producer phải được đánh dấu **không dùng cho CINE**. Lý do sâu hơn nằm ở chỗ Tube Atlas lấy dữ liệu bằng cách cào trang web, trong khi Điều khoản YouTube cấm truy cập bằng "scrapers" ([YouTube Terms](https://www.youtube.com/static?template=terms)). Vì vậy quyết định mua và dùng ở mức nào là quyết định của owner, không phải của agent.

> **Nhãn số liệu.** **OBSERVED** là đọc được trên trang hoặc file được dẫn nguồn. **INFERRED** là suy luận của giáo trình. **ESTIMATED** là ước tính có giả định. **VENDOR CLAIM** là lời nhà bán tự nói, chưa ai kiểm chứng. Nghiên cứu này chỉ đọc: **không cài, không mua, không đăng nhập, không chạy** phần mềm nào. Vì vậy mọi đường bấm chuột cụ thể chỉ đến từ chữ của nhà sản xuất, ghi chú phiên bản, tiêu đề video hướng dẫn và các bài review. Những chỗ cần owner tự bấm thử được ghi là "chưa xác nhận". Ngày dữ liệu: 13/11/2026.

## Bài 0: Xác định đúng "Tube Atlas" và đúng phiên bản trước khi học

Có hai sản phẩm trùng tên, khác nhau hoàn toàn về bản chất. Nếu owner xem một video hướng dẫn có bảng "outlier ×5", điểm "Keyword Score kiểu VidIQ" hoặc nút "Clone", thì người trong video đang dùng bản mã nguồn mở hoặc một công cụ khác như TubeLab, không phải tubeatlas.com (INFERRED).

| | **Tube Atlas (trả phí)** | **tube-atlas-oss (mã nguồn mở)** |
|---|---|---|
| Ai làm | AppBreed / Innantech Industries Inc. (Canada), lập trình viên Dave Guindon ([tubeatlas.com](https://tubeatlas.com/); [AppBreed Terms](https://appbreed.com/terms-and-conditions/)) | GitHub user quyenmanhnguyen (Nguyễn Mạnh Quyền); phần lớn commit do bot Devin AI viết ([repo](https://github.com/quyenmanhnguyen/tube-atlas-oss)) |
| Dạng | Phần mềm desktop Windows XP–11 / macOS 10.10+, viết bằng Delphi, không có bản cloud hay mobile | Ứng dụng web Streamlit chạy cục bộ (`streamlit run app.py`, cổng 8501), Python 3.10+ |
| Nguồn dữ liệu | Cào trang YouTube/Google qua trình duyệt tích hợp và autosuggest; không dùng khoá YouTube API (INFERRED từ changelog) | YouTube Data API v3 chính thức (cần khoá), cộng các thư viện cào: pytrends, youtube-comment-downloader, yt-dlp |
| AI | Chỉ có công cụ văn bản phụ (tóm tắt, tiêu đề, chấm câu) | DeepSeek là trung tâm (đánh giá ngách, kịch bản), Gemini dự phòng |
| Giá | $47 một lần (niêm yết $67) | Miễn phí (MIT), nhưng DeepSeek tính tiền theo lượng dùng |
| Phiên bản | **1.0.6.7, ngày 12/11/2026** (OBSERVED, [version history](https://appbreed.com/apps/api/app-download.php?aid=26)) | Commit master `f0b2a0d` ngày 29/4/2026; không có tag hay release ([repo](https://github.com/quyenmanhnguyen/tube-atlas-oss)) |
| Bảo trì | Chủ yếu vá lỗi khi YouTube đổi giao diện, nhịp chậm dần | Ngừng sau 5 ngày phát triển (25–29/4/2026) |

**Mâu thuẫn về phiên bản và cách xử lý.** SaaSPic (cập nhật 5/11/2026) ghi bản mới nhất là 1.0.6.6 ngày 12/4/2026 và "không có bản nào từ tháng 4" ([SaaSPic](https://saaspic.com/tools/tube-atlas/)). Trang lịch sử phiên bản chính thức thì ghi **1.0.6.7 (12/11/2026) là "Current available version"**, trước đó là 1.0.6.6 (12/4/2026) và 1.0.6.5 (5/1/2026) ([AppBreed version history](https://appbreed.com/apps/api/app-download.php?aid=26)). Lịch sử của nhà sản xuất là nguồn có thẩm quyền nhất và mới hơn review một tuần, nên giáo trình lấy **1.0.6.7** làm mốc. Bản này đáng chú ý vì bốn thay đổi: dữ liệu video "now extracts with half the requests" (ít bị giới hạn "too many requests" hơn); nút Auto punctuate chạy **offline cho tiếng Anh**; Downloader hỗ trợ đến 4K; sửa lỗi sắp xếp cột (OBSERVED, cùng nguồn). Ứng dụng tự kiểm tra cập nhật mỗi lần mở, và mọi cập nhật của "major version 1" đều miễn phí ([tubeatlas.com FAQ](https://tubeatlas.com/)). Khi mở app lần đầu, owner nên xem tab **News and updates** hoặc cửa sổ cập nhật và ghi số phiên bản vào nhật ký quyết định.

## Phần 1: Tube Atlas là máy trích xuất chạy trên máy bạn, không phải bản đồ ngách

### Nó làm được gì và không làm được gì

Nhà sản xuất tự mô tả Tube Atlas là "Powerful YouTube Research Software with 12 Built-in Tools", "not cloud based", chạy trên máy Windows hoặc Mac và lấy dữ liệu "using the power of your computer" ([tubeatlas.com](https://tubeatlas.com/)). Câu đó nói lên điều quan trọng nhất: **Tube Atlas không có cơ sở dữ liệu riêng**. Mỗi con số là ảnh chụp tại lúc bạn bấm trích xuất, và bạn chỉ thấy những gì bạn tìm hoặc lướt qua. Từ đó suy ra ba hệ quả thực tế (INFERRED). Thứ nhất, nó **không tự phát hiện được** "kênh mới đang bùng nổ trên toàn YouTube"; việc đó cần một kho đã cào sẵn như TubeLab (quảng cáo "500K+ channels", lọc RPM, "faceless") ([tubelab.net](https://tubelab.net/)) hoặc TubeMind (preset "Breakouts… at least one video at 5× their median") ([TubeMind](https://tubemind.io/discover)). Thứ hai, để theo dõi trung vị ngách theo thời gian, studio phải tự chạy lại và tự lưu file. Thứ ba, dữ liệu tốt hay xấu phụ thuộc vào việc YouTube có vừa đổi giao diện hay không.

Những thứ **không tồn tại** trong Tube Atlas trả phí, dù nhiều người tưởng là có: điểm outlier, tỉ lệ view/sub, bộ lọc RPM theo ngách, cờ faceless, lọc trạng thái kiếm tiền theo kênh, tốc độ tăng trưởng, cảnh báo/theo dõi tự động, tiện ích Chrome, API công khai, chia sẻ nhóm trên cloud, AI tạo thumbnail (OBSERVED: không nguồn chính thức nào nhắc tới) ([tubeatlas.com](https://tubeatlas.com/)). SaaSPic xếp nó là công cụ nghiên cứu ngách trên desktop. Theo SaaSPic, ai muốn tối ưu kênh của chính mình nên chọn vidIQ hoặc TubeBuddy, và Tube Atlas "does not claim outlier-video detection" ([SaaSPic](https://saaspic.com/tools/tube-atlas/)).

### Dữ liệu đến từ đâu và tin được đến đâu

Nhà sản xuất nói từ khoá lấy "directly from the Youtube autosuggest engine", còn Trends lấy từ "Youtube search, Google search, Image search, News search, & Google Shopping search" (VENDOR CLAIM) ([tubeatlas.com](https://tubeatlas.com/)). Tài liệu chính thức không hề nhắc tới YouTube Data API hay khoá API. Changelog thì liên tục có các dòng như "fixed… due to changes on youtube", cảnh báo "too many requests", lỗi do màn hình đồng ý GDPR ở châu Âu, và từng có tính năng proxy cho Trends ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)). Ghép lại thì gần như chắc chắn **Tube Atlas cào trang web** (INFERRED). Một review affiliate nói nó dùng "YouTube's API", nhưng điều này mâu thuẫn với tài liệu của chính nhà sản xuất ([revuuit](https://revuuit.blogspot.com/2025/09/tube-atlas-review.html)).

Bảng mức tin cậy dưới đây là cách nên đọc từng loại số (INFERRED, tổng hợp từ ghi chú):

| Loại số | Mức tin | Lý do và cách dùng |
|---|---|---|
| View, like, số bình luận, ngày đăng, tiêu đề, tag, mô tả | Khá, nhưng phải kiểm tra mẫu | Chép từ trang công khai. Changelog có nhiều lần cột "không trích được" sau khi YouTube đổi giao diện: like, subs, ngày tham gia hỏng tháng 1/2024 (v1.0.5.0); tổng view kênh hỏng tháng 8/2024 (v1.0.5.5); mô tả sai lệch (v1.0.5.7) ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)). Mỗi lần xuất, so 5 dòng với youtube.com. |
| Average Views per Day | Khá | Có lẽ là view ÷ tuổi video (INFERRED). Đây là số dẫn xuất xác định, nhưng là trung bình nên che mất đỉnh tăng ban đầu. |
| Subscribers | Gần đúng | YouTube làm tròn số sub công khai, nên tỉ lệ dựa trên sub của kênh nhỏ chỉ là xấp xỉ (INFERRED). |
| Estimated Video Earnings / per Day | **Không tin** | Công thức không công bố. Video hướng dẫn số 27 có thể giải thích nhưng chưa ai chép lại ([help videos](https://appbreed.com/help-videos-tube-atlas)). SaaSPic: "estimates, not real data" ([SaaSPic](https://saaspic.com/tools/tube-atlas/)). Để so sánh: Social Blade dùng view × RPM $0,25–4 và thừa nhận có thể "NO views are monetized" ([Social Blade](https://socialblade.com/help/how-are-estimated-earnings-calculated)). Chỉ dùng để xếp hạng tương đối trong cùng ngách, không bao giờ dùng làm dự báo doanh thu. |
| Search volume, CPC, competition | Ước tính bên thứ ba | Lấy từ "free resources" (file Google Keyword Planner) hoặc tài khoản Keywords Everywhere trả phí ([SaaSPic](https://saaspic.com/tools/tube-atlas/)). |
| Trends (search volume index) | Hạn chế | Changelog v1.0.6.0 (24/1/2025): "still restricted due to Google getting more and more strict" ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)). Rất có thể là chỉ số tương đối 0–100 kiểu Google Trends (INFERRED). |

Chưa có ai công bố phép đo độ chính xác của Tube Atlas so với số thật của YouTube. **Sai số thực tế: chưa đo.**

### Mua, cài, giấy phép, chi phí ẩn

Chỉ có **một gói duy nhất**: $67 niêm yết, **$47 với coupon TUBE20**, trả một lần, gồm mọi công cụ, "Commercial License", "Outsource License", **10 máy cài** (bình thường là 1 máy, 10 máy là quyền lợi "trong đợt khuyến mãi") và cập nhật miễn phí trọn đời **cho major version 1** (OBSERVED) ([tubeatlas.com](https://tubeatlas.com/)). Không có bản miễn phí, không có dùng thử, nhưng có **hoàn tiền 30 ngày** qua helpdesk Freshdesk ([tubeatlas.com FAQ](https://tubeatlas.com/)). Sau khi thanh toán sẽ có hai lời mời mua thêm. Upsell 1 là Tube Video Translator + Tube Video Tracker, ban đầu $47, sau bộ đếm giờ hiện "$134 ($67 Each)" ([tube-video-bundle](https://tubeatlas.com/tube-video-bundle/)). Upsell 2 là gói 4 app giá $97. Trang bundle của AppBreed bán Tube Atlas + Translator + Tracker giá $77, nhưng ghi rõ **"There are no refunds on bundle deals"** ([appbreed.com/bundlesale](https://appbreed.com/bundlesale)). Chi phí ẩn chỉ phát sinh nếu bạn tự bật: tài khoản Keywords Everywhere trả phí, khoá Gladia/Deepgram cho File-to-Text, và tuỳ chọn prompt ChatGPT cho chấm câu ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)). Theo luật studio, cả ba đều là API tính tiền và **cần owner duyệt trước**.

Quy trình cài: đặt hàng qua PayKickstart, vào trang tải, nhập **đúng email đã mua** để lấy link, xem video cài cho PC hoặc Mac ("Mac users must allow the software to be installed"), rồi kích hoạt ([download-tube-atlas](https://tubeatlas.com/download-tube-atlas)). Video hướng dẫn số 25 nói cách quản lý số máy đã cài ([help videos](https://appbreed.com/help-videos-tube-atlas)). Bản crack "Tube Atlas v1.0.6.6" đang được đăng trên các diễn đàn warez (OBSERVED trong kết quả tìm kiếm tháng 1–4/2026; cố ý không dẫn link). **Không bao giờ cài bản crack lên máy CINE**: ngoài chuyện bản quyền, đây là đường lây mã độc phổ biến (INFERRED).

Về giấy tờ, "commercial license" chỉ là lời hứa trên trang bán. Văn bản pháp lý duy nhất công khai là Terms chung của AppBreed (cập nhật 24/5/2018), trong đó lại ghi "non-transferable… revocable license… from one device" và "personal and non-commercial use" ([AppBreed Terms](https://appbreed.com/terms-and-conditions/)). Nếu mua, hãy **giữ biên lai và ảnh chụp trang bán** (INFERRED).

### Tube Atlas va chạm luật studio ở đâu

Điều khoản YouTube cấm "access the Service using any automated means (such as robots, botnets or scrapers)", trừ công cụ tìm kiếm công khai hoặc khi có văn bản cho phép ([YouTube Terms](https://www.youtube.com/static?template=terms)). Chính sách YouTube API cũng cấm ứng dụng dùng API thu thập dữ liệu đã cào ([YouTube API Developer Policies](https://developers.google.com/youtube/terms/developer-policies)). CLAUDE.md của studio có luật cứng "Don't automate third-party apps against their terms". Đọc nghiêm thì **các chức năng trích xuất hàng loạt của Tube Atlas nằm ở vùng xám đến đỏ** (INFERRED). Đây là lý do giáo trình không thể tự quyết thay owner. Bảng dưới phân loại từng chức năng theo luật studio:

| Nhóm | Chức năng | Trạng thái CINE | Luật liên quan |
|---|---|---|---|
| Đọc metadata | Keywords, Trends, Videos, Browse & Extract, Channels, Tag/Title Analyzer, Comments (đọc chủ đề), Title Generator (gợi ý), hashtag | **Dùng được, chỉ đọc, khối lượng vừa phải**, sau khi owner chấp nhận rủi ro ToS | Research policy; benchmark là trung vị |
| Có điều kiện | Video-to-Text (đọc cấu trúc 1–2 video, không sao chép) | Chỉ để hiểu nhịp mở đầu; không thay được cổng `competitor-complete-study` | Original IP; maker ≠ checker |
| Có điều kiện | Keywords Everywhere, File-to-Text (Gladia/Deepgram), prompt ChatGPT | Chỉ khi owner duyệt chi phí | Không gọi API tính tiền khi chưa có owner |
| **Không dùng cho CINE** | Video Downloader | Cấm | "no downloading third-party videos" |
| **Không dùng cho CINE** | Content Spinner; "Convert Video to Text & Spin… make it unique"; "generate unlimited legal content" từ video Creative Commons | Cấm | Original IP only; không quay vòng/viết lại kịch bản đối thủ |
| **Không dùng cho CINE** | Emails/Phone Numbers in Description, "Save emails to CSV or TXT" | Cấm | Quyền riêng tư; studio không làm outreach |
| **Tránh** | Extract Unlisted Videos | Không cần, tránh | Video unlisted là video người ta không muốn công khai (INFERRED) |
| **Tránh** | Đăng nhập kênh của owner vào trình duyệt tích hợp | Không làm | Giảm rủi ro tài khoản (INFERRED) |

Ngay trên trang bán, nhà sản xuất còn quảng cáo các bonus như "Copy & Paste Videos And Earn $217 Per Day" ([tubeatlas.com](https://tubeatlas.com/)). Một review affiliate kể đã lấy "an entire competitor's video script… spun it" ([differ.blog](https://differ.blog/p/honest-tube-atlas-review-12-tools-that-changed-everything-8ed24c)). Đây chính là cách dùng mà studio **không** được làm.

## Phần 2: Học từng module, từ lưới dữ liệu chung đến từng nút

Cả 12 công cụ có chung một thiết kế: tìm hoặc lướt, đổ dữ liệu vào **lưới (grid)**, lọc và phân tích, rồi chuyển sang công cụ kế tiếp hoặc xuất ra ([SaaSPic](https://saaspic.com/tools/tube-atlas/)). LearnWire mô tả nó "very like excel or database driven", nhiều số trên một trang hơn vidIQ/TubeBuddy ([LearnWire tutorial](https://www.youtube.com/watch?v=bQDZ2T7jphg)). Vì vậy bài đầu tiên phải là lưới dữ liệu.

### 2.0 Lưới dữ liệu: bộ lọc nhanh, bộ lọc tuỳ biến, file bộ lọc, cột, lưu và xuất

| Tính năng | Làm gì | Cách dùng | Nguồn |
|---|---|---|---|
| **Quick filter** trên đầu cột | Lọc một cú bấm | Bấm ô lọc trên đầu cột, chọn hoặc gõ điều kiện, bấm **apply**. Từ v1.0.1.9 nhận cả số có dấu "+" | [tubeatlas.com](https://tubeatlas.com/); [version history](https://appbreed.com/apps/api/app-download.php?aid=26) |
| **Custom filter** | Điều kiện tuỳ ý trên bất kỳ cột nào | Mở cửa sổ custom filter, thêm điều kiện cho nhiều cột | Như trên; video hướng dẫn 24 |
| **Lưu/nạp file bộ lọc** | Dùng lại một bộ điều kiện | "save your favorite filter combination to a file, and load your saved filters" | [tubeatlas.com](https://tubeatlas.com/) |
| **Sắp xếp** | Bấm tiêu đề cột | Cột ngày đăng sắp được trong Videos và Channels; lỗi sắp xếp được vá ở 1.0.2.6, 1.0.3.6, 1.0.6.7 | [version history](https://appbreed.com/apps/api/app-download.php?aid=26) |
| **Column configuration** | Ẩn, hiện, đổi thứ tự cột của Videos và Channels | Có từ v1.0.2.0; lỗi đổi thứ tự vá ở 1.0.5.8; video 39 | Như trên |
| **Thanh trạng thái** | Đếm tổng số dòng | Xem góc dưới (v1.0.1.3) | Như trên |
| **Save / Load data** | Lưu dự án theo định dạng riêng của Tube Atlas | File → Save / Load; video 23; file cũ của Videos vẫn mở được | [help videos](https://appbreed.com/help-videos-tube-atlas) |
| **Preview & save table/feed report** | Báo cáo **HTML tương tác**, 2 định dạng, mở được độc lập | Video 22; cải tiến ở v1.0.3.1 | [affiliate page](https://tubeatlas.com/affiliates/) |
| **CSV** | Xuất bảng tính | **Đã thấy ở Keywords**: File → save to CSV, app nhớ thư mục lưu lần trước (Vidsilo ~10:37). **Chưa xác nhận** cho lưới Videos/Channels. Văn bản chính thức chỉ nói rõ "Save emails to CSV or TXT" | [Vidsilo keyword](https://www.youtube.com/watch?v=TKpGsi4pXfo); [version history](https://appbreed.com/apps/api/app-download.php?aid=26) |
| **Open data folder** | Mở thư mục dữ liệu | Nút File trong Keywords, Video to Text, Comments (v1.0.4.2) | [version history](https://appbreed.com/apps/api/app-download.php?aid=26) |
| **Re-extract rows / ReExtract NOT EXTRACTED / Extract Missing** | Trích lại các dòng lỗi hoặc chưa trích | Chuột phải (1.0.1.2, 1.0.5.4); nút Extract Missing (1.0.6.1) | Như trên |

**Chưa xác nhận:** các bộ lọc kết hợp theo AND hay OR, có nhóm điều kiện được hay không. App chị em Tik Analyzer quảng cáo "AND/OR groups" và "Export to CSV, TXT, or HTML", nhưng đó là sản phẩm khác ([hudareview](https://hudareview.com/tik-analyzer-review)). Video 24 của nhà sản xuất và chương "Filtering and exporting data" (9:40–14:11) của LearnWire là hai nơi cần xem để chốt câu này ([LearnWire](https://www.youtube.com/watch?v=bQDZ2T7jphg)). **Việc owner cần làm ngay ngày đầu:** mở menu File của từng công cụ và ghi lại công cụ nào có "CSV". Câu trả lời này quyết định đường ống ở Phần 4.

### 2.1 Keyword Generator: cây từ khoá từ autosuggest của YouTube

Công cụ này sinh "hundreds of top popular keywords directly from the Youtube autosuggest engine". Nó có thể ghép thêm search volume, CPC và competition từ nguồn miễn phí (VENDOR CLAIM) ([tubeatlas.com](https://tubeatlas.com/)). Các bước theo video Vidsilo và review imnights:

| Bước | Thao tác | Ghi chú |
|---|---|---|
| 1 | Mở tab **Keywords**, gõ seed (ví dụ "minecraft horror"), chọn **country** | Dropdown quốc gia được vá ở v1.0.1.3 ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)); imnights nói có thể "choose your search range" ([imnights](https://imnights.com/tube-atlas-review)) |
| 2 | Bấm **Generate** | Ra hàng trăm cụm từ ([Vidsilo ~0:00–7:00](https://www.youtube.com/watch?v=TKpGsi4pXfo)) |
| 3 | Thêm volume: nhập file volume miễn phí (video 4, định dạng file Google Keyword Planner từ v1.0.2.8), hoặc dùng **Keywords Everywhere tool** (video 5, cần tài khoản trả phí) | Keywords Everywhere: cần owner duyệt chi phí |
| 4 | Chuột phải để bật checkbox chọn dòng (~7:20) | [Vidsilo](https://www.youtube.com/watch?v=TKpGsi4pXfo) |
| 5 | Chuột phải → **copy comma separated keywords**; hoặc **hashtag generator** | v1.0.0.7 và v1.0.0.6 |
| 6 | **Import Keywords** từ nút File hoặc chuột phải (video 40) | Nạp danh sách từ khoá có sẵn |
| 7 | File → Save (định dạng dự án) hoặc **save to CSV** (~10:37) | Đây là CSV duy nhất đã thấy tận mắt trong tutorial |

Các cột đã biết: keyword, search volume, CPC, competition. **Danh sách cột đầy đủ chưa được công bố.** Mẹo từ imnights: đừng bỏ qua từ khoá volume nhỏ, vì chúng có thể mang ý định rõ ràng hơn ([imnights](https://imnights.com/tube-atlas-review)).

### 2.2 Trends: chỉ số tìm kiếm 12 tháng, 258 quốc gia, 5 nguồn

Nhà sản xuất quảng cáo "a full year of search volume data", "258 countries", 5 nguồn tìm kiếm (VENDOR CLAIM) ([tubeatlas.com](https://tubeatlas.com/)). Đầu vào là danh sách từ khoá nhập từ Keyword Generator hoặc từ file bất kỳ. Lưới kết quả có **mini chart** cho từng từ khoá, bấm vào ra biểu đồ đầy đủ theo thời gian ([SaaSPic](https://saaspic.com/tools/tube-atlas/)). Ngoài những gì Google Trends có, công cụ thêm hai số: **"The averages"** và **"The trend slopes"** ([imnights](https://imnights.com/tube-atlas-review)). Từ v1.0.5.2 có thêm khoảng thời gian. Chuột phải có copy comma-separated keywords và hashtag generator. Có thể lưu ảnh biểu đồ ([affiliate page](https://tubeatlas.com/affiliates/)). Proxy từng được hỗ trợ từ v1.0.0.1 rồi bị gỡ ở v1.0.1.0. Trạng thái mới nhất được ghi: "still restricted" ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)).

Cách dùng (INFERRED từ tài liệu): nhập danh sách → chọn nguồn **YouTube search** → chọn quốc gia và khoảng thời gian → sắp theo **slope** để tìm cụm đang lên, theo **average** để tìm cụm lớn và ổn định → bấm mini chart xem mùa vụ → lưu ảnh biểu đồ làm bằng chứng. Nên chạy lô nhỏ (10–20 từ khoá) vì Google giới hạn tốc độ. **Chưa xác nhận:** số từ khoá tối đa mỗi lô, và chỉ số là tương đối 0–100 hay tuyệt đối.

### 2.3 Videos (Video Analyzer): 35 cột cho mỗi video, cộng cột Is Shorts

Đây là trái tim của phần mềm. Có bốn cách đổ dữ liệu vào lưới: (1) gõ seed và bấm nút **Search màu đỏ**, có thể "change any settings" ([imnights](https://imnights.com/tube-atlas-review)); (2) bấm **Trending Videos**, nguồn được đổi ở v1.0.6.3 ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)); (3) nhập từ **Browse & Extract** (video 10); (4) nhập từ "content extraction tool" (video 11) ([help videos](https://appbreed.com/help-videos-tube-atlas)). Ngoài ra còn có tuỳ chọn nguồn "Google option", là nguồn hay gây cảnh báo "too many requests" (v1.0.4.1).

**35 cột chính thức** (OBSERVED trên trang bán, [tubeatlas.com](https://tubeatlas.com/)):

| # | Cột | # | Cột | # | Cột |
|---|---|---|---|---|---|
| 1 | Video Image | 13 | Hashtags in Description | 25 | Estimated Video Earnings |
| 2 | Video ID | 14 | Emails in Description (không dùng) | 26 | Estimated Earnings per Day |
| 3 | Video Link | 15 | Phone Numbers in Description (không dùng) | 27 | Category |
| 4 | Source | 16 | Readability of Description | 28 | Subtitles |
| 5 | Search Phrase | 17 | Grade Level of Description | 29 | Creative Commons License |
| 6 | Title | 18 | Total Video Views | 30 | Ads Found |
| 7 | Characters in Title | 19 | Total Likes | 31 | Channel Name |
| 8 | Description | 20 | Total Comments | 32 | Channel Link |
| 9 | Characters in Description | 21 | Video Length in Seconds | 33 | Total Channel Subscribers |
| 10 | Word Count in Description | 22 | Date Published | 34 | Tag Count |
| 11 | Link Count in Description | 23 | Publish Age in Days | 35 | Tag Keywords |
| 12 | Hashtag Count in Description | 24 | Average Views per Day | + | **Is Shorts** (thêm ở v1.0.4.2) |

Lịch sử cột ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)): "Ads Found" thêm ở 1.0.1.1. "Channel Country" thêm ở 1.0.2.7 rồi **bị gỡ** ở 1.0.3.0 vì làm treo app. Cột "Email" đổi tên thành "Email in Desc". Các cột doanh thu thêm ở 1.0.0.6. Bản quảng cáo năm 2022 ghi "25 columns", nên các tutorial cũ sẽ trông khác.

**Nút và thao tác của lưới Videos:**

| Thao tác | Làm gì | Phiên bản |
|---|---|---|
| **Get Related Videos** | Mở rộng tập video từ các dòng đang chọn | 1.0.1.4; video 31 |
| **Unlisted videos** | Trích video unlisted (tránh dùng) | 1.0.1.4; video 32 |
| **Get Video Ads** | Trích quảng cáo trong các video đã chọn | 1.0.1.6; video 33 |
| **Extract Missing** | Trích các dòng chưa trích | 1.0.6.1 |
| Chuột phải → **re-extract rows** / **ReExtract NOT EXTRACTED rows** | Trích lại dòng lỗi | 1.0.1.2 / 1.0.5.4 |
| Chuột phải → **copy hashtags** | Chép hashtag, cách nhau bằng dấu cách | 1.0.1.3 |
| Chuột phải → **Convert to video embed codes** | Sinh mã nhúng (chứa ID video) | 1.0.2.2 |
| File → **Save emails to CSV or TXT** | Xuất email (không dùng cho CINE) | 1.0.4.1 |
| Bấm ô **Video ID** | Mở trình phát không quảng cáo | 1.0.2.0 |
| Nhấp đúp ô **Video Image** | Mở cửa sổ Video Details | trang bán |

**Đọc cột cho đúng (INFERRED).** Cặp cột quan trọng nhất là **Average Views per Day** và **Publish Age in Days**. Một video mới có view/ngày cao là tín hiệu "đang chạy". Một video 800 ngày tuổi mà vẫn giữ view/ngày khá là "evergreen". Demo của nhà sản xuất đưa ví dụ: video 1 ngày tuổi đạt 228 view/ngày, so với video 800 ngày tuổi vẫn 69 view/ngày ([Vidsilo ~1:54:30](https://www.youtube.com/watch?v=Vt8ktMezDJ4)). Cột **Is Shorts** tách Shorts khỏi video dài, thay cho mốc ≤180 giây mà `cf_research_stats.py` dùng. Cột **Subtitles** và **Category** giúp đoán định dạng. Cột **Creative Commons License** chỉ nên dùng để biết; studio không lấy nội dung CC về dùng.

**"Outlier" bằng tay.** Không có cột tỉ lệ. Gần đúng nhất là custom filter kết hợp Publish Age in Days (nhỏ), Total Channel Subscribers (nhỏ), rồi sắp theo Average Views per Day giảm dần. Lưu thành file bộ lọc (INFERRED từ [tubeatlas.com](https://tubeatlas.com/)). Trang bán chỉ có đúng một công thức lọc, và nó dành cho đặt quảng cáo chứ không phải tìm ngách: "see the videos that allow monetization, then filter your results by the most daily RECENT views" ([tubeatlas.com](https://tubeatlas.com/)). **Không nguồn nào đưa ra ngưỡng số khuyến nghị.** Mọi ngưỡng như "≤25K sub, ≤180 ngày" đều mượn từ preset của công cụ khác như TubeMind ([TubeMind](https://tubemind.io/discover)) và phải thành **quyết định OWNER**.

### 2.4 Cửa sổ Video Details: xem sâu một video

Nhấp đúp ảnh ở cột Image sẽ mở cửa sổ có: copy tiêu đề, tag, mô tả bằng một cú bấm; tải video và thumbnail; "spin" mô tả bằng một cú bấm; đếm từ, ký tự, link, hashtag; điểm đọc và cấp lớp ([tubeatlas.com](https://tubeatlas.com/)). Các bản sau thêm word replace (1.0.0.7), readability/grade (1.0.1.2), nút **watch**, bấm thumbnail để mở trình phát tích hợp (1.0.2.0), cải thiện lưu file (1.0.4.6) và trình xem HTML (1.0.5.5) ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)). Với CINE: được **copy tag và tiêu đề để phân tích**. **Không** dùng nút tải video và nút spin mô tả. Muốn xem video đối thủ thì nên xem trên youtube.com thay vì trình phát "ad-free". Lý do: creator vẫn nhận tiền quảng cáo, và việc xem đầy đủ phục vụ cổng `competitor-complete-study` (INFERRED).

### 2.5 Browse & Extract: vượt giới hạn một trang kết quả

Đây là tính năng mà các review gọi là đáng tiền nhất. Nó là một trình duyệt tích hợp có bookmark (trang chủ YouTube là bookmark mặc định từ 1.0.0.8), nút **extract links / extract video or channel links**, nút **auto scroll** (1.0.0.2, 1.0.3.7, 1.0.4.0), và hiển thị số kênh tìm thấy (1.0.2.9) ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)). Bạn dùng chính bộ lọc của YouTube trong trình duyệt này (Upload date, Type, Duration…). Công cụ chạy trên "any page on the internet that contains Youtube video links" ([affiliate page](https://tubeatlas.com/affiliates/)). Nó cũng chạy cho Shorts: "simply browse the YouTube Shorts section within the built-in web browser and click analyze" ([tubeatlas.com](https://tubeatlas.com/)). Một beta tester (lời chứng do nhà sản xuất chọn) kể đã "extracting data for over 1000 videos in just minutes" (VENDOR CLAIM).

| Bước | Thao tác (INFERRED từ tài liệu; video 10 và 13 là nguồn chuẩn) |
|---|---|
| 1 | Mở tab Browse & Extract, vào YouTube, tìm "minecraft horror" |
| 2 | Dùng bộ lọc của YouTube: Upload date = This month, Type = Video, Duration = Over 20 minutes |
| 3 | Bật **auto scroll** để trang tải thêm kết quả |
| 4 | Bấm **extract video links** (hoặc channel links) |
| 5 | Chuyển kết quả sang tab Videos (hoặc Channels) để trích đủ 35 cột |
| 6 | Nếu dòng nào trống thì bấm **Extract Missing** |

Đây cũng chính là thao tác studio đã làm tay trong nghiên cứu Shorts ngày 13/11. Lần đó studio tìm trên trình duyệt với bộ lọc Shorts, thu 782 Shorts của 639 kênh, rồi lấy số chính xác qua `videos.list`/`channels.list` với 119 unit (OBSERVED, `docs/niches/minecraft_long_short_choice_2026-11-13.md`). Browse & Extract tự động hoá bước "thu link" đó (INFERRED). Bù lại, nó đưa studio vào vùng cào dữ liệu tự động, đúng điểm mà ToS YouTube cấm. **Chưa xác nhận:** cột "Source" và "Search Phrase" được điền thế nào khi nhập từ Browse & Extract; auto scroll đi được bao xa trước khi bị chặn.

### 2.6 Channels (Channel Analyzer): kênh nào thắng lặp lại

Nhà sản xuất quảng cáo "27+ data points for every Youtube channel". Trang affiliate cũ ghi "17+" (VENDOR CLAIM, hai con số mâu thuẫn) ([tubeatlas.com](https://tubeatlas.com/); [affiliate page](https://tubeatlas.com/affiliates/)). Có ba cách đổ dữ liệu: tìm bằng từ khoá, nhập từ Browse & Extract (video 13), nhập từ content extraction (video 14). Tính năng then chốt là **"analyze all videos in a given Youtube channel"** (video 15) ([help videos](https://appbreed.com/help-videos-tube-atlas)). Các cột đã xác nhận qua changelog: total channel views, total channel videos, total subscribers, title, **date joined**, Channel Tags, Email in Desc, Tags Count, estimated revenue, cùng 10 cột thống kê mô tả ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)). Video Marketing Island còn thấy "estimated total earnings" và "average earnings per video" ([Marketing Island ~5:10](https://www.youtube.com/watch?v=aFs7HlShjJg)). Khung chi tiết kênh hiện date joined, country, channel keywords và external links ([IM Toolkit ~1:57:34](https://www.youtube.com/watch?v=sAiYwVGZ6JI)). Link kiểu @handle được hỗ trợ từ 1.0.2.7.

Cách dùng: mở một kênh, trích toàn bộ video, rồi sắp theo "most views per day" để thấy video nào là outlier **trong chính kênh đó** ([IM Toolkit ~2:13:10](https://www.youtube.com/watch?v=sAiYwVGZ6JI)). Đây là phương pháp gần nhất với định nghĩa outlier của studio (≥3× trung vị kênh). Lưu ý "date joined" từng bị hỏng vào tháng 1/2024. Với kênh quan trọng cho quyết định, hãy đối chiếu trên trang About. **Chưa xác nhận:** danh sách đủ 27 cột.

### 2.7 Comments (Comment Analyzer): khai thác câu hỏi của người xem

Công cụ sắp bình luận theo like và reply, tách bình luận có **câu hỏi** hoặc **chửi thề**, tìm **cụm từ lặp nhiều nhất**, và lọc bình luận chứa một cụm đã chọn ([tubeatlas.com](https://tubeatlas.com/)). Các trường có: tên người bình luận, like, reply, cờ câu hỏi, cột profanity. Điều khiển gồm autoscroll, nút **extract comments**, phân tích cụm từ, hiện bình luận theo cụm (1.0.0.2), nhấp đúp để xem nguyên văn (1.0.0.7) ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)). Nhà sản xuất định vị công cụ này để "uncover hidden niche ideas and identify user issues" ([imnights](https://imnights.com/tube-atlas-review)). Một reviewer affiliate tự báo đã trích 2.847 bình luận trong 3 phút (chưa kiểm chứng) ([Medium](https://medium.com/@earnmoneyonlinefast/youtube-success-isnt-about-luck-it-s-about-intelligence-92188ecfc2de)). Với CINE, đây là đầu vào trực tiếp cho kỹ năng `r03-comment-insight`, tức tiếng nói, lời phàn nàn và mong muốn của người xem. Chỉ đọc chủ đề. **Không lưu tên người bình luận** vào báo cáo của studio (INFERRED, quyền riêng tư).

### 2.8 Tag Analyzer, Title Analyzer và hashtag

**Tag Analyzer** cho mỗi tag số lần xuất hiện, phần trăm, view trung bình và like trung bình ([SaaSPic](https://saaspic.com/tools/tube-atlas/)). Demo của nhà sản xuất còn gán "giá trị" cho tag ("this particular tag is worth 32 000") ([Vidsilo ~1:03:00](https://www.youtube.com/watch?v=Vt8ktMezDJ4)). Con số đó là sản phẩm của công thức doanh thu không công bố, nên bỏ qua. **Title Analyzer** đếm "top word combinations across unlimited number of Youtube video titles" trong danh sách hiện tại ([tubeatlas.com](https://tubeatlas.com/)). Đây là n-gram tiêu đề, và hữu ích nhất khi chạy trên **danh sách đã lọc chỉ còn outlier** (INFERRED). **Hashtag generator** nằm trong Keywords, Trends, Tag Analyzer và Title Analyzer (1.0.0.6). Trang affiliate nói "4 ways", trang bán hiện nay nói "6 ways". Danh sách 6 cách **chưa được ghi thành chữ**. Nút **Tools** có link đến trình tạo mô tả online ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)).

### 2.9 Video Title Generator: 1.200 khuôn tiêu đề

Gõ một cụm chủ đề, nhận "over 1,200 powerful headlines". Nhà sản xuất nói các khuôn được "compiled… based on views, comments, and likes" (VENDOR CLAIM) ([tubeatlas.com](https://tubeatlas.com/)). Với CINE, đây chỉ là nguồn khuôn để brainstorm. Mọi tiêu đề cuối vẫn phải đi qua `packaging-seo` và `policy-check`: hứa đúng điều video có, không dùng tên nhân vật của người khác.

### 2.10 Video-to-Text, File-to-Text và các công cụ văn bản AI

Đầu vào là link YouTube, kể cả link rút gọn (1.0.1.1) và Shorts (1.0.3.8). Công cụ xử lý phụ đề không phải tiếng Anh (1.0.1.4) và tự nhận ngôn ngữ khi video có nhiều phụ đề (1.0.1.7). **File to Text** chuyển file âm thanh/video cục bộ sang chữ, "99 different languages". Tính năng này cần khoá **Gladia hoặc Deepgram** nhập ở Settings → "Speech to Text APIs" (1.0.4.3, 1.0.4.5; video 44). Nút **Auto punctuate** có dropdown: punctuator online miễn phí, "free online AI API", prompt ChatGPT (1.0.5.9). **Từ 1.0.6.7 nút này chạy offline cho tiếng Anh**, giữ dấu câu sẵn có và chỉ tách đoạn ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)). Các nút khác: Find & Replace, spinner, **HTML editor** và **Save to HTML**, **Keyword detection**, **Important sentences**, **Image search / Suggested images**, **Text summarization**, **Text-to-Headline** (AI), readability/grade, **Make Paragraphs**, "copy content as unpunctuated", **Watch** (video 34–43) ([help videos](https://appbreed.com/help-videos-tube-atlas)). Video 30 "Generate legal content from creative common videos" dạy lấy nội dung từ video có cột Creative Commons License. Với CINE, **quy trình này không dùng**.

Dùng thế nào cho CINE (INFERRED). Được phép đọc transcript của 1–2 video thắng để ghi lại **cấu trúc**: mở đầu sau bao nhiêu giây thì có đe doạ, mỗi bao lâu có một mốc. Không chép câu chữ, không đưa qua Spinner. Transcript không thay được việc xem trọn video có hình và tiếng mà cổng `competitor-complete-study` yêu cầu. File-to-Text cho file của chính studio thì đã có giải pháp chạy cục bộ là skill `local-whisper`, nên không cần trả tiền Gladia/Deepgram.

### 2.11 Content Spinner: biết để tránh

Công cụ này viết lại văn bản bằng cách dịch qua Google Translate: "through 2 different languages and back to English", 109 ngôn ngữ, "No Google Translate API costs". Có word replace và auto-punctuation ([tubeatlas.com](https://tubeatlas.com/); [version history](https://appbreed.com/apps/api/app-download.php?aid=26)). SaaSPic cảnh báo nó "invite[s] reusing other creators' content, which can breach copyright and YouTube's rules" ([SaaSPic](https://saaspic.com/tools/tube-atlas/)). **Không dùng cho CINE.** Viết lại kịch bản của đối thủ vẫn là sao chép, chỉ khó nhận ra hơn. Nó còn đi ngược thẳng luật "Original IP only".

### 2.12 Video Downloader: biết để tránh

Từ 1.0.6.7, công cụ tải được video ở mọi độ phân giải có sẵn đến 4K, chỉ âm thanh (m4a/mp3), chỉ hình, kèm thumbnail. Nó có nút dừng, các thành phần tải tự cập nhật, và hiển thị thumbnail, tiêu đề, thời lượng (video 20) ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)). **Không dùng cho CINE.** Luật cứng là "no downloading third-party videos".

### 2.13 Thiết lập và phím tắt ẩn

**Settings** có: nhiều đăng nhập YouTube (1.0.0.6; video 29); tab "Speech to Text APIs"; quản lý máy cài (video 25); tab Welcome; tab **News and updates** (1.0.6.2); cửa sổ tin nhắn trong app có chỉnh âm lượng (1.0.3.9); menu **Tools** ([version history](https://appbreed.com/apps/api/app-download.php?aid=26)). Có các bản vá cho người dùng châu Âu vướng GDPR (1.0.2.9, 1.0.5.1). Từ Việt Nam thì **chưa ai thử**. Không có phím tắt bàn phím, tham số dòng lệnh, tham số URL hay API nào được ghi trong tài liệu. "Sức mạnh ẩn" nằm ở thao tác chuột:

| Thao tác ẩn | Ở đâu | Kết quả |
|---|---|---|
| Nhấp đúp ô Image | Videos | Mở Video Details |
| Bấm ô Video ID / thumbnail trong Details | Videos | Trình phát tích hợp |
| Nhấp đúp ô bình luận | Comments | Xem nguyên văn |
| Chuột phải | Videos | re-extract, ReExtract NOT EXTRACTED, copy hashtags, embed codes |
| Chuột phải | Keywords, Trends | copy comma separated, hashtag generator, Import Keywords |
| Chuột phải | Spinner | word replace |
| Lưu/nạp file bộ lọc | Mọi lưới | Bộ lọc "outlier tay" dùng lại được |
| Auto scroll + extract | Browse & Extract | Hàng trăm đến hàng nghìn link |

Quy tắc an toàn (INFERRED): **không đăng nhập Google của kênh owner** vào trình duyệt tích hợp. Không chạy trích xuất nặng cùng lúc owner đang upload từ cùng máy và cùng IP. Hệ quả thực tế dễ gặp nhất là IP bị chặn tạm hoặc phải giải CAPTCHA, chứ không phải gậy cho kênh. Hiện chưa có báo cáo công khai nào về tài khoản bị xử lý vì Tube Atlas.

### 2.14 Bonus và upsell: có gì trong hộp

Hộp mua gồm Description Generator, 19 Description Templates, Online Hashtag Generator, đào tạo YouTube Shorts (hướng dẫn 83 trang và 15 video), 10 content reports, 8 PDF reports, video đào tạo ([tubeatlas.com](https://tubeatlas.com/); [affiliate page](https://tubeatlas.com/affiliates/)). Thư viện hướng dẫn có **44 video đánh số** cộng các video cập nhật; FAQ nói 48 ([help videos](https://appbreed.com/help-videos-tube-atlas)). Thư viện **không có video riêng về Shorts**. **Tube Video Tracker** (upsell) là công cụ duy nhất kiểm tra thứ hạng từ khoá của video theo thời gian, xuất CSV/TXT, biểu đồ SVG/PNG và HTML. **Tube Video Translator** dịch tiêu đề, mô tả, phụ đề sang hơn 100 ngôn ngữ và tạo file .SBV ([tube-video-bundle](https://tubeatlas.com/tube-video-bundle/)). Cả hai đều không cần cho giai đoạn hiện tại của studio (INFERRED).

## Phần 3: tube-atlas-oss, bản mã nguồn mở có outlier thật nhưng nhiều bẫy

Repo bắt đầu ngày 25/4/2026 như một bản dựng lại 10 công cụ của Tube Atlas trả phí, rồi trong 5 ngày chuyển thành pipeline 5 trang "nghiên cứu → kịch bản → video". Trang GitHub ngày 13/11/2026 hiện 0 sao, 0 fork, 12 PR mở, 13 commit trên master, không có release ([repo](https://github.com/quyenmanhnguyen/tube-atlas-oss)). Giấy phép MIT; riêng `core/pixelle/` là Apache-2.0 lấy từ Pixelle-Video ([NOTICE](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/NOTICE)). README đã lỗi thời: vẫn liệt kê `01_Niche_Finder.py`/`02_Keyword_Finder.py` và không nhắc Producer ([README](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/README.md)). Toàn bộ mô tả dưới đây đến từ việc **đọc mã ở commit `f0b2a0d`, không chạy** (OBSERVED về mã; hành vi thực tế chưa đo).

### Trang chủ và 01 Research: hai tab trong một nút Run

Trang chủ `app.py` có 5 thẻ dẫn tới 5 trang, chỉ báo "active/missing" cho `YOUTUBE_API_KEY` và `DEEPSEEK_API_KEY`, và chọn ngôn ngữ EN/KO/JA/VI ([app.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/app.py)). Trang **01 Research** có ba đầu vào chung: seed, vùng `gl` (US, KR, JP, VN, GB, ID, CN; mặc định US) và ngôn ngữ autocomplete `hl` ([01_Research.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/01_Research.py)).

**Tab A "Long-tail keywords"** có: (a) gợi ý autocomplete của YouTube, **không cần khoá**; (b) nếu có khoá thì thêm ba đồng hồ 0–100 (Keyword Score, Volume, Competition) và biểu đồ VPH của top 10; (c) công tắc **KGR** chấm dễ/trung bình/khó cho tối đa 25 gợi ý; (d) thẻ cho 15 gợi ý đầu, mỗi thẻ có nút "Send to Studio"; (e) bảng đầy đủ tải được **CSV** (keyword, length, words, competition, score, grade); (f) **Question buckets**, tức autocomplete cho từ hỏi + seed. Tiếng Việt dùng "làm sao, tại sao, khi nào, ở đâu, có nên, có thể", tiếng Anh dùng "how, what, why…". Chính giao diện ghi rằng điểm là "Proxy score… not VidIQ" ([keywords.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/keywords.py)).

**Tab B "Niche analysis"** có: Google Trends qua pytrends (`gprop='youtube'`, khung 7 ngày / 1 / 3 / 12 tháng), Avg/Peak, bảng "Top related" và "Rising"; **Trend Pulse 7d** (HOT/cooling/stable); **Opportunity score** 0–100; **Breakout videos** (tối đa 8, cột "× median"); **Top channels** (10 kênh); **Audience pulse**, tức cào 150 bình luận của video số 1 rồi chấm cảm xúc VADER; và **AI verdict** của DeepSeek (hot/warm/cold, điểm, cơ hội, rủi ro, khoảng trống nội dung) ([trends.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/trends.py); [comments.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/comments.py)). Vì Streamlit chạy cả hai tab trong mỗi lần bấm, một lần **Run** sẽ chạy luôn tab B, kể cả DeepSeek và việc cào bình luận (INFERRED từ cấu trúc mã).

### 02 Video Cloner, 03 Outlier Finder, 04 Studio, 05 Producer

**02 Video Cloner** nhận URL (watch, youtu.be, shorts, embed, ID), một "chủ đề mới cho bản clone", số tiêu đề clone (5–20) và ngôn ngữ đầu ra. Đầu ra gồm: *fingerprint* (thumbnail, view, like, bình luận, engagement % = (like+bình luận)/view×100, tag gốc); transcript (youtube-transcript-api, dự phòng yt-dlp, cắt ở 8.000 ký tự); và "clone kit" của DeepSeek gồm phân tích hook 0–15 giây, N tiêu đề clone, **kịch bản 600–900 từ Hook·Body·CTA tải về .md**, 5 dòng chữ thumbnail và 12 tag ([02_Video_Cloner.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/02_Video_Cloner.py)). **Không dùng cho CINE** phần tiêu đề clone và kịch bản clone. Phần fingerprint chỉ là metadata và có thể đọc tham khảo, nhưng phân tích hook do DeepSeek làm là API tính tiền và chỉ dựa trên transcript.

**03 Outlier Finder** có đầu vào: seed, vùng (VN mặc định, US, JP, KR, GB, ID), cửa sổ 7/14/30 ngày, **Max subs** 1.000–5.000.000 (mặc định 100.000), **Min outlier ratio** 0,5–10 (mặc định 1,5). Đầu ra: số outlier, VPH lớn nhất và trung bình, điểm trung bình; mỗi dòng có thumbnail, kênh, sub, số ngày, view, VPH và điểm tô màu (≥5× xanh, ≥2× vàng); nút "Clone" và "Use topic"; **CSV** (title, channel_title, subs, views, vph, outlier_score, hours_since, url); cache 15 phút ([03_Outlier_Finder.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/03_Outlier_Finder.py)).

**04 Studio** là wizard 5 bước của DeepSeek: 20 ý tưởng → 10 tiêu đề (top 3 theo "predicted CTR") → dàn ý 8 phần → kịch bản dài (mặc định 18.000 ký tự, viết trong 2 lần gọi) → "humanize rewrite". Chú thích trong mã nói prompt mô phỏng quy trình 'H2Dev "PROMPT NGÁCH NHỎ PHẬT PHÁP"' ([llm.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/llm.py)). **Không dùng cho CINE**: nó tạo ra một xưởng kịch bản song song, điều CLAUDE.md cấm, vì studio đã có `cine-script-factory`.

**05 Producer** có hai chế độ ([05_Producer.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/05_Producer.py)). Chế độ `short` dùng Edge-TTS và phụ đề theo từ, ghép mp4 9:16 bằng moviepy, nền gradient Ken Burns hoặc ảnh từ ComfyUI cục bộ, RunningHub cloud, hay Grok. Chế độ `long_form` chia kịch bản thành cảnh theo 150 từ/phút; mỗi cảnh có lời đọc, prompt ảnh, prompt video cho Veo 3/Sora/Wan/Kling; xuất .md/.json và prompt thumbnail. **Grok provider** đăng nhập `accounts.x.ai` bằng email và mật khẩu qua Playwright, bắt cookie và header, gọi các endpoint không chính thức của grok.com. Docstring ghi "There is no public xAI API behind this", và phần tải ảnh còn "race-download… keep the largest one" để lấy bản chưa bị làm mờ do kiểm duyệt ([grok_web_client.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/grok_web_client.py)). **Grok Producer: không dùng cho CINE.** Nó tự động hoá ứng dụng bên thứ ba trái điều khoản và lách kiểm duyệt. Phần còn lại của Producer cũng thua xa vòng render/edit/QC của studio.

### Công thức chấm điểm và chi phí quota của bản OSS

| Chỉ số | Công thức (OBSERVED trong mã) | Điểm yếu (INFERRED) |
|---|---|---|
| Outlier score | view ÷ max(sub, 1.000) trên 50 kết quả `search.list` sắp theo viewCount ([outliers.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/outliers.py)) | So với **sub**, không so với trung vị của chính kênh; không chuẩn hoá theo tuổi video; kênh ẩn sub bị coi là 1.000 |
| VPH | view ÷ số giờ từ lúc đăng (tối thiểu 1) | Ổn |
| Breakouts | view > 2,5 × trung vị của ≤25 kết quả top | Trung vị của tập kết quả tìm kiếm, trộn kênh mọi cỡ |
| Opportunity | activity(0–40) + reach(0–40) + (20 − saturation); mốc cứng 50 upload/14 ngày, 5M view, 5M kết quả ([youtube.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/youtube.py)) | Mốc tuỳ tiện; dựa trên `totalResults` vốn chỉ xấp xỉ |
| Keyword Score | 0,7·Volume + 0,3·(100 − Competition) | Chỉ là điểm đại diện |
| KGR | competition ÷ breadth, chia bậc 500 / 5.000 / 50.000 | breadth giống nhau cho mọi dòng nên thực tế chỉ phụ thuộc competition |
| Trend Pulse | (7 ngày gần − 7 ngày trước)/7 ngày trước; hot nếu ≥30% và ≥5 | `totalResults` nhiễu |

Quota tính theo mã và bảng đơn vị trong README (ESTIMATED, chưa chạy): **một lần Research ≈ 503 unit**, bật KGR thì ≈ 3.003. Như vậy 10.000 unit/ngày chỉ đủ khoảng 19 lần, hoặc 3 lần nếu có KGR. **Một lần Outlier Finder ≈ 102 unit**, khoảng 98 lần/ngày. Video Cloner ≈ 1 unit. Trang Research **không có cache**. Thêm một lỗi trải nghiệm suy ra từ mã: đổi công tắc KGR hoặc khung thời gian Trends làm trang dừng và mất kết quả, phải bấm Run lại và tốn thêm ~500 unit (INFERRED, chưa chạy). Lưu ý: tài liệu Google tháng 10/2026 được ghi chú là tách `search.list` thành nhóm riêng 100 lần gọi/ngày, 1 unit mỗi lần ([YouTube quota](https://developers.google.com/youtube/v3/determine_quota_cost)), trong khi README và script `cf_mc_api_dataset.py` của studio tính 100 unit/lần. Cách tính nào cũng cho **trần thực tế khoảng 100 lần tìm kiếm mỗi ngày**.

### Cài trên Windows và giữ khoá an toàn

README hướng dẫn: `git clone` → `pip install -r requirements.txt` → `cp .env.example .env` → điền `YOUTUBE_API_KEY`, `DEEPSEEK_API_KEY` → `streamlit run app.py`. Có Dockerfile (python:3.12-slim, cổng 8501) ([README](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/README.md); [Dockerfile](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/Dockerfile)). Trên Windows, chuỗi lệnh tương đương (INFERRED, chưa chạy) là `py -3.12 -m venv .venv`, `.venv\Scripts\activate`, `pip install -r requirements.txt`, `copy .env.example .env`, `notepad .env`, `streamlit run app.py`. **Đặt ở thư mục riêng ngoài repo CineFactory**, vì CLAUDE.md cấm tạo repo CineFactory khác. Quy tắc về khoá: chỉ để trong `.env`, không commit, không gửi cho ai, không dán vào chat. **Không deploy lên Streamlit Community Cloud** như README gợi ý: trang không có đăng nhập, ai có URL cũng tiêu được quota và tín dụng DeepSeek của bạn (INFERRED). Không tìm thấy telemetry nào; `gatherUsageStats = false` ([config.toml](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/.streamlit/config.toml)). Trang Producer có ô ghi `DEEPSEEK_API_KEY` dạng chữ thường vào `.env` ở gốc repo ([05_Producer.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/05_Producer.py)). DeepSeek là API tính tiền, nên **cần owner duyệt** trước khi điền khoá.

Nhìn thẳng thì Outlier Finder của bản OSS **kém hơn** công cụ studio đang có. Studio đã có `tools/cf_mc_api_dataset.py`, script chỉ đọc dùng thư viện chuẩn: chạy `search.list` → `videos.list` → `channels.list` → lấy danh sách upload của các kênh dẫn đầu, có trần cứng 9.300 unit, khoá đọc từ `.env` và không bao giờ in ra. Kết quả đi vào `cf_research_stats.py`, nơi outlier được tính so với **trung vị của chính kênh** (OBSERVED, mã nguồn). Phần OSS đáng học hỏi chỉ có **tab A** (autocomplete và question buckets miễn phí) và ý tưởng **Trend Pulse** (INFERRED).

## Phần 4: Ghép Tube Atlas với API miễn phí và cf_research_stats.py

### Chia việc: ai làm gì

Ghi chú so sánh ước tính khoảng 70% đầu ra nghiên cứu của Tube Atlas có thể làm lại miễn phí bằng YouTube Data API v3 và các nguồn mở (INFERRED, chưa đo). Bảng chia việc dưới đây giữ nguyên nguyên tắc "benchmark là TRUNG VỊ ngách":

| Câu hỏi | Công cụ nên dùng | Vì sao |
|---|---|---|
| View, like, bình luận, ngày đăng của danh sách video | **API `videos.list`** (1 unit/50 ID), qua script của studio | Chính xác và đúng điều khoản ([quota](https://developers.google.com/youtube/v3/determine_quota_cost)) |
| Outlier (≥3× trung vị kênh), view/ngày, trung vị ngách, dài vs ngắn | **`tools/cf_research_stats.py`** | Công thức minh bạch; Tube Atlas không có |
| Tuổi kênh, số sub | API `channels.list` (`publishedAt`) | "date joined" của Tube Atlas từng hỏng |
| Tốc độ tăng 24 giờ | `cf_research_stats.py --snapshot` / `--compare` | Một lần đo không thấy được "đang nổ" |
| RPM ngách | Không công cụ nào có số thật; dùng Studio của chính mình sau 7 ngày (`analytics-loop`) | Doanh thu ước tính của Tube Atlas không có cơ sở |
| Cây từ khoá autosuggest | Tube Atlas Keywords, hoặc tab A của OSS (miễn phí) | Nhanh khi làm số lượng lớn |
| Khai thác câu hỏi trong bình luận | **Tube Atlas Comments** (tiện), hoặc API `commentThreads.list` (cần viết script) | Lọc câu hỏi và cụm từ sẵn có |
| Tần suất tag, n-gram tiêu đề trên 500+ video | Tube Atlas Tag/Title Analyzer, hoặc `cf_research_stats.py` (đã có "words that repeat in outlier titles") | Tube Atlas tiện khi không muốn code |
| Trends nhiều quốc gia, nhiều nguồn | Tube Atlas Trends (bị hạn chế) hoặc trang Google Trends | |
| Kênh mới bùng nổ trên toàn YouTube | **Không công cụ nào ở đây làm được**; cần kho cào sẵn (TubeLab, 1of10, NexLev, TubeMind) | Tube Atlas chỉ thấy cái bạn tìm |

Một điểm tinh tế (INFERRED): chính sách API cấm ứng dụng API "obtain scraped YouTube data" ([Developer Policies](https://developers.google.com/youtube/terms/developer-policies)). Vì vậy **đừng nạp danh sách ID do Tube Atlas cào vào script API của studio**. Hãy giữ hai bộ dữ liệu tách nhau: CSV Tube Atlas đi thẳng vào `cf_research_stats.py`, còn bộ dữ liệu API thu bằng tìm kiếm và duyệt tay như cách studio đã làm ngày 13/11. Ngoài ra, dữ liệu thống kê lấy qua API không được lưu quá 30 ngày mà không làm mới (cùng nguồn).

### Đường ống xuất CSV từ Tube Atlas vào cf_research_stats.py

`cf_research_stats.py` cần mỗi video có `channel, title, views, published`, có thể thêm `duration_s, channel_subs, url`. Tên cột được khớp "lỏng" theo một danh sách alias có phân biệt hoa thường, ví dụ `channel_name`, `view_count`, `publishedAt`, `upload_date` (OBSERVED, mã nguồn `tools/cf_research_stats.py`). Tên cột của Tube Atlas, như "Channel Name" hay "Total Video Views", **không nằm trong danh sách alias**. Vì vậy phải đổi tên tiêu đề cột trước khi chạy:

| Cột Tube Atlas (theo trang bán) | Đổi thành | Ghi chú |
|---|---|---|
| Channel Name | `channel` | bắt buộc |
| Title | `title` | bắt buộc |
| Total Video Views | `views` | bắt buộc; dấu phẩy nghìn được tự bỏ |
| Date Published | `published` | bắt buộc; **phải ở dạng YYYY-MM-DD** (tool đọc YYYY-MM-DD hoặc YYYYMMDD; dạng 11/03/2026 sẽ thành rỗng) |
| Video Length in Seconds | `duration_s` | để tách dài/ngắn (mặc định ≤180 giây là Short) |
| Total Channel Subscribers | `channel_subs` | tuỳ chọn |
| Video Link | `url` | cần cho `--snapshot` / `--compare` |

Tên cột thật trong file CSV xuất ra và định dạng ngày **chưa đo**. Lần xuất đầu tiên phải mở file kiểm tra. Cách nhanh là mở bằng Excel/LibreOffice, đổi 7 tiêu đề, lưu "CSV UTF-8" vào `data/research/raw/2026-11-xx_tubeatlas_<ngách>.csv`, rồi chạy:

```
python tools/cf_research_stats.py data/research/raw/2026-11-14_tubeatlas_mc_horror.csv --niche "minecraft horror long" --out reports/research/2026-11-14_tubeatlas_mc_horror_stats.md --json reports/research/2026-11-14_tubeatlas_mc_horror_stats.json --snapshot reports/research/snapshots/2026-11-14_tubeatlas_mc_horror.csv
```

Ngày hôm sau, chạy lại với bộ dữ liệu mới và thêm `--compare reports/research/snapshots/2026-11-14_tubeatlas_mc_horror.csv` để có view tăng mỗi ngày thật. Các tham số khác: `--outlier-x` (mặc định 3,0), `--short-seconds` (mặc định 180), `--as-of`. Hai lưu ý từ cách tool tính (OBSERVED trong mã). Thứ nhất, outlier chỉ được tính cho kênh có **ít nhất 3 video** trong mẫu. Một mẫu Browse & Extract thường chỉ có 1 video mỗi kênh nên gần như không ra outlier. Muốn có trung vị kênh thật, hãy dùng **Channels → analyze all videos in channel** cho các kênh ứng viên rồi gộp vào file. Thứ hai, nếu Videos không có CSV, phương án dự phòng là báo cáo HTML (video 22) chuyển sang bảng tính, hoặc chép từ lưới. **Đề xuất cho `pipeline-engineer`** (INFERRED, cần owner đồng ý): thêm alias tiêu đề cột Tube Atlas vào `ALIASES` của `cf_research_stats.py`, kèm parse định dạng ngày và một pytest. Làm vậy đúng luật "extend existing modules", và owner khỏi phải đổi tên cột tay.

**Biên bản cho mỗi lần xuất** (INFERRED, theo quy tắc "measure, don't guess"): ghi phiên bản app, ngày giờ trích xuất, từ khoá và bộ lọc YouTube đã dùng, số dòng, số dòng trống hoặc lỗi, và kết quả so 5 dòng với youtube.com. Sau đó ghi quyết định bằng `python tools/cf_decision.py add --kind topic --decision "..." --why "..." --evidence "reports/research/..." --label OBSERVED --by owner` (đọc `list` trước).

## Phần 5: Ba quy trình thực chiến cho studio

**Quy trình A — Thẩm định ngách long-form (khoảng 2 giờ, khung `fast-niche-study`).** Keywords (seed theo ngách, quốc gia US) → Trends (YouTube search, 12 tháng, sắp theo slope) → Browse & Extract theo 3–5 từ khoá hàng đầu với bộ lọc thời lượng dài và tháng này → lưới Videos, lọc `Is Shorts = No` → custom filter "outlier tay", lưu file bộ lọc → **Get Related Videos** trên nhóm thắng để mở rộng → Channels: analyze all videos của 10 kênh đứng đầu → Tag/Title Analyzer trên tập outlier → Comments trên 3 video top → xuất → `cf_research_stats.py` → 3 đề xuất cho showrunner. Đây là phiên bản cụ thể của pipeline mà các tutorial đều mô tả ([imnights](https://imnights.com/tube-atlas-review); [SaaSPic](https://saaspic.com/tools/tube-atlas/)).

**Quy trình B — Phòng thí nghiệm Shorts (45 phút, khung `nightly-research`).** Mở mục Shorts trong trình duyệt tích hợp → tìm theo từng ngách con → auto scroll → analyze → chỉ giữ `Is Shorts = Yes` → sắp theo Average Views per Day → Title Analyzer để lấy mẫu câu → xuất → so với cổng 21 ngày của studio (trung vị ≥5K view/Short và ít nhất 1 Short ≥100K) (OWNER/PROPOSED, `docs/niches/minecraft_long_short_choice_2026-11-13.md`). Một reviewer affiliate khuyên người chỉ làm Shorts nên bỏ qua Tube Atlas ([Medium](https://medium.com/@earnmoneyonlinefast/youtube-success-isnt-about-luck-it-s-about-intelligence-92188ecfc2de)). Thực tế thư viện hướng dẫn không có video Shorts riêng, nên quy trình B phải được **owner tự kiểm chứng**.

**Quy trình C — Vòng tuần (khoảng 2 giờ/tuần, theo mô hình của reviewer Medium, đã điều chỉnh).** 30 phút Trends tìm chủ đề đang lên → 45 phút Channel Analyzer cho 5 đối thủ, chỉ xem video thắng trong 90 ngày → 20 phút cho mỗi video sắp làm: Keywords → Videos → tag/tiêu đề → 15 phút Comments tìm câu hỏi và lời phàn nàn ([Medium](https://medium.com/@earnmoneyonlinefast/youtube-success-isnt-about-luck-it-s-about-intelligence-92188ecfc2de)). Thêm bước của studio: snapshot hôm nay và compare với tuần trước.

## Phần 6: Bài tập tự làm cho các ngách Minecraft hiện tại

Các bài tập dùng đúng các ngách đang đề xuất: **L1** truyện kinh dị sinh tồn với thực thể gốc (20–30 phút) và **L2** "100 Days in a [mối đe doạ gốc]" (40–55 phút) cho long-form; **S2** vòng lặp vật lý 3D dựng bằng Blender với mascot khối gốc và **S3** thí nghiệm trong game / build hack cho Shorts (`docs/niches/minecraft_long_short_choice_2026-11-13.md`; `reports/Tiền Shorts Minecraft 1 triệu view.md`). Mỗi bài có câu hỏi tự kiểm tra. Nếu trả lời được bằng số có nhãn OBSERVED thì bài đã xong.

| # | Bài tập | Thao tác | Câu hỏi tự kiểm tra |
|---|---|---|---|
| 0 | **Cài đặt và smoke test** (30 phút) | Cài bản chính thức; ghi số phiên bản (mong đợi 1.0.6.7); **không** đăng nhập YouTube; tab Videos tìm "minecraft horror"; mở 5 dòng và so view/ngày đăng/sub với youtube.com; mở menu File của Keywords, Videos, Channels, Comments và ghi công cụ nào có CSV | Có bao nhiêu trong 5 dòng khớp với YouTube? Cột nào trống? Lưới Videos có xuất CSV không? (Nếu số liệu sai hoặc không xuất được, hãy cân nhắc hoàn tiền trong 30 ngày.) |
| 1 | **Cây từ khoá L1/L2** | Keywords: seed "minecraft horror", "minecraft 100 days", "minecraft survival movie", country US → Generate → copy comma separated → lưu CSV | Liệt kê 5 cụm long-tail có từ chỉ mối đe doạ ("hunted", "entity", "infection"…) **không** chứa tên nhân vật của creator khác. Cụm nào hợp với thực thể gốc của studio? |
| 2 | **Trends so sánh ba làn** | Trends: nhập "minecraft horror", "minecraft 100 days", "minecraft build hacks", "minecraft physics"; nguồn YouTube search, US, 12 tháng; sắp theo slope; lưu ảnh biểu đồ | Cụm nào có slope dương? Có mùa vụ nào (ví dụ Halloween) không? Vì sao không được đọc chỉ số này như số lượt tìm tuyệt đối? |
| 3 | **Thu mẫu long-form horror** | Browse & Extract: tìm "minecraft horror", lọc This month + Over 20 minutes; auto scroll; extract → Videos; `Is Shorts = No`; custom filter Publish Age ≤ 90 và sắp Average Views per Day; lưu file bộ lọc `CINE_L1_horror`; xuất → đổi tên cột → `cf_research_stats.py --niche "mc horror long"` | Trung vị view của mẫu là bao nhiêu? So với trung vị horror 371K/video trong mẫu API trước, vì sao hai số có thể khác (khác cách lấy mẫu, khác ngày)? |
| 4 | **Kênh thắng lặp lại hay ăn may** | Channels: nhập kênh của 10 video top bài 3 → analyze all videos → sắp theo views per day; xem date joined; gộp vào file và chạy lại stats | Kênh nào có ≥2 video vượt 3× trung vị của chính kênh (thắng lặp lại)? Kênh nào ≤365 ngày tuổi? Có kênh nào giống Day Zero (2M view chỉ với 2 video) không? |
| 5 | **Bình luận cho L1** | Comments trên 3 video horror dài top: extract → lọc câu hỏi → top cụm từ (ví dụ "part 2", "scared", "ending") | Ghi 5 điều người xem muốn và 3 điều họ phàn nàn (nhịp, jumpscare, kết). Điều nào biến được thành lời hứa trung thực ở 30 giây đầu của tập L1? |
| 6 | **Shorts S2: vòng lặp vật lý Blender** | Trình duyệt tích hợp → mục Shorts; tìm "minecraft physics", "satisfying minecraft", "1000 tnt vs"; auto scroll → analyze; `Is Shorts = Yes`; sắp view/ngày; Title Analyzer trên top 50 | Ba mẫu tiêu đề lặp nhiều nhất là gì? Ý tưởng nào là **cơ chế** (studio dùng được) và ý tưởng nào là **tài sản riêng** của kênh khác (không được chép)? Trung vị ngách có vượt mốc 5K của cổng 21 ngày không? |
| 7 | **Shorts S3: thí nghiệm trong game / build hack** | Như bài 6 với "minecraft build hack", "minecraft redstone trick", "minecraft experiment"; Tag Analyzer; Comments trên 3 Short top để lọc câu hỏi | Kể 5 câu hỏi người xem đặt ra ("how do you…", "what version…") mà chưa video top nào trả lời. Đó là danh sách ý tưởng S3 đầu tiên. |
| 8 | **Tiêu đề cho tập của mình** | Title Generator: "minecraft survival horror" → chọn 10 khuôn → viết lại với thực thể gốc → đưa qua `policy-check` | Mỗi tiêu đề có hứa đúng điều video thật sự có không? Có từ nào là tên hay nhân vật của người khác không? |
| 9 | **(Tuỳ chọn) bản OSS** | Sau khi owner duyệt khoá: tab A với seed "minecraft horror" US/en, không KGR, xuất CSV và xem question buckets; Outlier Finder US, 14 ngày, max subs 100K, ratio 3; xuất CSV → `cf_research_stats.py` | Vì sao một video xếp cao trong Outlier Finder (view/sub) lại có thể không phải outlier trong `cf_research_stats` (view/trung vị kênh)? Bạn tiêu bao nhiêu unit quota (xem Google Cloud console)? |
| 10 | **Vòng 24 giờ** | Chạy lại bài 3 và bài 6 vào hôm sau với `--compare` snapshot hôm trước | Video nào tăng view/ngày thật cao nhất? Kết quả có khác với "Average Views per Day" của Tube Atlas (trung bình cả đời video) không, và vì sao? |

Đáp án gợi ý cho câu khó nhất (bài 9, INFERRED): công thức OSS chia view cho **sub**, nên một kênh nhỏ có một video ăn may, hoặc kênh ẩn sub (bị coi là 1.000), sẽ có tỉ lệ cao. `cf_research_stats` so với **trung vị view của chính kênh** và cần ít nhất 3 video, nên nó loại được những vụ ăn may đó. Đó là lý do studio dùng trung vị làm chuẩn.

## Phần 7: Checklist để không bỏ sót chức năng nào

Cột "Đã thử" để owner tự đánh dấu. "Dùng" nghĩa là dùng được cho CINE sau khi owner chấp nhận rủi ro ToS; "Điều kiện" là cần owner duyệt; "Không" là không dùng cho CINE nhưng cần biết.

| Module | Chức năng | CINE | Đã thử |
|---|---|---|---|
| Lưới chung | Quick filter; custom filter; lưu/nạp file bộ lọc; sắp xếp; column configuration; thanh đếm; re-extract; ReExtract NOT EXTRACTED; Extract Missing | Dùng | ☐ |
| Lưới chung | Save/Load data; preview/save báo cáo HTML (2 định dạng); Open data folder; CSV (kiểm tra từng công cụ) | Dùng | ☐ |
| Keywords | Seed; country; Generate; checkbox; import volume miễn phí (file Keyword Planner); Import Keywords; copy comma separated; hashtag; save CSV | Dùng | ☐ |
| Keywords | Keywords Everywhere tool | Điều kiện (tốn tiền) | ☐ |
| Trends | Import; 258 quốc gia; 5 nguồn; khoảng thời gian; mini chart/full chart; average; slope; lưu ảnh; copy; hashtag | Dùng (bị hạn chế) | ☐ |
| Videos | Search đỏ + settings; Google option; Trending Videos; nhập từ Browse & Extract; nhập từ content extraction | Dùng | ☐ |
| Videos | 35 cột + Is Shorts; Average Views per Day; Publish Age; Category; Subtitles; Ads Found; Tag Keywords | Dùng | ☐ |
| Videos | Estimated Video Earnings / per Day | Chỉ xếp hạng tương đối | ☐ |
| Videos | Get Related Videos; Get Video Ads; copy hashtags; embed codes | Dùng | ☐ |
| Videos | Unlisted videos | Tránh | — |
| Videos | Emails/Phone in Description; Save emails to CSV/TXT | **Không** | — |
| Video Details | Copy tiêu đề/tag/mô tả; đếm; readability/grade; HTML viewer | Dùng | ☐ |
| Video Details | Tải video/thumbnail; spin mô tả; trình phát ad-free | **Không** | — |
| Browse & Extract | Trình duyệt; bookmark; bộ lọc YouTube; auto scroll; extract video/channel links; đếm kênh; Shorts analyze; trang web bất kỳ | Dùng, khối lượng vừa phải | ☐ |
| Channels | Tìm từ khoá; nhập từ B&E/content extraction; analyze all videos; date joined; khung chi tiết (country, keywords, external links); @handle; doanh thu ước tính | Dùng | ☐ |
| Comments | Extract; autoscroll; like/reply; cờ câu hỏi; profanity; cụm từ; lọc theo cụm; nhấp đúp xem | Dùng (không lưu tên người) | ☐ |
| Tag Analyzer | Số lần xuất hiện; %; view/like trung bình; hashtag | Dùng | ☐ |
| Title Analyzer | Cụm từ tiêu đề; hashtag | Dùng | ☐ |
| Title Generator | 1.200+ khuôn | Dùng để brainstorm | ☐ |
| Video-to-Text | Link/Shorts; nhận ngôn ngữ; Auto punctuate offline (EN); Make Paragraphs; Find & Replace; keyword detection; important sentences; summarization; text-to-headline; image search/suggested images; HTML editor/Save to HTML | Điều kiện (chỉ đọc cấu trúc) | ☐ |
| Video-to-Text | File-to-Text (Gladia/Deepgram); prompt ChatGPT | Điều kiện (tốn tiền); dùng `local-whisper` thay thế | — |
| Video-to-Text | "Legal content" từ video Creative Commons; spin transcript | **Không** | — |
| Content Spinner | Dịch vòng 109 ngôn ngữ; word replace | **Không** | — |
| Video Downloader | Video đến 4K, m4a/mp3, chỉ hình, thumbnail | **Không** | — |
| Settings | Kiểm tra cập nhật; News and updates; quản lý máy cài; Speech to Text APIs; tin nhắn trong app; menu Tools | Dùng | ☐ |
| Settings | Nhiều đăng nhập YouTube | Không đăng nhập kênh owner | — |
| Bonus | Description Generator; 19 template; hashtag online; đào tạo Shorts; 10 content + 8 PDF reports; 44 video hướng dẫn | Tham khảo | ☐ |
| Upsell | Tube Video Translator; Tube Video Tracker; gói 4 app $97; bundle $77 (không hoàn tiền) | Không cần lúc này | — |
| OSS | Trang chủ (trạng thái khoá, ngôn ngữ); Research tab A (autocomplete, question buckets, gauges, KGR, CSV) | Dùng tab A miễn phí; KGR cẩn thận quota | ☐ |
| OSS | Research tab B (Trends, Trend Pulse, Opportunity, Breakouts, Top channels, Audience pulse) | Dùng có chừng mực (~503 unit/lần) | ☐ |
| OSS | AI verdict DeepSeek | Điều kiện (tốn tiền) | — |
| OSS | Outlier Finder (CSV, cache 15 phút) | Dùng, rồi chuẩn hoá bằng `cf_research_stats` | ☐ |
| OSS | Video Cloner: fingerprint | Chỉ đọc metadata | ☐ |
| OSS | Video Cloner: title clones, script clone | **Không** | — |
| OSS | Studio 5 bước | **Không** (xưởng kịch bản song song) | — |
| OSS | Producer short/long_form; ComfyUI/RunningHub | Không cần (đã có vòng render của studio) | — |
| OSS | Producer → Grok | **Không** (tự động hoá trái điều khoản) | — |

## Kết luận và khuyến nghị

Điều thay đổi sau khi học kỹ: giá trị của Tube Atlas **không nằm ở việc "tìm ngách"**, việc nó không làm được. Giá trị nằm ở **thu thập hàng loạt và khai thác chữ**: Browse & Extract vượt giới hạn một trang, Comments lọc câu hỏi, Tag/Title Analyzer đếm n-gram, Trends nhiều nguồn. Những gì cần độ chính xác (số liệu, outlier, tăng trưởng) studio đã làm tốt hơn và sạch hơn bằng API chính thức cộng `cf_research_stats.py`. Vì vậy hướng đúng là **API làm xương sống, Tube Atlas làm tay chân phụ**, chứ không ngược lại. Hai bản Tube Atlas cũng đều đang chậm lại: bản trả phí chỉ vá lỗi theo kiểu chữa cháy, bản OSS đã ngừng. Mọi kết luận dựa trên dữ liệu của chúng phải kèm số phiên bản, ngày trích xuất và lần so 5 dòng.

**Khuyến nghị (INFERRED, cần owner quyết):** Nếu owner muốn công cụ giao diện để tự nghiên cứu, **có thể mua Tube Atlas bản chính thức 1.0.6.7 giá $47, chỉ gói chính, bỏ qua mọi upsell và bundle** (bundle không được hoàn tiền). Dùng 30 ngày hoàn tiền như một bài kiểm tra nghiệm thu, tức bài tập 0: nếu số liệu không khớp YouTube, lưới Videos không xuất được dữ liệu, hoặc Browse & Extract bị chặn khi chạy từ Việt Nam, thì hoàn tiền. Chỉ dùng các chức năng đọc dữ liệu được đánh "Dùng" trong checklist. Với bản OSS, chỉ đáng chạy **tab A** (miễn phí) và có thể là Outlier Finder; không điền khoá DeepSeek nếu chưa duyệt chi phí; không bao giờ dùng Cloner script, Studio hay Grok. Việc rẻ hơn và đúng luật hơn cả là nhờ `pipeline-engineer` thêm vào script API hiện có hai thứ: lấy bình luận qua `commentThreads.list` (1 unit) và alias cột cho CSV Tube Atlas. Làm vậy thì phần lớn lý do để mua sẽ biến mất. Owner cần quyết năm điều: (1) đang nói về Tube Atlas nào; (2) có chấp nhận rủi ro điều khoản YouTube của một công cụ cào dữ liệu ở mức dùng tay, khối lượng nhỏ hay không, vì luật studio cấm tự động hoá trái điều khoản; (3) có duyệt $47 không; (4) có duyệt chi phí API tính tiền (Keywords Everywhere, Gladia/Deepgram, DeepSeek) hay giữ ở $0; (5) các ngưỡng lọc "outlier tay" (tuổi video, trần sub, bội số trung vị). Theo luật số 3 của studio, đây là quyết định OWNER và phải được ghi bằng `tools/cf_decision.py`.
