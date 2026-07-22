import re  


class NameAmountExtractor:
    @staticmethod
    def extract_name(text: str):
        """
        Извлекает наименование витража из строки.

        Наименование витража - это часть от начала строки до скобок,
        внутри которых присутствует "шт" (штук).

        Аргументы:
            text: исходная строка с описанием витража

        Возвращает:
            Наименование витража или None, если шаблон не найден

        Примеры:
            >>> extract_window_name("Витрадж Атлант (3 шт)")
            'Витрадж Атлант'

            >>> extract_window_name("Стеклопакет двухкамерный (10 шт.)")
            'Стеклопакет двухкамерный'

            >>> extract_window_name("Окно ПВХ белое (5шт)")
            'Окно ПВХ белое'
        """
        if not text:
            return None

        # Проверяем наличие "шт" в тексте
        if "шт" not in text and "ШТ" not in text:
            return text.replace("\n", '')

        # Паттерн: всё до скобок, внутри которых есть "шт"
        # - \s* - пробелы перед скобками (опционально)
        # - \( - открывающая скобка
        # - [^)]* - любой текст внутри скобок (кроме закрывающей)
        # - шт - обязательное наличие "шт"
        # - [^)]* - любой текст после "шт" до закрывающей скобки
        # - \) - закрывающая скобка
        pattern = r'^(.*?)\s*\([^)]*шт[^)]*\)'

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            # Возвращаем захваченную группу (название до скобок)
            return match.group(1).strip()
        
        return text.replace("\n", '')
    
    @staticmethod
    def extract_quantity_advanced(text: str):
        """
        Извлекает число перед "шт"

        Примеры:
        "ВВ-3 2 шт" → 2
        "ВВ-32шт" → 32 (теперь извлекает 32, а не 2)
        "ВВ-3  2шт" → 2
        "шт 5" → None (нет числа перед шт)
        "2 штуки" → 2
        "ВВ-32 2 шт" → 2 (первое число перед шт)
        """
        if not text:
            return 1

        # Очищаем текст от лишних пробелов
        text = text.strip()

        # Ищем число перед "шт" (с пробелом или без)
        # \d+ - одно или более цифр
        # \s* - ноль или более пробелов
        # шт - буквы "шт"
        pattern = r'(\d+)\s*шт'

        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # Если "шт" не найдено, пробуем другие варианты
        patterns = [
            # Цифра перед "штук" или "штуки"
            (r'(\d+)\s*штук', 1),
            # Цифра после дефиса и перед "шт"
            (r'-(\d+)\s*шт', 1),
        ]

        for pattern, group in patterns:
            match = re.search(pattern, text, re.IGNORECASE)  
            if match:
                return int(match.group(group))

        return 1