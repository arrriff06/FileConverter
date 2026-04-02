import os
import time
from PIL import Image, ImageDraw, ImageFont


def _output_name(prefix: str, ext: str):
    return f"{prefix}_{int(time.time())}.{ext.lower()}"


def resize_image(image_path, width, height, output_folder):
    if not os.path.exists(image_path):
        raise Exception("Image file not found.")

    width = int(width)
    height = int(height)
    if width <= 0 or height <= 0:
        raise Exception("Width and height must be greater than 0.")

    os.makedirs(output_folder, exist_ok=True)
    with Image.open(image_path) as img:
        resized = img.resize((width, height))
        ext = (img.format or "PNG").lower()
        output_path = os.path.join(output_folder, _output_name("resized", ext))
        resized.save(output_path)
    return output_path


def compress_image(image_path, quality, output_folder):
    if not os.path.exists(image_path):
        raise Exception("Image file not found.")

    quality = int(quality)
    quality = max(1, min(95, quality))

    os.makedirs(output_folder, exist_ok=True)
    with Image.open(image_path) as img:
        # save as jpeg/webp/png depending on source
        ext = (img.format or "JPEG").lower()
        if ext not in ["jpeg", "jpg", "png", "webp"]:
            ext = "jpg"

        # JPEG doesn't support alpha
        if ext in ["jpg", "jpeg"] and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        output_path = os.path.join(output_folder, _output_name("compressed", ext))
        save_kwargs = {}
        if ext in ["jpg", "jpeg", "webp"]:
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True

        img.save(output_path, **save_kwargs)
    return output_path


def crop_image(image_path, x, y, w, h, output_folder):
    if not os.path.exists(image_path):
        raise Exception("Image file not found.")

    x, y, w, h = int(x), int(y), int(w), int(h)
    if w <= 0 or h <= 0:
        raise Exception("Crop width/height must be > 0.")

    os.makedirs(output_folder, exist_ok=True)
    with Image.open(image_path) as img:
        img_w, img_h = img.size
        if x < 0 or y < 0 or x + w > img_w or y + h > img_h:
            raise Exception(f"Crop area out of bounds. Image size is {img_w}x{img_h}.")

        cropped = img.crop((x, y, x + w, y + h))
        ext = (img.format or "PNG").lower()
        output_path = os.path.join(output_folder, _output_name("cropped", ext))
        cropped.save(output_path)
    return output_path


def watermark_image(image_path, text, output_folder):
    if not os.path.exists(image_path):
        raise Exception("Image file not found.")
    if not text.strip():
        raise Exception("Watermark text is required.")

    os.makedirs(output_folder, exist_ok=True)

    with Image.open(image_path).convert("RGB") as img:
        draw = ImageDraw.Draw(img)

        # Large font attempt
        font_size = max(30, img.width // 12)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        # Center position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = max(10, (img.width - text_w) // 2)
        y = max(10, (img.height - text_h) // 2)

        # Draw thick black stroke + bright red text (very visible)
        draw.text((x-2, y-2), text, font=font, fill=(0, 0, 0))
        draw.text((x+2, y-2), text, font=font, fill=(0, 0, 0))
        draw.text((x-2, y+2), text, font=font, fill=(0, 0, 0))
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0))
        draw.text((x, y), text, font=font, fill=(255, 0, 0))  # RED text

        output_path = os.path.join(output_folder, _output_name("watermarked", "jpg"))
        img.save(output_path, quality=95)

    return output_path


def convert_image_format(image_path, target_format, output_folder):
    if not os.path.exists(image_path):
        raise Exception("Image file not found.")

    fmt = target_format.strip().upper()
    allowed = {"JPG", "JPEG", "PNG", "WEBP"}
    if fmt not in allowed:
        raise Exception("Target format must be JPG, PNG, or WEBP.")

    os.makedirs(output_folder, exist_ok=True)
    with Image.open(image_path) as img:
        if fmt in {"JPG", "JPEG"} and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        ext = "jpg" if fmt in {"JPG", "JPEG"} else fmt.lower()
        output_path = os.path.join(output_folder, _output_name("converted_img", ext))
        img.save(output_path, format=fmt)
    return output_path