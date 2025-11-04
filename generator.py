# generator.py - Криптографически безопасный генератор паролей
import secrets
import string
import math


class PasswordGenerator:
    """Генератор криптографически стойких паролей"""

    @staticmethod
    def generate(
            length: int = 16,
            uppercase: bool = True,
            lowercase: bool = True,
            digits: bool = True,
            symbols: bool = True,
            exclude_ambiguous: bool = False
    ) -> str:
        """
        Генерация криптографически стойкого пароля

        Args:
            length: Длина пароля (8-128)
            uppercase: Использовать A-Z
            lowercase: Использовать a-z
            digits: Использовать 0-9
            symbols: Использовать !@#$%...
            exclude_ambiguous: Исключить похожие символы (0OIl1)

        Returns:
            Случайный пароль
        """
        if length < 8:
            length = 8
        if length > 128:
            length = 128

        # Набор символов
        chars = ""
        required_chars = []

        if lowercase:
            lc = string.ascii_lowercase
            if exclude_ambiguous:
                lc = lc.replace('l', '').replace('o', '')
            chars += lc
            if lc:
                required_chars.append(secrets.choice(lc))

        if uppercase:
            uc = string.ascii_uppercase
            if exclude_ambiguous:
                uc = uc.replace('I', '').replace('O', '')
            chars += uc
            if uc:
                required_chars.append(secrets.choice(uc))

        if digits:
            dg = string.digits
            if exclude_ambiguous:
                dg = dg.replace('0', '').replace('1', '')
            chars += dg
            if dg:
                required_chars.append(secrets.choice(dg))

        if symbols:
            sym = "!@#$%^&*()-_=+[]{};:,.<>?/"
            chars += sym
            required_chars.append(secrets.choice(sym))

        # Минимум один набор должен быть выбран
        if not chars:
            chars = string.ascii_lowercase + string.digits
            required_chars = [
                secrets.choice(string.ascii_lowercase),
                secrets.choice(string.digits)
            ]

        # Генерируем остальные символы
        remaining_length = max(0, length - len(required_chars))
        password_list = required_chars + [
            secrets.choice(chars) for _ in range(remaining_length)
        ]

        # Перемешиваем криптографически стойким способом
        for i in range(len(password_list) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password_list[i], password_list[j] = password_list[j], password_list[i]

        return ''.join(password_list)

    @staticmethod
    def estimate_strength(password: str) -> tuple[str, int, float]:
        """
        Оценка силы пароля

        Returns:
            (уровень, процент, энтропия в битах)
        """
        if not password:
            return "Нет пароля", 0, 0.0

        score = 0
        length = len(password)

        # Длина
        if length >= 8:
            score += 1
        if length >= 12:
            score += 1
        if length >= 16:
            score += 1
        if length >= 20:
            score += 1

        # Типы символов
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in "!@#$%^&*()-_=+[]{};:,.<>?/" for c in password)

        if has_lower:
            score += 1
        if has_upper:
            score += 1
        if has_digit:
            score += 1
        if has_symbol:
            score += 1

        # Бонус за разнообразие
        char_set_size = 0
        if has_lower:
            char_set_size += 26
        if has_upper:
            char_set_size += 26
        if has_digit:
            char_set_size += 10
        if has_symbol:
            char_set_size += 32

        # Рассчитываем энтропию (биты случайности)
        entropy = 0.0
        if char_set_size > 0:
            entropy = length * math.log2(char_set_size)

        # Бонус за высокую энтропию
        if entropy >= 60:
            score += 1
        if entropy >= 80:
            score += 1

        # Ограничиваем score
        score = min(score, 10)

        # Уровни безопасности
        if score <= 2:
            level = "Очень слабый"
            percent = 10
        elif score <= 4:
            level = "Слабый"
            percent = 30
        elif score <= 6:
            level = "Средний"
            percent = 50
        elif score <= 8:
            level = "Сильный"
            percent = 75
        else:
            level = "Очень сильный"
            percent = 100

        return level, percent, entropy