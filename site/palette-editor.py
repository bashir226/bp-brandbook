import re
from pathlib import Path

SITE = Path(__file__).resolve().parent

STYLE = r"""
:root { --ui-ink:#1a1d1e; --ui-muted:#495054; --ui-border:#aabbcd; }
* { box-sizing:border-box; margin:0; padding:0; }
body { background:#f3f5f7; color:var(--ui-ink); font:15px/1.6 "Segoe UI",Arial,sans-serif; }
button,input,textarea { font:inherit; }
button { cursor:pointer; }
button:disabled { cursor:default; opacity:.5; }
a { color:inherit; }
h1 { font:400 38px/1.15 Georgia,serif; }
h2 { font-size:21px; line-height:1.3; }
h3 { font-size:16px; }
[hidden] { display:none !important; }
.sprite { position:absolute; width:0; height:0; overflow:hidden; }
.logo { --logo-a:var(--logo-original-red); --logo-b:var(--logo-original-graphite); display:block; max-width:100%; height:auto; }
.logo__a { fill:var(--logo-a); }
.logo__b { fill:var(--logo-b); }
.logo--reversed { --logo-a:var(--logo-reversed-red); --logo-b:var(--logo-original-white); }
button:focus-visible,input:focus-visible,textarea:focus-visible,summary:focus-visible,a:focus-visible { outline:2px solid #494951; outline-offset:3px; }
header { padding:28px max(24px,calc((100% - 1280px)/2)); background:#fff; border-bottom:1px solid var(--ui-border); }
.heading { display:flex; justify-content:space-between; gap:24px; align-items:start; }
.heading p { max-width:760px; color:var(--ui-muted); margin-top:12px; }
.header-logo { flex-shrink:0; }
.steps { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin-top:20px; padding-top:18px; border-top:1px solid var(--ui-border); list-style:none; font-size:14px; }
.steps li { padding:12px 14px; background:#f3f5f7; }
.steps strong { display:block; margin-bottom:2px; }
.publish { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:20px; align-items:end; margin-top:20px; }
.key-label { display:block; margin-bottom:6px; font-size:13px; font-weight:600; }
.key-input { width:100%; height:44px; padding:8px 12px; border:1px solid var(--ui-border); border-radius:3px; background:#fff; }
.remember { display:flex; align-items:center; gap:8px; margin-top:8px; font-size:13px; }
.key-note { margin-top:6px; color:var(--ui-muted); font-size:12px; }
.toolbar { display:flex; flex-wrap:wrap; gap:12px; align-items:center; }
.action { padding:11px 18px; min-height:44px; border:1px solid var(--ui-ink); border-radius:4px; background:var(--ui-ink); color:#fff; font-weight:600; }
.action--secondary { background:#fff; color:var(--ui-ink); }
.back-link { font-size:14px; text-decoration:underline; text-underline-offset:3px; }
.publish-status { min-height:24px; margin-top:16px; padding:10px 14px; background:#f3f5f7; font-size:14px; }
.publish-status--done { background:#edf6f0; color:#165a39; }
.publish-status--error { background:#fdecea; color:#8a1c12; }
.layout { display:grid; grid-template-columns:360px minmax(0,1fr); max-width:1280px; gap:28px; margin:28px auto; padding:0 24px; }
.controls { align-self:start; position:sticky; top:16px; max-height:calc(100vh - 32px); overflow:auto; background:#fff; border:1px solid var(--ui-border); }
details { border-bottom:1px solid var(--ui-border); }
details:last-child { border-bottom:0; }
summary { cursor:pointer; padding:16px 18px; font-weight:600; }
.fields { padding:0 18px 18px; }
.subgroup { margin-top:18px; padding-top:12px; border-top:1px solid #e4e9f0; font-size:13px; font-weight:700; }
.subgroup:first-child { margin-top:0; padding-top:0; border-top:0; }
.field { margin-top:16px; }
.field-label { display:flex; justify-content:space-between; gap:8px; margin-bottom:6px; font-size:13px; font-weight:600; }
.field-badge { color:#8a1c12; font-size:11px; font-weight:600; }
.field-row { display:grid; grid-template-columns:48px minmax(0,1fr) auto; gap:10px; align-items:center; }
.picker { padding:2px; width:48px; height:40px; border:1px solid var(--ui-border); background:#fff; cursor:pointer; }
.hex { width:100%; min-width:0; height:40px; padding:8px 10px; border:1px solid var(--ui-border); border-radius:3px; font-size:14px; }
.hex[aria-invalid="true"] { border-color:#b42318; }
.rgb { color:var(--ui-muted); font-size:10px; min-width:64px; }
.field-use { display:block; color:var(--ui-muted); font-size:11px; line-height:1.5; margin-top:5px; }
.field-error { display:block; color:#b42318; font-size:11px; margin-top:4px; }
.field-actions { display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; }
.field-source { min-height:34px; padding:5px 10px; background:#fff; border:1px solid var(--ui-border); border-radius:3px; color:var(--ui-ink); font-size:12px; }
.sampler { width:min(820px,calc(100% - 32px)); max-height:88vh; margin:auto; padding:24px; border:1px solid var(--ui-border); border-radius:6px; background:#fff; color:var(--ui-ink); overflow:auto; }
.sampler::backdrop { background:rgba(24,31,39,.5); }
.sampler-heading { display:flex; align-items:start; justify-content:space-between; gap:20px; }
.sampler-heading h2 { margin-top:3px; }
.sampler-close { min-width:44px; min-height:44px; border:1px solid var(--ui-border); border-radius:3px; background:#fff; color:var(--ui-ink); }
.sampler-target { display:block; margin-top:20px; font-size:13px; font-weight:600; }
.sampler-select { width:100%; min-height:44px; margin:6px 0 16px; padding:8px 10px; border:1px solid var(--ui-border); background:#fff; color:var(--ui-ink); font:inherit; }
.sampler-hint { margin-top:10px; color:var(--ui-muted); font-size:13px; }
.sampler-image-label { display:block; margin-top:24px; padding-top:20px; border-top:1px solid var(--ui-border); font-weight:600; font-size:14px; }
.sampler-file { display:block; max-width:100%; margin-top:12px; color:var(--ui-ink); font-size:13px; }
.sampler-status { margin-top:14px; color:var(--ui-ink); font-size:13px; min-height:22px; }
.sampler-stage { margin-top:16px; padding:12px; border:1px solid var(--ui-border); background:#f3f5f7; text-align:center; overflow:auto; }
.sampler-frame { position:relative; display:inline-block; max-width:100%; vertical-align:top; line-height:0; }
.sampler-canvas { display:block; max-width:100%; height:auto; background:#fff; cursor:crosshair; touch-action:manipulation; }
.sampler-marker { position:absolute; width:16px; height:16px; border:2px solid #fff; border-radius:50%; box-shadow:0 0 0 1px #26313c; transform:translate(-50%,-50%); pointer-events:none; }
.sampler-caption { margin-top:12px; color:var(--ui-muted); font-size:12px; }
.preview { min-width:0; }
.preview > section { background:#fff; padding:24px; margin-bottom:24px; border:1px solid var(--ui-border); }
.section-note { color:var(--ui-muted); font-size:13px; margin:8px 0 20px; }
.shade-book { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:10px; }
.shade-column { min-width:0; }
.shade-base { display:flex; flex-direction:column; justify-content:space-between; height:120px; padding:10px; font-size:12px; font-weight:600; }
.shade-cell { display:flex; justify-content:space-between; gap:4px; padding:9px 10px; font-size:11px; }
.shade-cell b { font-weight:700; }
.shade-cell--custom { box-shadow:inset 3px 0 0 #1a1d1e; }
.brand-pair { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; margin-top:20px; }
.brand-sample { padding:28px 20px; background:var(--white); color:var(--graphite-900); border:1px solid #d6dde4; }
.brand-sample--dark { background:var(--graphite-900); color:var(--white); }
.brand-sample .logo { width:220px; margin:0 auto; }
.brand-sample p { margin-top:20px; font-size:12px; text-align:center; }
.button-themes { display:grid; gap:24px; }
.button-theme h3 { margin-bottom:10px; }
.button-states { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; }
.button-state { display:flex; flex-direction:column; gap:8px; min-width:0; }
.button-sample { display:block; padding:12px 16px; border-radius:4px; font-size:14px; font-weight:600; text-align:center; }
.button-state small { font-size:11px; color:var(--ui-muted); }
.gradients { display:grid; gap:20px; }
.gradient-color { height:90px; border:1px solid var(--ui-border); }
.gradient h3 { font-size:13px; margin-top:10px; }
.gradient p { font-size:12px; color:var(--ui-muted); }
.captions { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; }
.caption-sample { padding:20px; border:1px solid var(--ui-border); }
.caption-sample h3 { font-size:14px; margin-bottom:16px; }
.caption-sample p { margin-top:10px; font-size:13px; }
.contrast-summary { margin:12px 0 16px; padding:12px 14px; background:#edf6f0; color:#165a39; font-size:13px; }
.contrast-summary--warning { background:#fff3da; color:#785000; }
.contrast-table { width:100%; border-collapse:collapse; font-size:12px; }
.contrast-table th,.contrast-table td { text-align:left; padding:10px 6px; border-bottom:1px solid var(--ui-border); }
.contrast-table th { color:var(--ui-muted); font-weight:400; }
.contrast-table td:first-child { width:54px; }
.contrast-chip { display:inline-block; min-width:40px; padding:5px; text-align:center; border:1px solid #d6dde4; font-weight:700; }
.result-ok { color:#165a39; }
.result-fail { color:#b42318; font-weight:600; }
.result-caution { color:#785000; }
.selection { width:100%; min-height:220px; padding:14px; border:1px solid var(--ui-border); background:#fafbfc; border-radius:3px; resize:vertical; color:var(--ui-ink); font-size:13px; line-height:1.6; margin:16px 0; }
@media(max-width:960px) { .layout { grid-template-columns:300px minmax(0,1fr); gap:18px; } .brand-pair,.captions { grid-template-columns:minmax(0,1fr); } .shade-book { grid-template-columns:repeat(3,minmax(0,1fr)); } .button-states { grid-template-columns:minmax(0,1fr); } }
@media(max-width:700px) { h1 { font-size:30px; } .heading { display:flex; flex-direction:column; gap:16px; } .header-logo { width:120px; } .steps,.publish { grid-template-columns:minmax(0,1fr); } .layout { grid-template-columns:minmax(0,1fr); padding:0 16px; } .controls { position:static; max-height:none; } .preview > section { padding:20px; } header { padding:24px 20px; } .toolbar .action { flex:1; } .shade-book { grid-template-columns:repeat(2,minmax(0,1fr)); } .contrast-table { font-size:11px; } .contrast-table th,.contrast-table td { padding:9px 4px; } }
"""

BODY = r"""
<header>
  <div class="heading">
    <div>
      <h1>Редактирование палитры</h1>
      <p>Меняйте базовые цвета, фоны, подписи, кнопки и отдельные оттенки. Цвет можно выбрать в квадратике, вписать HEX-код или взять пипеткой с экрана или картинки. Логотип не перекрашивается.</p>
    </div>
    <svg class="logo header-logo" viewBox="72.31 44.02 492.18 193.59" width="160" height="63" role="img" aria-label="Бизнес Партнер"><use href="#logo-full"/></svg>
  </div>
  <ol class="steps">
    <li><strong>Измените цвета</strong>Оттенки базового цвета пересчитаются сами. Любой оттенок можно задать вручную.</li>
    <li><strong>Проверьте читаемость</strong>Таблица ниже покажет, где текст станет плохо читаться.</li>
    <li><strong>Опубликуйте</strong>Через 2–4 минуты обновятся сайт, палитры, PNG и все комплекты для скачивания.</li>
  </ol>
  <div class="publish">
    <div>
      <label class="key-label" for="access-key">Ключ доступа</label>
      <input class="key-input" id="access-key" type="password" autocomplete="off" spellcheck="false">
      <label class="remember"><input type="checkbox" id="remember-key">Запомнить на этом компьютере</label>
      <p class="key-note">Ключ разрешает только сохранять палитру этого сайта. Не пересылайте его другим людям.</p>
    </div>
    <div class="toolbar">
      <button class="action" id="publish" type="button" disabled>Опубликовать на сайте</button>
      <button class="action action--secondary" id="reset" type="button" disabled>Отменить изменения</button>
      <a class="back-link" href="./">Вернуться к брендбуку</a>
    </div>
  </div>
  <p class="publish-status" id="publish-status" role="status" aria-live="polite">Изменений пока нет.</p>
</header>
<main class="layout">
  <aside class="controls" id="controls" aria-label="Настройки цветов"></aside>
  <div class="preview">
    <section aria-labelledby="book-heading">
      <h2 id="book-heading">Базовые цвета и оттенки</h2>
      <p class="section-note">Оттенки по умолчанию — смесь базового цвета с белым. Оттенки, заданные вручную, отмечены чёрной полосой слева.</p>
      <div class="shade-book" id="shade-book"></div>
      <div class="brand-pair">
        <div class="brand-sample">
          <svg class="logo" viewBox="72.31 44.02 492.18 193.59" width="220" height="86.5" role="img" aria-label="Логотип на светлом фоне"><use href="#logo-full"/></svg>
          <p>На светлом фоне</p>
        </div>
        <div class="brand-sample brand-sample--dark">
          <svg class="logo logo--reversed" viewBox="72.31 44.02 492.18 193.59" width="220" height="86.5" role="img" aria-label="Логотип на тёмном фоне"><use href="#logo-full"/></svg>
          <p>На тёмном фоне</p>
        </div>
      </div>
    </section>
    <section aria-labelledby="buttons-heading">
      <h2 id="buttons-heading">Кнопки</h2>
      <p class="section-note">Наведение и нажатие рассчитываются автоматически: каждый канал цвета темнее на 5 и 10 %. Цвет текста кнопки не меняется.</p>
      <div class="button-themes" id="button-themes"></div>
    </section>
    <section aria-labelledby="gradients-heading">
      <h2 id="gradients-heading">Градиенты</h2>
      <p class="section-note">Красный и графитовый градиенты строятся из базовых цветов. Фоновый градиент задан отдельно и не меняется.</p>
      <div class="gradients" id="gradient-preview"></div>
    </section>
    <section aria-labelledby="captions-heading">
      <h2 id="captions-heading">Подписи на светлом и тёмном</h2>
      <div class="captions" id="caption-preview"></div>
    </section>
    <section id="contrast" aria-labelledby="contrast-heading">
      <h2 id="contrast-heading">Проверка читаемости</h2>
      <p class="section-note">Для обычного текста нужно не меньше 4,5:1, для крупного — от 3:1. Это те же сочетания, что показаны на сайте.</p>
      <p class="contrast-summary" id="contrast-summary" aria-live="polite"></p>
      <table class="contrast-table"><thead><tr><th>Пример</th><th>Сочетание</th><th>Контраст</th><th>Результат</th></tr></thead><tbody id="contrast-rows"></tbody></table>
    </section>
    <section aria-labelledby="selection-heading">
      <h2 id="selection-heading">Список цветов</h2>
      <p class="section-note">Список можно отправить сообщением: нажмите «Выделить список», затем Ctrl+C.</p>
      <textarea class="selection" id="selection" aria-label="Список выбранных цветов" readonly></textarea>
      <button class="action action--secondary" id="select-text" type="button">Выделить список</button>
    </section>
  </div>
</main>
<dialog class="sampler" id="sampler" aria-labelledby="sampler-heading">
  <div class="sampler-heading">
    <h2 id="sampler-heading">Взять цвет</h2>
    <button class="sampler-close" id="sampler-close" type="button" aria-label="Закрыть пипетку">✕</button>
  </div>
  <label class="sampler-target" for="sampler-target">Какой цвет меняем</label>
  <select class="sampler-select" id="sampler-target"></select>
  <button class="action" id="sample-screen" type="button">Взять цвет с экрана</button>
  <p class="sampler-hint" id="screen-hint"></p>
  <label class="sampler-image-label" for="sample-image">Или выберите цвет из картинки</label>
  <input class="sampler-file" id="sample-image" type="file" accept="image/png,image/jpeg,image/webp">
  <p class="sampler-hint">Скриншот, фотография или логотип в PNG, JPG, WebP. Картинка обрабатывается только в браузере и никуда не отправляется.</p>
  <p class="sampler-status" id="sampler-status" role="status" aria-live="polite"></p>
  <div class="sampler-stage" id="sampler-stage" hidden>
    <div class="sampler-frame">
      <canvas class="sampler-canvas" id="sample-canvas" width="1" height="1" tabindex="0" aria-label="Выбор пикселя из картинки" aria-describedby="sample-instructions"></canvas>
      <span class="sampler-marker" id="sample-marker" hidden></span>
    </div>
  </div>
  <p class="sampler-caption" id="sample-instructions" hidden>Нажмите на нужное место картинки — цвет применится сразу. Можно выбрать другую точку. С клавиатуры: стрелки перемещают выбор на один пиксель, Enter выбирает текущий пиксель. Прозрачные участки показаны на белом фоне.</p>
</dialog>
"""

SCRIPT = r"""
const startEditor = () => {
  const data = window.brandPalette;
  const settings = data.publishing;
  const api = `https://api.github.com/repos/${settings.repository}/contents/${settings.path}`;
  const storageKey = `palette-key:${settings.repository}`;
  const groups = [['brand','Базовые цвета'],['neutral','Фоны'],['caption','Цвета подписей'],['accent','Цвета кнопок']].map(([id,name]) => ({id,name,items:data.tokens[id]}));
  const shadeKey = (token,percent) => `${token}@${percent}`;
  const shadeItems = data.tokens.brand.flatMap(color => data.shades[color.token].map(shade => ({key:shadeKey(color.token,shade.percent),base:color.token,percent:shade.percent,name:`${color.name} ${shade.percent}%`,hex:shade.hex,custom:shade.custom})));
  const names = new Map([...groups.flatMap(group => group.items.map(item => [item.token,item.name])),...shadeItems.map(item => [item.key,item.name])]);
  let published = Object.fromEntries([...groups.flatMap(group => group.items.map(item => [item.token,item.hex])),...shadeItems.map(item => [item.key,item.hex])]);
  let publishedCustom = new Set(shadeItems.filter(item => item.custom).map(item => item.key));
  let colors = {...published};
  let custom = new Set(publishedCustom);
  const fields = new Map();
  const invalid = new Set();
  const publishButton = document.getElementById('publish');
  const resetButton = document.getElementById('reset');
  const keyInput = document.getElementById('access-key');
  const rememberInput = document.getElementById('remember-key');
  const statusLine = document.getElementById('publish-status');
  const status = (message,kind) => {
    statusLine.textContent = message;
    statusLine.classList.toggle('publish-status--done',kind==='done');
    statusLine.classList.toggle('publish-status--error',kind==='error');
  };
  const savedKey = localStorage.getItem(storageKey);
  if (savedKey) {
    keyInput.value = savedKey;
    rememberInput.checked = true;
  }
  const sampler = document.getElementById('sampler');
  const samplerTarget = document.getElementById('sampler-target');
  const samplerStatus = document.getElementById('sampler-status');
  const screenButton = document.getElementById('sample-screen');
  const imageInput = document.getElementById('sample-image');
  const imageCanvas = document.getElementById('sample-canvas');
  const imageStage = document.getElementById('sampler-stage');
  const imageMarker = document.getElementById('sample-marker');
  const imageContext = imageCanvas.getContext('2d',{willReadFrequently:true});
  const logoVariables = {red:'logo-original-red',graphite:'logo-original-graphite',reversedRed:'logo-reversed-red',white:'logo-original-white'};
  Object.entries(logoVariables).forEach(([key,variable]) => document.documentElement.style.setProperty('--'+variable,data.logoColors[key]));
  let imageReady = false;
  let imagePoint = {x:0,y:0};
  screenButton.disabled = typeof window.EyeDropper !== 'function' || !window.isSecureContext;
  document.getElementById('screen-hint').textContent = screenButton.disabled
    ? 'В этом браузере экранная пипетка недоступна. Выберите картинку ниже — из неё тоже можно взять любой цвет.'
    : 'После нажатия выберите пиксель в любом месте экрана, даже за пределами браузера. Esc отменяет выбор.';
  const normalize = value => {
    const text = value.trim().replace(/^#/, '').toUpperCase();
    return /^[0-9A-F]{6}$/.test(text) ? '#' + text : null;
  };
  const rgb = hex => [1,3,5].map(offset => parseInt(hex.slice(offset,offset+2),16));
  const toHex = values => '#'+values.map(value => value.toString(16).padStart(2,'0')).join('').toUpperCase();
  const mix = (hex,percent) => toHex(rgb(hex).map(channel => Math.floor(255*(1-percent/100)+channel*percent/100+.5)));
  const darken = (hex,factor) => toHex(rgb(hex).map(channel => Math.floor(channel*factor+.5)));
  const luminance = hex => {
    const values = rgb(hex).map(value => { const c=value/255; return c<=0.04045 ? c/12.92 : ((c+0.055)/1.055)**2.4; });
    return values[0]*0.2126 + values[1]*0.7152 + values[2]*0.0722;
  };
  const ratio = (foreground,background) => {
    const a=luminance(foreground), b=luminance(background);
    return (Math.max(a,b)+0.05)/(Math.min(a,b)+0.05);
  };
  const readable = hex => ratio('#000000',hex) >= ratio('#FFFFFF',hex) ? '#000000' : '#FFFFFF';
  const tints = new Map(data.tokens.tint.map(tint => [tint.token,shadeKey(tint.shadeOf,tint.percent)]));
  const resolve = value => tints.has(value) ? colors[tints.get(value)] : colors[value] || value;
  const node = (tag,className,text) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  };
  const followsBase = key => shadeItems.some(item => item.key===key) && !custom.has(key) && !publishedCustom.has(key);
  const changedKeys = () => Object.keys(colors).filter(key => !followsBase(key) && (colors[key]!==published[key] || custom.has(key)!==publishedCustom.has(key)));

  const states = [{id:'normal',name:'Обычное',factor:1},{id:'hover',name:'Наведение',factor:data.buttonStates.hover.factor},{id:'active',name:'Нажатие',factor:data.buttonStates.active.factor}];
  const buttonLabels = new Map();
  data.buttons.forEach(button => {
    const theme = node('div','button-theme');
    const samples = node('div','button-states');
    theme.append(node('h3','',button.name),samples);
    states.forEach(state => {
      const item = node('div','button-state');
      const sample = node('span','button-sample','Подобрать удобрения');
      sample.style.backgroundColor = `var(--button-${button.id}${state.id==='normal' ? '' : '-'+state.id})`;
      sample.style.color = button.foreground;
      const label = node('small');
      buttonLabels.set(button.id+'-'+state.id,label);
      item.append(sample,label);
      samples.append(item);
    });
    document.getElementById('button-themes').append(theme);
  });
  const gradientLabels = new Map();
  data.gradients.forEach(gradient => {
    const sample = node('div','gradient');
    const color = node('div','gradient-color');
    color.style.backgroundImage = `var(--${gradient.token})`;
    const label = node('p');
    gradientLabels.set(gradient.token,label);
    sample.append(color,node('h3','',gradient.name),label);
    document.getElementById('gradient-preview').append(sample);
  });
  const captionBackgrounds = [{token:'white',foreground:'graphite-900',name:'На светлом фоне'},{token:'graphite-900',foreground:'white',name:'На тёмном фоне'}];
  captionBackgrounds.forEach(background => {
    const sample = node('div','caption-sample');
    sample.style.backgroundColor = `var(--${background.token})`;
    sample.style.color = `var(--${background.foreground})`;
    sample.append(node('h3','',background.name));
    data.tokens.caption.forEach(item => {
      const caption = node('p','',`${item.name}: подбор и доставка в поле`);
      caption.style.color = `var(--${item.token})`;
      sample.append(caption);
    });
    document.getElementById('caption-preview').append(sample);
  });

  const update = () => {
    const root = document.documentElement.style;
    groups.forEach(group => group.items.forEach(item => root.setProperty('--'+item.token,colors[item.token])));
    tints.forEach((key,token) => root.setProperty('--'+token,colors[key]));
    const book = document.getElementById('shade-book');
    book.replaceChildren(...data.tokens.brand.map(color => {
      const column = node('div','shade-column');
      const base = node('div','shade-base');
      base.style.backgroundColor = colors[color.token];
      base.style.color = readable(colors[color.token]);
      base.append(node('span','',color.name),node('span','',colors[color.token]));
      column.append(base);
      shadeItems.filter(item => item.base===color.token).forEach(item => {
        const cell = node('div',custom.has(item.key) ? 'shade-cell shade-cell--custom' : 'shade-cell');
        cell.style.backgroundColor = colors[item.key];
        cell.style.color = readable(colors[item.key]);
        cell.append(node('span','',`${item.percent} %`),node('b','',colors[item.key]));
        column.append(cell);
      });
      return column;
    }));
    data.buttons.forEach(button => {
      const hex = colors[button.token];
      root.setProperty('--button-'+button.id,hex);
      states.forEach(state => {
        const background = darken(hex,state.factor);
        if (state.id!=='normal') root.setProperty(`--button-${button.id}-${state.id}`,background);
        buttonLabels.get(button.id+'-'+state.id).textContent = `${state.name}: ${background}, ${ratio(button.foreground,background).toFixed(2)}:1`;
      });
    });
    data.gradients.forEach(gradient => {
      const stops = gradient.stops.map(stop => `${stop.token ? colors[stop.token] : stop.hex} ${stop.position}%`);
      root.setProperty('--'+gradient.token,`linear-gradient(${gradient.angle}deg,${stops.join(',')})`);
      gradientLabels.get(gradient.token).textContent = stops.join(', ');
    });
    const rows = document.getElementById('contrast-rows');
    rows.replaceChildren();
    let warnings = 0;
    data.contrasts.forEach(pair => {
      const foreground = resolve(pair.foreground);
      const background = resolve(pair.background);
      const value = ratio(foreground,background);
      if (value<4.5) warnings += 1;
      const row = node('tr');
      const sampleCell = node('td');
      const chip = node('span','contrast-chip','Аа');
      chip.style.color = foreground;
      chip.style.backgroundColor = background;
      sampleCell.append(chip);
      row.append(sampleCell,node('td','',pair.name),node('td','',value.toFixed(2)+':1'));
      row.append(node('td',value>=4.5 ? 'result-ok' : value>=3 ? 'result-caution' : 'result-fail',value>=7 ? 'AAA' : value>=4.5 ? 'AA' : value>=3 ? 'Только крупный' : 'Не подходит'));
      rows.append(row);
    });
    const summary = document.getElementById('contrast-summary');
    summary.classList.toggle('contrast-summary--warning',warnings>0);
    summary.textContent = warnings ? `Сочетаний ниже 4,5:1: ${warnings}. Они подходят только для крупного текста или не подходят для текста совсем — смотрите последнюю колонку.` : 'Все сочетания проходят AA для обычного текста.';
    const lines = [...groups.map(group => group.name+'\n'+group.items.map(item => `${item.name}: ${colors[item.token]}`).join('\n')),'Оттенки\n'+shadeItems.map(item => `${item.name}: ${colors[item.key]}${custom.has(item.key) ? ' (задан вручную)' : ''}`).join('\n')];
    document.getElementById('selection').value = 'Бизнес Партнер — палитра\n\n'+lines.join('\n\n');
    const changes = changedKeys();
    publishButton.disabled = changes.length===0 || invalid.size>0;
    resetButton.disabled = changes.length===0;
  };

  const refreshField = key => {
    const field = fields.get(key);
    field.picker.value = colors[key];
    field.hex.value = colors[key];
    field.rgb.textContent = rgb(colors[key]).join(' / ');
    field.hex.removeAttribute('aria-invalid');
    field.error.hidden = true;
    if (field.badge) {
      field.badge.hidden = !custom.has(key);
      field.restore.hidden = !custom.has(key);
    }
  };
  const setColor = (key,hex) => {
    colors[key] = hex;
    invalid.delete(key);
    const shade = shadeItems.find(item => item.key===key);
    if (shade) {
      if (hex===mix(colors[shade.base],shade.percent)) custom.delete(key); else custom.add(key);
    } else {
      shadeItems.filter(item => item.base===key && !custom.has(item.key)).forEach(item => {
        colors[item.key] = mix(hex,item.percent);
        refreshField(item.key);
      });
    }
    refreshField(key);
    update();
    const count = changedKeys().length;
    status(count ? `Неопубликованных изменений: ${count}. Нажмите «Опубликовать на сайте», когда закончите.` : 'Изменений пока нет.');
  };

  const openSampler = key => {
    samplerTarget.value = key;
    imageMarker.hidden = true;
    samplerStatus.textContent = `Меняем «${names.get(key)}». Выберите источник цвета.`;
    sampler.showModal();
  };
  const sampleImagePoint = (x,y) => {
    if (!imageReady) return;
    imagePoint = {x:Math.max(0,Math.min(imageCanvas.width-1,Math.floor(x))),y:Math.max(0,Math.min(imageCanvas.height-1,Math.floor(y)))};
    const pixel = imageContext.getImageData(imagePoint.x,imagePoint.y,1,1).data;
    const hex = toHex([pixel[0],pixel[1],pixel[2]]);
    setColor(samplerTarget.value,hex);
    imageMarker.style.left = ((imagePoint.x+.5)/imageCanvas.width*100)+'%';
    imageMarker.style.top = ((imagePoint.y+.5)/imageCanvas.height*100)+'%';
    imageMarker.hidden = false;
    samplerStatus.textContent = `Цвет ${hex} применён к «${names.get(samplerTarget.value)}». Можно выбрать другую точку или закрыть окно.`;
  };
  document.getElementById('sampler-close').addEventListener('click',() => sampler.close());
  samplerTarget.addEventListener('change',() => {
    imageMarker.hidden = true;
    samplerStatus.textContent = `Меняем «${names.get(samplerTarget.value)}». Выберите нужный пиксель.`;
  });
  screenButton.addEventListener('click',async () => {
    const key = samplerTarget.value;
    sampler.close();
    try {
      const result = await new EyeDropper().open();
      setColor(key,result.sRGBHex.toUpperCase());
      fields.get(key).hex.focus();
    } catch (error) {
      if (error.name === 'AbortError') {
        fields.get(key).hex.focus();
      } else {
        sampler.showModal();
        samplerStatus.textContent = 'Не удалось открыть экранную пипетку. Выберите картинку ниже и нажмите на нужный цвет.';
      }
    }
  });
  imageInput.addEventListener('change',async () => {
    const file = imageInput.files[0];
    if (!file) return;
    if (file.type && !['image/png','image/jpeg','image/webp'].includes(file.type)) {
      samplerStatus.textContent = 'Выберите картинку PNG, JPG или WebP.';
      imageInput.value = '';
      return;
    }
    imageInput.disabled = true;
    samplerStatus.textContent = 'Открываем картинку…';
    try {
      const bitmap = await createImageBitmap(file);
      try {
        imageCanvas.width = bitmap.width;
        imageCanvas.height = bitmap.height;
        imageContext.fillStyle = '#FFFFFF';
        imageContext.fillRect(0,0,bitmap.width,bitmap.height);
        imageContext.drawImage(bitmap,0,0);
      } finally {
        bitmap.close();
      }
      imageReady = true;
      imagePoint = {x:Math.floor(imageCanvas.width/2),y:Math.floor(imageCanvas.height/2)};
      imageMarker.hidden = true;
      imageStage.hidden = false;
      document.getElementById('sample-instructions').hidden = false;
      samplerStatus.textContent = `Открыто: ${file.name}. Нажмите на нужный цвет картинки.`;
    } catch {
      samplerStatus.textContent = 'Не удалось прочитать картинку. Выберите другой файл PNG, JPG или WebP.';
    } finally {
      imageInput.disabled = false;
      imageInput.value = '';
    }
  });
  imageCanvas.addEventListener('click',event => {
    const bounds = imageCanvas.getBoundingClientRect();
    sampleImagePoint((event.clientX-bounds.left)*imageCanvas.width/bounds.width,(event.clientY-bounds.top)*imageCanvas.height/bounds.height);
  });
  imageCanvas.addEventListener('keydown',event => {
    const movement = {ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]};
    if (movement[event.key]) {
      event.preventDefault();
      const [x,y] = movement[event.key];
      sampleImagePoint(imagePoint.x+x,imagePoint.y+y);
    } else if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      sampleImagePoint(imagePoint.x,imagePoint.y);
    }
  });

  const createField = (key,name,use,isShade) => {
    const field = node('div','field');
    const label = node('label','field-label');
    label.htmlFor = 'hex-'+key;
    label.append(node('span','',name));
    let badge = null;
    if (isShade) {
      badge = node('span','field-badge','задан вручную');
      label.append(badge);
    }
    const row = node('div','field-row');
    const picker = document.createElement('input');
    picker.type = 'color';
    picker.className = 'picker';
    picker.setAttribute('aria-label','Выбрать цвет: '+name);
    const hex = document.createElement('input');
    hex.type = 'text';
    hex.className = 'hex';
    hex.id = 'hex-'+key;
    hex.maxLength = 7;
    hex.spellcheck = false;
    hex.autocomplete = 'off';
    const channels = node('span','rgb');
    row.append(picker,hex,channels);
    const error = node('span','field-error','Нужен HEX из 6 знаков, например #CD192A.');
    error.id = 'error-'+key;
    hex.setAttribute('aria-describedby',error.id);
    const actions = node('div','field-actions');
    const source = node('button','field-source','Пипетка');
    source.type = 'button';
    source.setAttribute('aria-label','Взять цвет пипеткой: '+name);
    source.setAttribute('aria-haspopup','dialog');
    source.addEventListener('click',() => openSampler(key));
    actions.append(source);
    let restore = null;
    if (isShade) {
      restore = node('button','field-source','Вернуть расчётный');
      restore.type = 'button';
      restore.setAttribute('aria-label','Вернуть расчётный оттенок: '+name);
      restore.addEventListener('click',() => {
        const shade = shadeItems.find(item => item.key===key);
        setColor(key,mix(colors[shade.base],shade.percent));
      });
      actions.append(restore);
    }
    fields.set(key,{picker,hex,rgb:channels,error,badge,restore});
    picker.addEventListener('input',() => setColor(key,picker.value.toUpperCase()));
    hex.addEventListener('input',() => {
      const value = normalize(hex.value);
      if (value) {
        setColor(key,value);
      } else {
        invalid.add(key);
        hex.setAttribute('aria-invalid','true');
        error.hidden = false;
        publishButton.disabled = true;
        status('Исправьте HEX-код: публикация недоступна, пока код неверный. Предпросмотр показывает последний корректный цвет.','error');
      }
    });
    field.append(label,row);
    if (use) field.append(node('span','field-use',use));
    field.append(actions,error);
    refreshField(key);
    return field;
  };

  const controls = document.getElementById('controls');
  groups.forEach((group,index) => {
    const details = node('details');
    details.open = index===0;
    const list = node('div','fields');
    group.items.forEach(item => list.append(createField(item.token,item.name,item.use,false)));
    details.append(node('summary','',group.name),list);
    controls.append(details);
    const optionGroup = document.createElement('optgroup');
    optionGroup.label = group.name;
    group.items.forEach(item => optionGroup.append(new Option(item.name,item.token)));
    samplerTarget.append(optionGroup);
  });
  const shadeDetails = node('details');
  const shadeList = node('div','fields');
  data.tokens.brand.forEach(color => {
    shadeList.append(node('div','subgroup',color.name));
    shadeItems.filter(item => item.base===color.token).forEach(item => shadeList.append(createField(item.key,`${item.percent} %`,null,true)));
    const optionGroup = document.createElement('optgroup');
    optionGroup.label = `Оттенки: ${color.name}`;
    shadeItems.filter(item => item.base===color.token).forEach(item => optionGroup.append(new Option(item.name,item.key)));
    samplerTarget.append(optionGroup);
  });
  shadeDetails.append(node('summary','','Оттенки'),shadeList);
  controls.insertBefore(shadeDetails,controls.children[1]);
  fields.forEach((field,key) => refreshField(key));

  const encodeBase64 = text => {
    let binary = '';
    new TextEncoder().encode(text).forEach(byte => { binary += String.fromCharCode(byte); });
    return btoa(binary);
  };
  const decodeBase64 = text => new TextDecoder().decode(Uint8Array.from(atob(text.replace(/\s/g,'')),character => character.charCodeAt(0)));
  const waitForSite = async revision => {
    for (let attempt = 0; attempt < 48; attempt += 1) {
      await new Promise(resolve => setTimeout(resolve,15000));
      try {
        const response = await fetch(`palette-data.js?check=${Date.now()}`,{cache:'no-store'});
        if (response.ok && (await response.text()).includes(revision)) {
          status('Готово: сайт обновлён. Новые цвета уже в палитрах, PNG и комплектах для скачивания. Если сайт открыт в другой вкладке, обновите её.','done');
          return;
        }
      } catch {
        continue;
      }
    }
    status('Изменения сохранены, но сайт ещё не обновился. Проверьте через несколько минут; если цвета не поменяются, напишите исполнителю.','error');
  };
  publishButton.addEventListener('click',async () => {
    const key = keyInput.value.trim();
    if (!key) {
      status('Введите ключ доступа: без него сохранить палитру нельзя.','error');
      keyInput.focus();
      return;
    }
    if (rememberInput.checked) localStorage.setItem(storageKey,key); else localStorage.removeItem(storageKey);
    const changes = changedKeys();
    publishButton.disabled = true;
    resetButton.disabled = true;
    status('Сохраняем изменения…');
    const headers = {Accept:'application/vnd.github+json',Authorization:`Bearer ${key}`,'X-GitHub-Api-Version':'2022-11-28'};
    try {
      const current = await fetch(`${api}?ref=${encodeURIComponent(settings.branch)}`,{headers,cache:'no-store'});
      if (current.status===401) throw new Error('Ключ не подходит или срок его действия закончился. Попросите новый ключ у исполнителя.');
      if (current.status===403 || current.status===404) throw new Error('У этого ключа нет доступа к палитре сайта. Попросите ключ с правом изменения файлов.');
      if (!current.ok) throw new Error(`Не удалось получить палитру с сервера: ошибка ${current.status}.`);
      const file = await current.json();
      const source = JSON.parse(decodeBase64(file.content));
      source.shadeOverrides = source.shadeOverrides || {};
      changes.forEach(changeKey => {
        const shade = shadeItems.find(item => item.key===changeKey);
        if (shade) {
          const overrides = source.shadeOverrides[shade.base] || {};
          if (custom.has(changeKey)) overrides[String(shade.percent)] = colors[changeKey]; else delete overrides[String(shade.percent)];
          if (Object.keys(overrides).length) source.shadeOverrides[shade.base] = overrides; else delete source.shadeOverrides[shade.base];
        } else {
          Object.values(source.tokens).flat().filter(color => color.token===changeKey).forEach(color => { color.hex = colors[changeKey]; });
        }
      });
      const revision = new Date().toISOString();
      source.revision = revision;
      const message = 'Палитра: '+changes.map(changeKey => `${names.get(changeKey)} ${colors[changeKey]}`).join(', ');
      const saved = await fetch(api,{method:'PUT',headers:{...headers,'Content-Type':'application/json'},body:JSON.stringify({message:message.slice(0,500),content:encodeBase64(JSON.stringify(source,null,2)+'\n'),sha:file.sha,branch:settings.branch})});
      if (saved.status===409 || saved.status===422) throw new Error('Палитру только что изменили в другом окне. Обновите страницу и внесите изменения ещё раз.');
      if (saved.status===401 || saved.status===403 || saved.status===404) throw new Error('Ключ не позволяет сохранять изменения. Попросите ключ с правом изменения файлов.');
      if (!saved.ok) throw new Error(`Не удалось сохранить палитру: ошибка ${saved.status}.`);
      published = {...colors};
      publishedCustom = new Set(custom);
      update();
      status('Сохранено. Сайт и все файлы обновятся через 2–4 минуты. Оставьте страницу открытой, чтобы увидеть подтверждение.');
      waitForSite(revision);
    } catch (error) {
      status(error instanceof TypeError ? 'Нет связи с сервером. Проверьте интернет и попробуйте ещё раз.' : error.message,'error');
      update();
    }
  });
  resetButton.addEventListener('click',() => {
    if (!confirm('Отменить все неопубликованные изменения?')) return;
    colors = {...published};
    custom = new Set(publishedCustom);
    invalid.clear();
    fields.forEach((field,key) => refreshField(key));
    update();
    status('Изменения отменены.');
  });
  document.getElementById('select-text').addEventListener('click',() => {
    const text = document.getElementById('selection');
    text.focus();
    text.select();
  });
  update();
};
const paletteScript = document.createElement('script');
paletteScript.src = `palette-data.js?editor=${Date.now()}`;
paletteScript.addEventListener('load',startEditor);
paletteScript.addEventListener('error',() => {
  document.getElementById('publish-status').textContent = 'Не удалось загрузить палитру. Обновите страницу.';
});
document.head.append(paletteScript);
"""


def main():
    source = (SITE / "index.html").read_text(encoding="utf-8")
    definitions = re.search(r"<defs>.*?</defs>", source, re.S).group(0)
    policy = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' https://api.github.com; base-uri 'none'; form-action 'none'"
    document = (
        "<!doctype html>\n<html lang=\"ru\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<meta name=\"robots\" content=\"noindex,nofollow\">"
        f"<meta http-equiv=\"Content-Security-Policy\" content=\"{policy}\">"
        "<title>Редактирование палитры — Бизнес Партнер</title><style>" + STYLE + "</style></head><body>\n"
        "<svg class=\"sprite\" aria-hidden=\"true\">" + definitions + "</svg>\n"
        + BODY + "<script>" + SCRIPT + "</script></body></html>\n"
    )
    (SITE / "edit.html").write_text(document, encoding="utf-8")
    print(SITE / "edit.html")


if __name__ == "__main__":
    main()
