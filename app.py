#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能问答系统核心模块 - 完整增强版
功能：文本分类、情感分析、机器翻译、智能问答 + 7个新增文本分析功能 + 图片功能
新增：文本统计、文本摘要、词频分析、语言检测、关键词提取、命名实体识别、深度思考、生成图片、添加图片
✅ 所有功能只要开启就显示，不受文本长度限制
"""

import os
import json
import re
import sys
import http.client
import warnings
import base64
import time
from io import BytesIO
from PIL import Image
import requests
from typing import Tuple, Dict, Optional
from flask import Flask, request, jsonify, render_template

# 导入火山引擎方舟SDK（图片生成核心依赖）
from volcenginesdkarkruntime import Ark

# 禁用TensorFlow警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

# 导入新增模块
try:
    from text_analysis_modules import (
        analyze_text_statistics,
        analyze_text_summary,
        analyze_word_frequency,
        analyze_language,
        analyze_keywords,
        analyze_entities,
        analyze_deep_thinking
    )
    NEW_MODULES_AVAILABLE = True
except ImportError:
    print("⚠️ 新增文本分析模块未找到，部分功能将不可用")
    NEW_MODULES_AVAILABLE = False

# ========== 配置常量 ==========
class Config:
    """系统配置类"""
    ARK_API_HOST = "ark.cn-beijing.volces.com"
    ARK_API_PATH = "/api/v3/chat/completions"
    ARK_AUTH_TOKEN = "Bearer 7ee197bf-ebd0-482c-931c-f3bae5e3a5ec"
    ARK_MODEL = "doubao-seed-1-6-251015"
    
    # 图片功能配置（直接填写API Key，无需环境变量）
    ARK_IMAGE_API_KEY = "你的火山引擎API Key"  # 👉 必须替换为实际API Key
    IMAGE_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploaded_images')

    @staticmethod
    def get_model_paths() -> Dict[str, str]:
        """获取模型路径配置"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return {
            'text_category_model': os.path.join(base_dir, '../tmp/text_category_model.h5'),
            'sentiment_model': os.path.join(base_dir, '../tmp/sentiment_model.h5'),
            'sentiment_dicts': os.path.join(base_dir, '../tmp/sentiment_dicts.csv'),
            'vocab_dir': os.path.join(base_dir, '../data/cnews.vocab.txt')
        }

    @staticmethod
    def init_image_dir():
        """初始化图片上传目录"""
        if not os.path.exists(Config.IMAGE_UPLOAD_DIR):
            os.makedirs(Config.IMAGE_UPLOAD_DIR)

# ========== 全局状态 ==========
class SystemState:
    """系统状态管理器"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._sentiment_dicts = None
            cls._instance._sentiment_model = None
            cls._instance._translation_loaded = False
            cls._instance._text_classification_available = False
            cls._instance._enabled_models = {
                'text_classification': True,
                'sentiment_analysis': True,
                'translation': True,
                'qa': True,
                'text_statistics': True,
                'text_summary': True,
                'word_frequency': True,
                'language_detection': True,
                'keyword_extraction': True,
                'entity_recognition': True,
                'deep_thinking': True,
                'image_generate': True,  # 生成图片功能开关
                'image_upload': True      # 添加图片功能开关
            }
        return cls._instance

    @property
    def translation_loaded(self) -> bool:
        return self._translation_loaded

    @translation_loaded.setter
    def translation_loaded(self, value: bool):
        self._translation_loaded = value

    @property
    def text_classification_available(self) -> bool:
        return self._text_classification_available

    @text_classification_available.setter
    def text_classification_available(self, value: bool):
        self._text_classification_available = value

    def is_model_enabled(self, model_name: str) -> bool:
        """检查模型是否启用"""
        return self._enabled_models.get(model_name, False)

    def set_model_state(self, model_name: str, enabled: bool):
        """设置模型状态"""
        if model_name in self._enabled_models:
            self._enabled_models[model_name] = enabled
            return True
        return False

# ========== 文本处理工具 ==========
class TextProcessor:
    """文本处理工具类"""

    CONTROL_CHARS = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]')
    PUNCT_MAP = {
        ',': '，', '.': '。', '?': '？', '!': '！',
        ':': '：', ';': '；', '(': '（', ')': '）',
        '[': '【', ']': '】'
    }
    END_PUNCTS = '。！？；，'

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """清理文本中的非法字符"""
        if not text:
            return ""
        return cls.CONTROL_CHARS.sub(' ', text).strip()

    @classmethod
    def format_text(cls, text: str) -> str:
        """格式化文本（标点转换、Markdown处理等）"""
        if not text:
            return ""

        text = cls.sanitize_text(text)

        try:
            text = json.loads(f'"{text}"')
        except:
            pass

        text = text.replace('\n', '<br>').replace('　', ' ')
        text = re.sub(r'[\u200b\u200c\u200d\r]', '', text)

        # Markdown加粗处理
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

        # 标点转换
        for en, cn in cls.PUNCT_MAP.items():
            text = text.replace(en, cn)

        # 数字中的点号恢复
        text = re.sub(r'(\d+)。(\d+)', r'\1.\2', text)
        text = re.sub(r'(\d+\.\d+)。(\d+)', r'\1.\2', text)

        return text

# ========== 图片处理工具类 ==========
class ImageProcessor:
    """图片处理工具类（集成火山引擎SDK）"""
    @staticmethod
    def generate_image(prompt: str) -> str:
        """直接调用火山引擎SDK生成图片（修复参数和错误处理）"""
        try:
            # 验证API Key是否填写
            if not Config.ARK_IMAGE_API_KEY or Config.ARK_IMAGE_API_KEY == "你的火山引擎API Key":
                print("❌ 错误：请在Config类中填写真实的ARK_IMAGE_API_KEY")
                return ""

            # 初始化Ark客户端
            client = Ark(
                base_url="https://ark.cn-beijing.volces.com/api/v3",
                api_key=Config.ARK_IMAGE_API_KEY
            )

            # 修复：添加必填参数n，指定生成图片数量（火山SDK必填）
            imagesResponse = client.images.generate(
                model="doubao-seedream-4-5-251128",  # 确认该模型已开通
                prompt=prompt,
                n=1,  # 新增必填参数：生成1张图片
                sequential_image_generation="disabled",
                response_format="url",
                size="1024x1024",  # 降低分辨率，加快生成速度，减少失败概率
                stream=False,
                watermark=True  # 免费版必须启用水印
            )

            # 下载图片并保存到本地（添加超时重试）
            try:
                image_url = imagesResponse.data[0].url
                # 修复：添加User-Agent，避免被拒绝访问
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                image_data = requests.get(image_url, headers=headers, timeout=30).content
            except requests.exceptions.RequestException as e:
                print(f"❌ 图片下载失败：{str(e)}")
                return ""
            
            # 生成唯一文件名（避免冲突）
            img_name = f"generated_{int(time.time())}.png"
            img_path = os.path.join(Config.IMAGE_UPLOAD_DIR, img_name)
            
            with open(img_path, 'wb') as f:
                f.write(image_data)
            
            # 返回前端可访问的相对路径
            return f"static/uploaded_images/{img_name}"
        
        except ImportError:
            print("❌ 错误：未安装火山引擎SDK")
            print("👉 请执行：pip install 'volcengine-python-sdk[ark]' -i https://pypi.tuna.tsinghua.edu.cn/simple")
            return ""
        except Exception as e:
            # 详细输出错误信息，方便排查
            print(f"❌ 图片生成完整错误：{str(e)}")
            # 常见错误提示
            if "Invalid API key" in str(e):
                print("👉 提示：API Key无效，请检查是否填写正确")
            elif "permission" in str(e).lower():
                print("👉 提示：权限不足，请开通doubao-seedream-4-5-251128模型权限")
            elif "quota" in str(e).lower():
                print("👉 提示：免费额度已用完，请充值或更换账号")
            return ""

    @staticmethod
    def upload_image(file_data: str, filename: str) -> str:
        """处理上传的本地图片（修复base64解码兼容）"""
        try:
            # 修复：兼容不同格式的base64数据
            if 'base64,' in file_data:
                base64_data = file_data.split('base64,')[-1]
            else:
                base64_data = file_data
            
            img_data = base64.b64decode(base64_data)
            img = Image.open(BytesIO(img_data))
            
            # 修复：统一保存为PNG格式，避免格式兼容问题
            img_name = f"uploaded_{int(time.time())}.png"
            img_path = os.path.join(Config.IMAGE_UPLOAD_DIR, img_name)
            img.save(img_path, format='PNG')
            
            # 返回前端可访问路径
            return f"static/uploaded_images/{img_name}"
        except Exception as e:
            print(f"❌ 图片上传失败：{str(e)}")
            return ""

# ========== 模型管理器 ==========
class ModelManager:
    """模型加载和管理类"""

    @staticmethod
    def initialize_models() -> None:
        """初始化所有模型"""
        state = SystemState()
        paths = Config.get_model_paths()

        print("=" * 50)
        print("智能问答系统初始化中...")
        print("=" * 50)

        state.text_classification_available = ModelManager._check_text_classification_model(
            paths['text_category_model']
        )

        ModelManager._load_sentiment_model(
            paths['sentiment_model'],
            paths['sentiment_dicts']
        )

        ModelManager._load_translation_model()
        
        if NEW_MODULES_AVAILABLE:
            print("✓ 文本分析扩展模块已加载（7个新功能）")
        else:
            print("✗ 文本分析扩展模块未加载")
        
        # 初始化图片目录
        Config.init_image_dir()
        print("✓ 图片功能目录已初始化")

        print("=" * 50)
        print("系统初始化完成！")
        print("=" * 50)

    @staticmethod
    def _check_text_classification_model(model_path: str) -> bool:
        if os.path.exists(model_path):
            print("✓ 文本分类模型已就绪")
            return True
        else:
            print("✗ 文本分类模型不存在（功能将被禁用）")
            return False

    @staticmethod
    def _load_sentiment_model(model_path: str, dicts_path: str) -> None:
        state = SystemState()
        if os.path.exists(model_path):
            try:
                from emotion_analysis import load_sentiment_deps
                state._sentiment_dicts, state._sentiment_model = load_sentiment_deps(
                    model_path, dicts_path)
                if state._sentiment_dicts is not None:
                    print("✓ 情感分析模型加载成功")
                else:
                    print("✗ 情感分析模型加载失败")
            except Exception as e:
                print(f"✗ 情感分析模型加载错误: {str(e)}")
        else:
            print("✗ 情感分析模型不存在（功能将被禁用）")

    @staticmethod
    def _load_translation_model() -> None:
        state = SystemState()
        try:
            from machine_translation import load_translation_model
            load_translation_model()
            state.translation_loaded = True
            print("✓ 机器翻译模型加载成功")
        except Exception as e:
            state.translation_loaded = False
            print(f"✗ 机器翻译模型加载失败: {str(e)}")

# ========== 核心聊天服务 ==========
class ChatService:
    """智能问答服务核心类"""

    SENTIMENT_PROMPTS = {
        "positive": "用户情绪积极，请保持热情回复；",
        "negative": "用户情绪消极，请先安抚再解答；",
        "neutral": "用户情绪中性，请简洁专业地回复；"
    }

    TRANSLATION_PATTERN = re.compile(
        r'中译英[:：]?\s*(.+?)($|；|。|，|！|？)|翻译[:：]?\s*(.+?)($|；|。|，|！|？)',
        re.IGNORECASE
    )

    # 图片生成指令匹配（支持"生成图片：关键词"格式）
    IMAGE_GENERATE_PATTERN = re.compile(r'生成图片[:：]?\s*(.+?)($|；|。|，|！|？)', re.IGNORECASE)

    @classmethod
    def process_message(cls, sentence: str, enabled_models: Dict[str, bool]) -> str:
        """处理用户消息 - 所有启用的功能自动显示"""
        try:
            # 收集所有分析结果
            analysis_results = []
            
            # 1. 文本分类（原有功能）
            category, cat_score = "未知", 0.0
            if enabled_models.get('text_classification', True):
                category, cat_score = cls._classify_text(sentence)

            # 2. 情感分析（原有功能）
            sentiment, sent_score = "neutral", 0.5
            if enabled_models.get('sentiment_analysis', True):
                sentiment, sent_score = cls._analyze_sentiment(sentence)
            
            # 3. 7大文本分析功能（原有新增）
            if NEW_MODULES_AVAILABLE:
                if enabled_models.get('text_statistics', True):
                    try:
                        analysis_results.append(analyze_text_statistics(sentence))
                    except Exception as e:
                        print(f"文本统计错误: {e}")
                if enabled_models.get('language_detection', True):
                    try:
                        analysis_results.append(analyze_language(sentence))
                    except Exception as e:
                        print(f"语言检测错误: {e}")
                if enabled_models.get('keyword_extraction', True):
                    try:
                        analysis_results.append(analyze_keywords(sentence, top_n=5))
                    except Exception as e:
                        print(f"关键词提取错误: {e}")
                if enabled_models.get('word_frequency', True):
                    try:
                        analysis_results.append(analyze_word_frequency(sentence, top_n=8))
                    except Exception as e:
                        print(f"词频分析错误: {e}")
                if enabled_models.get('text_summary', True):
                    try:
                        analysis_results.append(analyze_text_summary(sentence, max_sentences=2))
                    except Exception as e:
                        print(f"文本摘要错误: {e}")
                if enabled_models.get('entity_recognition', True):
                    try:
                        analysis_results.append(analyze_entities(sentence))
                    except Exception as e:
                        print(f"实体识别错误: {e}")
                if enabled_models.get('deep_thinking', True):
                    try:
                        analysis_results.append(analyze_deep_thinking(sentence))
                    except Exception as e:
                        print(f"深度思考错误: {e}")

            # 4. 图片生成处理（新增核心功能）
            if enabled_models.get('image_generate', True):
                image_match = cls.IMAGE_GENERATE_PATTERN.search(sentence)
                if image_match:
                    prompt = image_match.group(1).strip()
                    if prompt:
                        image_path = ImageProcessor.generate_image(prompt)
                        if image_path:
                            # 生成图片成功，返回结果+分析信息
                            image_result = f"""🖼️ <b>图片生成结果</b>
<br>━━━━━━━━━━━━━━━━
<br>📝 生成提示词：{prompt}
<br><img src="{image_path}" style="max-width:300px;border-radius:8px;margin-top:8px;">"""
                            if analysis_results:
                                image_result += "<br><br>━━━━━━━━━━━━━━━━<br><b>【扩展分析】</b><br><br>"
                                image_result += "<br><br>".join(analysis_results)
                            return image_result
                        else:
                            analysis_results.append("🖼️ <b>图片生成</b>：生成失败（请查看终端错误信息）")

            # 5. 翻译处理（原有功能）
            if enabled_models.get('translation', True):
                translation_result = cls._handle_translation(
                    sentence, category, cat_score, sentiment, sent_score, enabled_models
                )
                if translation_result:
                    if analysis_results:
                        translation_result += "<br><br>━━━━━━━━━━━━━━━━<br><b>【扩展分析】</b><br><br>"
                        translation_result += "<br><br>".join(analysis_results)
                    return translation_result

            # 6. 智能问答（原有功能）
            if enabled_models.get('qa', True):
                qa_response = cls._generate_response(
                    sentence, category, cat_score, sentiment, sent_score, enabled_models
                )
                if analysis_results:
                    qa_response += "<br><br>━━━━━━━━━━━━━━━━<br><b>【扩展分析】</b><br><br>"
                    qa_response += "<br><br>".join(analysis_results)
                return qa_response
            else:
                # 问答禁用时返回分析结果
                if analysis_results or enabled_models.get('text_classification') or enabled_models.get('sentiment_analysis'):
                    result_text = "<b>【智能分析】</b><br>"
                    if enabled_models.get('text_classification'):
                        result_text += f"📌 文本分类：{category}（置信度：{cat_score:.2f}）<br>"
                    if enabled_models.get('sentiment_analysis'):
                        result_text += f"❤️ 情感倾向：{sentiment}（置信度：{sent_score:.2f}）<br>"
                    if analysis_results:
                        result_text += "<br>━━━━━━━━━━━━━━━━<br><b>【扩展分析】</b><br><br>"
                        result_text += "<br><br>".join(analysis_results)
                    return TextProcessor.format_text(result_text)
                else:
                    return TextProcessor.format_text("所有功能已禁用，请在左侧面板启用至少一个功能")

        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            print(f"聊天服务错误: {error_msg}")
            return TextProcessor.format_text(error_msg)

    @classmethod
    def _classify_text(cls, text: str) -> Tuple[str, float]:
        state = SystemState()
        if not state.text_classification_available:
            return "未知", 0.0
        try:
            from text_classification import predict_text_category
            paths = Config.get_model_paths()
            return predict_text_category(text=text, model_path=paths['text_category_model'], vocab_dir=paths['vocab_dir'])
        except Exception as e:
            print(f"文本分类失败: {str(e)}")
            return "未知", 0.0

    @classmethod
    def _analyze_sentiment(cls, text: str) -> Tuple[str, float]:
        state = SystemState()
        try:
            from emotion_analysis import predict_sentiment
            return predict_sentiment(text=text, dicts=state._sentiment_dicts, model=state._sentiment_model)
        except Exception as e:
            print(f"情感分析失败: {str(e)}")
            return "neutral", 0.5

    @classmethod
    def _handle_translation(cls, text: str, category: str, cat_score: float,
                            sentiment: str, sent_score: float, enabled_models: Dict) -> Optional[str]:
        state = SystemState()
        match = cls.TRANSLATION_PATTERN.search(text)
        if not match or not state.translation_loaded:
            return None
        try:
            from machine_translation import machine_translate
            translate_text = match.group(1) or match.group(3)
            translate_text = translate_text.strip() if translate_text else text
            if not translate_text:
                return TextProcessor.format_text("请输入需要翻译的中文内容")
            if translate_text[-1] not in TextProcessor.END_PUNCTS:
                translate_text += '。'
            result = machine_translate(translate_text, src_lang="zh", tgt_lang="en")
            response = f"<b>【中译英结果】</b><br>{result}<br><br>"
            if enabled_models.get('text_classification') or enabled_models.get('sentiment_analysis'):
                response += "<b>【基础分析】</b><br>"
                if enabled_models.get('text_classification'):
                    response += f"📌 文本分类：{category}（置信度：{cat_score:.2f}）<br>"
                if enabled_models.get('sentiment_analysis'):
                    response += f"❤️ 情感倾向：{sentiment}（置信度：{sent_score:.2f}）"
            return TextProcessor.format_text(response)
        except Exception as e:
            print(f"翻译失败: {str(e)}")
            return TextProcessor.format_text(f"翻译服务暂时不可用<br>错误：{str(e)}")

    @classmethod
    def _generate_response(cls, text: str, category: str, cat_score: float,
                           sentiment: str, sent_score: float, enabled_models: Dict) -> str:
        sentiment_prompt = cls.SENTIMENT_PROMPTS.get(sentiment, "")
        category_prompt = f"用户问题属于{category}领域，请使用相关专业知识；"
        system_prompt = f"你是智能问答助手，遵循以下规则：1. {sentiment_prompt}2. {category_prompt}3. 回复长度控制在200字以内；4. 无法回答时，友好告知并引导。"
        
        payload = json.dumps({
            "model": Config.ARK_MODEL,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": text}]
        })
        headers = {'Authorization': Config.ARK_AUTH_TOKEN, 'Content-Type': 'application/json'}
        
        try:
            conn = http.client.HTTPSConnection(Config.ARK_API_HOST)
            conn.request("POST", Config.ARK_API_PATH, payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()
            clean_data = TextProcessor.sanitize_text(data)
            reply = json.loads(clean_data)["choices"][0]["message"]["content"]
            
            response_text = f"<b>【智能回答】</b><br>{reply}<br><br>"
            if enabled_models.get('text_classification') or enabled_models.get('sentiment_analysis'):
                response_text += "<b>【基础分析】</b><br>"
                if enabled_models.get('text_classification'):
                    response_text += f"📌 文本分类：{category}（置信度：{cat_score:.2f}）<br>"
                if enabled_models.get('sentiment_analysis'):
                    response_text += f"❤️ 情感倾向：{sentiment}（置信度：{sent_score:.2f}）"
            return TextProcessor.format_text(response_text)
        except Exception as e:
            raise Exception(f"API调用失败: {str(e)}")

# ========== Web应用 ==========
app = Flask(__name__, template_folder='templates', static_folder='static')

# 图片上传接口（修复：明确指定Content-Type，兼容form-data和json）
@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        # 修复：同时支持json和form-data格式
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        file_data = data.get('file_data')
        filename = data.get('filename', 'unknown.png')
        enabled_models_str = data.get('models', '{}')
        
        try:
            enabled_models = json.loads(enabled_models_str)
        except:
            enabled_models = {k: True for k in SystemState()._enabled_models.keys()}
        
        if not enabled_models.get('image_upload', True):
            return jsonify({'status': 'error', 'message': '图片上传功能已禁用'})
        if not file_data:
            return jsonify({'status': 'error', 'message': '请选择图片'})
        
        image_path = ImageProcessor.upload_image(file_data, filename)
        if image_path:
            return jsonify({
                'status': 'success',
                'html': f"""📤 <b>图片上传成功</b>
<br>━━━━━━━━━━━━━━━━
<br><img src="{image_path}" style="max-width:300px;border-radius:8px;margin-top:8px;">"""
            })
        else:
            return jsonify({'status': 'error', 'message': '图片上传失败（查看终端错误）'})
    except Exception as e:
        print(f"上传接口错误：{str(e)}")
        return jsonify({'status': 'error', 'message': f'上传错误：{str(e)}'})

# 消息处理接口（原有）
@app.route('/message', methods=['POST'])
def handle_message():
    message = request.form.get('msg', '').strip()
    enabled_models_str = request.form.get('models', '{}')
    try:
        enabled_models = json.loads(enabled_models_str)
    except:
        enabled_models = {k: True for k in SystemState()._enabled_models.keys()}
    if not message:
        return jsonify({'text': TextProcessor.format_text('请输入内容～')})
    response = ChatService.process_message(message, enabled_models)
    response = response.replace('_UNK', '^_^').strip()
    return jsonify({'text': response if response else TextProcessor.format_text('我们来聊聊天吧～')})

# 模型状态查询接口（原有+图片功能）
@app.route('/get_model_status', methods=['GET'])
def get_model_status():
    state = SystemState()
    status = {
        'text_classification': {'enabled': state.is_model_enabled('text_classification'), 'available': state.text_classification_available},
        'sentiment_analysis': {'enabled': state.is_model_enabled('sentiment_analysis'), 'available': state._sentiment_model is not None},
        'translation': {'enabled': state.is_model_enabled('translation'), 'available': state.translation_loaded},
        'qa': {'enabled': state.is_model_enabled('qa'), 'available': True},
        'image_generate': {'enabled': state.is_model_enabled('image_generate'), 'available': True},
        'image_upload': {'enabled': state.is_model_enabled('image_upload'), 'available': True}
    }
    new_features = ['text_statistics', 'text_summary', 'word_frequency', 'language_detection', 'keyword_extraction', 'entity_recognition', 'deep_thinking']
    for feature in new_features:
        status[feature] = {'enabled': state.is_model_enabled(feature), 'available': NEW_MODULES_AVAILABLE}
    return jsonify(status)

# 页面路由（原有）
@app.route("/")
def home():
    return render_template('html.html')

@app.route("/classic")
def classic():
    return render_template('index.html')

# ========== 主程序 ==========
if __name__ == '__main__':
    ModelManager.initialize_models()

    print("\n" + "=" * 50)
    print("🚀 Web服务已启动")
    print("=" * 50)
    print("增强版界面: http://127.0.0.1:8808")
    print("经典版界面: http://127.0.0.1:8808/classic")
    print("=" * 50)
    print("📦 功能列表：")
    print("  ✓ 核心功能：文本分类、情感分析、机器翻译、智能问答")
    print("  ✓ 文本分析：文本统计、文本摘要、词频分析、语言检测、关键词提取、实体识别、深度思考")
    print("  ✓ 图片功能：生成图片（火山SDK）、添加图片（本地上传）")
    print("=" * 50)
    print("✨ 使用说明：")
    print("  - 生成图片：输入'生成图片：关键词'（例：生成图片：蓝天白云）")
    print("  - 添加图片：点击'上传图片'按钮选择本地文件")
    print("  - 问题排查：查看终端输出的详细错误信息")
    print("=" * 50 + "\n")

app.run(host='127.0.0.1', port=8808, debug=False)