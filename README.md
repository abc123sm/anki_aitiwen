# Anki 插件：AI提问

本插件允许你在 Anki 复习卡片时，一键调用 Google Gemini AI（或者其他AI），对日语句子进行详细的语法和词汇解析，并将结果自动填入指定字段。




## 功能特性

- **一键调用**：在卡片模板中添加一个按钮，即可快速向AI提问。
- **高度可配置**：支持自定义 API Key、模型、系统提示词、上下文对话等。
- **智能上下文**：支持配置多轮对话作为上下文，让AI的回答更符合你的期望。
- **无缝体验**：优化了与 `Edit Field During Review` 插件的兼容性，更新解析后无需刷新卡片。
- **自动创建配置**：首次使用时会自动生成配置文件，简化初始设置。

## 安装与配置
1.  **安装插件**：
    *   通过 AnkiWeb 页面下载，或使用代码 `[发布后获得的ID]` 安装本插件。
    *   通过 AnkiWeb 页面下载，或使用代码 `[1020366288]` 安装依赖插件Edit Field During Review。

2.  **获取 Gemini API Key**：
    *   访问 [Google AI Studio](https://aistudio.google.com/app/apikey)。
    *   点击 "Create API key" 生成你的密钥。

3.  **配置插件**：
    *   在 Anki 主界面，点击菜单栏的 **工具 > AI提问配置**。
    *   将你获取的 API Key 填入 `API Key` 字段。
    *   根据你的卡片模板，设置 `提问字段` (例如：`Expression`) 和 `回答字段` (例如：`Edit`)。
    *   （可选）根据你的需求修改系统提示词和其他参数。
    *   点击 "保存"。

4.  **在卡片模板中添加按钮**：
    *   这是**必须**的步骤！你需要手动在你的卡片模板中添加一个按钮来触发AI。
    *   打开 Anki 的 **工具 > 管理笔记类型**，选择你使用的笔记类型，然后点击 **卡片...**。
    *   在“正面模板”或“背面模板”的 HTML 代码中，找到一个合适的位置，粘贴以下代码：

    ```html
    <button onclick="pycmd('aiGenerate')" style="padding: 10px 1px; background: #3d8b40; font-size: 14px;">AI提问</button>
    ```
    *   **示例模板**：如果你想在看到答案后才提问，可以把代码加在“背面模板”的 `{{AI解析}}` 字段旁边。


## Front Template
```html
<!--
<div>{{kanji:am-highlighted}}</div>

复制Expression字段
<button class="copy-btn" onclick="copyReading(this)" data-copy-anniu="{{Expression}}">复制</button>
-->
{{Audio}}
<div>{{Snapshot}}</div>


<script>
function copyReading(button) {
  // 从按钮的anniu属性获取特定字段的内容
  const readingText = button.getAttribute('data-copy-anniu');
  
  // 创建临时textarea元素
  const textarea = document.createElement('textarea');
  textarea.value = readingText;
  document.body.appendChild(textarea);
  
  // copy
  textarea.select();
  document.execCommand('copy');
  
  // delete
  document.body.removeChild(textarea);
  
  // update
  const originalText = button.textContent;
  button.textContent = '搞掂';
  button.classList.add('copied');
}
</script>
```
## Back Template
```html
<button class="copy-btn" onclick="copyReading(this)" data-copy-anniu="{{Expression}}">复制</button>
<div>{{furigana:am-highlighted}}</div>
<div>{{Snapshot}}</div>
<div style='font-size: 40px'>{{edit:Meaning}}</div>
<div style='font-size: 25px; text-align:start'>{{edit:Edit}}</div>
<button onclick="pycmd('aiGenerate')" style="padding: 10px 1px; background: #3d8b40; font-size: 14px;">AI提问</button>
```
## Styling
```css
.card {
  font-family: arial;
  font-size: 50px;
  text-align: center;
  color: #CDC8B1;
  background-color: #25390c;##f1e5c9;
}
.card.nightMode {
  font-family: arial;//arial
  font-size: 50px;
  text-align: center;
  color: #8B8878;
  #background-color: #25390c;
}

.expression{
  font-size: 40px;
}
[morph-status=unknown] { color: red; }
[morph-status=learning] { color: #1E90FF; }
[morph-status=known] { color: green; }


.copy-btn {
  padding: 10px 1px;
  background-color: #3d8b40;
  font-size: 18px;     /* 可用 !important增大字体 */
  float: left;
}

.copy-btn.copied {
  background-color: #666;
}

```


## 问题反馈

如果你遇到任何问题或有功能建议，欢迎到本项目的 [GitHub Issues](https://github.com/abc123sm/anki_aitiwen/issues) 页面提交。

---
