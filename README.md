# AI Trilingual Coach 🤖🌏

An automated AI language tutor that generates daily trilingual vocabulary lessons (English, Chinese, Malay) and publishes them to Notion for interactive learning.

## 🎯 What It Does

- **Daily Vocabulary Learning**: Generates 5-8 practical expressions daily
- **Trilingual Support**: English + Chinese + Malay (Formal & Casual variants)
- **Interactive Learning**: Toggle-based quiz system in Notion
- **Context-Aware**: Distinguishes between formal/casual Malay usage
- **Automated Delivery**: Runs daily via GitHub Actions

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Google Gemini API key ([Get here](https://makersuite.google.com/app/apikey))
- Notion account with Internal Integration
- GitHub account (for automation)

### 2. Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd ai-trilingual-coach

# Create virtual environment
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Notion Setup
1. Create a new Notion database
2. Add these properties:
   - `Title` (Title): Daily lesson title
   - `Theme` (Select): Options: `Work`, `Life`, `Tech`
   - `Date` (Date): Creation date
   - `Vocabulary Count` (Number): Number of vocabulary items
   - `Completed` (Checkbox): User completion status

3. Create an Internal Integration:
   - Go to [Notion Integrations](https://www.notion.com/my-integrations)
   - Copy the integration token
   - Share your database with the integration

### 4. Test Locally
```bash
# Test without publishing to Notion
python main.py --test

# Run full pipeline (requires valid API keys)
python main.py
```

### 5. Deploy to GitHub Actions
1. Push code to GitHub
2. Go to repository Settings → Secrets and variables → Actions
3. Add these secrets:
   - `GEMINI_API_KEY`
   - `NOTION_TOKEN`
   - `NOTION_DATABASE_ID`
4. The workflow runs daily at 8 AM Malaysia time

## 📁 Project Structure

```
ai-trilingual-coach/
├── main.py                    # Main entry point
├── worker_lang.py            # AI content generator
├── notion_builder.py         # Notion page builder
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── .github/workflows/
    └── daily_run.yml        # GitHub Actions workflow
```

## 🎨 Daily Lesson Structure

Each day generates a lesson like this:

### 📅 2024-01-16 - Office Communication

**🎯 Key Vocabulary:**
- schedule meeting | 安排会议 | jadualkan mesyuarat
- deadline approaching | 截止日期临近 | tarikh akhir mendekati

**🏢 Work Scenario:**
- 💼 Formal: Mari kita jadualkan mesyuarat (Blue quote block)
- 💼 Casual: Jom schedule meeting (Orange paragraph block)

**❓ Practice Quiz:**
- ▶️ Q1: How to say '项目延误了' in BM? *(Click to reveal answer)*

## 🛠️ Configuration

### Required Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key
- `NOTION_TOKEN`: Notion integration token
- `NOTION_DATABASE_ID`: Target Notion database ID

### Optional Environment Variables
- `GEMINI_MODEL`: AI model (default: `models/gemini-1.5-flash`)
- `MAX_VOCABULARY`: Vocabulary items per day (default: 6)
- `THEME_ROTATION`: Daily themes (default: `work,life,tech`)

## 🔧 Customization

### Adding New Themes
Edit `THEME_ROTATION` in environment variables:
```
THEME_ROTATION=work,life,tech,culture,travel
```

### Modifying AI Prompts
Edit `GENERATE_CONTENT_PROMPT` in `config.py` to change lesson generation behavior.

### Adjusting Vocabulary Count
Set `MAX_VOCABULARY` environment variable to change daily vocabulary items.

## 📊 Learning Flow

1. **Daily Notification**: Notion sends notification at 8 AM
2. **Vocabulary Study**: Learn 5-8 new expressions in three languages
3. **Context Practice**: See formal/casual Malay usage in different scenarios
4. **Active Recall**: Click toggles to test yourself
5. **Progress Tracking**: Mark lessons as completed

## 🐛 Troubleshooting

### Common Issues

**"API key not valid"**
- Check your Gemini API key is correct
- Ensure the key has sufficient quota

**"Notion API error"**
- Verify integration token is correct
- Ensure database is shared with the integration
- Check database ID is correct

**"Workflow failed"**
- Check GitHub Actions logs
- Verify all secrets are set correctly
- Ensure `.env` file is not committed

### Debug Mode
Run with verbose logging:
```bash
python main.py 2>&1 | tee debug.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `python main.py --test`
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use and modify as needed.

## 🙏 Acknowledgments

- Built with [Google Gemini](https://gemini.google.com/)
- Powered by [Notion API](https://developers.notion.com/)
- Inspired by Malaysian multilingual education needs
