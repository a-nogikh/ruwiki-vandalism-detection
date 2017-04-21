from .feature import Feature
import re
from collections import defaultdict


class SandboxFeatures(Feature):
    sandbox_parts = [
        "'''Полужирное начертание'''",
        "''Курсивное начертание''",
        "== Текст заголовка ==",
        "=== Текст заголовка ===",
        "==== Текст заголовка ====",
        "===== Текст заголовка =====",
        "* Элемент маркированного списка",
        "# Элемент нумерованного списка",
        "<nowiki>Вставьте сюда текст, который не нужно форматировать</nowiki>",
        "<big>Крупный текст</big>",
        "<small>Мелкий текст</small>",
        "<sup>Надстрочный текст</sup>",
        "<sub>Подстрочный текст</sub>",
        "<gallery>\nExample.jpg|Описание1\nExample.jpg|Описание2\n</gallery>",
        "#перенаправление [[Название целевой страницы]]",
        "! Текст заголовка !! Текст заголовка !! Текст заголовка",
        "| Текст ячейки || Текст ячейки || Текст ячейки",
        "Название целевой страницы"
    ]

    def extract(self, raw):
        revs = Feature.revs(raw)
        curr_text = (revs["current"]['text'] if revs['current'] is not None else '') or ''
        prev_text = (revs['prev_user']['text'] if revs['prev_user'] is not None else '') or ''

        added = 0
        plain_added = 0
        for s in self.sandbox_parts:
            been = s in prev_text
            new = s in curr_text
            if been:
                added += -1
            if new:
                added += 1

            if not been and new:
                plain_added += 1

        res = {
            'sb_added': plain_added
        }

        return res
