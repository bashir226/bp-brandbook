import colorsys
import json
import math
from pathlib import Path


def gradient_css(gradient):
    stops = ",".join(f"{stop['hex']} {stop['position']}%" for stop in gradient["stops"])
    return f"linear-gradient({gradient['angle']}deg,{stops})"


def channels(hex_value):
    return [int(hex_value[index:index + 2], 16) for index in (1, 3, 5)]


def to_hex(values):
    return "#" + "".join(f"{value:02X}" for value in values)


def mix_with_white(hex_value, percent):
    amount = percent / 100
    return to_hex(math.floor(255 * (1 - amount) + channel * amount + 0.5) for channel in channels(hex_value))


def darken(hex_value, factor):
    return to_hex(math.floor(channel * factor + 0.5) for channel in channels(hex_value))


def luminance(hex_value):
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in (channel / 255 for channel in channels(hex_value))]
    return linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722


def contrast(foreground, background):
    lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def describe(color):
    red, green, blue = channels(color["hex"])
    hue, lightness, saturation = colorsys.rgb_to_hls(red / 255, green / 255, blue / 255)
    color["rgb"] = [red, green, blue]
    color["hsl"] = [round(hue * 360, 2), round(saturation * 100, 2), round(lightness * 100, 2)]


def load_palette():
    directory = Path(__file__).resolve().parent
    palette = json.loads((directory.parent / "palette.json").read_text(encoding="utf-8"))
    tokens = palette["tokens"]
    tints = {(color["shadeOf"], color["percent"]): color for color in tokens["tint"]}
    palette["shades"] = {}
    for color in tokens["brand"]:
        overrides = palette["shadeOverrides"].get(color["token"], {})
        palette["shades"][color["token"]] = [
            {
                "percent": percent,
                "hex": overrides.get(str(percent), mix_with_white(color["hex"], percent)),
                "token": tints[(color["token"], percent)]["token"] if (color["token"], percent) in tints else None,
                "custom": str(percent) in overrides,
            }
            for percent in palette["shadePercents"]
        ]
    for tint in tokens["tint"]:
        tint["hex"] = next(shade["hex"] for shade in palette["shades"][tint["shadeOf"]] if shade["percent"] == tint["percent"])
    for group in tokens.values():
        for color in group:
            describe(color)
    hexes = {color["token"]: color["hex"] for group in tokens.values() for color in group}
    states = palette["buttonStates"]
    for button in palette["buttons"]:
        button["hover"] = darken(hexes[button["token"]], states["hover"]["factor"])
        button["active"] = darken(hexes[button["token"]], states["active"]["factor"])
    for gradient in palette["gradients"]:
        for stop in gradient["stops"]:
            if "token" in stop:
                stop["hex"] = hexes[stop["token"]]
    for pair in palette["contrasts"]:
        ratio = contrast(hexes.get(pair["foreground"], pair["foreground"]), hexes.get(pair["background"], pair["background"]))
        pair.update({"ratio": ratio, "normalTextAA": ratio >= 4.5, "largeTextAA": ratio >= 3})
    return palette


def main():
    directory = Path(__file__).resolve().parent
    palette = load_palette()
    variables = {}
    for group in palette["tokens"].values():
        for color in group:
            variables[color["token"]] = color["hex"]
    for button in palette["buttons"]:
        prefix = f"button-{button['id']}"
        variables[prefix] = variables[button["token"]]
        variables[f"{prefix}-hover"] = button["hover"]
        variables[f"{prefix}-active"] = button["active"]
        variables[f"{prefix}-text"] = button["foreground"]
    for gradient in palette["gradients"]:
        variables[gradient["token"]] = gradient_css(gradient)
    css = ":root{" + "".join(f"--{name}:{value};" for name, value in variables.items()) + "}"
    payload = json.dumps(palette, ensure_ascii=False, separators=(",", ":"))
    stylesheet = json.dumps(css, ensure_ascii=False)
    javascript = (
        "(() => {\n"
        f"  window.brandPalette = {payload};\n"
        "  const style = document.createElement('style');\n"
        "  style.id = 'brand-palette-variables';\n"
        f"  style.textContent = {stylesheet};\n"
        "  document.head.append(style);\n"
        "})();\n"
    )
    (directory / "palette-data.js").write_text(javascript, encoding="utf-8")


if __name__ == "__main__":
    main()
