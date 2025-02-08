WINDOW_COLORS = [
    "#ffeeba",  # Window 2: pale yellow
    "#c3e6cb",  # Window 3: pale green
    "#bee5eb",  # Window 4: pale blue
    "#f5c6cb",  # Window 5: pale red/pink
]

class ColorCycler:
    _index = 0

    @classmethod
    def get_next_color(cls):
        color = WINDOW_COLORS[cls._index % len(WINDOW_COLORS)]
        cls._index += 1
        return color