#!/usr/bin/env python3
"""
AI Trilingual Coach - Main Entry Point
Generates daily trilingual vocabulary lessons and publishes to Notion
"""

import sys
import logging
from datetime import datetime
import os
import json

from config import validate_config, APP_NAME, APP_VERSION
from worker_lang import generate_content
from notion_builder import publish_to_notion

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_trilingual_coach.log')
    ]
)
logger = logging.getLogger(__name__)

def run() -> int:
    """
    Main execution function

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    start_time = datetime.now()
    logger.info(f"🚀 Starting {APP_NAME} v{APP_VERSION}")

    try:
        # Step 1: Validate configuration
        logger.info("📋 Step 1: Validating configuration...")
        if not validate_config():
            logger.error("❌ Configuration validation failed")
            return 1

        # Step 2: Generate AI content
        logger.info("🤖 Step 2: Generating daily content...")
        content_data = generate_content()

        if not content_data:
            logger.error("❌ Failed to generate content")
            return 1

        logger.info(f"✅ Generated content: {content_data.get('theme')} with {len(content_data.get('vocabulary_focus', []))} vocabulary items")

        # Step 3: Publish to Notion
        logger.info("📝 Step 3: Publishing to Notion...")
        page_id = publish_to_notion(content_data)

        if not page_id:
            logger.error("❌ Failed to publish to Notion")
            return 1

        # Step 4: Success summary
        end_time = datetime.now()
        duration = end_time - start_time

        logger.info("Success! Daily lesson published")
        logger.info(f"Theme: {content_data.get('theme')}")
        logger.info(f"Vocabulary items: {len(content_data.get('vocabulary_focus', []))}")
        logger.info(f"Quiz questions: {len(content_data.get('quiz_toggle', []))}")
        logger.info(f"Notion page ID: {page_id}")
        logger.info(f"Total time: {duration.total_seconds():.2f} seconds")
        # Optionally write generated JSON to repository (workflow can commit it)
        write_json_flag = os.getenv("WRITE_JSON", "0") == "1"
        if "--write-json" in sys.argv:
            write_json_flag = True

        if write_json_flag and content_data:
            try:
                os.makedirs("data", exist_ok=True)
                date_str = datetime.now().strftime("%Y-%m-%d")
                filename = f"data/{date_str}.json"
                with open(filename, "w", encoding="utf-8") as fh:
                    json.dump(content_data, fh, ensure_ascii=False, indent=2)
                logger.info(f"Wrote generated JSON to {filename}")
            except Exception as e:
                logger.error(f"Failed to write JSON file: {e}")

        return 0

    except KeyboardInterrupt:
        logger.info("⏹️  Execution interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}", exc_info=True)
        return 1

def test_mode() -> int:
    """
    Test mode - runs without publishing to Notion
    Useful for development and testing

    Returns:
        int: Exit code
    """
    logger.info("🧪 Running in test mode (no Notion publishing)")

    try:
        # Validate config
        if not validate_config():
            return 1

        # Generate content only
        content_data = generate_content()

        if not content_data:
            logger.error("❌ Content generation failed")
            return 1

        # Display results
        print("\n" + "="*50)
        print("📊 GENERATED CONTENT SUMMARY")
        print("="*50)
        print(f"Theme: {content_data.get('theme')}")
        print(f"Vocabulary Items: {len(content_data.get('vocabulary_focus', []))}")

        # Show sample vocabulary
        vocab = content_data.get('vocabulary_focus', [])
        if vocab:
            print("\n📖 Sample Vocabulary:")
            item = vocab[0]
            expr = item.get('expressions', {})
            print(f"  Concept: {item.get('concept')}")
            print(f"  EN: {expr.get('en')}")
            print(f"  CN: {expr.get('cn')}")
            print(f"  BM Formal: {expr.get('bm_formal')}")
            print(f"  BM Casual: {expr.get('bm_casual')}")

        # Show scenarios
        scenarios = content_data.get('practice_scenarios', {})
        print(f"\n🏢 Scenarios: {len(scenarios)}")

        # Show quiz
        quiz = content_data.get('quiz_toggle', [])
        print(f"❓ Quiz Questions: {len(quiz)}")
        if quiz:
            print(f"  Sample: {quiz[0].get('question')}")

        print("\n✅ Test completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        exit_code = test_mode()
    else:
        exit_code = run()

    sys.exit(exit_code)