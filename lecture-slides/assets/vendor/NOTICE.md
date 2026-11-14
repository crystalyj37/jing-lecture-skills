# 第三方资源：KaTeX 0.19.0

`katex.min.js` 与 `katex.css` 来自 [KaTeX](https://katex.org/)，用于**构建期**把 `::: fml` 块里的
LaTeX 排成静态 HTML。产物里不含 `katex.min.js`；只有样式表与按需裁剪的字体（base64）会内嵌进
单个 .html。

- 版本：0.19.0
- 许可：MIT，Copyright (c) 2013–2020 Khan Academy and other contributors
- 上游：https://github.com/KaTeX/KaTeX
- 上游许可全文：见同目录 [LICENSE](LICENSE)

## 这两个文件的实际来源（别按“npm dist 原件”理解）

| 文件 | 来源 | sha256 |
|---|---|---|
| `katex.min.js` | npm `katex@0.19.0` 的 `dist/katex.min.js`，原样 | `103a53763cc033bba8d175bf3f0ba597c3505c9b6747dd3f2c7bc2a6bfcc8ae7` |
| `katex.css` | **不是** `dist/katex.min.css` 原件（那个约 24 KB）。这份 360 KB，是把 20 个字体以 base64 内嵌进 `@font-face` 的版本，取自实际演示页里内联的 KaTeX 样式，以便单文件离线可用 | `63cf9c823f909998e404800809df1e9aeebd03fc1dceb030e76fdf46fa41ad4f` |

`build.py` 的 `katex_css()` 会在构建时按源稿实际用到的字形族删掉多余的 `@font-face`：
默认保留 14 个（Main / Math / Size1–4 / AMS / Caligraphic / Script 等），
用到 `\mathfrak`、`\mathtt`、`\texttt`、`\mathsf`、`\textsf` 时自动补回对应字族。

改这两个文件等于换公式引擎版本：动完必须重跑 `assets/example.deck.md` 与 `showcase.deck.md`
的构建，并逐条看一眼公式屏。
