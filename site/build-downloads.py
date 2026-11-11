import asyncio
import hashlib
import importlib.util
import json
import shutil
import struct
import zipfile
from pathlib import Path
from string import Template
from tempfile import TemporaryDirectory

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor
from playwright.async_api import async_playwright

SITE = Path(__file__).resolve().parent
WORK = SITE.parent
MATERIALS = WORK / "materials"
LOGOS = WORK / "logo"
FONTS = WORK / "fonts"
OUTPUT = SITE / "downloads"
BRAND = "Бизнес Партнер"
SITE_URL = "https://bashir226.github.io/bp-brandbook/"

FONT_FILES = {
    "PT Serif": ["PTSerif-Regular.ttf", "PTSerif-Italic.ttf", "PTSerif-Bold.ttf", "PTSerif-BoldItalic.ttf", "OFL.txt"],
    "Inter": ["Inter-Regular.ttf", "Inter-Italic.ttf", "Inter-Medium.ttf", "Inter-SemiBold.ttf", "Inter-Bold.ttf", "Inter-BoldItalic.ttf", "OFL.txt"],
}

FONT_FALLBACKS = {
    "Inter": {"alternate": "Arial", "panose": "02000503000000020004", "family": "swiss"},
    "PT Serif": {"alternate": "Times New Roman", "panose": "020A0603040505020204", "family": "roman"},
}

LOGO_SETS = {
    "Полный логотип": [
        (LOGOS / "bp-logo-color.svg", "Цветной.svg"),
        (LOGOS / "bp-logo-color.png", "Цветной.png"),
        (LOGOS / "bp-logo-graphite.svg", "Графитовый.svg"),
        (LOGOS / "bp-logo-graphite.png", "Графитовый.png"),
        (LOGOS / "bp-logo-white.svg", "Белый для тёмного фона.svg"),
        (LOGOS / "bp-logo-white.png", "Белый для тёмного фона.png"),
        (LOGOS / "bp-logo-reversed.svg", "Инверсный для тёмного фона.svg"),
        (LOGOS / "bp-logo-reversed.png", "Инверсный для тёмного фона.png"),
        (MATERIALS / "03_Полный_логотип_ПРОЗРАЧНЫЙ.pdf", "Цветной для печати.pdf"),
        (MATERIALS / "03_Полный_логотип_ПРОЗРАЧНЫЙ_4000.png", "Объёмный 4000 px.png"),
        (MATERIALS / "03_Полный_логотип_ПРОЗРАЧНЫЙ.svg", "Объёмный.svg"),
    ],
    "Знак": [
        (LOGOS / "bp-symbol-color.svg", "Цветной.svg"),
        (LOGOS / "bp-symbol-color.png", "Цветной.png"),
        (LOGOS / "bp-symbol-graphite.svg", "Графитовый.svg"),
        (LOGOS / "bp-symbol-graphite.png", "Графитовый.png"),
        (LOGOS / "bp-symbol-white.svg", "Белый для тёмного фона.svg"),
        (LOGOS / "bp-symbol-white.png", "Белый для тёмного фона.png"),
        (LOGOS / "bp-symbol-reversed.svg", "Инверсный для тёмного фона.svg"),
        (LOGOS / "bp-symbol-reversed.png", "Инверсный для тёмного фона.png"),
        (MATERIALS / "04_Знак_ПРОЗРАЧНЫЙ.pdf", "Цветной для печати.pdf"),
        (MATERIALS / "04_Знак_ПРОЗРАЧНЫЙ_3000.png", "Объёмный 3000 px.png"),
        (MATERIALS / "04_Знак_ПРОЗРАЧНЫЙ.svg", "Объёмный.svg"),
    ],
    "Аватары": [
        (MATERIALS / "05_Аватар_квадрат_1024.png", "Квадрат 1024 px.png"),
        (MATERIALS / "06_Аватар_квадрат_512.png", "Квадрат 512 px.png"),
        (MATERIALS / "07_Аватар_круг_1024.png", "Круг 1024 px.png"),
        (MATERIALS / "08_Аватар_круг_512.png", "Круг 512 px.png"),
    ],
}


def load_palette_module():
    specification = importlib.util.spec_from_file_location("palette_data", SITE / "palette-data.py")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def rgb(hex_value):
    return [int(hex_value[index:index + 2], 16) for index in (1, 3, 5)]


def color_groups(palette):
    groups = [("Основные цвета", [(color["name"], color["hex"]) for color in palette["tokens"]["brand"]])]
    for color in palette["tokens"]["brand"]:
        groups.append((f"Оттенки: {color['name']}", [(f"{color['name']} {shade['percent']}%", shade["hex"]) for shade in palette["shades"][color["token"]]]))
    groups.append(("Фоны", [(color["name"], color["hex"]) for color in palette["tokens"]["neutral"]]))
    groups.append(("Подписи", [(color["name"], color["hex"]) for color in palette["tokens"]["caption"]]))
    accents = {color["token"]: color for color in palette["tokens"]["accent"]}
    buttons = []
    for button in palette["buttons"]:
        base = accents[button["token"]]
        buttons += [(base["name"], base["hex"]), (f"{base['name']}, наведение", button["hover"]), (f"{base['name']}, нажатие", button["active"])]
    groups.append(("Кнопки", buttons))
    return groups


def ase_text(text):
    return struct.pack(">H", len(text) + 1) + (text + "\0").encode("utf-16-be")


def ase_block(kind, payload):
    return struct.pack(">HI", kind, len(payload)) + payload


def write_ase(path, groups):
    blocks = []
    for title, colors in groups:
        blocks.append(ase_block(0xC001, ase_text(title)))
        for name, hex_value in colors:
            red, green, blue = rgb(hex_value)
            blocks.append(ase_block(0x0001, ase_text(f"{name} {hex_value}") + b"RGB " + struct.pack(">fffH", red / 255, green / 255, blue / 255, 2)))
        blocks.append(ase_block(0xC002, b""))
    path.write_bytes(b"ASEF" + struct.pack(">HHI", 1, 0, len(blocks)) + b"".join(blocks))


def write_gpl(path, groups):
    lines = ["GIMP Palette", f"Name: {BRAND}", "Columns: 6"]
    for title, colors in groups:
        for name, hex_value in colors:
            red, green, blue = rgb(hex_value)
            lines.append(f"{red:3d} {green:3d} {blue:3d}\t{title}: {name} {hex_value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_css(path, palette, gradient_css):
    lines = [":root {"]
    for group in ("brand", "neutral", "caption", "accent"):
        for color in palette["tokens"][group]:
            lines.append(f"  --bp-{color['token']}: {color['hex']};")
            for shade in palette["shades"].get(color["token"], []):
                lines.append(f"  --bp-{color['token']}-{shade['percent']}: {shade['hex']};")
    for button in palette["buttons"]:
        accent = next(color for color in palette["tokens"]["accent"] if color["token"] == button["token"])
        lines += [
            f"  --bp-button-{button['id']}: {accent['hex']};",
            f"  --bp-button-{button['id']}-hover: {button['hover']};",
            f"  --bp-button-{button['id']}-active: {button['active']};",
            f"  --bp-button-{button['id']}-text: {button['foreground']};",
        ]
    for gradient in palette["gradients"]:
        lines.append(f"  --bp-{gradient['token']}: {gradient_css(gradient)};")
    lines += ["  --bp-font-heading: \"PT Serif\", Georgia, serif;", "  --bp-font-text: \"Inter\", Arial, sans-serif;", "}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(path, palette):
    payload = {
        "brand": BRAND,
        "colors": {
            color["token"]: {"name": color["name"], "group": group, "hex": color["hex"], "rgb": rgb(color["hex"]), "source": color["source"], "use": color["use"]}
            for group in ("brand", "neutral", "caption", "accent")
            for color in palette["tokens"][group]
        },
        "shades": {token: [{"percent": shade["percent"], "hex": shade["hex"], "rgb": rgb(shade["hex"])} for shade in shades] for token, shades in palette["shades"].items()},
        "buttons": palette["buttons"],
        "gradients": palette["gradients"],
        "logoColors": palette["logoColors"],
        "fonts": {"heading": "PT Serif", "text": "Inter"},
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_office_colors(path, palette):
    colors = {color["token"]: color["hex"][1:] for group in palette["tokens"].values() for color in group}
    slots = [
        ("dk1", "graphite-900"), ("lt1", "white"), ("dk2", "graphite-700"), ("lt2", "stone-50"),
        ("accent1", "red-700"), ("accent2", "red-600"), ("accent3", "stone-500"), ("accent4", "steel-400"),
        ("accent5", "red-500"), ("accent6", "slate-500"), ("hlink", "red-700"), ("folHlink", "graphite-700"),
    ]
    body = "".join(f"<a:{slot}><a:srgbClr val=\"{colors[token]}\"/></a:{slot}>" for slot, token in slots)
    path.write_text(f"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<a:clrScheme xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" name=\"{BRAND}\">{body}</a:clrScheme>\n", encoding="utf-8")


def write_office_fonts(path):
    path.write_text(
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n"
        f"<a:fontScheme xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" name=\"{BRAND}\">"
        "<a:majorFont><a:latin typeface=\"PT Serif\"/><a:ea typeface=\"\"/><a:cs typeface=\"\"/></a:majorFont>"
        "<a:minorFont><a:latin typeface=\"Inter\"/><a:ea typeface=\"\"/><a:cs typeface=\"\"/></a:minorFont>"
        "</a:fontScheme>\n",
        encoding="utf-8",
    )


def set_run_font(run, family, size, color, bold=False):
    run.font.name = family
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)
    fonts = run._element.get_or_add_rPr().get_or_add_rFonts()
    for attribute in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fonts.set(qn(attribute), family)


def add_paragraph(container, text, family="Inter", size=10.5, color="1F2021", bold=False, align=None, after=6):
    paragraph = container.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = 1.35
    if align is not None:
        paragraph.alignment = align
    lines = text.split("\n")
    for index, line in enumerate(lines):
        run = paragraph.add_run(line)
        set_run_font(run, family, size, color, bold)
        if index < len(lines) - 1:
            run.add_break()
    return paragraph


def bottom_border(paragraph, color):
    properties = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    for key, value in (("w:val", "single"), ("w:sz", "8"), ("w:space", "8"), ("w:color", color)):
        bottom.set(qn(key), value)
    borders.append(bottom)
    properties.append(borders)


def write_letterhead(path):
    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Mm(210), Mm(297)
    section.top_margin, section.bottom_margin = Mm(42), Mm(30)
    section.left_margin, section.right_margin = Mm(25), Mm(18)
    section.header_distance, section.footer_distance = Mm(12), Mm(10)
    normal = document.styles["Normal"]
    normal.font.name = "Inter"
    normal.font.size = Pt(10.5)
    normal.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), "Inter")
    header = section.header.paragraphs[0]
    header.add_run().add_picture(str(LOGOS / "bp-logo-color.png"), width=Mm(46))
    bottom_border(header, "B8130E")
    footer = section.footer.paragraphs[0]
    footer.paragraph_format.line_spacing = 1.3
    for index, line in enumerate(["ООО «Бизнес Партнер», 173001, Великий Новгород, ул. Великая, д. 16, стр. 1", "+7 (8162) 60-33-40, info@bp-nov.ru"]):
        run = footer.add_run(line)
        set_run_font(run, "Inter", 8, "495054")
        if index == 0:
            run.add_break()
    add_paragraph(document, "Исх. № ______ от «___» ____________ 20___ г.", size=9.5, color="495054", after=18)
    add_paragraph(document, "Должность получателя\nНазвание организации\nФамилия И. О.", align=WD_ALIGN_PARAGRAPH.RIGHT, after=28)
    add_paragraph(document, "Тема письма", family="PT Serif", size=15, bold=True, after=12)
    add_paragraph(document, "Текст письма.", after=36)
    add_paragraph(document, "С уважением,\nДолжность\nФамилия И. О.", after=0)
    document.core_properties.title = f"Бланк письма {BRAND}"
    document.core_properties.author = BRAND
    document.save(path)
    declare_font_fallbacks(path)


def declare_font_fallbacks(path):
    with zipfile.ZipFile(path) as source:
        parts = {name: source.read(name) for name in source.namelist()}
    declarations = "".join(
        f"<w:font w:name=\"{name}\"><w:altName w:val=\"{font['alternate']}\"/><w:panose1 w:val=\"{font['panose']}\"/><w:charset w:val=\"CC\"/><w:family w:val=\"{font['family']}\"/><w:pitch w:val=\"variable\"/></w:font>"
        for name, font in FONT_FALLBACKS.items()
    )
    parts["word/fontTable.xml"] = parts["word/fontTable.xml"].decode("utf-8").replace("</w:fonts>", declarations + "</w:fonts>").encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as target:
        target.writestr("[Content_Types].xml", parts.pop("[Content_Types].xml"))
        for name, data in parts.items():
            target.writestr(name, data)


INSTRUCTIONS = {
    "documents": """Комплект для документов и презентаций «Бизнес Партнер»

1. Шрифты. Откройте папку «Шрифты», выделите все файлы .ttf, нажмите правой кнопкой и выберите «Установить для всех пользователей». Перезапустите Word и PowerPoint.

2. Цвета и шрифты в Word и PowerPoint. Нажмите Win + R, вставьте строку
%APPDATA%\\Microsoft\\Templates\\Document Themes
и нажмите Enter. Скопируйте файл из папки «Тема Office\\Theme Colors» в папку Theme Colors, а файл из «Тема Office\\Theme Fonts» — в папку Theme Fonts. Если таких папок нет, создайте их с этими же названиями.
В Word: «Конструктор» → «Цвета» и «Шрифты» → «Бизнес Партнер».
В PowerPoint: «Конструктор» → «Варианты» → «Цвета» и «Шрифты» → «Бизнес Партнер».
После этого фирменные цвета и их светлые оттенки появятся в палитре, а заголовки и текст получат нужные шрифты.

3. Бланк письма. Откройте «Бланк письма.docx», замените поля на свои данные и сохраните копию. Чтобы бланк всегда был под рукой, сохраните его как шаблон: «Файл» → «Сохранить как» → «Шаблон Word». Логотип в шапке и реквизиты в подвале менять не нужно.

4. Логотипы. PNG с прозрачным фоном: цветной — для светлых фонов, белый и инверсный — для тёмных. Не растягивайте и не перекрашивайте логотип.
""",
    "design": """Комплект для рекламы и макетов «Бизнес Партнер»

1. Шрифты. Установите все файлы .ttf из папки «Шрифты»: правая кнопка → «Установить для всех пользователей».

2. Палитра в Adobe Illustrator, Photoshop и InDesign: откройте панель «Образцы» (Swatches) → меню панели → «Открыть библиотеку образцов» / «Загрузить образцы» → выберите файл «Палитра Adobe.ase». Цвета разложены по группам: основные, оттенки каждого цвета, фоны, подписи, кнопки.

3. GIMP, Inkscape, Krita: импортируйте «Палитра GIMP и Inkscape.gpl» в окне палитр.

4. Figma: скопируйте HEX-коды с картинки «Палитра.png» или с сайта брендбука и сохраните их как стили цвета.

5. Печать. В файлах указаны цвета для экрана (RGB, HEX). Перед печатью передайте их типографии: CMYK подбирается под конкретную бумагу и оборудование.

6. Логотипы. SVG — для экрана и редактирования, PDF — для печати. Объёмные версии — только для презентационных материалов.
""",
    "web": """Комплект для сайта и соцсетей «Бизнес Партнер»

1. Цвета. Подключите «brand-colors.css» на сайте и используйте переменные, например:
color: var(--bp-graphite-900);
background: var(--bp-red-700);
Оттенки доступны с процентом в имени: var(--bp-red-700-18).
Тот же набор в машинном виде — «brand-colors.json».

2. Шрифты на сайте подключаются из Google Fonts:
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=PT+Serif:wght@400;700&display=swap">
Заголовки — PT Serif, текст и кнопки — Inter.

3. Кнопки. Используйте одну тему для одного действия. Цвет текста и состояния наведения и нажатия указаны в CSS: --bp-button-green, --bp-button-green-hover, --bp-button-green-active, --bp-button-green-text.

4. Логотипы — SVG для сайта, PNG для соцсетей. Аватары — квадрат и круг 1024 и 512 px.
""",
}


def add_tree(archive, source, target):
    if source.is_dir():
        for item in sorted(source.rglob("*")):
            if item.is_file():
                archive.write(item, f"{target}/{item.relative_to(source).as_posix()}")
    else:
        archive.write(source, target)


def write_zip(path, entries, texts=None):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, text in (texts or {}).items():
            archive.writestr(name, text.replace("\n", "\r\n").encode("utf-8-sig"))
        for source, target in entries:
            add_tree(archive, source, target)


async def capture_png(palette):
    paths = {"palette": OUTPUT / "bp-palette.png"}
    paths.update({color["token"]: OUTPUT / f"bp-shades-{color['token']}.png" for color in palette["tokens"]["brand"]})
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        try:
            page = await browser.new_page(viewport={"width": 1440, "height": 1200}, device_scale_factor=2)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            await page.goto((SITE / "index.html").as_uri(), wait_until="networkidle")
            await page.add_style_tag(content=(
                ".book-downloads { display: none !important; }"
                " #palette-catalog .palette-group:first-child { padding: 48px; background: #FFFFFF; }"
                " .color-book[data-capture] { grid-template-columns: 300px; }"
                " .color-book[data-capture] .color-book__column:not([data-capture]) { display: none; }"
                " .color-book__column[data-capture] { padding: 32px; background: #FFFFFF; }"
            ))
            await page.evaluate("document.fonts.ready")
            if errors:
                raise RuntimeError("Ошибка страницы при подготовке PNG:\n" + "\n".join(errors))
            await page.locator("#palette-catalog .palette-group").first.screenshot(path=str(paths["palette"]), animations="disabled")
            for color in palette["tokens"]["brand"]:
                await page.evaluate("""token => {
                    const book = document.querySelector('.color-book');
                    book.dataset.capture = '';
                    book.querySelectorAll('.color-book__column').forEach(column => column.toggleAttribute('data-capture', column.dataset.token === token));
                }""", color["token"])
                await page.locator(f".color-book__column[data-token=\"{color['token']}\"]").screenshot(path=str(paths[color["token"]]), animations="disabled")
        finally:
            await browser.close()


async def build_guide(palette):
    with TemporaryDirectory() as directory:
        temporary = Path(directory)
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            try:
                page = await browser.new_page(viewport={"width": 1440, "height": 1200}, device_scale_factor=2)
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                await page.goto((SITE / "index.html").as_uri(), wait_until="networkidle")
                await page.evaluate("document.fonts.ready")
                if errors:
                    raise RuntimeError("Ошибка страницы при подготовке инструкции:\n" + "\n".join(errors))
                shots = {"shot_tasks": "#download-tasks", "shot_logo_versions": "#logo .grid--4"}
                for name, selector in shots.items():
                    await page.locator(selector).first.screenshot(path=str(temporary / f"{name}.png"), animations="disabled")
                values = {name: (temporary / f"{name}.png").as_uri() for name in shots}
                values.update({
                    "inter_regular": (FONTS / "Inter" / "Inter-Regular.ttf").as_uri(),
                    "inter_semibold": (FONTS / "Inter" / "Inter-SemiBold.ttf").as_uri(),
                    "pt_regular": (FONTS / "PT Serif" / "PTSerif-Regular.ttf").as_uri(),
                    "logo_reversed": (LOGOS / "bp-logo-reversed.png").as_uri(),
                    "site_url": SITE_URL,
                    "cover_colors": "".join(f"<span style=\"background:{color['hex']}\"></span>" for color in palette["tokens"]["brand"]),
                })
                document = temporary / "guide.html"
                document.write_text(Template((SITE / "guide.html").read_text(encoding="utf-8")).substitute(values), encoding="utf-8")
                guide = await browser.new_page()
                await guide.goto(document.as_uri(), wait_until="networkidle")
                await guide.evaluate("document.fonts.ready")
                failed = await guide.evaluate("[...document.fonts].filter(font => font.status === 'error').map(font => font.family)")
                if failed:
                    raise RuntimeError(f"Шрифты инструкции не загружены: {failed}")
                await guide.pdf(
                    path=str(OUTPUT / "bp-guide.pdf"),
                    prefer_css_page_size=True,
                    print_background=True,
                    display_header_footer=True,
                    header_template="<span></span>",
                    footer_template="<div style=\"width:100%;margin:0 15mm;display:flex;justify-content:space-between;font-family:Arial,sans-serif;font-size:7px;color:#495054\"><span>Бизнес Партнер. Как пользоваться брендбуком</span><span>Страница <span class=\"pageNumber\"></span> из <span class=\"totalPages\"></span></span></div>",
                )
            finally:
                await browser.close()


def file_entry(path, name, title, format_label):
    version = hashlib.sha256(path.read_bytes()).hexdigest()[:10] if path.exists() else "0"
    return {"path": f"downloads/{path.name}?v={version}", "name": name, "title": title, "format": format_label, "size": path.stat().st_size if path.exists() else 0}


def write_manifest(palette, entries):
    manifest = {
        "tasks": [
            {
                "id": "documents",
                "title": "Документы и презентации",
                "audience": "Word, PowerPoint, коммерческие предложения и письма",
                "items": ["Тема цветов и шрифтов для Word и PowerPoint", "Шрифты PT Serif и Inter", "Бланк письма Word", "Логотипы PNG и карточка палитры", "Инструкция по установке"],
                "file": entries["kit-documents"],
            },
            {
                "id": "design",
                "title": "Реклама и макеты",
                "audience": "Illustrator, Photoshop, InDesign, Figma, печать",
                "items": ["Палитра ASE со всеми оттенками", "Палитра для GIMP и Inkscape", "Логотипы SVG и PDF", "Шрифты PT Serif и Inter", "PNG-шкалы оттенков и инструкция"],
                "file": entries["kit-design"],
            },
            {
                "id": "web",
                "title": "Сайт и соцсети",
                "audience": "Разработчики, SMM-специалисты, подрядчики",
                "items": ["CSS-переменные цветов, оттенков и кнопок", "Палитра в JSON", "Логотипы SVG и PNG", "Аватары для соцсетей", "Подключение шрифтов"],
                "file": entries["kit-web"],
            },
        ],
        "groups": [
            {"id": "files-guide", "title": "Инструкция для сотрудников", "files": [entries["guide"]]},
            {"id": "files-colors", "title": "Цвета и оттенки", "files": [entries[key] for key in ("palette-png", "ase", "gpl", "css", "json")]},
            {"id": "files-office", "title": "Word и PowerPoint", "files": [entries[key] for key in ("office-colors", "office-fonts", "letterhead")]},
            {"id": "files-fonts", "title": "Шрифты", "files": [entries[key] for key in ("font-pt-serif", "font-inter")]},
            {"id": "files-logos", "title": "Логотипы", "files": [entries["logos"]]},
        ],
        "shades": {color["token"]: {"ase": entries[f"ase-{color['token']}"], "png": entries[f"png-{color['token']}"]} for color in palette["tokens"]["brand"]},
    }
    (SITE / "downloads-data.js").write_text("window.brandDownloads = " + json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def main():
    module = load_palette_module()
    module.main()
    palette = module.load_palette()
    groups = color_groups(palette)
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    write_ase(OUTPUT / "bp-colors.ase", groups)
    write_gpl(OUTPUT / "bp-colors.gpl", groups)
    write_css(OUTPUT / "brand-colors.css", palette, module.gradient_css)
    write_json(OUTPUT / "brand-colors.json", palette)
    write_office_colors(OUTPUT / "bp-office-colors.xml", palette)
    write_office_fonts(OUTPUT / "bp-office-fonts.xml")
    write_letterhead(OUTPUT / "bp-letterhead.docx")
    brand = {color["token"]: color for color in palette["tokens"]["brand"]}
    for token, color in brand.items():
        write_ase(OUTPUT / f"bp-shades-{token}.ase", [(f"{color['name']} и оттенки", [(color["name"], color["hex"])] + [(f"{color['name']} {shade['percent']}%", shade["hex"]) for shade in palette["shades"][token]])])
    for family, files in FONT_FILES.items():
        write_zip(OUTPUT / f"bp-font-{family.lower().replace(' ', '-')}.zip", [(FONTS / family / name, f"{family}/{name}") for name in files])
    logo_entries = [(source, f"Логотипы/{folder}/{name}") for folder, items in LOGO_SETS.items() for source, name in items]
    write_zip(OUTPUT / "bp-logos.zip", logo_entries)

    def entries_map():
        result = {
            "palette-png": file_entry(OUTPUT / "bp-palette.png", "Бизнес Партнер — палитра.png", "Карточка палитры", "PNG"),
            "ase": file_entry(OUTPUT / "bp-colors.ase", "Бизнес Партнер — палитра Adobe.ase", "Палитра для Adobe Illustrator, Photoshop, InDesign", "ASE"),
            "gpl": file_entry(OUTPUT / "bp-colors.gpl", "Бизнес Партнер — палитра.gpl", "Палитра для GIMP, Inkscape, Krita", "GPL"),
            "css": file_entry(OUTPUT / "brand-colors.css", "brand-colors.css", "CSS-переменные для сайта", "CSS"),
            "json": file_entry(OUTPUT / "brand-colors.json", "brand-colors.json", "Палитра для разработчиков", "JSON"),
            "office-colors": file_entry(OUTPUT / "bp-office-colors.xml", "Бизнес Партнер — цвета.xml", "Тема цветов Office", "XML"),
            "office-fonts": file_entry(OUTPUT / "bp-office-fonts.xml", "Бизнес Партнер — шрифты.xml", "Тема шрифтов Office", "XML"),
            "letterhead": file_entry(OUTPUT / "bp-letterhead.docx", "Бизнес Партнер — бланк письма.docx", "Бланк письма", "DOCX"),
            "font-pt-serif": file_entry(OUTPUT / "bp-font-pt-serif.zip", "PT Serif.zip", "PT Serif — заголовки", "TTF, ZIP"),
            "font-inter": file_entry(OUTPUT / "bp-font-inter.zip", "Inter.zip", "Inter — текст и интерфейс", "TTF, ZIP"),
            "logos": file_entry(OUTPUT / "bp-logos.zip", "Бизнес Партнер — логотипы.zip", "Полный логотип, знак, аватары", "SVG, PNG, PDF, ZIP"),
            "kit-documents": file_entry(OUTPUT / "bp-kit-documents.zip", "Бизнес Партнер — документы и презентации.zip", "Документы и презентации", "ZIP"),
            "kit-design": file_entry(OUTPUT / "bp-kit-design.zip", "Бизнес Партнер — реклама и макеты.zip", "Реклама и макеты", "ZIP"),
            "kit-web": file_entry(OUTPUT / "bp-kit-web.zip", "Бизнес Партнер — сайт и соцсети.zip", "Сайт и соцсети", "ZIP"),
            "guide": file_entry(OUTPUT / "bp-guide.pdf", "Бизнес Партнер — инструкция для сотрудников.pdf", "Как пользоваться брендбуком", "PDF"),
        }
        for token, color in brand.items():
            result[f"ase-{token}"] = file_entry(OUTPUT / f"bp-shades-{token}.ase", f"{color['name']} — оттенки.ase", color["name"], "ASE")
            result[f"png-{token}"] = file_entry(OUTPUT / f"bp-shades-{token}.png", f"{color['name']} — оттенки.png", color["name"], "PNG")
        return result

    write_manifest(palette, entries_map())
    asyncio.run(capture_png(palette))
    fonts = [(FONTS / family, f"Шрифты/{family}") for family in FONT_FILES]
    shade_png = [(OUTPUT / f"bp-shades-{token}.png", f"Оттенки/{color['name']}.png") for token, color in brand.items()]
    write_zip(OUTPUT / "bp-kit-documents.zip", [
        (OUTPUT / "bp-office-colors.xml", "Тема Office/Theme Colors/Бизнес Партнер.xml"),
        (OUTPUT / "bp-office-fonts.xml", "Тема Office/Theme Fonts/Бизнес Партнер.xml"),
        (OUTPUT / "bp-letterhead.docx", "Бланк письма.docx"),
        (OUTPUT / "bp-palette.png", "Палитра.png"),
        (LOGOS / "bp-logo-color.png", "Логотипы/Полный логотип, цветной.png"),
        (LOGOS / "bp-logo-white.png", "Логотипы/Полный логотип, белый.png"),
        (LOGOS / "bp-logo-reversed.png", "Логотипы/Полный логотип, инверсный.png"),
        (LOGOS / "bp-symbol-color.png", "Логотипы/Знак, цветной.png"),
        (LOGOS / "bp-symbol-white.png", "Логотипы/Знак, белый.png"),
        *fonts,
    ], {"Как установить.txt": INSTRUCTIONS["documents"]})
    write_zip(OUTPUT / "bp-kit-design.zip", [
        (OUTPUT / "bp-colors.ase", "Палитра Adobe.ase"),
        (OUTPUT / "bp-colors.gpl", "Палитра GIMP и Inkscape.gpl"),
        (OUTPUT / "bp-palette.png", "Палитра.png"),
        *shade_png,
        *[(source, f"Логотипы/{folder}/{name}") for folder, items in LOGO_SETS.items() if folder != "Аватары" for source, name in items if source.suffix in (".svg", ".pdf")],
        *fonts,
    ], {"Как установить.txt": INSTRUCTIONS["design"]})
    write_zip(OUTPUT / "bp-kit-web.zip", [
        (OUTPUT / "brand-colors.css", "brand-colors.css"),
        (OUTPUT / "brand-colors.json", "brand-colors.json"),
        (OUTPUT / "bp-palette.png", "Палитра.png"),
        *[(source, f"Логотипы/{folder}/{name}") for folder, items in LOGO_SETS.items() for source, name in items if source.suffix in (".svg", ".png") and "Объёмный" not in name],
    ], {"Как подключить.txt": INSTRUCTIONS["web"]})
    write_manifest(palette, entries_map())
    asyncio.run(build_guide(palette))
    write_manifest(palette, entries_map())
    for path in sorted(OUTPUT.iterdir()):
        print(f"{path.name}: {path.stat().st_size} байт")


if __name__ == "__main__":
    main()
