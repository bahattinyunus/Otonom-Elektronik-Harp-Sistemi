import numpy as np


class SpectralDenoiser:
    """Spectral baseline denoiser using a sliding median filter.

    Estimates the broadband noise floor via a wide median window, then
    optionally enhances signal peaks above that baseline.
    """

    def __init__(self, window: int = 33, enhance: float = 1.3):
        self.window  = window | 1   # Force odd
        self.enhance = enhance
        self._half   = self.window // 2

    def process(self, psd_frame: list) -> list:
        arr  = np.array(psd_frame, dtype=float)
        n    = len(arr)
        half = self._half
        baseline = np.empty(n)

        # Sliding median – estimate noise floor
        for i in range(n):
            lo = max(0, i - half)
            hi = min(n, i + half + 1)
            baseline[i] = np.median(arr[lo:hi])

        # Enhance peaks that rise above baseline
        diff     = arr - baseline
        enhanced = baseline + diff * np.where(diff > 0, self.enhance, 1.0)
        return enhanced.tolist()
