# Ma trận năng lực × ngách: những ngách studio làm được, không chỉ bằng AI (2026-11-12)

Owner hỏi: "nghiên cứu kỹ xem các ngách bạn làm được, đâu chỉ AI thôi". Trạng thái: **PROPOSED**, chờ owner duyệt.

> **OWNER 16:33:** CineFactory chỉ làm YouTube. Bỏ hết các mục ngoài YouTube: WoodFab, B2B, quay xưởng thật, dịch vụ, khóa học. Phương án còn hiệu lực xem mục "Đề xuất sau khi owner sửa" ở cuối tài liệu.

## Dữ liệu
- **Quét API toàn YouTube, 22 ngách:** `reports/research/wide_scan_2026-11-12/`.
- **Quét theo năng lực, thêm 12 ngách:** `reports/research/capability_scan_2026-11-12/`. Tìm kiếm trên trình duyệt (top tháng và đăng hôm nay), cộng `channels.list` tốn 9 unit. Mẫu nhỏ, chỉ cho biết xu hướng.
- **Nghiên cứu sâu:** `reports/Ngách YouTube ngoại làm bằng AI.md`.
- **RPM:** AIR Media-Tech, số đo theo nhóm danh mục. Education $10,22; Crafting $2,39; Tech $2,33; Gaming $2,05.

## Năng lực thật của studio (không chỉ AI)
| Năng lực | Công cụ |
|---|---|
| 3D thủ tục, có cơ khí và kiến trúc | Blender 4.5/5.2 + Python (bpy), Geometry Nodes, OSM, Poly Haven |
| Hoạt hình bằng code | Manim, Revideo, D3/Plotly, bản đồ, dữ liệu |
| Kịch bản và giọng đọc | Afanta Studio, TTS có giấy phép thương mại |
| Chuyên môn nội thất và CNC | Xưởng CNC thật, WoodFab (từ bản vẽ đến G-code) |
| Mod Minecraft | Fabric/GeckoLib, datapack |
| Quay màn hình hướng dẫn phần mềm | Blender, Python, Claude Code, WoodFab |
| Agent và tự động hoá | Claude Code + MCP, CineFactory OS |

## Kết quả quét 12 ngách theo năng lực (OBSERVED)
| Ngách | Top tháng: trung vị view | Video ≥1M | Kênh mới (≤365 ngày) có video ≥100K | Ví dụ kênh mới |
|---|---|---|---|---|
| How it works 3D | 136K | 0 | 4 | Exploded Works (44 ngày, 482K); Keelprint (31 ngày, 109K) |
| Ancient engineering 3D | 45K | 3 | 2 | The Farm Blueprint (50 ngày, **1,41M**); Stone & Physics (50 ngày, 395K) |
| Bản đồ lịch sử / data-viz | 268K | 6 | 3 | RoZoom Maps (34 ngày, 268K, 41 phút); Atlas Unfolded (29 ngày, 181K); Mapnificent (211 ngày, 399K) |
| Woodworking build (thật) | 220K | 2 | 2 | TaLiLu (129 ngày, 13,7K sub, 323K/41 phút); MONIE DOLLY (85 ngày, 192K) |
| Math/physics explainer | 13K | 0 | 1 | Mr Space Explainer (251 ngày, 213K) |
| Coding/AI tools tutorial | 555K | 3 | 2 | Video lớn chủ yếu thuộc kênh có người dẫn |
| Blender tutorial | 50K | 0 | 0 | 15 kênh đăng hôm nay thì 13 kênh ≥1K sub: kênh cũ chiếm chỗ |
| Excel/CAD tutorial | 20K | 0 | 0 | Kênh cũ chiếm chỗ |
| CAD/CNC/cabinet | **2K** | 0 | 0 | Nhu cầu quảng cáo rất nhỏ, chỉ hợp làm kênh B2B tìm khách cho WoodFab |
| Minecraft build/mod | 557K | 8 | 1 | Gần như toàn kênh lớn |
| Game devlog | 152K | 0 | 0 | mjgdev (232 ngày, 88K) |
| True scale 3D | 76K | 0 | 0 | Không thấy kênh mới bứt phá trong mẫu |

## Xếp hạng ngách studio làm được (INFERRED)
| Hạng | Ngách | Làm bằng gì | RPM | Bằng chứng kênh mới | Vai trò |
|---|---|---|---|---|---|
| 1 | **Tài liệu 3D lịch sử và kỹ thuật**: how it works, ancient engineering, thảm họa trước 1950 | Blender + Python, Afanta | Education ~$10 | Mạnh: Farm Blueprint 1,41M, Exploded Works 482K, Deconstructed 439K sub | **Kênh tiền chính** |
| 2 | **Bản đồ lịch sử động / data-viz** | Code (Manim/D3/Blender GIS), OSM, Afanta | Education/News ~$3–10 | Mạnh: RoZoom Maps, Atlas Unfolded, Mapnificent | Nhập vào kênh 1 thành một dòng video riêng, hoặc làm kênh 2 |
| 3 | **Woodworking/CNC build thật**, chỉ quay tay, không lộ mặt | Xưởng thật, máy quay, WoodFab | Crafting ~$2,4, cộng affiliate dụng cụ, khách B2B, khách WoodFab | Có: TaLiLu, MONIE DOLLY | Kênh 2 nếu xưởng có thời gian. Đây là lợi thế độc quyền |
| 4 | Hướng dẫn phần mềm (Blender/Python/Claude Code/WoodFab) | Quay màn hình + giọng | Tech ~$2,3; tiền thật nằm ở khóa học/affiliate | Yếu: kênh cũ chiếm chỗ | Để sau, làm như bộ hồ sơ năng lực cho dịch vụ |
| 5 | Math/physics bằng Manim | Code | Education | Có nhưng nhỏ | Dòng phụ của kênh 1 |
| – | Minecraft (horror/build), Slow English, sleep, revenge drama, AI nature, kids | | | | Không làm kênh tiền (xem các tài liệu trước) |

## Đề xuất
1. **Kênh 1 (chính): "3D history & engineering explained".**
   - Chủ đề: thảm họa và công trình trước 1950, cỗ máy cổ, bản đồ chiến dịch lịch sử.
   - Video 20–40 phút, 2–4 video mỗi tháng.
   - Hình chính: Blender và code. AI chỉ hỗ trợ kịch bản và giọng đọc.
2. **Kênh 2, owner chọn một:**
   - (a) Woodworking/CNC build thật từ xưởng: độc quyền, kéo thêm khách WoodFab.
   - (b) Bản đồ lịch sử động thành kênh riêng.
3. **Cổng thử nghiệm:**
   - G0: làm thử 1 video và đo giờ làm thật.
   - G2: sau 6 video, cần ít nhất 1 video ≥10K view trong 28 ngày và trung vị ≥1K.

## Đề xuất sau khi owner sửa (16:33): chỉ YouTube
1. **Kênh 1:** 3D history & engineering explained.
2. **Kênh 2:** bản đồ lịch sử động / data-viz.

Cả hai kênh làm hoàn toàn trên máy bằng CineFactory (Blender, Python, code, Afanta). Nguồn thu là quảng cáo YouTube.
