/**
 * =============================================================================
 * 项目名称: 绘演万象前端交互逻辑
 * 文件名称: app.js
 * 描述: 处理用户输入、与 Python 后端通信、实时渲染 Canvas 以及界面状态管理。
 * =============================================================================
 */

// 全局变量，用于存储当前生成的代码，便于后续下载或修改
let currentCode = "";
let isGenerating = false;

/**
 * 核心函数：向服务器发起生成请求
 * 触发条件：用户点击“启动生成”按钮
 */
async function generatePage() {
    // 1. 获取 DOM 元素
    const promptInput = document.getElementById('userPrompt');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const baseUrlInput = document.getElementById('baseUrlInput');
    const modelNameInput = document.getElementById('modelNameInput');
    const btn = document.getElementById('generateBtn');
    const status = document.getElementById('statusText');
    const editor = document.getElementById('codeEditor');

    // 2. 获取用户输入值
    const prompt = promptInput.value.trim();
    const apiKey = apiKeyInput.value.trim();
    const baseUrl = baseUrlInput.value.trim();
    const modelName = modelNameInput.value.trim();
    
    // 3. 基础校验 (Validation)
    if (!apiKey) {
        alert("⚠️ 安全警告：请先填写 API Key 才能启动引擎。");
        apiKeyInput.focus();
        // 添加错误动画
        apiKeyInput.style.borderColor = "var(--error-color)";
        setTimeout(() => apiKeyInput.style.borderColor = "#444", 2000);
        return;
    }
    
    if (!prompt) { 
        alert("⚠️ 指令为空：请输入您想生成的物理/数学演示内容。"); 
        promptInput.focus();
        return; 
    }

    // 4. 更新 UI 状态
    isGenerating = true;
    btn.disabled = true;
    btn.innerHTML = "⏳ 正在连接神经网络...";
    status.innerHTML = `<span class="blink"></span>引擎正在运算 | 模型: ${modelName}`;
    editor.value = "// 正在建立 WebSocket 连接...\n// 正在解析自然语言指令...\n// 正在构建物理模型...\n// 请耐心等待...";

    console.log(`[System] Starting generation task. Model: ${modelName}`);

    try {
        // 5. 发送异步 POST 请求 (Fetch API)
        const response = await fetch('/api/generate-html', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-Client-Version': '1.0.0' // 自定义头
            },
            body: JSON.stringify({ 
                prompt: prompt,
                api_key: apiKey,
                base_url: baseUrl,
                model: modelName
            })
        });

        // 6. 处理响应数据
        const data = await response.json();

        if (data.html) {
            // 成功分支
            currentCode = data.html;
            editor.value = currentCode; 
            updatePreview(currentCode);
            
            // 更新成功状态 UI
            status.innerHTML = `<span class="blink" style="background:var(--success-color);"></span>生成完毕 | 已归档至服务器`;
            console.log(`[System] Generation success. Saved to: ${data.saved_path}`);
        } else {
            // 业务逻辑错误分支
            throw new Error(data.error || "未知服务端错误");
        }
    } catch (e) {
        // 网络或系统错误分支
        console.error("[System Error]", e);
        status.innerHTML = `<span style="color:var(--error-color)">❌ 生成中断: ${e.message}</span>`;
        editor.value = `/* \n   系统发生错误 \n   Error: ${e.message} \n   请检查 API Key 或网络连接 \n*/`;
        
        if (e.message.includes("401")) {
            alert("认证失败：API Key 无效，请检查。");
        }
    } finally {
        // 7. 恢复 UI 状态
        isGenerating = false;
        btn.disabled = false;
        btn.innerHTML = "🚀 启动生成";
    }
}

/**
 * 应用代码修改
 * 触发条件：用户点击“手动运行”按钮
 */
function applyCode() {
    const editor = document.getElementById('codeEditor');
    const status = document.getElementById('statusText');
    
    currentCode = editor.value;
    updatePreview(currentCode);
    
    status.innerHTML = `<span class="blink" style="background:var(--warning-color);"></span>开发者模式 | 已应用手动修改`;
    console.log("[System] Manual code update applied.");
}

/**
 * 更新 iframe 预览区
 * @param {string} code - 完整的 HTML 代码字符串
 */
function updatePreview(code) {
    const iframe = document.getElementById('previewFrame');
    // 使用 srcdoc 属性进行沙箱渲染，更安全
    iframe.srcdoc = code;
}

// 页面加载完成后的初始化工作
window.addEventListener('DOMContentLoaded', () => {
    console.log("Huiyan Engine Frontend Ready.");
});