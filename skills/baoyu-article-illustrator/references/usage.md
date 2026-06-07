# Usage (QwenPaw Natural Language)

## Trigger Phrases

Say any of these to activate this skill:
- "为这篇文章配图" / "给文章配图"
- "add illustrations to this article"
- "generate images for this article"
- "add visuals to this content"
- "文章插图" / "配图"
- "illustrate my article"

## How to Use

### Input Methods

| Method | How | Example |
|--------|-----|---------|
| **Paste content** | Paste article text directly | Paste → ask type/style → generate |
| **Provide file path** | Point to an existing file | `C:\path\to\article.md` |
| **Describe article** | Talk about the article | "I have a tech article about Kubernetes" |

### What the Agent Will Do

1. **Read/analyze** your content
2. **Ask** 3-4 questions (type, density, style, language)
3. **Generate** an outline for you to approve
4. **Create** illustrations using AI
5. **Insert** them into the article

### What You'll Be Asked

| Question | Example Response |
|----------|------------------|
| What type of illustrations? | infographic / scene / flowchart |
| How many? | 3-5 (balanced) / 1 per section |
| What style? | vector-illustration / warm / blueprint |
| Language of text in images? | Chinese (match article) |

### Providing Reference Images

Let the agent know if you have reference images:
- "I have a reference image I want to match" (provide file path)
- "I want the same style as this image" (describe what you like about it)

### Examples

**Tech article with data**:
> User: "为这篇技术文章配图"
> Agent: analyzes → asks type/density/style → generates infographics

**Personal narrative**:
> User: "add illustrations to my travel story"
> Agent: analyzes → recommends scene + warm style → generates atmospheric scenes

**Tutorial with steps**:
> User: "illustrate this how-to guide"
> Agent: recommends flowchart → generates step-by-step visuals

## Tool Chain

```
User input → baoyu-article-illustrator → aigc-prompt skill (prompt optimization)
                                        → jimeng MCP (image generation)
                                        → local save → insert into article
```
