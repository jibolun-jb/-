<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>智能问答系统 - 完整版 TIPDM</title>
    <link rel='stylesheet' href='https://fonts.googleapis.com/css?family=Open+Sans'>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        html, body {
            height: 100%;
            font-family: 'Open Sans', 'Microsoft YaHei', sans-serif;
            overflow: hidden;
        }

        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-size: 14px;
        }

        .container {
            display: flex;
            height: 100vh;
            padding: 15px;
            gap: 15px;
        }

        /* 模型控制面板 */
        .model-panel {
            width: 320px;
            background: rgba(255, 255, 255, 0.98);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            overflow-y: auto;
            animation: slideInLeft 0.5s ease;
        }

        .model-panel::-webkit-scrollbar {
            width: 6px;
        }

        .model-panel::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 3px;
        }

        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .panel-header {
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 12px;
        }

        .panel-header h2 {
            font-size: 18px;
            color: #333;
            margin-bottom: 5px;
        }

        .panel-header p {
            font-size: 12px;
            color: #666;
        }

        /* 功能分组 */
        .feature-group {
            margin-bottom: 20px;
        }

        .feature-group-title {
            font-size: 13px;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
            padding-left: 8px;
            border-left: 3px solid #667eea;
        }

        .model-item {
            background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 10px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 2px solid transparent;
            cursor: pointer;
        }

        .model-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .model-item.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: rgba(255, 255, 255, 0.3);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .model-item.disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .model-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }

        .model-name {
            font-weight: 600;
            font-size: 14px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .model-item.active .model-name {
            color: white;
        }

        .model-desc {
            font-size: 11px;
            color: #666;
            line-height: 1.4;
        }

        .model-item.active .model-desc {
            color: rgba(255, 255, 255, 0.9);
        }

        /* 开关按钮 */
        .switch {
            position: relative;
            display: inline-block;
            width: 44px;
            height: 24px;
        }

        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .3s;
            border-radius: 24px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: .3s;
            border-radius: 50%;
        }

        input:checked + .slider {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        }

        input:checked + .slider:before {
            transform: translateX(20px);
        }

        /* 状态指示器 */
        .status-indicator {
            margin-top: 15px;
            padding: 12px;
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border-radius: 10px;
            font-size: 12px;
            color: #2e7d32;
            border-left: 3px solid #4CAF50;
        }

        .status-indicator strong {
            display: block;
            margin-bottom: 4px;
        }

        /* 聊天区域 */
        .chat {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: rgba(255, 255, 255, 0.98);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            animation: slideInRight 0.5s ease;
        }

        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .chat-title {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 18px 25px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .chat-title-left {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .chat-title .avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            overflow: hidden;
            border: 3px solid rgba(255, 255, 255, 0.3);
            flex-shrink: 0;
        }

        .chat-title .avatar img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .chat-title-text h1 {
            margin: 0;
            font-size: 20px;
            font-weight: 600;
        }

        .chat-title-text h2 {
            margin: 4px 0 0 0;
            font-size: 12px;
            opacity: 0.85;
            font-weight: normal;
        }

        .feature-count {
            background: rgba(255, 255, 255, 0.2);
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: linear-gradient(to bottom, #f8f9fa 0%, #e9ecef 100%);
        }

        .messages::-webkit-scrollbar {
            width: 8px;
        }

        .messages::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
        }

        .message {
            margin-bottom: 18px;
            animation: messageSlideIn 0.3s ease;
            clear: both;
        }

        @keyframes messageSlideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message-wrapper {
            display: flex;
            align-items: flex-end;
            gap: 8px;
        }

        .message-personal .message-wrapper {
            flex-direction: row-reverse;
        }

        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 16px;
            word-wrap: break-word;
            line-height: 1.5;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .message-personal .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .message-bot .message-content {
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
        }

        .message-content img {
            max-width: 100%;
            border-radius: 8px;
            margin: 8px 0;
        }

        .timestamp {
            font-size: 10px;
            color: #999;
            margin-top: 4px;
            padding: 0 8px;
        }

        /* 加载动画 */
        .loading {
            display: inline-flex;
            gap: 4px;
        }

        .loading span {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
            animation: bounce 1.4s infinite ease-in-out both;
        }

        .loading span:nth-child(1) {
            animation-delay: -0.32s;
        }

        .loading span:nth-child(2) {
            animation-delay: -0.16s;
        }

        @keyframes bounce {
            0%, 80%, 100% {
                transform: scale(0);
            }
            40% {
                transform: scale(1);
            }
        }

        /* 输入区域 */
        .message-box {
            background: white;
            padding: 18px 20px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }

        .message-input {
            flex: 1;
            border: 2px solid #e0e0e0;
            border-radius: 22px;
            padding: 10px 18px;
            font-size: 14px;
            outline: none;
            transition: all 0.3s;
            resize: none;
            font-family: 'Open Sans', 'Microsoft YaHei', sans-serif;
            max-height: 100px;
            line-height: 1.4;
        }

        .message-input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .message-submit {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 28px;
            border-radius: 22px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            white-space: nowrap;
        }

        .message-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .message-submit:active {
            transform: translateY(0);
        }

        /* 图片上传按钮 */
        .image-upload-btn {
            background: linear-gradient(135deg, #2196F3 0%, #0D47A1 100%);
            color: white;
            border: none;
            padding: 10px 18px;
            border-radius: 22px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .image-upload-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
        }

        .image-upload-btn input {
            display: none;
        }

        /* 欢迎界面 */
        .welcome-message {
            text-align: center;
            padding: 30px 20px;
            color: #666;
        }

        .welcome-message h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 22px;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
            margin-top: 20px;
        }

        .feature-card {
            background: white;
            padding: 12px;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
            text-align: left;
        }

        .feature-card strong {
            color: #667eea;
            display: block;
            margin-bottom: 4px;
            font-size: 13px;
        }

        .feature-card span {
            font-size: 11px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 模型控制面板 -->
        <div class="model-panel">
            <div class="panel-header">
                <h2>🎯 功能控制中心</h2>
                <p>13大智能功能，随心组合</p>
            </div>
            
            <!-- 核心AI功能 -->
            <div class="feature-group">
                <div class="feature-group-title">🤖 核心AI功能</div>
                
                <div class="model-item active" data-model="text_classification">
                    <div class="model-header">
                        <span class="model-name"><span>📝</span> 文本分类</span>
                        <label class="switch">
                            <input type="checkbox" checked class="model-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="model-desc">自动识别文本类别和主题领域</div>
                </div>

                <div class="model-item active" data-model="sentiment_analysis">
                    <div class="model-header">
                        <span class="model-name"><span>❤️</span> 情感分析</span>
                        <label class="switch">
                            <input type="checkbox" checked class="model-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="model-desc">分析文本情感倾向（积极/消极/中性）</div>
                </div>

                <div class="model-item active" data-model="translation">
                    <div class="model-header">
                        <span class="model-name"><span>🌐</span> 机器翻译</span>
                        <label class="switch">
                            <input type="checkbox" checked class="model-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="model-desc">中英互译（输入"翻译：xxx"）</div>
                </div>

                <div class="model-item active" data-model="qa">
                    <div class="model-header">
                        <span class="model-name"><span>💬</span> 智能问答</span>
                        <label class="switch">
                            <input type="checkbox" checked class="model-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="model-desc">基于大模型的智能对话服务</div>
                </div>
            </div>

            <!-- 文本分析功能 -->
            <div class="feature-group">
                <div class="feature-group-title">📊 文本分析功能</div>
                
                <div class="model-item active" data-model="text_statistics">
                    <div class="model-header">
                        <span class="model-name"><span>📈</span> 文本统计</span>
                        <label class="switch">
                            <input type="checkbox" checked class="model-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="model-desc">字数、词数、句数等全面统计</div>
                </div>

                <div class="model-item active" data-model="text_summary">
                    <div class="model-header">
                        <span class="model-name"><span>📋</span> 文本摘要</span>
                        <label class="switch">
                            <input type="checkbox" checked class="model-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="model-desc">基于TextRank自动提取摘要</div>
                </div>

                <div class="model-item active" data-model="word_frequency">
                    <div class="model-header">
                        <span class="model-name"><span>📊</span> 词频分析</span>
                        <label class="switch">
                            <input type="checkbox" checked class="model-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="model-desc">统计高频词汇及其出现次数</div>
                </div>

                <div class="model-item active" data-model="language_detection">
                    <div class="model-header">
                        <span class="model-name"><span>🌍</span> 语言检测</span>
                        <label class="switch">
                            <input type="checkbox" checked class="model-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="model-desc">识别文本主要语言及成分比例</div>
                </div>

                <div class="model-item active" data-model="keyword_extraction">
                    <div class="model-header">
                        <span class="model-name"><span>🔑</span> 关键词提取</span>
                        <label class="switch">
                            <input type="checkbox" checked class="model-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="model-desc">TF-IDF和TextRank双算法提取</div>
                </div>

                <div class="model-item active" data-model="entity_recognition">
                    <div class="model-header">
                        <span class="model-name"><span>👤</span> 实体识别</span>
                        <label class="switch">
                            <input type="checkbox" checked class="model-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="model-desc">识别人名、地点、机构等实体</div>
                </div>

                <div class="model-item active" data-model="deep_thinking">
                    <div class="model-header">
                        <span class="model-name"><span>🧠</span> 深度思考</span>
                        <label class="switch">
                            <input type="checkbox" checked class="model-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="model-desc">多维度文本深度分析（NEW）</div>
                </div>
            </div>

            <!-- 新增图片功能组 -->
            <div class="feature-group">
                <div class="feature-group-title">🖼️ 图片功能</div>
                
                <div class="model-item active" data-model="image_generate">
                    <div class="model-header">
                        <span class="model-name"><span>🎨</span> 生成图片</span>
                        <label class="switch">
                            <input type="checkbox" checked class="model-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="model-desc">输入"生成图片：关键词"生成对应图片</div>
                </div>

                <div class="model-item active" data-model="image_upload">
                    <div class="model-header">
                        <span class="model-name"><span>📤</span> 添加图片</span>
                        <label class="switch">
                            <input type="checkbox" checked class="model-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="model-desc">上传本地图片并显示在对话中</div>
                </div>
            </div>

            <div class="status-indicator">
                <strong>✅ 系统状态</strong>
                13个功能全部就绪
            </div>
        </div>

        <!-- 聊天区域 -->
        <div class="chat">
            <div class="chat-title">
                <div class="chat-title-left">
                    <figure class="avatar">
                        <img src="static/res/7.png" alt="AI" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Ccircle cx=%2250%22 cy=%2250%22 r=%2250%22 fill=%22%23667eea%22/%3E%3Ctext x=%2250%22 y=%2265%22 text-anchor=%22middle%22 fill=%22white%22 font-size=%2245%22 font-weight=%22bold%22%3EAI%3C/text%3E%3C/svg%3E'" />
                    </figure>
                    <div class="chat-title-text">
                        <h1>智能问答系统 Pro</h1>
                        <h2>13大功能 · 智能分析 · 精准服务</h2>
                    </div>
                </div>
                <div class="feature-count" id="featureCount">13/13 已启用</div>
            </div>
            
            <div class="messages" id="messageContainer">
                <div class="welcome-message">
                    <h3>👋 欢迎使用智能问答系统</h3>
                    <p style="margin: 10px 0;">提供13大智能功能，所有启用的功能都会在输出中显示</p>
                    <div class="feature-grid">
                        <div class="feature-card">
                            <strong>📝 文本分类</strong>
                            <span>10类新闻分类</span>
                        </div>
                        <div class="feature-card">
                            <strong>❤️ 情感分析</strong>
                            <span>3类情感识别</span>
                        </div>
                        <div class="feature-card">
                            <strong>🌐 机器翻译</strong>
                            <span>中英文互译</span>
                        </div>
                        <div class="feature-card">
                            <strong>💬 智能问答</strong>
                            <span>AI对话助手</span>
                        </div>
                        <div class="feature-card">
                            <strong>📈 文本统计</strong>
                            <span>13项统计指标</span>
                        </div>
                        <div class="feature-card">
                            <strong>📋 文本摘要</strong>
                            <span>TextRank算法</span>
                        </div>
                        <div class="feature-card">
                            <strong>📊 词频分析</strong>
                            <span>高频词统计</span>
                        </div>
                        <div class="feature-card">
                            <strong>🌍 语言检测</strong>
                            <span>多语言识别</span>
                        </div>
                        <div class="feature-card">
                            <strong>🔑 关键词提取</strong>
                            <span>双算法提取</span>
                        </div>
                        <div class="feature-card">
                            <strong>👤 实体识别</strong>
                            <span>5类实体提取</span>
                        </div>
                        <div class="feature-card">
                            <strong>🧠 深度思考</strong>
                            <span>6维度分析</span>
                        </div>
                        <div class="feature-card">
                            <strong>🎨 生成图片</strong>
                            <span>关键词生成图片</span>
                        </div>
                        <div class="feature-card">
                            <strong>📤 添加图片</strong>
                            <span>上传本地图片</span>
                        </div>
                    </div>
                    <p style="margin-top: 20px; color: #999; font-size: 12px;">
                        💡 所有启用的功能都会自动显示在【扩展分析】中 | 图片生成格式：生成图片：关键词
                    </p>
                </div>
            </div>
            
            <div class="message-box">
                <textarea 
                    class="message-input" 
                    placeholder="输入消息... (Shift+Enter 换行，Enter 发送) | 生成图片：关键词"
                    rows="1"></textarea>
                <!-- 新增图片上传按钮 -->
                <label class="image-upload-btn">
                    📤 上传图片
                    <input type="file" accept="image/*" id="imageUpload">
                </label>
                <button class="message-submit">发送</button>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $(document).ready(function() {
            let modelStates = {
                text_classification: true,
                sentiment_analysis: true,
                translation: true,
                qa: true,
                text_statistics: true,
                text_summary: true,
                word_frequency: true,
                language_detection: true,
                keyword_extraction: true,
                entity_recognition: true,
                deep_thinking: true,
                image_generate: true,
                image_upload: true
            };

            function updateFeatureCount() {
                const enabledCount = Object.values(modelStates).filter(v => v).length;
                const totalCount = Object.keys(modelStates).length;
                $('#featureCount').text(`${enabledCount}/${totalCount} 已启用`);
                
                const $status = $('.status-indicator');
                if (enabledCount === totalCount) {
                    $status.html('<strong>✅ 系统状态</strong>13个功能全部就绪');
                } else if (enabledCount > 0) {
                    $status.html(`<strong>⚠️ 系统状态</strong>${enabledCount}/13 个功能已启用`);
                } else {
                    $status.html('<strong>❌ 系统状态</strong>所有功能已禁用');
                }
            }

            $('.model-toggle').on('change', function() {
                const $item = $(this).closest('.model-item');
                const modelName = $item.data('model');
                const isEnabled = $(this).is(':checked');
                
                if ($item.hasClass('disabled')) {
                    $(this).prop('checked', false);
                    return;
                }
                
                modelStates[modelName] = isEnabled;
                
                if (isEnabled) {
                    $item.addClass('active');
                } else {
                    $item.removeClass('active');
                }

                updateFeatureCount();
            });

            function addMessage(text, isUser) {
                const time = new Date();
                const timeStr = `${time.getHours()}:${time.getMinutes().toString().padStart(2, '0')}`;
                
                const messageClass = isUser ? 'message-personal' : 'message-bot';
                const messageHtml = `
                    <div class="message ${messageClass}">
                        <div class="message-wrapper">
                            <div class="message-content">${text}</div>
                        </div>
                        <div class="timestamp">${timeStr}</div>
                    </div>
                `;
                
                $('.welcome-message').fadeOut(300, function() {
                    $(this).remove();
                });
                
                $('#messageContainer').append(messageHtml);
                scrollToBottom();
            }

            function showLoading() {
                const loadingHtml = `
                    <div class="message message-bot loading-message">
                        <div class="message-wrapper">
                            <div class="message-content">
                                <div class="loading">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                $('#messageContainer').append(loadingHtml);
                scrollToBottom();
            }

            function hideLoading() {
                $('.loading-message').fadeOut(200, function() {
                    $(this).remove();
                });
            }

            function scrollToBottom() {
                const $container = $('#messageContainer');
                $container.animate({
                    scrollTop: $container[0].scrollHeight
                }, 300);
            }

            function sendMessage() {
                const message = $('.message-input').val().trim();
                
                if (!message) {
                    return;
                }

                const enabledCount = Object.values(modelStates).filter(v => v).length;
                if (enabledCount === 0) {
                    addMessage('请至少启用一个功能模块后再进行对话', false);
                    return;
                }

                addMessage(message, true);
                $('.message-input').val('').css('height', 'auto');
                $('.message-submit').prop('disabled', true);

                showLoading();

                $.post('/message', {
                    msg: message,
                    models: JSON.stringify(modelStates)
                }).done(function(reply) {
                    hideLoading();
                    addMessage(reply.text, false);
                }).fail(function(xhr) {
                    hideLoading();
                    const errorMsg = xhr.responseJSON?.error || '抱歉，服务暂时不可用';
                    addMessage(`❌ ${errorMsg}`, false);
                }).always(function() {
                    $('.message-submit').prop('disabled', false);
                    $('.message-input').focus();
                });
            }

            $('.message-submit').click(sendMessage);

            $('.message-input').keydown(function(e) {
                if (e.which === 13 && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            $('.message-input').on('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 100) + 'px';
            });

            // 新增图片上传处理
            $('#imageUpload').on('change', function(e) {
                const file = e.target.files[0];
                if (!file) return;

                const reader = new FileReader();
                reader.onload = function(event) {
                    const fileData = event.target.result;
                    const filename = file.name;

                    // 显示加载中
                    addMessage('<div class="loading"><span></span><span></span><span></span></div>', false);

                    // 上传图片
                    $.post('/upload_image', {
                        file_data: fileData,
                        filename: filename,
                        models: JSON.stringify(modelStates)
                    }).done(function(response) {
                        // 移除加载中
                        $('.loading-message').last().remove();
                        if (response.status === 'success') {
                            addMessage(response.html, false);
                        } else {
                            addMessage(`❌ ${response.message}`, false);
                        }
                    }).fail(function() {
                        $('.loading-message').last().remove();
                        addMessage('❌ 图片上传失败，请重试', false);
                    });

                    // 重置文件输入
                    $('#imageUpload').val('');
                };
                reader.readAsDataURL(file);
            });

            updateFeatureCount();
            $('.message-input').focus();
        });
    </script>
</body>
</html>