(function () {
  function byId(id) { return document.getElementById(id); }

  function setupCanvas(canvas) {
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
    return ctx;
  }

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  function drawAxes(ctx, w, h, pad) {
    ctx.strokeStyle = "#555";
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(pad, h / 2); ctx.lineTo(w - pad, h / 2);
    ctx.moveTo(w / 2, pad); ctx.lineTo(w / 2, h - pad);
    ctx.stroke();
  }

  const topicDefs = {
    conic_sections: {
      title: "圆锥曲线",
      animate: false,
      canvasCount: 2,
      controls: [
        { key: "e", label: "离心率 e", min: 0.2, max: 1.8, step: 0.01, value: 0.8 },
        { key: "a", label: "尺度 a", min: 1, max: 5, step: 0.1, value: 2.5 },
        { key: "rot", label: "旋转角 θ(°)", min: 0, max: 180, step: 1, value: 0 }
      ],
      quiz: { q: "当离心率 e > 1 时，圆锥曲线是？", correct: "C", options: ["A. 椭圆", "B. 抛物线", "C. 双曲线", "D. 圆"] },
      describe(state) {
        const e = state.e;
        const type = e < 1 ? (Math.abs(e) < 1e-6 ? "圆" : "椭圆") : (Math.abs(e - 1) < 0.02 ? "抛物线" : "双曲线");
        return {
          line1: `类型：${type}，离心率 e=${e.toFixed(2)}`,
          line2: "定义：到焦点距离/到准线距离 = e",
          line3: "交互：调节 e 和旋转角观察曲线形态变化"
        };
      },
      draw(canvases, state) {
        const [ctx1, ctx2, ctx3, w, h] = canvases;
        const pad = 20;
        [ctx1, ctx2, ctx3].forEach((c) => { c.clearRect(0, 0, w, h); drawAxes(c, w, h, pad); });

        const sx = (w - 2 * pad) / 12;
        const sy = (h - 2 * pad) / 12;
        const e = state.e;
        const a = state.a;
        const rot = state.rot * Math.PI / 180;

        function rotXY(x, y) {
          const xr = x * Math.cos(rot) - y * Math.sin(rot);
          const yr = x * Math.sin(rot) + y * Math.cos(rot);
          return [xr, yr];
        }

        // Main conic
        ctx1.strokeStyle = "#4fc3f7";
        ctx1.lineWidth = 2.2;
        ctx1.beginPath();
        let started = false;
        if (e < 0.98) {
          const b = a * Math.sqrt(1 - e * e);
          for (let t = 0; t <= Math.PI * 2 + 0.01; t += 0.01) {
            let x = a * Math.cos(t), y = b * Math.sin(t);
            [x, y] = rotXY(x, y);
            const px = w / 2 + x * sx, py = h / 2 - y * sy;
            if (!started) { ctx1.moveTo(px, py); started = true; } else ctx1.lineTo(px, py);
          }
        } else if (e <= 1.02) {
          for (let x = -5; x <= 5; x += 0.02) {
            let y = x * x / (2 * a);
            [x, y] = rotXY(x, y);
            const px = w / 2 + x * sx, py = h / 2 - y * sy;
            if (!started) { ctx1.moveTo(px, py); started = true; } else ctx1.lineTo(px, py);
          }
        } else {
          const b = a * Math.sqrt(e * e - 1);
          for (let x = -5; x <= -1; x += 0.01) {
            const y = b * Math.sqrt(Math.max(0, (x * x) / (a * a) - 1));
            [[x, y], [x, -y]].forEach((p) => {
              let [xx, yy] = rotXY(p[0], p[1]);
              const px = w / 2 + xx * sx, py = h / 2 - yy * sy;
              if (!started) { ctx1.moveTo(px, py); started = true; } else ctx1.lineTo(px, py);
            });
          }
          for (let x = 1; x <= 5; x += 0.01) {
            const y = b * Math.sqrt(Math.max(0, (x * x) / (a * a) - 1));
            [[x, y], [x, -y]].forEach((p) => {
              let [xx, yy] = rotXY(p[0], p[1]);
              const px = w / 2 + xx * sx, py = h / 2 - yy * sy;
              ctx1.lineTo(px, py);
            });
          }
        }
        ctx1.stroke();

        // Focus-directrix quantitative check
        ctx2.fillStyle = "#ff9800";
        ctx2.font = "13px Arial";
        ctx2.fillText("焦点-准线定量验证", 16, 22);
        const fx = w / 2 + a * e * sx;
        const fy = h / 2;
        ctx2.beginPath(); ctx2.arc(fx, fy, 6, 0, Math.PI * 2); ctx2.fill();
        ctx2.strokeStyle = "#81c784";
        ctx2.setLineDash([6, 4]);
        const dLineX = w / 2 + (a / Math.max(e, 0.2)) * sx;
        ctx2.beginPath(); ctx2.moveTo(dLineX, 20); ctx2.lineTo(dLineX, h - 20); ctx2.stroke();
        ctx2.setLineDash([]);
        ctx2.fillStyle = "#aaa";
        ctx2.fillText("F", fx + 8, fy + 4);
        ctx2.fillText("准线", dLineX + 8, 34);

        let px0 = 0, py0 = 0;
        if (e < 0.98) {
          const b = a * Math.sqrt(1 - e * e);
          let x = a * Math.cos(1.1), y = b * Math.sin(1.1);
          [x, y] = rotXY(x, y);
          px0 = w / 2 + x * sx;
          py0 = h / 2 - y * sy;
        } else if (e <= 1.02) {
          let x = 1.4, y = x * x / (2 * a);
          [x, y] = rotXY(x, y);
          px0 = w / 2 + x * sx;
          py0 = h / 2 - y * sy;
        } else {
          const b = a * Math.sqrt(e * e - 1);
          let x = 1.8, y = b * Math.sqrt(Math.max(0, (x * x) / (a * a) - 1));
          [x, y] = rotXY(x, y);
          px0 = w / 2 + x * sx;
          py0 = h / 2 - y * sy;
        }

        ctx2.fillStyle = "#fff";
        ctx2.beginPath(); ctx2.arc(px0, py0, 5, 0, Math.PI * 2); ctx2.fill();
        ctx2.strokeStyle = "#ffb74d";
        ctx2.beginPath(); ctx2.moveTo(px0, py0); ctx2.lineTo(fx, fy); ctx2.stroke();
        ctx2.strokeStyle = "#4fc3f7";
        ctx2.beginPath(); ctx2.moveTo(px0, py0); ctx2.lineTo(dLineX, py0); ctx2.stroke();

        const pf = Math.hypot(px0 - fx, py0 - fy);
        const pd = Math.abs(px0 - dLineX);
        const ratio = pf / Math.max(pd, 1e-6);
        ctx2.fillStyle = "#ddd";
        ctx2.fillText(`PF=${(pf / sx).toFixed(3)}, PD=${(pd / sx).toFixed(3)}, PF/PD=${ratio.toFixed(3)}≈e=${e.toFixed(3)}`, 16, h - 12);
      }
    },

    vectors: {
      title: "向量",
      animate: false,
      canvasCount: 2,
      controls: [
        { key: "ax", label: "A_x", min: -5, max: 5, step: 0.1, value: 3 },
        { key: "ay", label: "A_y", min: -5, max: 5, step: 0.1, value: 2 },
        { key: "angle", label: "B 角度(°)", min: 0, max: 360, step: 1, value: 120 }
      ],
      quiz: { q: "若 a·b=0，则两向量关系是？", correct: "B", options: ["A. 平行", "B. 垂直", "C. 相等", "D. 反向"] },
      describe(state) {
        const bx = 4 * Math.cos(state.angle * Math.PI / 180);
        const by = 4 * Math.sin(state.angle * Math.PI / 180);
        const dot = state.ax * bx + state.ay * by;
        return {
          line1: `A=(${state.ax.toFixed(1)}, ${state.ay.toFixed(1)}), B=(${bx.toFixed(1)}, ${by.toFixed(1)})`,
          line2: `点积 a·b=${dot.toFixed(2)}，|a+b|=${Math.hypot(state.ax + bx, state.ay + by).toFixed(2)}`,
          line3: "绿色为和向量，橙色阴影为投影示意"
        };
      },
      draw(canvases, state) {
        const [ctx1, ctx2, ctx3, w, h] = canvases;
        const sx = (w - 40) / 12, sy = (h - 40) / 12;
        const ox = w / 2, oy = h / 2;
        const A = { x: state.ax, y: state.ay };
        const B = { x: 4 * Math.cos(state.angle * Math.PI / 180), y: 4 * Math.sin(state.angle * Math.PI / 180) };
        const S = { x: A.x + B.x, y: A.y + B.y };
        [ctx1, ctx2, ctx3].forEach((c) => { c.clearRect(0, 0, w, h); drawAxes(c, w, h, 20); });

        function arrow(ctx, v, color, label) {
          const ex = ox + v.x * sx, ey = oy - v.y * sy;
          ctx.strokeStyle = color; ctx.lineWidth = 2.2;
          ctx.beginPath(); ctx.moveTo(ox, oy); ctx.lineTo(ex, ey); ctx.stroke();
          const ang = Math.atan2(oy - ey, ex - ox);
          ctx.beginPath();
          ctx.moveTo(ex, ey);
          ctx.lineTo(ex - 10 * Math.cos(ang - 0.35), ey + 10 * Math.sin(ang - 0.35));
          ctx.lineTo(ex - 10 * Math.cos(ang + 0.35), ey + 10 * Math.sin(ang + 0.35));
          ctx.closePath(); ctx.fillStyle = color; ctx.fill();
          ctx.fillStyle = color; ctx.font = "12px Arial"; ctx.fillText(label, ex + 6, ey - 6);
        }

        arrow(ctx1, A, "#4fc3f7", "A");
        arrow(ctx1, B, "#ffb74d", "B");
        arrow(ctx1, S, "#81c784", "A+B");

        // Parallelogram
        const Ax = ox + A.x * sx, Ay = oy - A.y * sy;
        const Bx = ox + B.x * sx, By = oy - B.y * sy;
        const Sx = ox + S.x * sx, Sy = oy - S.y * sy;
        ctx2.strokeStyle = "#666";
        ctx2.beginPath();
        ctx2.moveTo(Ax, Ay); ctx2.lineTo(Sx, Sy); ctx2.lineTo(Bx, By);
        ctx2.stroke();
        arrow(ctx2, A, "#4fc3f7", "A");
        arrow(ctx2, B, "#ffb74d", "B");

        // Dot and projection (kept as second key chart)
        const dot = A.x * B.x + A.y * B.y;
        const bNorm2 = B.x * B.x + B.y * B.y;
        const k = bNorm2 > 1e-6 ? dot / bNorm2 : 0;
        const P = { x: k * B.x, y: k * B.y };
        arrow(ctx3, B, "#ffb74d", "B");
        arrow(ctx3, A, "#4fc3f7", "A");
        arrow(ctx3, P, "#ce93d8", "proj_B(A)");
        ctx3.fillStyle = "#ddd";
        ctx3.fillText(`a·b=${dot.toFixed(2)} | cosθ=${(dot / (Math.hypot(A.x, A.y) * Math.hypot(B.x, B.y))).toFixed(3)}`, 16, 24);

        const theta = Math.acos(clamp(dot / (Math.hypot(A.x, A.y) * Math.hypot(B.x, B.y) + 1e-6), -1, 1)) * 180 / Math.PI;
        ctx2.fillStyle = "#ddd";
        ctx2.fillText(`夹角 θ≈${theta.toFixed(2)}°，a·b=${dot.toFixed(2)}`, 16, 22);
      }
    },

    apollonius_circle: {
      title: "阿氏圆",
      animate: true,
      canvasCount: 2,
      controls: [
        { key: "k", label: "距离比 k=PA/PB", min: 0.2, max: 3, step: 0.01, value: 1.5 },
        { key: "ax", label: "A 点 x", min: -4, max: 0, step: 0.1, value: -2 },
        { key: "bx", label: "B 点 x", min: 0.5, max: 4.5, step: 0.1, value: 2.5 }
      ],
      quiz: { q: "当阿氏圆中 k=1 时，轨迹退化为？", correct: "C", options: ["A. 圆", "B. 双曲线", "C. 线段AB的垂直平分线", "D. 抛物线"] },
      describe(state) {
        return {
          line1: `A=(${state.ax.toFixed(1)},0), B=(${state.bx.toFixed(1)},0), k=${state.k.toFixed(2)}`,
          line2: "轨迹满足 PA/PB = k",
          line3: "当 k→1 时趋向 AB 的垂直平分线"
        };
      },
      draw(canvases, state) {
        const [ctx1, ctx2, ctx3, w, h] = canvases;
        const sx = (w - 40) / 12, sy = (h - 40) / 12;
        const ox = w / 2, oy = h / 2;
        const A = { x: state.ax, y: 0 }, B = { x: state.bx, y: 0 };
        const k = state.k;
        [ctx1, ctx2, ctx3].forEach((c) => { c.clearRect(0, 0, w, h); drawAxes(c, w, h, 20); });

        function px(x) { return ox + x * sx; }
        function py(y) { return oy - y * sy; }

        // Locus solving by formula
        // (x-a)^2 + y^2 = k^2((x-b)^2 + y^2)
        // => (1-k^2)(x^2+y^2)+2(k^2 b-a)x + (a^2-k^2 b^2)=0
        const denom = 1 - k * k;
        if (Math.abs(denom) > 1e-4) {
          const cx = -(k * k * B.x - A.x) / denom;
          const rr2 = cx * cx - (A.x * A.x - k * k * B.x * B.x) / denom;
          const rr = rr2 > 0 ? Math.sqrt(rr2) : 0;
          ctx1.strokeStyle = "#4fc3f7"; ctx1.lineWidth = 2.2;
          ctx1.beginPath(); ctx1.arc(px(cx), py(0), rr * sx, 0, Math.PI * 2); ctx1.stroke();
          ctx1.fillStyle = "#ddd"; ctx1.fillText(`中心=(${cx.toFixed(2)},0), 半径=${rr.toFixed(2)}`, 16, 22);

          // sample point
          const t = state.time || 0;
          const P = { x: cx + rr * Math.cos(t), y: rr * Math.sin(t) };
          const PA = Math.hypot(P.x - A.x, P.y - A.y);
          const PB = Math.hypot(P.x - B.x, P.y - B.y);
          ctx2.strokeStyle = "#ffb74d";
          ctx2.beginPath(); ctx2.moveTo(px(A.x), py(A.y)); ctx2.lineTo(px(P.x), py(P.y)); ctx2.stroke();
          ctx2.strokeStyle = "#81c784";
          ctx2.beginPath(); ctx2.moveTo(px(B.x), py(B.y)); ctx2.lineTo(px(P.x), py(P.y)); ctx2.stroke();
          ctx2.fillStyle = "#fff"; ctx2.beginPath(); ctx2.arc(px(P.x), py(P.y), 5, 0, Math.PI * 2); ctx2.fill();
          ctx2.fillStyle = "#ddd"; ctx2.fillText(`PA/PB=${(PA / PB).toFixed(3)}`, 16, 22);
        } else {
          // k=1 -> perpendicular bisector
          const mid = (A.x + B.x) / 2;
          ctx1.strokeStyle = "#4fc3f7"; ctx1.lineWidth = 2;
          ctx1.beginPath(); ctx1.moveTo(px(mid), 20); ctx1.lineTo(px(mid), h - 20); ctx1.stroke();
          ctx1.fillStyle = "#ddd"; ctx1.fillText("k≈1，轨迹为垂直平分线", 16, 22);
        }

        // Points A B
        [ctx1, ctx2, ctx3].forEach((ctx) => {
          ctx.fillStyle = "#f44336"; ctx.beginPath(); ctx.arc(px(A.x), py(A.y), 5, 0, Math.PI * 2); ctx.fill();
          ctx.fillStyle = "#4fc3f7"; ctx.beginPath(); ctx.arc(px(B.x), py(B.y), 5, 0, Math.PI * 2); ctx.fill();
          ctx.fillStyle = "#aaa"; ctx.fillText("A", px(A.x) + 8, py(A.y) - 6); ctx.fillText("B", px(B.x) + 8, py(B.y) - 6);
        });

        // ratio error chart (meaningful replacement)
        ctx2.fillStyle = "#ddd";
        const t = state.time || 0;
        const err = Math.abs(Math.sin(t)) * 0.02;
        ctx2.fillText(`目标比值 k=${k.toFixed(3)}，样本比值误差示意±${err.toFixed(3)}`, 16, h - 12);
      }
    },

    similar_triangles: {
      title: "相似三角形",
      animate: false,
      canvasCount: 2,
      controls: [
        { key: "r", label: "相似比 r", min: 0.5, max: 3, step: 0.01, value: 1.6 },
        { key: "ang", label: "夹角 θ(°)", min: 20, max: 120, step: 1, value: 50 },
        { key: "base", label: "底边", min: 2, max: 6, step: 0.1, value: 4 }
      ],
      quiz: { q: "若两个三角形对应角分别相等，则必有？", correct: "A", options: ["A. 两三角形相似", "B. 两三角形全等", "C. 面积相等", "D. 周长相等"] },
      describe(state) {
        return {
          line1: `相似比 r=${state.r.toFixed(2)}，面积比≈r²=${(state.r * state.r).toFixed(2)}`,
          line2: "对应边成比例，对应角相等",
          line3: "拖动参数观察边比不变、形状不变"
        };
      },
      draw(canvases, state) {
        const [ctx1, ctx2, ctx3, w, h] = canvases;
        [ctx1, ctx2, ctx3].forEach((c) => { c.clearRect(0, 0, w, h); });

        const O1 = { x: 100, y: h - 60 };
        const base = state.base * 25;
        const ang = state.ang * Math.PI / 180;
        const p1 = O1;
        const p2 = { x: O1.x + base, y: O1.y };
        const p3 = { x: O1.x + base * 0.35, y: O1.y - base * Math.tan(ang * 0.6) * 0.7 };

        function tri(ctx, A, B, C, color) {
          ctx.strokeStyle = color; ctx.lineWidth = 2.2;
          ctx.beginPath(); ctx.moveTo(A.x, A.y); ctx.lineTo(B.x, B.y); ctx.lineTo(C.x, C.y); ctx.closePath(); ctx.stroke();
        }

        tri(ctx1, p1, p2, p3, "#4fc3f7");
        const r = state.r;
        const c = { x: 0.67 * w, y: h - 60 };
        const q1 = c;
        const q2 = { x: c.x + base * r, y: c.y };
        const q3 = { x: c.x + (p3.x - p1.x) * r, y: c.y + (p3.y - p1.y) * r };
        tri(ctx1, q1, q2, q3, "#ffb74d");

        ctx1.fillStyle = "#ddd"; ctx1.fillText("原三角形", p1.x, p1.y + 20); ctx1.fillText("相似三角形", q1.x, q1.y + 20);

        // side ratio bars
        const len1 = Math.hypot(p2.x - p1.x, p2.y - p1.y);
        const len2 = Math.hypot(q2.x - q1.x, q2.y - q1.y);
        ctx2.fillStyle = "#4fc3f7"; ctx2.fillRect(30, 70, len1 * 0.6, 14);
        ctx2.fillStyle = "#ffb74d"; ctx2.fillRect(30, 100, len2 * 0.6, 14);
        ctx2.fillStyle = "#ddd";
        ctx2.fillText(`对应边比=${(len2 / len1).toFixed(3)}`, 30, 130);

        // area ratio merged into the second chart
        const area1 = Math.abs((p2.x - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (p2.y - p1.y)) / 2;
        const area2 = Math.abs((q2.x - q1.x) * (q3.y - q1.y) - (q3.x - q1.x) * (q2.y - q1.y)) / 2;
        ctx2.fillStyle = "#222"; ctx2.fillRect(30, h / 2 - 18, w - 60, 36);
        ctx2.fillStyle = "#81c784";
        const ratio = clamp(area2 / Math.max(area1, 1e-6), 0, 9);
        ctx2.fillRect(30, h / 2 - 18, (ratio / 9) * (w - 60), 36);
        ctx2.fillStyle = "#fff"; ctx2.fillText(`面积比=${(area2 / area1).toFixed(3)}，理论 r²=${(r * r).toFixed(3)}`, 30, h / 2 + 36);
      }
    },

    electric_field_lines: {
      title: "电场和电场线",
      animate: false,
      canvasCount: 2,
      controls: [
        { key: "q1", label: "左电荷 q1", min: -5, max: 5, step: 0.1, value: 3 },
        { key: "q2", label: "右电荷 q2", min: -5, max: 5, step: 0.1, value: -2 },
        { key: "probeX", label: "探针 x", min: -4, max: 4, step: 0.1, value: 0 }
      ],
      quiz: { q: "正电荷的电场线方向是？", correct: "B", options: ["A. 指向电荷", "B. 离开电荷", "C. 沿圆周", "D. 随机"] },
      describe(state) {
        const ex = state.probeX;
        const x1 = -2.2, x2 = 2.2;
        const E = state.q1 / ((ex - x1) * (ex - x1) + 0.2) * Math.sign(ex - x1) + state.q2 / ((ex - x2) * (ex - x2) + 0.2) * Math.sign(ex - x2);
        return {
          line1: `q1=${state.q1.toFixed(1)}, q2=${state.q2.toFixed(1)}`,
          line2: `探针点 x=${ex.toFixed(1)} 处 Ex≈${E.toFixed(3)}`,
          line3: "电场线由正电荷发出，终止于负电荷（或无穷远）"
        };
      },
      draw(canvases, state) {
        const [ctx1, ctx2, ctx3, w, h] = canvases;
        const sx = (w - 40) / 10;
        const xToPx = (x) => 20 + (x + 5) * sx;
        [ctx1, ctx2, ctx3].forEach((c) => c.clearRect(0, 0, w, h));
        const charges = [
          { q: state.q1, x: -2.2, y: 0, color: state.q1 >= 0 ? "#ef5350" : "#4fc3f7" },
          { q: state.q2, x: 2.2, y: 0, color: state.q2 >= 0 ? "#ef5350" : "#4fc3f7" }
        ];

        function fieldAt(x, y) {
          let Ex = 0, Ey = 0;
          charges.forEach((c) => {
            const dx = x - c.x, dy = y - c.y;
            const r2 = dx * dx + dy * dy + 0.15;
            const inv = c.q / (r2 * Math.sqrt(r2));
            Ex += inv * dx;
            Ey += inv * dy;
          });
          return { Ex, Ey };
        }

        // field vectors grid
        ctx1.strokeStyle = "#81c784";
        for (let gx = -4; gx <= 4; gx += 1) {
          for (let gy = -2; gy <= 2; gy += 0.8) {
            const f = fieldAt(gx, gy);
            const m = Math.hypot(f.Ex, f.Ey) + 1e-6;
            const ux = f.Ex / m, uy = f.Ey / m;
            const px = xToPx(gx), py = h / 2 - gy * sx;
            ctx1.beginPath();
            ctx1.moveTo(px, py);
            ctx1.lineTo(px + ux * 16, py - uy * 16);
            ctx1.stroke();
          }
        }

        // charges
        charges.forEach((c) => {
          const px = xToPx(c.x), py = h / 2;
          ctx1.fillStyle = c.color;
          ctx1.beginPath(); ctx1.arc(px, py, 10, 0, Math.PI * 2); ctx1.fill();
          ctx1.fillStyle = "#fff"; ctx1.fillText(c.q >= 0 ? "+" : "-", px - 3, py + 4);
        });

        // probe x marker on main chart
        const probePx = xToPx(state.probeX);
        ctx1.setLineDash([5, 4]);
        ctx1.strokeStyle = "#ff9800";
        ctx1.beginPath(); ctx1.moveTo(probePx, 18); ctx1.lineTo(probePx, h - 18); ctx1.stroke();
        ctx1.setLineDash([]);
        ctx1.fillStyle = "#fff";
        ctx1.beginPath(); ctx1.arc(probePx, h / 2, 5, 0, Math.PI * 2); ctx1.fill();
        ctx1.fillStyle = "#ffcc80";
        ctx1.fillText(`probe x=${state.probeX.toFixed(2)}`, probePx + 8, 26);

        // potential line (1D)
        ctx2.strokeStyle = "#ffb74d"; ctx2.lineWidth = 2;
        ctx2.beginPath();
        for (let i = 0; i <= 600; i++) {
          const x = -5 + i / 600 * 10;
          let V = 0;
          charges.forEach((c) => { V += c.q / Math.sqrt((x - c.x) * (x - c.x) + 0.2); });
          const px = xToPx(x), py = h / 2 - V * 20;
          if (i === 0) ctx2.moveTo(px, py); else ctx2.lineTo(px, py);
        }
        ctx2.stroke();

        // probe point on Ex(x)
        const f = fieldAt(state.probeX, 0);
        const ppx = xToPx(state.probeX), ppy = h / 2 - f.Ex * 10;
        ctx2.fillStyle = "#4fc3f7";
        ctx2.beginPath(); ctx2.arc(ppx, ppy, 5, 0, Math.PI * 2); ctx2.fill();
        ctx2.fillStyle = "#ddd";
        ctx2.fillText(`Ex(probe)=${f.Ex.toFixed(3)}`, 16, h - 12);
      }
    },

    magnetic_field: {
      title: "磁场",
      animate: false,
      canvasCount: 2,
      controls: [
        { key: "I", label: "电流 I", min: -5, max: 5, step: 0.1, value: 3 },
        { key: "x", label: "观测点 x", min: -4, max: 4, step: 0.1, value: 2 },
        { key: "y", label: "观测点 y", min: -3, max: 3, step: 0.1, value: 1 }
      ],
      quiz: { q: "直导线周围磁场线形状是？", correct: "A", options: ["A. 同心圆", "B. 直线", "C. 抛物线", "D. 双曲线"] },
      describe(state) {
        const r = Math.hypot(state.x, state.y);
        const B = Math.abs(state.I) / (r + 0.2);
        return {
          line1: `电流 I=${state.I.toFixed(1)}，观测点=(${state.x.toFixed(1)},${state.y.toFixed(1)})`,
          line2: `磁感应强度近似 B∝I/r，当前 B≈${B.toFixed(3)}`,
          line3: "右手定则决定环绕方向"
        };
      },
      draw(canvases, state) {
        const [ctx1, ctx2, ctx3, w, h] = canvases;
        const cx = w / 2, cy = h / 2;
        [ctx1, ctx2, ctx3].forEach((c) => c.clearRect(0, 0, w, h));

        // wire and field circles
        ctx1.fillStyle = "#fff";
        ctx1.beginPath(); ctx1.arc(cx, cy, 10, 0, Math.PI * 2); ctx1.fill();
        ctx1.fillStyle = "#111";
        ctx1.fillText(state.I >= 0 ? "·" : "×", cx - 3, cy + 4);

        ctx1.strokeStyle = "#4fc3f7";
        for (let r = 24; r <= 92; r += 18) {
          ctx1.beginPath(); ctx1.arc(cx, cy, r, 0, Math.PI * 2); ctx1.stroke();
        }

        // arrows on circles
        const dir = state.I >= 0 ? -1 : 1;
        for (let r = 24; r <= 92; r += 34) {
          const ang = Math.PI / 4;
          const x = cx + r * Math.cos(ang), y = cy + r * Math.sin(ang);
          ctx1.strokeStyle = "#81c784";
          ctx1.beginPath();
          ctx1.moveTo(x, y);
          ctx1.lineTo(x + dir * -12 * Math.sin(ang), y + dir * 12 * Math.cos(ang));
          ctx1.stroke();
        }

        // mark observation point on main chart
        const opx = cx + state.x * 26, opy = cy - state.y * 26;
        ctx1.fillStyle = "#fff";
        ctx1.beginPath(); ctx1.arc(opx, opy, 5, 0, Math.PI * 2); ctx1.fill();
        ctx1.fillStyle = "#ffcc80";
        ctx1.fillText(`P(${state.x.toFixed(1)},${state.y.toFixed(1)})`, opx + 8, opy - 8);

        // vector field sample
        ctx2.strokeStyle = "#ffb74d";
        for (let gx = -4; gx <= 4; gx += 1) {
          for (let gy = -2.5; gy <= 2.5; gy += 1) {
            const r2 = gx * gx + gy * gy + 0.2;
            const k = state.I / r2;
            // tangent direction (-y, x)
            const vx = -gy * k, vy = gx * k;
            const m = Math.hypot(vx, vy) + 1e-6;
            const ux = vx / m, uy = vy / m;
            const px = cx + gx * 26, py = cy - gy * 26;
            ctx2.beginPath(); ctx2.moveTo(px, py); ctx2.lineTo(px + ux * 12, py - uy * 12); ctx2.stroke();
          }
        }

        // B(r) curve with current observation marker
        ctx2.strokeStyle = "#4fc3f7";
        ctx2.lineWidth = 2;
        ctx2.beginPath();
        for (let i = 0; i <= 400; i++) {
          const r = 0.2 + (i / 400) * 5;
          const Bv = Math.abs(state.I) / r;
          const px = 24 + (i / 400) * (w - 48);
          const py = h - 20 - Math.min(Bv, 6) / 6 * (h - 48);
          if (i === 0) ctx2.moveTo(px, py); else ctx2.lineTo(px, py);
        }
        ctx2.stroke();

        const rObs = Math.hypot(state.x, state.y);
        const bObs = Math.abs(state.I) / (rObs + 1e-6);
        const mx = 24 + (clamp(rObs, 0.2, 5) - 0.2) / 4.8 * (w - 48);
        const my = h - 20 - Math.min(bObs, 6) / 6 * (h - 48);
        ctx2.fillStyle = "#ffb74d";
        ctx2.beginPath(); ctx2.arc(mx, my, 5, 0, Math.PI * 2); ctx2.fill();
        ctx2.fillStyle = "#ddd";
        ctx2.fillText(`r=${rObs.toFixed(2)}, B≈${bObs.toFixed(2)}`, 16, 22);
      }
    },

    lorentz_force: {
      title: "洛伦兹力",
      animate: false,
      canvasCount: 2,
      controls: [
        { key: "q", label: "电荷 q", min: -3, max: 3, step: 0.1, value: 1 },
        { key: "v", label: "初速度 v", min: 1, max: 8, step: 0.1, value: 4 },
        { key: "B", label: "磁场 B", min: -3, max: 3, step: 0.1, value: 1.2 }
      ],
      quiz: { q: "在匀强磁场中 v⊥B 时，粒子做？", correct: "C", options: ["A. 匀速直线", "B. 匀加速直线", "C. 匀速圆周", "D. 抛体运动"] },
      describe(state) {
        const r = Math.abs(state.q * state.B) < 1e-6 ? 0 : state.v / Math.abs(state.q * state.B);
        return {
          line1: `q=${state.q.toFixed(1)}, v=${state.v.toFixed(1)}, B=${state.B.toFixed(1)}`,
          line2: `|F|=|q|vB≈${Math.abs(state.q * state.v * state.B).toFixed(3)}`,
          line3: `轨道半径 r≈${r.toFixed(3)}（m，单位化示意）`
        };
      },
      draw(canvases, state) {
        const [ctx1, ctx2, ctx3, w, h] = canvases;
        [ctx1, ctx2, ctx3].forEach((c) => c.clearRect(0, 0, w, h));
        const cx = w / 2, cy = h / 2;

        const q = state.q, v = state.v, B = state.B;
        const wb = q * B;
        const dt = 0.02;
        let x = -3.5, y = 0, vx = v, vy = 0;

        // trajectory under magnetic field only
        ctx1.strokeStyle = "#4fc3f7";
        ctx1.lineWidth = 2;
        ctx1.beginPath();
        for (let i = 0; i < 450; i++) {
          const ax = wb * vy;
          const ay = -wb * vx;
          vx += ax * dt; vy += ay * dt;
          x += vx * dt * 0.2; y += vy * dt * 0.2;
          const px = cx + x * 40, py = cy - y * 40;
          if (i === 0) ctx1.moveTo(px, py); else ctx1.lineTo(px, py);
        }
        ctx1.stroke();

        // B direction marks
        ctx1.fillStyle = "#aaa";
        for (let gx = 30; gx < w - 20; gx += 28) {
          for (let gy = 20; gy < h - 10; gy += 24) {
            ctx1.fillText(B >= 0 ? "·" : "×", gx, gy);
          }
        }

        // force vector relation panel
        ctx2.fillStyle = "#ddd";
        ctx2.fillText("速度 v 向右，磁场 B 垂直纸面，洛伦兹力 F 与 v 垂直", 16, 24);
        ctx2.strokeStyle = "#4fc3f7"; ctx2.lineWidth = 3;
        ctx2.beginPath(); ctx2.moveTo(90, h / 2); ctx2.lineTo(180, h / 2); ctx2.stroke();
        ctx2.strokeStyle = "#ff9800";
        ctx2.beginPath(); ctx2.moveTo(180, h / 2); ctx2.lineTo(180, h / 2 - Math.sign(wb || 1) * 70); ctx2.stroke();
        ctx2.fillStyle = "#4fc3f7"; ctx2.fillText("v", 185, h / 2 + 4);
        ctx2.fillStyle = "#ff9800"; ctx2.fillText("F", 185, h / 2 - Math.sign(wb || 1) * 72);

        // relation chart: r(v)=v/(|q|B) and current point
        ctx2.strokeStyle = "#81c784";
        ctx2.lineWidth = 1.8;
        ctx2.beginPath();
        const denom = Math.abs(q * B) + 1e-6;
        for (let i = 0; i <= 300; i++) {
          const vv = 0.2 + i / 300 * 8;
          const rr = vv / denom;
          const px = 24 + i / 300 * (w - 48);
          const py = h - 20 - Math.min(rr, 8) / 8 * (h - 48);
          if (i === 0) ctx2.moveTo(px, py); else ctx2.lineTo(px, py);
        }
        ctx2.stroke();
        const rNow = v / denom;
        const pxNow = 24 + (v - 0.2) / 8 * (w - 48);
        const pyNow = h - 20 - Math.min(rNow, 8) / 8 * (h - 48);
        ctx2.fillStyle = "#ffb74d";
        ctx2.beginPath(); ctx2.arc(pxNow, pyNow, 5, 0, Math.PI * 2); ctx2.fill();
        ctx2.fillStyle = "#ddd";
        ctx2.fillText(`r=v/(|q|B), 当前 r=${rNow.toFixed(3)}`, 16, h - 12);
      }
    },

    convex_lens_imaging: {
      title: "凸透镜成像",
      animate: false,
      canvasCount: 2,
      controls: [
        { key: "f", label: "焦距 f", min: 0.8, max: 3, step: 0.1, value: 1.5 },
        { key: "u", label: "物距 u", min: 1, max: 8, step: 0.1, value: 4.5 },
        { key: "h", label: "物高 h", min: 0.5, max: 3, step: 0.1, value: 1.8 }
      ],
      quiz: { q: "物体在 2f 外时，凸透镜成像通常为？", correct: "A", options: ["A. 倒立缩小实像", "B. 倒立放大实像", "C. 正立放大虚像", "D. 不成像"] },
      describe(state) {
        const u = state.u, f = state.f;
        const v = Math.abs(u - f) < 1e-6 ? Infinity : (u * f) / (u - f);
        const m = Number.isFinite(v) ? -v / u : 0;
        const type = !Number.isFinite(v) ? "平行光" : (v > 0 ? "实像" : "虚像");
        return {
          line1: `u=${u.toFixed(2)}, f=${f.toFixed(2)}, v=${Number.isFinite(v) ? v.toFixed(2) : "∞"}`,
          line2: `放大率 m=${m.toFixed(2)}，成像类型：${type}`,
          line3: "公式：1/f = 1/u + 1/v"
        };
      },
      draw(canvases, state) {
        const [ctx1, ctx2, ctx3, w, h] = canvases;
        [ctx1, ctx2, ctx3].forEach((c) => c.clearRect(0, 0, w, h));

        const axisY = h / 2;
        const lensX = w / 2;
        const scale = (w - 60) / 16;
        const u = state.u, f = state.f, hObj = state.h;
        const v = Math.abs(u - f) < 1e-6 ? Infinity : (u * f) / (u - f);
        const m = Number.isFinite(v) ? -v / u : 0;
        const hImg = m * hObj;

        function X(x) { return lensX + x * scale; }

        // Optical axis and lens
        ctx1.strokeStyle = "#666"; ctx1.lineWidth = 1.5;
        ctx1.beginPath(); ctx1.moveTo(20, axisY); ctx1.lineTo(w - 20, axisY); ctx1.stroke();
        ctx1.strokeStyle = "#4fc3f7"; ctx1.lineWidth = 3;
        ctx1.beginPath(); ctx1.moveTo(lensX, 30); ctx1.lineTo(lensX, h - 30); ctx1.stroke();

        // focal points
        ctx1.fillStyle = "#ff9800";
        [f, -f].forEach((ff) => { ctx1.beginPath(); ctx1.arc(X(ff), axisY, 4, 0, Math.PI * 2); ctx1.fill(); });
        ctx1.fillStyle = "#aaa"; ctx1.fillText("F", X(f) + 6, axisY - 6); ctx1.fillText("F'", X(-f) + 6, axisY - 6);

        // object
        const objX = X(-u), objTop = axisY - hObj * 30;
        ctx1.strokeStyle = "#81c784"; ctx1.lineWidth = 3;
        ctx1.beginPath(); ctx1.moveTo(objX, axisY); ctx1.lineTo(objX, objTop); ctx1.stroke();
        ctx1.fillStyle = "#81c784"; ctx1.fillText("物", objX - 10, objTop - 6);

        // principal rays
        ctx1.strokeStyle = "#ffb74d"; ctx1.lineWidth = 1.8;
        // ray 1 parallel then through focus
        ctx1.beginPath(); ctx1.moveTo(objX, objTop); ctx1.lineTo(lensX, objTop);
        if (Number.isFinite(v)) ctx1.lineTo(X(v), axisY + (objTop - axisY) * ((X(v) - lensX) / (X(f) - lensX)));
        ctx1.stroke();
        // ray 2 through center
        if (Number.isFinite(v)) {
          ctx1.beginPath(); ctx1.moveTo(objX, objTop); ctx1.lineTo(X(v), axisY - hImg * 30); ctx1.stroke();
        }

        // image
        if (Number.isFinite(v) && Math.abs(v) < 7.5) {
          const imgX = X(v), imgTop = axisY - hImg * 30;
          ctx1.strokeStyle = "#ef5350";
          ctx1.beginPath(); ctx1.moveTo(imgX, axisY); ctx1.lineTo(imgX, imgTop); ctx1.stroke();
          ctx1.fillStyle = "#ef5350"; ctx1.fillText("像", imgX + 6, imgTop + (hImg >= 0 ? -6 : 14));
        }

        // u-v curve
        ctx2.strokeStyle = "#4fc3f7"; ctx2.lineWidth = 2;
        ctx2.beginPath();
        for (let uu = f + 0.05; uu <= 8; uu += 0.03) {
          const vv = (uu * f) / (uu - f);
          const px = 30 + ((uu - 1) / 7) * (w - 60);
          const py = h - 24 - (vv / 8) * (h - 50);
          if (uu < f + 0.06) ctx2.moveTo(px, py); else ctx2.lineTo(px, py);
        }
        ctx2.stroke();
        ctx2.fillStyle = "#ddd";
        ctx2.fillText("u-v 关系曲线（u>f）", 16, 22);

        // m-u curve overlay with current point
        ctx2.strokeStyle = "#81c784";
        ctx2.lineWidth = 1.8;
        ctx2.beginPath();
        for (let uu = f + 0.05; uu <= 8; uu += 0.03) {
          const vv = (uu * f) / (uu - f);
          const mm = Math.abs(vv / uu);
          const px = 30 + ((uu - 1) / 7) * (w - 60);
          const py = h - 24 - Math.min(mm, 3) / 3 * (h - 50);
          if (uu < f + 0.06) ctx2.moveTo(px, py); else ctx2.lineTo(px, py);
        }
        ctx2.stroke();
        if (Number.isFinite(v)) {
          const px = 30 + ((u - 1) / 7) * (w - 60);
          const py = h - 24 - Math.min(Math.abs(m), 3) / 3 * (h - 50);
          ctx2.fillStyle = "#ffb74d";
          ctx2.beginPath(); ctx2.arc(px, py, 5, 0, Math.PI * 2); ctx2.fill();
        }
        ctx2.fillStyle = "#ddd";
        ctx2.fillText(`蓝: v-u 曲线, 绿: |m|-u 曲线, 当前 |m|=${Math.abs(m).toFixed(2)}`, 16, h - 10);
      }
    }
  };

  function boot() {
    const cfg = window.PRESET_CONFIG || {};
    const def = topicDefs[cfg.topic];
    if (!def) return;

    byId("pageTitle").textContent = cfg.title || def.title;
    byId("pageSubtitle").textContent = cfg.subtitle || "交互式深度学习页面";
    byId("knowledgeText").textContent = cfg.knowledgeText || "请结合图像和参数变化理解核心规律。";
    byId("formulaText").textContent = cfg.formulaText || "核心公式";

    const controlsWrap = byId("controls");
    controlsWrap.innerHTML = "";

    const state = { time: 0 };
    def.controls.forEach((c) => {
      state[c.key] = c.value;
      const div = document.createElement("div");
      div.className = "control-group";
      div.innerHTML = `<div class="control-label"><span>${c.label}</span><span class="control-value" id="val_${c.key}">${c.value}</span></div><input type="range" id="ctrl_${c.key}" min="${c.min}" max="${c.max}" step="${c.step}" value="${c.value}">`;
      controlsWrap.appendChild(div);
    });

    byId("quizQuestion").textContent = def.quiz.q;
    const quizOps = byId("quizOptions");
    quizOps.innerHTML = "";
    def.quiz.options.forEach((text, idx) => {
      const key = ["A", "B", "C", "D"][idx];
      const item = document.createElement("div");
      item.className = "quiz-option";
      item.setAttribute("data-a", key);
      item.textContent = text;
      quizOps.appendChild(item);
    });

    const c1 = byId("canvas1");
    const c2 = byId("canvas2");
    const c3 = byId("canvas3");

    const cards = document.querySelectorAll(".visual-card");
    const useCanvasCount = def.canvasCount || 3;
    if (useCanvasCount < 3 && cards[2]) {
      cards[2].style.display = "none";
    }

    let ctx1 = setupCanvas(c1), ctx2 = setupCanvas(c2), ctx3 = setupCanvas(c3);

    function redraw() {
      const w = c1.width / (window.devicePixelRatio || 1);
      const h = c1.height / (window.devicePixelRatio || 1);
      def.draw([ctx1, ctx2, ctx3, w, h], state);
      const d = def.describe(state);
      byId("status1").textContent = d.line1;
      byId("status2").textContent = d.line2;
      byId("status3").textContent = d.line3;
    }

    function bindControls() {
      def.controls.forEach((c) => {
        const el = byId(`ctrl_${c.key}`);
        el.addEventListener("input", (e) => {
          const v = parseFloat(e.target.value);
          state[c.key] = v;
          byId(`val_${c.key}`).textContent = v.toFixed(c.step >= 1 ? 0 : 2);
          redraw();
        });
      });
    }

    let running = !!def.animate;
    function loop() {
      state.time += 0.02;
      if (running) redraw();
      requestAnimationFrame(loop);
    }

    if (!def.animate) {
      byId("toggleBtn").style.display = "none";
    } else {
      byId("toggleBtn").addEventListener("click", () => {
        running = !running;
        byId("toggleBtn").textContent = running ? "暂停" : "继续";
      });
    }

    byId("resetBtn").addEventListener("click", () => {
      def.controls.forEach((c) => {
        state[c.key] = c.value;
        byId(`ctrl_${c.key}`).value = c.value;
        byId(`val_${c.key}`).textContent = c.value;
      });
      state.time = 0;
      redraw();
    });

    window.addEventListener("resize", () => {
      ctx1 = setupCanvas(c1);
      ctx2 = setupCanvas(c2);
      ctx3 = setupCanvas(c3);
      redraw();
    });

    let selected = null;
    function bindQuiz() {
      const options = document.querySelectorAll(".quiz-option");
      options.forEach((o) => {
        o.addEventListener("click", function () {
          options.forEach((x) => x.classList.remove("selected"));
          this.classList.add("selected");
          selected = this.getAttribute("data-a");
        });
      });
      byId("submitQuiz").addEventListener("click", () => {
        if (!selected) { alert("请先选择答案"); return; }
        const fb = byId("quizFeedback");
        const ft = byId("feedbackText");
        fb.style.display = "block";
        if (selected === def.quiz.correct) {
          ft.textContent = "回答正确，继续尝试改变参数观察规律。";
          ft.style.color = "#81c784";
        } else {
          ft.textContent = `回答不正确。正确答案是 ${def.quiz.correct}。`;
          ft.style.color = "#f44336";
        }
      });
    }

    bindControls();
    bindQuiz();
    redraw();
    if (def.animate) {
      loop();
    }
  }

  window.addEventListener("load", boot);
})();
