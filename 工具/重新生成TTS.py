#!/usr/bin/env python3
"""
从剧本.json重新生成TTS音频
用于批量更新音色

用法：python3 重新生成TTS.py <剧集目录>
"""

import subprocess
import os
import sys
import json

# TTS配置（与生成TTS.py保持一致）
VOICE_MAP = {
    "橘猫": "zh-CN-YunjianNeural",  # 男声（体育风格，热情有力）
    "白猫": "zh-CN-XiaoyiNeural",   # 女声（活泼）
    "老公": "zh-CN-YunyangNeural",  # 男声（稳重，适合中老年）
    "老婆": "zh-CN-XiaoxiaoNeural", # 女声（温暖，适合中老年）
}

def regenerate_tts(episode_dir):
    """从剧本.json重新生成TTS"""
    script_file = os.path.join(episode_dir, "剧本.json")
    audio_dir = os.path.join(episode_dir, "音频")

    if not os.path.exists(script_file):
        print(f"错误：找不到 {script_file}")
        return False

    with open(script_file, 'r', encoding='utf-8') as f:
        script_data = json.load(f)

    title = script_data.get("title", "未命名")
    dialogue = script_data.get("dialogue", [])

    print("=" * 50)
    print(f"重新生成TTS: {title}")
    print("=" * 50)

    os.makedirs(audio_dir, exist_ok=True)

    for item in dialogue:
        character = item["character"]
        text = item["text"]
        audio_file = item["audio"]
        voice = VOICE_MAP.get(character, "zh-CN-YunxiNeural")

        filepath = os.path.join(audio_dir, audio_file)

        cmd = [
            "edge-tts",
            "--voice", voice,
            "--text", text,
            "--write-media", filepath
        ]

        print(f"生成 {audio_file}: {text[:20]}...")
        subprocess.run(cmd, capture_output=True)

    print(f"\n完成！共生成 {len(dialogue)} 条语音")
    return True

def main():
    if len(sys.argv) < 2:
        print("用法: python3 重新生成TTS.py <剧集目录>")
        sys.exit(1)

    episode_dir = sys.argv[1]
    regenerate_tts(episode_dir)

if __name__ == "__main__":
    main()
