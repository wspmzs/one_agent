# View Image（图像理解）

很多强大的推理模型原生不具备视觉能力，无法直接理解图片内容。View Image 插件通过接入一个多模态 VLM（Vision Language Model），赋予 Agent 图像理解能力。

你只需配置一个便宜的多模态模型（如豆包 lite、千问 VL 等），即可让 Agent"看懂"截图、照片、设计稿、图表等内容。配合 `prompt_template`，可以根据不同 Agent 的角色配置不同风格的描述提示词——比如设计师 Agent 侧重 UI 布局，数据分析师 Agent 侧重图表趋势。

## 注意

此工具名称 `describe_image` 与 QwenPaw 内置的 `view_image` 不同，避免冲突。

## 安装

在 QwenPaw 运行的终端中执行：

```bash
qwenpaw plugin install /path/to/view-image
```

QwenPaw 会自动：

1. 复制 Plugin 到 `~/.qwenpaw/plugins/` 目录
2. 自动安装 `requirements.txt` 中的依赖
3. **热加载**到当前运行中的 QwenPaw，无需重启

> 如果 QwenPaw 未运行，Plugin 会在下次启动时加载。

## 配置（必需）

`describe_image` **必须配置 VLM 才能使用**，不存在降级模式。

### 通过 QwenPaw UI 配置（推荐）

在 QwenPaw Console → Agent Settings → Tools → `describe_image` 中填写：

| 字段                  | 说明                                                 |
| ------------------- | -------------------------------------------------- |
| `vlm_api_url`       | VLM API 端点（OpenAI 兼容格式），如火山引擎、OpenAI、硅基流动          |
| `vlm_api_key`       | API 密钥                                             |
| `vlm_model_name`    | 模型名称，如 `doubao-seed-2-0-lite-260428`、`qwen-vl-max` |
| `per_image_timeout` | 单图超时秒数（默认 60）                                      |
| `prompt_template`   | 默认提示词（选填，不同 Agent 可按需定制）                           |

保存后即时生效。

## 启用

Plugin 安装后，Tool 默认处于**禁用**状态。需在以下位置启用：

- **QwenPaw Console** → Agent Settings → Tools → 勾选 `describe_image` → 保存

## 使用

```python
# 本地图片
describe_image(path="/path/to/image.jpg")

# URL 图片
describe_image(path="https://example.com/photo.png")

# 自定义提示词（覆盖默认）
describe_image(path="/path/to/image.jpg", prompt="请描述这个 UI 设计的布局和配色")
```

### 参数

| 参数       | 类型  | 必填  | 说明                    |
| -------- | --- | --- | --------------------- |
| `path`   | str | ✅   | 本地图片绝对路径或 HTTP(S) URL |
| `prompt` | str | ❌   | 自定义提示词（覆盖 config 默认值） |

### 返回值

纯文本：图片描述结果（如 VLM 分析成功）或错误信息。

## 常见问题

- **VLM 未配置**：返回明确错误，提示在 UI 中配置
- **VLM 调用超时**：增大 `per_image_timeout` 或检查 VLM 服务负载
- **不支持的图片格式**：支持 png / jpg / jpeg / gif / webp / bmp

## 依赖

- Pillow>=10.0.0
- httpx>=0.27.0

---

作者：impmzs
