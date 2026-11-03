# Nhóm B — Chuyển động cơ thể trong Mine-imator 2.0.x (sổ tay nghiên cứu)

Ngày đọc: 2026-11-03. Nguồn: transcript YouTube của 18 video nhóm B, đọc **toàn bộ** từng transcript (đọc read-only qua tab Chrome riêng, không tải video, không gọi API trả phí).
Quy ước nhãn: **OBSERVED** = có trong transcript / file / lệnh; **INFERRED** = suy luận của mình (cần render thử); **OWNER** = chủ kênh nói.
Trích dẫn dạng `[videoId mm:ss]` = mốc thời gian của câu nói trong transcript (bộ đọc gộp mốc mỗi ~15 s, nên mốc có thể sớm hơn câu nói tới ~15 s).

Lưu ý chung (OBSERVED):
- Gần như không video nào đọc to **góc độ cụ thể** cho chân/tay trong walk cycle; họ chỉnh bằng mắt trong viewport. Các số thật sự được nói ra được gom ở mục 2.1 và đánh dấu nguồn. Mọi góc chân/tay khác trong sổ này là INFERRED.
- Không video nào nói rõ tempo (fps) của project. Người làm video gọi đơn vị thời gian là "frame" hoặc "tick". Template của mình dùng `"tempo":24` (OBSERVED trong `tools/mineimator/binbo_thu01/template.miproject`). Mọi chỗ đổi sang 20/24/30 fps là INFERRED: giữ nguyên thời lượng (giây), nhân số frame theo tỉ lệ.
- 3 kênh: **AnxiousCynic** (giải thích rõ menu Mine-imator 2), **SharpWind** (nguyên lý animation: overlap, weight, idle, turn; có nhân vật/rig riêng), **Ayrzens** (IK walk, rig bên thứ ba "Opaque V1").

---

## 1. Danh sách video

| # | id | Tiêu đề | Kênh | Độ dài | Lượt xem (2026-11-03) | Transcript |
|---|---|---|---|---|---|---|
| 1 | NU0fAvOgEv0 | How to Animate & Make A Walk Cycle - Part 3 - Mine-imator 2 Tutorial | AnxiousCynic | 19:01 | 41,996 | có (1016 đoạn) |
| 2 | BmWf6dR4kks | Mine Imator Walking & Running Tutorial EXPLAINED IN DEPTH! | SharpWind | 17:25 | 57,628 | có (438) |
| 3 | mxc0aDlg7tU | EMOTIONAL WALKING CYCLES ~ A Mine Imator Tutorial! | SharpWind | 8:53 | 39,044 | có (262) |
| 4 | WRgtbdkLYf8 | STOP Doing Animations WRONG! Walk & Run Cycle Tutorial︱Inverse Kinematics in Mine-imator 2.0 | Ayrzens | 3:24 | 41,266 | có (25, ngắn, nhiều nhạc) |
| 5 | eEtFSQGXi_I | How to Use IK (Inverse Kinematics) - Mine-imator Tutorial | AnxiousCynic | 8:14 | 35,483 | có (199) |
| 6 | NMRHDtSkehw | Inverse Kinematics, Constraints & Paths - Part 4 - Mine-imator 2 Tutorial | AnxiousCynic | 15:16 | 16,711 | có (406) |
| 7 | vXG6QEJN8p0 | How To Use PATHS - Mine-imator Tutorial | AnxiousCynic | 13:03 | 65,985 | có (332) |
| 8 | LaVMLYU6JEA | Weight Tutorial ~ Make Your Animations More Realistic! | SharpWind | 10:20 | 8,677 | có (289) |
| 9 | IyUfooxLmGE | OVERLAPPING ACTION?? Improove your skill! ~ Mine Imator | SharpWind | 14:25 | 26,223 | có (333) |
| 10 | VdJh-vTewJY | Idle Motion Tutorial! Breathing / Looking Around! [Mine - Imator] | SharpWind | 25:17 | 6,814 | có (588) |
| 11 | aMTNQBzSGA8 | IMPROVED Idle Motion Tutorial! ~ Mine Imator | SharpWind | 22:46 | 15,258 | có (624) |
| 12 | M-upI7h19kw | How to Animate a Realistic Turning Around Animation! In Place + Mid Walking! | SharpWind | 19:04 | 21,780 | có (454) |
| 13 | VRC_CwYqPVM | Running Stop ~ Mine Imator Tutorial! | SharpWind | 12:58 | 8,024 | có (356) |
| 14 | DO3d7Rh3e0E | Running Start! ~ A Mine Imator Tutorial! | SharpWind | 12:31 | 13,468 | có (401) |
| 15 | Vjcc_vau-u8 | How to Pick Up and Drop Objects - Mine-imator 2 Tutorial | AnxiousCynic | 10:24 | 8,471 | có (262) |
| 16 | BUweokJnBXo | How to Throw Items ~ A Mine Imator Tutorial! | SharpWind | 9:38 | 9,887 | có (259) |
| 17 | I1CGhhEcOc4 | GRAVITY ~ A Mine Imator Tutorial! | SharpWind | 16:47 | 6,133 | có (480) |
| 18 | Tjuvp57Ijg4 | How to Animate Animal Walk Cycles - Mine-imator Tutorial | AnxiousCynic | 3:07 | 3,287 | có (88) |

Cả 18 video đều có transcript tiếng Anh (phụ đề tự động). Con số trong ngoặc là số đoạn transcript sau khi bỏ trùng.
Một số video dùng rig/template của bên thứ ba (Opaque V1, Oblivion, template tải về). Mình **chỉ học kỹ thuật**, không dùng các asset đó (luật Original IP).

---

## 2. Kiến thức theo chủ đề

### 2.0 Cơ bản về keyframe và transition (nền tảng cho mọi chủ đề sau)
- **Tạo keyframe** có ba cách [NU0fAvOgEv0 0:30]:
  - double-click lên timeline;
  - chọn một part rồi di chuyển nó (keyframe tự sinh);
  - đặt con trỏ timeline rồi bấm **Ctrl+Q**.
- **Base keyframe:** kéo chọn hết các part rồi bấm Ctrl+Q để tạo keyframe gốc cho tất cả [NU0fAvOgEv0 1:04].
- **Bẫy hay gặp:** nếu một keyframe đang được highlight, mọi chỉnh sửa sẽ ghi đè vào keyframe đó thay vì tạo keyframe mới, bất kể con trỏ timeline đang ở đâu. Phải bỏ chọn trước khi chỉnh [NU0fAvOgEv0 2:22].
- **Tốc độ = khoảng cách giữa hai keyframe.** Ví dụ: cùng một cú quay chân 90°, đặt keyframe ở frame 20 thì chậm, kéo về frame 10 thì nhanh gấp đôi [NU0fAvOgEv0 2:52].
- **Chọn transition** ở Keyframe settings → **Transitions** (mặc định là **Linear**). Nếu bật "compact panels" trong Preferences thì danh sách bị tràn khỏi màn hình; cách khác là **right-click keyframe → Transition** [NU0fAvOgEv0 4:09–5:04].
- **Bounce transition:** đặt keyframe cách 60 frame thì thấy rõ hiệu ứng nảy; cách 30 frame thì cú rơi "thật" hơn [NU0fAvOgEv0 5:33–6:00].
- **Transition được kế thừa:** keyframe mới tạo nhận transition của keyframe trước đó, nên cần giữ transition gọn gàng [NU0fAvOgEv0 10:04–10:20].
- **Chọn nhiều keyframe:** Shift+click nhiều keyframe rồi đổi một giá trị thì tất cả cùng nhận giá trị đó [NU0fAvOgEv0 11:52].
- **Copy/paste:** Ctrl+C / Ctrl+V; bản paste nằm ở vị trí con trỏ timeline [NU0fAvOgEv0 10:51].
- **Loop để xem:** right-click và kéo trên timeline để tạo vùng chọn, bật **Enable looping**. Bấm lần nữa thì thành **seamless looping**. Right-click lên timeline để bỏ vùng chọn [NU0fAvOgEv0 9:00–9:48].
- **Transition xuất hiện trong transcript:**
  - Linear; Instant [NMRHDtSkehw 8:56];
  - "bouncy"/Bounce [NU0fAvOgEv0 5:11];
  - "ease in and ease out" [NU0fAvOgEv0 13:24];
  - "quadratic" [WRgtbdkLYf8 0:40];
  - "ease in/out cubic", để có "transition mạnh hơn": cùng thời lượng nhưng có lực hơn [BmWf6dR4kks 12:10] [VdJh-vTewJY 11:40];
  - "ease out sine"/"sine", nhẹ và thư giãn hơn [BmWf6dR4kks 14:31] [aMTNQBzSGA8 6:18].
- **Tên dùng trong JSON (INFERRED theo cách đặt tên mình đã dùng thành công):**
  - `linear`, `instant`;
  - `easeinquad` / `easeoutquad` / `easeinoutquad`;
  - `easeinoutcubic`;
  - `easeinsine` / `easeoutsine` / `easeinoutsine`;
  - `easeoutback`;
  - `easeoutbounce`: tên này chưa kiểm, cần đối chiếu enum trong source Mine-imator.
- **Giới hạn công cụ:** Mine-imator không có custom curve, chỉ có các preset ease. SharpWind than là không có cách "ease nhẹ mà không dừng hẳn" [I1CGhhEcOc4 12:16, 14:22].

### 2.1 Walk cycle (đi bộ)

**A. Walk cycle tự động** [NU0fAvOgEv0 6:10–7:26]:
1. Trên **root object** của nhân vật, đặt keyframe đầu và keyframe cuối (ví dụ frame 45).
2. Chọn **keyframe đầu**, right-click → **Create walk cycle** (hoặc **Create run cycle**).
3. Nếu đã có base keyframe thì walk cycle sẽ sinh keyframe trùng; xoá chúng đi [6:55].
4. Kết quả trông "kiểu Minecraft cổ điển", không được đẹp lắm [7:10]. Walk cycle tự động **không có keyframe cho đầu** [7:42].
5. AnxiousCynic chuyển tất cả keyframe sang **Linear** để có "blank slate" [7:26].
6. Mob bốn chân cũng có walk cycle tự động [Tjuvp57Ijg4 0:00]. Walk cycle cũng chạy được trên path [vXG6QEJN8p0 8:08].

**B. Nâng cấp từ key pose** (AnxiousCynic) [NU0fAvOgEv0 7:57–17:41]:
- **Key pose:** đứng yên → chân phải trước → chân trái trước → đứng yên [7:57].
- **Passing pose:** ở giữa hai key pose, **gập gối** chân đang đưa lên trước [8:12–8:59].
- **Lặp mượt:** copy/paste rồi đặt vùng loop từ pose "chân phải trước" tới pose "chân phải trước" kế tiếp [11:06–11:21].
- **Thân:** tại các pose chân dang rộng nhất, thân xoay (twist) **+5°** và **−5°** luân phiên [11:36–12:07].
- **Đầu:** "dip" khoảng **4°** rồi **−4°**, thêm một chút quay đầu [12:39–12:54].
- **Transition:** chân giữ **Linear** (thêm transition có thể làm hỏng walk cycle); tay đổi sang **ease in & out** để có quán tính [13:09–13:24].
- **Bob (nhún):** ở pose chân dang rộng (contact) hạ người **−1**; ở pose chân thẳng đứng (passing) để **0**, nếu không chân sẽ lún vào đất [16:35–17:07].
- **Tách cycle và quãng di chuyển:** right-click nhân vật → **Add folder**. Cycle animate trên nhân vật, quãng đường di chuyển animate trên folder [15:27–16:16]. Nhân vật phải ở vị trí 0 trùng với folder.
- **Chống trượt chân:** chỉnh khoảng cách hoặc timing keyframe của folder [17:26–18:11].

**C. Walk "chống trượt chân" kiểu SharpWind** [BmWf6dR4kks 1:01–9:42]:
- Mỗi bước dùng **2 keyframe** [1:34]. Pose mới cứ **mỗi 3 frame** [3:37, 5:45, 6:19].
- **Quy tắc vàng:** sau mỗi keyframe, dời **cả nhân vật** tới/lên/xuống sao cho điểm chạm đất của bàn chân trụ nằm **đúng chỗ cũ**. Bấm qua lại giữa các keyframe để kiểm [2:35–3:06].
- Nếu keyframe chân dùng ease mà nhân vật di chuyển linear thì chân sẽ trượt. Phải cho cả hai cùng linear, hoặc cùng ease in/out [3:22].
- **Thứ tự pose (mỗi pose cách 3 frame):**
  1. chân sau duỗi, chân trước gập chuẩn bị đặt xuống [2:05];
  2. chân sau lùi thêm, chân trước chạm đất; hạ nhân vật để chân trụ chạm đất, hai chân ngang nhau [3:37–4:09];
  3. gập chân trụ cho đế bàn chân nằm phẳng trên đất [4:26–4:58];
  4. chân sau lùi thêm và hơi gập, bàn chân "bóc" khỏi đất. Pose này chính là pose 1 lật ngược = nửa chu kỳ [5:45–6:00].
- **Nửa chu kỳ còn lại:** copy, tiến 3 frame, paste, rồi đặt lại nhân vật **thủ công** ở từng frame ("không có cách tự động") [6:19–6:34].
- **Đổi hướng đi:** cho nhân vật vào folder rồi xoay folder [6:49–7:05].
- **Thân** xoay về phía chân đang "bóc" khỏi đất, dùng ease in/out, frame sau xoay ngược lại [7:22–7:54].
- **Đầu** luôn nhìn thẳng (xoay bù lại thân) và cũng phải có ease in/out, nếu không sẽ trễ so với thân. Thân của SharpWind xoay **14°**. Nếu biên độ nhỏ hơn thì để đầu linear "đuổi theo" thân trông tự nhiên [8:09–8:55].
- **Tay** lệch (overlap) chứ không thẳng hàng với thân, dùng ease in/out [8:55–9:25].

**D. Walk bằng IK** (Ayrzens, rig Opaque V1 của bên thứ ba) [WRgtbdkLYf8 0:15–2:03]:
- **Pose bước:** IK chân trước tiến **+5**, chân sau lùi **−5** (số âm bị nhận dạng méo thành "negative state"; −5 là INFERRED). Gập thân, đặt tay, transition **quadratic** [0:15–0:40].
- **Đầu:** **tắt "Inherit rotation"** để đầu không xoay theo thân [0:47].
- **Di chuyển:** chọn root ("body", đánh dấu "move"), tới khoảng **frame 10**, đẩy về trước, rồi đưa chân sau lên trước [0:55–1:10].
- **Nhún:** frame giữa nhấc chân bước lên để không kéo lê; frame thứ hai hạ thân khoảng **−0.5**; frame giữa nâng thân **cao hơn** độ cao lúc đầu [1:18–1:37].
- **Đối xứng:** đảo dấu góc bend của thân; copy rotation tay trái, **đảo dấu Y và Z**, dán sang tay phải [1:37–1:52]. Đầu nhún xuống rất nhẹ [1:52].

**Bảng key pose walk — chỉ các số video nói ra (OBSERVED):**

| Pose | Part | Giá trị | Nguồn |
|---|---|---|---|
| Contact phải (chân dang rộng) | thân twist | +5° | [NU0fAvOgEv0 11:52] |
| Contact trái | thân twist | −5° | [NU0fAvOgEv0 12:07] |
| Contact phải / trái | đầu dip | +4° / −4° | [NU0fAvOgEv0 12:39] |
| Contact (cả hai bên) | vị trí Z thân/nhân vật | −1 | [NU0fAvOgEv0 16:51] |
| Passing | vị trí Z | 0 | [NU0fAvOgEv0 17:07] |
| Mỗi pose | khoảng cách | 3 frame | [BmWf6dR4kks 3:37] |
| (SharpWind) | thân xoay tối đa | 14° | [BmWf6dR4kks 8:40] |
| IK contact | chân trước/sau | +5 / −5 (đơn vị vị trí) | [WRgtbdkLYf8 0:23] |
| IK contact | thân | −0.5 | [WRgtbdkLYf8 1:18] |

**Walk cảm xúc** [mxc0aDlg7tU 1:37–7:53]. Không có số cụ thể; chỉ có so sánh tương đối:

| Cảm xúc | Nhịp | Sải bước | Thân | Đầu | Tay | Transition |
|---|---|---|---|---|---|---|
| Casual | khá chậm | thường | lắc trái-phải | nhìn thẳng, ngó quanh tò mò | đánh trước-sau | thường |
| Sad | chậm hơn nhiều | nhỏ | cúi trước, nhún lên-xuống mỗi bước | cúi; khi ngó cũng chỉ ngẩng chút | gần như không gập, thả lỏng | — |
| Happy | như casual | **lớn** | ưỡn, "tự hào" | gần như ngước | đánh mạnh, gập nhiều | "intense" (mạnh hơn, không nhanh hơn) |
| Nervous | **nhanh** | lớn | cúi trước | hơi cúi, ngó quanh gấp | đánh mạnh, **hướng vào trong** | intense; chậm lại một chút ở key chân đi xa nhất |
| Angry | như nervous | lớn | cúi | **không ngó quanh** (nhìn chằm mục tiêu) | như nervous | intense |
| Tired | chậm nhất | nhỏ | cúi + nhún | overlap nhiều (lê thân), vẫn ngẩng nhìn | chậm, gần như không gập | — |
| Shy/Scared | nhanh | nhỏ | thu vào trong, ngả ra sau | cúi | gập lên và vào trong | nhanh khi ngó |

### 2.2 Run cycle, chạy xuất phát, dừng chạy
- **Run** (SharpWind, học từ YouTuber "Kazuko Gaea") [BmWf6dR4kks 10:48–16:35]:
  - Nghiêng cả nhân vật **45° về trước** [10:48].
  - **Pose xuất phát:** một chân duỗi hết (X); chân kia đưa lên trước, gập tối đa; thân hơi ngửa lên để "nhìn đường"; đầu nhìn thẳng. Tay quay Y/Z/X và gập; tay kia làm ngược ra sau [11:05–11:51].
  - **Nhịp:** keyframe **mỗi 2 frame** cho chạy nhanh [12:26]. Thử **ease in/out cubic** [12:10].
  - **Chu kỳ:** chân chính lùi và gập, chân kia hạ xuống và duỗi → frame sau chạm đất gập → đổi chân → copy/paste [12:41–13:11].
  - Thân xoay bù theo từng sải (ease in/out); đầu cũng vậy [13:28–14:00].
  - **Tay chỉ trễ 1 tick, không phải 2.** Thử **ease out sine** cho hiệu ứng nhẹ. Khi chạy, overlap làm tay "vẫy loạn" nên **không dùng overlap cho tay khi chạy** [14:15–15:01].
  - Chạy không cần chính xác như đi bộ [15:32].
  - **Nhún bằng folder:** đặt keyframe ở những lúc chân chạm đất; khi bay nâng folder lên **+1 đến 1.5**. Folder dùng transition thoải mái mà không phá cycle [15:47–16:35].
- **Run IK** (Ayrzens): giống đi bộ nhưng phóng đại hơn: thân đổ về trước, **bend angle 40** [WRgtbdkLYf8 2:12–2:31]. Đẩy thân tới trước cho tới khi chân sau bay lên [2:40].
- **Running Start** [DO3d7Rh3e0E]:
  - **Thiết lập:** dời Steve **−12** xuống trong folder và dời folder **+12** lên. Kết quả: pivot của folder ở giữa thân, pivot của Steve ở bàn chân, cần cả hai [1:03–1:33]. SharpWind nói custom rotation point "bị lỗi" ở bản của anh (OBSERVED lời anh nói, chưa kiểm ở 2.0.2).
  - **Kiểu 1, bứt tốc:** chuẩn bị bằng cách hạ người, khép gối, nghiêng trước. Khi bắt đầu chạy, xoay lên 45° rồi đưa trở lại −12. Folder tiến tới với **một keyframe ease in dài**. Chân trụ duỗi để vẫn bám đất [1:49–2:21]. Thân nghiêng **ngược hướng** trước (anticipation) rồi mới lao [2:37–2:52]. Đầu nhìn hướng chạy [3:08].
  - **Kiểu 2, tăng dần từ walk:**
    - Thân nghiêng dần về trước, đầu hơi ngẩng, tay đánh mạnh dần [4:43].
    - Dồn các keyframe chân lại gần nhau (bỏ qua một bước, lặp lại); chân sau lùi xa hơn, gập nhiều hơn. Đi bộ dần thành "nhảy cóc" rồi thành chạy [4:43–6:17].
    - Không học thuộc số thập phân; làm theo cảm giác. Người đứng thẳng thì không thể nhảy cóc nhiều [6:17–6:32].
  - **Cung nhảy:** tiến linear ở một timeline; lên/xuống ở timeline khác, **ease out → ease in xen kẽ**. Năng lượng đẩy lên thì chậm dần, rơi xuống thì nhanh dần [6:32–7:50].
  - **Góc thân:** xoay dần tới 45°: lần nhảy này nghiêng một chút, lần sau nghiêng đủ 45° [8:20–8:36]. Folder nghiêng 18° thì bỏ bớt rotation của Steve để tránh hiệu ứng "bậc thang"; thay đổi quá lớn thì dùng linear [10:11–10:27].
  - **Hoàn thiện:** đừng cho bay lâu; đầu nhìn hướng chạy, không nghiêng [10:43]. Tay đánh rộng hơn khi nghiêng nhiều hơn và chạy nhanh hơn; không cần in-between cho tay [10:58–11:31].
- **Running Stop** [VRC_CwYqPVM]:
  - **Kiểm tra trượt chân:** phát lại chậm [1:18]. Run nhún **0.5** (không lún) và **1.2** khi bay [1:48].
  - **Hiểu cơ chế:** quán tính → phải dừng dần qua **2–3 bước** [2:52].
  - **Bước giảm tốc:** chân trước duỗi nhiều hơn và hơi nâng; chân sau "ít chuẩn bị" để giữ thăng bằng [3:09–3:25]. Bước chạy vốn **mỗi 2 keyframe**; khi giảm tốc giãn thành **mỗi 3** [3:41].
  - **Dừng:** đổ người lên **chân trước đang gập**, thân nằm trên chân trước [5:44–6:16]. Về pose gốc, thả lỏng [7:03].
  - **Chân in-between:** gập để không xuyên đất; ease in ở keyframe đầu, ease out ở keyframe sau, tổng lại thành "một ease in/out lớn" [7:19–7:34].
  - **Đứng thẳng dậy:** **nhô người tới trước rồi mới lên** (hãy tự diễn thử) [7:50–8:21].
  - **Thân:** đổ mạnh về trước khi dừng, ease out; các keyframe thân **trễ hơn** (overlap) [8:37–9:24]. **Đầu** vẫn nhìn trước, chỉnh sau với overlap [9:24–9:55].
  - **Tay** (sau khi tự diễn): tay **vẫn đánh như đang chạy**, xoay để luôn hướng trước. Keyframe giữa: ease in tới giữa, ease out tới cuối [10:29–11:32].
  - **Nếu dừng quá gắt:** giãn khoảng cách keyframe trước khi dừng (chạy chậm lại trước) hoặc thêm 2 bước đệm [11:32–11:47].

### 2.3 IK (Inverse Kinematics)
1. Click một limb → tab **Constraints**: có **Follow path** và **Inverse kinematics** [eEtFSQGXi_I 0:33].
2. Tạo **Target**: một object bất kỳ, thường là **Sphere** [eEtFSQGXi_I 0:49–1:04].
   - **Parent target vào root nhân vật**, *không* parent vào limb [1:19, 2:07].
   - Đặt custom rotation **0** [1:35].
   - Scale link khoảng **0.15** [1:50].
   - Đổi blend color sang đỏ cho dễ thấy [2:24].
   - Đặt tên, ví dụ "IK Tar left arm" [2:39].
3. Limb → Inverse kinematics → **Target**. Lúc này limb tự xoay lung tung [2:56–3:11].
4. **Angle target:** duplicate target, đặt tên "IK Ang Tar…", để **phía sau khuỷu** (hoặc trước gối), scale **0.075**. Gán vào ô **Angle target**: khuỷu/gối sẽ quay về phía nó [3:26–4:13] [NMRHDtSkehw 12:37–13:27].
5. **Tác dụng:** dời thân thì tay/chân vẫn bám target. Ngoài tầm với thì limb duỗi thẳng [eEtFSQGXi_I 4:28–4:44].
   - IK cho chân: dời thân lên xuống mà chân vẫn chạm đất (nhún, nhảy múa) [5:01].
   - IK cho cả hai tay: nhân vật treo/bám [NMRHDtSkehw 14:00].
   - Đặt target chân khoảng **2** để thẳng hàng tư thế mặc định [NMRHDtSkehw 12:21].
6. **Ẩn target khi render:** Appearance → **HQ hiding** (vẫn thấy trong viewport, mất trong render). **LQ hiding** thì ẩn trong viewport. Bật cho target đầu tiên trước khi duplicate [eEtFSQGXi_I 5:48–6:19] [NMRHDtSkehw 14:17–14:48].
7. **Giới hạn:** chỉ model dạng người có IK (human, zombie, skeleton; creeper có ở chân). Sphere, squid, spider chỉ có Follow path [eEtFSQGXi_I 6:36–7:43].
8. **FK vs IK:** FK thì không có gì neo; IK neo được [NMRHDtSkehw 10:23–10:48].

### 2.4 Constraints, parenting và path
- **Parent item vào tay** [NMRHDtSkehw 0:16–1:34]:
  1. Thêm Item (sword), zero vị trí.
  2. Ô **Parent** → Steve → body → right arm.
  3. Bật **Custom rotation point**, khoảng **3.5 / 3.5** ở chuôi kiếm, xoay **−90**.
  4. Từ giờ item đi theo tay.
- **Path** [vXG6QEJN8p0 0:15–2:21] [NMRHDtSkehw 1:45–3:26]:
  - Tạo path, bấm **Add point** trước. Tạo điểm tiếp bằng **Ctrl+D** (hoặc right-click → Duplicate) rồi kéo; đường cong tự nội suy. Chọn được nhiều điểm cùng lúc; nâng điểm lên để có độ cao.
  - **Connect ends** = vòng kín. **Detail** cao = mượt hơn. **Smooth path** tắt đi để căn điểm theo đường ray [vXG6QEJN8p0 10:29]. Detail **16** chạy tốt hơn cho minecart [12:08].
  - **Generate shape / Tube shape / Export map**: biến path thành hình khối (ít liên quan tới nhóm B).
- **Đi theo path** [NMRHDtSkehw 3:43–6:03] [vXG6QEJN8p0 6:03–8:39]:
  1. Chọn **root** → Constraints → **Follow path** → chọn path (nên đặt tên path).
  2. Reset vị trí nhân vật về 0 ở **cả hai** keyframe để nằm đúng trên path [vXG6QEJN8p0 7:38–7:53].
  3. Keyframe thứ hai kéo **Offset** (vòng kín: **360** = một vòng). Muốn đi chậm hơn thì giảm Offset, ví dụ **180** [vXG6QEJN8p0 7:23–8:24]. Hoặc kéo keyframe cuối lại gần = nhanh hơn, để khớp tốc độ của run cycle [NMRHDtSkehw 5:16–5:32].
  4. Coi chừng con trỏ timeline vô tình tạo keyframe [NMRHDtSkehw 4:15].
  5. Ở khúc cua nhân vật **nghiêng theo path**. Thêm keyframe nghiêng bù; nhớ chỉnh timing trước, hoặc đặt nhân vật trong folder [NMRHDtSkehw 6:50–7:36].
- **Rời path liền mạch** [NMRHDtSkehw 8:08–10:18]:
  1. Tại keyframe rời path, đặt path = **None**. Nhân vật nhảy về giá trị position của chính nó.
  2. Đặt keyframe đó là **Instant** (tránh nội suy "điên").
  3. Copy toạ độ điểm cuối của path (ví dụ **50.9**) bằng Ctrl+C / Ctrl+V vào X/Y của nhân vật.
- **Folder và Inherit:**
  - Xoay folder khi nhân vật ở xa pivot của folder thì nhân vật **quay quanh** thay vì xoay tại chỗ. Sửa: chọn nhân vật → **Inherit options → bỏ tick Position** (giữ Rotation) [M-upI7h19kw 6:21–7:07] [VdJh-vTewJY 5:48–6:18].
  - Head **Inherit rotation** tắt để đầu không xoay theo thân [WRgtbdkLYf8 0:47].
- **Import asset:** nút "Import an asset" nạp rig hoặc file keyframe đã lưu thành bản sao nội bộ [M-upI7h19kw 0:36–1:53] [Tjuvp57Ijg4 2:05].

### 2.5 Trọng lượng (weight)
- **Vật nặng không tăng tốc tức thì**, cần thời gian dồn năng lượng. Cửa cỡ người mở "bật" ngay thì trông như không có trọng lượng [LaVMLYU6JEA 0:48–1:35].
- Cửa to gấp 10 thì mở lâu hơn nhiều, dù tính theo đơn vị thế giới thì nó vẫn di chuyển nhanh [1:51–2:24].
- **Rơi:** trọng lực như nhau (9.81 m/s²). Vật to *trông* rơi chậm vì so với kích thước của nó. Rơi nhanh = vật nhỏ ("hòn bi") [2:58–4:48].
- **Bóng bãi biển:** có sức cản không khí → bay chậm, nhẹ. Còn vật nặng mà bị làm "slow motion" thì đơn giản là animation dở, đừng nhầm [5:20–5:51].
- **Ném khối đá:** dáng hai tay đỡ (nặng) mà ném nhanh (nhẹ) thì mâu thuẫn. Làm chậm toàn bộ, đẩy điểm cuối lại gần, nâng thấp hơn → thấy nặng [6:06–7:42].
- **Trọng lượng gắn với tempo và gia tốc** [7:42]. Búa nhựa nhấc tỉnh bơ. Búa nặng: nhấc chậm, tay kia đỡ, xoay bằng thân/vai, gối gập [7:57–9:00].
- **Thăng bằng khi tạo dáng** [I1CGhhEcOc4 3:26–5:33]:
  - Dáng "thả lỏng" mà đổ về trước là sẽ ngã.
  - Bàn chân phải tiếp đất chắc; một chân gập, một chân duỗi để đỡ trọng lượng.
  - **Trọng tâm phải nằm trên vùng tiếp xúc của bàn chân**; kiểm cả nhìn trước lẫn nhìn ngang.

### 2.6 Overlapping action, follow-through, xếp lớp chuyển động
- **Định nghĩa:** nhiều chuyển động cùng áp lên một vật cùng lúc mà không phá nhau [IyUfooxLmGE 0:31].
- **Arc:** bóng chạy theo X (linear); đặt bóng trong folder, nâng folder lên ở giữa (ease) → cung đẹp. Nếu cả X và Y cùng ease trên một timeline thì thành tam giác, xấu [IyUfooxLmGE 0:46–2:05]. Gravity tutorial nhắc lại y hệt: keyframe 1 ease out, keyframe 2 ease in **trên cùng timeline** thì vật "đứng giữa không trung như kẹt trong thạch" [I1CGhhEcOc4 0:36–1:06]. Cách đúng là folder **"gravity"** chỉ lên/xuống (ease out lên, ease in xuống), còn chiều ngang và rotation để linear [I1CGhhEcOc4 1:22–2:55].
- **Camera mượt:** 3 folder lồng nhau (Z, X, Y) cộng camera (rotation) = 4 lớp, mỗi lớp ease riêng [IyUfooxLmGE 2:37–5:52].
- **Nhân vật** [IyUfooxLmGE 6:53–7:40]:
  - **Thân đi trước**, đầu trễ hơn, **tay trễ nhất** (tay dài).
  - Hai tay cũng lệch nhau.
  - Thân bắt đầu động tác tiếp theo khi các phần khác còn đang chuyển động.
- **Tách một tay làm hai lớp** [IyUfooxLmGE 10:02–12:32]:
  1. Dùng **Add body part** (right arm), khoá vào **nửa trên** của tay thật; nếu lệch thì position = 0.
  2. Tay gốc: **Color → Alpha = 0**. Đừng dùng invisible, vì sẽ ẩn cả hai.
  3. Trục Y ở lớp trên (frame 0→20), trục Z ở lớp dưới (10→30), mỗi lớp ease in/out riêng.
  4. Nhưng thường **một folder là đủ** [12:49–13:20].

### 2.7 Idle / thở / ngó quanh
- **Luật:** nhân vật 3D **không bao giờ đứng im hoàn toàn** [VdJh-vTewJY 0:21–0:51].
- **Công thức idle (bản cải tiến)** [aMTNQBzSGA8]:
  1. **Thân:** mỗi **~20 tick** một keyframe; lệch trái chút, xoay phần trên, gập nhẹ; keyframe sau ngược lại. Thay đổi **rất nhỏ**. Biên độ lớn quá thì trông "say rượu" [1:36–1:51, 4:14, 7:04].
  2. Chọn **tất cả part** → **ease in and out** (thư giãn = bắt đầu chậm, dừng chậm) [2:06]. Transition quá gắt thì đổi sang **sine** [6:18].
  3. **Đầu trễ ~10 frame** so với thân. Thân hạ thì đầu cũng hơi hạ [2:22]. Luôn chỉnh **cả 3 trục** của đầu [2:56]. Keyframe đầu mà sát keyframe thân quá thì mất overlap [5:31].
  4. **Tay** cũng overlap (trước hay sau đầu đều được, miễn đừng trùng); hai tay lệch nhau [6:33–6:49]. Khi xoay người tay hơi nâng; xoay về thì tay rơi xuống, bớt gập [7:20–7:37]. Thư giãn thì **đừng quặp tay vào trong** (quặp vào là dáng lo lắng), hơi mở ra ngoài [8:08].
  5. **Chân:** cảnh không thấy chân thì để yên được. Cảnh rộng thì gập nhẹ, chỉnh lại thân để bàn chân không dời chỗ [8:40–9:11]. Trước khi quay về phía nào thì **dồn trọng lượng lên chân phía đó** [9:27–9:43].
  6. **Bước nhỏ:** khoảng **10 frame chân đứng yên** là ổn (thân trên vẫn chuyển động). Chân bước xoay ra ngoài chút; xoay/dời nhân vật để chân trụ giữ chỗ [9:58–11:04]. Animate **folder** như "nhân vật tổng thể"; pivot của nhân vật ở bàn chân nên xoay vẫn giữ tiếp xúc đất [12:07–12:38]. Trước khi bước, **ngả về chân trụ 0.4** [12:54–13:10].
  7. **Camera idle:** camera nằm trong folder "camera" ở 0,0,0. Keyframe camera mỗi vài frame (rung tay nhẹ, ease in/out). Folder dùng **một keyframe linear dài**. Thêm chút nghiêng, cuối về 0 [20:30–21:46].
  8. **Mặt** (thuộc nhóm khác, ghi chú nhanh): chớp mắt **trước khi quay**; sau chớp mắt mở to hơn rồi dịu lại; con ngươi nhỏ lại, nhìn đồ vật, bám theo vật [14:59–19:43].
- **Ngó / quay đầu:**
  - **Đầu (mắt) đi trước, thân theo sau**, như khi ai gọi tên mình [aMTNQBzSGA8 3:13–3:29] [VdJh-vTewJY 22:34–23:08]. Bản cũ để đầu trễ sau thân khoảng "vài frame" [VdJh-vTewJY 2:39] và sau đó tự nhận là sai.
  - **Settle:** quay sang một bên rồi keyframe tiếp theo **lùi lại chút** (không quay thêm), sau đó chỉnh nhỏ [aMTNQBzSGA8 6:02] [VdJh-vTewJY 8:29–9:17].
  - **ease in/out cubic:** cùng thời lượng nhưng "có lực", đỡ "nhão" [VdJh-vTewJY 11:40–11:57]. Tay gập nhanh, duỗi chậm [13:15–13:30]. Keyframe tay đừng trùng keyframe thân [14:02].
  - **Tư thế nghỉ** không phải toàn số 0: tay xoay Y/Z hơi ra ngoài, X hơi ra sau, gập nhẹ; transition dài cho tay thả lỏng [VdJh-vTewJY 15:58–16:14].
- **"Idle in a nutshell"** [VdJh-vTewJY 23:40–24:12]: thân hạ → keyframe sau lên kèm xoay nhẹ → hạ kèm xoay ngược, chuyển động quanh một điểm. Đầu và tay overlap (trễ).

### 2.8 Quay người (turning) và bắt đầu / dừng bước
- **Vừa đi vừa rẽ** [M-upI7h19kw 2:08–5:30]:
  - Folder chính lo chuyển động thẳng. Chân trượt về trước = dời quá nhiều; chân trượt ra sau = dời chưa đủ [2:23–2:54].
  - Quay **ROT linear** từ frame **30** tới cuối, khoảng **40° sang phải** [3:10]. Lớp thứ hai lo dời ngang [3:40].
  - **Dời ngang phải là ease in** (vì lúc mới bắt đầu quay người vẫn còn đi thẳng) [4:27–4:58]. Nếu chưa đẹp thì sửa điểm cuối, đừng tăng độ mạnh transition [5:14].
  - Muốn đi hướng khác thì xoay cả folder (tái dùng walk) [5:48–6:21]. Khi xoay folder thì **bỏ inherit position** [6:51–7:07].
- **Quay tại chỗ** [M-upI7h19kw 7:22–17:54]:
  - Khoảng **20–22 tick** cho **90°**; nghiêng người sang bên và dời vào trong; ease in/out cả hai [7:22–7:54].
  - **Bàn chân trụ giữ nguyên chỗ trên đất:** thân xoay 45° thì bàn chân xoay **−45°** tương đối, để vẫn hướng như cũ. Chỉnh độ nghiêng, rồi dời thân cho bàn chân trùng chỗ [8:10–8:58].
  - **Chân trụ phải có cùng transition và cùng thời điểm keyframe với thân**, nếu không sẽ trượt [9:16, 9:46–10:01]. Chân tự do thì lệch keyframe (overlap) [9:31].
  - Chân nhấc: keyframe 1 ease in, keyframe 2 ease out [13:57]. Cuối cùng hai chân hướng trước [12:24–12:40]. Đừng xoay quá tay [17:54].
  - Mẹo thật: **giấu chân bằng khung hình** khi khó; SharpWind "làm suốt" [12:09].
  - Thêm một folder để sửa độ nhún Y (ease out ở điểm giữa rồi ease in/out) [15:47–16:50].
- **Bước nhỏ khi idle** [VdJh-vTewJY 3:12–6:35]:
  - Tưởng tượng bước chân trong lúc phát timeline để chọn độ dài [3:27].
  - Ở keyframe giữa, chân trụ giữ nguyên chỗ; chân bước **nhấc lên** (đừng kéo lê) và xoay ngang chút [4:31–5:18].
  - Ease in rồi ease out [5:33]. Giữa bước thân ngả lên chân trụ [6:18].
- **Tiếp đất sau bước:** hạ thấp chút, gập chân [VdJh-vTewJY 19:57–20:12]. Dừng gắt quá thì "settle": hạ thân, gập gối, ease out; thà chân lún nhẹ vào sàn còn hơn trượt [VdJh-vTewJY 16:48–17:20].

### 2.9 Nhặt / cầm / ném đồ
- **Cách 1, nhân đôi item** (cả hai kênh khuyên dùng):
  1. Hai bản item: một bản **parent vào tay**, một bản **tự do** trong thế giới.
  2. Bật/tắt **Visibility** bằng keyframe **trên cùng một frame** [Vjcc_vau-u8 0:49–1:52] [BUweokJnBXo 7:22–8:08].
  3. Tại frame đổi, bản trong tay phải trùng tư thế bản trên đất. Gần đúng là được vì diễn ra rất nhanh [Vjcc_vau-u8 2:08–2:40]. SharpWind: thêm instance bằng icon "add another instance", rotation point **8,8,8** (tâm), copy scale, đồng bộ position/rotation/scale [BUweokJnBXo 7:22–7:52].
  4. **Ném:** frame rời tay thì bản tay ẩn, bản tự do hiện [Vjcc_vau-u8 3:28] [BUweokJnBXo 8:08].
  5. Bản tự do cho vào folder **"gravity"**: lên **ease out**, xuống **ease in** [BUweokJnBXo 8:24–8:55].
  6. Bản trong tay có thể animate tương đối với tay (tung lên, xoay, bắt lại) [Vjcc_vau-u8 3:13].
- **Cách 2, "hack" bằng path** [Vjcc_vau-u8 3:44–9:51]:
  1. Tạo path, **parent vào tay trái**, căn ở bàn tay; path cần **2 điểm** thì constraint mới chạy.
  2. Item position 0 → Constraints → path.
  3. Thả: path = None, khớp toạ độ bằng thử-sai; keyframe trước đó phải **Instant** (nếu linear thì item trôi).
  4. Nhược điểm: không có bản tham chiếu để căn.
- **Diễn xuất khi ném** [BUweokJnBXo 0:46–7:06]:
  1. Dồn trọng lượng lên chân phải (ngả ra sau chút) để nhấc chân trái; chân trụ giữ chỗ; bắt đầu ease in.
  2. Nhảy: chân đạp duỗi; giữa nhảy hạ người và gập; ease out → ease in.
  3. Tiếp đất: chân bám sàn, gập, **hạ thấp để triệt chuyển động dọc**.
  4. **Thân:** anticipation, tức là đi ngược hướng trước rồi mới vặn ra sau, sau đó vặn ngược lại khi ném [3:54–4:26]. Đầu nhìn mục tiêu suốt [4:42].
  5. **Tay ném:** vặn ra sau **trễ vài frame** so với thân, xoắn vào trong, cũng có anticipation [4:57–5:28]. Tay kia chỉ để lấy đà: vung lên [6:02–6:17].
  6. Sửa dáng: thân đổ về trước; bước cuối dài hơn, chân duỗi hơn = cú ném mạnh hơn [6:35–7:06].
- **Trọng lượng của vật** quyết định tempo của cú ném [LaVMLYU6JEA 6:06–7:42].

### 2.10 Trọng lực và vật rơi / nảy [I1CGhhEcOc4]
1. Block cho rotation point **8,8,8**; folder chính nâng **+8** để pivot ở giữa [5:49–6:22].
2. Tưởng tượng thời gian rơi. Ví dụ chạm đất ở **frame 10** [6:37–6:53].
3. Làm ngang và xoay trước (linear), sau đó mới hạ folder gravity xuống điểm chạm (**ease in**) [6:53–7:09].
4. Giảm độ xoay. Nghĩ xem góc nào chạm đất trước; giữ **góc chạm cố định giữa hai frame** khi bật nảy [7:24–8:26].
5. Năng lượng phải đi đâu đó: xoay chậm lại → nảy cao hơn [9:58]. Tốc độ lớn thì **trượt** nhẹ khi chạm [10:28].
6. Dùng **reference footage** (video quay chậm) [9:13–9:28]. Đặt một camera gần folder làm "mắt" để chỉnh [9:43].
7. Lật mặt cuối cho phẳng, ví dụ **−270** và **540** độ [13:52]. Nhích timing từng **1 frame** cho đúng tempo [14:37–15:39].

### 2.11 Đi bộ động vật bốn chân [Tjuvp57Ijg4]
1. Spawn mob → **Create walk cycle**. Giữ **2 key pose**, xoá phần còn lại [0:00–0:32].
2. Copy một key pose để có chỗ đặt **pose trung gian**: chân đang đưa lên trước **gập** ở khoảng giữa động tác (như passing pose của người) [0:32–0:47].
3. Vùng loop + **Enable looping**; tất cả keyframe → **Linear** [0:47–1:02].
4. **Bob thân:** chân thẳng đứng = cao nhất = **0**; chân dang rộng = **hạ xuống chút** [1:02–1:33].
5. **Library:** đổi sang mob cùng kiểu thân thì keyframe vẫn dùng được [1:33–1:49].
6. **Lưu và tái dùng:** chọn các key pose → right-click → **Save**. Project mới: chọn mob → **File → Import asset** → file keyframe; copy/paste lặp lại, giãn đều [1:49–2:37].

---

## 3. Áp dụng cho Bin & Bo (và Zu)

Bối cảnh: tập 1–3 phút hội thoại, khán giả trẻ em/gia đình Mỹ. Pipeline của mình **viết `.miproject` bằng Python** (`tools/mineimator/binbo_thu01/build.py`, OBSERVED). Mine-imator chỉ render.

**Quy ước đã kiểm trên render** (OBSERVED, README build.py):
- `ROT_Z = t` → nhân vật nhìn hướng `(sin t, cos t)`.
- `+ROT_X` làm đỉnh part ngả về trước: đầu cúi; tay/chân đang buông thì đánh **ra sau**. Giơ tay ra trước dùng ROT_X **âm**.
- Keyframe chỉ lưu giá trị khác mặc định; `build.py` có hàm `K()` mang trạng thái của keyframe trước sang.
- Template project `"tempo":24`.

**Chưa kiểm** (INFERRED, cần một render thử trước khi dùng hàng loạt):
- Dấu của ROT_Z trên **part** (đầu/thân xoay trái/phải).
- Dấu của ROT_Y (nghiêng sang bên).
- Dấu và trục của `BEND_ANGLE_X` ở gối/khuỷu (template có key `BEND_ANGLE_X`, OBSERVED).
- Tên `easeinoutcubic`, `easeoutbounce`.

Mọi công thức dưới đây ghi theo dạng `K(timeline, frame, transition, **giá trị)` như trong `build.py`, ở **24 fps**. Đổi fps (INFERRED): frame × 20/24 cho 20 fps, × 30/24 cho 30 fps.

### 3.0 Xếp hạng kỹ thuật cho tập hội thoại 1–3 phút

| Hạng | Kỹ thuật | Lý do (INFERRED) | Nguồn chính |
|---|---|---|---|
| 1 | Idle thở/lắc nhẹ cho người đang nghe | chiếm phần lớn thời lượng; luật "không bao giờ đứng im" | [aMTNQBzSGA8] [VdJh-vTewJY] |
| 2 | Quay đầu nhìn người nói (đầu đi trước, thân theo, settle) | mỗi lượt thoại đều cần | [aMTNQBzSGA8 3:13, 6:02] |
| 3 | Overlap/offset keyframe (đầu trễ ~10 frame, tay trễ hơn, hai tay lệch nhau) | rẻ, áp cho mọi động tác | [IyUfooxLmGE 6:53] |
| 4 | Đi vào khung hình + dừng có settle, chống trượt chân | mở cảnh / đổi vị trí | [NU0fAvOgEv0] [BmWf6dR4kks] [VdJh-vTewJY 16:48] |
| 5 | Quay người tại chỗ 90° (20–22 tick) | đổi hướng giữa thoại | [M-upI7h19kw 7:22] |
| 6 | Đưa/nhận đồ vật (nhân đôi item + visibility) | đạo cụ trong truyện | [Vjcc_vau-u8] [BUweokJnBXo] |
| 7 | Nhảy mừng (anticipation, gravity ease) | điểm nhấn cảm xúc | [I1CGhhEcOc4] [DO3d7Rh3e0E 6:32] |
| 8 | Quỳ / ngồi xổm ngang tầm Zu | cảnh an ủi bé zombie; **không có video nào trong nhóm B dạy trực tiếp**, chỉ suy từ nguyên lý thăng bằng | [I1CGhhEcOc4 3:26] (nguyên lý) |
| 9 | Walk cảm xúc (Bin happy, Zu tired/sad…) | tô màu tính cách | [mxc0aDlg7tU] |
| 10 | IK / Path | tiện trong GUI, nhưng **chưa biết cấu trúc JSON** cho constraint → chưa nên script (INFERRED) | [eEtFSQGXi_I] [NMRHDtSkehw] |

### 3.1 Idle khi người khác đang nói (thở + lắc)
Nguyên lý: thân mỗi ~20 tick (≈ 24 frame ở 24 fps); thay đổi rất nhỏ; mọi part `easeinoutsine`; đầu trễ ~10 frame; tay trễ hơn và lệch nhau [aMTNQBzSGA8 1:36–6:49].

Biên độ là INFERRED vì video chỉ nói "minimal". Đề xuất:

```python
def idle(ch, f0, f1, seed=0):
    # ~48 frame/chu kỳ thở = 2 nhịp 24 frame (chu kỳ INFERRED từ "~20 tick" [aMTNQBzSGA8 1:36])
    P = 24
    for i, f in enumerate(range(f0, f1, P)):
        up = i % 2
        s = 1 if (i // 2) % 2 else -1          # đổi bên mỗi chu kỳ
        K(ch['body'], f,      'easeinoutsine', BEND_ANGLE_X=1.5 if up else 0, ROT_Z=1.0*s)  # thân: nhô/hạ + xoay nhẹ
        K(ch['head'], f + 10, 'easeinoutsine', ROT_X=(-1 if up else 1.5), ROT_Z=-0.8*s, ROT_Y=0.5*s)  # đầu trễ 10, 3 trục [aMTNQBzSGA8 2:56]
        K(ch['right_arm'], f + 12, 'easeinoutsine', ROT_X=2 if up else 0, ROT_Z=3)   # tay nghỉ hơi mở ra ngoài [VdJh-vTewJY 15:58]
        K(ch['left_arm'],  f + 15, 'easeinoutsine', ROT_X=2 if up else 0, ROT_Z=-3)  # lệch tay kia 3 frame
```

- Tư thế nghỉ đừng để tay toàn 0 [VdJh-vTewJY 15:58]. Cảnh rộng thì thỉnh thoảng thêm một **weight shift** (ngả 0.4 về một chân) [aMTNQBzSGA8 12:54].
- Dấu ±, cũng như trục BEND/ROT_Y của thân và tay, là **INFERRED**. Cần render 1 lần để chắc chắn tay mở ra ngoài chứ không quặp vào (quặp vào = lo lắng [aMTNQBzSGA8 8:08]).
- Nhân vật đang nói: dùng cùng nền idle, thêm nhấn nhá đầu theo nhịp câu. Phần này thuộc nhóm hội thoại/lip-sync, không thuộc nhóm B.

### 3.2 Quay đầu → thân nhìn người nói (look-at) có settle
Nguyên lý:
- Đầu đi trước [aMTNQBzSGA8 3:13].
- Thân theo sau vài frame [VdJh-vTewJY 2:39].
- Đến nơi rồi lùi lại chút (settle) [aMTNQBzSGA8 6:02].
- Transition `easeinoutcubic` cho có lực [VdJh-vTewJY 11:40]; `easeinoutsine` nếu muốn thư thái.

```python
import math
def heading(dx, dy): return math.degrees(math.atan2(dx, dy))   # vì facing(t)=(sin t, cos t)  (OBSERVED convention)
def look_at(ch, f, body_t_now, target_dx, target_dy, s=1):
    t = heading(target_dx, target_dy); d = t - body_t_now        # góc cần quay (độ)
    # 1) đầu quay ~70% trước (8 frame), chớp mắt nên đặt ngay trước f  [aMTNQBzSGA8 15:30]
    K(ch['head'], f,     'easeinoutquad',  ROT_Z=0)
    K(ch['head'], f + 8, 'easeinoutcubic', ROT_Z=s*0.7*d)
    # 2) thân + root theo sau 4 frame, quay phần còn lại
    K(ch['char'], f + 4, 'easeinoutquad', ROT_Z=body_t_now)
    K(ch['char'], f + 16,'easeinoutquad', ROT_Z=body_t_now + 0.6*d)
    # 3) đầu bù lại khi thân đã tới + settle lùi nhẹ (không quay thêm)
    K(ch['head'], f + 18,'easeinoutsine', ROT_Z=s*(0.4*d - 0.05*d))
    K(ch['head'], f + 26,'easeinoutsine', ROT_Z=s*0.4*d)
```

- `s` là dấu ROT_Z của part đầu so với root. **Chưa kiểm** (INFERRED); dựng một render thử với `d=+30`.
- Tỉ lệ 70/60/40% và số frame 8/16/26 là INFERRED. Video chỉ nói "đầu trước", "đầu trễ ~10 frame" (bản idle cải tiến) và "đừng để keyframe đầu sát keyframe thân".
- Nếu chỉ liếc mắt (không quay thân), làm bước 1 rồi về 0 sau 30–60 frame.

### 3.3 Đi vào khung hình và dừng (walk-in + stop + settle)
**Rút ra cho `build.py` hiện tại** (OBSERVED code, INFERRED đánh giá):
- Đoạn walk-in hiện tại lắc chân/tay **±30° mỗi 6 frame** bằng `easeinoutsine`, còn root di chuyển `linear` → `easeoutquad`. Theo [BmWf6dR4kks 3:22], chân ease + thân linear = **trượt chân**. Theo [NU0fAvOgEv0 13:09], chân nên **linear**.
- Kiểm tra sải chân (INFERRED, chưa đo trên render):
  - Chân dài khoảng 12 đơn vị (chân Minecraft 12 px, INFERRED).
  - Đánh ±a độ → hai bàn chân cách nhau ≈ 2·12·sin(a). Với a=30°, khoảng cách ≈ **12 đơn vị mỗi nửa chu kỳ (6 frame)**.
  - Bin đi 120→30 = 90 đơn vị trong 80 frame ≈ **6.75 đơn vị / 6 frame**. Lệch gần ×2, nên rất có thể chân "trượt lùi".
  - Sửa bằng một trong hai cách: giảm biên độ còn **±16°** (2·12·sin16° ≈ 6.6), hoặc tăng quãng đường lên ~160 đơn vị / 80 frame.
  - Đo bằng contact sheet trước khi chốt.

**Công thức walk cycle 4 pose** (khung từ [NU0fAvOgEv0], số thân/đầu/bob OBSERVED; góc chân/tay INFERRED). Chu kỳ 24 frame (2 bước) ở 24 fps ≈ nhịp casual:

| frame (trong chu kỳ) | pose | right_leg ROT_X | left_leg ROT_X | right_leg BEND | left_leg BEND | right_arm ROT_X | left_arm ROT_X | body ROT_Z (twist) | head ROT_X (dip) | root POS_Z (bob) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | contact, chân phải trước | −16 | +16 | 0 | 0 | +12 | −12 | +5 [NU0f 11:52] | +4 [NU0f 12:39] | −1 [NU0f 16:51] |
| 6 | passing (chân trái đưa lên) | 0 | 0 | 0 | gập ~30 [NU0f 8:27, góc INFERRED] | 0 | 0 | 0 | 0 | 0 [NU0f 17:07] |
| 12 | contact, chân trái trước | +16 | −16 | 0 | 0 | −12 | +12 | −5 | −4 | −1 |
| 18 | passing (chân phải đưa lên) | 0 | 0 | gập ~30 | 0 | 0 | 0 | 0 | 0 | 0 |
| 24 | = frame 0 (loop) | | | | | | | | | |

Transition (OBSERVED nguồn):
- Chân: `linear` [NU0fAvOgEv0 13:09].
- Tay: `easeinoutquad` [NU0fAvOgEv0 13:24]; nên lệch tay trễ 1–2 frame [BmWf6dR4kks 8:55]. Lưu ý: khi **chạy** thì **không** trễ [BmWf6dR4kks 14:46].
- Bob và twist: `easeinoutsine` (INFERRED).
- Root di chuyển: `linear`, khớp quãng đường với sải chân.
- Nếu muốn root ease in lúc xuất phát và ease out lúc dừng, theo nguyên lý thì chân cũng phải cùng ease ở các keyframe đó [BmWf6dR4kks 3:22]. Cách thực tế hơn: chèn **bước dừng** riêng như dưới đây.

**Dừng có settle** [VdJh-vTewJY 16:48–17:20] [VRC_CwYqPVM 3:41] (đi bộ thì nhẹ hơn dừng chạy):

```python
# fs = frame bước cuối chạm đất
K(ch['char'], fs,      'linear',       POS_X=x_stop)               # root tới nơi đúng lúc bàn chân cuối chạm đất
K(ch['body'], fs,      'easeoutquad',  ROT_X=0)
K(ch['body'], fs + 4,  'easeoutquad',  ROT_X=4)                    # thân đổ nhẹ về trước theo quán tính (overlap) [VRC_CwYqPVM 8:37]
K(ch['char'], fs + 4,  'easeoutquad',  POS_Z=-0.6)                 # "settle": hạ người, gập gối nhẹ
K(ch['right_leg'], fs+4,'easeoutquad', BEND_ANGLE_X=8); K(ch['left_leg'], fs+4,'easeoutquad', BEND_ANGLE_X=8)
K(ch['body'], fs + 12, 'easeinoutsine',ROT_X=0)
K(ch['char'], fs + 12, 'easeinoutsine',POS_Z=0)
for leg in ('right_leg','left_leg'): K(ch[leg], fs+12, 'easeinoutsine', ROT_X=0, BEND_ANGLE_X=0)
K(ch['head'], fs + 6,  'easeinoutsine',ROT_X=-3); K(ch['head'], fs+16,'easeinoutsine',ROT_X=0)   # đầu trễ hơn thân
for arm,d in (('right_arm',2),('left_arm',5)): K(ch[arm], fs+d+8, 'easeoutquad', ROT_X=0)   # tay trễ nhất, lệch nhau
```

Mọi giá trị là INFERRED. Nguyên lý OBSERVED: chân không trượt, thân/đầu/tay trễ dần, ease out khi dừng.

### 3.4 Quay người tại chỗ 90° (đổi hướng nói chuyện)
Nguồn: [M-upI7h19kw 7:22–13:57]. **20–22 tick** cho 90° (OBSERVED), ở 24 fps ≈ 22–26 frame (INFERRED).

```python
# f0 = bắt đầu, quay từ t0 sang t0+90; chân trụ = left
K(ch['head'], f0,      'easeinoutquad', ROT_Z=0)
K(ch['head'], f0 + 8,  'easeinoutcubic',ROT_Z=s*45)                 # đầu dẫn trước
K(ch['char'], f0 + 2,  'easeinoutquad', ROT_Z=t0)
K(ch['char'], f0 + 24, 'easeinoutquad', ROT_Z=t0 + 90)              # thân + chân trụ cùng transition, cùng frame [M-upI7h19kw 9:16]
K(ch['left_leg'], f0 + 2, 'easeinoutquad', ROT_Z=0)
K(ch['left_leg'], f0 + 24,'easeinoutquad', ROT_Z=-s*90)             # bàn chân trụ xoay ngược để "đứng yên" trên đất [8:26]
K(ch['char'], f0 + 12, 'easeinoutquad', ROT_Y=s*3)                  # nghiêng nhẹ về phía quay [7:39]
K(ch['char'], f0 + 24, 'easeinoutquad', ROT_Y=0)
# chân tự do: nhấc (ease in) – đặt (ease out), LỆCH thời điểm so với thân [9:31][13:57]
K(ch['right_leg'], f0 + 6,  'easeinquad',  ROT_X=-10, BEND_ANGLE_X=15)
K(ch['right_leg'], f0 + 18, 'easeoutquad', ROT_X=0,   BEND_ANGLE_X=0)
# bước chỉnh cuối: chân trụ "trả" về 0 bằng một bước nhỏ (mỗi chân một lần), ease in -> ease out
K(ch['left_leg'], f0 + 26, 'easeinquad',  ROT_Z=-s*45, ROT_X=-8, BEND_ANGLE_X=12)
K(ch['left_leg'], f0 + 32, 'easeoutquad', ROT_Z=0, ROT_X=0, BEND_ANGLE_X=0)
K(ch['head'], f0 + 30, 'easeinoutsine', ROT_Z=0)                    # đầu về thẳng khi thân đã tới (settle)
```

- Dấu `s` và trục ROT_Z/ROT_Y của part là **INFERRED**; cần render kiểm.
- Pivot của nhân vật trong Mine-imator nằm ở bàn chân [aMTNQBzSGA8 12:22] (OBSERVED lời SharpWind), nên quay root thì chân không bay khỏi đất. Riêng chân trụ vẫn phải xoay bù.
- Nếu khó làm sạch, cắt khung ngang hông [M-upI7h19kw 12:09].

### 3.5 Đưa / nhận đồ vật (ví dụ Bin đưa quả táo cho Zu)
Phương pháp: **nhân đôi item + visibility cùng frame** [Vjcc_vau-u8 0:49–3:28] [BUweokJnBXo 7:22–8:08].

Cấu trúc:
- `apple_bin`: parent vào `right_arm` của Bin.
- `apple_zu`: parent vào tay Zu.
- (tuỳ chọn) `apple_free` nằm trong thế giới.

Chuyển giao:
1. **f_reach** (Bin vươn tay): `K(B['right_arm'], f_reach, 'easeinoutquad', ROT_X=0)` → `K(B['right_arm'], f_reach+10, 'easeoutback', ROT_X=-70)`. Giơ tay ra trước dùng ROT_X âm (OBSERVED convention); −70 ≈ ngang ngực (INFERRED).
   - Thân hơi đổ theo: `K(B['body'], f_reach+4, 'easeinoutquad', ROT_X=5)` (INFERRED). Có thể dồn trọng lượng sang chân trước [BUweokJnBXo 0:46].
   - Đầu nhìn vật/người nhận trước khi tay tới [aMTNQBzSGA8 3:13].
2. **Zu với tay** trễ 4–6 frame: `K(Z['right_arm'], f_reach+6, 'easeoutback', ROT_X=-60)`.
3. **f_swap** = f_reach+12: `K(apple_bin, f_swap, 'instant', VISIBLE=False)` và `K(apple_zu, f_swap, 'instant', VISIBLE=True)`. Hai bản phải trùng tư thế ở frame này [Vjcc_vau-u8 2:08].
   - **INFERRED:** tên key visibility trong `.miproject` chưa xác minh. Cần mở `template.miproject` hoặc source để lấy đúng tên trước khi dùng.
4. Hai tay rút về theo thứ tự lệch nhau (`easeinoutquad`, 10–14 frame). Thêm một nhịp "follow-through" nhỏ: tay Zu hạ, hơi nảy lại.

Nếu **ném** (Bo tung bóng cho Bin):
- Bản tự do nằm trong folder "gravity", lên `easeoutquad`, xuống `easeinquad`; ngang và xoay `linear` [BUweokJnBXo 8:24] [I1CGhhEcOc4 1:53].
- `build.py` đã làm đúng kiểu này cho cú nhảy của Zu: `easeoutquad` khi lên, `easeinquad` khi xuống (OBSERVED code) — khớp với nguyên lý trong video.

### 3.6 Nhảy mừng (jumping for joy)
Nguyên lý OBSERVED:
- Anticipation hạ người, khép gối trước khi bật [DO3d7Rh3e0E 1:49].
- Lên dùng **ease out**, xuống dùng **ease in** trên lớp lên/xuống riêng [DO3d7Rh3e0E 6:32] [I1CGhhEcOc4 1:53].
- Tiếp đất thì hạ thấp, gập chân để triệt chuyển động dọc [BUweokJnBXo 3:04].
- Tay trễ sau thân [IyUfooxLmGE 6:53].

```python
# fj = bắt đầu; nhảy 2 lần liên tiếp
K(ch['char'], fj,      'easeinoutquad', POS_Z=0)
K(ch['char'], fj + 5,  'easeoutquad',   POS_Z=-1.5)      # anticipation: hạ người
for leg in ('right_leg','left_leg'):
    K(ch[leg], fj + 5, 'easeoutquad', BEND_ANGLE_X=25, ROT_X=-12)   # gập gối (INFERRED sign)
K(ch['body'], fj + 5,  'easeoutquad',   ROT_X=8)         # thân cúi chuẩn bị
for k in range(2):
    a = fj + 5 + k*14
    K(ch['char'], a + 7,  'easeoutquad', POS_Z=6)        # lên: ease out (chậm dần ở đỉnh)
    K(ch['char'], a + 14, 'easeinquad',  POS_Z=0 if k else -1.0)   # xuống: ease in (nhanh dần), lần 1 tiếp đất có lún
    for leg in ('right_leg','left_leg'):
        K(ch[leg], a + 7,  'easeoutquad', BEND_ANGLE_X=0, ROT_X=0)
        K(ch[leg], a + 14, 'easeinquad',  BEND_ANGLE_X=18 if not k else 0)
    for arm, sgn, d in (('right_arm', 1, 2), ('left_arm', -1, 4)):     # tay vung lên, trễ 2/4 frame
        K(ch[arm], a + 7 + d, 'easeoutback', ROT_X=-150, ROT_Z=20*sgn)
K(ch['body'], fj + 12, 'easeoutquad', ROT_X=-6)          # ngực ưỡn khi ở đỉnh (happy = thân ưỡn [mxc0aDlg7tU 3:11])
K(ch['body'], fj + 36, 'easeinoutsine', ROT_X=0)
```

- Độ cao 6 và thời gian 14 frame mỗi lần nhảy là INFERRED. Kiểm tempo theo [LaVMLYU6JEA 2:58]: nhân vật cao ~32 đơn vị, nhảy 6 đơn vị trong ~0.3 s là hợp lý (INFERRED).
- Tay giơ `ROT_X=-150` khớp với cảnh cổ vũ đã có trong build.py (OBSERVED code).

### 3.7 Quỳ / ngồi xổm ngang tầm Zu (INFERRED hoàn toàn — không video nào trong nhóm dạy trực tiếp)
Áp nguyên lý:
- Trọng tâm nằm trên vùng tiếp xúc, một chân gập một chân duỗi đỡ trọng lượng [I1CGhhEcOc4 3:26–5:33].
- Hạ xuống ease in/out; vật nặng không tăng tốc tức thì [LaVMLYU6JEA 1:18].
- Đứng dậy thì **nhô tới trước rồi mới lên** [VRC_CwYqPVM 7:50].

```python
# quỳ một gối (chân phải chống, gối trái chạm đất)
K(ch['char'], fk,      'easeinoutquad', POS_Z=0)
K(ch['char'], fk + 14, 'easeinoutquad', POS_Z=-6)                     # hạ hông ~1/2 chiều dài chân (INFERRED)
K(ch['body'], fk + 6,  'easeinoutquad', ROT_X=10)                      # thân đổ trước giữ trọng tâm, trễ nhẹ sau hông
K(ch['body'], fk + 18, 'easeinoutsine', ROT_X=4)
K(ch['right_leg'], fk + 14,'easeinoutquad', ROT_X=-90, BEND_ANGLE_X=90)  # đùi phải ngang, cẳng thẳng đứng
K(ch['left_leg'],  fk + 14,'easeinoutquad', ROT_X=0,   BEND_ANGLE_X=90)  # gối trái xuống sàn, cẳng ra sau (dấu cần kiểm)
K(ch['head'], fk + 18, 'easeinoutsine', ROT_X=6)                       # nhìn xuống Zu, trễ hơn thân
# đứng dậy (ngược lại): body ROT_X tăng tới ~15 trước (nhô tới), rồi POS_Z về 0 với easeinoutquad trong 14–16 frame
```

Tất cả là INFERRED. Phải render từ góc nghiêng để xác nhận gối chạm sàn và bàn chân không xuyên sàn. Nếu khó, khung trung cảnh cắt ngang hông [M-upI7h19kw 12:09].

### 3.8 Gán phong cách đi theo nhân vật (đề xuất, INFERRED, cần OWNER duyệt)
- **Bin:** "Happy" khi hào hứng: sải dài, ngực ưỡn, tay đánh mạnh, transition gắt [mxc0aDlg7tU 2:56].
- **Bo:** "Casual": nhịp vừa, ngó quanh tò mò [mxc0aDlg7tU 1:37].
- **Zu (bé zombie):** "Tired" (sải nhỏ, overlap nhiều, lê thân) hoặc "Sad" khi buồn [mxc0aDlg7tU 1:53, 5:29]. Đổi sang Happy khi được an ủi; đó là vòng cung cảm xúc thể hiện bằng dáng đi.

### 3.9 Việc cần làm tiếp (đề xuất cho pipeline-engineer, có pytest)
1. Render một cảnh thử 5 giây để **chốt dấu**:
   - ROT_Z / ROT_Y của part đầu và thân;
   - `BEND_ANGLE_X` ở gối và khuỷu;
   - tên key visibility;
   - tên transition `easeinoutcubic` và bounce.
   Ghi kết quả vào README `binbo_thu01`.
2. Viết `walk_cycle(ch, f0, f1, stride, tempo)` dùng bảng 4 pose ở 3.3. Tính biên độ chân từ quãng đường root (sải ≈ 2·12·sin a) để hết trượt chân. Test: tổng dịch chuyển root mỗi nửa chu kỳ ≈ sải tính toán (±10%).
3. Viết `idle()`, `look_at()`, `turn90()`, `settle()` như 3.1–3.4. Thêm tham số offset ngẫu nhiên ±2 frame để hai nhân vật không thở đồng bộ (INFERRED từ luật "không trùng keyframe" [aMTNQBzSGA8 6:33]).
4. Cân nhắc dùng **folder** (timeline cha) để tách di chuyển và cycle như các video khuyên [NU0fAvOgEv0 15:27]. Cấu trúc folder trong `.miproject` chưa kiểm (INFERRED); cũng có thể dùng root (di chuyển) + body (bob) như hiện tại.

---

## 4. Những gì **không** có trong transcript (để khỏi giả định)
- Không có bảng góc chuẩn cho chân/tay của walk/run, trừ các số ở 2.1.
- Không nói fps của project.
- Không dạy quỳ/ngồi trong nhóm B.
- Không có cách viết IK/constraint vào JSON; video chỉ hướng dẫn GUI.
- Không có số đo nào về "cảm giác đúng". SharpWind nhấn mạnh: tự diễn thử, xem reference footage, chỉnh theo cảm giác [DO3d7Rh3e0E 6:17] [VRC_CwYqPVM 2:19] [I1CGhhEcOc4 9:13].
