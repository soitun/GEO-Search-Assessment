# GitCode API Specification

## Status: Confirmed ✅ (requires auth)

MindSpore repository at `https://gitcode.com/mindspore/mindspore` is hosted on GitCode (AtomGit). The API requires a `private-token` header for authentication.

## Base URL

```
https://api.gitcode.com/api/v5
```

## Authentication

All requests require a `private-token` header:

```
private-token: <GITCODE_TOKEN>
```

Token can be generated at GitCode account settings. Store in `.env` as `GITCODE_TOKEN`.

## Endpoints

### List Repository Issues

```
GET /repos/{owner}/{repo}/issues?state={state}&sort={sort}&direction={direction}&page={page}&per_page={per_page}
```

Parameters:
- `owner`: Repository owner (e.g., `mindspore`)
- `repo`: Repository name (e.g., `mindspore`)
- `state`: `open`, `closed`, `all` (default: `all`)
- `sort`: `created`, `updated` (default: `created`)
- `direction`: `asc`, `desc` (default: `desc`)
- `page`: Page number (default: `1`)
- `per_page`: Items per page, max 100 (default: `20`)

### Issue Object Fields

```json
{
  "id": 12345,
  "number": "I123AB",
  "title": "MindSpore GPU 版本安装报错",
  "state": "open",
  "labels": [
    {"name": "bug", "color": "#d73a4a"}
  ],
  "comments": 15,
  "created_at": "2026-02-15T10:00:00+08:00",
  "updated_at": "2026-02-20T08:30:00+08:00",
  "html_url": "https://gitcode.com/mindspore/mindspore/issues/I123AB"
}
```

## Target Repository

```
Owner: mindspore
Repo:  mindspore
URL:   https://gitcode.com/mindspore/mindspore/issues
```

## Rate Limits

GitCode API rate limits are not publicly documented. The script fetches 1-3 pages typically (50-150 issues), which should be within limits.

## Error Responses

- `400`: Missing `private-token` header
- `403`: Invalid token or insufficient scopes (needs `read_projects`)
- `404`: Repository not found

## Fallback

If `GITCODE_TOKEN` is not set or API fails, Path 2 (issue) is skipped entirely. No LLM fallback — issue data must come from real sources.
