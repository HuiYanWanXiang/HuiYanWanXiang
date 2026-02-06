let currentCode = "";

async function generatePage() {
    const prompt = document.getElementById('userPrompt').value;
    const apiKey = document.getElementById('apiKeyInput').value;
    const baseUrl = document.getElementById('baseUrlInput').value;
    const modelName = document.getElementById('modelNameInput').value;
    
    const btn = document.getElementById('generateBtn');
    const status = document.getElementById('statusText');
    const editor = document.getElementById('codeEditor');
    
    // 1. 校验 Key 是否填写
    if (!apiKey) {
        alert("⚠️ 请先在左上角填写您的 API Key！\n\n如果没有，请去 DeepSeek 或 Kimi 官网申请。");
        document.getElementById('apiKeyInput').focus();
        return;
    }
    
    if (!prompt) { alert("请下达指令！"); return; }

    btn.disabled = true;
    status.innerHTML = `<span class="blink"></span>正在连接 ${modelName} 模型...`;
    editor.value = "// 正在发送请求...";

    try {
        // 2. 发送完整的数据包 (Payload)
        const response = await fetch('/api/generate-html', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                prompt: prompt,
                api_key: apiKey,     // 用户的 Key
                base_url: baseUrl,   // 用户的 URL
                model: modelName     // 用户的模型名
            })
        });

        const data = await response.json();

        if (data.html) {
            currentCode = data.html;
            editor.value = currentCode; 
            updatePreview(currentCode);
            status.innerHTML = `<span class="blink" style="background:#0f0;"></span>生成完毕 | 已存档`;
        } else {
            status.innerHTML = `<span style="color:red">ERROR: ${data.error}</span>`;
            // 如果是 401 错误，提示用户检查 Key
            if (data.error && data.error.includes("401")) {
                alert("认证失败！请检查您的 API Key 是否正确。");
            }
        }
    } catch (e) {
        console.error(e);
        status.innerText = "网络连接中断";
    } finally {
        btn.disabled = false;
    }
}

function applyCode() {
    const editor = document.getElementById('codeEditor');
    const status = document.getElementById('statusText');
    currentCode = editor.value;
    updatePreview(currentCode);
    status.innerHTML = `<span class="blink" style="background:#fa0;"></span>已应用手动修改`;
}

function updatePreview(code) {
    const iframe = document.getElementById('previewFrame');
    iframe.srcdoc = code;
}