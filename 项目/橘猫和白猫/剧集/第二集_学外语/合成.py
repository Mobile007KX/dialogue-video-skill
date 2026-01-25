#!/usr/bin/env python3
"""
通用视频合成脚本
从剧本.json读取台词，与视频素材合成为完整短剧

用法：python3 合成.py [剧集目录]
"""

import subprocess
import os
import sys
import json

def load_config(episode_dir):
    """从剧集目录加载配置"""
    config = {
        "episode_dir": episode_dir,
        "audio_dir": f"{episode_dir}/音频",
        "output_dir": f"{episode_dir}/成品",
        "temp_dir": f"{episode_dir}/temp_segments",
        "video_a": f"{episode_dir}/橘猫说话.mp4",
        "video_b": f"{episode_dir}/白猫说话.mp4",
    }

    # 从剧本.json读取台词
    script_file = f"{episode_dir}/剧本.json"
    if os.path.exists(script_file):
        with open(script_file, "r", encoding="utf-8") as f:
            script_data = json.load(f)
            config["dialogue"] = script_data.get("dialogue", [])
            config["title"] = script_data.get("title", "未命名")
            # 支持自定义角色名到视频的映射
            if "characters" in script_data:
                chars = script_data["characters"]
                if "A" in chars:
                    config["video_a"] = f"{episode_dir}/{chars['A']['video']}"
                    config["char_a"] = chars['A']['name']
                if "B" in chars:
                    config["video_b"] = f"{episode_dir}/{chars['B']['video']}"
                    config["char_b"] = chars['B']['name']
    else:
        print(f"错误：找不到 {script_file}")
        print("请先生成TTS，TTS生成时会自动创建剧本.json")
        sys.exit(1)

    return config

# 默认角色名
DEFAULT_CHAR_A = "橘猫"
DEFAULT_CHAR_B = "白猫"

def wrap_subtitle(text, max_chars=14):
    """智能分行字幕，每行不超过max_chars个字符，返回行列表"""
    if len(text) <= max_chars:
        return [text]

    # 优先在标点处分行
    punctuation = ['，', '。', '！', '？', '、', '；', '：', ' ']

    lines = []
    current = ""

    for char in text:
        current += char
        # 如果当前行够长且遇到标点，就分行
        if len(current) >= max_chars * 0.6 and char in punctuation:
            lines.append(current)
            current = ""
        # 如果超过最大长度，强制分行
        elif len(current) >= max_chars:
            lines.append(current)
            current = ""

    if current:
        lines.append(current)

    return lines

def get_duration(file_path):
    """获取音频/视频时长"""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", file_path],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())

def create_segment(index, audio_file, character, subtitle, config):
    """创建单个视频片段（视频+音频+字幕）"""
    audio_path = f"{config['audio_dir']}/{audio_file}"
    duration = get_duration(audio_path)

    # 选择视频素材：根据角色名判断用哪个视频
    char_a = config.get("char_a", DEFAULT_CHAR_A)
    char_b = config.get("char_b", DEFAULT_CHAR_B)
    if character == char_a:
        video_src = config["video_a"]
    else:
        video_src = config["video_b"]
    video_duration = get_duration(video_src)

    # 如果音频比视频长，需要循环视频
    loop_count = int(duration / video_duration) + 1

    output_path = f"{config['temp_dir']}/seg_{index:02d}.mp4"

    # 使用ffmpeg合成：循环视频 + 音频 + 字幕
    # 多行字幕使用多个drawtext滤镜堆叠
    lines = wrap_subtitle(subtitle, max_chars=12)

    # 构建滤镜链
    filter_parts = [f"[0:v]trim=0:{duration},setpts=PTS-STARTPTS"]

    line_height = 40  # 每行高度
    base_y = 120 + (len(lines) - 1) * line_height // 2  # 从底部往上算

    for i, line in enumerate(lines):
        line_escaped = line.replace("'", "'\\''").replace(":", "\\:")
        y_pos = f"h-{base_y - i * line_height}"
        filter_parts.append(
            f"drawtext=text='{line_escaped}':"
            f"font='PingFang SC':"
            f"fontsize=32:fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y={y_pos}"
        )

    filter_str = ",".join(filter_parts) + "[v]"

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", str(loop_count - 1),  # 循环视频
        "-i", video_src,
        "-i", audio_path,
        "-filter_complex", filter_str,
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-t", str(duration),
        "-shortest",
        output_path
    ]

    print(f"生成片段 {index}: {character} - {subtitle[:20]}... ({duration:.2f}s)")
    subprocess.run(cmd, capture_output=True)

    return output_path

def concat_segments(segment_files, output_path, config):
    """拼接所有片段"""
    # 创建文件列表
    list_file = f"{config['temp_dir']}/concat_list.txt"
    with open(list_file, "w") as f:
        for seg in segment_files:
            f.write(f"file '{seg}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        output_path
    ]

    print(f"\n拼接所有片段...")
    subprocess.run(cmd, capture_output=True)
    print(f"输出: {output_path}")

def main():
    # 获取剧集目录：命令行参数 或 当前目录
    if len(sys.argv) > 1:
        episode_dir = sys.argv[1]
    else:
        episode_dir = os.getcwd()

    # 加载配置（从剧本.json）
    config = load_config(episode_dir)

    # 创建临时目录
    os.makedirs(config["temp_dir"], exist_ok=True)
    os.makedirs(config["output_dir"], exist_ok=True)

    title = config.get("title", "未命名")
    print("=" * 50)
    print(f"《{title}》视频合成")
    print("=" * 50)

    # 生成每个片段
    dialogue = config["dialogue"]
    segments = []
    for i, item in enumerate(dialogue, 1):
        audio = item["audio"]
        char = item["character"]
        sub = item["text"]
        seg_path = create_segment(i, audio, char, sub, config)
        segments.append(seg_path)

    # 拼接所有片段
    output_file = f"{config['output_dir']}/{title}_demo.mp4"
    concat_segments(segments, output_file, config)

    # 获取最终时长
    final_duration = get_duration(output_file)
    print(f"\n完成！总时长: {final_duration:.2f}秒")
    print(f"文件位置: {output_file}")

if __name__ == "__main__":
    main()
