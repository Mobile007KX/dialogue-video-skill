# Video Request - 白猫说话

```yaml
mode: image_to_video
model: MiniMax-Hailuo-2.3-Fast
duration: 6
resolution: 1080P
prompt: |
  Same scene, same lighting, same camera angle, static camera, absolutely no camera movement.
  White cat is TALKING - mouth movements, gestures, expressive pleading face, holding sign.
  Orange cat is LISTENING SILENTLY - mouth firmly CLOSED, just nodding occasionally, holding sign.
  Both characters stay in frame throughout, street begging scene at night.
  Loop-friendly: end pose must be similar to start pose for seamless looping.
  3D Pixar animation style, night street scene, emotional atmosphere.
first_frame_image: /Users/yunboxiong/projects/对话短剧工具/项目/橘猫和白猫/剧集/第四集_命运反转/起始帧.png
last_frame_image: ""
subject_reference:
  type: character
  images:
    - ""
out: /Users/yunboxiong/projects/对话短剧工具/项目/橘猫和白猫/剧集/第四集_命运反转/白猫说话.mp4
poll_interval_ms: 10000
max_polls: 90
```
