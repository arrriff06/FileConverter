from PIL import Image, ImageFile
import os
import time

ImageFile.LOAD_TRUNCATED_IMAGES = True


def convert_jpg_to_pdf(image_paths, output_folder):
    if not image_paths:
        raise Exception("No images provided")

    os.makedirs(output_folder, exist_ok=True)

    images = []

    for path in image_paths:

        # 🔥 HANDLE TUPLE BUG (important)
        if isinstance(path, tuple):
            path = path[0]

        if not isinstance(path, str):
            continue

        if not os.path.exists(path):
            continue

        try:
            img = Image.open(path)

            # Convert to RGB (required for PDF)
            if img.mode != "RGB":
                img = img.convert("RGB")

            images.append(img)

        except Exception as e:
            print(f"Skipping file {path}: {e}")

    if not images:
        raise Exception("No valid images found")

    output_filename = f"converted_{int(time.time())}.pdf"
    output_path = os.path.join(output_folder, output_filename)

    try:
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:]
        )
    finally:
        # 🔥 CLOSE ALL IMAGES (important for stability)
        for img in images:
            try:
                img.close()
            except:
                pass

    return output_path