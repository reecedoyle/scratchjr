#!/usr/bin/env python3
"""
Convert SVGs in an input directory to PNGs in an output directory, sized to fit
within MAX_WIDTH x MAX_HEIGHT while preserving aspect ratio. PNGs in the input
directory are passed through ImageMagick to be resized to the same bounds.

Renderers (searched on PATH):
  - SVG -> PNG : inkscape
  - PNG resize : magick (ImageMagick v7)
"""

import argparse
import os
import shutil
import subprocess
import sys

import pysvg.parser

MAX_WIDTH = 180
MAX_HEIGHT = 140


def find_tool(*names):
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--input', required=True, help='SVG input directory')
    parser.add_argument('-o', '--output', required=True, help='PNG output directory')
    args = parser.parse_args()

    svg_dir = args.input.strip()
    png_dir = args.output.strip()

    inkscape = find_tool('inkscape', 'inkscape.com')
    magick = find_tool('magick', 'magick.exe')

    if not inkscape:
        sys.exit('Could not find inkscape on PATH; install via "scoop install inkscape"')
    if not magick:
        sys.exit('Could not find magick on PATH; install via "scoop install imagemagick"')

    print(f'Input SVG directory: {svg_dir}')
    print(f'Output PNG directory: {png_dir}')

    os.makedirs(png_dir, exist_ok=True)
    count = 0

    for name in sorted(os.listdir(svg_dir)):
        ext = os.path.splitext(name)[1].lower()
        in_path = os.path.join(svg_dir, name)
        out_path = os.path.join(png_dir, os.path.splitext(name)[0] + '.png')

        if ext == '.png':
            subprocess.check_call([
                magick, in_path,
                '-resize', f'{MAX_WIDTH}x{MAX_HEIGHT}',
                out_path,
            ])
            count += 1
            continue
        if ext != '.svg':
            continue

        svg = pysvg.parser.parse(in_path)
        try:
            svg_height = float(svg.get_height().rstrip('px'))
            svg_width = float(svg.get_width().rstrip('px'))
        except (TypeError, ValueError):
            # Some SVGs may have no explicit width/height — fall back to width.
            svg_height = float(MAX_HEIGHT)
            svg_width = float(MAX_WIDTH)

        ratio = svg_width / svg_height if svg_height else 1.0
        height_bound_by_width = MAX_WIDTH / ratio if ratio else MAX_HEIGHT

        if height_bound_by_width > MAX_HEIGHT:
            size_args = ['--export-height', str(MAX_HEIGHT)]
        else:
            size_args = ['--export-width', str(MAX_WIDTH)]

        subprocess.check_call([
            inkscape,
            *size_args,
            '--export-type=png',
            f'--export-filename={out_path}',
            in_path,
        ])
        count += 1

    print(f'Converted {count} files to PNG')


if __name__ == '__main__':
    main()
