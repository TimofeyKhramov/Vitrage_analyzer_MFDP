import base64
import logging
import math

import cv2
import numpy as np
from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)


class OcrService:

    def __init__(self):

        logger.info("Initializing PaddleOCR...")

        self.ocr = PaddleOCR(
            text_recognition_model_name="eslav_PP-OCRv5_mobile_rec",
            text_detection_model_name="PP-OCRv5_server_det",
        )

        logger.info("PaddleOCR initialized successfully.")

    def decode(self, image: str):

        data = base64.b64decode(image)

        return cv2.imdecode(
            np.frombuffer(data, np.uint8),
            cv2.IMREAD_COLOR,
        )

    def _box_angle(
        self,
        poly: np.ndarray,
    ) -> float:

        x1, y1 = poly[0]
        x2, y2 = poly[1]

        return abs(
            math.degrees(
                math.atan2(
                    y2 - y1,
                    x2 - x1,
                )
            )
        )

    def _box_center(
        self,
        poly: np.ndarray,
    ):

        return (
            poly[:, 0].mean(),
            poly[:, 1].mean(),
        )

    def extract_max_horizontal_size(
        self,
        crop,
        result: dict,
        score_threshold: float = 0.9,
        angle_threshold: float = 30,
    ):

        H, W = crop.shape[:2]

        texts = result.get("rec_texts", [])
        scores = result.get("rec_scores", [])
        polys = result.get("rec_polys", [])

        candidates = []

        for text, score, poly in zip(
            texts,
            scores,
            polys,
        ):

            if score < score_threshold:
                continue

            try:
                value = int(text)
            except ValueError:
                continue

            angle = self._box_angle(poly)

            if angle > angle_threshold:
                continue

            # Нормализованные размеры бокса
            box_width = (poly[:, 0].max() - poly[:, 0].min()) / W
            box_height = (poly[:, 1].max() - poly[:, 1].min()) / H

            # Бокс должен быть более вытянут по горизонтали
            if box_width <= box_height:
                continue

            cx, cy = self._box_center(poly)

            candidates.append(
                {
                    "value": value,
                    "x": cx,
                    "y": cy,
                }
            )

        if not candidates:
            return None

        return max(
            c["value"]
            for c in candidates
        )

    def extract_drawing(
        self,
        image: str,
    ):

        try:

            img = self.decode(image)

            if img is None:
                raise ValueError(
                    "Failed to decode image."
                )
            padding = 50
            
            img_pad = cv2.copyMakeBorder(
                img,
                top=padding,
                bottom=padding,
                left=padding,
                right=padding,
                borderType=cv2.BORDER_CONSTANT,
                value=(255, 255, 255),  # белый фон
            )

            result = self.ocr.predict(
                img_pad,
                use_textline_orientation=False,
                return_word_box=False,
                use_doc_orientation_classify=False,
            )
            # print(result[0]["rec_texts"])
            # print(result[0]["rec_scores"])

            width = self.extract_max_horizontal_size(
                img,
                result[0],
            )

            img_rot = cv2.rotate(
                img,
                cv2.ROTATE_90_CLOCKWISE,
            )
            padding = 50

            img_rot_pad = cv2.copyMakeBorder(
                img_rot,
                top=padding,
                bottom=padding,
                left=padding,
                right=padding,
                borderType=cv2.BORDER_CONSTANT,
                value=(255, 255, 255),  # белый фон
            )
            cv2.imwrite('border.png', img_rot_pad)

            result = self.ocr.predict(
                img_rot_pad,
                use_textline_orientation=True,
                return_word_box=False,
                use_doc_orientation_classify=False,
            )
            print(result[0]["rec_texts"])
            print(result[0]["rec_scores"])

            height = self.extract_max_horizontal_size(
                img_rot,
                result[0],
            )

            return {
                "width": width,
                "height": height,
            }

        except Exception:

            logger.exception(
                "Drawing OCR failed."
            )

            return {
                "width": None,
                "height": None,
            }

    def extract_name(
        self,
        image: str,
    ):

        try:

            img = self.decode(image)

            if img is None:
                raise ValueError(
                    "Failed to decode image."
                )

            result = self.ocr.predict(
                img,
                use_textline_orientation=False,
                return_word_box=False,
                use_doc_orientation_classify=False,
            )

            texts = result[0].get(
                "rec_texts",
                [],
            )

            return {
                "name": " ".join(texts)
                if texts
                else None,
            }

        except Exception:

            logger.exception(
                "Name OCR failed."
            )

            return {
                "name": None,
            }

    def extract_amount(
        self,
        image: str,
    ):

        try:

            img = self.decode(image)

            if img is None:
                raise ValueError(
                    "Failed to decode image."
                )

            result = self.ocr.predict(
                img,
                use_textline_orientation=False,
                return_word_box=False,
                use_doc_orientation_classify=False,
            )

            texts = result[0].get(
                "rec_texts",
                [],
            )

            return {
                "amount": texts[0]
                if texts
                else None,
            }

        except Exception:

            logger.exception(
                "Amount OCR failed."
            )

            return {
                "amount": None,
            }