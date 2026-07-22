import os

import fitz


class PDFSplitter:

    @staticmethod
    def split(
        pdf_path,
        page_number: int,
        output_dir,
        dpi=300,
        jpeg_quality=100,
    ):
        """
        Нарезка одной страницы PDF на тайлы.
        """

        os.makedirs(output_dir, exist_ok=True)

        doc = fitz.open(pdf_path)

        page = doc.load_page(page_number - 1)

        width_pt = page.rect.width
        height_pt = page.rect.height

        max_side = max(width_pt, height_pt)

        if max_side < 1000:
            rows = cols = 1
            overlap_px = 0

        elif max_side > 3000:
            rows = cols = 3
            overlap_px = 400

        elif max_side > 2000:
            rows = cols = 3
            overlap_px = 300

        elif max_side > 1500:
            rows = cols = 3
            overlap_px = 250

        else:
            rows = cols = 1
            overlap_px = 200

        tiles_info = []

        if rows == 1:

            pix = page.get_pixmap(dpi=dpi)

            outfile = os.path.join(
                output_dir,
                f"page_{page_number:03d}.jpg",
            )

            pix.save(outfile, jpg_quality=jpeg_quality)

            tiles_info.append(
                {
                    "page": page_number,
                    "tile_id": 0,
                    "file": outfile,
                    "x_offset_pt": 0,
                    "y_offset_pt": 0,
                    "dpi": dpi,
                }
            )

            doc.close()

            return tiles_info

        overlap_pt = overlap_px * 72.0 / dpi

        tile_w = width_pt / cols
        tile_h = height_pt / rows

        crop_w = tile_w + 2 * overlap_pt
        crop_h = tile_h + 2 * overlap_pt

        tile_id = 0

        for r in range(rows):

            for c in range(cols):

                x1 = c * tile_w - overlap_pt
                y1 = r * tile_h - overlap_pt

                if x1 < 0:
                    x1 = 0

                if x1 + crop_w > width_pt:
                    x1 = width_pt - crop_w

                if y1 < 0:
                    y1 = 0

                if y1 + crop_h > height_pt:
                    y1 = height_pt - crop_h

                clip = fitz.Rect(
                    x1,
                    y1,
                    x1 + crop_w,
                    y1 + crop_h,
                )

                pix = page.get_pixmap(
                    dpi=dpi,
                    clip=clip,
                )

                outfile = os.path.join(
                    output_dir,
                    f"tile_{page_number:03d}_{tile_id:02d}.jpg",
                )

                pix.save(
                    outfile,
                    jpg_quality=jpeg_quality,
                )

                tiles_info.append(
                    {
                        "page": page_number,
                        "tile_id": tile_id,
                        "file": outfile,
                        "x_offset_pt": x1,
                        "y_offset_pt": y1,
                        "dpi": dpi,
                    }
                )

                tile_id += 1

        doc.close()

        return tiles_info