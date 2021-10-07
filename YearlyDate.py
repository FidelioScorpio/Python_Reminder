from datetime import date
from RecurringDate import RecurringDate


class YearlyDate(RecurringDate):

    def __init__(self, the_date, string1, string2="", last=True, one_time=False, reminder_length="1d",
                 mute=None):
        self._the_date = date(the_date.year, the_date.month, the_date.day)
        self._birthday = False
        self._last = last
        self._event = string1
        self._string2 = string2

        # check syntax via absence of crash:
        self.old_string_generator(y=1, m=1, d=1)
        self.new_string_generator(date(1, 1, 1), date(1, 1, 1))

        self.title = "[Yearly Event] {}".format(self._event)

        self.dates.append(self)
        self._oneTime = one_time
        self._reminder_delta = self.reminder_length_parser(reminder_length)
        self._mute = mute

    @property
    def the_date(self):
        """I'm the 'the_date' property."""
        return self._the_date

    @the_date.setter
    def the_date(self, value):
        self._the_date = value

    @property
    def reminder_delta(self):
        return self._reminder_delta

    def next_date(self, today=date.today()):
        if self._mute is not None and self._mute > today:
            today = self._mute
        if self._the_date.month == 2 and self._the_date.day == 29:
            year = 2012
            while True:
                year += 4
                if year % 100 == 0:
                    year += 4
                new_date = date(year, self._the_date.month, self._the_date.day)
                if new_date > today:
                    return new_date
        else:
            new_date = date(today.year, self._the_date.month, self._the_date.day)
            if new_date <= today:
                new_date = date(today.year + 1, self._the_date.month, self._the_date.day)
            return new_date

    def old_string_generator(self, y, m, d):
        if not self._last:
            return None
        if self._birthday:
            s = "{name} is {pretty_time} old"
            return s.format(name=self._name, pretty_time=self.get_pretty_time(y, m, d))
        elif self._event is None:
            return None
        else:
            s = "Last {event} was {pretty_time} ago"
            if self._string2 is not None:
                s = self._string2
            return s.format(event=self._event, pretty_time=self.get_pretty_time(y, m, d))

    def old_string_generator_should_have(self, y, m, d):
        return self.old_string_generator(y, m, d)

    def today_string_generator(self):
        if self._birthday:
            return "Today is {name_plural} birthday!".format(name_plural=self._name_plural)
        else:
            return "{event} is today".format(event=self._event)

    def new_string_generator(self, next_date, today):
        diff_year, diff_month, diff_day = self.date_difference(today, next_date)
        s = ""
        if diff_year == 0 and diff_month == 0 and diff_day == 0:
            s = self.today_string_generator() + "\n"
        if self._birthday:
            s += "{name_pl} next birthday is on " + self.new_string_generator_base(next_date, today)
            return s.format(name_pl=self._name_plural, y=next_date.year, m=next_date.month, d=next_date.day,
                            pretty_time=self.get_pretty_time(diff_year, diff_month, diff_day))
        elif self._event is None:
            return None
        else:
            s += "Next {event} is on " + self.new_string_generator_base(next_date, today)
            return s.format(event=self._event, y=next_date.year, m=next_date.month, d=next_date.day,
                            pretty_time=self.get_pretty_time(diff_year, diff_month, diff_day))


class BirthdayDate(YearlyDate):
    def __init__(self, the_date, string1, string2="", last=True, one_time=False, reminder_length="1d",
                 mute=None):
        super().__init__(the_date, string1, string2=string2, last=last, one_time=one_time,
                         reminder_length=reminder_length, mute=mute)
        self._birthday = True

        self._name = string1
        self._name_plural = string2

        self.title = "[Yearly Event] {} birthday".format(self._name_plural)