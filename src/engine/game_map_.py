from pygame import Vector2
import pygame as pg

class _MapManager:
    def __init__(self):
        # List of static collision segments
        # Each segment: ((x1, y1), (x2, y2))
        self.collision_segments = []

    # --- authoring / setup ---

    def add_wall(self, p1, p2):
        """Add a blocking segment (world coordinates)."""
        self.collision_segments.append((p1, p2))


    def raycast(self, start, end):
        """
        Cast a segment from start -> end.
        Returns:
            (hit, hit_point, hit_segment)
        """
        closest_t = None
        hit_point = None
        hit_segment = None

        for seg in self.collision_segments:
            hit, t, point = self._segment_intersect_parametric(
                start, end, seg[0], seg[1]
            )

            if hit and (closest_t is None or t < closest_t) and point:
                closest_t = t
                hit_point = Vector2(point)
                hit_segment = seg

        return hit_point is not None, hit_point, hit_segment

    def _segment_intersect_parametric(self, a, b, c, d):
        """
        Segment AB vs CD
        Returns:
            hit (bool)
            t (float along AB)
            intersection point
        """
        ax, ay = a
        bx, by = b
        cx, cy = c
        dx, dy = d

        r_x = bx - ax
        r_y = by - ay
        s_x = dx - cx
        s_y = dy - cy

        denom = r_x * s_y - r_y * s_x
        if denom == 0:
            return False, None, None  # parallel

        t = ((cx - ax) * s_y - (cy - ay) * s_x) / denom
        u = ((cx - ax) * r_y - (cy - ay) * r_x) / denom

        if 0 <= t <= 1 and 0 <= u <= 1:
            ix = ax + t * r_x
            iy = ay + t * r_y
            return True, t, (ix, iy)

        return False, None, None

    def draw(self, surf, offset: Vector2):
        for line in self.collision_segments:
            pg.draw.line(surf, (255, 255, 255), line[0] + offset, line[1] + offset, 1)