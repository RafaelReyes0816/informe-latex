import shutil
from pathlib import Path


def collect_image_urls(tokens):
    urls = []
    for token in tokens:
        if token.get("type") == "image":
            url = token.get("attrs", {}).get("url", "")
            if url:
                urls.append(url)
        for key in ("children",):
            if key in token and isinstance(token[key], list):
                urls.extend(collect_image_urls(token[key]))
    return urls


def handle_images(tokens, output_dir="."):
    output_path = Path(output_dir).resolve()
    figures_dir = output_path / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    urls = collect_image_urls(tokens)
    image_map = {}

    for url in urls:
        src = Path(url)
        if src.is_file():
            dst = figures_dir / src.name
            if dst.exists():
                dst = figures_dir / f"{src.stem}_{hash(str(src.resolve())) & 0xFFFFFFFF}{src.suffix}"
            shutil.copy2(src, dst)
            image_map[url] = dst.name
        else:
            image_map[url] = url

    return image_map
