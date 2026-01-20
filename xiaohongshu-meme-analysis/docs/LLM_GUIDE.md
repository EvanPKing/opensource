# 🚀 LLM增强版使用指南

## 🎯 新架构 - 全网联网搜索

```
用户输入（自然语言）
   ↓
🧠 LLM-Planner Agent
   └─ DeepSeek理解意图、提取关键词
   ↓
🌐 LLM-Crawler Agent  
   └─ DeepSeek Web Search联网搜索全网数据
   └─ 范围：微博、知乎、B站、小红书、抖音等
   ↓
📊 LLM-Analyzer Agent
   └─ DeepSeek深度分析：热度/趋势/文化/预测
   ↓
📝 LLM-Writer Agent
   └─ DeepSeek生成3000-5000字专业报告
   ↓
✨ 专家级洞察报告
```

---

## 🔧 快速开始

### Step 1: 安装依赖

```bash
pip install openai python-dotenv
```

### Step 2: 配置API Key

```bash
# 方式1: 环境变量
set DEEPSEEK_API_KEY=your_key  # Windows
export DEEPSEEK_API_KEY=your_key  # Linux/Mac

# 方式2: 创建.env文件
echo "DEEPSEEK_API_KEY=your_key" > .env
```

### Step 3: 运行

```bash
# 交互式运行
python llm_main.py

# 或命令行运行
python workflows/llm_orchestrator.py "分析2025年全网最火的梗"
```

---

## 💬 支持的自然语言输入

```python
✅ "分析2025年全网最火的梗"
✅ "我想知道年轻人最近在玩什么梗"
✅ "对比小红书和微博的热梗差异"
✅ "找出最有商业价值的网络流行语"
✅ "2025年表情包文化趋势分析"
✅ "年轻人都在用什么梗"
✅ "今年热词和去年有什么不同"
```

---

## 🌐 数据来源（联网搜索）

DeepSeek Web Search 会搜索：

- 📱 **社交平台讨论**
  - 微博热搜话题
  - 知乎高赞回答
  - B站热门评论
  - 小红书笔记分享
  - 抖音热门话题

- 📰 **媒体报道**
  - 科技媒体（36氪、虎嗅）
  - 文化评论
  - 行业分析报告

- 💬 **用户讨论**
  - 贴吧帖子
  - 豆瓣讨论
  - 论坛内容

---

## 📊 输出内容

### 1. 数据文件
```
data/raw/web_search_data.json
- 搜集到的原始数据
- 包含梗名称、来源、热度等
```

### 2. 洞察文件
```
data/processed/llm_insights.json
- 多维度分析结果
- 趋势预测
- 文化洞察
```

### 3. 专业报告
```
output/llm_report_YYYYMMDD_HHMMSS.md
- 3000-5000字深度报告
- 包含：
  ├─ 执行摘要
  ├─ 热门梗深度解析
  ├─ 传播机制分析
  ├─ 文化意义解读
  ├─ 趋势预测
  └─ 商业建议
```

---

## 💰 成本估算

基于DeepSeek定价（假设）：

```
单次完整分析：
- Planner: ~500 tokens → ¥0.001
- Crawler: ~10,000 tokens → ¥0.02
- Analyzer: ~20,000 tokens → ¥0.04
- Writer: ~15,000 tokens → ¥0.03

总计: 约¥0.1 ($0.014) per analysis
```

**超级便宜！** 比传统LLM便宜10-50倍。

---

## 🆚 对比：旧版 vs LLM版

| 特性 | 旧版（基础） | LLM增强版 |
|------|-------------|-----------|
| 数据来源 | 模拟数据 | 全网真实数据 ✅ |
| 输入方式 | 固定格式 | 自然语言 ✅ |
| 分析深度 | 统计描述 | 深度洞察 ✅ |
| 报告质量 | 数据堆砌 | 专家叙事 ✅ |
| 适应性 | 需要编码 | 自动适应 ✅ |
| 成本 | 免费 | ~¥0.1/次 |

---

## 🎓 使用场景

### 1. 学术研究
```python
python llm_main.py
> 分析2025年网络流行语的代际差异
```

### 2. 内容创作
```python
python llm_main.py  
> 找出最有潜力的热梗，适合视频创作
```

### 3. 品牌营销
```python
python llm_main.py
> 对比各平台热梗，制定营销策略
```

### 4. 文化研究
```python
python llm_main.py
> 分析梗文化对年轻人的影响
```

---

## ⚠️ 注意事项

1. **API Key安全**
   - 不要提交.env文件到git
   - 不要分享你的API Key

2. **数据真实性**
   - LLM搜索的是公开数据
   - 可能包含媒体报道和二手资料
   - 不是小红书App内的一手数据

3. **成本控制**
   - 建议设置使用限额
   - 避免频繁调用

---

## 🔜 待提供

请提供你的 **DeepSeek API Key**，格式：

```
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
```

我会帮你配置并测试运行！
