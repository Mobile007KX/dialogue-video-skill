#!/usr/bin/env python3
"""
通用视频合成脚本
从剧本.json读取台词，与视频素材合成为完整短剧

用法：python3 合成脚本.py [剧集目录]

字幕逻辑：
- 长台词按句子切分（句号、叹号、问号）
- 每句按字数比例分配显示时间
- 说一句显示一句，说完消失
- 单句超长时最多分2行显示
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

def split_into_sentences(text, fine_grained=True):
    """
    按句子切分长台词

    fine_grained=True 时：按逗号、句号等切分，适合大段独白
    fine_grained=False 时：只按句号/叹号/问号切分

    每个片段独立显示，说一句出现一句
    """
    sentences = []
    current = ""

    if fine_grained:
        # 细粒度切分：逗号、句号、叹号、问号都作为切分点
        end_marks = ['，', '。', '！', '？', ',', '!', '?']
    else:
        # 粗粒度切分：只按句子结束符
        end_marks = ['。', '！', '？', '!', '?']

    for char in text:
        current += char
        if char in end_marks:
            if current.strip():
                sentences.append(current.strip())
            current = ""

    # 处理没有结尾标点的部分（如省略号结尾）
    if current.strip():
        sentences.append(current.strip())

    # 如果整句没有标点，返回原文
    return sentences if sentences else [text]

def wrap_subtitle_line(text, max_chars=14):
    """
    单句字幕分行，最多2行
    用于单个句子太长时的处理
    """
    if len(text) <= max_chars:
        return [text]

    # 优先在逗号、顿号处分行
    soft_breaks = ['，', '、', '；', '：', ' ']

    # 找最佳分割点
    best_pos = -1
    for i, char in enumerate(text):
        if char in soft_breaks and i >= len(text) * 0.3 and i <= len(text) * 0.7:
            best_pos = i + 1

    # 如果找到了合适的分割点
    if best_pos > 0:
        return [text[:best_pos].strip(), text[best_pos:].strip()]

    # 否则强制从中间分割
    mid = len(text) // 2
    return [text[:mid], text[mid:]]

def strip_punctuation(text):
    """去掉字幕中的标点符号，保持干净"""
    punctuation = '，。！？、；：""''（）【】《》—…·,!?;:\'"()[]'
    return ''.join(char for char in text if char not in punctuation)

def escape_text(text):
    """转义ffmpeg drawtext特殊字符"""
    # 转义顺序很重要
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "'\\''")
    text = text.replace(":", "\\:")
    return text

def get_duration(file_path):
    """获取音频/视频时长"""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", file_path],
        capture_output=True, text=True
    )
    output = result.stdout.strip()
    if not output:
        return 0.0
    return float(output)

def get_video_height(video_path):
    """获取视频高度"""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=height", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
        capture_output=True, text=True
    )
    return int(result.stdout.strip())

def create_segment(index, audio_file, character, subtitle, config):
    """
    创建单个视频片段（视频+音频+分时字幕）

    字幕逻辑：
    1. 长台词按句子切分
    2. 每句按字数比例分配时间
    3. 使用enable='between(t,start,end)'控制显示时间
    """
    audio_path = f"{config['audio_dir']}/{audio_file}"
    duration = get_duration(audio_path)

    # 选择视频素材
    char_a = config.get("char_a", DEFAULT_CHAR_A)
    char_b = config.get("char_b", DEFAULT_CHAR_B)
    if character == char_a:
        video_src = config["video_a"]
    else:
        video_src = config["video_b"]
    video_duration = get_duration(video_src)

    # 循环视频以适配音频长度
    loop_count = int(duration / video_duration) + 1

    output_path = f"{config['temp_dir']}/seg_{index:02d}.mp4"

    # 根据视频高度自适应字体大小（基准：688px高度对应32px字体）
    video_height = get_video_height(video_src)
    scale = video_height / 688
    fontsize = int(32 * scale)
    line_height = int(40 * scale)
    border_width = int(3 * scale)
    base_y_offset = int(100 * scale)  # 距离底部的基准距离

    # === 核心：按句子切分，分时显示 ===
    # 长台词（超过20字）使用细粒度切分（逗号也切），短台词只按句子切
    use_fine_grained = len(subtitle) > 20
    sentences = split_into_sentences(subtitle, fine_grained=use_fine_grained)
    total_chars = sum(len(s) for s in sentences)

    # 构建滤镜链
    filter_parts = [f"[0:v]trim=0:{duration},setpts=PTS-STARTPTS"]

    current_time = 0.0
    for sent in sentences:
        # 计算这句的显示时长（按字数比例）
        sent_duration = duration * (len(sent) / total_chars) if total_chars > 0 else duration
        end_time = current_time + sent_duration

        # 单句太长时分行（最多2行）
        lines = wrap_subtitle_line(sent, max_chars=14)
        num_lines = len(lines)

        # 计算垂直位置（从底部往上）
        for i, line in enumerate(lines):
            # 去掉标点符号，保持字幕干净
            line_clean = strip_punctuation(line)
            line_escaped = escape_text(line_clean)

            # y位置：最后一行在base_y_offset，往上叠加
            y_offset = base_y_offset + (num_lines - 1 - i) * line_height
            y_pos = f"h-{y_offset}"

            # 添加带时间控制的drawtext
            filter_parts.append(
                f"drawtext=text='{line_escaped}':"
                f"enable='between(t,{current_time:.3f},{end_time:.3f})':"
                f"font='PingFang SC':"
                f"fontsize={fontsize}:fontcolor=white:borderw={border_width}:bordercolor=black:"
                f"x=(w-text_w)/2:y={y_pos}"
            )

        current_time = end_time

    filter_str = ",".join(filter_parts) + "[v]"

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", str(loop_count - 1),
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

    # 显示句子数量
    sent_info = f"({len(sentences)}句)" if len(sentences) > 1 else ""
    print(f"生成片段 {index}: {character} - {subtitle[:20]}... ({duration:.2f}s) {sent_info}")
    subprocess.run(cmd, capture_output=True)

    return output_path

def concat_segments(segment_files, output_path, config):
    """拼接所有片段"""
    list_file = f"{config['temp_dir']}/concat_list.txt"
    with open(list_file, "w") as f:
        for seg in segment_files:
            f.write(f"file '{os.path.basename(seg)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", "concat_list.txt",
        "-c", "copy",
        os.path.abspath(output_path)
    ]

    print(f"\n拼接所有片段...")
    subprocess.run(cmd, capture_output=True, cwd=config['temp_dir'])
    print(f"输出: {output_path}")

def main():
    if len(sys.argv) > 1:
        episode_dir = sys.argv[1]
    else:
        episode_dir = os.getcwd()

    config = load_config(episode_dir)

    os.makedirs(config["temp_dir"], exist_ok=True)
    os.makedirs(config["output_dir"], exist_ok=True)

    title = config.get("title", "未命名")
    print("=" * 50)
    print(f"《{title}》视频合成")
    print("=" * 50)

    dialogue = config["dialogue"]
    segments = []
    for i, item in enumerate(dialogue, 1):
        audio = item["audio"]
        char = item["character"]
        sub = item["text"]
        seg_path = create_segment(i, audio, char, sub, config)
        segments.append(seg_path)

    output_file = f"{config['output_dir']}/{title}_demo.mp4"
    concat_segments(segments, output_file, config)

    final_duration = get_duration(output_file)
    print(f"\n完成！总时长: {final_duration:.2f}秒")
    print(f"文件位置: {output_file}")

if __name__ == "__main__":
    main()
