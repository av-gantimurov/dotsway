#!/usr/bin/env python
import sys
from datetime import date

words = ["день", "дня", "дней"]

try:
    d = date.fromisoformat(sys.argv[1])
except Exception:
    d = date(2025, 8, 1)


def get_plural(value: int) -> str:
    if all((value % 10 == 1, value % 100 != 11)):
        return words[0]
    elif all((2 <= value % 10 <= 4, any((value % 100 < 10, value % 100 >= 20)))):
        return words[1]
    return words[2]


days = (d - date.today()).days - 1
print(f"{days} {get_plural(days)}")
