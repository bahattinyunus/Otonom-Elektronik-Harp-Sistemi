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
        arr = np.array(psd_frame, dtype=float)
        n = len(arr)
        
        # Optimized sliding median estimate using NumPy windowing or simple median filter
        # If scipy is available, we'd use median_filter. Fallback to numpy stride-based median.
        try:
            from scipy.ndimage import median_filter
            baseline = median_filter(arr, size=self.window)
        except ImportError:
            # Vectorized sliding window for median if scipy is missing
            # (Note: this is memory intensive for very large windows, but fine for 33)
            temp = np.pad(arr, self._half, mode='edge')
            from numpy.lib.stride_tricks import sliding_window_view
            baseline = np.median(sliding_window_view(temp, self.window), axis=1)

        # Enhance peaks that rise above baseline
        diff     = arr - baseline
        enhanced = baseline + diff * np.where(diff > 0, self.enhance, 1.0)
        return enhanced.tolist()
