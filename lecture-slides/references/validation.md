# 验收

两道关：先跑 `audit.py`（秒级、离线），再跑浏览器量测（要真打开一次）。
静检过不了的不要往下走。

## 一、静态

```bash
python3 scripts/audit.py 课程.html
```

退出码 0 才继续。它只能发现「结构上确定错了」的事，发现不了「字压到边了」「第三列折行了」。

## 二、浏览器量测

用 ego-browser，视口锁 1920×1080。**不要用截图判断**——截图在这个环境里会超时，
而且肉眼看不出 3px 的越界。量 DOM。

```bash
export PATH="$HOME/.local/bin:$PATH"
ego-browser nodejs <<'EOF'
const task = await taskSpace("deck 验收");
const page = task.page("p1");
await page.goto("file:///绝对路径/课程.html");
await page.cdp("Emulation.setDeviceMetricsOverride",
  {width:1920,height:1080,deviceScaleFactor:1,mobile:false});
await page.waitForTimeout(300);

const rep = await page.evaluate(() => {
  const safeBottom = 1080 - 40;      // 底部工具条 40px
  const screens = [...document.querySelectorAll('.screen')];
  const keep = screens.map(s => s.classList.contains('active'));
  const out = [];

  screens.forEach((s, i) => {
    screens.forEach(x => x.classList.remove('active'));
    s.classList.add('active');
    s.querySelectorAll('[data-step]').forEach(e => e.classList.add('on'));
    void s.offsetHeight;

    const over = [], small = [], clipped = [];
    s.querySelectorAll('*').forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') return;
      const r = el.getBoundingClientRect();
      if (!r.width && !r.height) return;

      if (r.right > 1921 || r.bottom > safeBottom + 1 || r.left < -1 || r.top < -1) {
        over.push([el.tagName, String(el.className).slice(0, 34),
                   [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]]);
      }
      // 有直接文字、字号小于 16px
      const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
      if (own && parseFloat(cs.fontSize) < 16) {
        small.push([el.tagName, String(el.className).slice(0, 24), cs.fontSize,
                    el.textContent.trim().slice(0, 18)]);
      }
      // 内容被容器裁掉
      if (cs.overflow !== 'visible' && el.scrollHeight > el.clientHeight + 2 && el.clientHeight > 0) {
        clipped.push([el.tagName, String(el.className).slice(0, 30),
                      el.scrollHeight - el.clientHeight]);
      }
    });

    out.push({
      id: s.id, title: s.dataset.title,
      steps: +s.dataset.steps || 0,
      marks: s.querySelectorAll('[data-step]').length,
      note: !!s.querySelector('.spk'),
      over: over.slice(0, 6), small: small.slice(0, 6), clipped: clipped.slice(0, 4)
    });
  });

  screens.forEach((s, i) => s.classList.toggle('active', keep[i]));
  return out;
});

const bad = rep.filter(r => r.over.length || r.clipped.length);
const tiny = rep.filter(r => r.small.length);
console.log("屏数", rep.length, "｜越界/裁切屏", bad.length, "｜小字屏", tiny.length);
rep.forEach(r => {
  const flag = (r.over.length || r.clipped.length) ? "✗" : "✓";
  console.log(flag, r.id, "steps=" + r.steps, "marks=" + r.marks, r.note ? "有备注" : "无备注", r.title);
  r.over.forEach(o => console.log("   越界", o.join(" ")));
  r.clipped.forEach(o => console.log("   裁切", o.join(" ")));
  r.small.forEach(o => console.log("   小字", o.join(" ")));
});
EOF
```

判读：

| 结果 | 处理 |
|---|---|
| `越界` 且 `right ≈ 1921` | 该元素宽度把右边距吃掉了，改 `max-width` 或缩列 |
| `越界` 且 `bottom > 1040` | 内容太多，删一层或缩小字号档位 |
| `裁切` 且差值 < 20px | 多半是行高取整，可忽略 |
| `裁切` 且差值 > 40px | 真的有内容看不见了，必须改 |
| `小字` 是 `.ghost`、`.qnote` | 正常，装饰与脚注可以有 14–15px |
| `小字` 是正文 `p`/`li`/`td` | 投影上看不清，提到 18px 以上 |

## 三、手感（必须人看一遍）

量测查不出的是「讲起来顺不顺」，交付前自己走一遍：

1. 按 `空格` 从头到尾，**记下每一屏按了几次**，跟源稿 `steps` 对得上
2. 每屏停 3 秒，问一句「这屏想让人记住什么」——答不出来就是内容问题，不是版式问题
3. 按 `S`，看备注是否够讲 1 分钟；只有一句「强调一下这里」等于没写
4. 按 `R` 进阅读模式，从头滚一遍，看 `.deep` 细读是否自洽
5. `F` 全屏，退到 3 米外看一次：最小的那行字还认得出吗

## 四、交付前后

- 文件名用 `<主题>_<场景>.html`，不要留 `test`、`v2`、`最终` 这类词在正式文件上
- 单文件体积：纯文字 60–300 KB 正常；超过 4 MB 多半是图片/视频内嵌，考虑外链
- 交付前把 html 复制一份到别的目录再交给预览——
  预览会改写被预览的文件（剥离 KaTeX 结构、改动字节），源文件要留干净的
