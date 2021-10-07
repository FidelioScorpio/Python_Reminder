from datetime import date, timedelta
from YearlyDate import YearlyDate, BirthdayDate
from WeeklyDate import WeeklyDate
from AppointmentDate import AppointmentDate

# Birthdays
BirthdayDate(date(1990,  2, 24), "Person A", "Person A's", reminder_length="1m")

# Reminders etc
YearlyDate(date(   1, 12, 25), "Christmas", last=False)
YearlyDate(date(2019,  4, 12), "MOT date", reminder_length="1m")

WeeklyDate(date(2021,  9, 15), "Roughly yearly", 52, reminder_length="1m", last=False)
WeeklyDate(date(2021,  9, 15), "biannual", 104, red_next=True, one_time=True, reminder_length="1m")
WeeklyDate(date(2021,  9, 16), "3 weeks' time", 3, red_next=True, one_time=True, reminder_length="2d")
WeeklyDate(date(2021, 10,  7), "Important thing", 7, reminder_length="6d", reminder_col="\033[1;31m")

AppointmentDate(date(2021, 10, 10), "A future appointment", reminder_length="1w")

print("\nHOW LONG AGO")
YearlyDate.how_long_ago()
print("\nWHAT IS NEXT")
# YearlyDate.what_is_next(date.today() + timedelta(days=20))
YearlyDate.what_is_next(10)
