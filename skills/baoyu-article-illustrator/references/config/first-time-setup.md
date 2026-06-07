---
name: first-time-setup
description: First-time setup flow for baoyu-article-illustrator preferences (qwenpaw)
---

# First-Time Setup

## Overview

When no saved preferences are found, guide user through a quick preference setup.

**⛔ BLOCKING OPERATION**: This setup MUST complete before ANY other workflow steps. Do NOT proceed to content analysis until preferences are saved.

## Setup Flow

```
No saved preferences found
        │
        ▼
Ask user in natural conversation:
  1. Watermark preference
  2. Default style preference
  3. Output directory preference
        │
        ▼
Save preferences to qwenpaw memory
        │
        ▼
Continue to Step 2 (analyze content)
```

## Questions to Ask

Ask in natural conversation — one at a time or together:

### 1. Watermark
"Would you like a watermark on generated illustrations? (e.g., your name/logo, or 'no watermark')"

### 2. Preferred Style
"Any preferred illustration style? (or I'll auto-select based on content)"
Suggestions if they want examples: vector-illustration, notion, warm, blueprint, watercolor, editorial

### 3. Save Location
Preferences will be saved to qwenpaw memory so they persist across sessions.

## Save Format

Save to qwenpaw memory (MEMORY.md or project config):

```yaml
baoyu-article-illustrator:
  preferences:
    watermark:
      enabled: false
      content: ""
      position: bottom-right
    preferred_style: null
    language: null
    default_output_dir: illustrations-subdir
```
