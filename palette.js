(() => {
  const data = window.brandPalette;
  const tokens = new Map(Object.values(data.tokens).flat().map(token => [token.token, token]));
  const resolve = value => tokens.has(value) ? tokens.get(value).hex : value;
  const paint = value => tokens.has(value) ? `var(--${value})` : value;
  const element = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const luminance = hex => [1, 3, 5]
    .map(index => parseInt(hex.slice(index, index + 2), 16) / 255)
    .map(channel => channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4)
    .reduce((total, channel, index) => total + channel * [0.2126, 0.7152, 0.0722][index], 0);
  const contrast = (foreground, background) => {
    const values = [luminance(resolve(foreground)), luminance(resolve(background))].sort((a, b) => a - b);
    return (values[1] + 0.05) / (values[0] + 0.05);
  };
  const readable = hex => contrast('#000000', hex) >= contrast('#FFFFFF', hex) ? '#000000' : '#FFFFFF';
  const ratioText = ratio => `${ratio.toFixed(2).replace('.', ',')}:1`;
  const verdict = ratio => ratio >= 7 ? 'AAA' : ratio >= 4.5 ? 'AA' : ratio >= 3 ? 'Только крупный текст' : 'Не для текста';
  const heading = (title, description) => {
    const header = element('div', 'palette-heading');
    header.append(element('h3', 'palette-heading__title', title));
    if (description) header.append(element('p', 'palette-heading__text', description));
    return header;
  };
  const swatch = (className, background, foreground) => {
    const card = element('div', `swatch ${className}`);
    const color = element('div', 'swatch__color');
    color.style.backgroundColor = background;
    if (foreground) color.style.color = foreground;
    card.append(color);
    return { card, color };
  };

  const stripes = document.querySelector('#cover-stripes');
  data.tokens.brand.forEach(token => {
    const stripe = element('div', 'cover-stripe');
    stripe.setAttribute('role', 'listitem');
    stripe.style.backgroundColor = paint(token.token);
    stripe.style.color = readable(token.hex);
    if (contrast(token.hex, 'ink') < 1.5) stripe.classList.add('cover-stripe--outlined');
    stripe.append(element('span', 'cover-stripe__name', token.name), element('span', 'cover-stripe__hex', token.hex));
    stripes.append(stripe);
  });

  const catalog = document.querySelector('#palette-catalog');
  const catalogContent = document.createDocumentFragment();

  const bookGroup = element('section', 'palette-group');
  const proposed = data.tokens.tint.map(token => token.hex).join(', ');
  bookGroup.append(heading('Базовые цвета и оттенки', `Каждый цвет смешан с белым: ${data.shadePercents.join(', ')} %. Шкалы оттенков — наше предложение. У яркого красного это четыре цвета плавного перехода от белого: ${proposed}.`));
  const book = element('div', 'color-book');
  data.tokens.brand.forEach(token => {
    const column = element('div', 'color-book__column');
    column.dataset.token = token.token;
    const base = swatch('book-base', paint(token.token), readable(token.hex));
    base.color.append(
      element('span', 'book-base__name', token.name),
      element('span', 'book-base__codes'),
    );
    base.color.lastChild.append(element('span', 'swatch__hex book-base__hex', token.hex), element('span', 'book-base__rgb', `RGB ${token.rgb.join(' ')}`));
    column.append(base.card);
    data.shades[token.token].forEach(shade => {
      const cell = swatch(`book-shade${shade.token ? ' book-shade--proposed' : ''}`, shade.hex, readable(shade.hex));
      cell.color.append(element('span', 'book-shade__percent', `${shade.percent} %`), element('span', 'swatch__hex book-shade__hex', shade.hex));
      column.append(cell.card);
    });
    column.append(element('p', 'color-book__use', token.use));
    book.append(column);
  });
  bookGroup.append(book);
  catalogContent.append(bookGroup);

  const surfaceGroup = element('section', 'palette-group');
  surfaceGroup.append(heading('Фоны', 'Шесть светлых поверхностей для страниц, блоков и документов. Разница между ними тонкая — так фон не спорит с содержанием.'));
  const surfaces = element('div', 'surface-strip');
  data.tokens.neutral.forEach(token => {
    const cell = swatch('surface', paint(token.token), '#1A1D1E');
    cell.color.append(element('span', 'surface__name', token.name), element('span', 'swatch__hex surface__hex', token.hex));
    cell.card.append(element('p', 'surface__use', token.use));
    surfaces.append(cell.card);
  });
  surfaceGroup.append(surfaces);
  catalogContent.append(surfaceGroup);

  const captionGroup = element('section', 'palette-group');
  captionGroup.append(heading('Цвета подписей', 'Один и тот же цвет читается по-разному на светлом и тёмном. Выбирайте по оценке рядом с образцом.'));
  const captions = element('div', 'caption-list');
  data.tokens.caption.forEach(token => {
    const row = swatch('caption-row', paint(token.token));
    row.color.classList.add('caption-row__chip');
    const info = element('div', 'caption-row__info');
    info.append(element('span', 'caption-row__name', token.name), element('span', 'swatch__hex caption-row__hex', token.hex), element('span', 'caption-row__use', token.use));
    row.card.append(info);
    [['white', 'На белом'], ['ink', 'На тёмном']].forEach(([background, label]) => {
      const sample = element('div', `caption-sample caption-sample--${background}`);
      const text = element('span', 'caption-sample__text', 'Подбор и доставка в поле');
      text.style.color = paint(token.token);
      const ratio = contrast(token.token, background);
      sample.append(text, element('span', 'caption-sample__result', `${label}: ${ratioText(ratio)}, ${verdict(ratio)}`));
      row.card.append(sample);
    });
    captions.append(row.card);
  });
  captionGroup.append(captions);
  catalogContent.append(captionGroup);

  const buttonGroup = element('section', 'palette-group');
  buttonGroup.append(heading('Цвета кнопок', 'Четыре темы. Для одного и того же действия на сайте используйте одну тему.'));
  const buttons = element('div', 'button-cards');
  data.buttons.forEach(button => {
    const base = tokens.get(button.token);
    const card = swatch('button-card', `var(--button-${button.id})`, `var(--button-${button.id}-text)`);
    card.color.append(element('span', 'button-card__label', 'Запросить подбор'), element('span', 'swatch__hex button-card__hex', base.hex));
    const states = element('div', 'button-card__states');
    [['Наведение', button.hover], ['Нажатие', button.active]].forEach(([label, hex]) => {
      const state = element('span', 'button-card__state');
      const chip = element('span', 'button-card__chip');
      chip.style.backgroundColor = hex;
      state.append(chip, element('span', '', `${label} ${hex}`));
      states.append(state);
    });
    card.card.append(element('span', 'button-card__name', `${button.name} тема, текст ${button.foreground === '#000000' ? 'чёрный' : 'белый'}`), states);
    buttons.append(card.card);
  });
  buttonGroup.append(buttons);
  catalogContent.append(buttonGroup);

  catalogContent.append(element('p', 'palette-notice', `Логотип не перекрашивается: его цвета остаются ${data.logoColors.red} и ${data.logoColors.graphite}, в инверсной версии — ${data.logoColors.reversedRed} и ${data.logoColors.white}. Новая палитра работает в рекламе, на сайте и в документах.`));
  catalog.replaceChildren(catalogContent);

  const details = document.querySelector('#palette-details');
  const detailContent = document.createDocumentFragment();

  const gradientGroup = element('section', 'palette-group');
  gradientGroup.append(heading('Градиенты', 'Текст размещайте рядом с градиентом или на однотонной плашке, а не на переходе цвета.'));
  const gradients = element('div', 'gradient-list');
  data.gradients.forEach(gradient => {
    const item = element('article', 'gradient-item');
    const band = element('div', 'gradient-item__band');
    band.style.backgroundImage = `var(--${gradient.token})`;
    band.setAttribute('role', 'img');
    band.setAttribute('aria-label', gradient.name);
    const info = element('div', 'gradient-item__info');
    const css = `linear-gradient(${gradient.angle}deg, ${gradient.stops.map(stop => `${stop.hex} ${stop.position}%`).join(', ')})`;
    info.append(element('h4', 'gradient-item__name', gradient.name), element('p', 'gradient-item__use', gradient.use), element('code', 'gradient-item__code', css));
    item.append(band, info);
    gradients.append(item);
  });
  gradientGroup.append(gradients);
  detailContent.append(gradientGroup);

  const stateGroup = element('section', 'palette-group');
  stateGroup.append(heading('Состояния кнопок', 'Наведение — каждый канал цвета темнее на 5 %, нажатие — на 10 %. Цвет текста не меняется.'));
  const panel = element('div', 'state-panel');
  data.buttons.forEach(button => {
    const row = element('div', 'state-row');
    row.append(element('span', 'state-row__name', button.name));
    Object.entries(data.buttonStates).forEach(([state, definition]) => {
      const cell = element('div', 'state-cell');
      const sample = element('span', `state-button state-button--${state}`, 'Продолжить');
      const background = state === 'disabled' ? definition.background : state === 'hover' || state === 'active' ? button[state] : button.token;
      const foreground = state === 'disabled' ? definition.foreground : button.foreground;
      sample.style.backgroundColor = state === 'disabled' ? paint(background) : `var(--button-${button.id}${state === 'hover' || state === 'active' ? `-${state}` : ''})`;
      sample.style.color = state === 'disabled' ? paint(foreground) : `var(--button-${button.id}-text)`;
      cell.append(element('span', 'state-cell__name', definition.name), sample, element('span', 'state-cell__value', `${resolve(background)}, ${ratioText(contrast(foreground, background))}`));
      row.append(cell);
    });
    panel.append(row);
  });
  stateGroup.append(panel);
  detailContent.append(stateGroup);

  const readingGroup = element('section', 'palette-group');
  readingGroup.append(heading('Читаемость', 'Обычный текст — от 4,5:1, крупный (от 24 px или от 19 px жирным) — от 3:1.'));
  const rules = element('ul', 'reading-rules');
  ['red-600', 'red-500'].forEach(key => {
    const token = tokens.get(key);
    rules.append(element('li', '', `${token.name} ${token.hex}: белый текст ${ratioText(contrast('white', key))} — только крупный. Для мелкого текста на этом цвете берите чёрный: ${ratioText(contrast('#000000', key))}.`));
  });
  ['red-400', 'steel-400', 'steel-300'].forEach(key => {
    const token = tokens.get(key);
    rules.append(element('li', '', `${token.name} ${token.hex}: на белом ${ratioText(contrast(key, 'white'))}, на тёмном ${ratioText(contrast(key, 'ink'))}. ${contrast(key, 'white') >= 4.5 ? '' : 'На белом не используйте для мелких подписей.'}`.trim()));
  });
  readingGroup.append(rules);

  const table = element('details', 'contrast-details');
  table.dataset.exportIgnore = '';
  table.append(element('summary', 'contrast-details__summary', `Полная таблица контраста: ${data.contrasts.length} сочетаний`));
  const scroll = element('div', 'contrast-scroll');
  scroll.tabIndex = 0;
  scroll.setAttribute('role', 'region');
  scroll.setAttribute('aria-label', 'Таблица контраста');
  const grid = element('table', 'contrast-table');
  const head = element('thead');
  const headRow = element('tr');
  ['Сочетание', 'Текст и фон', 'Контраст', 'Обычный текст', 'Крупный текст'].forEach(title => {
    const cell = element('th', '', title);
    cell.scope = 'col';
    headRow.append(cell);
  });
  head.append(headRow);
  const body = element('tbody');
  data.contrasts.forEach(pair => {
    const row = element('tr');
    const title = element('th', '', pair.name);
    title.scope = 'row';
    const colors = element('td', 'contrast-table__colors');
    [pair.foreground, pair.background].forEach(value => {
      const chip = element('span', 'contrast-chip');
      const square = element('span', 'contrast-chip__color');
      square.style.backgroundColor = paint(value);
      chip.append(square, element('span', '', resolve(value)));
      colors.append(chip);
    });
    row.append(title, colors, element('td', '', ratioText(pair.ratio)));
    [[pair.normalTextAA, pair.ratio >= 7 ? 'AAA' : 'AA'], [pair.largeTextAA, 'AA']].forEach(([pass, label]) => {
      row.append(element('td', pass ? 'contrast-pass' : 'contrast-fail', pass ? label : 'Нет'));
    });
    body.append(row);
  });
  grid.append(head, body);
  scroll.append(grid);
  table.append(scroll);
  readingGroup.append(table);
  detailContent.append(readingGroup);

  details.replaceChildren(detailContent);
})();
