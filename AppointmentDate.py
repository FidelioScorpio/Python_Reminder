from datetime import date
from RecurringDate import RecurringDate


class AppointmentDate(RecurringDate):

    def __init__(self, the_date, string1, predicted=False, reminder_length="1d"):
        self._the_date = date(the_date.year, the_date.month, the_date.day)
        self._event = string1
        self._predicted = predicted

        # check syntax via absence of crash:
        self.old_string_generator(y=1, m=1, d=1)
        self.new_string_generator(date(1, 1, 1), date(1, 1, 1))

        self.title = "[Appointment Event] {}".format(self._event)

        self.dates.append(self)
        self._reminder_delta = self.reminder_length_parser(reminder_length)

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
        return self.the_date

    def old_string_generator(self, y, m, d):
        return None

    def old_string_generator_should_have(self, y, m, d):
        predicted = "is predicted to" if self._predicted else "should"
        s = "{event} {predicted} have been {pretty_time} ago"
        return s.format(event=self._event, pretty_time=self.get_pretty_time(y, m, d), predicted=predicted)

    def today_string_generator(self, predicted="is"):
        return "{event} {predicted} today".format(event=self._event, predicted=predicted)

    def new_string_generator(self, next_date, today):
        if next_date < today:
            return self.string_how_long_since_should_have(today, next_date)
        diff_year, diff_month, diff_day = self.date_difference(today, next_date)
        s = ""
        predicted = "is predicted to happen" if self._predicted else "is"
        if diff_year == 0 and diff_month == 0 and diff_day == 0:
            s += self.today_string_generator(predicted)
        else:
            s += "{event} {predicted} on " + self.new_string_generator_base(next_date, today)

        return s.format(event=self._event, y=next_date.year, m=next_date.month, d=next_date.day,
                        pretty_time=self.get_pretty_time(diff_year, diff_month, diff_day), predicted=predicted)

