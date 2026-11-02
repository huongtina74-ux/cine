import json, sys, html
tl=json.load(open('web/timeline.json'))
VIDEO, THUMB = sys.argv[1], sys.argv[2]
B={b['id']:b for b in tl['beats']}
S=lambda i:B[i]['start']
shots=[(0,'Hook — Bin rơi xuống hố sâu (3 giây đầu)'),(S('card')-.25,'Thẻ "30 GIÂY TRƯỚC..."'),(S('see')-.6,'Đồng cỏ — Bin & Bo đi tới nút đỏ'),
 (S('warn')-.1,'Bo cảnh báo (góc qua vai)'),(S('tiny')-.1,'Bin định bấm (cận mặt, nút ở tiền cảnh)'),(S('press')-.5,'Cận nút — CLICK'),
 (S('press'),'Sàn mở ra, Bin rơi'),(S('jump')-.3,'Nhìn từ đáy hố lên — Bo nhảy xuống'),(S('gold')-.3,'Lộ phòng toàn vàng (camera lượn vòng)'),
 (S('wait')-.15,'Bo: "Khoan đã!"'),(S('grab')-.2,'Bin lấy khối vàng — hầm rung chuyển'),(S('lava')-.1,'Nham thạch dâng lên'),
 (S('climb')-.1,'Xây cột thoát lên (nhìn từ trên xuống)'),(S('drop')-.1,'Cận Bin ôm vàng: "Không đời nào!"'),
 (S('phew')-.3,'Lên mặt đất — "Tớ hứa!"'),(S('blue')-.2,'Phát hiện nút xanh'),(S('boom')-.2,'BÙMMM!'),(S('boom')+B['boom']['dur']+1.0,'Mặt mũi lấm lem + màn kêu gọi đăng ký')]
fmt=lambda t:f"{int(t//60)}:{t%60:05.2f}"
rows=''.join(f'<div style="display: grid; grid-template-columns: 96px minmax(0, 1fr); gap: 12px; padding: 6px 0; border-top: 1px solid #2c333d"><span style="font-family: monospace; font-size: 13px; color: #eeeeff">{fmt(t)}</span><span style="font-size: 14px; color: #eeeeff">{html.escape(d)}</span></div>' for t,d in shots)
lines=''.join(f'<div style="display: grid; grid-template-columns: 96px 44px minmax(0, 1fr); gap: 12px; padding: 5px 0; border-top: 1px solid #2c333d"><span style="font-family: monospace; font-size: 13px; color: #eeeeff">{fmt(b["start"])}</span><span style="font-family: monospace; font-size: 13px; color: #eeeeff">{ {"bin":"BIN","bo":"BO","nar":"KỂ"}[b["who"]] }</span><span style="font-size: 14px; color: #eeeeff">{html.escape(b.get("cap") or b["text"])}</span></div>' for b in tl['beats'])
log=[("Kịch bản","PASS","Hook 3 giây đầu: Bin đang rơi và la hét. Phân vai tương phản: Bin ngố, tò mò, tham; Bo thông minh, nghiêm túc. 22 câu thoại ngắn, nhiều câu cảm thán."),
 ("Thu âm trước","PASS","Thu toàn bộ lời thoại trước, rồi dựng hình theo đúng thời lượng từng câu. Giọng Bin tăng cao độ 35% (kiểu chipmunk), Bo 6%, người kể giảm 14%. Miệng nhân vật mấp máy theo âm lượng giọng đọc."),
 ("Map & skin","PASS","Thế giới khối vuông tự dựng: đồng cỏ, cây, hố sâu, hầm vàng, nham thạch. Bin và Bo là nhân vật gốc, không dùng skin hay nhân vật của kênh khác."),
 ("Diễn & góc máy","PASS","18 cảnh, camera lia, lượn vòng, nhìn từ đáy hố lên, rung khi nổ. Render 1920×1080, 30 fps."),
 ("Hậu kỳ","PASS","Phụ đề vàng neon viền đen nảy theo từng từ, kèm nhãn tên người nói. Nhạc nền tự sáng tác (rón rén, phép thuật, hành động, vui nhộn). 40+ hiệu ứng âm thanh. Nhạc tự hạ khi có thoại."),
 ("Thumbnail","PASS","1280×720: Bin rơi xuống hố, Bo hét lên, nút đỏ khoanh tròn kèm mũi tên đỏ, chữ to ĐỪNG BẤM NÚT ĐỎ NÀY!")]
logh=''.join(f'<div style="display: grid; grid-template-columns: 140px 64px minmax(0, 1fr); gap: 12px; padding: 8px 0; border-top: 1px solid #2c333d"><span style="font-size: 14px; font-weight: 700; color: #eeeeff">{a}</span><span style="font-family: monospace; font-size: 13px; color: #eeeeff">{b}</span><span style="font-size: 14px; color: #eeeeff">{html.escape(c)}</span></div>' for a,b,c in log)
gaps=["Giọng đọc là AI tiếng Việt (Piper). Thanh điệu đúng nhưng vẫn hơi máy. Bản đăng thật nên thay bằng giọng người thật hoặc giọng clone, dùng đúng thời lượng từng câu trong file kịch bản.",
 "Hình dựng bằng trình kết xuất 3D tự viết, không quay trong Minecraft thật. Muốn có shader đẹp kiểu Replay Mod hoặc BBS thì quay lại cảnh trong game theo cùng kịch bản và nhịp âm thanh.",
 "Thumbnail chưa được thử A/B. Chưa có số liệu CTR hay tỉ lệ giữ chân người xem."]
gh=''.join(f'<p style="margin: 0; padding: 8px 0; border-top: 1px solid #2c333d; font-size: 14px; color: #eeeeff; text-wrap: pretty">{html.escape(g)}</p>' for g in gaps)
card='background: #151920; border: 1px solid #2c333d; border-radius: 10px; padding: 14px; box-sizing: border-box'
doc=f'''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Bin &amp; Bo — Tập 1</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<style>
body{{margin:0}}
a{{color:#eeeeff}}a:hover{{color:#e7edf6}}
</style>
</helmet>
<div style="width: 1440px; height: 1900px; box-sizing: border-box; padding: 30px 18px; background: #0d0f12; color: #eeeeff; font-family: system-ui, sans-serif; display: flex; flex-direction: column; gap: 18px">
<div style="display: flex; flex-direction: column; gap: 8px">
<h1 style="margin: 0; font-size: 32px; font-weight: 700">Bin &amp; Bo — Tập 1: Nút Đỏ Bí Ẩn</h1>
<p style="margin: 0; font-family: monospace; font-size: 13px">{tl["total"]:.1f}s · 1920×1080 · 30fps · language: "vi" · READY_FOR_HUMAN_VISUAL_REVIEW</p>
</div>
<div style="display: grid; grid-template-columns: 960px minmax(0, 1fr); gap: 12px">
<div style="{card}; display: flex; flex-direction: column; gap: 8px">
<h2 style="margin: 0; font-size: 16px; font-weight: 700">Master</h2>
<video src="{VIDEO}" poster="{THUMB}" controls="controls" playsinline="playsinline" preload="metadata" style="width: 930px; height: 523px; border-radius: 8px; background: #000; display: block"></video>
</div>
<div style="{card}; display: flex; flex-direction: column; gap: 8px">
<h2 style="margin: 0; font-size: 16px; font-weight: 700">Thumbnail</h2>
<img src="{THUMB}" alt="Thumbnail: Bin rơi xuống hố, Bo hét, nút đỏ được khoanh tròn, chữ ĐỪNG BẤM NÚT ĐỎ NÀY" style="width: 100%; border-radius: 8px; display: block">
<p style="margin: 0; font-family: monospace; font-size: 13px">1280×720 · jpg</p>
</div>
</div>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px">
<div style="{card}"><h2 style="margin: 0 0 8px; font-size: 16px; font-weight: 700">Pipeline</h2>{logh}</div>
<div style="{card}"><h2 style="margin: 0 0 8px; font-size: 16px; font-weight: 700">Shots</h2>{rows}</div>
</div>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px">
<div style="{card}"><h2 style="margin: 0 0 8px; font-size: 16px; font-weight: 700">Dialogue</h2>{lines}</div>
<div style="{card}"><h2 style="margin: 0 0 8px; font-size: 16px; font-weight: 700">Not Yet Proven</h2>{gh}</div>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1440,"height":1900}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
print(doc)

