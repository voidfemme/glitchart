#!/usr/bin/env python3

import argparse
import random
import requests  # make sure requests is installed: pip install requests
import numpy as np
from io import BytesIO
from PIL import Image

def open_image_from_path_or_url(input_path):
    """
    Open an image from a local path or a URL.
    Returns a PIL Image object.
    """
    if input_path.startswith("http://") or input_path.startswith("https://"):
        # Download image from URL
        response = requests.get(input_path)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
    else:
        # Local file
        img = Image.open(input_path)
    return img

def glitch_image(
    input_path,
    output_path,
    glitch_amount=5,
    glitch_iterations=10,
    operations=None
):
    """
    Applies a more varied glitch effect by randomly performing operations 
    on rows, columns, or chunks of the image.

    :param input_path: Path (or URL) to the input image.
    :param output_path: Path to the output glitched image.
    :param glitch_amount: Maximum pixel shift or manipulation amount.
    :param glitch_iterations: Number of random glitch operations to perform.
    :param operations: A list of operation names to use for glitching.
    """
    # 1) Open the image (local file or URL)
    img = open_image_from_path_or_url(input_path)

    # 2) Convert the PIL image to a NumPy array
    img_array = np.array(img)

    # Separate alpha if it exists
    has_alpha = False
    if img_array.shape[-1] == 4:
        has_alpha = True
        alpha_channel = img_array[:, :, 3]
        img_array = img_array[:, :, :3]

    height, width = img_array.shape[:2]

    # --- Define Glitch Operations ---
    def shift_row(row_idx, shift_val):
        """Shift an entire row left or right."""
        if shift_val != 0:
            img_array[row_idx] = np.roll(img_array[row_idx], shift_val, axis=0)

    def shift_col(col_idx, shift_val):
        """Shift an entire column up or down."""
        if shift_val != 0:
            img_array[:, col_idx] = np.roll(img_array[:, col_idx], shift_val, axis=0)

    def shift_chunk():
        """Shift a random rectangular chunk in the image by some offset."""
        chunk_width = random.randint(1, width // 2)
        chunk_height = random.randint(1, height // 2)

        x0 = random.randint(0, width - chunk_width)
        y0 = random.randint(0, height - chunk_height)

        shift_x = random.randint(-glitch_amount, glitch_amount)
        shift_y = random.randint(-glitch_amount, glitch_amount)

        chunk = img_array[y0:y0+chunk_height, x0:x0+chunk_width].copy()

        # Roll the chunk in x- and y-directions
        if shift_x != 0:
            chunk = np.roll(chunk, shift_x, axis=1)
        if shift_y != 0:
            chunk = np.roll(chunk, shift_y, axis=0)

        img_array[y0:y0+chunk_height, x0:x0+chunk_width] = chunk

    def shift_color_channel():
        """Shift one color channel (R, G, or B) in a random row or column."""
        if img_array.shape[2] < 3:
            return  # Skip if not an RGB image

        channel = random.randint(0, 2)  # R=0, G=1, or B=2
        shift_val = random.randint(-glitch_amount, glitch_amount)

        if random.random() < 0.5:
            # Shift a row in one channel
            row = random.randint(0, height - 1)
            if shift_val != 0:
                img_array[row, :, channel] = np.roll(img_array[row, :, channel], shift_val)
        else:
            # Shift a column in one channel
            col = random.randint(0, width - 1)
            if shift_val != 0:
                img_array[:, col, channel] = np.roll(img_array[:, col, channel], shift_val)

    def invert_colors():
        """Randomly invert colors in a small region of the image."""
        chunk_width = random.randint(1, width // 2)
        chunk_height = random.randint(1, height // 2)

        x0 = random.randint(0, width - chunk_width)
        y0 = random.randint(0, height - chunk_height)

        img_array[y0:y0+chunk_height, x0:x0+chunk_width] = \
            255 - img_array[y0:y0+chunk_height, x0:x0+chunk_width]

    # Default operations if none supplied
    if not operations:
        operations = [
            "shift_row",
            "shift_col",
            "shift_chunk",
            "shift_color_channel",
            "invert_colors"
        ]

    # --- Randomly apply glitch operations ---
    for _ in range(glitch_iterations):
        op = random.choice(operations)

        if op == "shift_row":
            row = random.randint(0, height - 1)
            shift_val = random.randint(-glitch_amount, glitch_amount)
            shift_row(row, shift_val)
        elif op == "shift_col":
            col = random.randint(0, width - 1)
            shift_val = random.randint(-glitch_amount, glitch_amount)
            shift_col(col, shift_val)
        elif op == "shift_chunk":
            shift_chunk()
        elif op == "shift_color_channel":
            shift_color_channel()
        elif op == "invert_colors":
            invert_colors()

    # Reattach alpha if needed
    if has_alpha:
        alpha_channel = alpha_channel.reshape((height, width, 1))
        if alpha_channel.shape[0] == img_array.shape[0] and alpha_channel.shape[1] == img_array.shape[1]:
            img_array = np.concatenate([img_array, alpha_channel], axis=2)

    # Convert back to PIL Image
    glitched_img = Image.fromarray(img_array.astype(np.uint8))

    # Convert from RGBA to RGB if necessary
    if glitched_img.mode == "RGBA":
        glitched_img = glitched_img.convert("RGB")

    # Save the final glitched image
    glitched_img.save(output_path)

def main():
    parser = argparse.ArgumentParser(
        description="Glitch an image (local file or URL) with various random operations."
    )
    parser.add_argument("input_path", help="Path or URL to the input image.")
    parser.add_argument("output_path", help="Where to save the glitched image.")

    # Short (-a) and long (--glitch-amount) options
    parser.add_argument(
        "-a", "--glitch-amount",
        type=int,
        default=5,
        help="Maximum pixel shift or manipulation (default: 5)."
    )
    parser.add_argument(
        "-n", "--glitch-iterations",
        type=int,
        default=10,
        help="Number of glitch operations (default: 10)."
    )

    # Flags to disable specific operations
    parser.add_argument(
        "-R", "--no-shift-row",
        action="store_true",
        help="Disable the 'shift_row' operation."
    )
    parser.add_argument(
        "-C", "--no-shift-col",
        action="store_true",
        help="Disable the 'shift_col' operation."
    )
    parser.add_argument(
        "-H", "--no-shift-chunk",
        action="store_true",
        help="Disable the 'shift_chunk' operation."
    )
    parser.add_argument(
        "-O", "--no-shift-color-channel",
        action="store_true",
        help="Disable the 'shift_color_channel' operation."
    )
    parser.add_argument(
        "-I", "--no-invert-colors",
        action="store_true",
        help="Disable the 'invert_colors' operation."
    )

    # Allow a seed for reproducible results
    parser.add_argument(
        "-s", "--seed",
        type=int,
        default=None,
        help="Set a random seed for reproducible glitching."
    )

    args = parser.parse_args()

    # Start with the full set of possible operations
    possible_ops = [
        "shift_row",
        "shift_col",
        "shift_chunk",
        "shift_color_channel",
        "invert_colors"
    ]

    # Remove operations the user wants disabled
    if args.no_shift_row and "shift_row" in possible_ops:
        possible_ops.remove("shift_row")
    if args.no_shift_col and "shift_col" in possible_ops:
        possible_ops.remove("shift_col")
    if args.no_shift_chunk and "shift_chunk" in possible_ops:
        possible_ops.remove("shift_chunk")
    if args.no_shift_color_channel and "shift_color_channel" in possible_ops:
        possible_ops.remove("shift_color_channel")
    if args.no_invert_colors and "invert_colors" in possible_ops:
        possible_ops.remove("invert_colors")

    # If a seed was provided, apply it
    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    # Perform the glitch
    glitch_image(
        input_path=args.input_path,
        output_path=args.output_path,
        glitch_amount=args.glitch_amount,
        glitch_iterations=args.glitch_iterations,
        operations=possible_ops
    )

if __name__ == "__main__":
    main()

