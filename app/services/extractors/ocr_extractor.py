import math
import numpy as np
import cv2


class OcrExtracor():
    def replace_english_to_russian(self, text):
        """
        Заменяет английские буквы на визуально похожие русские

        Args:
            text: строка для преобразования

        Returns:
            str: строка с заменёнными буквами
        """
        # Словарь соответствия английских букв русским
        replace_map = {
            # Строчные буквы
            'a': 'а',
            'b': 'в',
            'c': 'с',
            'e': 'е',
            'h': 'н',
            'k': 'к',
            'm': 'м',
            'o': 'о',
            'p': 'р',
            't': 'т',
            'x': 'х',
            'y': 'у',
            # Заглавные буквы
            'A': 'А',
            'B': 'В',
            'C': 'С',
            'E': 'Е',
            'H': 'Н',
            'K': 'К',
            'M': 'М',
            'O': 'О',
            'P': 'Р',
            'T': 'Т',
            'X': 'Х',
            'Y': 'У'
        }

        # Заменяем все буквы по словарю
        result = ''
        for char in text:
            result += replace_map.get(char, char)

        return result

    def _box_angle(poly: np.ndarray) -> float:
        """
        Угол верхней стороны полигона относительно горизонтали.
        poly.shape == (4, 2)
        """
        x1, y1 = poly[0]
        x2, y2 = poly[1]
        return abs(math.degrees(math.atan2(y2 - y1, x2 - x1)))


    def _box_center(poly: np.ndarray) -> tuple[float, float]:
        return poly[:, 0].mean(), poly[:, 1].mean()


    def extract_max_horizontal_size(self, crop,
                                    result: dict,
                                    score_threshold: float = 0.8,
                                    angle_threshold: float = 15):
        """
        Возвращает максимальный горизонтальный размер (например, 2980).

        Parameters
        ----------
        result : dict
            Один элемент списка, возвращаемого PaddleOCR.

        score_threshold : float
            Минимальная уверенность OCR.

        angle_threshold : float
            Максимальный угол отклонения текста от горизонтали.

        Returns
        -------
        int | None
        """

        image = cv2.imread('/content/crop.png')
        H, W = crop.shape[:2]

        texts = result["rec_texts"]
        scores = result["rec_scores"]
        polys = result["rec_polys"]

        candidates = []

        for text, score, poly in zip(texts, scores, polys):

            if score < score_threshold:
                continue

            try:
                value = int(text)
            except ValueError:
                continue

            angle = self.box_angle(poly)
            if angle > angle_threshold:
                continue

            cx, cy =self.box_center(poly)

            candidates.append({
                "value": value,
                "x": cx,
                "y": cy,
            })

        if not candidates:
            return None

        # группировка по верхней строке размеров
        row_eps = H * 0.03

        top_y = min(c["y"] for c in candidates)

        top_row = [
            c for c in candidates
            if abs(c["y"] - top_y) <= row_eps
        ]

        if not top_row:
            return None

        return max(c["value"] for c in top_row)

    def extract_box(self, crop,  cls_name, ocr):
        
        """
        bbox : [x1, y1, x2, y2]
        cls_name : drawing | name | amount
        """
        # -----------------------------
        # NAME
        # -----------------------------
        if cls_name == "name":
            name_clear = None

            res = ocr.predict(crop, use_textline_orientation=False, return_word_box=False, use_doc_orientation_classify=False)
            name_rus = self.replace_english_to_russian(res[0]["rec_texts"][0])

            return ' '.join(res[0]["rec_texts"])

                # name_clear = replace_english_to_russian(res[0]["rec_texts"][0])
                # amount = extract_quantity_advanced(name_clear)


        # -----------------------------
        # AMOUNT
        # -----------------------------
        elif cls_name == "amount":
            amount = None
            res = ocr.predict(crop, use_textline_orientation=False, return_word_box=False, use_doc_orientation_classify=False)
            return res[0]["rec_texts"][0]

        # -----------------------------
        # DRAWING
        # -----------------------------
        elif cls_name == "drawing":

            # обычная ориентация
            res = ocr.predict(crop, use_textline_orientation=False, return_word_box=False, use_doc_orientation_classify=False)
            width = self.extract_max_horizontal_size(crop, res[0])

            # # поворот
            crop_rot = cv2.rotate(
                crop,
                cv2.ROTATE_90_CLOCKWISE
            )
            # cv2.imwrite("cdv.png", crop_rot)
            res = ocr.predict(crop_rot, use_textline_orientation=True, return_word_box=False, use_doc_orientation_classify=False)
            height = self.extract_max_horizontal_size(crop_rot, res[0])
            # print("MISTAKE", [width, height, res[0]["text_word"], res[0]["text_word_region"]])
            return width, height

        return None