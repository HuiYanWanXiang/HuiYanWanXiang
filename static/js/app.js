/**
 * YiYanKeTang Console Frontend
 * 已改为：
 * - 前端不再输入 API Key
 * - 使用登录 token 访问后端
 * - 自动获取当前用户信息与剩余次数
 * - HTML / Video 生成统一走鉴权
 * - 新增：预设场景优先匹配，命中则秒开
 */

let currentCode = "";
let promptOptimizeEnabled = false;

window.__last_html_job_id = null;
window.__last_html_download_url = null;

const $ = (id) => document.getElementById(id);
function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }

function setTag(id, text){
  const el = $(id);
  if (el) el.textContent = text;
}

function toggleRootOnlyFeature(isRoot){
  const nav = $("rootOnlyNav");
  const btn = $("rootOnlyBtn");
  const videoWallNav = $("rootOnlyVideoWallNav");
  const videoWallBtn = $("rootOnlyVideoWallBtn");
  const display = isRoot ? "" : "none";

  if(nav) nav.style.display = display;
  if(btn) btn.style.display = display;
  if(videoWallNav) videoWallNav.style.display = display;
  if(videoWallBtn) videoWallBtn.style.display = display;
}

function showStatus(text){
  const box = $("statusText");
  if(box) box.textContent = text;
}

function getOptimizePayload(){
  const hint = ($("optHint")?.value || "").trim();
  return {
    optimize: promptOptimizeEnabled,
    optimize_hint: hint
  };
}

/* ---------------- Auth ---------------- */
function getToken(){
  return localStorage.getItem("token") || "";
}

function logout(){
  localStorage.removeItem("token");
  window.location.href = "/";
}

function authHeaders(){
  const token = getToken();
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  };
}

async function loadMe(){
  const token = getToken();
  if(!token){
    window.location.href = "/";
    return null;
  }

  try{
    const resp = await fetch("/api/auth/me", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    const data = await resp.json().catch(() => ({}));

    if(!resp.ok){
      localStorage.removeItem("token");
      window.location.href = "/";
      return null;
    }

    const userInfoText = $("userInfoText");
    const quotaText = $("quotaText");
    const usernameText = $("usernameText");
    
    if(userInfoText){
      userInfoText.textContent = data.is_root
        ? `当前用户：${data.username}（root）`
        : `当前用户：${data.username}`;
    }
    
    if(usernameText){
      usernameText.textContent = data.is_root
        ? `${data.username}（管理员）`
        : data.username;
    }
    
    if(quotaText){
      quotaText.textContent = data.is_root
        ? "当前账号为 root，使用次数无限制"
        : `剩余次数：${data.remaining_count}/${data.free_quota}`;
    }

    toggleRootOnlyFeature(!!data.is_root);

    return data;
  }catch(err){
    console.error("loadMe error:", err);
    localStorage.removeItem("token");
    window.location.href = "/";
    return null;
  }
}

/* ---------------- Optimizer Switch ---------------- */
function bindOptimizerSwitch(){
  const sw = $("optSwitch");
  if(!sw) return;

  const setOn = (on)=>{
    promptOptimizeEnabled = !!on;
    sw.classList.toggle("on", promptOptimizeEnabled);
    sw.setAttribute("aria-checked", promptOptimizeEnabled ? "true":"false");
  };

  setOn(false);
  sw.addEventListener("click", ()=> setOn(!promptOptimizeEnabled));
}

/* ---------------- Demo ---------------- */
function fillDemo(){
  const p = $("userPrompt");
  const opt = $("optHint");

  if(p){
    p.value = "请生成一个面向高中生的可交互网页：主题是“阻尼振动与受迫振动”。要求包含：参数滑条（阻尼系数、驱动力幅值、驱动频率）、位移-时间曲线、相图，以及简短的概念解释和一个小测验。页面风格简洁、信息密度高。";
  }

  if(opt){
    opt.value = "输出必须包含：1) 结构化标题与小节 2) 互动控件与默认值 3) 图表用 Canvas/SVG 4) 末尾小测验（答案折叠）。";
  }

  showStatus("已填充示例。现在可以点击「生成 HTML 页面」。");
}

/* ---------------- Editor + Embedded Preview ---------------- */
function updateOutputs(html){
  currentCode = html || "";

  const editor = $("codeEditor");
  if(editor) editor.value = currentCode;

  const embed = $("embeddedFrame");
  if(embed){
    embed.removeAttribute("src");
    embed.srcdoc = currentCode;
  }

  setTag("editorPill", "已更新");
  setTag("embedPill", "已嵌入");
}

function applyEditor(){
  const editor = $("codeEditor");
  if(!editor) return;

  updateOutputs(editor.value);
  showStatus("开发者模式：已手动运行编辑器内容（已刷新嵌入预览）。");
}

/* ---------------- Preset Match ---------------- */
async function checkPresetMatch(prompt){
  const resp = await fetch("/api/preset-match", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ prompt })
  });

  const data = await resp.json().catch(() => ({}));

  if(!resp.ok){
    throw new Error(data.detail || `预设匹配失败 HTTP ${resp.status}`);
  }

  return data;
}

async function loadPresetResult(preset){
  const embed = $("embeddedFrame");
  const player = $("videoPlayer");
  const link = $("videoOpenLink");
  const editor = $("codeEditor");
  const dlBtn = $("downloadHtmlBtn");

  currentCode = "";

  if(embed){
    embed.removeAttribute("srcdoc");
    if(preset.html_url){
      embed.src = `${preset.html_url}?t=${Date.now()}`;
    }
  }

  if(player){
    if(preset.video_url){
      player.src = `${preset.video_url}?t=${Date.now()}`;
      player.load();
    }else{
      player.removeAttribute("src");
      player.load();
    }
  }

  if(link){
    if(preset.video_url){
      link.href = `${preset.video_url}?t=${Date.now()}`;
      link.style.display = "inline-block";
    }else{
      link.style.display = "none";
      link.href = "#";
    }
  }

  if(editor){
    editor.value =
`// 当前命中预设场景：${preset.title}
// 匹配方式：${preset.match_type || "preset"}
// 置信分数：${preset.score ?? ""}
// HTML: ${preset.html_url || ""}
// Video: ${preset.video_url || ""}

// 当前为预设模式，右侧 iframe 已直接加载静态页面。
// 若要查看源码，请直接打开对应的 /static/presets/.../index.html 文件。`;
  }

  if(dlBtn){
    dlBtn.disabled = true;
  }

  window.__last_html_job_id = null;
  window.__last_html_download_url = null;

  setTag("editorPill", "预设模式");
  setTag("embedPill", "预设已加载");
  setTag("videoPill", preset.video_url ? "预设已加载" : "无预设视频");

  showStatus(`已匹配预设场景：${preset.title}，正在秒级加载交互网页与视频…`);
}

/* ---------------- Download HTML ---------------- */
function downloadHtml(){
  const url = window.__last_html_download_url
    || (window.__last_html_job_id ? `/api/html-download/${window.__last_html_job_id}` : null);

  if(!url){
    alert("暂无可下载的网页：请先生成 HTML。");
    return;
  }

  downloadHtmlWithToken(url);
}

async function downloadHtmlWithToken(url){
  try{
    const resp = await fetch(url, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${getToken()}`
      }
    });

    if(!resp.ok){
      const data = await resp.text().catch(() => "");
      throw new Error(data || `下载失败 HTTP ${resp.status}`);
    }

    const blob = await resp.blob();
    const objectUrl = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = "yiyanketang_generated.html";
    document.body.appendChild(a);
    a.click();
    a.remove();

    URL.revokeObjectURL(objectUrl);
  }catch(e){
    console.error(e);
    alert(`下载失败：${e.message || e}`);
  }
}

/* ---------------- Generate HTML ---------------- */
async function generateHtml(){
  const prompt = ($("userPrompt")?.value || "").trim();

  if(!prompt){
    alert("请输入 Prompt");
    $("userPrompt")?.focus();
    return;
  }

  const genBtn = $("generateBtn");
  const dlBtn = $("downloadHtmlBtn");

  if(genBtn) genBtn.disabled = true;
  if(dlBtn) dlBtn.disabled = true;

  try{
    showStatus("正在识别是否命中预设场景…");

    // 1) 先查预设
    const preset = await checkPresetMatch(prompt);

    if(preset.matched){
      await loadPresetResult(preset);
      return;
    }

    // 2) 没命中预设，走原有生成逻辑
    window.__last_html_job_id = null;
    window.__last_html_download_url = null;

    setTag("editorPill","生成中…");
    setTag("embedPill","生成中…");
    showStatus("未命中预设，已提交任务：等待队列…");

    const resp = await fetch("/api/generate-html", {
      method:"POST",
      headers: authHeaders(),
      body: JSON.stringify({
        prompt,
        ...getOptimizePayload()
      })
    });

    const data = await resp.json().catch(() => ({}));

    if(!resp.ok){
      throw new Error(data.detail || `提交失败 HTTP ${resp.status}`);
    }

    const jobId = data.job_id;
    window.__last_html_job_id = jobId;

    showStatus(`任务已提交：job_id=${jobId}，生成中…`);
    if(genBtn) genBtn.textContent = "生成中…";

    while(true){
      await sleep(1500);

      const s = await fetch(`/api/html-status/${jobId}`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${getToken()}`
        }
      });

      const st = await s.json().catch(() => ({}));

      if(!s.ok){
        throw new Error(st.detail || `查询失败 HTTP ${s.status}`);
      }

      if(st.status === "done"){
        updateOutputs(st.html || "");

        if(st.download_url){
          window.__last_html_download_url = st.download_url;
        }

        if(dlBtn) dlBtn.disabled = false;

        showStatus("生成完毕 ✅ 已写入编辑器并嵌入预览，可下载 HTML。");
        await loadMe();
        break;
      }

      if(st.status === "error"){
        setTag("editorPill","失败");
        setTag("embedPill","失败");
        showStatus(`生成失败 ❌ ${st.error || "未知错误"}`);

        const editor = $("codeEditor");
        if(editor){
          editor.value = `/*\n生成失败\n${st.error || ""}\n*/`;
        }
        break;
      }

      showStatus(`生成中 (${st.status}) … job_id=${jobId}`);
    }

  }catch(e){
    console.error(e);
    setTag("editorPill","异常");
    setTag("embedPill","异常");
    showStatus(`生成中断 ❌ ${e.message || e}`);
    alert(e.message || e);
  }finally{
    if(genBtn){
      genBtn.disabled = false;
      genBtn.textContent = "生成 HTML 页面";
    }
  }
}

/* ---------------- Generate Video ---------------- */
async function generateVideo(){
  const prompt = ($("userPrompt")?.value || "").trim();

  if(!prompt){
    alert("请输入 Prompt");
    $("userPrompt")?.focus();
    return;
  }

  const btn = $("generateVideoBtn");
  const pill = $("videoPill");
  const player = $("videoPlayer");
  const link = $("videoOpenLink");

  if(btn) btn.disabled = true;
  if(pill) pill.textContent = "识别中…";

  try{
    showStatus("正在识别是否命中预设视频…");

    const preset = await checkPresetMatch(prompt);

    if(preset.matched && preset.video_url){
      if(player){
        player.src = `${preset.video_url}?t=${Date.now()}`;
        player.load();
      }

      if(link){
        link.href = `${preset.video_url}?t=${Date.now()}`;
        link.style.display = "inline-block";
      }

      if(pill) pill.textContent = "预设已加载";
      showStatus(`已匹配预设场景：${preset.title}，已秒级加载视频。`);
      return;
    }

    // 没命中预设，走原有视频生成逻辑
    if(player){
      player.removeAttribute("src");
      player.load();
    }

    if(link){
      link.style.display = "none";
      link.href = "#";
    }

    showStatus("视频任务已提交，等待渲染…");

    const resp = await fetch("/api/generate-video", {
      method:"POST",
      headers: authHeaders(),
      body: JSON.stringify({
        prompt,
        duration: 12.0,
        quality: "m",
        fps: 30,
        resolution: "1280,720",
        ...getOptimizePayload()
      })
    });

    const data = await resp.json().catch(() => ({}));

    if(!resp.ok){
      throw new Error(data.detail || data.error || `提交失败 HTTP ${resp.status}`);
    }

    const jobId = data.job_id;
    if(pill) pill.textContent = "生成中…";
    showStatus(`视频任务已提交：job_id=${jobId}，正在渲染…`);

    while(true){
      await sleep(1500);

      const s = await fetch(`/api/video-status/${jobId}`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${getToken()}`
        }
      });

      const st = await s.json().catch(() => ({}));

      if(!s.ok){
        throw new Error(st.detail || st.error || `查询失败 HTTP ${s.status}`);
      }

      if(st.status === "done"){
        if(pill) pill.textContent = "已完成";

        if(st.video_url && player){
          player.src = st.video_url;
          player.load();
        }

        if(st.video_url && link){
          link.href = st.video_url;
          link.style.display = "inline-block";
        }

        showStatus("视频生成完成 ✅");
        await loadMe();
        break;
      }

      if(st.status === "error"){
        if(pill) pill.textContent = "失败";
        showStatus(`视频生成失败 ❌ ${st.stderr_tail || ""}`);
        alert("视频生成失败，请查看日志或稍后重试。");
        break;
      }

      if(pill) pill.textContent = "进行中…";
      showStatus(`视频渲染中 (${st.status}) … job_id=${jobId}`);
    }

  }catch(e){
    console.error(e);
    if(pill) pill.textContent = "异常";
    showStatus(`视频生成异常 ❌ ${e.message || e}`);
    alert(`视频生成异常：${e.message || e}`);
  }finally{
    if(btn) btn.disabled = false;
  }
}

/* ---------------- Init ---------------- */
window.addEventListener("DOMContentLoaded", async () => {
  // 1. 先校验登录态
  await loadMe();

  // 2. 绑定按钮
  $("btnFillDemo")?.addEventListener("click", fillDemo);
  $("generateBtn")?.addEventListener("click", generateHtml);
  $("downloadHtmlBtn")?.addEventListener("click", downloadHtml);
  $("applyBtn")?.addEventListener("click", applyEditor);
  $("generateVideoBtn")?.addEventListener("click", generateVideo);
  $("logoutBtn")?.addEventListener("click", logout);

  // 3. 提示词优化开关
  bindOptimizerSwitch();

  // 4. 初始化嵌入区域
  const blank = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    html,body{height:100%;margin:0}
    body{background:#0b0f14;display:flex;align-items:center;justify-content:center}
    .tip{border:1px dashed rgba(255,255,255,.12);border-radius:14px;padding:16px 18px;background:rgba(0,0,0,.25);color:rgba(200,220,255,.55);font:13px system-ui}
  </style></head><body><div class="tip">嵌入预览区域（生成/手动运行后自动填充）</div></body></html>`;

  if($("embeddedFrame")) $("embeddedFrame").srcdoc = blank;

  setTag("editorPill","等待生成…");
  setTag("embedPill","等待生成…");
  setTag("videoPill","等待任务…");

  if($("downloadHtmlBtn")) $("downloadHtmlBtn").disabled = true;

  showStatus("READY. 输入 Prompt 后点击「生成 HTML 页面」。");
});