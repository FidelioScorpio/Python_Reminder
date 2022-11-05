import abc
from datetime import date, timedelta
from calendar import monthrange, IllegalMonthError, day_name
import re

MAX_WEEKS = 104

class RecurringDate(metaclass=abc.ABCMeta):
    dates = list()
    title = "RecurringDate"

    reminder_col_now = "\033[1;31m"
    reminder_col_soon = "\033[1;33m"

    reminder_length_parser_re = re.compile("(?:(?P<years>\d+)y)?(?:(?P<months>\d+)m)?(?:(?P<weeks>\d+)w)?(?:(?P<days>\d+)d)?")

    @property
    @abc.abstractmethod
    def the_date(self):
        pass

    @property
    @abc.abstractmethod
    def reminder_delta(self):
        pass

    @staticmethod
    def date_difference(day1, day2):
        # Problems:
        # - It is impossible to be more accutate that weeks with no estimation (months and years are both variable length
        # - It is not useful to display only in immutable units (weeks and days)

        dyear = day2.year - day1.year
        dmonth = day2.month - day1.month
        dday = day2.day - day1.day
        if dday < 0:
            dmonth -= 1
            dday += monthrange(day1.year, day1.month)[1]
        if dmonth < 0:
            dyear -= 1
            dmonth += 12
        total_day_diff = (day2 - day1).days
        rem_day_diff = total_day_diff % 7
        rem_week_diff = int(total_day_diff / 7)
        # print("days diff is {}, rw {}, rd {}".format(total_day_diff, rem_week_diff, rem_day_diff))
        return dyear, dmonth, dday, rem_week_diff, rem_day_diff

    @staticmethod
    def get_pretty_time_wd(w, d):
        s = ""
        if w > 0:
            s += "{w} week"
            if w != 1:
                s += "s"
            if d > 0:
                s += " and "
            else:
                s += " "
        if (d > 0) or w == 0:
            s += "{d} day"
            if d != 1:
                s += "s "
            else:
                s += " "
        return s.strip().format(w=w, d=d)

    @staticmethod
    def get_pretty_time_ymd(y, m, d):
        s = ""
        if y > 0:
            s += "{y} year"
            if y != 1:
                s += "s"
            if (m > 0 and d == 0) or (m == 0 and d > 0):
                s += ", and "
            elif m > 0 and d > 0:
                s += ", "
            else:
                s += " "
        if m > 0:
            s += "{m} month"
            if m != 1:
                s += "s"
            if d > 0:
                s += " and "
            else:
                s += " "
        if (d > 0) or (m == 0 and y == 0):
            s += "{d} day"
            if d != 1:
                s += "s "
            else:
                s += " "
        return s.strip().format(y=y, m=m, d=d)

    @staticmethod
    def get_pretty_time(y, m, d, rw, rd):
        s = "{pretty_ymd}"
        if rw <= MAX_WEEKS:
            s = "{pretty_ymd} ({pretty_wd})"
        return s.format(pretty_ymd=RecurringDate.get_pretty_time_ymd(y,m,d), pretty_wd=RecurringDate.get_pretty_time_wd(rw,rd))

    @classmethod
    def reminder_length_parser(cls, reminder_length):
        # Expecting "(?:(?P<years>\d+)y)?(?:(?P<months>\d+)m)?(?:(?P<weeks>\d+)w)?(?:(?P<days>\d+)d)?"
        result = cls.reminder_length_parser_re.match(reminder_length)
        years = 0 if result.group("years") is None else int(result.group("years"))
        months = 0 if result.group("months") is None else int(result.group("months"))
        weeks = 0 if result.group("weeks") is None else int(result.group("weeks"))
        days = 0 if result.group("days") is None else int(result.group("days"))

        total = weeks + 4*months + 52*years  # get total weeks
        total = days + (7*total)
        delta = timedelta(total)
        return delta

    def string_date_colour(self, today=date.today()):
        next_date = self.next_date(today)
        colour_start = ""
        if next_date < today:
            colour_start = self.reminder_col_now
        elif next_date <= today + self.reminder_delta:
            colour_start = self.reminder_col_soon
        return colour_start

    def string_next_date(self, today=date.today()):
        next_date = self.next_date(today)
        if next_date is None:
            return "will not happen again"
        colour_start = self.string_date_colour(today)
        colour_end = "\033[0m"
        result = self.new_string_generator(next_date, today)
        if result is not None:
            return colour_start + result + colour_end

    def string_how_long_since_should_have(self, today=date.today(), other_day=None):
        diff_year, diff_month, diff_day, rw, rd = self.how_long_since(today, other_day)
        if diff_year == 0 and diff_month == 0 and diff_day == 0:  # TODO possibly remove this and put equivalent in old_string_generator_should_have
            return self.today_string_generator()
        if diff_year < 0 or (diff_year == 0 and diff_month < 0) or (diff_year == 0 and diff_month == 0 and diff_day < 0):
            return None  # Date is -ve
        return self.old_string_generator_should_have(y=diff_year, m=diff_month, d=diff_day, rw=rw, rd=rd)

    def string_how_long_since(self, today=date.today()):
        if self._event is None or not self._last:
            return None
        diff_year, diff_month, diff_day, rw, rd = self.how_long_since(today)
        if diff_year == 0 and diff_month == 0 and diff_day == 0:  # TODO possibly remove this and put equivalent in old_string_generator_should_have
            return self.today_string_generator()
        if diff_year < 0 or (diff_year == 0 and diff_month < 0) or (diff_year == 0 and diff_month == 0 and diff_day < 0):
            return None  # Date is -ve
        return self.old_string_generator(y=diff_year, m=diff_month, d=diff_day, rw=rw, rd=rd)

    def how_long_since(self, today, other_day=None):
        if other_day is None:
            other_day = self.the_date
        # Returns how long today is since the_date
        diff_year, diff_month, diff_day, rw, rd = self.date_difference(other_day, today)
        return diff_year, diff_month, diff_day, rw, rd

    def string_how_long_until(self, today=date.today()):
        next_date = self.next_date(today)
        if next_date is None:
            return "will not happen again"
        diff_year, diff_month, diff_day, rw, rd = self.date_difference(today, next_date)
        if diff_year == 0 and diff_month == 0 and diff_day == 0:
            return self.today_string_generator()
        return self.get_pretty_time(diff_year, diff_month, diff_day, rw,rd)

    @classmethod
    def what_is_next(cls, max_num=0, max_date=None):
        if type(max_num) == date:
            max_date = max_num
            max_num = 0
        dic = {}
        for recurring_date in cls.dates:
            if not issubclass(type(recurring_date), RecurringDate):
                continue
            dte = recurring_date.next_date()
            if dte is None:
                continue
            if dte in dic:
                dic[dte].append(recurring_date)
            else:
                dic[dte] = [recurring_date]

        sorted_keys = sorted(dic)

        for i in range(len(sorted_keys)):
            if (max_num == 0 or i < max_num) and \
               (max_date is None or sorted_keys[i] < max_date):
                # Print all the dates in this collection because they are within the maximums
                for dt in dic[sorted_keys[i]]:
                    next = dt.string_next_date()
                    if next is not None:
                        print(next)
            else:
                # Exceeds number or date. Only print if the reminder date is coloured
                for dt in dic[sorted_keys[i]]:
                    col = dt.string_date_colour()
                    if len(col) > 0:
                        next = dt.string_next_date()
                        if next is not None:
                            print(next)

    @classmethod
    def how_long_ago(cls):
        dic = {}
        for recurring_date in cls.dates:
            if not issubclass(type(recurring_date), RecurringDate):
                continue

            dte = recurring_date.the_date
            s = recurring_date.string_how_long_since()
            if s is not None and s != "":
                if dte in dic:
                    dic[dte].append(s)
                else:
                    dic[dte] = [s]

        sorted_keys = sorted(dic)
        for i in range(len(dic)):
            for s in dic[sorted_keys[i]]:
                print(s)

    @abc.abstractmethod
    def next_date(self, today):
        pass

    @abc.abstractmethod
    def today_string_generator(self):
        pass

    @abc.abstractmethod
    def new_string_generator(self, next_date, today):
        pass

    def new_string_generator_base(self, next_date, today):
        # Generate base text for WHAT IS NEXT
        if next_date < today:
            return self.string_how_long_since_should_have(today, next_date)
        diff_year, diff_month, diff_day, rw, rd = self.date_difference(today, next_date)
        s = "{d:02}/{m:02}/{y}, which is {pretty_time} away"

        # If the date is really soon, print 'Today' or 'next Tuesday for example
        if diff_year == 0 and diff_month == 0:
            if diff_day == 0:
                s = self.today_string_generator()
            elif diff_day <= 7:
                s += " ("
                today_day = today.weekday()
                nextday_day = next_date.weekday()
                if (today_day < 5 and nextday_day <= today_day) or \
                    (today_day == 5 and nextday_day == 5) or \
                    (today_day == 6 and nextday_day >= 5):
                    s += "next "
                s += day_name[nextday_day] + ")"
        return s

    @abc.abstractmethod
    def old_string_generator(self, y, m, d):
        pass

    @abc.abstractmethod
    def old_string_generator_should_have(self, y, m, d):
        pass
