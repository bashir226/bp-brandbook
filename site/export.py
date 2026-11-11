import argparse
import asyncio
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pymupdf
from playwright.async_api import async_playwright

from assemble_site import assemble


BASE = Path(__file__).resolve().parent.parent
OVERVIEW = ("01-Hero", "04-Colors", "07-ToneOfVoice")


def save_pdf(document, path):
    with TemporaryDirectory(dir=path.parent) as directory:
        temporary = Path(directory) / "export.pdf"
        document.save(temporary, garbage=4, deflate=True)
        temporary.replace(path)
    print(path)


def save_site(directory):
    assemble(directory)
    archive = shutil.make_archive(str(directory), "zip", root_dir=directory.parent, base_dir=directory.name)
    print(directory)
    print(archive)


async def export_layout(browser, url, layout, width, filename, output):
    context = await browser.new_context(
        viewport={"width": width, "height": 1000},
        device_scale_factor=2,
        locale="ru-RU",
        reduced_motion="reduce",
    )
    document = pymupdf.open()
    overview = pymupdf.open()
    try:
        page = await context.new_page()
        runtime_errors = []
        page.on("pageerror", lambda error: runtime_errors.append(str(error)))
        page.on(
            "requestfailed",
            lambda request: runtime_errors.append(f"Шрифт не загружен: {request.url}: {request.failure}")
            if request.resource_type == "font"
            else None,
        )
        response = await page.goto(url, wait_until="networkidle")
        if response is None or not response.ok:
            raise RuntimeError(f"Страница не загружена: {url}")
        await page.add_style_tag(content="[data-export-ignore] { display: none !important; }")
        await page.add_script_tag(path=str(Path(__file__).with_name("export.js")))
        await page.evaluate("""async () => {
            await document.fonts.ready;
            if (!window.brandPalette || !document.querySelector('#palette-catalog')?.children.length) {
                throw new Error('Палитра не готова: отсутствуют данные или каталог цветов');
            }
            const failedFonts = [...document.fonts].filter(font => font.status === 'error');
            if (failedFonts.length) {
                throw new Error(`Не загружены шрифты: ${failedFonts.map(font => font.family).join(', ')}`);
            }
            await Promise.all([...document.images].map(image => image.decode()));
            await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        }""")
        await page.mouse.move(0, 0)
        await page.evaluate("window.scrollTo(0, 0)")
        frames = await page.evaluate("window.exportFrames()")
        if runtime_errors:
            raise RuntimeError("Ошибка страницы при экспорте:\n" + "\n".join(runtime_errors))
        if not frames:
            raise RuntimeError("На странице нет фреймов для экспорта")
        if layout == "desktop" and any(name not in frames for name in OVERVIEW):
            raise RuntimeError("Не найдены все три фрейма для Обзор.pdf")
        svg_directory = BASE / "figma" / layout
        preview_directory = BASE / "figma" / "preview" / layout
        svg_directory.mkdir(parents=True, exist_ok=True)
        preview_directory.mkdir(parents=True, exist_ok=True)
        for name, svg in frames.items():
            if Path(name).name != name or any(char in name for char in '<>:"/\\|?*'):
                raise RuntimeError(f"Недопустимое имя фрейма: {name}")
            frame = page.locator(f'[data-frame="{name}"]')
            box = await frame.bounding_box()
            if box is None or box["width"] <= 0 or box["height"] <= 0:
                raise RuntimeError(f"Фрейм не виден: {name}")
            (svg_directory / f"{name}.svg").write_text(svg, encoding="utf-8")
            await page.mouse.move(0, 0)
            image = await frame.screenshot(
                path=str(preview_directory / f"{name}.png"),
                animations="disabled",
                caret="hide",
                scale="device",
            )
            pdf_page = document.new_page(width=box["width"] * 0.75, height=box["height"] * 0.75)
            pdf_page.insert_image(pdf_page.rect, stream=image)
            if layout == "desktop" and name in OVERVIEW:
                overview.insert_pdf(document, from_page=document.page_count - 1, to_page=document.page_count - 1)
        save_pdf(document, output / filename)
        if layout == "desktop":
            save_pdf(overview, output / "Обзор.pdf")
        print(f"{layout}: {len(frames)} SVG и PNG, масштаб PNG 2×; PDF из PNG")
    finally:
        overview.close()
        document.close()
        await context.close()


async def main():
    parser = argparse.ArgumentParser(description="Экспорт брендбука в SVG, PNG и PDF из PNG высокого разрешения")
    parser.add_argument("url", nargs="?", default="http://127.0.0.1:8765/index.html")
    parser.add_argument("--pdf-dir", type=Path, default=BASE / "for-client" / "Палитра_клиента")
    arguments = parser.parse_args()
    arguments.pdf_dir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        try:
            await export_layout(browser, arguments.url, "desktop", 1440, "Брендбук_компьютер.pdf", arguments.pdf_dir)
            await export_layout(browser, arguments.url, "mobile", 390, "Брендбук_телефон.pdf", arguments.pdf_dir)
            save_site(arguments.pdf_dir / "Сайт_брендбука")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
