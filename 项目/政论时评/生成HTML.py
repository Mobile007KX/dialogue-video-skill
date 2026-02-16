#!/usr/bin/env python3
"""政论时评：HTML自动生成器
从 剧本.json + 时间戳 自动生成带动画的字幕HTML页面

用法：python 生成HTML.py 取消中考/剧本.json 取消中考/AIDOCS/timestamps.json
"""
import json
import sys
from pathlib import Path

# gallery 图片池（按序号轮转分配给场景）
GALLERY_IMAGES = [
    "gallery_color_03.jpg", "gallery_color_07.jpg", "gallery_color_12.jpg",
    "gallery_color_01.jpg", "gallery_color_15.jpg", "gallery_color_09.jpg",
    "gallery_color_05.jpg", "gallery_color_18.jpg", "gallery_color_10.jpg",
    "gallery_color_14.jpg", "gallery_color_20.jpg", "gallery_color_16.jpg",
    "gallery_color_02.jpg", "gallery_color_08.jpg", "gallery_color_11.jpg",
]


def build_line_html(line, is_first=True):
    """将一行定义转换为HTML"""
    text = line["text"]
    style = line.get("style", "white")
    anim = line.get("anim", "fade")
    mt = "" if is_first else " mt1"

    if style == "block-yellow":
        return '    <div class="t1 %s%s"><span class="block-yellow">%s</span></div>' % (anim, mt, text)

    css_map = {
        "white-stroke": "t2 c-white stroke",
        "white": "t2 c-white stroke",
        "white-big": "t1 c-white stroke",
        "white-dim": "t3 c-white stroke",
        "yellow": "t2 c-yellow stroke",
        "yellow-big": "t1 c-yellow stroke",
        "red": "t2 c-red stroke",
    }
    css = css_map.get(style, "t2 c-white stroke")
    dim_attr = ' style="opacity:.6"' if style == "white-dim" else ""
    return '    <div class="%s %s%s"%s>%s</div>' % (css, anim, mt, dim_attr, text)


def build_scene_html(scene):
    """将场景定义转换为HTML"""
    sid = scene["id"]
    lines_html = []

    for i, line in enumerate(scene["lines"]):
        lines_html.append(build_line_html(line, is_first=(i == 0)))

    if "counter" in scene:
        c = scene["counter"]
        color = c.get("color", "red")
        lines_html.append('    <div class="big-num c-%s pop" id="%s">0</div>' % (color, c["id"]))
        if c.get("suffix"):
            label = c.get("label", "")
            lines_html.append('    <div class="t2 c-white stroke fade mt1">%s%s</div>' % (label, c["suffix"]))

    inner = "\n".join(lines_html)
    return '  <div class="scene" id="%s">\n%s\n  </div>' % (sid, inner)


def build_timeline_js(scenes, timestamps):
    """生成 JavaScript timeline 数组"""
    lines = ["const timeline = ["]

    for i, scene in enumerate(scenes):
        sid = scene["id"]
        ts = timestamps[i]
        start = ts["start"]
        dur = ts["duration"]

        anims = []
        delay = 0.0
        for j, line in enumerate(scene["lines"]):
            anim_type = line.get("anim", "fade")
            sel = "#%s .%s:nth-child(%d)" % (sid, anim_type, j + 1)
            anims.append("    [%.1f, '%s', '%s']" % (delay, sel, anim_type))
            delay += 0.4

        if "counter" in scene:
            c = scene["counter"]
            child_idx = len(scene["lines"]) + 1
            anims.append("    [%.1f, '#%s .pop:nth-child(%d)', 'pop']" % (delay, sid, child_idx))
            anims.append("    [%.1f, '#%s', 'counter:%s']" % (delay + 0.2, c["id"], c["target"]))

        anims_str = ",\n".join(anims)
        lines.append("  ['%s', %5.2f, %5.2f, [\n%s\n  ]]," % (sid, start, dur, anims_str))

    lines.append("];")
    return "\n".join(lines)


def generate_html(script_data, timestamps, gallery_dir):
    """生成完整的HTML文件"""
    scenes = script_data["scenes"]
    total_duration = timestamps[-1]["start"] + timestamps[-1]["duration"]
    title = script_data["title"]

    # 背景图 divs
    bg_divs = []
    for i in range(len(scenes)):
        img = GALLERY_IMAGES[i % len(GALLERY_IMAGES)]
        bg_divs.append(
            '    <div class="bg-img" data-bg="%d" style="background-image:url(\'%s/%s\')"></div>'
            % (i + 1, gallery_dir, img)
        )

    # 场景 divs
    scene_divs = [build_scene_html(s) for s in scenes]

    # bgMap JS object
    bg_map_entries = ["%s:%d" % (s["id"], i + 1) for i, s in enumerate(scenes)]
    bg_map_js = "{" + ",".join(bg_map_entries) + "}"

    # timeline JS
    timeline_js = build_timeline_js(scenes, timestamps)

    # counter reset JS
    counter_ids = [s["counter"]["id"] for s in scenes if "counter" in s]
    counter_reset_lines = []
    for cid in counter_ids:
        counter_reset_lines.append(
            "  {const e=document.getElementById('%s');if(e)e.textContent='0';}" % cid
        )
    counter_reset_js = "\n".join(counter_reset_lines)

    # 用 CSS + HTML 部分（无 JS 花括号冲突）拼接
    parts = []

    # HTML head + CSS
    parts.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s — 政论时评</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;display:flex;justify-content:center;align-items:center;min-height:100vh;font-family:"PingFang SC","Noto Sans SC",sans-serif}
.screen{position:relative;width:405px;height:720px;overflow:hidden;background:#111}
.bg-layer{position:absolute;inset:0;z-index:0;overflow:hidden}
.bg-img{position:absolute;inset:0;background-size:cover;background-position:center;filter:brightness(0.45) saturate(1.1);opacity:0;transition:opacity 1s ease}
.bg-img.on{opacity:1}
.scene{position:absolute;inset:0;z-index:1;display:flex;flex-direction:column;align-items:center;text-align:center;justify-content:flex-start;padding:60px 20px 80px;opacity:0;pointer-events:none;transition:opacity .4s ease}
.scene.on{opacity:1;pointer-events:auto}
.t1{font-size:42px;font-weight:900;line-height:1.2}
.t2{font-size:32px;font-weight:800;line-height:1.3}
.t3{font-size:26px;font-weight:700;line-height:1.3}
.big-num{font-size:72px;font-weight:900;line-height:1.1;margin:12px 0}
.c-white{color:#fff}.c-yellow{color:#FFD600}.c-red{color:#FF3B30}
.stroke{text-shadow:0 2px 8px rgba(0,0,0,.7),0 0 2px rgba(0,0,0,.9)}
.block-yellow{display:inline-block;background:#FFD600;color:#111;padding:4px 18px;border-radius:4px;font-weight:900}
.mt1{margin-top:12px}.mt2{margin-top:24px}
.fade{opacity:0;transform:translateY(16px);transition:all .5s cubic-bezier(.23,1,.32,1)}
.fade.show{opacity:1;transform:translateY(0)}
.pop{opacity:0;transform:scale(.7);transition:all .4s cubic-bezier(.34,1.56,.64,1)}
.pop.show{opacity:1;transform:scale(1)}
.bar{position:absolute;bottom:0;left:0;right:0;z-index:10;background:linear-gradient(transparent,rgba(0,0,0,.6));padding:8px 12px 10px;display:flex;align-items:center;gap:8px;color:#fff;font-size:12px}
.pbar-bg{flex:1;height:3px;background:rgba(255,255,255,.2);border-radius:1px;cursor:pointer}
.pbar{height:100%%;background:#FFD600;width:0%%;border-radius:1px;transition:width .3s linear}
</style>
</head>
<body>
<div class="screen">
  <div class="bg-layer">
%s
  </div>
%s
  <div class="bar">
    <span id="playBtn" onclick="togglePlay()" style="cursor:pointer">&#9654; 播放</span>
    <span id="restartBtn" onclick="restart()" style="cursor:pointer">&#8634; 重播</span>
    <div class="pbar-bg" onclick="seekTo(event)"><div class="pbar" id="pbar"></div></div>
    <span><span id="elapsed">0:00</span> / <span id="total">0:00</span></span>
  </div>
</div>""" % (title, "\n".join(bg_divs), "\n".join(scene_divs)))

    # JS 部分用字面量字符串（不用 f-string / % 格式化）
    js_code = "\n".join([
        "<script>",
        timeline_js,
        "",
        "const TOTAL=%.2f;" % total_duration,
        "let playing=false,startT=0,elapsed=0,raf=null;",
        "const fired=new Set();",
        "const bgMap=%s;" % bg_map_js,
        "let curBg=0;",
        "",
        "document.getElementById('total').textContent=fmt(TOTAL);",
        "function fmt(s){return Math.floor(s/60)+':'+String(Math.floor(s%60)).padStart(2,'0')}",
        "",
        "function switchBg(n){",
        "  if(n===curBg)return;curBg=n;",
        "  document.querySelectorAll('.bg-img').forEach(i=>i.classList.toggle('on',+i.dataset.bg===n));",
        "}",
        "",
        "function resetAll(){",
        "  document.querySelectorAll('.scene').forEach(s=>s.classList.remove('on'));",
        "  document.querySelectorAll('.show').forEach(e=>e.classList.remove('show'));",
        counter_reset_js,
        "  document.querySelectorAll('.bg-img').forEach(i=>i.classList.remove('on'));",
        "  curBg=0;fired.clear();",
        "}",
        "",
        "function fire(sel,act){",
        "  if(act==='fade'||act==='pop'){",
        "    document.querySelectorAll(sel).forEach(e=>e.classList.add('show'));",
        "  }else if(act.startsWith('counter:')){",
        "    const target=+act.split(':')[1],el=document.querySelector(sel);",
        "    let cur=0,step=0;const steps=40,inc=target/steps;",
        "    const t=setInterval(()=>{",
        "      step++;cur+=inc;",
        "      if(step>=steps){el.textContent=target.toLocaleString();clearInterval(t)}",
        "      else el.textContent=Math.floor(cur).toLocaleString();",
        "    },1200/steps);",
        "  }",
        "}",
        "",
        "function tick(){",
        "  if(!playing)return;",
        "  elapsed=(performance.now()-startT)/1000;",
        "  if(elapsed>=TOTAL){playing=false;document.getElementById('playBtn').textContent='\\u25b6 \\u64ad\\u653e';return}",
        "  document.getElementById('pbar').style.width=(elapsed/TOTAL*100)+'%';",
        "  document.getElementById('elapsed').textContent=fmt(elapsed);",
        "  for(const[sid,st,dur,anims]of timeline){",
        "    const el=document.getElementById(sid);",
        "    if(elapsed>=st&&elapsed<st+dur){",
        "      if(!el.classList.contains('on')){",
        "        document.querySelectorAll('.scene.on').forEach(s=>s.classList.remove('on'));",
        "        el.classList.add('on');switchBg(bgMap[sid]||1);",
        "      }",
        "      for(const[d,s,a]of anims){",
        "        const k=sid+s+a;",
        "        if(!fired.has(k)&&elapsed>=st+d){fired.add(k);fire(s,a)}",
        "      }",
        "    }",
        "  }",
        "  raf=requestAnimationFrame(tick);",
        "}",
        "",
        "function togglePlay(){",
        "  if(playing){playing=false;cancelAnimationFrame(raf);document.getElementById('playBtn').textContent='\\u25b6 \\u64ad\\u653e'}",
        "  else{",
        "    if(elapsed>=TOTAL)restart();",
        "    playing=true;startT=performance.now()-elapsed*1000;",
        "    document.getElementById('playBtn').textContent='\\u23f8 \\u6682\\u505c';",
        "    raf=requestAnimationFrame(tick);",
        "  }",
        "}",
        "",
        "function restart(){",
        "  playing=false;cancelAnimationFrame(raf);elapsed=0;resetAll();",
        "  document.getElementById('pbar').style.width='0%';",
        "  document.getElementById('elapsed').textContent='0:00';",
        "  document.getElementById('playBtn').textContent='\\u25b6 \\u64ad\\u653e';",
        "  setTimeout(togglePlay,200);",
        "}",
        "",
        "function seekTo(e){",
        "  const r=e.currentTarget.getBoundingClientRect();",
        "  elapsed=(e.clientX-r.left)/r.width*TOTAL;",
        "  startT=performance.now()-elapsed*1000;resetAll();",
        "  for(const[sid,st,dur,anims]of timeline){",
        "    if(elapsed>=st&&elapsed<st+dur){",
        "      document.getElementById(sid).classList.add('on');switchBg(bgMap[sid]||1);",
        "      for(const[d,s,a]of anims){if(elapsed>=st+d){fired.add(sid+s+a);fire(s,a)}}",
        "    }",
        "  }",
        "}",
        "",
        "document.addEventListener('keydown',e=>{if(e.code==='Space'){e.preventDefault();togglePlay()}});",
        "</script>",
        "</body>",
        "</html>",
    ])

    parts.append(js_code)
    return "\n".join(parts)


def main():
    if len(sys.argv) < 3:
        print("用法: python 生成HTML.py <剧本.json> <timestamps.json> [输出.html]")
        sys.exit(1)

    script_path = Path(sys.argv[1])
    ts_path = Path(sys.argv[2])

    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)
    with open(ts_path, "r", encoding="utf-8") as f:
        timestamps = json.load(f)

    gallery_dir = "../gallery"
    output_path = Path(sys.argv[3]) if len(sys.argv) > 3 else script_path.parent / "字幕.html"

    html = generate_html(script_data, timestamps, gallery_dir)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("HTML生成完成: %s" % output_path)
    print("  场景数: %d" % len(script_data["scenes"]))
    print("  总时长: %.2fs" % (timestamps[-1]["start"] + timestamps[-1]["duration"]))


if __name__ == "__main__":
    main()
