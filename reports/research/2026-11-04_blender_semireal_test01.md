# Bản thử 01: Blender bán-hiện-thực "Zu ăn pizza" (2026-11-04)

**Tóm tắt:** 10 giây, 6 shot, 1080p24, dựng hoàn toàn bằng code (`tools/blender_block/`) và render bằng EEVEE trên RTX 3060.
- File: `BinBo_Blender_thu01_ZuPizza.mp4` (5,1 MB), lưu ở `C:\Users\ADMIN\Downloads\Bin_Bo\`.
- IP gốc: skin và mặt Zu do code của mình vẽ. Bếp, pizza, khói đều dựng thủ tục, không tải model, texture hay HDRI nào.
- Minecraft Java: Launcher đã cài, có thư mục bản 26.3 (OBSERVED). Bản thử này **không dùng** game.

## Thời gian render (OBSERVED, `render_log.json`, RTX 3060, 1920×1080)

| Cách render | Giây/khung | 10 s phim | Ghi chú |
|---|---|---|---|
| Cycles 48 spp, khử nhiễu OIDN trên CPU (mặc định) | 36–40 | ~2,5 giờ | 1 spp vẫn mất 6,9 s |
| Cycles 48 spp, khử nhiễu OIDN trên **GPU** | 13,6 | ~55 phút | Sửa trong `render.py` và `build.py` |
| Cycles 128 spp, khử nhiễu CPU | 54 | — | |
| EEVEE 64 TAA, volumetric thô | 2,2–2,7 | ~10 phút | Khói gần như không thấy |
| **EEVEE 96 TAA, volumetric tile 2 (bản cuối)** | **6,3 trung bình, 6,0 trung vị, 9,2 tối đa** | **25,2 phút** | |
| Mine-imator thu03, để so | 1,35 | 3,6 phút | Cần bấm giao diện |

Quy đổi (INFERRED): khoảng 150 phút render cho mỗi phút phim với EEVEE, so với khoảng 33 phút với Mine-imator. Một tập 10 phút cần khoảng 25 giờ GPU.

Bù lại, toàn bộ quy trình chạy không cần giao diện. Có thể render qua đêm, render song song nhiều cảnh, và chỉ render lại đúng cảnh vừa sửa.

## Số đo hình và tiếng (OBSERVED: `benchmark_frames.py`, ebur128)

| Chỉ số | Blender thu01 | Mine-imator thu03 v2 | BigSchool |
|---|---|---|---|
| Cắt cảnh / phút | 24 (máy đo nhận 4 trên 5 lần cắt thật) | 15 | 39–45 |
| Chuyển động | 12,9 | 10,4 | 5,1–5,4 |
| Độ sáng | 172 | 138 | 116–133 |
| Độ bão hòa | 0,34 | 0,46 | 0,43–0,45 |
| Độ to | −13,7 LUFS, đỉnh −2,4 dBFS | −14,4 LUFS | — |
| Tỉ lệ âm trầm | 0,39 | 0,11 | 0,17 (MSToons 0,57) |
| Sàn tiếng p10 | −22,9 dB | −39,7 dB | −33,6 dB |

## Điểm được và chưa được (INFERRED)

**Được**
- Ánh sáng ấm, có chiều sâu trường ảnh, đổ bóng thật, khói nóng.
- Pizza có phô mai kéo sợi; tay cầm đúng miếng bánh, sai số khi chạm vỏ 13,7 mm; đầu miếng bánh vào miệng, sai số dưới 3 mm.
- Chọn chế độ màu **Khronos PBR Neutral** thay cho AgX: AgX làm nhạt màu đồ ăn, đã thử so sánh các bản `vw_*`.

**Chưa được**
- Ảnh hơi sáng (172).
- Ở khung 162–172 tay xoay nhanh nên bị nhòe chuyển động, miếng bánh mất trong vài khung.
- Tay khối không có khuỷu, nên ở cận cảnh cắn bánh cánh tay che mất nửa khung hình.
- Pizza vẫn có cảm giác "đồ chơi" khi so với ảnh AI tả thực.

**Ngách (xem `reports/Ngách Minecraft RPM cao bền vững.md`):** thể thức đồ ăn bán-hiện-thực chỉ được 9/20 điểm, vì dễ bị xếp vào nội dung trẻ em và vướng luật nội dung lặp mẫu. Bản thử này nên coi là **kiểm tra kỹ thuật** (rig, vật liệu, tốc độ), không phải định hướng nội dung.

## Bài học kỹ thuật (MEASURED, đã đưa vào code)
1. `cycles.denoising_use_gpu` mặc định là False. Bật lên thì Cycles nhanh gấp 2,8 lần.
2. `device_commit_files` lấy bản cũ khi ghi đè cùng một đường dẫn staged. Mỗi bản dựng phải đặt tên mới (`zu_pizza_bN.blend`) và kiểm tra md5 trên máy trước khi render.
3. Render nền bằng `subprocess.Popen` từ Blender MCP, không chặn GUI và không bị hết thời gian chờ.
