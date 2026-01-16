#!/usr/bin/env python3
"""
List available Gemini / Google GenAI models for the current API key.
Run this locally by exporting GEMINI_API_KEY, or run as a GitHub Actions workflow
that injects the secret.
"""
import os
import sys

try:
    from google import genai
except Exception as e:
    print("Missing dependency 'google-genai'. Install with: pip install google-genai")
    raise


def list_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set in environment. Exiting.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    print("Listing models available to this API key...\n")
    models = client.models.list()
    for m in models:
        # Print name and any metadata that helps (fallback to dict)
        name = getattr(m, "name", None) or getattr(m, "model", None) or str(m)
        supported = getattr(m, "supported_methods", None)
        print(f"- {name}  supported_methods={supported}")


if __name__ == "__main__":
    list_models()


