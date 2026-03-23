from PIL import Image, ImageFile
import os
import time

ImageFile.LOAD_TRUNCATED_IMAGES = True


def convert_jpg_to_pdf(image_paths, output_folder):

    images = []

    for path in image_paths:

        img = Image.open(path)

        # Convert RGBA → RGB (important for PDF)
        if img.mode == "RGBA":
            img = img.convert("RGB")

        images.append(img)

    output_filename = f"converted_{int(time.time())}.pdf"

    output_path = os.path.join(output_folder, output_filename)

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:]
    )

    return output_path