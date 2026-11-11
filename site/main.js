(() => {
  const menu = document.querySelector('.topbar__menu');
  const navigation = document.querySelector('.topbar__nav');
  const notice = document.querySelector('#notice');
  let noticeTimer;

  const announce = message => {
    clearTimeout(noticeTimer);
    notice.textContent = message;
    notice.hidden = false;
    noticeTimer = setTimeout(() => { notice.hidden = true; }, 3800);
  };

  const closeMenu = () => {
    navigation.classList.remove('is-open');
    menu.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-label', 'Открыть разделы');
  };

  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    navigation.classList.toggle('is-open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Закрыть разделы' : 'Открыть разделы');
  });
  navigation.addEventListener('click', event => {
    if (event.target.closest('a')) closeMenu();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      menu.focus();
    }
  });

  document.querySelectorAll('.swatch').forEach(swatch => {
    const code = swatch.querySelector('.swatch__hex').textContent.trim();
    const color = swatch.querySelector('.swatch__color');
    const copyButton = color.querySelector('button');
    const target = copyButton || color;
    target.setAttribute('aria-label', `Скопировать цвет ${code}`);
    if (!copyButton) {
      color.setAttribute('role', 'button');
      color.tabIndex = 0;
    }
    const copy = async () => {
      try {
        await navigator.clipboard.writeText(code);
        announce(`Цвет ${code} скопирован`);
      } catch {
        announce(`Не удалось скопировать автоматически. Скопируйте код вручную: ${code}`);
      }
    };
    swatch.addEventListener('click', copy);
    if (!copyButton) {
      color.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          copy();
        }
      });
    }
  });
})();
