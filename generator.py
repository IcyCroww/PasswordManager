# generator.py
import random
import string


class PasswordGenerator:
    @staticmethod
    def generate(length=16, uppercase=True, digits=True, symbols=True) -> str:
        chars = string.ascii_lowercase
        if uppercase:
            chars += string.ascii_uppercase
        if digits:
            chars += string.digits
        if symbols:
            chars += "!@#$%^&*()-_=+[]{};:,.<>?/"

        return "".join(random.choice(chars) for _ in range(length))

    @staticmethod
    def estimate_strength(password: str) -> str:
        score = 0
        if len(password) >= 12:
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()-_=+[]{};:,.<>?/" for c in password):
            score += 1

        levels = ["Очень слабый", "Слабый", "Средний", "Сильный", "Очень сильный"]
        return levels[score]
