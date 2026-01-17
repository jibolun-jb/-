#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文本分析扩展模块
包含：文本统计、文本摘要、词频分析、语言检测、关键词提取、命名实体识别、深度思考
"""

import jieba
import jieba.analyse
import re
from collections import Counter
from typing import Dict, List, Tuple
import numpy as np


# ========== 1. 文本统计分析 ==========
class TextStatistics:
    """文本统计分析模块"""
    
    @staticmethod
    def analyze(text: str) -> Dict:
        """
        文本统计分析
        :param text: 输入文本
        :return: 统计结果字典
        """
        try:
            # 基础统计
            total_chars = len(text)
            chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
            english_chars = len(re.findall(r'[a-zA-Z]', text))
            digits = len(re.findall(r'\d', text))
            punctuation = len(re.findall(r'[^\w\s]', text))
            spaces = text.count(' ') + text.count('\n') + text.count('\t')
            
            # 分词统计
            words = list(jieba.cut(text))
            words_clean = [w for w in words if w.strip() and len(w) > 1]
            unique_words = len(set(words_clean))
            
            # 句子统计
            sentences = re.split(r'[。！？.!?]', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # 平均值计算
            avg_word_length = sum(len(w) for w in words_clean) / max(len(words_clean), 1)
            avg_sentence_length = sum(len(s) for s in sentences) / max(len(sentences), 1)
            
            return {
                'total_chars': total_chars,
                'chinese_chars': chinese_chars,
                'english_chars': english_chars,
                'digits': digits,
                'punctuation': punctuation,
                'spaces': spaces,
                'total_words': len(words_clean),
                'unique_words': unique_words,
                'total_sentences': len(sentences),
                'avg_word_length': round(avg_word_length, 2),
                'avg_sentence_length': round(avg_sentence_length, 2),
                'lexical_diversity': round(unique_words / max(len(words_clean), 1), 4)
            }
        except Exception as e:
            print(f"文本统计失败: {str(e)}")
            return {}


# ========== 2. 文本摘要提取 ==========
class TextSummarization:
    """基于TextRank的文本摘要模块"""
    
    @staticmethod
    def summarize(text: str, ratio: float = 0.3, max_sentences: int = 3) -> str:
        """
        提取文本摘要
        :param text: 输入文本
        :param ratio: 摘要比例
        :param max_sentences: 最大句子数
        :return: 摘要文本
        """
        try:
            # 分句
            sentences = re.split(r'[。！？.!?]', text)
            sentences = [s.strip() for s in sentences if s.strip() and len(s) > 5]
            
            if len(sentences) == 0:
                return "文本过短，无法生成摘要"
            
            if len(sentences) <= max_sentences:
                return '。'.join(sentences) + '。'
            
            # 计算句子权重（简化版TextRank）
            sentence_scores = {}
            
            for i, sent in enumerate(sentences):
                words = list(jieba.cut(sent))
                # 过滤停用词
                words = [w for w in words if len(w) > 1 and w not in ['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这']]
                
                # 基于词频和位置的评分
                word_freq = Counter(words)
                position_weight = 1.0 / (i + 1)  # 靠前的句子权重更高
                length_weight = min(len(words) / 20, 1.0)  # 适中长度的句子权重更高
                
                score = sum(word_freq.values()) * position_weight * length_weight
                sentence_scores[i] = score
            
            # 选择得分最高的句子
            num_sentences = min(max_sentences, max(1, int(len(sentences) * ratio)))
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
            top_sentences = sorted(top_sentences, key=lambda x: x[0])  # 按原顺序排列
            
            summary = '。'.join([sentences[i] for i, _ in top_sentences]) + '。'
            return summary
            
        except Exception as e:
            print(f"文本摘要失败: {str(e)}")
            return text[:100] + '...' if len(text) > 100 else text


# ========== 3. 词频分析 ==========
class WordFrequency:
    """词频分析模块"""
    
    @staticmethod
    def analyze(text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        词频统计
        :param text: 输入文本
        :param top_n: 返回前N个高频词
        :return: [(词, 频次), ...]
        """
        try:
            # 分词
            words = jieba.cut(text)
            
            # 停用词列表
            stopwords = set(['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', 
                           '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会',
                           '着', '没有', '看', '好', '自己', '这', '那', '这个', '什么', '为',
                           '被', '最', '该', '些', '您', '吗', '能', '把', '让', '啊', '呢'])
            
            # 过滤并统计
            words_filtered = [w for w in words if len(w) > 1 and w not in stopwords]
            
            if not words_filtered:
                return []
            
            word_counts = Counter(words_filtered)
            
            return word_counts.most_common(top_n)
            
        except Exception as e:
            print(f"词频分析失败: {str(e)}")
            return []


# ========== 4. 语言检测 ==========
class LanguageDetection:
    """语言检测模块"""
    
    @staticmethod
    def detect(text: str) -> Dict:
        """
        检测文本语言
        :param text: 输入文本
        :return: 语言信息字典
        """
        try:
            # 统计各类字符
            chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
            english_chars = len(re.findall(r'[a-zA-Z]', text))
            japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF]', text))
            korean_chars = len(re.findall(r'[\uAC00-\uD7A3]', text))
            digits = len(re.findall(r'\d', text))
            
            total_chars = len(re.findall(r'\S', text))
            
            if total_chars == 0:
                return {'language': 'unknown', 'confidence': 0.0, 'details': {}}
            
            # 计算比例
            ratios = {
                'chinese': chinese_chars / total_chars,
                'english': english_chars / total_chars,
                'japanese': japanese_chars / total_chars,
                'korean': korean_chars / total_chars,
                'digits': digits / total_chars
            }
            
            # 判断主要语言
            if ratios['chinese'] > 0.3:
                language = 'Chinese'
                confidence = ratios['chinese']
            elif ratios['english'] > 0.5:
                language = 'English'
                confidence = ratios['english']
            elif ratios['japanese'] > 0.2:
                language = 'Japanese'
                confidence = ratios['japanese']
            elif ratios['korean'] > 0.2:
                language = 'Korean'
                confidence = ratios['korean']
            else:
                language = 'Mixed'
                confidence = max(ratios.values())
            
            return {
                'language': language,
                'confidence': round(confidence, 4),
                'details': {k: round(v, 4) for k, v in ratios.items()}
            }
            
        except Exception as e:
            print(f"语言检测失败: {str(e)}")
            return {'language': 'unknown', 'confidence': 0.0, 'details': {}}


# ========== 5. 关键词提取 ==========
class KeywordExtraction:
    """关键词提取模块"""
    
    @staticmethod
    def extract(text: str, top_n: int = 5, method: str = 'tfidf') -> List[Tuple[str, float]]:
        """
        提取关键词
        :param text: 输入文本
        :param top_n: 返回前N个关键词
        :param method: 提取方法 ('tfidf' 或 'textrank')
        :return: [(关键词, 权重), ...]
        """
        try:
            if method == 'tfidf':
                keywords = jieba.analyse.extract_tags(text, topK=top_n, withWeight=True)
            else:  # textrank
                keywords = jieba.analyse.textrank(text, topK=top_n, withWeight=True)
            
            if not keywords:
                return []
            
            return [(word, round(weight, 4)) for word, weight in keywords]
            
        except Exception as e:
            print(f"关键词提取失败: {str(e)}")
            return []


# ========== 6. 命名实体识别（简化版）==========
class NamedEntityRecognition:
    """命名实体识别模块（基于规则）"""
    
    @staticmethod
    def extract(text: str) -> Dict[str, List[str]]:
        """
        提取命名实体
        :param text: 输入文本
        :return: 实体字典 {'person': [...], 'location': [...], ...}
        """
        try:
            entities = {
                'person': [],
                'location': [],
                'organization': [],
                'time': [],
                'number': []
            }
            
            # 人名（简单规则：常见姓氏+1-2个字）
            common_surnames = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
                             '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '罗', '高']
            person_pattern = '|'.join([f'{s}[\\u4e00-\\u9fa5]{{1,2}}' for s in common_surnames])
            persons = re.findall(person_pattern, text)
            entities['person'] = list(set(persons))
            
            # 地点（包含地名关键词）
            location_keywords = ['省', '市', '县', '区', '镇', '村', '路', '街', '巷', '国', '州']
            for word in jieba.cut(text):
                if len(word) > 1 and any(kw in word for kw in location_keywords):
                    entities['location'].append(word)
            
            # 机构（包含机构关键词）
            org_keywords = ['公司', '学校', '大学', '医院', '银行', '政府', '部门', '中心', '协会', '集团']
            for word in jieba.cut(text):
                if len(word) > 2 and any(kw in word for kw in org_keywords):
                    entities['organization'].append(word)
            
            # 时间（日期时间模式）
            time_patterns = [
                r'\d{4}年\d{1,2}月\d{1,2}日',
                r'\d{4}年\d{1,2}月',
                r'\d{1,2}月\d{1,2}日',
                r'\d{1,2}:\d{2}',
                r'今天|明天|昨天|前天|后天'
            ]
            for pattern in time_patterns:
                times = re.findall(pattern, text)
                entities['time'].extend(times)
            
            # 数字（金额、数量等）
            number_patterns = [
                r'\d+\.?\d*[万亿千百]?元',
                r'\d+\.?\d*%',
                r'\d+\.?\d*[万亿千百]?',
            ]
            for pattern in number_patterns:
                numbers = re.findall(pattern, text)
                entities['number'].extend(numbers)
            
            # 去重
            for key in entities:
                entities[key] = list(set(entities[key]))
            
            return entities
            
        except Exception as e:
            print(f"命名实体识别失败: {str(e)}")
            return {'person': [], 'location': [], 'organization': [], 'time': [], 'number': []}


# ========== 7. 深度思考 ==========
class DeepThinking:
    """深度思考模块 - 多维度文本分析"""
    
    @staticmethod
    def analyze(text: str) -> str:
        """
        深度思考分析
        :param text: 输入文本
        :return: 分析结果
        """
        try:
            analysis_parts = []
            
            # 1. 文本复杂度分析
            words = list(jieba.cut(text))
            words_clean = [w for w in words if w.strip() and len(w) > 1]
            unique_ratio = len(set(words_clean)) / max(len(words_clean), 1)
            
            if unique_ratio > 0.8:
                complexity = "高（词汇丰富，表达精炼）"
            elif unique_ratio > 0.5:
                complexity = "中等（用词适中）"
            else:
                complexity = "低（词汇重复较多）"
            
            analysis_parts.append(f"📐 文本复杂度：{complexity}")
            
            # 2. 表达风格分析
            sentence_count = len(re.split(r'[。！？.!?]', text))
            avg_sentence_len = len(text) / max(sentence_count, 1)
            
            if avg_sentence_len > 30:
                style = "正式严谨（长句为主）"
            elif avg_sentence_len > 15:
                style = "平衡适中（句长合理）"
            else:
                style = "简洁明快（短句为主）"
            
            analysis_parts.append(f"✍️ 表达风格：{style}")
            
            # 3. 语气倾向分析
            question_marks = text.count('？') + text.count('?')
            exclamation_marks = text.count('！') + text.count('!')
            
            if exclamation_marks > 2:
                tone = "强烈情绪化"
            elif question_marks > 2:
                tone = "探索询问性"
            elif exclamation_marks > 0 or question_marks > 0:
                tone = "适度情感表达"
            else:
                tone = "平静陈述性"
            
            analysis_parts.append(f"💭 语气倾向：{tone}")
            
            # 4. 信息密度分析
            info_density = len(words_clean) / max(len(text), 1)
            
            if info_density > 0.5:
                density = "高（信息量大）"
            elif info_density > 0.3:
                density = "中等（信息适中）"
            else:
                density = "低（留白较多）"
            
            analysis_parts.append(f"📊 信息密度：{density}")
            
            # 5. 主题集中度分析
            if words_clean:
                word_freq = Counter(words_clean)
                top_word_freq = word_freq.most_common(1)[0][1]
                concentration = top_word_freq / len(words_clean)
                
                if concentration > 0.15:
                    focus = "高（主题明确集中）"
                elif concentration > 0.08:
                    focus = "中等（主题相对清晰）"
                else:
                    focus = "低（话题较分散）"
                
                analysis_parts.append(f"🎯 主题集中度：{focus}")
            
            # 6. 可读性评估
            avg_word_len = sum(len(w) for w in words_clean) / max(len(words_clean), 1)
            
            if avg_word_len > 3:
                readability = "较难（专业术语较多）"
            elif avg_word_len > 2:
                readability = "适中（通俗易懂）"
            else:
                readability = "简单（基础词汇为主）"
            
            analysis_parts.append(f"📖 可读性：{readability}")
            
            return "<br>".join(analysis_parts)
            
        except Exception as e:
            print(f"深度思考分析失败: {str(e)}")
            return "深度思考分析暂时不可用"


# ========== 统一接口 ==========
def analyze_text_statistics(text: str) -> str:
    """文本统计分析接口"""
    stats = TextStatistics.analyze(text)
    if not stats:
        return "📊 <b>文本统计</b>：统计失败"
    
    result = f"""📊 <b>文本统计</b>
<br>━━━━━━━━━━━━━━━━
<br>📝 总字符数：{stats['total_chars']} | 🀄 中文：{stats['chinese_chars']} | 🔤 英文：{stats['english_chars']}
<br>📚 总词数：{stats['total_words']} | 🎯 不重复词：{stats['unique_words']} | 📄 句子数：{stats['total_sentences']}
<br>📈 平均词长：{stats['avg_word_length']}字 | 📏 平均句长：{stats['avg_sentence_length']}字
<br>🎨 词汇丰富度：{stats['lexical_diversity']}"""
    
    return result.strip()


def analyze_text_summary(text: str, max_sentences: int = 3) -> str:
    """文本摘要接口"""
    summary = TextSummarization.summarize(text, max_sentences=max_sentences)
    result = f"""📋 <b>文本摘要</b>
<br>━━━━━━━━━━━━━━━━
<br>{summary}"""
    return result.strip()


def analyze_word_frequency(text: str, top_n: int = 8) -> str:
    """词频分析接口"""
    word_freq = WordFrequency.analyze(text, top_n)
    if not word_freq:
        return "📊 <b>词频分析</b>：文本过短，无法分析"
    
    result = f"📊 <b>词频分析（Top {min(top_n, len(word_freq))}）</b><br>━━━━━━━━━━━━━━━━"
    for i, (word, count) in enumerate(word_freq, 1):
        bar = '█' * min(count, 15)
        result += f"<br>{i}. {word}：{count}次 {bar}"
    
    return result


def analyze_language(text: str) -> str:
    """语言检测接口"""
    lang_info = LanguageDetection.detect(text)
    
    result = f"""🌍 <b>语言检测</b>
<br>━━━━━━━━━━━━━━━━
<br>🎯 主要语言：{lang_info['language']} | 📊 置信度：{lang_info['confidence']*100:.1f}%
<br>🀄 中文：{lang_info['details']['chinese']*100:.1f}% | 🔤 英文：{lang_info['details']['english']*100:.1f}% | 🗾 日文：{lang_info['details']['japanese']*100:.1f}%"""
    return result.strip()


def analyze_keywords(text: str, top_n: int = 5, method: str = 'tfidf') -> str:
    """关键词提取接口"""
    keywords = KeywordExtraction.extract(text, top_n, method)
    if not keywords:
        return "🔑 <b>关键词提取</b>：文本过短，无法提取"
    
    method_name = 'TF-IDF' if method == 'tfidf' else 'TextRank'
    result = f"🔑 <b>关键词提取（{method_name}）</b><br>━━━━━━━━━━━━━━━━"
    for i, (word, weight) in enumerate(keywords, 1):
        result += f"<br>{i}. {word} (权重: {weight})"
    
    return result


def analyze_entities(text: str) -> str:
    """命名实体识别接口"""
    entities = NamedEntityRecognition.extract(text)
    
    result = "👤 <b>命名实体识别</b><br>━━━━━━━━━━━━━━━━"
    
    has_entity = False
    if entities['person']:
        result += f"<br>👨 人名：{', '.join(entities['person'][:8])}"
        has_entity = True
    if entities['location']:
        result += f"<br>📍 地点：{', '.join(entities['location'][:8])}"
        has_entity = True
    if entities['organization']:
        result += f"<br>🏢 机构：{', '.join(entities['organization'][:8])}"
        has_entity = True
    if entities['time']:
        result += f"<br>⏰ 时间：{', '.join(entities['time'][:8])}"
        has_entity = True
    if entities['number']:
        result += f"<br>🔢 数值：{', '.join(entities['number'][:8])}"
        has_entity = True
    
    if not has_entity:
        result += "<br>未识别到明显的命名实体"
    
    return result


def analyze_deep_thinking(text: str) -> str:
    """深度思考接口"""
    thinking = DeepThinking.analyze(text)
    result = f"""🧠 <b>深度思考</b>
<br>━━━━━━━━━━━━━━━━
<br>{thinking}"""
    return result.strip()


# ========== 测试代码 ==========
if __name__ == '__main__':
    test_text = """
    华为技术有限公司成立于1987年，总部位于广东省深圳市。
    2023年，华为在全球市场的销售额达到8500亿元人民币。
    公司创始人任正非先生带领团队研发了5G技术。
    今天，华为Mate60系列手机在北京正式发布。
    这款手机搭载了麒麟9000S芯片，性能提升30%。
    """
    
    print("=" * 50)
    print("测试7大文本分析模块")
    print("=" * 50)
    
    print("\n1. 文本统计：")
    print(analyze_text_statistics(test_text))
    
    print("\n2. 文本摘要：")
    print(analyze_text_summary(test_text))
    
    print("\n3. 词频分析：")
    print(analyze_word_frequency(test_text))
    
    print("\n4. 语言检测：")
    print(analyze_language(test_text))
    
    print("\n5. 关键词提取：")
    print(analyze_keywords(test_text))
    
    print("\n6. 命名实体识别：")
    print(analyze_entities(test_text))
    
    print("\n7. 深度思考：")
    print(analyze_deep_thinking(test_text))