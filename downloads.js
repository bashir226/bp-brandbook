(() => {
  const data = window.brandDownloads;
  const element = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const size = bytes => bytes >= 1048576
    ? `${(bytes / 1048576).toFixed(1).replace('.', ',')} МБ`
    : `${Math.max(1, Math.round(bytes / 1024))} КБ`;
  const link = (file, className, label) => {
    const anchor = element('a', className, label);
    anchor.href = file.path;
    anchor.download = file.name;
    return anchor;
  };

  const tasks = document.querySelector('#download-tasks');
  data.tasks.forEach(task => {
    const card = element('article', `task-card task-card--${task.id}`);
    const head = element('div', 'task-card__head');
    head.append(element('h3', 'task-card__title', task.title), element('p', 'task-card__audience', task.audience));
    const list = element('ul', 'task-card__list');
    task.items.forEach(item => list.append(element('li', '', item)));
    const action = link(task.file, 'button task-card__button', 'Скачать комплект');
    action.append(element('span', 'task-card__size', `ZIP, ${size(task.file.size)}`));
    card.append(head, list, action);
    tasks.append(card);
  });

  const files = document.querySelector('#download-files');
  data.groups.forEach(group => {
    const section = element('section', 'file-group');
    section.id = group.id;
    section.append(element('h4', 'file-group__title', group.title));
    const list = element('ul', 'file-group__list');
    group.files.forEach(file => {
      const row = element('li', 'file-row');
      const info = element('div', 'file-row__info');
      info.append(element('span', 'file-row__title', file.title), element('span', 'file-row__meta', `${file.format}, ${size(file.size)}`));
      row.append(info, link(file, 'file-row__link', 'Скачать'));
      list.append(row);
    });
    section.append(list);
    files.append(section);
  });

  document.querySelectorAll('.color-book__column[data-token]').forEach(column => {
    const shade = data.shades[column.dataset.token];
    const links = element('div', 'book-downloads');
    links.append(element('span', 'book-downloads__label', 'Скачать шкалу'), link(shade.ase, 'book-downloads__link', 'ASE'), link(shade.png, 'book-downloads__link', 'PNG'));
    column.insertBefore(links, column.querySelector('.color-book__use'));
  });
})();
