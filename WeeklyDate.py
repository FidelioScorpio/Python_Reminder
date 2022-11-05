from datetime import date, timedelta
from RecurringDate import RecurringDate


class WeeklyDate(RecurringDate):
    
    def __init__(self, the_date, event, num_weeks=1, predicted=False, last=True, red_next=False, one_time=False, reminder_length="1d", reminder_col=""):
        self._the_date = date(the_date.year, the_date.month, the_date.day)
        self._event = event
        self._predicted = predicted
        self._last = last
        self._red_next = red_next
        if red_next:
            self._last = False
        self._num_weeks = int(num_weeks)
        if self._num_weeks < 0:
            raise ValueError("numWeeks should be positive")
        
        self.title = "[Weekly Event ({})] {}".format(self._num_weeks, event)
        self.dates.append(self)
        self._oneTime = one_time
        self._reminder_delta = self.reminder_length_parser(reminder_length)
        if reminder_col != "":
            self.reminder_col_soon = reminder_col
            
        # check syntax via absence of crash:
        self.old_string_generator(y=1, m=1, d=1, rw=1, rd=1)
        self.new_string_generator(date(1, 1, 1), date(1, 1, 1))

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
        if self._num_weeks == 0:
            return None
        new_date = self._the_date + timedelta(self._num_weeks * 7)

        if not self._oneTime:
            while new_date <= today:
                new_date = new_date + timedelta(self._num_weeks * 7)
        return new_date

    def old_string_generator(self, y, m, d, rw, rd):
        if self._event is None or not self._last:
            return None
        s = "{event} was {pretty_time} ago"
        return s.format(event=self._event, pretty_time=self.get_pretty_time(y, m, d, rw, rd))

    def old_string_generator_should_have(self, y, m, d, rw, rd):
        if self._event is None or not self._red_next:
            return None
        s = "{event} should have been {pretty_time} ago"
        return s.format(event=self._event, pretty_time=self.get_pretty_time(y, m, d, rw, rd))

    def today_string_generator(self, predicted="is"):
        return "{event} {predicted} today".format(event=self._event, predicted=predicted)
        
    def new_string_generator(self, next_date, today):
        if next_date < today:
            return self.string_how_long_since_should_have(today, next_date)
        diff_year, diff_month, diff_day, rw, rd = self.date_difference(today, next_date)
        s = ""
        predicted = "is predicted to happen" if self._predicted else "is"
        if self._num_weeks == 0:
            if diff_year == 0 and diff_month == 0 and diff_day == 0:
                s += self.today_string_generator(predicted) + " and will not happen again"
            else:
                s += "{event} will not happen again"
        else:
            if diff_year == 0 and diff_month == 0 and diff_day == 0:
                s += self.today_string_generator(predicted)
            else:
                s += "Next {event} {predicted} on " + self.new_string_generator_base(next_date, today)

        return s.format(event=self._event, y=next_date.year, m=next_date.month, d=next_date.day,
                        pretty_time=self.get_pretty_time(diff_year, diff_month, diff_day, rw, rd), predicted=predicted)
