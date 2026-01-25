#!/usr/bin/env python3
"""
一键生成脚本
从定装照+剧本一键生成完整短剧

用法：python3 一键生成.py <剧集目录> [剧本文件]

前置条件：
- 剧集目录下有 起始帧.png
- 剧本文件（纯文本格式）或 剧集目录下有 剧本.txt

完整流程：
1. 生成视频素材（橘猫说话、白猫说话）
2. 生成TTS语音
3. 保存剧本.json
4. 合成最终视频
"""

import subprocess
import os
import sys

# 工具目录
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_name, *args):
    """运行工具脚本"""
    script_path = os.path.join(TOOLS_DIR, script_name)
    cmd = ["python3", script_path] + list(args)
    print(f"\n>>> 执行: python3 {script_name} {' '.join(args)}\n")
    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    if len(sys.argv) < 2:
        print("用法: python3 一键生成.py <剧集目录> [剧本文件]")
        print("示例: python3 一键生成.py 剧集/第五集_新剧/ 剧本.txt")
        sys.exit(1)

    episode_dir = sys.argv[1]
    script_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(episode_dir, "剧本.txt")

    # 检查前置条件
    first_frame = os.path.join(episode_dir, "起始帧.png")
    if not os.path.exists(first_frame):
        print(f"错误: 找不到起始帧 {first_frame}")
        sys.exit(1)

    if not os.path.exists(script_file):
        print(f"错误: 找不到剧本文件 {script_file}")
        sys.exit(1)

    print("=" * 60)
    print("  一键生成短剧")
    print("=" * 60)
    print(f"剧集目录: {episode_dir}")
    print(f"剧本文件: {script_file}")
    print("=" * 60)

    # Step 1: 检查视频素材是否已存在
    video_a = os.path.join(episode_dir, "橘猫说话.mp4")
    video_b = os.path.join(episode_dir, "白猫说话.mp4")

    if os.path.exists(video_a) and os.path.exists(video_b):
        print("\n✅ 视频素材已存在，跳过生成")
    else:
        print("\n" + "=" * 60)
        print("  Step 1/3: 生成视频素材")
        print("=" * 60)
        if not run_script("生成视频素材.py", episode_dir):
            print("❌ 视频素材生成失败")
            sys.exit(1)

    # Step 2: 生成TTS
    print("\n" + "=" * 60)
    print("  Step 2/3: 生成TTS语音")
    print("=" * 60)
    if not run_script("生成TTS.py", episode_dir, script_file):
        print("❌ TTS生成失败")
        sys.exit(1)

    # Step 3: 合成视频
    print("\n" + "=" * 60)
    print("  Step 3/3: 合成视频")
    print("=" * 60)
    if not run_script("合成脚本.py", episode_dir):
        print("❌ 视频合成失败")
        sys.exit(1)

    # 完成
    print("\n" + "=" * 60)
    print("  ✅ 一键生成完成！")
    print("=" * 60)

    # 显示结果
    title = os.path.basename(episode_dir.rstrip('/'))
    if '_' in title:
        title = title.split('_', 1)[1]
    output_file = os.path.join(episode_dir, "成品", f"{title}_demo.mp4")
    print(f"成品: {output_file}")

if __name__ == "__main__":
    main()
