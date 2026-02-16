#!/usr/bin/env python3
"""取消中考：视频合成（逐帧精确控制）"""
import shutil
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

# 配置
PROJECT_DIR = Path(__file__).parent
HTML_PATH = PROJECT_DIR / "字幕.html"
AUDIO_PATH = PROJECT_DIR / "AIDOCS/取消中考_Kevin_1.5x.wav"
OUTPUT_DIR = PROJECT_DIR / "AIDOCS/frames"
VIDEO_NO_AUDIO = PROJECT_DIR / "AIDOCS/视频_无音频.mp4"
VIDEO_FINAL = PROJECT_DIR / "AIDOCS/取消中考_最终版.mp4"

DURATION = 56.67
FPS = 30
TOTAL_FRAMES = int(DURATION * FPS)

# 逐帧渲染函数（注入HTML）
RENDER_JS = """
window.renderAtTime = function(t) {
    document.querySelectorAll('.scene').forEach(s => s.classList.remove('on'));
    document.querySelectorAll('.show').forEach(e => e.classList.remove('show'));
    document.querySelectorAll('.bg-img').forEach(i => i.classList.remove('on'));
    curBg = 0;

    let matched = null;
    for (let i = 0; i < timeline.length; i++) {
        const [sid, st, dur, anims] = timeline[i];
        if (t >= st && t < st + dur) {
            matched = timeline[i];
            break;
        }
        if (t >= st + dur) {
            const next = timeline[i + 1];
            if (!next || t < next[1]) {
                matched = timeline[i];
                break;
            }
        }
    }

    if (matched) {
        const [sid, st, dur, anims] = matched;
        document.getElementById(sid).classList.add('on');
        switchBg(bgMap[sid] || 1);

        for (const [d, sel, act] of anims) {
            if (t >= st + d) {
                if (act === 'fade' || act === 'pop') {
                    document.querySelectorAll(sel).forEach(e => e.classList.add('show'));
                } else if (act.startsWith('counter:')) {
                    const target = +act.split(':')[1];
                    const el = document.querySelector(sel);
                    if (el) {
                        const counterElapsed = t - (st + d);
                        const progress = Math.min(counterElapsed / 1.2, 1);
                        const val = progress >= 1 ? target : Math.floor(target * progress);
                        el.textContent = val.toLocaleString();
                    }
                }
            }
        }
    }

    document.getElementById('pbar').style.width = (t / TOTAL * 100) + '%';
};
"""

print("=" * 70)
print("取消中考 视频合成")
print("=" * 70)
print(f"时长: {DURATION}s | 帧率: {FPS}fps | 总帧数: {TOTAL_FRAMES}")
print("=" * 70)

# 清理帧目录
if OUTPUT_DIR.exists():
    shutil.rmtree(OUTPUT_DIR)
OUTPUT_DIR.mkdir(parents=True)

print("\n[1/3] 逐帧渲染...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 406, "height": 720})

    page.goto(f"file://{HTML_PATH.absolute()}")
    page.wait_for_load_state("networkidle")

    # 禁用CSS transition
    page.evaluate("""
        const style = document.createElement('style');
        style.textContent = '*, *::before, *::after { transition: none !important; animation: none !important; }';
        document.head.appendChild(style);
    """)

    page.evaluate(RENDER_JS)

    for frame_num in range(TOTAL_FRAMES):
        target_time = frame_num / FPS
        page.evaluate(f"renderAtTime({target_time})")

        screenshot_path = OUTPUT_DIR / f"frame_{frame_num:04d}.png"
        page.locator(".screen").screenshot(path=str(screenshot_path))

        if (frame_num + 1) % 200 == 0 or frame_num == TOTAL_FRAMES - 1:
            progress = (frame_num + 1) / TOTAL_FRAMES * 100
            print(f"  {progress:5.1f}% ({frame_num + 1}/{TOTAL_FRAMES}) t={target_time:.2f}s")

    browser.close()

print("  完成")

# [2/3] ffmpeg合成视频
print("\n[2/3] 合成视频...")
subprocess.run([
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", str(OUTPUT_DIR / "frame_%04d.png"),
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

# 文件信息
size_mb = VIDEO_FINAL.stat().st_size / 1024 / 1024
probe = subprocess.run([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", str(VIDEO_FINAL)
], capture_output=True, text=True)
dur = float(probe.stdout.strip())

print(f"\n{'=' * 70}")
print(f"完成: {VIDEO_FINAL.name}")
print(f"大小: {size_mb:.2f}MB | 时长: {dur:.2f}s | 分辨率: 406x720")
print(f"{'=' * 70}")
