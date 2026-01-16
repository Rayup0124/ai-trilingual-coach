"""
AI Content Generator for AI Trilingual Coach
Generates daily trilingual vocabulary lessons using Google Gemini
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import time
import pathlib

from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GENERATE_CONTENT_PROMPT,
    MAX_VOCABULARY,
    THEME_ROTATION
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIContentGenerator:
    """AI content generator using Google Gemini"""

    def __init__(self):
        """Initialize Gemini client"""
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info(f"Initialized Gemini client with model: {GEMINI_MODEL}")
        # prepare raw response dir
        try:
            self._raw_dir = pathlib.Path("logs/raw_responses")
            self._raw_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            self._raw_dir = None

    def select_daily_theme(self) -> str:
        """
        Select theme based on current date
        Rotates through available themes
        """
        today = datetime.now()
        theme_index = today.day % len(THEME_ROTATION)
        theme = THEME_ROTATION[theme_index].strip()

        # Map theme codes to descriptive names
        theme_mapping = {
            'work': 'Office Communication',
            'life': 'Daily Life',
            'tech': 'Technology & Development'
        }

        return theme_mapping.get(theme, theme)

    def generate_prompt(self, theme: str) -> str:
        """
        Generate the complete prompt for AI

        Args:
            theme: Selected theme for the day

        Returns:
            str: Complete prompt with theme and requirements
        """
        return GENERATE_CONTENT_PROMPT.format(
            theme=theme,
            max_vocab=MAX_VOCABULARY
        )

    def extract_json_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from AI response using markers
        Based on BUILD_FROM_SOURCE parsing strategy

        Args:
            response_text: Raw AI response text

        Returns:
            Optional[Dict]: Parsed JSON data or None if parsing failed
        """
        try:
            # Method 1: Extract between markers
            start_marker = "<<<JSON_START>>>"
            end_marker = "<<<JSON_END>>>"

            start_idx = response_text.find(start_marker)
            end_idx = response_text.find(end_marker)

            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx + len(start_marker):end_idx].strip()
            else:
                # Method 2: Find first { and last }
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')

                if start_idx == -1 or end_idx == -1:
                    logger.error("No JSON markers or braces found in response")
                    return None

                json_text = response_text[start_idx:end_idx + 1]

            # Clean up common issues
            json_text = self._clean_json_text(json_text)

            # Parse JSON
            data = json.loads(json_text)
            logger.info("Successfully parsed JSON response")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Raw response text: {response_text[:500]}...")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {e}")
            return None

    def _clean_json_text(self, json_text: str) -> str:
        """
        Clean JSON text to handle common formatting issues

        Args:
            json_text: Raw JSON text

        Returns:
            str: Cleaned JSON text
        """
        # Remove markdown code fences
        json_text = re.sub(r'```\w*\n?', '', json_text)
        json_text = re.sub(r'```', '', json_text)

        # Normalize quotes
        json_text = json_text.replace('“', '"').replace('”', '"').replace('“', '"')
        json_text = json_text.replace("’", "'").replace("‘", "'")

        # Remove ellipses which often break JSON ("..." or "…")
        json_text = json_text.replace("...", "").replace("…", "")

        # Remove trailing commas before closing braces/brackets
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)

        # Remove control chars
        json_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', json_text)

        # Attempt to balance braces/brackets if truncated
        open_braces = json_text.count('{')
        close_braces = json_text.count('}')
        if open_braces > close_braces:
            json_text = json_text + ('}' * (open_braces - close_braces))
        open_brackets = json_text.count('[')
        close_brackets = json_text.count(']')
        if open_brackets > close_brackets:
            json_text = json_text + (']' * (open_brackets - close_brackets))

        return json_text.strip()

    def _save_raw_response(self, text: str) -> Optional[str]:
        """Save raw model response for debugging. Returns path or None."""
        try:
            if not self._raw_dir:
                return None
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            path = self._raw_dir / f"resp_{ts}.txt"
            path.write_text(text, encoding="utf-8")
            return str(path)
        except Exception:
            return None

    def _call_model(self, prompt: str, temperature: float = 0.7, max_output_tokens: int = 4000) -> Optional[str]:
        """Call model and return response text (or None)."""
        try:
            resp = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=temperature, max_output_tokens=max_output_tokens)
            )
            if not resp.candidates:
                return None
            # concatenate parts safely
            parts = []
            for p in resp.candidates[0].content.parts:
                text = getattr(p, "text", None)
                if text is None:
                    try:
                        text = str(p)
                    except Exception:
                        text = ""
                parts.append(text)
            return "".join(parts)
        except Exception as e:
            logger.error(f"Model call error: {e}")
            return None

    def validate_response_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate the structure of parsed response data

        Args:
            data: Parsed JSON data

        Returns:
            bool: True if data structure is valid
        """
        required_keys = ['theme', 'vocabulary_focus', 'practice_scenarios', 'quiz_toggle']

        for key in required_keys:
            if key not in data:
                logger.error(f"Missing required key: {key}")
                return False

        # Validate vocabulary_focus structure
        vocab = data.get('vocabulary_focus', [])
        if not isinstance(vocab, list) or len(vocab) == 0:
            logger.error("vocabulary_focus must be non-empty list")
            return False

        for item in vocab:
            if not isinstance(item, dict):
                logger.error("vocabulary_focus items must be dictionaries")
                return False
            if 'concept' not in item or 'expressions' not in item:
                logger.error("vocabulary_focus items missing required fields")
                return False

        # Validate quiz_toggle structure
        quiz = data.get('quiz_toggle', [])
        if not isinstance(quiz, list):
            logger.error("quiz_toggle must be a list")
            return False

        for item in quiz:
            if not isinstance(item, dict) or 'question' not in item or 'answer' not in item:
                logger.error("quiz_toggle items missing required fields")
                return False

        return True

    def generate_daily_content(self) -> Optional[Dict[str, Any]]:
        """
        Generate daily trilingual content

        Returns:
            Optional[Dict]: Generated content or None if failed
        """
        try:
            # Select theme for today
            theme = self.select_daily_theme()
            logger.info(f"Selected theme: {theme}")

            # Generate prompt
            prompt = self.generate_prompt(theme)

            # Call Gemini API with retries and stricter fallback
            attempts = 3
            data = None
            last_raw = None
            for attempt in range(1, attempts + 1):
                temp = 0.7 if attempt == 1 else 0.0
                logger.info(f"Calling Gemini API (attempt {attempt}, temp={temp})...")
                response_text = self._call_model(prompt, temperature=temp, max_output_tokens=4000)
                if not response_text:
                    logger.error("No response from model")
                    continue
                last_raw = response_text
                logger.info(f"Received response ({len(response_text)} chars)")
                # try parse
                data = self.extract_json_from_response(response_text)
                if data:
                    break
                # save raw for debugging
                raw_path = self._save_raw_response(response_text)
                if raw_path:
                    logger.info(f"Saved raw response to {raw_path}")
                # tweak prompt for next attempt
                prompt = prompt + "\n\nReturn ONLY valid JSON between <<<JSON_START>>> and <<<JSON_END>>> with no extra text."

            if not data:
                logger.error("Failed to parse JSON from response")
                if last_raw:
                    logger.error(f"Raw response text: {last_raw[:2000]}")
                return None

            # Validate structure
            if not self.validate_response_data(data):
                logger.error("Response data validation failed")
                return None

            logger.info(f"Successfully generated content with {len(data.get('vocabulary_focus', []))} vocabulary items")
            return data

        except Exception as e:
            logger.error(f"Error generating daily content: {e}")
            return None

def generate_content() -> Optional[Dict[str, Any]]:
    """
    Convenience function to generate daily content

    Returns:
        Optional[Dict]: Generated content or None if failed
    """
    generator = AIContentGenerator()
    return generator.generate_daily_content()

if __name__ == "__main__":
    # Test the content generator
    print("Testing AI Content Generator...")
    content = generate_content()

    if content:
        print("Content generated successfully!")
        print(f"Theme: {content.get('theme')}")
        print(f"Vocabulary items: {len(content.get('vocabulary_focus', []))}")
        print(f"Quiz questions: {len(content.get('quiz_toggle', []))}")

        # Show first vocabulary item as example
        vocab = content.get('vocabulary_focus', [])
        if vocab:
            print("\nExample vocabulary:")
            item = vocab[0]
            print(f"Concept: {item.get('concept')}")
            expr = item.get('expressions', {})
            print(f"EN: {expr.get('en')}")
            print(f"CN: {expr.get('cn')}")
            print(f"BM Formal: {expr.get('bm_formal')}")
            print(f"BM Casual: {expr.get('bm_casual')}")
    else:
        print("Failed to generate content")