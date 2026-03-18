---
name: twitter
description: Post tweets on X (Twitter).
---

# Twitter Skill

This skill provides access to the `twitter` command-line tool for posting on X (Twitter). Before executing any commands, ensure that `twitter` is installed and the virtual environment is properly set up.

## 1. Post Tweet

**Purpose**: Publish a text tweet to X (Twitter).
**When to Use**: When you want to post an update, announcement, or any content to X.
**Parameters**:

- `text` (str) — The content of the tweet. **Required.** Maximum 280 characters.

**Execution Steps**:

```bash
twitter post_tweet "Hello from my bot!"
```

Returns the published tweet's `id` and `text`.
