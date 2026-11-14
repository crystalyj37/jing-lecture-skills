#!/usr/bin/env node
/**
 * 构建期公式渲染：读 stdin 的 JSON 数组，吐 JSON 数组（渲染结果）。
 *
 * 输入：[{"tex": "\\frac{a}{b}", "display": true}, ...]
 * 输出：[{"ok": true, "html": "..."} | {"ok": false, "err": "..."}]
 *
 * display=true  → 独立成行的公式（::: fml 的每一行）
 * display=false → 行内公式（说明文字里的 \(...\)）
 *
 * 为什么在构建期做，而不是页面运行时：
 *   1. 产物不必带 katex.min.js（省 266 KB）
 *   2. 同步完成，放映时不可能出现「先看见 \frac 源码再跳成公式」
 *   3. 写错公式在构建阶段就报错，而不是讲课时白屏
 */

const path = require("path");

const KATEX = path.join(__dirname, "..", "assets", "vendor", "katex.min.js");

// KaTeX 在 trust:false 下会「渲染成红字但不报错」的命令
const TRUST_CMD = /\\(?:href|url|htmlClass|htmlId|htmlStyle|htmlData|includegraphics)\b/;
let katex;
try {
  katex = require(KATEX);
} catch (e) {
  console.error("[math] 载入 KaTeX 失败：" + KATEX);
  process.exit(3);
}

let buf = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (d) => (buf += d));
process.stdin.on("end", () => {
  let items;
  try {
    items = JSON.parse(buf);
  } catch (e) {
    console.error("[math] 输入不是合法 JSON");
    process.exit(2);
  }
  const out = items.map((item) => {
    try {
      // trust:false 下，\href / \url / \htmlClass 这类命令不会抛错，而是把命令名
      // 用 KaTeX 的错误色印在页面上——构建和审计都看不出来，放映时却露出一行红字。
      // 这里按「命令名」拦，不要按输出里的颜色值拦：#cc0000 确实是 KaTeX 的错误色，
      // 但 \textcolor{#cc0000}{x} 是合法写法，按颜色扫会把正常公式误判成违规。
      if (TRUST_CMD.test(item.tex)) {
        return {
          ok: false,
          err: "含需要 trust 的命令（\\href、\\url、\\htmlClass、\\includegraphics 之类），幻灯片里不支持",
        };
      }
      const html = katex.renderToString(item.tex, {
        displayMode: !!item.display,
        throwOnError: true,
        strict: "ignore",
        trust: false,
      });
      return { ok: true, html };
    } catch (e) {
      return { ok: false, err: String(e.message || e).split("\n")[0] };
    }
  });
  process.stdout.write(JSON.stringify(out));
});
