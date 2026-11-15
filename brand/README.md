# brand/ —— 这个仓库的署名信息

这里放的是**门面上的名字**：头像、微标、品牌名、标语、链接、版权行。

改这一处，页面和 README 一起变。**不要手改 `docs/index.html` 和 `README.md` 里的品牌段落**——那些段落被标记包着，跑一次脚本就会被重写。

```
brand/
├─ brand.json      文字、链接、版权（唯一事实源）
├─ assets/
│  ├─ avatar.png   头像原稿
│  └─ mark.png     微标原稿
└─ README.md       这份说明
scripts/apply_brand.py   注入脚本（只用标准库）
```

## 换成自己的 IP：三步

```bash
# 1. 改文字
$EDITOR brand/brand.json

# 2. 换两张图（同名覆盖即可）
cp 我的头像.png brand/assets/avatar.png
cp 我的微标.png brand/assets/mark.png

# 3. 注入
python3 scripts/apply_brand.py
```

跑完 `git diff` 只该出现脚本列出的那几处。核对一遍，没有别的地方被改动。

## 字段表

| 字段 | 必填 | 落到哪里 |
|---|---|---|
| `name` | 是 | 顶栏品牌名、README 副标题、页面 `<meta author>`、description 前缀 |
| `tagline` | 是 | 顶栏副行、README 副标题的第二段 |
| `owner` | 是 | 推导仓库地址与 Pages 地址（`github.com/<owner>/<repo>`、`<owner>.github.io/<repo>/`） |
| `repo` | 是 | 页面 `<title>`、clone 命令、README 一级标题 |
| `year` | 否 | LICENSE 版权年份，缺省取当年 |
| `copyright` | 否 | LICENSE 版权人，缺省同 `owner`（填单位也可以） |
| `description` | 否 | 页面 `<meta description>`，出现在搜索结果里 |
| `footer_note` | 否 | 页脚那句免责/版权说明 |
| `github` / `site` | 否 | 用自定义域名或仓库不在 GitHub 时覆盖推导值，注意 `site` 末尾带 `/` |
| `assets.avatar` / `assets.mark` | 否 | 图片路径，缺省 `brand/assets/avatar.png`、`brand/assets/mark.png` |

## 脚本会改写的地方（六个标记 + 一行 + 两张图）

| 文件 | 位置 | 内容 |
|---|---|---|
| `docs/index.html` | `<!--brand:head-->` | title、favicon、description、author、分享卡片（og / twitter） |
| `docs/index.html` | `<!--brand:topbar-->` | 头像、品牌名、标语、GitHub 链接 |
| `docs/index.html` | `<!--brand:clone-html-->` | 安装命令 |
| `docs/index.html` | `<!--brand:footer-->` | 微标、免责尾注、三份文档链接 |
| `README.md` | `<!--brand:sub-->` | 标题下的副标题 |
| `README.md` | `<!--brand:demo-->` | 四个在线示例链接 |
| `README.md` | `<!--brand:clone-md-->` | 安装命令 |
| `LICENSE` | 无标记 | `Copyright (c) 年份 版权人` 整行 |
| `docs/img/` | — | 从 `brand/assets/` 复制，文件名取原文件 basename |

标记必须各出现一次。缺了或重了，脚本直接报错退出——不会给你一个「看着正常、其实没换全」的页面。

## 图片规格

- **头像**：正方形、透明底、≥256px、**不加描边、投影、文字**。页面上显示 46px，256 够三倍屏。头像本身是成品，页面不再加工它。
- **微标**：透明底、≥128px。页面上 24px，同时作 favicon。
- 换文件名可以，但要同步改 `brand.json` 的 `assets` 路径，脚本按 basename 复制到 `docs/img/`。

## 校验

```bash
python3 scripts/apply_brand.py --check
```

六处落点、两张图、LICENSE 全一致 → 打印 `✓`，退出码 0；任何一处漂了 → 列出文件，退出码 1。适合挂成 pre-commit。

最容易漂的两种情况：手改了 `index.html` 忘了改 json；换了图没跑脚本。

## 两个边界

**品牌不进 skill。** `lecture-slides` / `lecture-pack` 是工具，产物里不该出现署名。所以 `brand/` 只服务这个仓库的门面（`docs/index.html`、`README.md`），同事把 skill 目录拷走用，不会带上你的名字和头像。

**仓库之外还有三处，脚本改不到**：GitHub 仓库 About 里的简介、仓库头像（跟随账号，不在仓库里）、Pages 的自定义域名。换 IP 时手工改。

## 放什么、不放什么

这个目录是公开的。放：名字/机构名、标语、头像、微标、仓库链接、版权人。

不放：手机号、私人邮箱、学生信息、课程名、内部项目名——这些一旦进 git 历史就很难真正删干净。头像如果是本人照片，等同于公开这张照片，自己确认过再放。
