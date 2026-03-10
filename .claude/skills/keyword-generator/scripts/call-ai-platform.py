#!/usr/bin/env python3
"""Call an AI platform API with a query and return the response.

Usage: python3 call-ai-platform.py --platform <name> --api-key <key> --query "<query>" [--base-url <url>]

Supported platforms: perplexity, chatgpt, deepseek, doubao, qwen

Output: JSON to stdout with fields: platform, query, response, citations (if available).
Errors: stderr with descriptive messages.
"""

import argparse
import json
import sys

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)


PLATFORM_CONFIG = {
    "perplexity": {
        "base_url": "https://api.perplexity.ai",
        "model": "sonar",
    },
    "chatgpt": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "doubao": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-1.5-pro-32k",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
    },
}


def call_platform(platform: str, api_key: str, query: str, base_url: str | None = None) -> dict:
    if platform not in PLATFORM_CONFIG:
        print(f"ERROR: Unknown platform '{platform}'. Supported: {list(PLATFORM_CONFIG.keys())}", file=sys.stderr)
        sys.exit(1)

    config = PLATFORM_CONFIG[platform]
    client = OpenAI(
        api_key=api_key,
        base_url=base_url or config["base_url"],
    )

    try:
        kwargs = {
            "model": config["model"],
            "messages": [{"role": "user", "content": query}],
        }

        # Perplexity returns citations in the response
        response = client.chat.completions.create(**kwargs)

        result = {
            "platform": platform,
            "query": query,
            "response": response.choices[0].message.content,
        }

        # Extract citations if available (Perplexity)
        if hasattr(response, "citations") and response.citations:
            result["citations"] = response.citations

        return result

    except Exception as e:
        print(f"ERROR: {platform} API call failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Call AI platform API")
    parser.add_argument("--platform", required=True, choices=list(PLATFORM_CONFIG.keys()))
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--base-url", default=None, help="Override base URL")
    args = parser.parse_args()

    result = call_platform(args.platform, args.api_key, args.query, args.base_url)
    print(json.dumps(result, ensure_ascii=False, indent=2))
