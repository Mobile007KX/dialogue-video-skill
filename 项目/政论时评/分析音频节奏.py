#!/usr/bin/env python3
"""根据音频静音段分析，重新规划字幕时间轴"""

# 播音稿（11个场景）
script = [
    "储蓄节节高，负债层层压",  # S1
    "2025年上半年，全国居民人均存款，再创历史新高",  # S2
    "人均存款余额，13万6800元",  # S3
    "听起来是好事，对吧？",  # S4
    "第一，表面是储蓄意愿增强，实际是消费信心不足",  # S5
    "第二，钱不是存在银行里，而是躲在银行里",  # S6
    "上半年关闭门店，161万家，每天8800家",  # S7
    "第三，经济好的时候，宁可犯错不能错过，经济差的时候，宁可错过不能犯错",  # S8
    "但这还并不是最重要的",  # S9
    "真正重要的是，守住现金流，多存钱少欠钱",  # S10
    "这也是短期震动，相信经过不断努力，未来一定越来越好",  # S11
]

# ffmpeg检测到的主要静音段（分界点）
silences = [
    (1.96, 2.67),   # S1结束
    (6.29, 6.91),   # S2结束
    (9.05, 9.64),   # S3结束
    (11.57, 12.00), # S4结束
    (14.51, 15.24), # S5结束
    (18.12, 18.55), # S6结束
    (21.93, 22.33), # S7结束
    (28.08, 28.79), # S8结束（较长）
    (30.98, 31.34), # S9结束
    (33.59, 34.08), # S10结束
    (34.87, 35.31), # S11结束（音频还有尾音到37.25s）
]

# 根据静音段推算每个场景的时间范围
scenes = []
start = 0
for i, (silence_start, silence_end) in enumerate(silences):
    scene_id = f"s{i+1}"
    duration = silence_end - start

    scenes.append({
        "id": scene_id,
        "text": script[i],
        "start": round(start, 2),
        "end": round(silence_end, 2),
        "duration": round(duration, 2)
    })

    # 下一个场景从静音结束后开始
    start = silence_end

# 打印分析结果
print("=" * 80)
print("音频节奏分析（根据静音段）")
print("=" * 80)
print()

for scene in scenes:
    print(f"{scene['id'].upper():4s} [{scene['start']:5.2f}s - {scene['end']:5.2f}s] (时长{scene['duration']:5.2f}s)")
    print(f"     {scene['text']}")
    print()

print("=" * 80)
print(f"总时长: 37.25秒")
print(f"最后场景结束: {scenes[-1]['end']}秒")
print(f"尾音/BGM: {37.25 - scenes[-1]['end']:.2f}秒")
print("=" * 80)

# 生成新的timeline代码
print("\n" + "=" * 80)
print("新timeline代码（粘贴到v5.html）")
print("=" * 80)
print()
print("const timeline = [")

for i, scene in enumerate(scenes, 1):
    sid = scene['id']
    start = scene['start']
    dur = scene['duration']

    # 根据场景内容调整内部动画时间
    # 简化版：开场0s，中间动画0.3s-0.5s间隔
    if i in [1, 4, 9]:  # 简单场景（2行文字）
        print(f"  ['{sid}', {start:5.2f}, {dur:5.2f}, [")
        print(f"    [0,    '#{sid} .fade:nth-child(1)', 'fade'],")
        print(f"    [0.4,  '#{sid} .fade:nth-child(2)', 'fade'],")
        print(f"  ]],")
    elif i in [2, 3, 7, 10, 11]:  # 中等场景（3行文字）
        print(f"  ['{sid}', {start:5.2f}, {dur:5.2f}, [")
        print(f"    [0,    '#{sid} .fade:nth-child(1)', 'fade'],")
        print(f"    [0.3,  '#{sid} .fade:nth-child(2)', 'fade'],")
        print(f"    [0.6,  '#{sid} .fade:nth-child(3)', 'fade'],")
        print(f"  ]],")
    elif i == 3:  # S3有数字counter
        print(f"  ['{sid}', {start:5.2f}, {dur:5.2f}, [")
        print(f"    [0,    '#{sid} .fade', 'fade'],")
        print(f"    [0.3,  '#{sid} .pop', 'pop'],")
        print(f"    [0.5,  '#counter1', 'counter:136800'],")
        print(f"  ]],")
    elif i == 7:  # S7有数字counter
        print(f"  ['{sid}', {start:5.2f}, {dur:5.2f}, [")
        print(f"    [0,    '#{sid} .fade', 'fade'],")
        print(f"    [0.3,  '#{sid} .pop', 'pop'],")
        print(f"    [0.5,  '#counter2', 'counter:161'],")
        print(f"    [1.6,  '#{sid} .fade:nth-child(3)', 'fade'],")
        print(f"  ]],")
    elif i in [5, 6]:  # 第一/第二（对比句）
        print(f"  ['{sid}', {start:5.2f}, {dur:5.2f}, [")
        print(f"    [0,    '#{sid} .fade:nth-child(1)', 'fade'],")
        print(f"    [0.5,  '#{sid} .fade:nth-child(2)', 'fade'],")
        print(f"    [1.2,  '#{sid} .fade:nth-child(3)', 'fade'],")
        print(f"  ]],")
    elif i == 8:  # S8（第三，最长句）
        print(f"  ['{sid}', {start:5.2f}, {dur:5.2f}, [")
        print(f"    [0,    '#{sid} .fade:nth-child(1)', 'fade'],")
        print(f"    [0.4,  '#{sid} .fade:nth-child(2)', 'fade'],")
        print(f"    [0.8,  '#{sid} .fade:nth-child(3)', 'fade'],")
        print(f"    [2.5,  '#{sid} .fade:nth-child(4)', 'fade'],")
        print(f"    [2.9,  '#{sid} .fade:nth-child(5)', 'fade'],")
        print(f"  ]],")

print("];")
print()
print(f"const TOTAL = 37.25;")
