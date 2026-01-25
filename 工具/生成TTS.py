#!/usr/bin/env python3
"""
TTS生成脚本
从剧本生成语音文件，并保存剧本.json

用法：python3 生成TTS.py <剧集目录> <剧本文件>

剧本文件格式（纯文本）：
【橘猫】台词1
【白猫】台词2
...
"""

import subprocess
import os
import sys
import json
import re

# TTS配置
VOICE_MAP = {
    "橘猫": "zh-CN-YunjianNeural",  # 男声（体育风格，热情有力）
    "白猫": "zh-CN-XiaoyiNeural",   # 女声（活泼）
    "老公": "zh-CN-YunyangNeural",  # 男声（稳重，适合中老年）
    "老婆": "zh-CN-XiaoxiaoNeural", # 女声（温暖，适合中老年）
}

# 默认角色视频映射
DEFAULT_VIDEO_MAP = {
    "橘猫": "橘猫说话.mp4",
    "白猫": "白猫说话.mp4",
}

def parse_script(script_path):
    """解析剧本文件"""
    dialogue = []
    pattern = r'【(.+?)】(.+)'

    with open(script_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = re.match(pattern, line)
            if match:
                character = match.group(1)
                text = match.group(2)
                dialogue.append({
                    "character": character,
                    "text": text
                })

    return dialogue

def generate_tts(dialogue, output_dir):
    """生成TTS音频"""
    os.makedirs(output_dir, exist_ok=True)

    for i, item in enumerate(dialogue, 1):
        character = item["character"]
        text = item["text"]
        voice = VOICE_MAP.get(character, "zh-CN-YunxiNeural")

        filename = f"{i:02d}_{character}.mp3"
        filepath = os.path.join(output_dir, filename)

        cmd = [
            "edge-tts",
            "--voice", voice,
            "--text", text,
            "--write-media", filepath
        ]

        print(f"生成 {filename}: {text[:20]}...")
        subprocess.run(cmd, capture_output=True)

        item["audio"] = filename

    return dialogue

def save_script_json(dialogue, episode_dir, title):
    """保存剧本.json"""
    # 提取角色列表
    characters = {}
    for item in dialogue:
        char = item["character"]
        if char not in characters:
            video = DEFAULT_VIDEO_MAP.get(char, f"{char}说话.mp4")
            characters[char] = {"name": char, "video": video}

    # 构建JSON结构
    script_data = {
        "title": title,
        "characters": {
            "A": list(characters.values())[0] if len(characters) > 0 else {},
            "B": list(characters.values())[1] if len(characters) > 1 else {},
        },
        "dialogue": [
            {
                "audio": item["audio"],
                "character": item["character"],
                "text": item["text"]
            }
            for item in dialogue
        ]
    }

    json_path = os.path.join(episode_dir, "剧本.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 已保存: {json_path}")
    return json_path

def main():
    if len(sys.argv) < 3:
        print("用法: python3 生成TTS.py <剧集目录> <剧本文件>")
        print("示例: python3 生成TTS.py 剧集/第五集_新剧/ 剧本.txt")
        sys.exit(1)

    episode_dir = sys.argv[1]
    script_path = sys.argv[2]

    # 从目录名提取标题
    title = os.path.basename(episode_dir.rstrip('/'))
    if '_' in title:
        title = title.split('_', 1)[1]

    print("=" * 50)
    print(f"TTS生成: {title}")
    print("=" * 50)

    # 解析剧本
    dialogue = parse_script(script_path)
    print(f"解析到 {len(dialogue)} 句台词\n")

    # 生成TTS
    audio_dir = os.path.join(episode_dir, "音频")
    dialogue = generate_tts(dialogue, audio_dir)

    # 保存剧本.json
    save_script_json(dialogue, episode_dir, title)

    print(f"\n完成！共生成 {len(dialogue)} 条语音")

if __name__ == "__main__":
    main()
