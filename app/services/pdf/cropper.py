import fitz
import numpy as np
import cv2
from PIL import Image


class PdfCropper:
    @staticmethod
    def crop_pdf_to_jpg(
        page: fitz.Page,
        bbox: list[float],
        dpi: int = 300,
    ) -> tuple[np.ndarray, float]:

        try:
            # Create a rectangle for clipping
            clip_rect = fitz.Rect(bbox)

            pix = page.get_pixmap(dpi=dpi, clip=clip_rect)

            # Get the pixmap of the clipped area
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            
            if pix.n == 4:
                img_array = img_array[:, :, :3]

            # Конвертируем RGB в BGR для OpenCV
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

            return img_bgr, dpi/72

            # cv2.imwrite("vfb.png", img_bgr)

            # Save the pixmap as a JPG
        except Exception as e:
            print(f"An error occurred: {e}")
        
        
