# Ngách có thể bùng nổ cho kênh mới, khả năng làm chất lượng cao, và đánh giá danh sách công cụ chủ kênh gửi (2026-11-03)

Số liệu là **OBSERVED** trong vòng nghiên cứu 1 (`2026-11-03_minecraft_story.md`), trừ chỗ ghi khác. Phần đánh giá là **INFERRED**.

## A. Ngách có tín hiệu "kênh nhỏ / kênh mới bùng nổ"

| # | Ngách | Bằng chứng (OBSERVED 2026-11-03) | Ta làm được không? |
|---|---|---|---|
| 1 | Fan-animation Maizen (JJ/Mikey, JJ Sister, love story) | Cubeee 2.06M = 41× subs; Mine Block 3.45M = 30× subs; Морфиз 1.54M = 21× subs; Ligabka 672K sau 3 ngày = 9.8× subs | **Không.** Dùng nhân vật của Maizen là vi phạm luật IP gốc của kênh và có rủi ro bản quyền |
| 2 | Crossover mascot hot (Verity, Sprunki, Poppy Playtime) | MyMy toon 4.1M = 10× median kênh | **Không** (IP của bên thứ ba). Chỉ học cấu trúc "SAD ORIGIN STORY" |
| 3 | Video AI bán-hiện-thực: Steve & Alex + baby mob + đồ ăn | DL Minecraft (2.58K subs): 502K = 195× subs | **Có, bằng 3D tự dựng, không cần AI** (sửa 2026-11-03: bản đầu ghi nhầm là phải dùng credit AI). Dựng rig khối trong Blender, render Cycles với vật liệu PBR thật và asset Poly Haven CC0. Nên dùng Zu thay cho Steve/Alex. Thời gian render chưa đo |
| 4 | **Hoạt hình truyện Minecraft gốc** (gia đình, nghèo–giàu, mob) | Iron Studio "Rich Axolotl's Downfall" 420K = 20.8× subs sau ~12 ngày; BigSchool median 1.7M; Class Monster School compilation 4.3M | **Có, đây là ngách chính của ta** |
| 5 | Gameplay / roleplay, "100 Days" | Mozi 945,889 view sau ~7 ngày = 2.6× subs; ProBoiz 6.82M/14 ngày; Carry Depie 2.57M/11 ngày | Chất lượng hình dễ đạt cao (Replay Mod + shader), nhưng **cần người chơi thật** 40–60 giờ mỗi video dài |
| 6 | "100 Days" dạng hoạt hình | Maizen "Survived 100 Days in an EXPANDING…" 3.52M trong ~28 ngày | **Có.** Ghép ngách 4 với thể thức 100 ngày; cần set lớn (Minecraft Java + map) |

**Thứ tự đề xuất:** 4 → 3 (dựng 3D bằng Blender, dùng Zu) → 6 → (5 nếu chủ kênh tự chơi). Ngách 1 và 2 bỏ.

## B. Quy trình có đạt chất lượng cao trong các ngách đó không (INFERRED)

- **Ngách 4 và 6: đạt được.**
  - Từng khung hình đã gần mức BigSchool (`2026-11-03_level_scorecard.md`).
  - Còn thiếu: nội dung dài, âm thanh, bối cảnh lớn, tốc độ.
  - Có Minecraft Java + map + BBS/Replay Mod thì bối cảnh và diễn xuất sẽ nhanh hơn nhiều.
  - Blender + MCprep dùng cho cảnh hiệu ứng.
  - Giới hạn thật là sản lượng: 1 GPU, khoảng 33 phút render cho mỗi phút phim với Mine-imator.
- **Ngách 5: hình đạt cao dễ dàng, nhưng điểm nghẽn là người chơi.** Bot Mineflayer làm được trên server riêng, nhưng diễn rất cứng.
- **Ngách 3: phụ thuộc credit AI.** Theo luật kênh, chưa có chủ kênh duyệt thì không chi.

## C. Đánh giá từng công cụ trong tài liệu

| Công cụ | Kết luận | Lý do / điều kiện |
|---|---|---|
| Mine-imator | ✅ Đang dùng | Công cụ chính hiện tại |
| Blender + Blender MCP | ✅ Đã có | Blender 4.5 đã có trên máy; Blender MCP đã kết nối với phiên này |
| sandraschi/blender-mcp | ⏸ Chưa cần | Chưa kiểm tra; đã có Blender MCP và worker headless của CineFactory |
| MCprep | ✅ Đã tải | Dùng để nạp rig và world Minecraft vào Blender |
| Blockbench | ✅ Nên cài | Miễn phí; làm đạo cụ, mô hình, mob gốc |
| Replay Mod | ✅ Nên dùng (cần Minecraft Java) | Ghi lại toàn bộ không gian 3D rồi đặt camera sau; hợp ngách 5 và 6 |
| BBS mod (McHorse) | ✅ Nên thử (cần Minecraft Java) | Modrinth: Fabric 1.20.1 / 1.20.4 / 1.21.1, giấy phép ARR (tải miễn phí, không được phân phối lại) |
| Mixamo | 🟡 Tùy chọn | Miễn phí với Adobe ID, dùng thương mại không trả phí bản quyền; chủ kênh phải tự tạo tài khoản; cần retarget sang rig khối trong Blender |
| Mineflayer | 🟡 Ưu tiên thấp | Chạy trên server riêng; diễn máy móc |
| Planet Minecraft / minecraft-maps | 🟡 Dùng có điều kiện | Cần Minecraft Java; giấy phép mỗi map khác nhau, phải ghi nguồn và kiểm tra quyền quay video từng map (lưu vào sổ nguồn) |
| NameMC / minecraftskins / PMC skins | ❌ Không dùng cho dàn nhân vật | Luật IP gốc; skin là tác phẩm của người khác. Chỉ tham khảo |
| NovaSkin editor | ✅ Dùng được | Vẽ hoặc sửa skin gốc của ta |
| NovaSkin wallpapers (thumbnail) | ❌ Không khuyên | Mẫu bị nhiều kênh dùng chung nên không độc đáo; chưa kiểm điều khoản. Ta tự render thumbnail |
| Incompetech | ✅ Dùng | CC-BY, ghi nguồn trong mô tả |
| Freesound | ✅ Dùng có lọc | Chỉ dùng CC0 / CC-BY; tránh CC-BY-NC vì kênh có kiếm tiền |
| TTSMaker | 🟡 Dùng được | Trang web ghi cho dùng thương mại miễn phí, không cần ghi nguồn; giới hạn 20.000 ký tự/tuần. Ta đã có Kokoro (Apache-2.0) chạy trên máy |
| CapCut PC | ❌ Không khuyên cho doanh nghiệp | Điều khoản 2025 bị phản ánh là cấp cho CapCut giấy phép rộng, vĩnh viễn trên nội dung. Ta dựng bằng ffmpeg + cf_auto_edit + Whisper |
| ChatGPT / DeepSeek | Không cần | Claude viết kịch bản |

**"Audio first" (thu tiếng trước, làm hình sau):** đồng ý. CineFactory đã làm vậy từ thu01/thu02 (lấy thời lượng câu thoại để quyết định khung hình).

## D. Cần thêm gì

1. Minecraft Java (trả phí, chủ kênh mua). Mở khóa được: Replay Mod, BBS, map, import world vào Mine-imator/Blender.
2. Fabric Loader + Fabric API, Replay Mod, BBS mod, Iris + Complementary shaders (miễn phí).
3. Blockbench (miễn phí).
4. Tùy chọn: Adobe ID cho Mixamo; tài khoản Freesound. Chủ kênh tự tạo, em không tạo tài khoản.
5. Một sổ nguồn (asset ledger) ghi giấy phép của mọi nhạc, SFX và map được dùng.
