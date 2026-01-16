# Project Specifications: AI Trilingual Coach

## 1. Project Overview (项目概述)
This project is an automated **AI Language Tutor** designed for the Malaysian context.
It runs daily to generate a **"Trilingual Thinking Matrix"** (English, Chinese, Bahasa Melayu), helping the user practice speaking and switching languages in real-life scenarios.

**Core Philosophy:**
- **No Translation**: Focus on "Mental Mapping" (How to express the same idea differently).
- **Context Aware**: Distinguish between **Formal** (Office) and **Casual** (Mamak/Street) Malay.
- **Interactive**: Use Notion's **Toggle Blocks** for active recall testing.

## 2. Technical Architecture (技术架构)
- **Language**: Python 3.10+
- **AI Brain**: Google Gemini API (`gemini-1.5-flash`)
- **Output Interface**: Notion API (Block Children & Page Creation)
- **Automation**: GitHub Actions (Cron Schedule: Daily)

## 3. Functional Logic (功能逻辑)

### 3.1 Content Generation (`worker_lang`)
The AI must generate a daily lesson containing **3 Distinct Scenes**:
1.  **🏢 Work**: Corporate/Professional context (e.g., Meeting, Email, Deadline).
    - *Requirement*: Use **Formal BM** (Bahasa Baku).
2.  **☕ Life**: Casual/Daily context (e.g., Ordering food, Grab, Chatting).
    - *Requirement*: Use **Casual/Spoken BM** (e.g., *tak*, *nak*, *camne*, *boss*).
3.  **💻 Tech**: IT/Developer context (e.g., Bug fix, Deployment).
    - *Requirement*: Tech terminology in BM.

### 3.2 Notion Block Construction (关键交互设计)
The Python script must construct complex Notion blocks, NOT just simple text.
- **Structure**:
  - **Headings**: Use `heading_2` for Scene Titles.
  - **Formal Section**: Use `quote` blocks (Color: Blue/Default) for professional phrases.
  - **Casual Section**: Use `paragraph` blocks (Color: Orange) for slang/spoken phrases.
  - **The Quiz (Interaction)**: 
    - Use **`toggle`** blocks.
    - **Visible**: The Question (e.g., "How to say [Chinese phrase] in BM?").
    - **Hidden (Children)**: The Answer (The BM sentence).

## 4. AI Prompt Specification (AI指令规范)

The AI must return **Strict JSON** using this structure:

```json
{
  "theme": "Office Communication",
  "vocabulary_focus": [
    {
      "concept": "schedule meeting",
      "expressions": {
        "en": "Let's schedule a meeting",
        "cn": "我们安排个会议吧",
        "bm_formal": "Mari kita jadualkan mesyuarat",
        "bm_casual": "Jom schedule meeting"
      }
    },
    {
      "concept": "deadline approaching",
      "expressions": {
        "en": "The deadline is approaching",
        "cn": "截止日期快到了",
        "bm_formal": "Tarikh akhir semakin mendekati",
        "bm_casual": "Deadline dah nak sampai"
      }
    }
  ],
  "practice_scenarios": {
    "work": {
      "scenario": "Email to boss about project delay",
      "key_phrases": ["I need more time", "Project timeline", "Alternative solution"]
    },
    "life": {
      "scenario": "Ordering food delivery",
      "key_phrases": ["Delivery time", "Payment method", "Special instructions"]
    },
    "tech": {
      "scenario": "Explaining bug fix",
      "key_phrases": ["Code review", "Testing phase", "Deployment ready"]
    }
  },
  "quiz_toggle": [
    {
      "question": "How to say '项目延误了' in BM (formal)?",
      "answer": "Projek telah tertangguh"
    }
  ]
}
```

## 5. Technical Implementation Details (技术实现细节)

### 5.1 Environment Variables (环境变量)
- **Required (必需)**:
  - `GEMINI_API_KEY` — Google Gemini API key
  - `NOTION_TOKEN` — Notion integration token (Internal Integration)
  - `NOTION_DATABASE_ID` — Notion database ID for storing daily lessons
- **Optional (可选)**:
  - `GEMINI_MODEL` — Model name (default: "models/gemini-1.5-flash")
  - `MAX_VOCABULARY` — Max vocabulary items per day (default: 6)
  - `THEME_ROTATION` — Comma-separated themes (default: "work,life,tech")

### 5.2 Dependencies (依赖包)
```txt
# requirements.txt
google-generativeai>=0.3.0
notion-client>=2.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

### 5.3 Notion Database Schema (Notion数据库结构)
Create a database with these properties:

| Property Name | Type | Notes |
|---------------|------|-------|
| `Title` | Title | Daily lesson title (e.g., "2024-01-16 - Office Communication") |
| `Theme` | Select | Options: `Work`, `Life`, `Tech` |
| `Date` | Date | Creation date |
| `Vocabulary Count` | Number | Number of vocabulary items |
| `Completed` | Checkbox | User completion status |

### 5.4 File Structure (文件结构)
```
ai-trilingual-coach/
├── main.py                    # 主程序入口
├── worker_lang.py            # AI内容生成器
├── notion_builder.py         # Notion页面构建器
├── config.py                 # 配置管理
├── requirements.txt          # Python依赖
├── .env.example             # 环境变量示例
└── .github/
    └── workflows/
        └── daily_run.yml     # GitHub Actions配置
```

### 5.5 AI Prompt Template (AI提示模板)
```python
GENERATE_CONTENT_PROMPT = """
You are a Malaysian language tutor specializing in trilingual education.

Generate a daily vocabulary lesson with the following requirements:
1. Theme: {theme}
2. 5-8 vocabulary items focused on practical expressions
3. Include formal and casual Malay variants
4. Create practice scenarios for work/life/tech contexts
5. Generate toggle quiz questions for active recall

Return ONLY valid JSON wrapped between:
<<<JSON_START>>>
{{
  "theme": "...",
  "vocabulary_focus": [...],
  "practice_scenarios": {...},
  "quiz_toggle": [...]
}}
<<<JSON_END>>>

Keep expressions natural and commonly used in Malaysia.
"""
```

### 5.6 Notion Block Structure (Notion块结构)
```
Page Title: 📅 2024-01-16 - Office Communication

🏢 Work Scenario
├── 💼 Key Vocabulary (heading_2)
├── 📝 Expressions (paragraph blocks)
└── ❓ Practice Quiz (toggle blocks)

☕ Life Scenario
└── (same structure)

💻 Tech Scenario
└── (same structure)
```

## 6. Development & Deployment (开发部署)

### 6.1 Local Development Setup (本地开发设置)
```bash
# 1. Clone and setup
git clone <your-repo>
cd ai-trilingual-coach

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Test locally
python main.py
```

### 6.2 GitHub Actions Setup (自动化部署)
1. Go to repository Settings → Secrets and variables → Actions
2. Add these secrets:
   - `GEMINI_API_KEY`
   - `NOTION_TOKEN`
   - `NOTION_DATABASE_ID`
3. The workflow will run daily at 8 AM Malaysia time

### 6.3 Testing Checklist (测试清单)
- [ ] Local run creates Notion page successfully
- [ ] Vocabulary items display correctly in three languages
- [ ] Toggle blocks work for quiz questions
- [ ] Formal/Casual Malay distinction is clear
- [ ] Theme rotation works properly
- [ ] Error handling for API failures

## 7. Usage Flow (使用流程)

### 7.1 For Users (用户使用)
1. **Daily Notification**: Receive Notion notification at 8 AM
2. **Open Page**: Click to view today's lesson
3. **Learn Vocabulary**: Study the 5-8 vocabulary items
4. **Practice Scenarios**: Read through work/life/tech examples
5. **Take Quiz**: Click toggles to test yourself
6. **Mark Complete**: Check the completed box

### 7.2 For Developers (开发者维护)
1. **Monitor Logs**: Check GitHub Actions logs for errors
2. **Update Themes**: Modify theme rotation in environment
3. **Adjust Prompts**: Refine AI prompts for better content
4. **Database Cleanup**: Archive old pages periodically