import fitz
import re
from app.services.pdf.cropper import PdfCropper
from app.services.extractors.name_amount_extractor import NameAmountExtractor
from ultralytics import YOLO
from pathlib import Path
from app.services.storage_service import StorageService
from app.models.document import Document    


class PdfExtractor:

    def __init__(
        self,
        model_doors_path: str,
        document: Document,
        page_number: int,
    ):

        self.model_doors = YOLO(model_doors_path)

        self.document = document
        self.page_number = page_number

        self.pdf_path = StorageService.get_pdf_path(
            document,
        )

        self.page_directory = StorageService.get_page_directory(
            document,
            page_number,
        )

        self.pdf = fitz.open(self.pdf_path)

        self.page = self.pdf.load_page(
            page_number - 1,
        )

    def close(self):

        if self.pdf is not None:

            self.pdf.close()

            self.pdf = None

    def get_max_horizontal_number(
        self,
        drawing_bbox,
        angle_threshold: float = 0.9,
    ):

        rect = fitz.Rect(drawing_bbox)

        data = self.page.get_text(
            "dict",
            clip=rect,
        )

        max_number = None

        for block in data["blocks"]:

            if block["type"] != 0:
                continue

            for line in block["lines"]:

                dx, dy = line["dir"]

                # Только горизонтальный текст
                if abs(dx) < angle_threshold or abs(dy) > 0.2:
                    continue

                text = "".join(
                    span["text"]
                    for span in line["spans"]
                )

                for token in text.replace(",", " ").split():

                    try:

                        value = int(token)

                    except ValueError:

                        continue

                    if max_number is None or value > max_number:

                        max_number = value

        return max_number

    def get_max_vertical_number(
        self,
        drawing_bbox,
        angle_threshold: float = 0.9,
    ):

        rect = fitz.Rect(drawing_bbox)

        data = self.page.get_text(
            "dict",
            clip=rect,
        )

        max_number = None

        for block in data["blocks"]:

            if block["type"] != 0:
                continue

            for line in block["lines"]:

                dx, dy = line["dir"]

                # Только вертикальный текст
                if abs(dy) < angle_threshold or abs(dx) > 0.2:
                    continue

                text = "".join(
                    span["text"]
                    for span in line["spans"]
                )

                for token in text.replace(",", " ").split():

                    try:

                        value = int(token)

                    except ValueError:

                        continue

                    if max_number is None or value > max_number:

                        max_number = value

        return max_number

    def find_nearest_vertical_number(
        self,
        box,
    ):

        x1, y1, x2, y2 = box

        cy = (y1 + y2) / 2

        candidates = []

        for block in self.page.get_text("dict")["blocks"]:

            if block["type"] != 0:
                continue

            for line in block["lines"]:

                dx, dy = line["dir"]

                if abs(dy) < 0.9 or abs(dx) > 0.2:
                    continue

                lx1, ly1, lx2, ly2 = line["bbox"]

                if (
                    lx1 >= x1
                    and ly1 >= y1
                    and lx2 <= x2
                    and ly2 <= y2
                ):
                    continue

                text = "".join(
                    span["text"]
                    for span in line["spans"]
                )

                try:

                    value = int(text)

                except ValueError:

                    continue

                candidates.append(
                    (
                        value,
                        (ly1 + ly2) / 2,
                    )
                )

        if not candidates:

            return None

        return min(
            candidates,
            key=lambda item: abs(item[1] - cy),
        )[0]

    def extract_params(
        self,
        for_ocr_dict: dict,
    ) -> dict:

        data_dict = {
            "materials": "",
            "drawings": [],
        }

        for value in for_ocr_dict.values():

            drawing_rect = fitz.Rect(
                value["drawing"],
            )

            # Проверка наличия текстового слоя
            if len(
                self.page.get_text(
                    "words",
                    clip=drawing_rect,
                )
            ) < 5:
                continue

            width = self.get_max_horizontal_number(
                value["drawing"],
            )

            height = self.get_max_vertical_number(
                value["drawing"],
            )

            crop, scale = PdfCropper.crop_pdf_to_jpg(
                page=self.page,
                bbox=value["drawing"],
            )

            detections = self.model_doors(
                crop,
                conf=0.8,
                verbose=False,
            )

            doors_amount = sum(
                len(detection.boxes)
                for detection in detections
            )

            doors_heights = []

            for detection in detections:

                for box in detection.boxes:

                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0].tolist(),
                    )

                    pdf_box = [
                        x1 / scale + value["drawing"][0],
                        y1 / scale + value["drawing"][1],
                        x2 / scale + value["drawing"][0],
                        y2 / scale + value["drawing"][1],
                    ]

                    door_height = self.find_nearest_vertical_number(
                        pdf_box,
                    )

                    doors_heights.append(
                        door_height,
                    )

            name = None

            amount = None

            if value["amount"]:

                amount = self.page.get_text(
                    clip=fitz.Rect(
                        value["amount"],
                    )
                ).strip()

                blocks = self.page.get_text(
                    "blocks",
                    clip=fitz.Rect(
                        value["name"],
                    ),
                )

                if blocks and len(blocks[0]) > 4:

                    name = NameAmountExtractor.extract_name(
                        blocks[0][4],
                    )

            elif value["name"]:

                blocks = self.page.get_text(
                    "blocks",
                    clip=fitz.Rect(
                        value["name"],
                    ),
                )

                if blocks and len(blocks[0]) > 4:

                    name = NameAmountExtractor.extract_name(
                        blocks[0][4],
                    )

                    amount = NameAmountExtractor.extract_quantity_advanced(
                        blocks[0][4],
                    )

            data_dict["drawings"].append(
                {
                    "name": name,
                    "amount": amount,
                    "width": width,
                    "height": height,
                    "doors_amount": doors_amount,
                    "doors_height": doors_heights,
                }
            )

        return data_dict
