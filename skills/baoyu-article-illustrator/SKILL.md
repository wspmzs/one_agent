---
name: baoyu-article-illustrator
description: "This skill should be used to analyze article structure, identify positions requiring visual aids, and generate illustrations with Type × Style two-dimension approach. Use when user asks to 'illustrate article', 'add images', 'generate images for article', '为文章配图', 'add illustrations to article', 'add visuals to content', '给文章配图', '文章插图'."
metadata:
  qwenpaw:
    emoji: "🖼️"
    requires: {}
---

# Article Illustrator

Analyze articles, identify illustration positions, generate images with Type × Style consistency.

## Two Dimensions

| Dimension | Controls | Examples |
|-----------|----------|----------|
| **Type** | Information structure | infographic, scene, flowchart, comparison, framework, timeline |
| **Style** | Visual aesthetics | notion, warm, minimal, blueprint, watercolor, elegant |

Combine freely: infographic + blueprint, scene + watercolor, etc.

## Types

| Type | Best For |
|------|----------|
| `infographic` | Data, metrics, technical |
| `scene` | Narratives, emotional |
| `flowchart` | Processes, workflows |
| `comparison` | Side-by-side, options |
| `framework` | Models, architecture |
| `timeline` | History, evolution |

## Styles

See [references/styles.md](references/styles.md) for Core Styles, full gallery, and Type × Style compatibility.

## Workflow

```
Step 1: Pre-check → Read context & check references
Step 2: Analyze content → Type, density, positions
Step 3: Confirm settings → Ask user 3-4 questions
Step 4: Generate outline → Outline each illustration
Step 5: Generate images → aigc-prompt + jimeng
Step 6: Finalize → Insert & summarize
```

### Step 1: Pre-check

1. Read the article content from user (paste, file path, or URL)
2. Check if user provided reference images:
   - File path provided → save to `references/NN-ref-{slug}.png`
   - No path but image in context → ask user for file path
   - Analyzed verbally → extract style/palette info, append to prompts
3. Determine input type:
   - File path → ask output directory preference
   - Pasted content → use `illustrations/{topic-slug}/`

### Step 2: Analyze Content

| Analysis | Output |
|----------|--------|
| Content type | Technical / Tutorial / Methodology / Narrative |
| Purpose | information / visualization / imagination |
| Core arguments | 2-5 main points to visualize |
| Positions | Where illustrations add value |

**CRITICAL**: If article uses metaphors, visualize the **underlying concept**, NOT literal image.

### Step 3: Confirm Settings

Ask user 3-4 questions in natural conversation. Do NOT skip.

| Q | Options |
|---|---------|
| **Q1: Type** | [Recommended based on analysis], infographic, scene, flowchart, comparison, framework, timeline, mixed |
| **Q2: Density** | minimal (1-2), balanced (3-5), per-section (Recommended), rich (6+) |
| **Q3: Style** | [Recommended based on compatibility], or choose from Core Styles |
| Q4: Language | Only ask when article language differs from user's language |

**Core Styles** for quick selection:

| Core Style | Best For |
|------------|----------|
| `vector-illustration` | Knowledge articles, tutorials, tech content |
| `minimal-flat` (notion) | General, knowledge sharing, SaaS |
| `sci-fi` (blueprint) | AI, frontier tech, system design |
| `hand-drawn` (sketch/warm) | Relaxed, reflective, casual |
| `editorial` | Processes, data, journalism |
| `scene` (warm/watercolor) | Narratives, emotional, lifestyle |

### Step 4: Generate Outline

Save `outline.md` with frontmatter (type, density, style, image_count) and entries:

```yaml
## Illustration 1
**Position**: [section/paragraph]
**Purpose**: [why]
**Visual Content**: [what to show]
**Filename**: 01-infographic-concept-name.png
```

### Step 5: Generate Images ⛔ BLOCKING

**Prompt files MUST be saved before ANY image generation.**

1. For each illustration, create a prompt file per [references/prompt-construction.md](references/prompt-construction.md)
2. Save to `prompts/NN-{type}-{slug}.md` with YAML frontmatter
3. Follow type-specific templates: Layout / ZONES / LABELS / COLORS / STYLE / ASPECT
4. Use **actual article data** for LABELS (real numbers, terms, metrics)
5. Optionally use **`aigc-prompt` skill** to optimize prompts
6. Dispatch to configured image generation backend (see [Backend Configuration](#backend-configuration))
7. Apply watermark if stored in preferences
8. Retry once on failure, then log and continue

#### jimeng MCP (default backend, built-in)

**⚠️ Anti-pitfall checklist — read before calling `generate_image`:**

| Rule | Why |
|------|-----|
| **Always `list_models()` first** | 确认账户已激活哪些模型，别盲猜 |
| **Never use `stream=true`** | 流式输出返回格式与工具解析器不兼容，直接崩 |
| **Use `doubao-seedream-5-0-260128`** | 当前最稳定的旗舰模型 |
| **Grayscale fallback: `5-0-lite` > `4-5`** | 5.0 不可用时逐级降级 |

**Correct invocation:**
```python
generate_image(
    prompt="...",
    size="16:9",
    model="doubao-seedream-5-0-260128"
    # stream: omit (default false)
)
```

**Reference images**: use `generate_image_with_reference(prompt, image_urls=[...], size="16:9")`.

**Download**: jimeng 返回 jpeg URL（24h 有效）。使用 Python `urllib.request.urlretrieve(url, outpath)` 下载到本地。**不用浏览器 open** — 浏览器会弹出下载对话框而非展示。

Download script pattern:
```python
import urllib.request
urllib.request.urlretrieve(url, r"illustrations/{slug}/NN-{type}-{slug}.png")
```

### Backend Configuration

See [references/config/backends.md](references/config/backends.md) for multi-backend setup (jimeng / nano banana pro / GPT-image-2 / custom).

Switch backend by editing the skill's backend config. The skill always produces prompts first; backend choice only affects generation step.

### Step 6: Finalize

1. Insert `![description](path/NN-{type}-{slug}.png)` after corresponding paragraphs
2. Report summary to user:

```
Article Illustration Complete!

Article: [path] | Type: [type] | Density: [level] | Style: [style]
Images: X/N generated

Positions:
- 01-xxx → After [Section]
- 02-yyy → After [Section]
```

## Output Directory

```
illustrations/{topic-slug}/
├── references/           # if provided
├── outline.md
├── prompts/
└── NN-{type}-{slug}.png
```

Slug: 2-4 words, kebab-case. On conflict: append `-YYYYMMDD-HHMMSS`.

## Preferences (Memory)

Save user preferences to `memory/` or project config:

```yaml
baoyu-article-illustrator:
  watermark:
    enabled: false
    content: ""
    position: bottom-right
  preferred_style: null
  language: null
  default_output_dir: illustrations-subdir
```

On first use, ask user about watermark and preferred style, then save preferences.

## Reference Files

| File | Content |
|------|---------|
| [references/workflow.md](references/workflow.md) | Detailed step-by-step procedures |
| [references/usage.md](references/usage.md) | Natural language usage patterns |
| [references/styles.md](references/styles.md) | Full style gallery + compatibility matrix |
| [references/prompt-construction.md](references/prompt-construction.md) | Prompt templates per type |
| [references/config/backends.md](references/config/backends.md) | Multi-backend switch configuration |
| [references/styles/](references/styles/) | Detailed style specifications (one per style) |
