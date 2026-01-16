"""
Notion Page Builder for AI Trilingual Coach
Constructs and publishes Notion pages with complex block structures
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from notion_client import Client

from config import NOTION_TOKEN, NOTION_DATABASE_ID, NOTION_API_VERSION

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionPageBuilder:
    """Builds and publishes Notion pages for trilingual lessons"""

    def __init__(self):
        """Initialize Notion client"""
        self.notion = Client(auth=NOTION_TOKEN, notion_version=NOTION_API_VERSION)
        logger.info("Initialized Notion client")

    def create_page(self, content_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new Notion page with the generated content

        Args:
            content_data: Generated content from AI

        Returns:
            Optional[str]: Page ID if successful, None if failed
        """
        try:
            # Prepare page properties
            page_title = self._generate_page_title(content_data)
            properties = self._build_page_properties(content_data, page_title)

            # Build page content blocks
            blocks = self._build_page_blocks(content_data)

            # Create the page
            response = self.notion.pages.create(
                parent={"database_id": NOTION_DATABASE_ID},
                properties=properties,
                children=blocks
            )

            page_id = response["id"]
            logger.info(f"Successfully created Notion page: {page_id}")
            return page_id

        except Exception as e:
            logger.error(f"Failed to create Notion page: {e}")
            return None

    def _generate_page_title(self, content_data: Dict[str, Any]) -> str:
        """
        Generate page title with date and theme

        Args:
            content_data: Content data

        Returns:
            str: Formatted page title
        """
        today = datetime.now()
        date_str = today.strftime("%Y-%m-%d")
        theme = content_data.get('theme', 'Daily Lesson')

        return f"📅 {date_str} - {theme}"

    def _build_page_properties(self, content_data: Dict[str, Any], title: str) -> Dict[str, Any]:
        """
        Build Notion page properties

        Args:
            content_data: Content data
            title: Page title

        Returns:
            Dict: Notion page properties
        """
        theme = content_data.get('theme', 'Daily Lesson')

        # Map theme to Notion select option
        theme_mapping = {
            'Office Communication': 'Work',
            'Daily Life': 'Life',
            'Technology & Development': 'Tech'
        }
        notion_theme = theme_mapping.get(theme, 'Work')

        vocab_count = len(content_data.get('vocabulary_focus', []))

        return {
            "Title": {
                "title": [{"text": {"content": title}}]
            },
            "Theme": {
                "select": {"name": notion_theme}
            },
            "Date": {
                "date": {"start": datetime.now().isoformat()}
            },
            "Vocabulary Count": {
                "number": vocab_count
            },
            "Completed": {
                "checkbox": False
            }
        }

    def _build_page_blocks(self, content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build the complete page content blocks

        Args:
            content_data: Content data

        Returns:
            List[Dict]: Notion blocks
        """
        blocks = []

        # Add theme introduction
        blocks.extend(self._build_theme_intro(content_data))

        # Add vocabulary overview
        blocks.extend(self._build_vocabulary_overview(content_data))

        # Add three scenario sections
        scenario_order = ['work', 'life', 'tech']
        scenario_emojis = {'work': '🏢', 'life': '☕', 'tech': '💻'}
        scenario_titles = {
            'work': 'Work Scenario',
            'life': 'Life Scenario',
            'tech': 'Tech Scenario'
        }

        for scenario in scenario_order:
            blocks.extend(
                self._build_scenario_section(
                    content_data,
                    scenario,
                    scenario_emojis[scenario],
                    scenario_titles[scenario]
                )
            )

        return blocks

    def _build_theme_intro(self, content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build theme introduction section

        Args:
            content_data: Content data

        Returns:
            List[Dict]: Notion blocks
        """
        theme = content_data.get('theme', 'Daily Lesson')
        vocab_count = len(content_data.get('vocabulary_focus', []))

        return [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"text": {"content": f"🎯 {theme}"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": f"Today's lesson focuses on {vocab_count} practical expressions for {theme.lower()}. "}},
                        {"text": {"content": "Practice switching between English, Chinese, and Malay!"}, "annotations": {"italic": True}}
                    ]
                }
            }
        ]

    def _build_vocabulary_overview(self, content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build vocabulary overview section

        Args:
            content_data: Content data

        Returns:
            List[Dict]: Notion blocks
        """
        vocab_items = content_data.get('vocabulary_focus', [])

        blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "🎯 Key Vocabulary"}}]
                }
            }
        ]

        for item in vocab_items:
            concept = item.get('concept', '')
            expressions = item.get('expressions', {})

            # Add concept as bold text
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": concept}, "annotations": {"bold": True}},
                        {"text": {"content": " | "}},
                        {"text": {"content": expressions.get('en', '')}, "annotations": {"code": True}},
                        {"text": {"content": " | "}},
                        {"text": {"content": expressions.get('cn', '')}, "annotations": {"code": True}},
                        {"text": {"content": " | "}},
                        {"text": {"content": expressions.get('bm_formal', '')}, "annotations": {"code": True}},
                        {"text": {"content": " | "}},
                        {"text": {"content": expressions.get('bm_casual', '')}, "annotations": {"code": True}}
                    ]
                }
            })

        return blocks

    def _build_scenario_section(self, content_data: Dict[str, Any], scenario: str,
                               emoji: str, title: str) -> List[Dict[str, Any]]:
        """
        Build a scenario section (Work/Life/Tech)

        Args:
            content_data: Content data
            scenario: Scenario key ('work', 'life', 'tech')
            emoji: Section emoji
            title: Section title

        Returns:
            List[Dict]: Notion blocks for this scenario
        """
        blocks = []

        # Section header
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"text": {"content": f"{emoji} {title}"}}]
            }
        })

        scenarios = content_data.get('practice_scenarios', {})
        scenario_data = scenarios.get(scenario, {})

        # Scenario description
        scenario_desc = scenario_data.get('scenario', '')
        if scenario_desc:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": f"💼 {scenario_desc}"}}]
                }
            })

        # Key phrases (formal/casual distinction)
        key_phrases = scenario_data.get('key_phrases', [])
        if key_phrases:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": "🔑 Key Phrases:"}, "annotations": {"bold": True}}]
                }
            })

            # Find relevant vocabulary for this scenario
            vocab_items = content_data.get('vocabulary_focus', [])
            relevant_vocab = self._find_relevant_vocab(vocab_items, key_phrases)

            for vocab in relevant_vocab:
                expressions = vocab.get('expressions', {})

                # Formal Malay (quote block - blue)
                if expressions.get('bm_formal'):
                    blocks.append({
                        "object": "block",
                        "type": "quote",
                        "quote": {
                            "rich_text": [
                                {"text": {"content": f"🇲🇾 Formal: {expressions['bm_formal']}"}},
                                {"text": {"content": f" | 🇬🇧 {expressions.get('en', '')}"}},
                                {"text": {"content": f" | 🇨🇳 {expressions.get('cn', '')}"}}
                            ],
                            "color": "blue"
                        }
                    })

                # Casual Malay (paragraph block - orange)
                if expressions.get('bm_casual'):
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"text": {"content": f"🇲🇾 Casual: {expressions['bm_casual']}"}},
                                {"text": {"content": f" | 🇬🇧 {expressions.get('en', '')}"}},
                                {"text": {"content": f" | 🇨🇳 {expressions.get('cn', '')}"}}
                            ],
                            "color": "orange"
                        }
                    })

        # Quiz section
        quiz_blocks = self._build_scenario_quiz(content_data, scenario)
        blocks.extend(quiz_blocks)

        return blocks

    def _find_relevant_vocab(self, vocab_items: List[Dict], key_phrases: List[str]) -> List[Dict]:
        """
        Find vocabulary items relevant to scenario key phrases

        Args:
            vocab_items: All vocabulary items
            key_phrases: Key phrases for this scenario

        Returns:
            List[Dict]: Relevant vocabulary items
        """
        relevant_vocab = []

        for vocab in vocab_items:
            concept = vocab.get('concept', '').lower()
            # Simple relevance check - if concept appears in key phrases
            for phrase in key_phrases:
                if concept in phrase.lower() or phrase.lower() in concept:
                    relevant_vocab.append(vocab)
                    break

        # If no relevant vocab found, return first few items
        if not relevant_vocab:
            relevant_vocab = vocab_items[:3]

        return relevant_vocab

    def _build_scenario_quiz(self, content_data: Dict[str, Any], scenario: str) -> List[Dict[str, Any]]:
        """
        Build quiz section for a scenario

        Args:
            content_data: Content data
            scenario: Scenario key

        Returns:
            List[Dict]: Quiz blocks
        """
        quiz_items = content_data.get('quiz_toggle', [])

        if not quiz_items:
            return []

        blocks = [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"text": {"content": "❓ Practice Quiz"}}]
                }
            }
        ]

        # Add toggle blocks for quiz questions
        for i, quiz_item in enumerate(quiz_items[:3], 1):  # Limit to 3 questions per scenario
            question = quiz_item.get('question', '')
            answer = quiz_item.get('answer', '')

            blocks.append({
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"text": {"content": f"Q{i}: {question}"}}],
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {"text": {"content": f"🇲🇾 {answer}"}, "annotations": {"bold": True}}
                                ]
                            }
                        }
                    ]
                }
            })

        return blocks

def publish_to_notion(content_data: Dict[str, Any]) -> Optional[str]:
    """
    Convenience function to publish content to Notion

    Args:
        content_data: Generated content data

    Returns:
        Optional[str]: Page ID if successful
    """
    builder = NotionPageBuilder()
    return builder.create_page(content_data)

if __name__ == "__main__":
    # Test the Notion builder with sample data
    sample_data = {
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
            }
        ],
        "practice_scenarios": {
            "work": {
                "scenario": "Email to boss about project delay",
                "key_phrases": ["I need more time", "Project timeline"]
            }
        },
        "quiz_toggle": [
            {
                "question": "How to say '项目延误了' in BM (formal)?",
                "answer": "Projek telah tertangguh"
            }
        ]
    }

    print("🧪 Testing Notion Page Builder...")
    page_id = publish_to_notion(sample_data)

    if page_id:
        print(f"✅ Page created successfully: {page_id}")
    else:
        print("❌ Failed to create page")
