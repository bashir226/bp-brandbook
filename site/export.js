(() => {
  const SVG_NS = 'http://www.w3.org/2000/svg';
  const serializer = new XMLSerializer();
  const measure = document.createElement('canvas').getContext('2d');
  const PRESENTATION_PROPS = ['fill', 'fill-opacity', 'fill-rule', 'stroke', 'stroke-opacity', 'stroke-width', 'stroke-linecap', 'stroke-linejoin', 'stroke-dasharray', 'stroke-dashoffset', 'clip-rule'];

  const round = value => Math.round(value * 100) / 100;
  const precise = value => Math.round(value * 1000000) / 1000000;

  const escapeXml = text => text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

  const parseColor = value => {
    const match = value.match(/rgba?\(([^)]+)\)/);
    if (!match) return null;
    const parts = match[1].split(/[ ,/]+/).filter(Boolean).map(Number);
    const hex = parts
      .slice(0, 3)
      .map(channel => Math.round(channel).toString(16).padStart(2, '0'))
      .join('');
    return { hex: `#${hex}`, alpha: parts.length > 3 ? parts[3] : 1 };
  };

  const splitTopLevel = source => {
    const parts = [];
    let depth = 0;
    let current = '';
    for (const char of source) {
      if (char === '(') depth++;
      if (char === ')') depth--;
      if (char === ',' && depth === 0) {
        parts.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    if (current.trim()) parts.push(current.trim());
    return parts;
  };

  const fontAscent = style => {
    measure.font = `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
    return measure.measureText('Hg').fontBoundingBoxAscent;
  };

  const cornerRadius = (style, width, height) => {
    const corners = ['TopLeft', 'TopRight', 'BottomRight', 'BottomLeft'].map(corner => {
      const value = style[`border${corner}Radius`].split(' ')[0];
      return value.endsWith('%') ? (Math.min(width, height) * parseFloat(value)) / 100 : parseFloat(value) || 0;
    });
    return Math.max(...corners);
  };

  const borderSides = style => ['Top', 'Right', 'Bottom', 'Left'].map(side => {
    const color = parseColor(style[`border${side}Color`]);
    const visible = Boolean(color) && color.alpha > 0 && style[`border${side}Style`] !== 'none';
    return {
      width: visible ? parseFloat(style[`border${side}Width`]) || 0 : 0,
      style: style[`border${side}Style`],
      color,
    };
  });

  const resolveUses = (root, style) => {
    root.querySelectorAll('use').forEach(use => {
      const href = use.getAttribute('href');
      const target = href?.startsWith('#') ? document.getElementById(href.slice(1)) : null;
      if (!target) throw new Error(`Не найден SVG-источник: ${href}`);
      const group = document.createElementNS(SVG_NS, 'g');
      const transform = use.getAttribute('transform');
      PRESENTATION_PROPS.forEach(prop => {
        if (use.hasAttribute(prop)) group.setAttribute(prop, use.getAttribute(prop));
      });
      if (transform) group.setAttribute('transform', transform);
      const sources = target.localName === 'symbol' ? [...target.children] : [target];
      sources.forEach(node => group.append(node.cloneNode(true)));
      group.querySelectorAll('[id]').forEach(node => node.removeAttribute('id'));
      group.removeAttribute('id');
      use.replaceWith(group);
    });
    root.querySelectorAll('[class]').forEach(node => {
      const brandPart = [...node.classList].find(name => /^logo__[a-z]$/.test(name));
      if (brandPart) {
        const property = `--logo-${brandPart.slice(-1)}`;
        node.setAttribute('fill', style.getPropertyValue(property).trim());
      }
      node.removeAttribute('class');
    });
  };

  const flattenSvg = (svg, style, box) => {
    const viewBox = svg.viewBox.baseVal;
    const stretch = (svg.getAttribute('preserveAspectRatio') || '').startsWith('none');
    const fit = Math.min(box.width / viewBox.width, box.height / viewBox.height);
    const scaleX = stretch ? box.width / viewBox.width : fit;
    const scaleY = stretch ? box.height / viewBox.height : fit;
    const translateX = box.x + (box.width - viewBox.width * scaleX) / 2 - viewBox.x * scaleX;
    const translateY = box.y + (box.height - viewBox.height * scaleY) / 2 - viewBox.y * scaleY;

    const content = document.createElementNS(SVG_NS, 'g');
    [...svg.childNodes].forEach(node => content.append(node.cloneNode(true)));
    const sources = svg.querySelectorAll('*');
    const copies = content.querySelectorAll('*');
    sources.forEach((source, index) => {
      const computed = getComputedStyle(source);
      PRESENTATION_PROPS.forEach(prop => {
        const value = computed.getPropertyValue(prop);
        if (value) copies[index].setAttribute(prop, value);
      });
    });
    resolveUses(content, style);
    PRESENTATION_PROPS.forEach(prop => {
      const value = style.getPropertyValue(prop);
      if (value && value !== 'normal') content.setAttribute(prop, value);
    });
    content.setAttribute(
      'transform',
      `matrix(${precise(scaleX)} 0 0 ${precise(scaleY)} ${round(translateX)} ${round(translateY)})`
    );
    return serializer.serializeToString(content).replace(/ xmlns="[^"]*"/g, '');
  };

  const exportFrame = frame => {
    const frameBox = frame.getBoundingClientRect();
    const defs = [];
    const nodes = [];
    let counter = 0;

    const layerName = element => {
      counter++;
      const [firstClass] = (element.getAttribute('class') || '').trim().split(/\s+/);
      return `${element.localName}${firstClass ? `-${firstClass}` : ''}-${counter}`;
    };

    const linearGradient = (backgroundImage, box) => {
      const match = backgroundImage.match(/^linear-gradient\((.*)\)$/s);
      if (!match) return null;
      const parts = splitTopLevel(match[1]);
      const angle = /deg$/.test(parts[0]) ? parseFloat(parts.shift()) : 180;
      const stops = parts.map((part, index) => {
        const [, colorSource, position] = part.match(/^(rgba?\([^)]+\))\s*([\d.]+%)?$/);
        return {
          color: parseColor(colorSource),
          offset: position ? parseFloat(position) / 100 : index / (parts.length - 1),
        };
      });
      const radians = (angle * Math.PI) / 180;
      const length = Math.abs(box.width * Math.sin(radians)) + Math.abs(box.height * Math.cos(radians));
      const centerX = box.x + box.width / 2;
      const centerY = box.y + box.height / 2;
      const deltaX = (Math.sin(radians) * length) / 2;
      const deltaY = (-Math.cos(radians) * length) / 2;
      const id = `gradient-${defs.length}`;
      const stopMarkup = stops
        .map(stop => `<stop offset="${round(stop.offset)}" stop-color="${stop.color.hex}"${stop.color.alpha < 1 ? ` stop-opacity="${stop.color.alpha}"` : ''}/>`)
        .join('');
      defs.push(`<linearGradient id="${id}" gradientUnits="userSpaceOnUse" x1="${round(centerX - deltaX)}" y1="${round(centerY - deltaY)}" x2="${round(centerX + deltaX)}" y2="${round(centerY + deltaY)}">${stopMarkup}</linearGradient>`);
      return `url(#${id})`;
    };

    const emitText = (textNode, style) => {
      if (!textNode.textContent.trim()) return;
      const range = document.createRange();
      const lines = new Map();
      for (const word of textNode.textContent.matchAll(/\S+/g)) {
        range.setStart(textNode, word.index);
        range.setEnd(textNode, word.index + word[0].length);
        const [rect] = range.getClientRects();
        if (!rect) continue;
        const key = Math.round(rect.top);
        if (!lines.has(key)) lines.set(key, { left: rect.left, top: rect.top, words: [] });
        lines.get(key).words.push(style.textTransform === 'uppercase' ? word[0].toUpperCase() : word[0]);
      }
      const color = parseColor(style.color);
      const ascent = fontAscent(style);
      const family = style.fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, '');
      const spacing = style.letterSpacing !== 'normal' ? ` letter-spacing="${round(parseFloat(style.letterSpacing))}"` : '';
      const italic = style.fontStyle !== 'normal' ? ` font-style="${style.fontStyle}"` : '';
      const opacity = color.alpha < 1 ? ` fill-opacity="${color.alpha}"` : '';
      for (const line of lines.values()) {
        nodes.push(`<text x="${round(line.left - frameBox.left)}" y="${round(line.top - frameBox.top + ascent)}" font-family="${escapeXml(family)}" font-size="${parseFloat(style.fontSize)}" font-weight="${style.fontWeight}"${italic}${spacing} fill="${color.hex}"${opacity}>${escapeXml(line.words.join(' '))}</text>`);
      }
    };

    const emitBackground = (style, box, radius) => {
      const rx = radius ? ` rx="${round(radius)}"` : '';
      const geometry = `x="${round(box.x)}" y="${round(box.y)}" width="${round(box.width)}" height="${round(box.height)}"${rx}`;
      const gradient = style.backgroundImage !== 'none' ? linearGradient(style.backgroundImage, box) : null;
      const color = parseColor(style.backgroundColor);
      if (gradient) {
        nodes.push(`<rect ${geometry} fill="${gradient}"/>`);
      } else if (color && color.alpha > 0) {
        nodes.push(`<rect ${geometry} fill="${color.hex}"${color.alpha < 1 ? ` fill-opacity="${color.alpha}"` : ''}/>`);
      }
    };

    const emitBorders = (style, box, radius) => {
      const [top, right, bottom, left] = borderSides(style);
      const uniform = [right, bottom, left].every(side =>
        side.width === top.width && side.style === top.style && side.color && top.color && side.color.hex === top.color.hex && side.color.alpha === top.color.alpha);
      if (uniform && top.width > 0) {
        const dash = top.style === 'dashed' ? ` stroke-dasharray="${top.width * 3} ${top.width * 2}"` : '';
        const inset = top.width / 2;
        nodes.push(`<rect x="${round(box.x + inset)}" y="${round(box.y + inset)}" width="${round(box.width - top.width)}" height="${round(box.height - top.width)}" rx="${round(Math.max(radius - inset, 0))}" fill="none" stroke="${top.color.hex}" stroke-opacity="${top.color.alpha}" stroke-width="${top.width}"${dash}/>`);
        return;
      }
      if (top.width > 0) nodes.push(`<rect x="${round(box.x)}" y="${round(box.y)}" width="${round(box.width)}" height="${top.width}" fill="${top.color.hex}" fill-opacity="${top.color.alpha}"/>`);
      if (bottom.width > 0) nodes.push(`<rect x="${round(box.x)}" y="${round(box.y + box.height - bottom.width)}" width="${round(box.width)}" height="${bottom.width}" fill="${bottom.color.hex}" fill-opacity="${bottom.color.alpha}"/>`);
      if (left.width > 0) nodes.push(`<rect x="${round(box.x)}" y="${round(box.y)}" width="${left.width}" height="${round(box.height)}" fill="${left.color.hex}" fill-opacity="${left.color.alpha}"/>`);
      if (right.width > 0) nodes.push(`<rect x="${round(box.x + box.width - right.width)}" y="${round(box.y)}" width="${right.width}" height="${round(box.height)}" fill="${right.color.hex}" fill-opacity="${right.color.alpha}"/>`);
    };

    const visit = element => {
      const style = getComputedStyle(element);
      if (element.hasAttribute('data-export-ignore') || style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return;
      const rect = element.getBoundingClientRect();
      const box = { x: rect.left - frameBox.left, y: rect.top - frameBox.top, width: rect.width, height: rect.height };

      const opacity = Number(style.opacity) < 1 ? ` opacity="${style.opacity}"` : '';
      if (element.localName === 'svg') {
        nodes.push(`<g id="${escapeXml(layerName(element))}"${opacity}>${flattenSvg(element, style, box)}</g>`);
        return;
      }

      nodes.push(`<g id="${escapeXml(layerName(element))}"${opacity}>`);
      const radius = cornerRadius(style, box.width, box.height);
      emitBackground(style, box, radius);
      emitBorders(style, box, radius);

      const clipped = ['hidden', 'clip'].includes(style.overflowX) && ['hidden', 'clip'].includes(style.overflowY);
      if (clipped) {
        const id = `clip-${defs.length}`;
        defs.push(`<clipPath id="${id}"><rect x="${round(box.x)}" y="${round(box.y)}" width="${round(box.width)}" height="${round(box.height)}" rx="${round(radius)}"/></clipPath>`);
        nodes.push(`<g clip-path="url(#${id})">`);
      }

      const children = [...element.childNodes];
      const isAbsolute = node => node.nodeType === 1 && getComputedStyle(node).position === 'absolute';
      for (const child of [...children.filter(node => !isAbsolute(node)), ...children.filter(isAbsolute)]) {
        if (child.nodeType === 3) emitText(child, style);
        else if (child.nodeType === 1) visit(child);
      }

      if (clipped) nodes.push('</g>');
      nodes.push('</g>');
    };

    visit(frame);
    const width = round(frameBox.width);
    const height = round(frameBox.height);
    return `<svg xmlns="${SVG_NS}" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}"><defs>${defs.join('')}</defs>${nodes.join('')}</svg>`;
  };

  window.exportFrames = () => Object.fromEntries(
    [...document.querySelectorAll('[data-frame]')].map(frame => [frame.dataset.frame, exportFrame(frame)])
  );
})();
