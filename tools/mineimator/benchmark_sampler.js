// In-page sampler for a public YouTube watch page (paste into the page console / javascript tool).
// Same metrics as benchmark_frames.py: 160x90 frames every 0.2 s by SEEKING (works even when the tab is
// throttled; requestVideoFrameCallback sampling dropped frames and invented cuts). Reads pixels only to
// compute numbers in the page; nothing is downloaded or saved.
// Usage: __bench([[0,60],[360,60]]) then poll window.__bench_out / window.__bench_done.
window.__cfs = async function (start, dur, step) {
  const v = document.querySelector('video'); v.muted = true; v.pause();
  const W = 160, H = 90, c = document.createElement('canvas'); c.width = W; c.height = H;
  const ctx = c.getContext('2d', { willReadFrequently: true });
  let prev = null; const out = { luma: [], con: [], sat: [], cf: [], d: [], t: [] };
  for (let t = start; t < start + dur; t += step) {
    await new Promise(r => { const f = () => { v.removeEventListener('seeked', f); r(); }; v.addEventListener('seeked', f); v.currentTime = t; setTimeout(r, 3000); });
    if (v.readyState < 2) await new Promise(r => setTimeout(r, 300));
    ctx.drawImage(v, 0, 0, W, H); const p = ctx.getImageData(0, 0, W, H).data;
    const n = W * H; let sy = 0, sy2 = 0, ss = 0, rg = 0, rg2 = 0, yb = 0, yb2 = 0; const g = new Float32Array(n);
    for (let i = 0, j = 0; i < p.length; i += 4, j++) {
      const r = p[i], gg = p[i + 1], b = p[i + 2]; const y = .299 * r + .587 * gg + .114 * b; g[j] = y; sy += y; sy2 += y * y;
      const mx = Math.max(r, gg, b), mn = Math.min(r, gg, b); ss += mx > 0 ? (mx - mn) / mx : 0;
      const a = r - gg, bb = .5 * (r + gg) - b; rg += a; rg2 += a * a; yb += bb; yb2 += bb * bb;
    }
    const m = sy / n; out.luma.push(m); out.con.push(Math.sqrt(sy2 / n - m * m)); out.sat.push(ss / n);
    const mrg = rg / n, myb = yb / n; out.cf.push(Math.sqrt((rg2 / n - mrg * mrg) + (yb2 / n - myb * myb)) + .3 * Math.sqrt(mrg * mrg + myb * myb));
    if (prev) { let s = 0; for (let k = 0; k < n; k++) s += Math.abs(g[k] - prev[k]); out.d.push(s / n); out.t.push(t); }
    prev = g; window.__prog = t;
  }
  const d = out.d, med = a => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)] || 0; }; const cuts = [];
  for (let i = 0; i < d.length; i++) if (d[i] > 10 && d[i] > 3 * med(d.slice(Math.max(0, i - 5), i + 6))) {
    const tt = +out.t[i].toFixed(1); if (!cuts.length || tt - cuts[cuts.length - 1] > 0.5) cuts.push(tt);
  }
  const avg = a => a.reduce((x, y) => x + y, 0) / a.length;
  return { start, secs: dur, res: v.videoWidth + 'x' + v.videoHeight, luma: +avg(out.luma).toFixed(1), contrast: +avg(out.con).toFixed(1),
    saturation: +avg(out.sat).toFixed(3), colorfulness: +avg(out.cf).toFixed(1), cuts: cuts.length, cuts_per_min: +(cuts.length / dur * 60).toFixed(1),
    avg_shot_s: +(dur / (cuts.length + 1)).toFixed(2), motion_median: +med(d).toFixed(2) };
};
window.__bench = windows => { window.__bench_out = []; window.__bench_done = false;
  (async () => { for (const [s, d] of windows) window.__bench_out.push(await window.__cfs(s, d, 0.2)); window.__bench_done = true; })()
    .catch(e => { window.__bench_err = String(e); }); };
