def modulate_color(color: tuple[int, int, int], mod: float | int) -> tuple[int, int, int]:
    """Multiply each color value in the color by mod."""
    return (int(color[0]*mod), int(color[1]*mod), int(color[2]*mod))

def color_linear_blend(color1: tuple[int, int, int], color2: tuple[int, int, int], fac: float) -> tuple[int, int, int]:
    """Blends color1 to color2 linearly with fac (assumed to be from 0.0 - 1.0)"""
    return (int(color1[0] + (color2[0]-color1[0])*fac), int(color1[1] + (color2[1]-color1[1])*fac), int(color1[2] + (color2[2]-color1[2])*fac))