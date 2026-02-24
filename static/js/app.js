/**
 * =============================================================================
 * 项目名称: 绘演万象前端交互逻辑
 * 文件名称: app.js
 * 描述: 处理用户输入、与 Python 后端通信、实时渲染 iframe 以及界面状态管理。
 * =============================================================================
 */

let currentCode = "";
let isGenerating = false;

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function generatePage() {
  const promptInput = document.getElementById('userPrompt');
  const apiKeyInput = document.getElementById('apiKeyInput');
  const baseUrlInput = document.getElementById('baseUrlInput');
  const modelNameInput = document.getElementById('modelNameInput');
  const btn = document.getElementById('generateBtn');
  const status = document.getElementById('statusText');
  const editor = document.getElementById('codeEditor');

  const prompt = (promptInput?.value || "").trim();
  const apiKey = (apiKeyInput?.value || "").trim();
  const baseUrl = (baseUrlInput?.value || "").trim();
  const modelName = (modelNameInput?.value || "").trim();

  if (!apiKey) {
    alert("⚠️ 请先填写 API Key 才能启动引擎。");
    apiKeyInput?.focus();
    apiKeyInput.style.borderColor = "var(--error-color)";
    setTimeout(() => apiKeyInput.style.borderColor = "#444", 2000);
    return;
  }
  if (!prompt) {
    alert("⚠️ 指令为空：请输入你想生成的物理/数学演示内容。");
    promptInput?.focus();
    return;
  }
  if (!baseUrl || !modelName) {
    alert("⚠️ Base URL / Model Name 为空：请切换一次 Provider 或选择 Custom 填写。");
    return;
  }

  isGenerating = true;
  btn.disabled = true;
  btn.innerHTML = "⏳ 提交任务中...";
  status.innerHTML = `<span class="blink"></span>已提交任务 | 等待队列...`;
  editor.value = "// 已提交任务...\n// 正在排队/生成中...\n// 请稍候...";

  try {
    // 1) 提交任务（秒回 job_id）
    const resp = await fetch('/api/generate-html', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Client-Version': '1.0.0' },
      body: JSON.stringify({
        prompt: prompt,
        api_key: apiKey,
        base_url: baseUrl,
        model: modelName
      })
    });

    if (!resp.ok) {
      const t = await resp.text();
      throw new Error(`提交失败: HTTP ${resp.status} | ${t}`);
    }

    const data = await resp.json();
    const jobId = data.job_id;
    status.innerHTML = `<span class="blink"></span>任务已提交 | job_id: ${jobId}`;
    btn.innerHTML = "⏳ 生成中...";

    // 2) 轮询状态（避免外网 60s 超时）
    while (true) {
      await sleep(1500);

      const s = await fetch(`/api/html-status/${jobId}`);
      if (!s.ok) {
        const t = await s.text();
        throw new Error(`查询失败: HTTP ${s.status} | ${t}`);
      }

      const st = await s.json();

      if (st.status === "done") {
        currentCode = st.html || "";
        editor.value = currentCode;
        updatePreview(currentCode);

        status.innerHTML =
          `<span class="blink" style="background:var(--success-color);"></span>` +
          `生成完毕 | 已归档: ${st.saved_path || "N/A"}`;
        break;
      }

      if (st.status === "error") {
        const msg = st.error || "未知错误";
        status.innerHTML = `<span style="color:var(--error-color)">❌ 生成失败: ${msg}</span>`;
        editor.value = `/*\n生成失败\nError: ${msg}\n*/`;
        break;
      }

      // queued / running
      status.innerHTML = `<span class="blink"></span>生成中 (${st.status}) | job_id: ${jobId}`;
    }

  } catch (e) {
    console.error("[System Error]", e);
    status.innerHTML = `<span style="color:var(--error-color)">❌ 生成中断: ${e.message}</span>`;
    editor.value = `/*\n系统发生错误\nError: ${e.message}\n*/`;

    if (String(e.message || "").includes("401")) {
      alert("认证失败：API Key 无效，请检查。");
    }
  } finally {
    isGenerating = false;
    btn.disabled = false;
    btn.innerHTML = "🚀 启动生成";
  }
}

function applyCode() {
  const editor = document.getElementById('codeEditor');
  const status = document.getElementById('statusText');

  currentCode = editor.value;
  updatePreview(currentCode);

  status.innerHTML =
    `<span class="blink" style="background:var(--warning-color);"></span>` +
    `开发者模式 | 已应用手动修改`;
}

function updatePreview(code) {
  const iframe = document.getElementById('previewFrame');
  iframe.srcdoc = code;

  const container = iframe?.closest('.iframe-container');
  if (container) container.classList.add('has-content');
}

window.addEventListener('DOMContentLoaded', () => {
  console.log("Huiyan Engine Frontend Ready.");
});

/**
 * 生成 Manim 视频（你原来的逻辑可以保留）
 * 这里不动，只要你的后端 manim_engine/router.py 正常即可
 */
async function generateVideo() {
  const promptInput = document.getElementById('userPrompt');
  const apiKeyInput = document.getElementById('apiKeyInput');
  const baseUrlInput = document.getElementById('baseUrlInput');
  const modelNameInput = document.getElementById('modelNameInput');

  const btn = document.getElementById('generateVideoBtn');
  const status = document.getElementById('videoStatus');
  const player = document.getElementById('videoPlayer');
  const link = document.getElementById('videoOpenLink');

  if (!status || !player || !link) {
    alert("前端缺少视频面板元素：请确认 index.html 已加入 videoStatus/videoPlayer/videoOpenLink。");
    return;
  }

  const prompt = (promptInput?.value || "").trim();
  const apiKey = (apiKeyInput?.value || "").trim();
  const baseUrl = (baseUrlInput?.value || "").trim();
  const modelName = (modelNameInput?.value || "").trim();

  if (!apiKey) { alert("⚠️ 请先填写 API Key 才能生成视频。"); apiKeyInput?.focus(); return; }
  if (!prompt) { alert("⚠️ 请输入指令（Prompt）。"); promptInput?.focus(); return; }
  if (!baseUrl || !modelName) { alert("⚠️ Base URL / Model Name 为空：请切换 Provider 或选择 Custom。"); return; }

  btn.disabled = true;
  btn.innerHTML = "⏳ 渲染中...";

  status.textContent = "状态：已提交渲染任务，等待队列…";
  player.removeAttribute("src");
  player.load();
  link.style.display = "none";
  link.href = "#";

  try {
    const resp = await fetch('/api/generate-video', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt, api_key: apiKey, base_url: baseUrl, model: modelName,
        duration: 12.0, quality: "m", fps: 30, resolution: "1280,720"
      })
    });

    if (!resp.ok) {
      const t = await resp.text();
      throw new Error(`提交失败: HTTP ${resp.status} | ${t}`);
    }

    const data = await resp.json();
    const jobId = data.job_id;
    status.textContent = `状态：任务已提交\njob_id: ${jobId}\n正在渲染（请勿关闭页面）…`;

    while (true) {
      await sleep(1500);

      const s = await fetch(`/api/video-status/${jobId}`);
      if (!s.ok) {
        const t = await s.text();
        throw new Error(`查询失败: HTTP ${s.status} | ${t}`);
      }

      const st = await s.json();

      if (st.status === "done") {
        status.textContent = `状态：完成 ✅\n输出: ${st.video_url}`;
        player.src = st.video_url;
        player.load();

        link.href = st.video_url;
        link.style.display = "inline";
        break;
      }

      if (st.status === "error") {
        status.textContent = `状态：失败 ❌\n${st.stderr_tail || ""}`;
        alert("视频生成失败：请查看下方日志（stderr_tail）。");
        break;
      }

      const tail = st.stderr_tail ? `\n--- stderr_tail ---\n${st.stderr_tail}` : "";
      status.textContent = `状态：${st.status}\njob_id: ${jobId}${tail}`;
    }
  } catch (e) {
    console.error(e);
    status.textContent = `状态：异常 ❌\n${e?.message || e}`;
    alert(`视频生成异常：${e?.message || e}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = "🎬 生成视频";
  }
}
