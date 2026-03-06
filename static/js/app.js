/**
 * HuiyanWanxiang - Klu-like Console Frontend
 * Endpoints:
 * - POST /api/generate-html -> {status, job_id}
 * - GET  /api/html-status/{job_id} -> {status, html, download_url, error}
 * - GET  /api/html-download/{job_id} -> file
 * - POST /api/generate-video -> {status, job_id}
 * - GET  /api/video-status/{job_id} -> {status, video_url, stderr_tail}
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

function showStatus(text){
  const box = $("statusText");
  if(box) box.textContent = text;
}

function getOptimizePayload(){
  const hint = ($("optHint")?.value || "").trim();
  return { optimize: promptOptimizeEnabled, optimize_hint: hint };
}

/* -------- Provider presets -> hidden baseUrlInput/modelNameInput -------- */
function applyProviderPreset(provider){
  const baseUrlHidden = $("baseUrlInput");
  const modelHidden = $("modelNameInput");
  if(!baseUrlHidden || !modelHidden) return;

  if(provider === "deepseek"){
    baseUrlHidden.value = "https://api.deepseek.com";
    modelHidden.value = "deepseek-coder";
  }else if(provider === "openai"){
    baseUrlHidden.value = "https://api.openai.com/v1";
    modelHidden.value = "gpt-4o-mini";
  }else if(provider === "moonshot"){
    baseUrlHidden.value = "https://api.moonshot.cn/v1";
    modelHidden.value = "moonshot-v1-8k";
  }else if(provider === "aliyun"){
    baseUrlHidden.value = "https://dashscope.aliyuncs.com/compatible-mode/v1";
    modelHidden.value = "qwen-plus";
  }else{
    // custom: user will input in visible custom fields
  }
}

function syncCustomVisibleToHidden(){
  const baseV = $("baseUrlInputVisible");
  const modelV = $("modelNameInputVisible");
  const baseH = $("baseUrlInput");
  const modelH = $("modelNameInput");
  if(baseV && baseH) baseH.value = (baseV.value || "").trim();
  if(modelV && modelH) modelH.value = (modelV.value || "").trim();
}

function setCustomRowsVisible(isVisible){
  const rows = $("customRows");
  if(rows) rows.style.display = isVisible ? "grid" : "none";
}

/* -------- Optimizer Switch -------- */
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

/* -------- Demo -------- */
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

/* -------- Update Editor + Embedded Preview -------- */
function updateOutputs(html){
  currentCode = html || "";
  const editor = $("codeEditor");
  if(editor) editor.value = currentCode;

  const embed = $("embeddedFrame");
  if(embed) embed.srcdoc = currentCode;

  setTag("editorPill", "已更新");
  setTag("embedPill", "已嵌入");
}

function applyEditor(){
  const editor = $("codeEditor");
  if(!editor) return;
  updateOutputs(editor.value);
  showStatus("开发者模式：已手动运行编辑器内容（已刷新嵌入预览）。");
}

/* -------- Download -------- */
function downloadHtml(){
  const url = window.__last_html_download_url
    || (window.__last_html_job_id ? `/api/html-download/${window.__last_html_job_id}` : null);

  if(!url){
    alert("暂无可下载的网页：请先生成 HTML。");
    return;
  }
  window.location.href = url;
}

/* -------- Generate HTML -------- */
async function generateHtml(){
  const prompt = ($("userPrompt")?.value || "").trim();
  const apiKey = ($("apiKeyInput")?.value || "").trim();
  const provider = ($("providerSelect")?.value || "deepseek").trim();

  if(provider === "custom") syncCustomVisibleToHidden();
  const baseUrl = ($("baseUrlInput")?.value || "").trim();
  const model = ($("modelNameInput")?.value || "").trim();

  if(!apiKey){ alert("请填写 API Key"); $("apiKeyInput")?.focus(); return; }
  if(!prompt){ alert("请输入 Prompt"); $("userPrompt")?.focus(); return; }
  if(!baseUrl || !model){
    alert("Base URL / Model 不能为空（custom 请填写）");
    return;
  }

  const genBtn = $("generateBtn");
  const dlBtn = $("downloadHtmlBtn");
  if(genBtn) genBtn.disabled = true;
  if(dlBtn) dlBtn.disabled = true;

  window.__last_html_job_id = null;
  window.__last_html_download_url = null;

  setTag("editorPill","生成中…");
  setTag("embedPill","生成中…");
  showStatus("已提交任务：等待队列…");

  try{
    const resp = await fetch("/api/generate-html", {
      method:"POST",
      headers: {"Content-Type":"application/json","X-Client-Version":"3.0.0"},
      body: JSON.stringify({
        prompt,
        api_key: apiKey,
        base_url: baseUrl,
        model,
        ...getOptimizePayload()
      })
    });

    if(!resp.ok){
      const t = await resp.text().catch(()=> "");
      throw new Error(`提交失败 HTTP ${resp.status} | ${t}`);
    }
    const data = await resp.json();
    const jobId = data.job_id;
    window.__last_html_job_id = jobId;

    showStatus(`任务已提交：job_id=${jobId}，生成中…`);
    if(genBtn) genBtn.textContent = "生成中…";

    while(true){
      await sleep(1500);
      const s = await fetch(`/api/html-status/${jobId}`);
      if(!s.ok){
        const t = await s.text().catch(()=> "");
        throw new Error(`查询失败 HTTP ${s.status} | ${t}`);
      }
      const st = await s.json();

      if(st.status === "done"){
        updateOutputs(st.html || "");
        if(st.download_url) window.__last_html_download_url = st.download_url;
        if(dlBtn) dlBtn.disabled = false;
        showStatus("生成完毕 ✅ 已写入编辑器并嵌入预览，可下载 HTML。");
        break;
      }
      if(st.status === "error"){
        setTag("editorPill","失败");
        setTag("embedPill","失败");
        showStatus(`生成失败 ❌ ${st.error || "未知错误"}`);
        const editor = $("codeEditor");
        if(editor) editor.value = `/*\n生成失败\n${st.error || ""}\n*/`;
        break;
      }
      showStatus(`生成中 (${st.status}) … job_id=${jobId}`);
    }

  }catch(e){
    console.error(e);
    setTag("editorPill","异常");
    setTag("embedPill","异常");
    showStatus(`生成中断 ❌ ${e.message || e}`);
  }finally{
    if(genBtn){
      genBtn.disabled = false;
      genBtn.textContent = "生成 HTML 页面";
    }
  }
}

/* -------- Generate Video -------- */
async function generateVideo(){
  const prompt = ($("userPrompt")?.value || "").trim();
  const apiKey = ($("apiKeyInput")?.value || "").trim();
  const provider = ($("providerSelect")?.value || "deepseek").trim();

  if(provider === "custom") syncCustomVisibleToHidden();
  const baseUrl = ($("baseUrlInput")?.value || "").trim();
  const model = ($("modelNameInput")?.value || "").trim();

  if(!apiKey){ alert("请填写 API Key"); $("apiKeyInput")?.focus(); return; }
  if(!prompt){ alert("请输入 Prompt"); $("userPrompt")?.focus(); return; }
  if(!baseUrl || !model){
    alert("Base URL / Model 不能为空（custom 请填写）");
    return;
  }

  const btn = $("generateVideoBtn");
  const pill = $("videoPill");
  const status = $("videoStatus");
  const player = $("videoPlayer");
  const link = $("videoOpenLink");

  if(btn) btn.disabled = true;
  if(pill) pill.textContent = "提交中…";
  if(status) status.textContent = "状态：已提交渲染任务，等待队列…";
  if(player){ player.removeAttribute("src"); player.load(); }
  if(link){ link.style.display="none"; link.href="#"; }

  try{
    const resp = await fetch("/api/generate-video", {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({
        prompt, api_key: apiKey, base_url: baseUrl, model,
        duration: 12.0, quality:"m", fps:30, resolution:"1280,720",
        ...getOptimizePayload()
      })
    });
    if(!resp.ok){
      const t = await resp.text().catch(()=> "");
      throw new Error(`提交失败 HTTP ${resp.status} | ${t}`);
    }
    const data = await resp.json();
    const jobId = data.job_id;

    if(pill) pill.textContent = "生成中…";
    if(status) status.textContent = `状态：任务已提交\njob_id: ${jobId}\n正在渲染…`;

    while(true){
      await sleep(1500);
      const s = await fetch(`/api/video-status/${jobId}`);
      if(!s.ok){
        const t = await s.text().catch(()=> "");
        throw new Error(`查询失败 HTTP ${s.status} | ${t}`);
      }
      const st = await s.json();

      if(st.status === "done"){
        if(pill) pill.textContent = "已完成";
        if(status) status.textContent = `状态：完成 ✅\n输出: ${st.video_url || ""}`;
        if(st.video_url && player){
          player.src = st.video_url;
          player.load();
        }
        if(st.video_url && link){
          link.href = st.video_url;
          link.style.display = "inline-block";
        }
        break;
      }

      if(st.status === "error"){
        if(pill) pill.textContent = "失败";
        if(status) status.textContent = `状态：失败 ❌\n${st.stderr_tail || ""}`;
        alert("视频生成失败：请查看日志。");
        break;
      }

      if(pill) pill.textContent = `进行中…`;
      const tail = st.stderr_tail ? `\n--- stderr_tail ---\n${st.stderr_tail}` : "";
      if(status) status.textContent = `状态：${st.status}\njob_id: ${jobId}${tail}`;
    }

  }catch(e){
    console.error(e);
    if(pill) pill.textContent = "异常";
    if(status) status.textContent = `状态：异常 ❌\n${e.message || e}`;
    alert(`视频生成异常：${e.message || e}`);
  }finally{
    if(btn) btn.disabled = false;
  }
}

/* -------- init -------- */
window.addEventListener("DOMContentLoaded", ()=>{
  const provider = $("providerSelect");
  if(provider){
    // init preset
    if(provider.value !== "custom") applyProviderPreset(provider.value);

    provider.addEventListener("change", ()=>{
      const isCustom = provider.value === "custom";
      setCustomRowsVisible(isCustom);

      if(!isCustom){
        applyProviderPreset(provider.value);
      }else{
        // sensible defaults for custom
        const baseV = $("baseUrlInputVisible");
        const modelV = $("modelNameInputVisible");
        if(baseV && !baseV.value) baseV.value = "https://api.deepseek.com";
        if(modelV && !modelV.value) modelV.value = "deepseek-coder";
        syncCustomVisibleToHidden();
      }
    });
  }

  // keep visible->hidden in sync for custom
  $("baseUrlInputVisible")?.addEventListener("input", syncCustomVisibleToHidden);
  $("modelNameInputVisible")?.addEventListener("input", syncCustomVisibleToHidden);

  // buttons
  $("btnFillDemo")?.addEventListener("click", fillDemo);
  $("generateBtn")?.addEventListener("click", generateHtml);
  $("downloadHtmlBtn")?.addEventListener("click", downloadHtml);
  $("applyBtn")?.addEventListener("click", applyEditor);
  $("generateVideoBtn")?.addEventListener("click", generateVideo);

  // optimizer
  bindOptimizerSwitch();

  // init embedded area (clean placeholder)
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
});