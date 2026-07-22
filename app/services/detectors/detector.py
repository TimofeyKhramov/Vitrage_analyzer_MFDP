import os
import re
import logging
import fitz
import math
from ultralytics import YOLO
import cv2
import numpy as np
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DrawingDetector:

    def __init__(
        self,
        model_drawing_path,
        conf_drawings: float,
        imgsz: int,
    ):
        self.model_drawing_path = model_drawing_path
        self.conf_drawings = conf_drawings
        self.imgsz = imgsz

    def tile_bbox_to_pdf(self, bbox_tile, tile_info):
        """
        Перевод bbox из координат тайла (px)
        в координаты исходной страницы PDF (pt).

        Parameters
        ----------
        bbox_tile : (x1,y1,x2,y2)
            Координаты YOLO на тайле (в пикселях)

        tile_info : dict
            {
                "x_offset_pt": ...,
                "y_offset_pt": ...,
                "dpi": ...
            }

        Returns
        -------
        fitz.Rect
        """

        x1, y1, x2, y2 = bbox_tile

        scale = 72.0 / tile_info["dpi"]

        x1 = x1 * scale + tile_info["x_offset_pt"]
        y1 = y1 * scale + tile_info["y_offset_pt"]

        x2 = x2 * scale + tile_info["x_offset_pt"]
        y2 = y2 * scale + tile_info["y_offset_pt"]


        return fitz.Rect(x1, y1, x2, y2), [x1, y1, x2, y2]
    
    def iou(self,box1, box2):
        """
        box = [x1, y1, x2, y2, class]
        """

        left = max(box1[0], box2[0])
        top = max(box1[1], box2[1])
        right = min(box1[2], box2[2])
        bottom = min(box1[3], box2[3])

        if right <= left or bottom <= top:
            return 0.0

        intersection = (right - left) * (bottom - top)

        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])

        union = area1 + area2 - intersection

        return intersection / union
    
    def mean_coord(self, array):
        x1, y1, x2, y2 = [], [], [], []
        amount = len(array)
        for i in range(amount):
            x1.append(array[i][0])
            y1.append(array[i][1])
            x2.append(array[i][2])
            y2.append(array[i][3])
       
        return [min(x1), min(y1), max(x2), max(y2)]

    def detect(
        self,
        tiles: list[dict],
    ) -> list[dict]:
        coords = []

        for tile in tiles:

            # изображение тайла
            img = cv2.imread(tile["file"])
            logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            model_drawings = YOLO(self.model_drawing_path)
            detections = model_drawings(tile["file"], conf=self.conf_drawings, verbose=False, imgsz=self.imgsz)
            logger.info('111111111111111111111111222')
            for detection in detections:
                # print(matches)

                for box in detection.boxes:

                    class_id = int(box.cls.item())
                    class_name = detection.names[class_id]
                    conf = float(box.conf)
                    # if class_name == 'drawning' and conf < 0.5:
                    #     continue


                    # координаты на тайле
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                    # перевод в координаты страницы
                    rect, coord = self.tile_bbox_to_pdf(
                        box.xyxy[0].tolist(),
                        tile
                    )

                    coords.append(
                        coord + [
                            class_name,
                            conf
                        ]
                    )

            # сохранить размеченный тайл
            out_name = os.path.join(
                "tiles_pdf",
                os.path.basename(tile["file"])
            )

            cv2.imwrite(out_name, img)



        groups = []
        used = set()

        groups = []

        order = sorted(
            range(len(coords)),
            key=lambda i: coords[i][5],   # confidence
            reverse=True
        )

        for i in order:

            if i in used:
                continue

            group = [i]
            used.add(i)

            for j in order:

                if j in used:
                    continue

                if coords[i][4] != coords[j][4]:
                    continue

                if self.iou(coords[i], coords[j]) >= 0.3:

                    group.append(j)
                    used.add(j)

            groups.append(group)

        boxes_array = []

        for group in groups:

            # один bbox
            if len(group) == 1:

                idx = group[0]

                boxes_array.append(
                    coords[idx][:5]
                )

                continue

            # confidences всех боксов группы
            confs = [
                coords[i][5]
                for i in group
            ]

            # --------------------------------------------------
            # все боксы уверенные -> объединяем границы
            # --------------------------------------------------

            if min(confs) >= 0.85:

                merged = self.mean_coord(
                    [
                        coords[i][:4]
                        for i in group
                    ]
                )

                merged.append(
                    coords[group[0]][4]
                )

                boxes_array.append(
                    merged
                )

            # --------------------------------------------------
            # иначе берем наиболее уверенный bbox
            # --------------------------------------------------

            else:

                best = max(
                    group,
                    key=lambda i: coords[i][5]
                )

                boxes_array.append(
                    coords[best][:5]
                )


        os.makedirs("find_boxes", exist_ok=True)

        nodes = []

        for i, box in enumerate(boxes_array):
            # print('!!!!!!!!!', box)
            x1, y1, x2, y2, cls = box

            node = {
                "id": i,
                "class": cls,

                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,

                "cx": (x1 + x2) / 2,
                "cy": (y1 + y2) / 2,

                "width": x2 - x1,
                "height": y2 - y1
            }


            nodes.append(node)

        return nodes


class DrawingAnalyzer:
    def rect_distance(self, a, b):
        """
        Минимальное расстояние между двумя прямоугольниками.

        Если они пересекаются,
        возвращается 0.
        """

        dx = max(
            a["x1"] - b["x2"],
            b["x1"] - a["x2"],
            0
        )

        dy = max(
            a["y1"] - b["y2"],
            b["y1"] - a["y2"],
            0
        )

        return math.sqrt(dx*dx + dy*dy)

    def dominant_angle(self, a, b):
        """
        Угол относительно доминирующей оси.

        0°  — почти вдоль главной оси.
        90° — сильное отклонение.
        """

        dx = b["cx"] - a["cx"]
        dy = b["cy"] - a["cy"]

        if abs(dx) >= abs(dy):
            angle = math.degrees(math.atan2(abs(dy), abs(dx)))
        else:
            angle = math.degrees(math.atan2(abs(dx), abs(dy)))

        return angle

    def score(self, a, b):

        d = self.rect_distance(a, b)
        angle = self.dominant_angle(a, b)

        score = d * (1 + angle / 90)
        if b["cy"] > a["cy"]:
            score *= 2

        # 2) Если объект b правее объекта a → увеличиваем score в 2 раза
        if b["cx"] > a["cx"]:
            score *= 2
        return score
    
    def graph(self, nodes):
        logger.info('33333333333333333333333')
        result = {}
        for_ocr_dict = {}
        for drawing in nodes:
            drawing_coords, best_name_coords, best_amount_coords = None, None, None
            if drawing["class"] != "drawning":
                continue

            drawing_coords = [drawing["x1"], drawing["y1"], drawing["x2"], drawing["y2"]]
            best_title = None
            best_title_score = float("inf")

            best_quantity = None
            best_quantity_score = float("inf")

            for obj in nodes:

                if obj["id"] == drawing["id"]:
                    continue

                if obj["class"] == "name":

                    s = self.score(drawing, obj)

                    if s < best_title_score:
                        best_title_score = s
                        best_title = obj["id"]
                        best_name_coords = [obj["x1"], obj["y1"], obj["x2"], obj["y2"]]

                elif obj["class"] == "amount":
                    if self.rect_distance(drawing, obj) < (drawing["y2"] - drawing["y1"]) * 1.3:

                        s = self.score(drawing, obj)

                        if s < best_quantity_score:
                            best_quantity_score = s
                            best_quantity = obj["id"]
                            best_amount_coords = [obj["x1"], obj["y1"], obj["x2"], obj["y2"]]

            for_ocr_dict[drawing["id"]] = {"drawing": drawing_coords, "name": best_name_coords, "amount": best_amount_coords}

            result[drawing["id"]] = {
                "name": best_title,
                "amount": best_quantity,
            }
            
        return for_ocr_dict
    