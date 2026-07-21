class PageRangeParser:

    @staticmethod
    def parse(
        pages: str,
        max_page: int,
    ) -> list[int]:
        """
        Parse page ranges.

        Examples:
            "1" -> [1]
            "1,3,5-7" -> [1, 3, 5, 6, 7]
        """

        if not pages or not pages.strip():
            raise ValueError("Не указан диапазон страниц.")

        result: set[int] = set()

        parts = pages.split(",")

        for part in parts:

            part = part.strip()

            if not part:
                raise ValueError("Некорректный формат диапазона страниц.")

            if "-" in part:

                bounds = part.split("-")

                if len(bounds) != 2:
                    raise ValueError(
                        f"Некорректный диапазон: '{part}'."
                    )

                start_str, end_str = bounds

                if not start_str.isdigit() or not end_str.isdigit():
                    raise ValueError(
                        f"Некорректный диапазон: '{part}'."
                    )

                start = int(start_str)
                end = int(end_str)

                if start > end:
                    raise ValueError(
                        f"Некорректный диапазон: '{part}'."
                    )

                if start < 1 or end > max_page:
                    raise ValueError(
                        f"Страницы '{part}' отсутствуют в документе."
                    )

                result.update(range(start, end + 1))

            else:

                if not part.isdigit():
                    raise ValueError(
                        f"Некорректный номер страницы: '{part}'."
                    )

                page = int(part)

                if page < 1 or page > max_page:
                    raise ValueError(
                        f"Страница {page} отсутствует в документе."
                    )

                result.add(page)

        return sorted(result)