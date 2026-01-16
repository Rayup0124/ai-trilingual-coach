"""
Configuration management for AI Trilingual Coach
Handles environment variables and application settings
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def require_env_var(name: str) -> str:
    """
    Get required environment variable or exit with error

    Args:
        name: Environment variable name

    Returns:
        str: Environment variable value

    Raises:
        SystemExit: If environment variable is not set
    """
    value = os.getenv(name)
    if not value:
        print(f"Error: Required environment variable '{name}' is not set!")
        print("Please set it in your .env file or environment variables.")
        sys.exit(1)
    return value

def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get optional environment variable with default value

    Args:
        name: Environment variable name
        default: Default value if not set

    Returns:
        Optional[str]: Environment variable value or default
    """
    return os.getenv(name, default)

# Required environment variables
GEMINI_API_KEY = require_env_var('GEMINI_API_KEY')
NOTION_TOKEN = require_env_var('NOTION_TOKEN')
NOTION_DATABASE_ID = require_env_var('NOTION_DATABASE_ID')

# Optional environment variables with defaults
GEMINI_MODEL = get_env_var('GEMINI_MODEL', 'models/gemini-1.5-flash')

# Parse MAX_VOCABULARY safely: handle None or empty-string from environment (e.g. GitHub Actions empty secrets)
_max_vocab_raw = get_env_var('MAX_VOCABULARY', None)
try:
    if _max_vocab_raw is None or str(_max_vocab_raw).strip() == '':
        MAX_VOCABULARY = 6
    else:
        MAX_VOCABULARY = int(str(_max_vocab_raw).strip())
except ValueError:
    print(f"Invalid MAX_VOCABULARY value '{_max_vocab_raw}', falling back to 6")
    MAX_VOCABULARY = 6

# Parse THEME_ROTATION into a cleaned list and filter out empty entries
_themes_raw = get_env_var('THEME_ROTATION', 'work,life,tech')
THEME_ROTATION = [t.strip() for t in str(_themes_raw).split(',') if t.strip()]
# If THEME_ROTATION ended up empty (e.g. secret set but empty), fall back to defaults
if not THEME_ROTATION:
    THEME_ROTATION = ['work', 'life', 'tech']
    print("THEME_ROTATION was empty; defaulting to: work,life,tech")

# Application constants
APP_NAME = "AI Trilingual Coach"
APP_VERSION = "1.0.0"

# Notion configuration
NOTION_API_VERSION = "2022-06-28"

# AI Prompt templates
GENERATE_CONTENT_PROMPT = """
You are a Malaysian language tutor specializing in trilingual education.

Generate a daily vocabulary lesson with the following requirements:
1. Theme: {theme}
2. {max_vocab} vocabulary items focused on practical expressions
3. Include formal and casual Malay variants
4. Create practice scenarios for work/life/tech contexts
5. Generate toggle quiz questions for active recall

Return ONLY valid JSON wrapped between:
<<<JSON_START>>>
{{
  "theme": "...",
  "vocabulary_focus": [
    {{
      "concept": "example concept",
      "expressions": {{
        "en": "English expression",
        "cn": "Chinese expression",
        "bm_formal": "Formal Malay expression",
        "bm_casual": "Casual Malay expression"
      }}
    }}
  ],
  "practice_scenarios": {{
    "work": {{
      "scenario": "Work scenario description",
      "key_phrases": ["phrase1", "phrase2", "phrase3"]
    }},
    "life": {{
      "scenario": "Life scenario description",
      "key_phrases": ["phrase1", "phrase2", "phrase3"]
    }},
    "tech": {{
      "scenario": "Tech scenario description",
      "key_phrases": ["phrase1", "phrase2", "phrase3"]
    }}
  }},
  "quiz_toggle": [
    {{
      "question": "Question in English/Chinese?",
      "answer": "Answer in Malay"
    }}
  ]
}}
<<<JSON_END>>>

Keep expressions natural and commonly used in Malaysia.
Focus on practical communication scenarios.
"""

def validate_config():
    """
    Validate configuration settings
    """
    print("Validating configuration...")

    # Check required variables
    required_vars = ['GEMINI_API_KEY', 'NOTION_TOKEN', 'NOTION_DATABASE_ID']
    for var in required_vars:
        if not globals().get(var):
            print(f"Missing required variable: {var}")
            return False

    # Validate theme rotation
    if not THEME_ROTATION:
        print("THEME_ROTATION cannot be empty")
        return False

    print("Configuration validation passed")
    return True

if __name__ == "__main__":
    # When run directly, validate configuration
    validate_config()
    print("\n📋 Current Configuration:")
    print(f"  Gemini Model: {GEMINI_MODEL}")
    print(f"  Max Vocabulary: {MAX_VOCABULARY}")
    print(f"  Theme Rotation: {', '.join(THEME_ROTATION)}")
    print(f"  Notion Database ID: {NOTION_DATABASE_ID[:8]}...")