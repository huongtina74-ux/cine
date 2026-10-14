Dựa trên kết quả điều tra và tổng hợp từ **4 chuyên gia nghiên cứu song song** (quét trực tiếp các cập nhật kỹ thuật, xu hướng studio Hollywood và mã nguồn GitHub đến thời điểm **Tháng 10/2026**), đây là bức tranh toàn cảnh về **"Cú nhảy Agentic" (The Agent Leap)** và hệ sinh thái **AI, Repos, MCP, Multi-Agent** mà các cao thủ điện ảnh và đồ họa đang sử dụng:

---

### BỐI CẢNH THÁNG 10/2026: SỰ CHUYỂN DỊCH TỪ "PROMPT" SANG "AGENTIC PIPELINE"
Nếu như giai đoạn 2023–2024 ngành đồ họa chỉ dừng lại ở việc gõ prompt tạo ảnh/video đơn lẻ, thì đến **cuối năm 2026**, toàn bộ ngành công nghiệp đã bước sang kỷ nguyên **Multi-Agent Orchestration**:
1. **Model Context Protocol (MCP)** trở thành "cổng USB-C phổ quát" kết nối trực tiếp các mô hình AI/Agent vào thẳng bên trong Maya, Nuke, Houdini, Blender, Figma và Photoshop.
2. **Sự biến mất của các mô hình hào nhoáng:** Đáng chú ý nhất, **OpenAI đã chính thức khai tử Sora** (đóng ứng dụng web vào tháng 4/2026 và tắt toàn bộ Developer API vào tháng 9/2026) do không đáp ứng được yêu cầu kiểm soát chuẩn pipeline. Ngành điện ảnh chuyển dịch hoàn toàn sang các mô hình có độ kiểm soát tham số tuyệt đối như **Runway Gen-4.5 ("David")**, **FLUX 3**, và **ComfyUI local clusters**.
3. **Từ 3DGS tiến hóa lên 4D Gaussian Splatting (4DGS):** Xử lý môi trường thể tích động có yếu tố thời gian, được chuẩn hóa bởi Khronos Group (`KHR_gaussian_splatting`) và tích hợp thẳng vào Nuke 17, Houdini 22.

---

## PHẦN 1: BẢNG TỔNG HỢP MCP SERVERS CHO CREATIVE & VFX (OCTOBER 2026)

*MCP (Model Context Protocol) cho phép AI Agents "nhìn" được cảnh 3D, hiểu cấu trúc Node Graph và tự viết mã API để thao tác thay con người:*

| Ứng dụng | Tên MCP Server / Repo | Năng lực & Công cụ tích hợp |
| :--- | :--- | :--- |
| **Blender** | **Official Blender MCP**<br>`RFingAdam/mcp-blender`<br>`6xvl/blender-mcp` | • Expose toàn bộ `bpy` API qua kết nối local `stdio`.<br>• Repo của RFingAdam cung cấp **218 tools**, repo của 6xvl cung cấp **~270 tools** hỗ trợ dựng hình, vật liệu, tự sửa lỗi treo máy (hang detection). |
| **Maya** | **`PatrickPalmer/MayaMCP`**<br>`AYDJI/Autodesk-Maya-MCP`<br>`dcc-mcp/dcc-mcp-core` | • Kết nối qua Maya MEL Command Port.<br>• Hơn **30+ tools** chuyên sâu: extrude, bevel, boolean, quản lý phân cấp xương và kiểm tra lưới tự động qua lệnh tự nhiên. |
| **Houdini** | **`healkeiser/fxhoudinimcp`**<br>`oculairmedia/houdini-mcp`<br>*(Native Apex Script in H22)* | • Hơn **215+ tools** điều khiển simulation, Solaris LOPs/USD và xuất cache.<br>• Sử dụng `hrpyc` (Houdini Remote Python) để AI can thiệp trực tiếp vào mạng VEX/Python node. |
| **Nuke** | **`kleer001/nuke-mcp`**<br>`linchpinhq/nuke-mcp` | • **57 tools** quản lý Node Graph, Deep Compositing, điều khiển không gian 3D của Nuke và tự động hóa khâu Render Passes. |
| **Cinema 4D** | **`kumoproductions/mcp-cinema4d`**<br>`sdimaging/cinema4d-mcp` | • **93 tools** hỗ trợ Scene Nodes, OSL shader injection và điều khiển tham số render Redshift/Octane. |
| **Unreal Engine** | **`remiphilippe/mcp-unreal`**<br>`ChiR24/Unreal_mcp` | • Kết nối Unreal Automation Bridge.<br>• Điều khiển trực tiếp Blueprint, spawn Actor, quản lý Level Sequencer và ánh sáng trường quay ảo. |
| **ComfyUI** | **`artokun/comfyui-mcp`**<br>`shawnrushefsky/comfyui-mcp` | • **178 tools** biến ComfyUI thành một "công cụ headless": AI Agent tự động đấu dây các node, nạp checkpoint LoRA và render hàng loạt không cần mở trình duyệt. |
| **Figma** | **`figma/mcp-server-guide`** *(Official)*<br>`southleft/figma-console-mcp` | • Chuẩn mực hàng đầu mảng Design-to-Code: Agent đọc Design Tokens, biến thể component, cấu trúc layout và tự đồng bộ ra mã giao diện. |
| **Photoshop** | **`alisaitteke/photoshop-mcp`**<br>`dcc-mcp/dcc-mcp-core` | • **118 tools** quản lý layer, smart filters, xử lý ảnh hàng loạt (khắc phục các hạn chế giao thức COM trên bản Photoshop mới). |

---

## PHẦN 2: BẢNG AI MODELS & NỀN TẢNG THẾ HỆ MỚI (OCTOBER 2026)

| Danh mục | Model / Nền tảng | Bản cập nhật & Vai trò thực tế trong Studio |
| :--- | :--- | :--- |
| **Foundation Generative** | **FLUX 3 (Black Forest Labs)** | Ra mắt tháng 7/2026; mô hình nền tảng đa phương thức (multimodal) đồng nhất xử lý cả hình ảnh, chuyển động video và âm thanh cinematic ăn khớp tuyệt đối. |
| **Hero Cinematic Video** | **Runway Gen-4.5 ("David")** | Kế thừa dòng Gen-4; đứng đầu thị trường điện ảnh về mô phỏng trọng lực, vật lý cơ thể và chuyển động camera chân thực phục vụ Previs & Stylization. |
| **Video Production Thay thế** | **Kling AI & Google Veo** | Trở thành lựa chọn ưu tiên sau khi OpenAI khai tử Sora; chuyên trị các phân cảnh dài với độ nhất quán nhân vật cao. |
| **Local Video Rigs** | **Wan 3.0 / LTX-2.5** (qua `Wan2GP`) | Mô hình video nguồn mở tối ưu VRAM cực tốt, cho phép các studio indie chạy render video điện ảnh trực tiếp trên phần cứng máy trạm tiêu dùng. |
| **Masking & Roto** | **Meta SAM 3** | Tiêu chuẩn toàn ngành thay thế hàng trăm giờ cắt tỉa Roto thủ công; tracking mặt nạ điểm/vùng với độ mịn viền sub-pixel. |
| **4D Volumetrics** | **4D Gaussian Splatting (4DGS)** | Tiến hóa từ 3DGS; ghi lại cả không gian và thời gian chuyển động. Chuẩn hóa qua định dạng `KHR_gaussian_splatting` của Khronos Group. |
| **Markerless Mocap** | **Move AI & Autodesk Flow Studio** | Thay thế bộ đồ cảm biến; trích xuất dữ liệu cử động khung xương 3D độ chính xác cao từ video đa góc quay để đưa thẳng vào Maya rig. |
| **AI Inpainting Video** | **ProPainter & DAEVI** | Tẩy xóa dây cáp và vật thể chuyển động có nhận biết bản đồ chiều sâu (Depth-aware), không để lại vệt mờ biến dạng. |

---

## PHẦN 3: AI NATIVE BÊN TRONG CÁC PHẦN MỀM ĐẦU BẢNG (DCC RELEASES 2026)

*Các hãng lớn không bị AI đánh bại mà đã "nuốt trọn" AI vào lõi phần mềm:*

* **The Foundry Nuke 17:**
  * **SmartRoto (Tháng 7/2026):** Trợ lý Roto thông minh tự động truyền các đường cong spline xuyên suốt toàn bộ phân cảnh (tăng tốc độ gấp 4 lần).
  * **BigCat & CopyCat:** Cho phép studio huấn luyện các mô hình Machine Learning quy mô lớn trên dữ liệu độc quyền. Tích hợp sẵn bộ khung agent **Griptape**.
  * Hỗ trợ giải mã **Native Gaussian Splatting** trực tiếp trong không gian 3D của Nuke.
* **Autodesk Maya 2026:**
  * **MotionMaker:** Hệ sinh thái tạo chuyển động bằng AI cho phép studio huấn luyện mô hình dựa trên chính hệ thống Rig nội bộ (*Bring Your Own Data - BYOD*).
  * **ML Deformer:** Nén các hệ thống rig nhân vật phức tạp (hàng nghìn khớp xương/cơ bắp) nhẹ đi **80%** để animator diễn xuất mượt mà ở 60 FPS.
* **SideFX Houdini 22:**
  * **ONNX Native Inference:** Hỗ trợ chạy trực tiếp các mạng nơ-ron AI ngay bên trong mạng node procedural mà không cần gọi script ngoài.
  * Trở thành công cụ số 1 thế giới để tạo **Dữ liệu tổng hợp (Synthetic Data)** dùng huấn luyện AI cho xe tự hành và robot.
* **Epic Games Unreal Engine 6 (UE6):**
  * **Scene-Aware AI:** Tích hợp mô hình Diffusion nhận thức được toàn bộ Depth pass, Normal map và dữ liệu Camera thật để tạo ra các khung hình kết xuất khớp 100% với phối cảnh 3D.

---

## PHẦN 4: HỆ THỐNG AI AGENTS & WORKFLOW AUTOMATION TRONG PIPELINE

Các studio lớn hiện nay vận hành theo mô hình **Đội ngũ đặc vụ phối hợp (Multi-Agent Swarm)**:

```
[PLANNER AGENT]               [EXECUTOR AGENTS]               [CRITIC / QC AGENT]
Đọc kịch bản / Brief ───►  Agent 1 (ComfyUI via MCP)      ───►  Quét lỗi N-Gons, UV,
Phân tích Shotlist         Agent 2 (Tripo3D / Remesher)         Lỗi màu ACES 
                           Agent 3 (Maya Auto-Rig)             (Đạt ➔ Duyệt / Lỗi ➔ Trả về)
```

1. **AYON AI (Khung Noya):** Nền tảng pipeline mã nguồn mở hàng đầu (kế thừa OpenPype) ra mắt trợ lý **Noya** kết nối qua MCP. Nghệ sĩ chỉ cần gõ: *"Lấy toàn bộ camera của shot 010 nạp vào Nuke và chuẩn bị sẵn node Roto"*, Noya sẽ tự động mở file, nạp asset và xếp node sẵn sàng.
2. **LangGraph Creative Pipelines (HITL - Human-in-the-Loop):**
   * Sử dụng cấu trúc đồ thị có vòng lặp (Cycles): Agent sinh bản nháp ➔ Agent thẩm định đánh giá tiêu chuẩn ➔ Nếu chưa đạt thì tự động sửa lại ➔ Dừng lại ở các chốt chặn quan trọng để Đạo diễn con người bấm "Approve".
3. **Headless ComfyUI qua API (Runflow / ComfyDeploy):**
   * ComfyUI không còn là phần mềm mở trên máy cá nhân mà được đóng gói thành các container Docker chạy trên server đám mây. Kỹ sư gọi qua API JSON để tạo hàng loạt biến thể asset tự động.
4. **AI Render Farm Automation:**
   * Hệ thống quản lý farm tự động quét log tệp kết xuất, dùng AI dự đoán nguy cơ tràn bộ nhớ VRAM trước khi render bị crash, đồng thời tự động áp dụng AI Denoising/Upscaling giúp **cắt giảm 40% – 75% chi phí điện năng render**.

---

## PHẦN 5: BẢNG DANH MỤC GITHUB REPOSITORIES TIÊU BIỂU (OCTOBER 2026)

| Kho lưu trữ GitHub (Repo URL) | Chức năng cốt lõi | Giá trị đối với Dân Chuyên Nghiệp |
| :--- | :--- | :--- |
| **[`storytold/artcraft`](https://github.com/storytold/artcraft)** | Intentional crafting engine & Agentic workflow | Cầu nối biến các mô hình AI thô thành quy trình chỉ đạo nghệ thuật có kiểm soát từng bước cho đạo diễn. |
| **[`Comfy-Org/ComfyUI`](https://github.com/Comfy-Org/ComfyUI)** | Node-based visual AI orchestration | "Hệ điều hành" của nghệ thuật tạo sinh cục bộ; hỗ trợ relighting, texturing và AI upscaling đa tầng. |
| **[`black-forest-labs/flux`](https://github.com/black-forest-labs/flux)** | Mã nguồn suy luận của dòng mô hình FLUX | Tiêu chuẩn tạo asset cinematic đa phương thức, thay thế hoàn toàn các workflow Stable Diffusion cũ. |
| **[`deepbeepmeep/Wan2GP`](https://github.com/deepbeepmeep/Wan2GP)** | Trình thực thi tối ưu VRAM cho Wan 3.0 / LTX-2.5 | Cho phép các studio vừa và nhỏ chạy mô hình video điện ảnh tiên tiến trên phần máy trạm cá nhân. |
| **[`sebastianstarke/AI4Animation`](https://github.com/sebastianstarke/AI4Animation)** | Framework Python cho hoạt hình nhân vật | Cực kỳ quan trọng cho Technical Animator làm việc với Mocap tự động và procedural animation. |
| **[`PixarAnimationStudios/OpenUSD`](https://github.com/PixarAnimationStudios/OpenUSD)** | Thư viện lõi Universal Scene Description | Xương sống bắt buộc kết nối toàn bộ dữ liệu 3D xuyên suốt Maya, Houdini, Unreal và Nuke. |
| **[`NVIDIA-Omniverse/usd-optimize`](https://github.com/NVIDIA-Omniverse/usd-optimize)** | Tối ưu hóa các Stage USD dung lượng lớn | Công cụ của Technical Director giúp các đại cảnh phim hàng trăm gigabyte load mượt trên mạng nội bộ. |
| **[`harry7557558/spirula-studio`](https://github.com/harry7557558/spirula-studio)** | Huấn luyện 3DGS đa nền tảng qua Vulkan | Tái tạo bối cảnh 3D siêu thực từ ảnh chụp mà không cần môi trường lập trình Python/PyTorch phức tạp. |
| **[`penpot/penpot`](https://github.com/penpot/penpot)** | Nền tảng thiết kế UI/UX mã nguồn mở | Chuẩn mực tự lưu trữ (self-hosted) bảo mật dữ liệu thay thế Figma cho các dự án game/phim bảo mật cao. |
| **[`onlook-dev/onlook`](https://github.com/onlook-dev/onlook)** | Trình biên tập trực quan kết hợp mã nguồn AI | Cho phép AI Coding Agents tương tác trực tiếp giữa bản vẽ thiết kế và code giao diện thực tế. |
| **[`GraphiteEditor/Graphite`](https://github.com/GraphiteEditor/Graphite)** | Trình đồ họa vector 2D dạng Node phi phá hủy | Ứng dụng tư duy Node của VFX 3D vào thiết kế đồ họa vector 2D truyền thống. |
| **[`dramaclaw/dramaclaw`](https://github.com/dramaclaw/dramaclaw)** | Công cụ AIGC kịch bản-ra-phim tự động | Tự động hóa phân tích kịch bản văn học thành danh sách phân cảnh và video thử nghiệm. |
| **[`pbakaus/impeccable`](https://github.com/pbakaus/impeccable)** | Hàng rào kiểm định Design System cho AI | Đảm bảo các AI Agent khi sinh giao diện/đồ họa không vi phạm quy chuẩn font chữ và màu sắc của thương hiệu. |

---

### TỔNG KẾT BÀI HỌC TÁC CHIẾN (THE 2026 VERDICT)
Các cao thủ đồ họa và điện ảnh trong giai đoạn hiện nay:
1. **Không coi AI là công cụ "thay thế nghệ sĩ"**, mà biến AI thành các **Agent chuyên trách** kết nối qua cổng **MCP**.
2. Nghệ sĩ đóng vai trò là **Tổng đạo diễn (Orchestrator)** ngồi ở trung tâm: ra lệnh bằng ngôn ngữ tự nhiên, giao việc cho các Agent chạy ngầm trên máy chủ, và dùng năng lực mỹ thuật cốt lõi (Ánh sáng, Giải phẫu, Màu sắc ACES, Lưới Topology) để kiểm soát chất lượng đầu ra cuối cùng.