#!/usr/bin/env python3
"""从Whisper转写结果生成精确的timeline"""
import json

# 读取Whisper转写结果
with open("AIDOCS/人均存款_Kevin_1.5x.json", "r", encoding="utf-8") as f:
    data = json.load(f)

segments = data["segments"]

# 场景映射（根据Whisper的segment ID）
scene_mapping = [
    ("s1", [0], "储蓄节节高，负债层层压"),
    ("s2", [1,2,3], "2025年上半年，全国居民人均存款，再创历史新高"),
    ("s3", [4], "人均存款余额，13万6800元"),
    ("s4", [5,6], "听起来是好事，对吧？"),
    ("s5", [7,8], "第一，表面是储蓄意愿增强，实际是消费信心不足"),
    ("s6", [9,10], "第二，钱不是存在银行里，而是躲在银行里"),
    ("s7", [11,12], "上半年关闭门店，161万家，每天8800家"),
    ("s8", [13,14,15,16], "第三，经济好的时候，宁可犯错不能错过，经济差的时候，宁可错过不能犯错"),
    ("s9", [17], "但这还并不是最重要的"),
    ("s10", [18,19,20], "真正重要的是，守住现金流，多存钱少欠钱"),
    ("s11", [21,22,23], "这也是短期震动，相信经过不断努力，未来一定越来越好"),
]

# 生成timeline
timeline = []
for sid, seg_ids, text in scene_mapping:
    start = segments[seg_ids[0]]["start"]
    end = segments[seg_ids[-1]]["end"]
    duration = end - start

    timeline.append({
        "id": sid,
        "num": int(sid[1:]),
        "start": round(start, 2),
        "duration": round(duration, 2),
        "text": text
    })

# 打印结果
print("=" * 80)
print("基于Whisper转写的Timeline")
print("=" * 80)
print()

for scene in timeline:
    end = scene["start"] + scene["duration"]
    print(f"{scene['id'].upper():4s} [{scene['start']:5.2f}s - {end:5.2f}s] (时长{scene['duration']:5.2f}s)")
    print(f"     {scene['text']}")
    print()

# 生成代码
print("=" * 80)
print("Timeline代码（粘贴到v5.html）")
print("=" * 80)
print()
print("const timeline = [")

for s in timeline:
    sid = s['id']
    num = s['num']
    start = s['start']
    dur = s['duration']

    print(f"  ['{sid}', {start:5.2f}, {dur:5.2f}, [")

    # 根据场景添加动画
    if num in [1, 4, 9]:  # 简单场景（2行）
        print(f"    [0,    '#{sid} .fade:nth-child(1)', 'fade'],")
        print(f"    [0.4,  '#{sid} .fade:nth-child(2)', 'fade'],")
    elif num in [3, 7]:  # 有counter的场景
        print(f"    [0,    '#{sid} .fade', 'fade'],")
        print(f"    [0.3,  '#{sid} .pop', 'pop'],")
        print(f"    [0.5,  '#counter{1 if num==3 else 2}', 'counter:{136800 if num==3 else 161}'],")
        if num == 7:
            print(f"    [1.6,  '#{sid} .fade:nth-child(3)', 'fade'],")
    elif num in [5, 6]:  # 第一/第二（对比句）
        print(f"    [0,    '#{sid} .fade:nth-child(1)', 'fade'],")
        print(f"    [0.5,  '#{sid} .fade:nth-child(2)', 'fade'],")
        print(f"    [1.2,  '#{sid} .fade:nth-child(3)', 'fade'],")
    elif num == 8:  # 第三（最长句）
        print(f"    [0,    '#{sid} .fade:nth-child(1)', 'fade'],")
        print(f"    [0.4,  '#{sid} .fade:nth-child(2)', 'fade'],")
        print(f"    [0.8,  '#{sid} .fade:nth-child(3)', 'fade'],")
        print(f"    [2.5,  '#{sid} .fade:nth-child(4)', 'fade'],")
        print(f"    [2.9,  '#{sid} .fade:nth-child(5)', 'fade'],")
    elif num == 9:  # pop动画
        print(f"    [0,    '#{sid} .pop:nth-child(1)', 'pop'],")
        print(f"    [0.4,  '#{sid} .pop:nth-child(2)', 'pop'],")
    else:  # 其他场景（3行）
        print(f"    [0,    '#{sid} .fade:nth-child(1)', 'fade'],")
        print(f"    [0.3,  '#{sid} .fade:nth-child(2)', 'fade'],")
        print(f"    [0.6,  '#{sid} .fade:nth-child(3)', 'fade'],")

    print(f"  ]],")

print("];")
print()
print("const TOTAL = 37.25;")
