# System Prompt for Image Generation

## Default Composition Requirements

**Apply to ALL prompts by default**:

| Requirement | Description |
|-------------|-------------|
| **Clean composition** | Simple layouts, no visual clutter |
| **White space** | Generous margins, breathing room around elements |
| **No complex backgrounds** | Solid colors or subtle gradients only, avoid busy textures |
| **Centered or content-appropriate** | Main visual elements centered or positioned by content needs |
| **Matching graphics** | Use graphic elements that align with content theme |
| **Highlight core info** | White space draws attention to key information |

Add to ALL prompts:
> Clean composition with generous white space. Simple or no background. Main elements centered or positioned by content needs.

## Character Rendering

When depicting people:

| Guideline | Description |
|-----------|-------------|
| **Style** | Simplified cartoon silhouettes or symbolic expressions |
| **Avoid** | Realistic human portrayals, detailed faces |
| **Diversity** | Varied body types when showing multiple people |
| **Emotion** | Express through posture and simple gestures |

Add to ALL prompts with human figures:
> Human figures: simplified stylized silhouettes or symbolic representations, not photorealistic.

## Text in Illustrations

| Element | Guideline |
|---------|-----------|
| **Size** | Large, prominent, immediately readable |
| **Style** | Handwritten fonts preferred for warmth |
| **Content** | Concise keywords and core concepts only |
| **Language** | Match article language |

Add to prompts with text:
> Text should be large and prominent with handwritten-style fonts. Keep minimal, focus on keywords.

## Prompt Structure

Every prompt must include:

1. **Layout Structure First**: Describe composition, zones, flow direction
2. **Specific Data/Labels**: Use actual numbers, terms from article
3. **Visual Relationships**: How elements connect
4. **Semantic Colors**: Meaning-based color choices (red=warning, green=efficient)
5. **Style Characteristics**: Line treatment, texture, mood
6. **Aspect Ratio**: End with ratio (16:9 for most illustrations)

## Generation via QwenPaw Tools

1. Create prompt files in `prompts/NN-{type}-{slug}.md`
2. Use **`aigc-prompt` skill** to refine/optimize the prompt if needed
3. Use **`jimeng` MCP** (`generate_image`) to generate the actual image
4. Download result and save to output directory

## What to Avoid

- Vague descriptions ("a nice image")
- Literal metaphor illustrations
- Missing concrete labels/annotations
- Generic decorative elements
