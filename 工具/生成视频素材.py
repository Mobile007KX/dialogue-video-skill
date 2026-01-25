#!/usr/bin/env python3
"""
视频素材生成脚本
从定装照生成对话视频素材（橘猫说话、白猫说话）

用法：python3 生成视频素材.py <剧集目录>

前置条件：
- 剧集目录下有 起始帧.png
- MiniMax API Key 已配置

生成结果：
- 橘猫说话.mp4
- 白猫说话.mp4
"""

import subprocess
import os
import sys
import json

# MiniMax视频生成Skill路径
MINIMAX_SKILL_PATH = os.path.expanduser("~/.config/alma/skills/my-minimax-video-gen")

# 固定参数（不可更改）
VIDEO_CONFIG = {
    "model": "MiniMax-Hailuo-02",
    "resolution": "512P",
    "duration": 6,
    "cost_per_video": 0.60
}

# Prompt模板
PROMPT_A_TALKING = """Same scene, same lighting, same camera angle, static camera, absolutely no camera movement.
Orange cat is TALKING - mouth movements, expressive gestures, animated face.
White cat is LISTENING SILENTLY - mouth firmly CLOSED, only subtle head nods and eye movements.
Both characters stay in frame throughout.
Loop-friendly: end pose must be similar to start pose for seamless looping.
3D Pixar animation style."""

PROMPT_B_TALKING = """Same scene, same lighting, same camera angle, static camera, absolutely no camera movement.
White cat is TALKING - mouth movements, gestures, expressive face.
Orange cat is LISTENING SILENTLY - mouth firmly CLOSED, just nodding occasionally.
Both characters stay in frame throughout.
Loop-friendly: end pose must be similar to start pose for seamless looping.
3D Pixar animation style."""

def create_video_request(episode_dir, character, prompt, output_name):
    """创建视频请求JSON文件"""
    first_frame = os.path.join(episode_dir, "起始帧.png")
    if not os.path.exists(first_frame):
        # 尝试其他格式
        for ext in [".jpg", ".jpeg"]:
            alt_path = os.path.join(episode_dir, f"起始帧{ext}")
            if os.path.exists(alt_path):
                first_frame = alt_path
                break

    request = {
        "mode": "image_to_video",
        "model": VIDEO_CONFIG["model"],
        "duration": VIDEO_CONFIG["duration"],
        "resolution": VIDEO_CONFIG["resolution"],
        "prompt": prompt,
        "first_frame_image": first_frame,
        "out": os.path.join(episode_dir, output_name),
        "poll_interval_ms": 10000,
        "max_polls": 90
    }

    request_path = os.path.join(episode_dir, f"video_request_{character}.json")
    with open(request_path, 'w', encoding='utf-8') as f:
        json.dump(request, f, ensure_ascii=False, indent=2)

    return request_path

def generate_video(request_path):
    """调用MiniMax视频生成"""
    script_path = os.path.join(MINIMAX_SKILL_PATH, "scripts", "minimax-video-gen.js")

    cmd = ["node", script_path, "--requestFile", request_path]

    print(f"调用: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=MINIMAX_SKILL_PATH, capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"错误: {result.stderr}")
        return False

def main():
    if len(sys.argv) < 2:
        print("用法: python3 生成视频素材.py <剧集目录>")
        print("示例: python3 生成视频素材.py 剧集/第五集_新剧/")
        sys.exit(1)

    episode_dir = sys.argv[1]

    # 检查起始帧
    first_frame = os.path.join(episode_dir, "起始帧.png")
    if not os.path.exists(first_frame):
        print(f"错误: 找不到起始帧 {first_frame}")
        print("请先上传定装照并命名为 起始帧.png")
        sys.exit(1)

    print("=" * 50)
    print("视频素材生成")
    print("=" * 50)
    print(f"模型: {VIDEO_CONFIG['model']}")
    print(f"分辨率: {VIDEO_CONFIG['resolution']}")
    print(f"时长: {VIDEO_CONFIG['duration']}秒")
    print(f"预计费用: {VIDEO_CONFIG['cost_per_video'] * 2}元（2条）")
    print("=" * 50)

    # 生成橘猫说话
    print("\n[1/2] 生成: 橘猫说话.mp4")
    request_a = create_video_request(episode_dir, "橘猫说话", PROMPT_A_TALKING, "橘猫说话.mp4")
    success_a = generate_video(request_a)

    # 生成白猫说话
    print("\n[2/2] 生成: 白猫说话.mp4")
    request_b = create_video_request(episode_dir, "白猫说话", PROMPT_B_TALKING, "白猫说话.mp4")
    success_b = generate_video(request_b)

    # 结果
    print("\n" + "=" * 50)
    if success_a and success_b:
        print("✅ 视频素材生成完成！")
        print(f"  - {episode_dir}/橘猫说话.mp4")
        print(f"  - {episode_dir}/白猫说话.mp4")
    else:
        print("❌ 部分视频生成失败，请检查错误信息")

if __name__ == "__main__":
    main()
