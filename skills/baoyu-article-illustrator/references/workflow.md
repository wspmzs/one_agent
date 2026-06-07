# Detailed Workflow Procedures

## Step 1: Pre-check

### 1.0 Detect & Save Reference Images ⚠️ REQUIRED if images provided

Check if user provided reference images. Handle based on input type:

| Input Type | Action |
|------------|--------|
| Image file path provided | Copy to `references/` subdirectory → use for `generate_image_with_reference` |
| Image in conversation (no path) | **Ask user for file path** |
| User can't provide path | Extract style/palette verbally → append to prompt text |

**If user provides file path**:
1. Copy to `references/NN-ref-{slug}.png`
2. Create description: `references/NN-ref-{slug}.md`
3. Verify files exist

**If user can't provide path** (extracted verbally):
1. Analyze image visually: colors, style, composition
2. Create `references/extracted-style.md` with extracted info
3. Append extracted info to prompt text (not as reference param)

### 1.1 Determine Input Type

| Input | Output Directory | Action |
|-------|------------------|--------|
| File path | Ask user preference | → ask output dir |
| Pasted content | `illustrations/{topic-slug}/` | → analyze content |

### 1.2 Preferences Check

Check if user has previously saved preferences (in memory or project config).

If no saved preferences → ask user in natural conversation:
- Watermark preference (text to add, or none)
- Preferred default style (or auto-select)
- Output directory preference

Save answers to memory/project config for future use.

## Step 2: Analyze Content

### 2.1 Content Analysis Table

| Analysis | Description |
|----------|-------------|
| Content type | Technical / Tutorial / Methodology / Narrative |
| Illustration purpose | information / visualization / imagination |
| Core arguments | 2-5 main points to visualize |
| Visual opportunities | Positions where illustrations add value |
| Recommended type | Based on content signals |
| Recommended density | Based on length and complexity |

### 2.2 Extract Core Arguments

- Main thesis
- Key concepts reader needs
- Comparisons/contrasts
- Framework/model proposed

**CRITICAL**: If article uses metaphors (e.g., "电锯切西瓜"), do NOT illustrate literally. Visualize the **underlying concept**.

### 2.3 Identify Positions

**Illustrate**:
- Core arguments (REQUIRED)
- Abstract concepts
- Data comparisons
- Processes, workflows

**Do NOT Illustrate**:
- Metaphors literally
- Decorative scenes
- Generic illustrations

### 2.4 Analyze Reference Images (if provided in Step 1.0)

For each reference image:

| Analysis | Description |
|----------|-------------|
| Visual characteristics | Style, colors, composition |
| Content/subject | What the reference depicts |
| Suitable positions | Which sections match this reference |
| Style match | Which illustration types/styles align |
| Usage recommendation | `direct` / `style` / `palette` |

| Usage | When to Use |
|-------|-------------|
| `direct` | Reference matches desired output closely → use `generate_image_with_reference` |
| `style` | Extract visual style characteristics only |
| `palette` | Extract color scheme only |

## Step 3: Confirm Settings

**Do NOT skip.** Ask user 3-4 questions in natural conversation. Q1, Q2, Q3 are ALL REQUIRED.

### Q1: Illustration Type ⚠️ REQUIRED
- [Recommended based on analysis] (Recommended)
- infographic / scene / flowchart / comparison / framework / timeline / mixed

### Q2: Density ⚠️ REQUIRED
- minimal (1-2) - Core concepts only
- balanced (3-5) - Major sections
- per-section - At least 1 per section/chapter (Recommended)
- rich (6+) - Comprehensive coverage

### Q3: Style ⚠️ REQUIRED

Present Core Styles with compatibility recommendation:

| Core Style | Best For |
|------------|----------|
| `vector-illustration` | Knowledge articles, tutorials, tech content |
| `minimal-flat` (notion) | General, knowledge sharing, SaaS |
| `sci-fi` (blueprint) | AI, frontier tech, system design |
| `hand-drawn` (sketch/warm) | Relaxed, reflective, casual |
| `editorial` | Processes, data, journalism |
| `scene` (warm/watercolor) | Narratives, emotional, lifestyle |

If user has preferred style saved → show it as [Recommended].

### Q4: Image Text Language ⚠️ REQUIRED when article language differs

Detect article language. If different from user's language preference, ask:
- Article language (match article content) (Recommended)
- User's preferred language

## Step 4: Generate Outline

Save as `outline.md`:

```yaml
---
type: infographic
density: balanced
style: blueprint
image_count: 4
references:                    # Only if references provided
  - ref_id: 01
    filename: 01-ref-diagram.png
    description: "Technical diagram showing system architecture"
---

## Illustration 1

**Position**: [section] / [paragraph]
**Purpose**: [why this helps]
**Visual Content**: [what to show]
**Type Application**: [how type applies]
**Filename**: 01-infographic-concept-name.png

## Illustration 2
...
```

**Requirements**:
- Each position justified by content needs
- Type applied consistently
- Style reflected in descriptions
- Count matches density

## Step 5: Generate Images

### 5.1 Create Prompts ⛔ BLOCKING

**Every illustration MUST have a saved prompt file before generation begins.**

For each illustration in the outline:

1. **Create prompt file**: `prompts/NN-{type}-{slug}.md`
2. **Include YAML frontmatter**:
   ```yaml
   ---
   illustration_id: 01
   type: infographic
   style: vector-illustration
   ---
   ```
3. **Follow type-specific template** from [prompt-construction.md](prompt-construction.md)
4. **Prompt quality requirements** (all REQUIRED):
   - `Layout`: Describe overall composition (grid / radial / hierarchical / left-right / top-down)
   - `ZONES`: Describe each visual area with specific content
   - `LABELS`: Use **actual numbers, terms, metrics, quotes from the article**
   - `COLORS`: Specify hex codes with semantic meaning
   - `STYLE`: Describe line treatment, texture, mood
   - `ASPECT`: Specify ratio (e.g., `16:9`)
5. **Optionally use `aigc-prompt` skill** to refine/optimize the prompt
6. **Backup rule**: If prompt file exists, rename to `prompts/NN-{type}-{slug}-backup-YYYYMMDD-HHMMSS.md`

**Verification**: Before proceeding, confirm ALL prompt files exist:
```
Prompt Files:
- prompts/01-infographic-overview.md ✓
- prompts/02-infographic-distillation.md ✓
```

### 5.2 Process References ⚠️ REQUIRED if references saved

For each illustration with references:

| Usage | Action |
|-------|--------|
| `direct` | Use `generate_image_with_reference` tool with saved reference image path |
| `style` | Analyze reference, append style traits to prompt text |
| `palette` | Extract colors from reference, append to prompt text |

### 5.3 Apply Watermark (if enabled in preferences)

Append to prompt:
```
Include a subtle watermark "[content]" at [position] with approximately [opacity*100]% visibility.
```

### 5.4 Select Backend

Determine which image generation backend to use. See [config/backends.md](config/backends.md) for full configuration.

**Default: jimeng MCP** (built into qwenpaw, no extra config).

**Switch to external backend**: Check user's backend preference in saved memory/config. If configured as `nano-banana-pro` / `gpt-image-2` / custom, use HTTP API calls instead of jimeng MCP.

### 5.5 Generate via jimeng MCP (default)

#### ⛔ Pre-flight checklist

| Step | Action | Why |
|------|--------|-----|
| 1 | `list_models()` | 确认账户已激活的模型列表 |
| 2 | Select model from result | 避免调用未激活模型导致 ModelNotOpen |
| 3 | Verify `stream` is NOT set to `true` | 流式输出格式与解析器不兼容 |
| 4 | Confirm prompt ≤ 600 words | 超长 prompt 可能被截断 |

**Model selection order**:
```
doubao-seedream-5-0-260128          ← 首选（旗舰，支持文生图+图生图+组图）
doubao-seedream-5-0-lite-260128     ← 5.0 不可用时降级
doubao-seedream-4-5-251128          ← 再降级
doubao-seedream-4-0-250828          ← 最后降级（需确认已激活）
doubao-seedream-3-0-t2i-250415      ← 仅文生图，不支持参考图
```

#### Correct invocation

```python
# No reference image
generate_image(
    prompt="[prompt content from saved file]",
    size="16:9",
    model="doubao-seedream-5-0-260128"
    # DO NOT set stream=true
)

# With reference image (direct usage)
generate_image_with_reference(
    prompt="[prompt content]",
    image_urls=["[reference image URL]"],
    size="16:9",
    model="doubao-seedream-5-0-260128"
)
```

#### Known pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Expecting value: line 1 column 1` | `stream=true` 开启了流式输出 | 移除 `stream` 参数或用 `stream=false` |
| `ModelNotOpen` | 调用了未激活的模型 | 先 `list_models()` 确认可用列表 |
| 浏览器弹出下载对话框 | 用 `browser_use` open 了图片 URL | 改用 Python `urllib.request.urlretrieve` |
| URL 24h 后失效 | jimeng 链接有时效 | 生成后立即下载到本地 |

#### Download images

jimeng 返回 jpeg URL（24h 有效）。下载方式：

```python
import urllib.request
urllib.request.urlretrieve(jimeng_url, r"illustrations/{slug}/NN-{type}-{slug}.png")
```

**❌ 不要用 `browser_use` open 图片 URL**——浏览器会弹出下载对话框导致 `Page.goto` 失败。

### 5.6 Generate (loop)

1. For each illustration:
   - Read prompt file content
   - Call `generate_image` / `generate_image_with_reference`
   - Download result to local path via Python
2. After each: report "Generated X/N"
3. On failure: retry once with next model in fallback chain, then log and skip

## Step 6: Finalize

### 6.1 Update Article

Insert after corresponding paragraph:
```markdown
![description](illustrations/{slug}/NN-{type}-{slug}.png)
```

Alt text: concise description in article's language.

### 6.2 Output Summary

```
Article Illustration Complete!

Article: [path]
Type: [type] | Density: [level] | Style: [style]
Location: [directory]
Images: X/N generated

Positions:
- 01-xxx.png → After "[Section]"
- 02-yyy.png → After "[Section]"

[If failures]
Failed:
- NN-zzz.png: [reason]
```
