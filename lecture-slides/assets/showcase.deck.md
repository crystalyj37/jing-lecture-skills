---
title: 示例 · 30 个样本凭什么够
---

::: screen id=c1 steps=0 title="示例 · 30 个样本凭什么够"
<header class="hd">
  <div class="kicker">示例 · 统计直觉</div>
  <h2>30 个样本，凭什么敢下结论</h2>
  <p class="lead">不是经验法则，是一条能算出来的定理。<span class="hl">看懂这一条，你就知道「差多少」该怎么估。</span></p>
</header>

<div class="big">\(1/\sqrt{n}\)<small>误差随样本量收缩的速度</small></div>
<p class="bignote">样本量翻四倍，误差才减半。这比「30 就够」有用得多——它同时告诉你 30 什么时候不够、什么时候绰绰有余。</p>
::: note
开场不要报公式。先让他们猜：10 个样本和 1000 个样本，结论的误差差几倍？多数人会猜 100 倍，实际是 10 倍。
这个落差就是整节的钩子。
:::
:::

::: screen id=c2 steps=4 title="一 · 一眼看见"
<header class="hd">
  <div class="kicker">一 · 一眼看见</div>
  <h2>同样是均值，为什么 n 越大越稳</h2>
  <p class="lead">四条横杠是同一件事的四种精度：<span class="hl">95% 的样本均值会落进去的范围</span>。</p>
</header>

<div class="fig">
  <svg viewBox="180 20 980 440" role="img" aria-label="n 为 10、30、100、1000 时，样本均值的 95% 落点范围逐级收窄">
    <line x1="700" y1="66" x2="700" y2="440" style="stroke:var(--line);stroke-width:2;stroke-dasharray:8 10"/>
    <text x="700" y="46" text-anchor="middle" style="fill:var(--muted);font-size:24px;letter-spacing:.12em">μ 真值</text>

    <g data-step="1">
    <rect x="420" y="96" width="560" height="52" rx="4" style="fill:var(--accent);opacity:.16"/>
    <rect x="420" y="96" width="560" height="52" rx="4" style="fill:none;stroke:var(--accent);stroke-width:2"/>
    <text x="372" y="132" text-anchor="end" style="fill:var(--ink);font-size:30px;font-weight:600">n = 10</text>
    <text x="1004" y="132" style="fill:var(--muted);font-size:24px;font-variant-numeric:tabular-nums">± 0.62</text>
    </g>

    <g data-step="2">
    <rect x="538" y="190" width="324" height="52" rx="4" style="fill:var(--accent);opacity:.16"/>
    <rect x="538" y="190" width="324" height="52" rx="4" style="fill:none;stroke:var(--accent);stroke-width:2"/>
    <text x="372" y="226" text-anchor="end" style="fill:var(--ink);font-size:30px;font-weight:600">n = 30</text>
    <text x="1004" y="226" style="fill:var(--muted);font-size:24px;font-variant-numeric:tabular-nums">± 0.36</text>
    </g>

    <g data-step="3">
    <rect x="612" y="284" width="176" height="52" rx="4" style="fill:var(--accent);opacity:.16"/>
    <rect x="612" y="284" width="176" height="52" rx="4" style="fill:none;stroke:var(--accent);stroke-width:2"/>
    <text x="372" y="320" text-anchor="end" style="fill:var(--ink);font-size:30px;font-weight:600">n = 100</text>
    <text x="1004" y="320" style="fill:var(--muted);font-size:24px;font-variant-numeric:tabular-nums">± 0.20</text>
    </g>

    <g data-step="4">
    <rect x="672" y="378" width="56" height="52" rx="4" style="fill:var(--accent);opacity:.16"/>
    <rect x="672" y="378" width="56" height="52" rx="4" style="fill:none;stroke:var(--accent);stroke-width:2"/>
    <text x="372" y="414" text-anchor="end" style="fill:var(--ink);font-size:30px;font-weight:600">n = 1000</text>
    <text x="1004" y="414" style="fill:var(--muted);font-size:24px;font-variant-numeric:tabular-nums">± 0.06</text>
    </g>
  </svg>
  <p class="figcap">同一总体、同一估计量，只改每次抽多少个。杠的长度按 \(1/\sqrt{n}\) 缩。</p>
</div>
::: note
先只讲第一条杠，问他们「如果你只抽 10 个，你的结论有可能偏到哪里」。再往下走一步。
第三、四条一起出：让他们看到「从 100 加到 1000」，杠缩得几乎看不见——这就是边际收益递减。
:::
:::

::: screen id=c3 steps=0 title="二 · 把它算出来"
<header class="hd">
  <div class="kicker">二 · 把它算出来</div>
  <h2>从「样本均值」到「它有多不稳」</h2>
  <p class="lead">三步，只用得到开方。<span class="hl">第三步是全部结论的来源。</span></p>
</header>

::: fml
\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i | (1)　样本均值
\mathrm{SE}(\bar{x})=\frac{\sigma}{\sqrt{n}} | (2)　标准误：σ 你改不了，n 是唯一的旋钮
Z=\frac{\bar{x}-\mu}{\sigma/\sqrt{n}}\ \longrightarrow\ N(0,1) | (3)　中心极限定理：不管总体长什么样，都归到同一个标准正态
:::
::: note
(1) 不要念公式，念成「把 n 个数加起来除以 n」。
(2) 停一下：σ 是总体自己的波动，你改不了；n 是你唯一能控制的旋钮。
(3) 只强调一句：减掉均值、除以标准误，就归到同一个标准正态。这是「一张表能查所有题」的原因。
:::
:::

::: screen id=c4 steps=0 title="二 · 把它看见"
<header class="hd">
  <div class="kicker">二 · 把它看见</div>
  <h2>把 n 拖大，看它怎么变成钟形</h2>
  <p class="lead">这里的总体是右偏的指数分布，完全不像正态。<span class="hl">取了均值以后，它就正了。</span></p>
</header>

<div class="plot">
  <div class="cv"><canvas id="cltcv" width="2340" height="700" role="img" aria-label="随着每次抽样的样本量增大，样本均值的直方图从右偏逐渐变为近似正态"></canvas></div>
  <div class="ctrl">
    <label for="nrange">每次抽 n =</label>
    <input id="nrange" type="range" min="2" max="120" step="1" value="2">
    <span class="val" id="nval">2</span>
    <button id="reseed" type="button">重新抽 1600 次</button>
    <span class="hint">灰线＝按正态分布算出的曲线；两者越贴，说明正态近似越好。</span>
  </div>
</div>

<script>
(function(){
  var cv = document.getElementById('cltcv');
  if (!cv || !cv.getContext) return;
  var g = cv.getContext('2d');
  var W = cv.width, H = cv.height;
  var L = 110, R = 44, T = 96, B = 96;
  var PW = W - L - R, PH = H - T - B;
  var N = 1600, means = [], seed = 20261114;
  var FONT = '-apple-system,"PingFang SC","Hiragino Sans GB",sans-serif';

  function rnd(){ seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; }
  function expo(){ return -Math.log(1 - rnd()); }   // 均值 1 的指数分布

  function resample(n){
    means.length = 0;
    for (var k = 0; k < N; k++){
      var s = 0;
      for (var i = 0; i < n; i++) s += expo();
      means.push(s / n);
    }
  }

  function paint(n){
    g.clearRect(0, 0, W, H);
    var se = 1 / Math.sqrt(n);
    var lo = Math.max(-0.2, 1 - 4 * se), hi = 1 + 4 * se;
    var BINS = 36, cnt = new Array(BINS).fill(0), i, b;

    for (i = 0; i < means.length; i++){
      b = Math.floor((means[i] - lo) / (hi - lo) * BINS);
      if (b >= 0 && b < BINS) cnt[b]++;
    }
    var maxC = Math.max.apply(null, cnt) || 1, bw = PW / BINS;

    for (b = 0; b < BINS; b++){
      var h = cnt[b] / maxC * PH;
      g.fillStyle = 'rgba(156,47,30,.16)';
      g.fillRect(L + b * bw, T + PH - h, Math.max(bw - 3, 1), h);
      g.fillStyle = 'rgba(156,47,30,.6)';
      g.fillRect(L + b * bw, T + PH - h, Math.max(bw - 3, 1), 3);
    }

    g.beginPath();
    for (var x = 0; x <= PW; x += 2){
      var v = lo + (hi - lo) * x / PW;
      var d = Math.exp(-Math.pow(v - 1, 2) / (2 * se * se));
      var y = T + PH - d * PH * 0.92;
      if (x === 0) g.moveTo(L + x, y); else g.lineTo(L + x, y);
    }
    g.strokeStyle = 'rgba(60,52,40,.5)';
    g.lineWidth = 3;
    g.stroke();

    g.strokeStyle = 'rgba(23,21,15,.32)';
    g.lineWidth = 2;
    g.beginPath(); g.moveTo(L, T + PH); g.lineTo(L + PW, T + PH); g.stroke();

    g.font = '26px ' + FONT;
    g.textAlign = 'center';
    g.fillStyle = 'rgba(95,88,76,.92)';
    // 刻度取整数：1/2/5 × 10^k 起步，避免出现 0.55、1.29 这种读不出来的数
    var span = hi - lo, raw = span / 5;
    var mag = Math.pow(10, Math.floor(Math.log10(raw)));
    var norm = raw / mag;
    var step = (norm <= 1.5 ? 1 : norm <= 3 ? 2 : norm <= 7 ? 5 : 10) * mag;
    var dec = Math.max(0, -Math.floor(Math.log10(step) + 1e-9));
    for (var vv = Math.ceil(lo / step) * step; vv <= hi + 1e-9; vv += step){
      var xp = L + PW * (vv - lo) / span;
      g.fillRect(xp - 1, T + PH + 4, 2, 8);
      g.fillText(vv.toFixed(dec), xp, T + PH + 42);
    }

    g.textAlign = 'left';
    g.font = '600 40px ' + FONT;
    g.fillStyle = 'rgba(23,21,15,.92)';
    g.fillText('n = ' + n, L, 56);
    g.fillStyle = 'rgba(156,47,30,.95)';
    g.fillText('SE = ' + se.toFixed(3), L + 230, 56);
    g.font = '26px ' + FONT;
    g.fillStyle = 'rgba(95,88,76,.85)';
    g.fillText('横轴：每次抽样算出的均值　　纵轴：出现次数', L + 620, 56);
  }

  var el = document.getElementById('nrange');
  var val = document.getElementById('nval');

  function refresh(){
    val.textContent = el.value;
    resample(+el.value);
    paint(+el.value);
  }

  el.addEventListener('input', refresh);
  el.addEventListener('keydown', function(e){ e.stopPropagation(); });  // 方向键别翻页
  document.getElementById('reseed').addEventListener('click', function(){
    seed = (seed * 48271 + 11) >>> 0;
    resample(+el.value);
    paint(+el.value);
  });

  refresh();
})();
</script>
::: note
这一屏一定要现场拖。从 2 拖到 5，让他们看「右偏得像小山坡」；再拖到 30，形态开始对称；到 120，几乎是钟形。
关键一句：总体没有变，变的只是「每次取多少个」。所以正态不是总体的性质，是均值的性质。
如果有人问「为什么偏偏是正态」，答：因为大量独立的小扰动相加，极限就是它。
:::
:::

::: screen id=c9 steps=0 title="二 · 换一种画法"
<header class="hd tight">
  <div class="kicker">二 · 换一种画法</div>
  <h2>同一条曲线，换个纵轴就成了直线</h2>
  <p class="lead">左右两边的横轴是同一套刻度，都按倍数排。<span class="hl">变的只有纵轴。</span></p>
</header>

<div class="pair">
  <div class="fig">
    <svg viewBox="0 0 560 410" role="img" aria-label="纵轴线性时，均值的标准误随样本量增大而下降，前几个点掉得很快，后面几乎贴地">
      <g style="stroke:var(--line-soft);stroke-width:1.5;stroke-dasharray:6 8">
        <line x1="70" y1="85.7" x2="540" y2="85.7"/>
        <line x1="70" y1="177.1" x2="540" y2="177.1"/>
        <line x1="70" y1="268.6" x2="540" y2="268.6"/>
      </g>
      <g style="stroke:var(--line);stroke-width:2">
        <line x1="70" y1="40" x2="70" y2="360"/>
        <line x1="70" y1="360" x2="540" y2="360"/>
      </g>
      <polyline points="70,70.9 160.5,193.1 259.7,268.6 350.3,307.2 449.5,331.1 540,343.3"
        style="fill:none;stroke:var(--accent);stroke-width:4;stroke-linejoin:round;stroke-linecap:round"/>
      <g style="fill:var(--accent)">
        <circle cx="70" cy="70.9" r="5.5"/><circle cx="160.5" cy="193.1" r="5.5"/>
        <circle cx="259.7" cy="268.6" r="5.5"/><circle cx="350.3" cy="307.2" r="5.5"/>
        <circle cx="449.5" cy="331.1" r="5.5"/><circle cx="540" cy="343.3" r="5.5"/>
      </g>
      <g style="fill:var(--muted);font-size:17px;text-anchor:middle">
        <text x="70" y="390">10</text><text x="160.5" y="390">30</text>
        <text x="259.7" y="390">100</text><text x="350.3" y="390">300</text>
        <text x="449.5" y="390">1000</text><text x="540" y="390">3000</text>
      </g>
      <g style="fill:var(--muted);font-size:17px;text-anchor:end">
        <text x="58" y="366">0</text><text x="58" y="274">0.1</text>
        <text x="58" y="183">0.2</text><text x="58" y="91">0.3</text>
      </g>
      <text x="70" y="22" style="fill:var(--muted);font-size:16px;letter-spacing:.08em">纵轴 线性</text>
    </svg>
    <p class="figcap">前几个点掉得最快，后面几乎贴着地走——「再抽也就这样了」</p>
  </div>

  <div class="fig">
    <svg viewBox="0 0 560 410" role="img" aria-label="纵轴取对数后，同一组数据落在一条直线上，说明标准误按样本量的平方根倒数下降">
      <g style="stroke:var(--line-soft);stroke-width:1.5;stroke-dasharray:6 8">
        <line x1="70" y1="45.9" x2="540" y2="45.9"/>
        <line x1="70" y1="169.2" x2="540" y2="169.2"/>
        <line x1="70" y1="304.3" x2="540" y2="304.3"/>
      </g>
      <g style="stroke:var(--line);stroke-width:2">
        <line x1="70" y1="40" x2="70" y2="360"/>
        <line x1="70" y1="360" x2="540" y2="360"/>
      </g>
      <polyline points="70,40 160.5,101.6 259.7,169.2 350.3,230.8 449.5,298.4 540,360"
        style="fill:none;stroke:var(--accent);stroke-width:4;stroke-linejoin:round;stroke-linecap:round"/>
      <g style="fill:var(--accent)">
        <circle cx="70" cy="40" r="5.5"/><circle cx="160.5" cy="101.6" r="5.5"/>
        <circle cx="259.7" cy="169.2" r="5.5"/><circle cx="350.3" cy="230.8" r="5.5"/>
        <circle cx="449.5" cy="298.4" r="5.5"/><circle cx="540" cy="360" r="5.5"/>
      </g>
      <g style="fill:var(--muted);font-size:17px;text-anchor:middle">
        <text x="70" y="390">10</text><text x="160.5" y="390">30</text>
        <text x="259.7" y="390">100</text><text x="350.3" y="390">300</text>
        <text x="449.5" y="390">1000</text><text x="540" y="390">3000</text>
      </g>
      <g style="fill:var(--muted);font-size:17px;text-anchor:end">
        <text x="58" y="51">0.3</text><text x="58" y="175">0.1</text><text x="58" y="310">0.03</text>
      </g>
      <text x="70" y="22" style="fill:var(--muted);font-size:16px;letter-spacing:.08em">纵轴 对数</text>
      <text x="300" y="150" style="fill:var(--accent);font-size:19px">六个点连成一条直线</text>
      <text x="300" y="176" style="fill:var(--muted);font-size:16px">斜率就是 −1/2</text>
    </svg>
    <p class="figcap">纵轴也按倍数排之后，点在一条直线上——这正是 \(1/\sqrt{n}\) 的证据</p>
  </div>
</div>
:::

::: screen id=c5 steps=4 title="三 · 换算成倍数"
<header class="hd">
  <div class="kicker">三 · 换算成倍数</div>
  <h2>样本量涨 100 倍，误差只缩到 1/10</h2>
  <p class="lead">把公式代进去算一遍，这个反直觉就变成了常识。</p>
</header>

<div class="tbl t4">
  <div class="tr th"><span>每次抽 n</span><span>标准误 SE</span><span>95% 区间半宽</span><span>相对 n = 10</span></div>
  <div class="tr" data-step="1"><span>10</span><span>0.316</span><span>± 0.62</span><span>1.00×</span></div>
  <div class="tr" data-step="2"><span>30</span><span>0.183</span><span>± 0.36</span><span>0.58×</span></div>
  <div class="tr" data-step="3"><span>100</span><span>0.100</span><span>± 0.20</span><span>0.32×</span></div>
  <div class="tr" data-step="4"><span>1000</span><span>0.032</span><span>± 0.06</span><span>0.10×</span></div>
</div>

<p class="foot" data-step="4">所以「样本越多越好」是对的，但<b>收益是开方级的</b>——这一点决定了调研该花多少钱。</p>
::: note
每一行都让他们自己算一下 1/√n，比看结论有用。
最后一列是重点：从 10 到 30，样本量三倍，误差只降四成。这是预算谈判时最常被忽略的一句。
:::
:::

::: screen id=c6 steps=2 title="四 · 两种说法"
<header class="hd">
  <div class="kicker">四 · 两种说法</div>
  <h2>「30 就够」这句话，对在哪、错在哪</h2>
  <p class="lead">它是一条经验分界，不是一条定理。<span class="hl">把它当定理用，就会在偏态数据上翻车。</span></p>
</header>

<div class="two">
  <div class="col" data-step="1">
    <h3>常听到的说法</h3>
    <p>「样本超过 30，就近似正态了。」</p>
    <p>「反正越多越好，能多取就多取。」</p>
    <p>「小样本没法做统计。」</p>
  </div>
  <div class="col" data-step="2">
    <h3>严格一点的说法</h3>
    <p>30 的前提是总体不太偏。分布重尾或强偏时，30 远远不够。</p>
    <p>误差按 \(1/\sqrt{n}\) 降：100 加到 400 才减半，100 加到 200 只减三成。</p>
    <p>小样本能做，只是要换工具：t 分布、精确检验、贝叶斯。</p>
  </div>
</div>
::: note
左右两栏不要逐条对读，那样太慢。挑第一条讲透：为什么偏偏是 30？因为偏度不太大时，n=30 的正态近似误差已经在可用范围内。
再说一句：这条经验来自 1900 年代的手算时代，今天算力够，可以自己模拟一遍验证。
:::
:::

::: screen id=c7 steps=3 title="五 · 一条链"
<header class="hd">
  <div class="kicker">五 · 一条链</div>
  <h2>从总体到你手里那个区间</h2>
  <p class="lead">每一步都只做一件事，链条断了，结论就不成立。</p>
</header>

<div class="chain">
  <div class="st" data-step="1">
    <div class="k">① 总 体</div>
    <b>有一个真值 \(\mu\)</b>
    <p>你永远看不到它，只能估计。</p>
  </div>
  <div class="st" data-step="2">
    <div class="k">② 抽 样</div>
    <b>随机，且独立</b>
    <p>这一条最容易破：方便抽样、重复回答、班级整群，都会让后面的公式失效。</p>
  </div>
  <div class="st" data-step="3">
    <div class="k">③ 估 计</div>
    <b>算均值，再算标准误</b>
    <p>得到区间。区间宽窄由 n 决定，位置由样本决定。</p>
  </div>
</div>

<div class="strip" data-step="3">这条链上<b>只有第 ② 步不能靠加样本补救</b>——样本再多，抽歪了还是歪的。</div>
::: note
全场最想让他们带走的一句就在横条里：样本量治随机误差，不治系统偏差。
可以举个他们熟悉的例子：只在工作日中午发问卷，n 再大也代表不了全体。
:::
:::

::: screen id=c8 steps=0 title="收口 · 三句话"
<header class="hd">
  <div class="kicker">收口</div>
  <h2>带走三句话</h2>
  <p class="lead">如果只记得三件事，记这三件。</p>
</header>

<div class="four">
  <div class="c"><div class="t">误差按 \(1/\sqrt{n}\) 缩</div><span class="ghost">01</span><p class="d">样本翻四倍，误差才减半。预算谈判先用这条。</p></div>
  <div class="c"><div class="t">正态是均值的性质</div><span class="ghost">02</span><p class="d">不是总体的性质。总体越偏，越需要大 n 才看得出。</p></div>
  <div class="c"><div class="t">30 是经验，不是定理</div><span class="ghost">03</span><p class="d">偏态、重尾、整群抽样，都要重新算。</p></div>
  <div class="c"><div class="t">加样本治不了抽样偏差</div><span class="ghost">04</span><p class="d">先保证随机与独立，再谈样本量。</p></div>
</div>

<div class="deep">
  <div class="dt">课 后 细 读</div>
  <h3>为什么「30」这个数字会流传下来</h3>
  <p>它来自上世纪上半叶的查表实践：那时没有计算机，t 分布表在自由度 30 以上与正态表的差别已经小于印刷精度，于是「30 以上直接查正态表」成了省事的惯例。<strong>它是算力约束的产物，不是数学结论。</strong></p>
  <p>今天你可以用十行代码验证它：从一个右偏分布里反复抽 n 个样本，画出均值的直方图，看它什么时候才像钟形。多数强偏分布需要 n 在 100 以上，重尾分布甚至要上千。这就是为什么「30 就够」在教科书里成立、在真实数据上翻车。</p>
  <div class="box"><p><strong>一句收口：</strong>样本量的问题，永远是「相对你的总体有多偏」的问题，而不是「够不够 30」的问题。</p></div>
</div>
::: note
四格不要逐个念，指一下 01 和 04 就够——一头一尾是他们最会用到的。
课后细读留给他们自己看，里面是「30 的来历」，讲台上讲这个会跑题。
:::
:::
