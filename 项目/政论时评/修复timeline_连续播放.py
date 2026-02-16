#!/usr/bin/env python3
"""修复：生成连续timeline，去掉gap"""
import json

# 读取Whisper结果
with open("AIDOCS/人均存款_Kevin_1.5x.json", "r", encoding="utf-8") as f:
    data = json.load(f)

segments = data["segments"]

# 场景映射
scene_mapping = [
    ("s1", [0]),
    ("s2", [1,2,3]),
    ("s3", [4]),
    ("s4", [5,6]),
    ("s5", [7,8]),
    ("s6", [9,10]),
    ("s7", [11,12]),
    ("s8", [13,14,15,16]),
    ("s9", [17]),
    ("s10", [18,19,20]),
    ("s11", [21,22,23]),
]

# 计算每个场景的duration（使用segment的实际时长）
scene_durations = []
for sid, seg_ids in scene_mapping:
    start = segments[seg_ids[0]]["start"]
    end = segments[seg_ids[-1]]["end"]
    duration = end - start
    scene_durations.append((sid, duration))

# 生成连续timeline（start紧接着上一个场景）
timeline = []
累计时间 = 0.0
for sid, dur in scene_durations:
    timeline.append((sid, 累计时间, dur))
    累计时间 += dur

# 打印
print("=" * 80)
print("连续Timeline（无gap）")
print("=" * 80)
for sid, start, dur in timeline:
    end = start + dur
    print(f"{sid.upper():4s} [{start:5.2f}s - {end:5.2f}s] (时长{dur:5.2f}s)")

print(f"\n总时长: {累计时间:.2f}s")
print(f"音频时长: 37.25s")

if 累计时间 > 37.25:
    print(f"\n⚠️  总时长{累计时间:.2f}s超出音频{37.25}s，需要压缩{累计时间 - 37.25:.2f}s")
    print("解决：等比例压缩所有duration")
    比例 = 37.25 / 累计时间
    timeline_压缩 = [(sid, start * 比例, dur * 比例) for sid, start, dur in timeline]
    print("\n压缩后：")
    for sid, start, dur in timeline_压缩:
        end = start + dur
        print(f"{sid.upper():4s} [{start:5.2f}s - {end:5.2f}s] (时长{dur:5.2f}s)")
    timeline = timeline_压缩

# 生成代码
print("\n" + "=" * 80)
print("Timeline代码")
print("=" * 80)
print("\nconst timeline = [")

for sid, start, dur in timeline:
    num = int(sid[1:])
    print(f"  ['{sid}', {start:5.2f}, {dur:5.2f}, [")

    if num in [1, 4, 9]:
        print(f"    [0,    '#{sid} .fade:nth-child(1)', 'fade'],")
        print(f"    [0.4,  '#{sid} .fade:nth-child(2)', 'fade'],")
    elif num in [3, 7]:
        print(f"    [0,    '#{sid} .fade', 'fade'],")
        print(f"    [0.3,  '#{sid} .pop', 'pop'],")
        print(f"    [0.5,  '#counter{1 if num==3 else 2}', 'counter:{136800 if num==3 else 161}'],")
        if num == 7:
            print(f"    [1.6,  '#{sid} .fade:nth-child(3)', 'fade'],")
    elif num in [5, 6]:
        print(f"    [0,    '#{sid} .fade:nth-child(1)', 'fade'],")
        print(f"    [0.5,  '#{sid} .fade:nth-child(2)', 'fade'],")
        print(f"    [1.2,  '#{sid} .fade:nth-child(3)', 'fade'],")
    elif num == 8:
        print(f"    [0,    '#{sid} .fade:nth-child(1)', 'fade'],")
        print(f"    [0.4,  '#{sid} .fade:nth-child(2)', 'fade'],")
        print(f"    [0.8,  '#{sid} .fade:nth-child(3)', 'fade'],")
        print(f"    [2.5,  '#{sid} .fade:nth-child(4)', 'fade'],")
        print(f"    [2.9,  '#{sid} .fade:nth-child(5)', 'fade'],")
    elif num == 9:
        print(f"    [0,    '#{sid} .pop:nth-child(1)', 'pop'],")
        print(f"    [0.4,  '#{sid} .pop:nth-child(2)', 'pop'],")
    else:
        print(f"    [0,    '#{sid} .fade:nth-child(1)', 'fade'],")
        print(f"    [0.3,  '#{sid} .fade:nth-child(2)', 'fade'],")
        print(f"    [0.6,  '#{sid} .fade:nth-child(3)', 'fade'],")

    print(f"  ]],")

print("];")
print("\nconst TOTAL = 37.25;")
