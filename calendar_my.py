"""
Simple design change.
"""

from telegram_bot_calendar import DetailedTelegramCalendar


class MyStyleCalendar(DetailedTelegramCalendar):
    # previous and next buttons style. they are emoji now!
    prev_button = "⬅️"
    next_button = "➡️"
    # you do not want empty cells when month and year are being selected
    empty_month_button = ""
    empty_year_button = ""
    size_year=1
    size_year_column=2
