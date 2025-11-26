from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip
import json
import requests
import os
import time

# 插件目录路径
addon_dir = os.path.dirname(__file__)
config_path = os.path.join(addon_dir, 'config.json')

def get_config():
    """获取配置"""
    try:
        if not os.path.exists(config_path):
            showInfo("请先在插件目录中创建config.json文件")
            return None
            
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        showInfo(f"读取配置失败: {str(e)}")
        return None

def save_config(config):
    """保存配置"""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        showInfo(f"保存配置失败: {str(e)}")
        return False

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI提问配置")
        self.setMinimumWidth(700)
        self.setMinimumHeight(800)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setup_ui()
        
    def setup_ui(self):
        config = get_config()
        if not config:
            return
            
        # 基础设置
        form_layout = QFormLayout()
        
        self.apikey = QLineEdit(config["apikey"])
        form_layout.addRow("API Key:", self.apikey)
        
        self.apiurl = QLineEdit(config["apiurl"])
        form_layout.addRow("API URL:", self.apiurl)
        
        self.model = QLineEdit(config["model"])
        form_layout.addRow("模型:", self.model)
        
        self.max_context = QSpinBox()
        self.max_context.setRange(1, 20)
        self.max_context.setValue(config["max_context"])
        form_layout.addRow("上下文消息数量上限:", self.max_context)
        
        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0.0, 2.0)
        self.temperature.setSingleStep(0.1)
        self.temperature.setValue(config["temperature"])
        form_layout.addRow("温度:", self.temperature)
        
        self.top_p = QDoubleSpinBox()
        self.top_p.setRange(0.0, 1.0)
        self.top_p.setSingleStep(0.1)
        self.top_p.setValue(config["top_p"])
        form_layout.addRow("Top P:", self.top_p)
        
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(100, 4000)
        self.max_tokens.setValue(config["max_tokens"])
        form_layout.addRow("最大Token数:", self.max_tokens)
        
        self.question_field = QLineEdit(config["question_field"])
        form_layout.addRow("提问字段:", self.question_field)
        
        self.answer_field = QLineEdit(config["answer_field"])
        form_layout.addRow("回答字段:", self.answer_field)
        
        self.layout.addLayout(form_layout)
        
        # 系统提示词
        self.layout.addWidget(QLabel("系统提示词:"))
        self.system_prompt = QTextEdit()
        self.system_prompt.setPlainText(config["system_prompt"])
        self.system_prompt.setMaximumHeight(200)
        self.layout.addWidget(self.system_prompt)
        
        # 上下文消息
        self.layout.addWidget(QLabel("上下文消息:"))
        self.context_scroll = QScrollArea()
        self.context_widget = QWidget()
        self.context_layout = QVBoxLayout(self.context_widget)
        self.context_edits = []
        
        # 创建上下文编辑框
        context_messages = config["context_messages"]
        for i in range(0, len(context_messages), 2):
            if i + 1 >= len(context_messages):
                break
                
            group_widget = QGroupBox(f"对话 {i//2 + 1}")
            group_layout = QVBoxLayout()
            
            # 用户消息
            user_layout = QHBoxLayout()
            user_layout.addWidget(QLabel("用户:"))
            user_edit = QTextEdit()
            user_edit.setPlainText(context_messages[i]["content"])
            user_edit.setMaximumHeight(80)
            user_layout.addWidget(user_edit)
            group_layout.addLayout(user_layout)
            
            # 助手消息
            assistant_layout = QHBoxLayout()
            assistant_layout.addWidget(QLabel("助手:"))
            assistant_edit = QTextEdit()
            assistant_edit.setPlainText(context_messages[i+1]["content"])
            assistant_edit.setMaximumHeight(80)
            assistant_layout.addWidget(assistant_edit)
            group_layout.addLayout(assistant_layout)
            
            group_widget.setLayout(group_layout)
            self.context_layout.addWidget(group_widget)
            self.context_edits.append((user_edit, assistant_edit))
        
        self.context_scroll.setWidget(self.context_widget)
        self.context_scroll.setWidgetResizable(True)
        self.context_scroll.setMaximumHeight(400)
        self.layout.addWidget(self.context_scroll)
        
        # 按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.layout.addLayout(button_layout)
    
    def save_config(self):
        try:
            config = {
                "apikey": self.apikey.text(),
                "apiurl": self.apiurl.text(),
                "model": self.model.text(),
                "max_context": self.max_context.value(),
                "temperature": self.temperature.value(),
                "top_p": self.top_p.value(),
                "max_tokens": self.max_tokens.value(),
                "system_prompt": self.system_prompt.toPlainText(),
                "question_field": self.question_field.text(),
                "answer_field": self.answer_field.text(),
                "context_messages": []
            }
            
            for user_edit, assistant_edit in self.context_edits:
                user_content = user_edit.toPlainText().strip()
                assistant_content = assistant_edit.toPlainText().strip()
                
                if user_content:
                    config["context_messages"].append({
                        "role": "user",
                        "content": user_content
                    })
                    config["context_messages"].append({
                        "role": "assistant", 
                        "content": assistant_content
                    })
            
            if save_config(config):
                tooltip("配置保存成功")
                self.accept()
            else:
                showInfo("配置保存失败")
                
        except Exception as e:
            showInfo(f"保存配置时出错: {str(e)}")

def call_gemini_api(question):
    """调用Gemini API"""
    config = get_config()
    if not config:
        return "配置错误"
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 构建消息
            messages = []
            
            # 添加系统提示词作为第一条用户消息
            messages.append({
                "role": "user", 
                "parts": [{"text": config["system_prompt"]}]
            })
            
            # 添加模型确认消息
            messages.append({
                "role": "model",
                "parts": [{"text": "明白了，我将严格按照您的要求处理。"}]
            })
            
            # 添加上下文消息
            for msg in config["context_messages"]:
                if msg["role"] == "user":
                    messages.append({
                        "role": "user", 
                        "parts": [{"text": msg["content"]}]
                    })
                else:  # assistant
                    messages.append({
                        "role": "model", 
                        "parts": [{"text": msg["content"]}]
                    })
            
            # 添加当前问题
            messages.append({
                "role": "user", 
                "parts": [{"text": question}]
            })
            
            # API请求数据
            data = {
                "contents": messages,
                "generationConfig": {
                    "temperature": config["temperature"],
                    "topP": config["top_p"],
                    "maxOutputTokens": config["max_tokens"]
                }
            }
            
            url = f"{config['apiurl']}/v1beta/models/{config['model']}:generateContent?key={config['apikey']}"
            response = requests.post(url, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                response_text = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # 检查是否需要重试
                if "SPECIAL INSTRUCTION: think silently if needed." in response_text:
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(1)  # 等待1秒后重试
                        continue
                    else:
                        return "API返回特殊指令，请稍后重试"
                
                return response_text
            else:
                return f"API返回格式错误"
                
        except Exception as e:
            return f"API调用错误: {str(e)}"
    
    return "重试次数用尽"

def generate_ai_response():
    """生成AI回复 (兼容 Edit Field During Review 插件)"""
    try:
        # 确保在复习模式下
        if not mw.reviewer or not mw.reviewer.card:
            showInfo("请在复习模式下使用此功能")
            return
        
        card = mw.reviewer.card
        note = card.note()
        config = get_config()
        if not config:
            return
        
        # 获取问题和回答字段的名称
        question_field = config["question_field"]
        answer_field = config["answer_field"]
        
        # 检查字段是否存在
        if question_field not in note:
            showInfo(f"模板中未找到字段 '{question_field}'，请检查配置")
            return
        if answer_field not in note:
            showInfo(f"模板中未找到字段 '{answer_field}'，请检查配置")
            return
            
        question = note[question_field]
        if not question.strip():
            showInfo(f"字段 '{question_field}' 内容为空")
            return
        
        tooltip("正在向AI提问，请稍候...")
        mw.app.processEvents()

        # 调用API
        response = call_gemini_api(question)
        
        # [修改1] 将换行符 \n 替换为HTML的 <br>
        response_html = response.replace('\r\n', '<br>').replace('\n', '<br>')
        
        # [修改2] 先将新内容保存到数据库
        # 这一步仍然是必要的，确保数据被持久化
        if note[answer_field] != response_html:
            note[answer_field] = response_html
            note.flush()
        
        # [修改3 - 核心] 使用JavaScript直接更新当前页面的内容，而不是刷新整个卡片
        # 这样做可以完美兼容 "Edit Field During Review" 插件
        if mw.reviewer.state == "answer":
            # 使用 json.dumps 来安全地将HTML内容转义为JavaScript字符串
            escaped_html = json.dumps(response_html)
            
            # 构建JavaScript代码，找到对应的可编辑字段并更新其内容
            js_code = f"""
            var field = document.querySelector('[data-field="{answer_field}"]');
            if (field) {{
                field.innerHTML = {escaped_html};
            }}
            """
            # 执行JavaScript
            mw.reviewer.web.eval(js_code)

        tooltip("AI回复已生成并更新")
        
    except Exception as e:
        showInfo(f"生成AI回复时出错: {str(e)}")




def setup_menu():
    """设置菜单"""
    action = QAction("AI提问配置", mw)
    action.triggered.connect(show_config_dialog)
    mw.form.menuTools.addAction(action)

def show_config_dialog():
    """显示配置对话框"""
    try:
        dialog = ConfigDialog(mw)
        dialog.exec()
    except Exception as e:
        showInfo(f"打开配置对话框时出错: {str(e)}")

# 处理来自前端的消息
def handle_webview_message(handled, cmd, context):
    if cmd == "aiGenerate":
        generate_ai_response()
        return (True, None)
    return handled

# 注册钩子
from aqt.gui_hooks import webview_did_receive_js_message
webview_did_receive_js_message.append(handle_webview_message)

# 初始化
setup_menu()