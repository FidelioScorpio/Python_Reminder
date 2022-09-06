import abc
from datetime import date, timedelta
from calendar import monthrange, IllegalMonthError, day_name
import re


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
        # TODO date-difference doesn't work properly...
        # TODO I have discovered that the month rollover fails when given a number of days that cannot fit into the month
        #  I have swapped the ifs in the dday< and dmonth< to fix an issue of getting month = -1 (when event <11mo away?)

        # This block is from ageDay.py. It may have other issues..
        dyear = day2.year - day1.year
        dmonth = day2.month - day1.month
        dday = day2.day - day1.day
        if dday < 0:
            dmonth -= 1
            dday += monthrange(day1.year, day1.month)[1]
        if dmonth < 0:
            dyear -= 1
            dmonth += 12
        return dyear, dmonth, dday
        # end of block from ageDay.py

        days_set, months_set, years_set = False, False, False
        days_num, months_num, years_num = 0, 0, 0
        days_temp, months_temp, years_temp = 0, 0, 0
        days_adjust, months_adjust, years_adjust = 0, 0, 0
        num = 0
        try:
            if day1 > day2:
                temp = day1
                day1 = day2
                day2 = temp
            while not (days_set and months_set and years_set):
                # try jump a year
                # if error, jump again etc
                # when not error, if date too high, rollback & set years_set
                num = 0
                while not years_set:
                    years_temp += 1
                    num += 1
                    try:
                        new_date = date(years_temp + years_num + day1.year, day1.month, day1.day)

                        # If date set worked, check it is valid
                        if new_date < day2:
                            # valid but still too small
                            years_num += num
                            years_adjust = years_temp
                            years_temp -= num
                            num = 0
                        elif new_date == day2:
                            years_num += num
                            years_set, months_set, days_set = True, True, True
                        else:
                            # we overshot, rollback & mark set
                            years_temp = years_adjust
                            years_set = True
                    except ValueError:  # day is out of range for month
                        pass

                num = 0
                while not months_set:
                    months_temp += 1
                    num += 1
                    try:
                        new_date = date(years_temp + years_num + day1.year, months_temp + months_num + day1.month,
                                        day1.day)

                        # If date set worked, check it is valid
                        if new_date < day2:
                            # valid but still too small
                            months_num += num
                            months_adjust = months_temp
                            months_temp -= num
                            num = 0
                        elif new_date == day2:
                            months_num += num
                            months_set, days_set = True, True
                        else:
                            # we overshot, rollback & mark set
                            months_temp = months_adjust
                            months_set = True
                    except ValueError:
                        if months_temp + months_num + day1.month < 1:
                            num -= 1  # redo this number of months because it wasn't a valid date
                            months_temp += 1
                        elif months_temp + months_num + day1.month > 12:
                            num -= 1  # redo this number of months because it wasn't a valid date
                            months_temp -= 13
                            years_temp += 1
                        # maybe the issue is that that number of days doesn't fit in that month..

                num = 0
                while not days_set:
                    days_temp += 1
                    num += 1
                    try:
                        new_date = date(years_temp + years_num + day1.year, months_temp + months_num + day1.month,
                                        days_temp + days_num + day1.day)

                        # If date set worked, check it is valid
                        if new_date < day2:
                            # valid but still too small
                            days_num += num
                            days_temp -= num
                            num = 0
                        elif new_date == day2:
                            days_num += num
                            days_set = True
                        else:
                            # we overshot, rollback & mark set
                            days_temp = 0
                            days_set = True
                    except ValueError:
                        num -= 1  # redo this number of days because it wasn't a valid date
                        if days_temp + days_num + day1.day < 1:
                            days_temp += 1
                        elif months_temp + months_num + day1.month < 1:
                            months_temp += 1
                        elif months_temp + months_num + day1.month > 12:
                            months_temp -= 13
                            years_temp += 1
                        elif days_temp + days_num + day1.day > monthrange(years_temp + years_num + day1.year,
                                                                          months_temp + months_num + day1.month)[1]:
                            days_temp -= 32
                            months_temp += 1
            return years_num, months_num, days_num
        except Exception as ex:
            print("date_difference error: {} (type = {})".format(ex, type(ex)))
            print("set: years_set = {}, months_set = {}, days_set = {}".format(years_set, months_set, days_set))
            print("     years_temp = {}, years_num = {}, day1.year = {}".format(years_temp, years_num, day1.year))
            print("     months_temp = {}, months_num = {}, day1.month = {}".format(months_temp, months_num, day1.month))
            print("     days_temp = {}, days_num = {}, day1.day = {}".format(days_temp, days_num, day1.day))
            print("date: {}/{}/{}".format(years_temp + years_num + day1.year, months_temp + months_num + day1.month,
                                          days_temp + days_num + day1.day))
            return None

    @staticmethod
    def get_pretty_time(y, m, d):
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

    def string_next_date(self, today=date.today()):
        next_date = self.next_date(today)
        colour_start = ""
        colour_end = ""
        if next_date is None:
            return "will not happen again"
        elif next_date < today:
            colour_start = self.reminder_col_now
            colour_end = "\033[0m"
        elif next_date <= today + self.reminder_delta:
            colour_start = self.reminder_col_soon
            colour_end = "\033[0m"
        result = self.new_string_generator(next_date, today)
        if result is not None:
            return colour_start + result + colour_end

    def string_how_long_since_should_have(self, today=date.today(), other_day=None):
        diff_year, diff_month, diff_day = self.how_long_since(today, other_day)
        if diff_year == 0 and diff_month == 0 and diff_day == 0:  # TODO possibly remove this and put equivalent in old_string_generator_should_have
            return self.today_string_generator()
        return self.old_string_generator_should_have(y=diff_year, m=diff_month, d=diff_day)

    def string_how_long_since(self, today=date.today()):
        if self._event is None or not self._last:
            return None
        diff_year, diff_month, diff_day = self.how_long_since(today)
        if diff_year == 0 and diff_month == 0 and diff_day == 0:  # TODO possibly remove this and put equivalent in old_string_generator_should_have
            return self.today_string_generator()
        return self.old_string_generator(y=diff_year, m=diff_month, d=diff_day)

    def how_long_since(self, today, other_day=None):
        if other_day is None:
            other_day = self.the_date
        # Returns how long today is since the_date
        diff_year, diff_month, diff_day = self.date_difference(other_day, today)
        return diff_year, diff_month, diff_day

    def string_how_long_until(self, today=date.today()):
        next_date = self.next_date(today)
        if next_date is None:
            return "will not happen again"
        diff_year, diff_month, diff_day = self.date_difference(today, next_date)
        if diff_year == 0 and diff_month == 0 and diff_day == 0:
            return self.today_string_generator()
        s = self.get_pretty_time(diff_year, diff_month, diff_day)

        return s.format(y=diff_year, m=diff_month, d=diff_day)

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
        if max_num == 0 or max_num > len(dic):
            max_num = len(dic)
        if max_date is None:
            max_date = sorted_keys[len(dic) - 1]
        for i in range(max_num):
            if sorted_keys[i] > max_date:
                break
            for dt in dic[sorted_keys[i]]:
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
        if next_date < today:
            return self.string_how_long_since_should_have(today, next_date)
        diff_year, diff_month, diff_day = self.date_difference(today, next_date)
        s = "{d:02}/{m:02}/{y}, which is {pretty_time} away"

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
