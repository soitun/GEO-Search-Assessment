# Forum API Specification

## Status: Pending Investigation

The MindSpore community forum (mindspore.cn) API availability has not been confirmed yet.

## Expected Endpoints (if available)

```
GET /api/topics?sort=views&limit={N}
GET /api/topics?sort=replies&limit={N}
```

## Expected Response Format

```json
{
  "topics": [
    {
      "id": 12345,
      "title": "MindSpore GPU 版本安装报错求助",
      "views": 1520,
      "replies": 23,
      "tags": ["安装", "GPU"],
      "created_at": "2026-02-15T10:00:00Z"
    }
  ]
}
```

## Fallback

If the forum API is unavailable, the skill falls back to LLM-generated usage questions.
Update `scripts/fetch-forum-posts.py` once the API is confirmed.
