#!/usr/bin/env python3
"""字节AI视频：视频合成（逐帧精确控制）
Timeline已通过Whisper校准，无需缩放"""
import shutil
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

# 配置
EPISODE_DIR = Path(__file__).parent
HTML_PATH = EPISODE_DIR / "字幕_v6_uipro.html"
AUDIO_PATH = EPISODE_DIR / "音频/字节AI_郜老师_原速.wav"
FRAMES_DIR = EPISODE_DIR / "成品/frames"
VIDEO_NO_AUDIO = EPISODE_DIR / "成品/视频_无音频.mp4"
VIDEO_FINAL = EPISODE_DIR / "成品/字节AI_郜老师_最终版.mp4"

# 从音频获取实际时长
result = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", str(AUDIO_PATH)],
    capture_output=True, text=True
)
DURATION = float(result.stdout.strip())
FPS = 30
TOTAL_FRAMES = int(DURATION * FPS)

# 逐帧渲染JS（counter用静态计算替代requestAnimationFrame）
RENDER_JS = """
const counterConfigs = {
    6:  {id:'counter1', target:90,   triggerDelay:0.5, dur:1.2},
    7:  {id:'counter2', target:16,   triggerDelay:0.5, dur:1.0},
    14: {id:'counter3', target:7500, triggerDelay:2.2, dur:1.8},
    17: {id:'counter4', target:23,   triggerDelay:0.5, dur:1.2},
    18: {id:'counter5', target:1305, triggerDelay:0.5, dur:1.5}
};

window.renderAtTime = function(t) {
    scenes.forEach(s => {
        s.classList.remove('on');
        s.querySelectorAll('.show').forEach(el => el.classList.remove('show'));
    });
    bgImgs.forEach(b => b.classList.remove('on'));

    timeline.forEach(([sceneIdx, start, duration, animations]) => {
        if (t >= start && t < start + duration) {
            const scene = scenes[sceneIdx - 1];
            const bgImg = bgImgs[sceneIdx - 1];
            scene.classList.add('on');
            bgImg.classList.add('on');

            animations.forEach(([delay, selector, className]) => {
                if (t >= start + delay) {
                    scene.querySelectorAll(selector).forEach(el => el.classList.add(className));
                }
            });

            const cc = counterConfigs[sceneIdx];
            if (cc) {
                const el = document.getElementById(cc.id);
                if (el) {
                    if (t >= start + cc.triggerDelay) {
                        const elapsed = t - (start + cc.triggerDelay);
                        const progress = Math.min(elapsed / cc.dur, 1);
                        const ease = 1 - Math.pow(1 - progress, 3);
                        el.textContent = Math.floor(cc.target * ease).toLocaleString('zh-CN');
                    }
                }
            }
        }
    });

    progressFill.style.width = (t / TOTAL_DURATION * 100) + '%';
};
"""

print("=" * 70)
print("字节AI视频 合成（Whisper校准版）")
print("=" * 70)
print(f"音频时长: {DURATION:.2f}s | 帧率: {FPS}fps | 总帧数: {TOTAL_FRAMES}")
print("=" * 70)

# 准备目录
(EPISODE_DIR / "成品").mkdir(parents=True, exist_ok=True)
if FRAMES_DIR.exists():
    shutil.rmtree(FRAMES_DIR)
FRAMES_DIR.mkdir(parents=True)

# [1/3] 逐帧渲染
print("\n[1/3] 逐帧渲染...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 406, "height": 720})

    page.goto(f"file://{HTML_PATH.absolute()}")
    page.wait_for_load_state("networkidle")

    # 禁用CSS transition/animation
    page.evaluate("""
        const style = document.createElement('style');
        style.textContent = '*, *::before, *::after { transition: none !important; animation: none !important; }';
        document.head.appendChild(style);
    """)

    # 隐藏播放控制栏
    page.evaluate("""
        const bar = document.querySelector('.bar');
        if (bar) bar.style.display = 'none';
    """)

    # 注入渲染函数
    page.evaluate(RENDER_JS)

    for frame_num in range(TOTAL_FRAMES):
        target_time = frame_num / FPS
        page.evaluate(f"renderAtTime({target_time})")

        screenshot_path = FRAMES_DIR / f"frame_{frame_num:04d}.png"
        page.locator(".screen").screenshot(path=str(screenshot_path))

        if (frame_num + 1) % 300 == 0 or frame_num == TOTAL_FRAMES - 1:
            progress = (frame_num + 1) / TOTAL_FRAMES * 100
            print(f"  {progress:5.1f}% ({frame_num + 1}/{TOTAL_FRAMES}) t={target_time:.2f}s")

    browser.close()

print("  渲染完成")

# [2/3] ffmpeg合成视频（无音频）
print("\n[2/3] 合成视频...")
subprocess.run([
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", str(FRAMES_DIR / "frame_%04d.png"),
    "-c:v", "libx264", "-pix_fmt", "yuv420p",
    "-preset", "medium", "-crf", "23",
    str(VIDEO_NO_AUDIO)
], capture_output=True, check=True)
print("  完成")

# [3/3] 合并音频
print("\n[3/3] 合并音频...")
subprocess.run([
    "ffmpeg", "-y",
    "-i", str(VIDEO_NO_AUDIO),
    "-i", str(AUDIO_PATH),
    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    str(VIDEO_FINAL)
], capture_output=True, check=True)

# 输出文件信息
size_mb = VIDEO_FINAL.stat().st_size / 1024 / 1024
probe = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", str(VIDEO_FINAL)],
    capture_output=True, text=True
)
dur = float(probe.stdout.strip())

print(f"\n{'=' * 70}")
print(f"完成: {VIDEO_FINAL.name}")
print(f"大小: {size_mb:.2f}MB | 时长: {dur:.2f}s | 分辨率: 406x720")
print(f"{'=' * 70}")
