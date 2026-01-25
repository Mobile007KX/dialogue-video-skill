# 对话短剧 Skill

> 二人对话推动剧情的AI短剧制作工具

---

## 触发条件

当用户提到以下关键词时触发此Skill：
- "对话短剧"、"做短剧"、"制作短剧"
- "橘猫白猫"、"猫咪对话"
- "图生视频"+"对话"
- "TTS合成视频"

---

## 依赖

| 依赖 | 用途 | 必需 |
|------|------|------|
| MiniMax API | 图片生成、视频生成 | ✅ |
| edge-tts | 免费TTS语音合成 | ✅ |
| ffmpeg | 视频合成 | ✅ |
| Python 3 | 运行合成脚本 | ✅ |

### API配置

```bash
# MiniMax API Key（在 ~/.config/alma/skills/my-minimax-video-gen/key.env）
MINIMAX_API_KEY=sk-xxx
```

---

## 核心流程

```
用户输入 → 定装照确认 → 角色设定 → 视频素材生成 → 剧本创作 → TTS → 合成出片
```

### Phase 1: 定装照确认

**必须询问用户**：

```
你有定装照吗？（两个角色同框的静态图）
  [A] 有，我上传
  [B] 没有，帮我用AI生成
```

- 选A：用户上传图片，保存为 `起始帧.png`
- 选B：调用 MiniMax 图片生成（my-minimax-image-gen skill）

### Phase 2: 角色设定

**询问用户或使用默认**：

```
请为角色设定名字、性格、口头禅
或输入 [D] 使用默认设定
```

默认设定：
- 橘猫：尼古拉斯·点橘，暴发户，东北腔，"哥有的是钱"
- 白猫：雪莉，泼辣直爽，"你可真是个人才"

### Phase 3: 视频素材生成

**固定参数（不可更改）**：

```json
{
  "model": "MiniMax-Hailuo-02",
  "resolution": "512P",
  "duration": 6,
  "费用": "0.60元/条"
}
```

**生成两条视频**：

1. `橘猫说话.mp4`
```
prompt: Same scene, same lighting, same camera angle, static camera, no camera movement.
Orange cat is TALKING - mouth movements, expressive gestures.
White cat is LISTENING SILENTLY - mouth firmly CLOSED.
Loop-friendly: end pose similar to start pose.
```

2. `白猫说话.mp4`
```
prompt: Same scene, same lighting, same camera angle, static camera, no camera movement.
White cat is TALKING - mouth movements, gestures.
Orange cat is LISTENING SILENTLY - mouth firmly CLOSED.
Loop-friendly: end pose similar to start pose.
```

**关键约束**：
- 机位灯光必须锁定（static camera, same lighting）
- 说话角色嘴动，听的角色嘴必须闭着（mouth firmly CLOSED）
- 首尾相连可循环（end pose similar to start pose）

### Phase 4: 剧本创作

**询问用户主题或提供模板**：

```
请输入剧本主题，或选择模板：
  [1] 炫富被怼
  [2] 土味情话
  [3] 回忆往事
  [4] 自定义主题：__________
```

**剧本格式**：
```
【橘猫】台词1
【白猫】台词2
【橘猫】台词3
...
```

**必须用户确认后才继续**。

### Phase 5: TTS生成

**使用 edge-tts（免费）**：

```bash
# 橘猫用男声
edge-tts --voice zh-CN-YunxiNeural --text "台词" --write-media XX_橘猫.mp3

# 白猫用女声
edge-tts --voice zh-CN-XiaoyiNeural --text "台词" --write-media XX_白猫.mp3
```

**生成后必须保存 `剧本.json`**：

```json
{
  "title": "剧集标题",
  "characters": {
    "A": {"name": "橘猫", "video": "橘猫说话.mp4"},
    "B": {"name": "白猫", "video": "白猫说话.mp4"}
  },
  "dialogue": [
    {"audio": "01_橘猫.mp3", "character": "橘猫", "text": "台词内容"},
    {"audio": "02_白猫.mp3", "character": "白猫", "text": "台词内容"}
  ]
}
```

### Phase 6: 视频合成

**调用合成脚本**：

```bash
python3 工具/合成脚本.py 剧集/第X集_标题/
```

脚本自动：
- 从 `剧本.json` 读取台词（唯一数据源）
- 根据角色匹配视频素材
- 循环视频适配音频长度
- 添加字幕（自适应字体大小）
- 拼接输出

---

## 目录结构

```
对话短剧工具/
├── SKILL.md                    # 本文件（AI读取入口）
├── 工具/
│   └── 合成脚本.py             # 视频合成脚本
├── 制作指南/
│   ├── Skill设计草案.md        # 详细交互设计
│   └── 分镜与运镜指南.md       # 技术要点
└── 项目/
    └── [项目名]/
        ├── README.md
        ├── 角色设定.md
        ├── 角色资产/
        │   ├── 形象/           # 定装照、视频素材
        │   └── 声音/           # 克隆音色相关
        └── 剧集/
            └── 第X集_标题/
                ├── 起始帧.png
                ├── 橘猫说话.mp4
                ├── 白猫说话.mp4
                ├── 剧本.json    # 唯一数据源
                ├── 音频/
                │   └── XX_角色.mp3
                └── 成品/
                    └── 标题_demo.mp4
```

---

## 费用估算

| 步骤 | 费用 |
|------|------|
| 定装照（AI生成） | 0.2元（可选） |
| 视频素材（2条） | 1.2元 |
| TTS | 免费 |
| **总计** | **1.2~1.4元/集** |

---

## 执行示例

```
用户：帮我做一个橘猫和白猫的搞笑短剧

AI：
═══════════════════════════════════════
  AI对话短剧制作
═══════════════════════════════════════

你有定装照吗？（两个角色同框的静态图）
  [A] 有，我上传
  [B] 没有，帮我用AI生成

用户：A [上传图片]

AI：检测到2个角色，确认使用？[Y/n]

用户：Y

AI：
────────────────────────────────────
  生成视频素材
────────────────────────────────────
预计费用：1.2元（512P × 2条）
确认生成？[Y/n]

用户：Y

AI：[生成中...] ✅ 完成

────────────────────────────────────
  剧本创作
────────────────────────────────────
请输入主题或选择模板：[1]炫富被怼 [2]土味情话 ...

用户：2

AI：[生成剧本] 确认？[Y/E/R]

用户：Y

AI：[生成TTS] ✅ 已保存剧本.json
    [合成视频] ✅ 完成

成品：剧集/第X集_土味情话/成品/土味情话_demo.mp4
时长：约50秒
```

---

## 注意事项

1. **每步必须用户确认**：不可自动跳过
2. **剧本.json是唯一数据源**：TTS和合成必须用同一份
3. **视频生成固定512P**：不可擅自改高分辨率
4. **机位灯光锁定**：prompt必须包含 `static camera, same lighting`
5. **一说一听**：prompt必须明确一个说话、另一个嘴闭着

---

*版本：v1.0*
*更新：2026-01-25*
