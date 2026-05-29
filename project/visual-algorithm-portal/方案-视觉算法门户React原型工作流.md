# 视觉算法门户平台 —— React 原型工作流方案

> 版本：v1.0 | 日期：2026-05-27
> 发起人：张硕（PM）| 执行：七仔 → 小帅 → 切图仔 | 交付：前端团队

---

## 目录

1. [环境准备](#一环境准备)
2. [工作流详解](#二工作流详解)
3. [规范体系](#三规范体系)
4. [切图仔能力评估与装备清单](#四切图仔能力评估与装备清单)
5. [Anthropic 开源 Skill 评估](#五anthropic-开源-skill-评估)
6. [风险与应对](#六风险与应对)

---

## 一、环境准备

### 1.1 你（PM）需要做的

| 项目 | 状态 | 说明 |
|------|------|------|
| Node.js LTS | ✅ **已完成** | v20.19.1，位于 `C:\tools\node-v20.19.1-win-x64` |
| npm | ✅ **已完成** | v10.8.2 |
| 浏览器 | ✅ **已有** | 任意现代浏览器，预览原型用 |

**不需要你做任何额外安装。**

### 1.2 七仔（我）需要搭建的

项目脚手架一次性搭建命令：

```bash
# 创建项目目录
cd project/visual-algorithm-portal

# Vite + React + TypeScript 脚手架
npm create vite@latest . -- --template react-ts

# 安装核心依赖
npm install antd@^6 react-router-dom@^6 echarts echarts-for-react

# 安装开发依赖（可选）
npm install -D @types/react-router-dom
```

**安装后项目结构：**

```text
project/visual-algorithm-portal/
├── public/
├── src/
│   ├── assets/           # 静态资源（图标、图片）
│   ├── components/       # 公共组件
│   ├── layouts/          # 页面布局
│   ├── pages/            # ★ 核心产出：一个页面一个文件夹
│   ├── hooks/            # 自定义 Hooks
│   ├── utils/            # 工具函数
│   ├── mock/             # Mock 数据
│   ├── styles/           # 全局样式
│   ├── App.tsx           # 路由入口
│   ├── main.tsx          # 启动文件
│   └── vite-env.d.ts     # 类型声明
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### 1.3 启动命令

```bash
npm run dev
# → 浏览器打开 http://localhost:5173
```

**终端保持运行，不要关闭。以后你只用刷新浏览器。**

---

## 二、工作流详解

### 2.1 宏观流程

```
┌────────────────────────────────────────────────────────────────────┐
│                       第 一 次 循 环                                │
│                                                                    │
│  你（PM）       七仔（default）     小帅（impmzs）    切图仔（creation-code）│
│     │               │                  │                 │         │
│     │──碎片需求─────→│                  │                 │         │
│     │               │──结构化需求文档───│                  │         │
│     │               │  写入 01-需求卡片.md                     │         │
│     │               │←──架构方案───────│                   │         │
│     │               │  写入 02-架构方案.md                     │         │
│     │               │────需求+架构───────→ 切图仔             │         │
│     │               │                     │                 │         │
│     │               │←───── pages/*.tsx ───│                 │         │
│     │←── 验收反馈 ──│                     │                 │         │
│     │──修改意见────→│                     │                 │         │
│     │               │────修改指令─────────→│                 │         │
│     │               │←───── 修改后文件 ────│                 │         │
│     │    ... 循环直到锁定 ...              │                 │         │
└────────────────────────────────────────────────────────────────────┘
```

### 2.2 每个环节的输入、输出、操作

---

#### 环节 A：需求输入（你 → 七仔）

| 项目 | 内容 |
|------|------|
| **你做什么** | 用自然语言描述页面需求 |
| **输入格式** | 卡片式，每个页面 3-10 句话 |
| **示例** | "用户管理页面：顶部统计卡片3张，搜索栏，表格列出所有用户，点击某行跳详情" |
| **工具** | 无（微信对话框直接说） |

---

#### 环节 B：需求结构化（七仔）

| 项目 | 内容 |
|------|------|
| **七仔做什么** | 把你的碎片需求整理成标准的需求卡片文档 |
| **输出文件** | `project/{项目名}/01-需求卡片.md` |
| **使用工具** | `write_file` / `edit_file` |
| **使用技能** | 无（这是默认能力） |
| **交付物结构** | 见下方模板 |

**需求卡片文档模板：**

```markdown
# 需求卡片文档

## 页面清单

### P01：用户管理列表页
- **访问路径**：/users
- **页面骨架**：
  - [顶部] 面包屑 + 页面标题「用户管理」
  - [统计区] 3 张卡片：用户总数(1,280) / 本月新增(86) / 7日活跃(942)
  - [搜索栏] 搜索框(用户名/邮箱) + 角色下拉 + 状态下拉
  - [操作区] 「新建用户」按钮
  - [主区域] Table（用户名/邮箱/角色/状态/注册时间/操作）
  - [底部] 分页（每页10条，共1,280条）
- **弹窗**：新建用户弹窗（用户名/邮箱/角色/备注，必填校验）
- **交互行为**：
  - 点击表格行 → 跳转 /users/:id
  - 搜索回车 → 刷新列表
  - 状态标签用颜色区分（正常=绿，禁用=红）

### P02：用户详情页
...

### P03：算法列表页
...
```

---

#### 环节 C：架构设计（七仔 → 小帅）

| 项目 | 内容 |
|------|------|
| **七仔做什么** | 将需求卡片文档派发给小帅做架构设计 |
| **小帅做什么** | 输出路由树、组件复用策略、数据流方案 |
| **输出文件** | `project/{项目名}/02-架构方案.md` |
| **通信模式** | **背景模式** `--background`（架构设计需要思考时间） |
| **使用工具** | `submit_to_agent`（派发）→ `check_agent_task`（查结果） |
| **使用技能** | `multi_agent_collaboration`、`caveman` |

**七仔→小帅派发消息模板：**

```
[Agent default requesting]

Background: PM要构建视觉算法门户平台的React原型，需求卡片已写入文件
Goal: 输出页面架构方案（路由树+组件复用策略+数据流方案）

Input: project/visual-algorithm-portal/01-需求卡片.md
Deliverable: 写入 project/visual-algorithm-portal/02-架构方案.md

Constraints:
  - 技术栈: Vite + React + Ant Design v6.x + TypeScript
  - 路由: react-router-dom v6
  - 图表: ECharts + echarts-for-react
  - 不要过度设计，保持原型阶段适度简化
  - 列出每个页面可复用的公共组件
  - 给出 Mock 数据方案（简单 JSON，不需要后端）

请读完需求卡片后输出架构方案。
```

**小帅输出的架构方案内容：**

```markdown
# 架构方案

## 路由树
/ → Layout → Dashboard（首页仪表盘）
/users → Layout → UserList（用户列表）
/users/:id → Layout → UserDetail（用户详情）
/users/create → Layout → UserCreate（新建用户）
/algorithms → Layout → AlgorithmList（算法列表）
/algorithms/:id → Layout → AlgorithmDetail（算法详情）

## 公共组件清单
- PageHeader（页面标题+面包屑）
- SearchBar（搜索区域复合组件）
- StatCardGroup（统计卡片组）
- StatusTag（算法状态/用户状态标签）
- ConfirmModal（通用确认弹窗）

## 数据流方案
- 使用 React useState + useEffect 管理页面级状态
- Mock 数据放在 src/mock/ 目录下，每个页面一个 JSON 文件
- 后续替换真实接口时：直接替换 mock 为 api 调用即可
```

---

#### 环节 D：页面编码（七仔 → 切图仔）

| 项目 | 内容 |
|------|------|
| **七仔做什么** | 将需求卡片+架构方案派发给切图仔 |
| **切图仔做什么** | 输出 React 组件代码（每个页面一个独立 .tsx 文件） |
| **输出位置** | `project/{项目名}/src/pages/{PageName}/index.tsx` |
| **通信模式** | **背景模式** `--background`（多页面编码耗时较长） |
| **使用工具** | `submit_to_agent` → `check_agent_task` |
| **使用技能** | `multi_agent_collaboration`、`caveman` |
| **切图仔使用的MCP** | `antdesign_mcp`（查询组件属性/代码示例/文档） |
| **切图仔使用的Tool** | `write_file` / `read_file` / `edit_file` / `execute_shell_command` |

**七仔→切图仔派发消息模板：**

```
[Agent default requesting]

Background: 视觉算法门户平台原型项目，技术栈Vite+React+Ant Design v6.x+TypeScript
Goal: 按需求文档和架构方案输出React组件代码

Input:
  - 需求: project/visual-algorithm-portal/01-需求卡片.md
  - 架构: project/visual-algorithm-portal/02-架构方案.md

Deliverable: project/visual-algorithm-portal/src/pages/{PageName}/index.tsx

Constraints:
  - 使用 antdesign_mcp 查询Ant Design组件属性和代码示例
  - 每个页面一个独立文件夹 src/pages/{PageName}/index.tsx
  - 组件用 function ComponentName: React.FC 写法
  - Mock数据放在 src/mock/{pageName}.ts
  - 样式用 style={...} 内联写法（原型阶段够用）
  - 路由配置写入 src/router/index.tsx
  - 文件需包含完整的数据类型定义（interface）
  - 每段核心逻辑上方加一行注释说明用途
  - 不需要考虑权限、鉴权、异常边界

首批需要编码的页面（按优先级排序）：
1. Dashboard - 首页仪表盘
2. AlgorithmList - 算法列表
3. AlgorithmDetail - 算法详情
4. UserList - 用户列表（后续再做）
```

---

#### 环节 E：验收与迭代（你 → 七仔）

| 项目 | 内容 |
|------|------|
| **你做什么** | 打开浏览器 `http://localhost:5173` 预览页面 |
| **你做什么** | 说哪里需要改（如"表格加一列部门"、"颜色太深了"） |
| **七仔做什么** | 定位到对应文件 → 用 `edit_file` 局部修改 |
| **使用工具** | `edit_file`（局部替换，不重写整个文件） |
| **你做什么** | 刷新浏览器看修改效果 |

**修改的三种粒度：**

| 改什么 | 七仔操作 | Token消耗 |
|--------|---------|-----------|
| 改文案（按钮文字、表格列名） | `edit_file` 精准替换 | ~1K |
| 加一个字段/列 | `edit_file` 插入新行 | ~2K |
| 换一个组件（Table→Card） | `write_file` 重写整个文件 | ~8K |

---

#### 环节 F：交付前端

| 项目 | 内容 |
|------|------|
| **你做什么** | 把 `project/visual-algorithm-portal/` 整个目录发给前端 |
| **前端做什么** | `npm install` → `npm run dev` → 打开看 |
| **前端做什么** | 打开每个 `src/pages/*/index.tsx`，看组件实现 |
| **前端做什么** | 复制核心逻辑到业务项目，按团队规范重写结构 |
| **交付物** | 整个项目目录 + `references/` 参考文档 |

---

## 三、规范体系

### 3.1 目录结构规范

```text
src/
├── pages/{PageName}/          # 一个页面一个文件夹
│   ├── index.tsx              # 页面主组件
│   └── components/            # 仅该页面使用的子组件（可选）
│
├── components/                 # 跨页面公共组件
│   ├── PageHeader/
│   ├── SearchBar/
│   └── StatusTag/
│
├── layouts/                    # 页面布局
│   ├── MainLayout/            # 侧边栏+顶栏+内容区
│   └── AuthLayout/            # 登录页布局
│
├── hooks/                      # 自定义 Hooks
│   ├── usePageTitle.ts
│   └── useMockData.ts
│
├── mock/                       # Mock 数据（每页一个文件）
│   ├── dashboard.ts
│   └── algorithmList.ts
│
├── router/                     # 路由配置
│   └── index.tsx
│
├── styles/                     # 全局样式
│   └── global.css
│
└── utils/                      # 工具函数
    └── index.ts
```

### 3.2 文件命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 页面文件夹 | `PascalCase` | `AlgorithmList/`、`UserDetail/` |
| 页面组件 | `index.tsx` | `pages/AlgorithmList/index.tsx` |
| 公共组件 | `PascalCase.tsx` | `components/PageHeader/index.tsx` |
| 路由配置 | `index.tsx` | `router/index.tsx` |
| Mock 数据 | `camelCase.ts` | `mock/algorithmList.ts` |
| Hook | `useCamelCase.ts` | `hooks/useMockData.ts` |
| 工具函数 | `index.ts` | `utils/index.ts` |
| 样式文件 | `camelCase.css` | `styles/global.css` |

### 3.3 代码编写规范

#### 组件规范

```tsx
// ✅ 正确写法
// 首页仪表盘组件
const Dashboard: React.FC = () => {
  return (
    <div style={{ padding: 24 }}>
      {/* 页面内容 */}
    </div>
  )
}
export default Dashboard

// ❌ 不要这样写
export default function Dashboard(props: any) { ... }  // 禁止 any
const Dashboard = () => { ... }  // 缺少类型声明
```

#### 注释规范

```tsx
// ── 1. 页面级：文件顶部一行注释，说明页面用途
// 算法列表页：展示所有可用算法，支持搜索和状态筛选

// ── 2. 区块级：每个数据请求/复杂逻辑前加注释
// 获取算法列表（从 mock 数据读取）
const { data, loading } = useMockData('algorithmList')

// ── 3. 行内：仅当逻辑不直观时加
```

#### 组件引用规范

```tsx
// ✅ 正确引用
import { Table, Button, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useNavigate } from 'react-router-dom'
import PageHeader from '@/components/PageHeader'
import StatCardGroup from '@/components/StatCardGroup'

// ✅ 配置 vite.config.ts 支持 @ 别名
// resolve: { alias: { '@': path.resolve(__dirname, 'src') } }

// ❌ 不要使用全量引入
// import { Table } from 'antd/es/table'  // 没必要，antd 自动 tree-shaking
```

#### Mock 数据规范

```ts
// src/mock/algorithmList.ts

// 算法列表 Mock 数据
export interface AlgorithmItem {
  id: string
  name: string
  version: string
  status: 'running' | 'stopped' | 'failed'
  accuracy: number
  updatedAt: string
  description: string
}

// 生成 20 条假数据
export const mockAlgorithmList: AlgorithmItem[] = Array.from({ length: 20 }, (_, i) => ({
  id: `alg-${i + 1}`,
  name: `算法 ${i + 1}`,
  version: `v${Math.floor(Math.random() * 5) + 1}.${Math.floor(Math.random() * 10)}`,
  status: ['running', 'stopped', 'failed'][Math.floor(Math.random() * 3)] as AlgorithmItem['status'],
  accuracy: Number((Math.random() * 0.3 + 0.7).toFixed(4)),
  updatedAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
  description: `这是算法 ${i + 1} 的描述`,
}))
```

### 3.4 索引文件规范（解决「上下文过长导致遗忘」问题）

这是最关键的一条规范。由于 LLM 在长对话中会丢失上下文，当你发起新会话修改代码时，需要一份索引文件让 LLM 快速定位。

**每个项目根目录维护一个 `INDEX.md`：**

```markdown
# 视觉算法门户 —— 项目索引

> 最后更新：2026-05-27
> 技术栈：Vite + React + Ant Design v6.x + ECharts + TypeScript

## 路由映射

| 路径 | 页面文件 | 状态 |
|------|---------|------|
| / | pages/Dashboard/index.tsx | ✅ 已完成 |
| /algorithms | pages/AlgorithmList/index.tsx | ✅ 已完成 |
| /algorithms/:id | pages/AlgorithmDetail/index.tsx | 🔧 修改中 |
| /users | pages/UserList/index.tsx | ⏳ 待编码 |
| /users/:id | pages/UserDetail/index.tsx | ⏳ 待编码 |

## 公共组件清单

| 组件 | 位置 | 说明 |
|------|------|------|
| PageHeader | components/PageHeader/ | 页面标题+面包屑 |
| SearchBar | components/SearchBar/ | 搜索区域 |
| StatusTag | components/StatusTag/ | 状态标签 |

## 最新修改记录

| 日期 | 修改内容 | 影响文件 |
|------|---------|---------|
| 2026-05-27 | 新增 Dashboard 页面 | pages/Dashboard/index.tsx |
| 2026-05-27 | 修改算法列表表格列定义 | pages/AlgorithmList/index.tsx |

## 数据流说明

- 所有页面数据来自 src/mock/ 目录
- 暂无接口调用（纯前端原型）
- 路由在 src/router/index.tsx 中配置
```

**规范要求：**
1. 每次页面创建/修改后，同步更新 `INDEX.md`
2. 新会话启动时，七仔先读 `INDEX.md`，快速定位文件
3. `INDEX.md` 中记录了当前所有页面状态，防止重复创建

### 3.5 路由规范

```tsx
// src/router/index.tsx
import { createBrowserRouter } from 'react-router-dom'
import MainLayout from '@/layouts/MainLayout'
import Dashboard from '@/pages/Dashboard'
import AlgorithmList from '@/pages/AlgorithmList'

const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'algorithms', element: <AlgorithmList /> },
      { path: 'algorithms/:id', element: <AlgorithmDetail /> },
      { path: 'users', element: <UserList /> },
      { path: 'users/:id', element: <UserDetail /> },
    ],
  },
])

export default router
```

### 3.6 样式规范

```
1. 原型阶段：全部使用内联 style={{ ... }} 对象
2. 不引入 CSS Modules / styled-components / Tailwind
3. 仅全局布局类样式（Layout、背景色）写在 styles/global.css
4. 颜色使用 Ant Design Token 变量：
   - 品牌色: token.colorPrimary
   - 文本色: token.colorText
   - 背景色: token.colorBgLayout
5. 间距使用 Ant Design 内置 token：
   - padding: token.paddingLG (24px)
   - margin: token.marginMD (16px)
```

### 3.7 版本迭代规范

```
1. 每次迭代前更新 INDEX.md 中的「最新修改记录」
2. 每次修改前，先读 INDEX.md 确认当前页面状态
3. 如果某页面存在且只需微调 → edit_file 局部改
4. 如果某页面需要大改 → write_file 全量替换
5. 删除废弃代码，不允许注释掉保留（降低混乱度）
6. 每完成一个页面 → 在 INDEX.md 标记状态为 ✅
```

### 3.8 测试规范（原型阶段）

```
原型阶段不需要自动化测试，遵循以下手动验证规则：
1. 每个页面生成后 → 七仔在本地 npm run dev 一次确认无编译错误
2. 页面间路由跳转手动验证（点击链接是否能到目标页）
3. mock 数据是否能正常渲染
4. 弹窗是否能正常打开/关闭
```

---

## 四、切图仔能力评估与装备清单

### 4.1 已安装的 Skills

| Skill | 用途 | 在本方案中的角色 |
|-------|------|----------------|
| antdesign_mcp (MCP) | Ant Design 官方组件查询 | ⭐ **核心** |
| design-tokens | 设计 Token 生成 | ⭐ **辅助** |
| aigc-prompt | AIGC 提示词 | ❌ 不需要 |
| baoyu-article-illustrator | 文章插图生成 | ❌ 不需要 |
| html-ppt | HTML 演示文稿 | ❌ 不需要 |
| browser_cdp / browser_visible | 浏览器控制 | ⭐ **辅助** |
| caveman | 消息压缩 | ⭐ **辅助** |
| chat_with_agent | Agent 通信 | ⭐ **核心** |
| docx / pdf / xlsx | 文件格式处理 | ❌ 不需要 |
| file_reader | 文件读取 | ⭐ **核心** |
| mcp-configurator | MCP 配置管理 | ⭐ **辅助** |

### 4.2 已安装的 MCP

| MCP | 配置状态 | 在本方案中的角色 |
|-----|---------|----------------|
| `antdesign_mcp` | ✅ **已配置启用** | ⭐ **核心** |
| `anime_js_mcp` | ✅ 存在于 mcp_pool | ❌ 本方案暂不需要 |

### 4.3 需要额外安装的工具

**结论：切图仔现有装备齐全，无需额外安装。**

---

## 五、Anthropic 开源 Skill 评估

逐一评估了 5 个 Skill，**不建议安装**。理由如下：

| Skill | 目标场景 | 适用？ | 原因 |
|-------|---------|--------|------|
| **frontend-design** | 高创意前端界面设计（着陆页、营销页） | ❌ | 我们要的是**标准企业后台**（Ant Design 风格），不是「胆大美学方向」的创意设计 |
| **theme-factory** | 给幻灯片/文档应用主题 | ❌ | 针对 presentation 场景，不是 web 应用 |
| **web-artifacts-builder** | 单文件 HTML 产物（React+Tailwind+shadcn） | ❌ | 单文件架构 ≠ 多页 React 项目；Tailwind+shadcn ≠ Ant Design |
| **webapp-testing** | Playwright 自动化测试 | ⚠️ 暂不 | 原型阶段不需要自动化测试，进入开发阶段再考虑 |
| **brand-guidelines** | 应用 Anthropic 品牌 | ❌ | 专为 Anthropic 品牌设计，不是通用工具 |

---

## 六、风险与应对

| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|---------|
| LLM 上下文过长导致遗忘或幻觉 | ⚠️ 高 | 🔴 编码错误 | ✅ INDEX.md 机制 |
| 切图仔生成的代码编译报错 | ⚠️ 中 | 🟡 无法预览 | ✅ 七仔在交付前编译验证 |
| 前端团队不认可代码风格 | ⚠️ 中 | 🟡 需要重写 | ✅ 事先约定「仅供参考，不直接合入」 |
| 需求变更频繁，文件版本混乱 | ⚠️ 中 | 🟡 定位困难 | ✅ INDEX.md 记录修改历史 |
| 你描述需求太模糊 | ⚠️ 中 | 🟡 返工 | ✅ 七仔主动追问澄清，不猜测 |

---

## 七、总结：这比 Figma 好在哪？

| 维度 | Figma | 本方案 |
|------|-------|--------|
| 你评审需求 | 打开 Figma 看设计稿 | 打开浏览器看真实页面 |
| 改一个字段 | 设计师改画板 → 重新导出 | 你说 → AI 秒改 → 你刷新（5分钟） |
| 前端接手 | 从零写 HTML+CSS+交互 | 打开 .tsx 看真实代码 |
| 需求变更 | 改 Figma → 通知前端 → 前端重写 | 改 .tsx 文件 → 前端同步更新 |
| 协作人数 | 你 + 设计师 + 前端（3人） | 你 + AI（2人），前端只看最终版 |
| 产出即交付 | ❌ 画板不是代码 | ✅ .tsx 就是代码 |
