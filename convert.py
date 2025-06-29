#!/usr/bin/env python3
"""
surface.py – Python clone of the Rust `serialize_to_buffer` and `serialize_color`.

Usage example
-------------
from surface import (
    Surface, Cell, PaletteColour, RGBColour, Size
)

# build a minimal 2×1 surface: letter 'A', white on black
surf = Surface(
    size=Size(2, 1),
    chars=[
        Cell(code=ord("A"),
             flags=0,
             foreground=PaletteColour.White,
             background=PaletteColour.Black),
        Cell(code=ord(" "),
             flags=0,
             foreground=PaletteColour.White,
             background=PaletteColour.Black),
    ],
)

buf = surf.serialize_to_buffer()
Path("example.srf").write_bytes(buf)
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Sequence, Tuple, Union

# ──────────────────────────────  Colour helpers ────────────────────────────────

class PaletteColour(int, Enum):
    Black       = 0
    DarkBlue    = 1
    DarkGreen   = 2
    Teal        = 3
    DarkRed     = 4
    Magenta     = 5
    Olive       = 6
    Silver      = 7
    Gray        = 8
    Blue        = 9
    Green       = 10
    Aqua        = 11
    Red         = 12
    Pink        = 13
    Yellow      = 14
    White       = 15
    Transparent = 16               # reserved

RGBColour = Tuple[int, int, int]    # (r, g, b) – each 0-255

Colour = Union[PaletteColour, RGBColour]

def _serialize_color(color: Colour, out: bytearray) -> None:
    """
    Push the binary representation of *color* into *out*.

    • Palette colours → single byte 0-16.
    • True-colour (r, g, b)  → 17 followed by three bytes.
    """
    if isinstance(color, tuple):
        r, g, b = color
        out.extend((17, r & 0xFF, g & 0xFF, b & 0xFF))
    else:
        out.append(int(color) & 0xFF)

# ─────────────────────────────── Data classes ─────────────────────────────────

@dataclass(slots=True, frozen=True)
class Size:
    width:  int
    height: int

@dataclass(slots=True, frozen=True)
class Cell:
    code:       int        # Unicode scalar value
    flags:      int        # 0-65535
    foreground: Colour
    background: Colour

@dataclass
class Surface:
    size:  Size
    chars: Sequence[Cell]

    # static packers
    _HEADER_STRUCT = struct.Struct("<3sBII")   # magic, version, w, h
    _CELL_STRUCT   = struct.Struct("<I H")     # code (u32), flags (u16)

    def serialize_to_buffer(self) -> bytes:
        """
        Return the binary .srf representation of the entire surface.

        Layout (total bytes = 12 + 8×N, N = width×height):
        ------------------------------------------------------------------------
        0–2   'SRF'                        magic
        3     0x01                         version
        4–7   uint32le width
        8–11  uint32le height
        12…   character buffer (code, flags, fg, bg) × N
        """
        if len(self.chars) != self.size.width * self.size.height:
            raise ValueError("chars length must equal width × height")

        buf = bytearray()
        # ─── header ──────────────────────────────────────────────────────────
        buf += self._HEADER_STRUCT.pack(b"SRF", 1, self.size.width,
                                        self.size.height)

        # ─── character buffer ───────────────────────────────────────────────
        for ch in self.chars:
            buf += self._CELL_STRUCT.pack(ch.code & 0xFFFFFFFF,
                                          ch.flags & 0xFFFF)
            _serialize_color(ch.foreground, buf)
            _serialize_color(ch.background, buf)

        return bytes(buf)

# ───────────────────────── utility: simple file converter ─────────────────────

def textfile_to_fixed_surface(
    txt_path: Path,
    width: int = 240,
    height: int = 67,
    fg: Colour = PaletteColour.White,
    bg: Colour = PaletteColour.Black,
) -> Surface:
    """
    Read *txt_path* and create a `Surface` exactly *width* × *height*,
    space-padding or truncating as necessary; colours are uniform.
    """
    text = txt_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    cells: List[Cell] = []
    for row in range(height):
        line = lines[row] if row < len(lines) else ""
        for col in range(width):
            ch = line[col] if col < len(line) else " "
            cells.append(Cell(code=ord(ch), flags=0, foreground=fg, background=bg))

    return Surface(size=Size(width, height), chars=cells)

# ────────────────────────────── CLI helper (optional) ─────────────────────────

if __name__ == "__main__":
    import glob
    import os

    # Create surfaces directory if it doesn't exist
    surfaces_dir = Path("src/surfaces")
    surfaces_dir.mkdir(exist_ok=True)
    
    # Find all .slide files in src/slides directory
    slide_files = glob.glob("src/slides/*.slide")
    
    if not slide_files:
        print("No .slide files found in src/slides/")
    else:
        for slide_path in slide_files:
            slide_file = Path(slide_path)
            output_name = slide_file.stem + ".srf"
            output_path = surfaces_dir / output_name
            
            if output_path.exists():
                print(f"Skipping {slide_file} -> {output_path} (already exists)")
                continue
            
            print(f"Converting {slide_file} -> {output_path}")
            surf = textfile_to_fixed_surface(slide_file)
            output_path.write_bytes(surf.serialize_to_buffer())
            print(f"Wrote {output_path}")
    
    print(f"Conversion complete! Files saved in {surfaces_dir.absolute()}")
