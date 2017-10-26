import calendar
import datetime
import pprint

WEEKDAYS = {day: i for i, day in enumerate(calendar.day_name)}
# For England & Wales - don't include Scottish Holidays
BANK_HOLIDAYS = {
    datetime.date(2017, 1, 1): ('NewYearsDay', 'AllHolidaysExceptChristmas'),
    datetime.date(2017, 4, 14): ('GoodFriday', 'AllHolidaysExceptChristmas'),
    datetime.date(2017, 4, 17): ('EasterMonday', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2017, 5, 1): ('MayDay', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2017, 5, 29): ('SpringBank', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2017, 8, 28): ('LateSummerBankHolidayNotScotland', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2017, 12, 25): ('ChristmasDay', 'Christmas'),
    datetime.date(2017, 12, 26): ('BoxingDay', 'Christmas'),

    datetime.date(2018, 1, 1): ('NewYearsDay', 'AllHolidaysExceptChristmas'),
    datetime.date(2018, 3, 30): ('GoodFriday', 'AllHolidaysExceptChristmas'),
    datetime.date(2018, 4, 2): ('EasterMonday', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2018, 5, 7): ('MayDay', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2018, 5, 28): ('SpringBank', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2018, 8, 27): ('LateSummerBankHolidayNotScotland', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2018, 12, 25): ('ChristmasDay', 'Christmas'),
    datetime.date(2018, 12, 26): ('BoxingDay', 'Christmas'),

    datetime.date(2019, 1, 1): ('NewYearsDay', 'AllHolidaysExceptChristmas'),
    datetime.date(2019, 4, 19): ('GoodFriday', 'AllHolidaysExceptChristmas'),
    datetime.date(2019, 4, 22): ('EasterMonday', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2019, 5, 6): ('MayDay', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2019, 5, 27): ('SpringBank', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2019, 8, 26): ('LateSummerBankHolidayNotScotland', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2019, 12, 25): ('ChristmasDay', 'Christmas'),
    datetime.date(2019, 12, 26): ('BoxingDay', 'Christmas'),

    datetime.date(2019, 1, 1): ('NewYearsDay', 'AllHolidaysExceptChristmas'),
    datetime.date(2019, 4, 10): ('GoodFriday', 'AllHolidaysExceptChristmas'),
    datetime.date(2019, 4, 13): ('EasterMonday', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2019, 5, 4): ('MayDay', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2019, 5, 25): ('SpringBank', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2019, 8, 31): ('LateSummerBankHolidayNotScotland', 'HolidayMondays', 'AllHolidaysExceptChristmas'),
    datetime.date(2019, 12, 25): ('ChristmasDay', 'Christmas'),
    datetime.date(2019, 12, 26): ('BoxingDay', 'Christmas'),
    datetime.date(2019, 12, 28): ('BoxingDayHoliday', 'DisplacementHolidays')
}

class DayOfWeek(object):
    def __init__(self, day):
        if isinstance(day, int):
            self.day = day
        else:
            self.day = WEEKDAYS[day]

    def __eq__(self, other):
        if type(other) == int:
            return self.day == other
        return self.day == other.day

    def __repr__(self):
        return calendar.day_name[self.day]

class DateRange(object):
    # Use this to represent the object that will later be stored in the database as a DateRangeField
    # https://docs.djangoproject.com/en/1.11/ref/contrib/postgres/fields/#django.contrib.postgres.fields.DateRangeField
    def __init__(self, element):
        print(repr(element))
        self.start = datetime.datetime.strptime(element['StartDate'], '%Y-%m-%d').date()
        self.end = datetime.datetime.strptime(element['EndDate'], '%Y-%m-%d').date()

    def contains(self, date):
        return self.start <= date and (not self.end or self.end >= date)


class OperatingProfile(object):
    def __init__(self, element):

        self.regular_days = []
        self.nonoperation_days = []
        self.operation_days = []
        self.nonoperation_bank_holidays = []
        self.operation_bank_holidays = []

        # RegularDayType
        if 'RegularDayType' in element and 'DaysOfWeek' in element['RegularDayType']:
            week_days_element = element['RegularDayType']['DaysOfWeek']
            for day in list(week_days_element.keys()):
                if 'To' in day:
                    day_range_bounds = [WEEKDAYS[i] for i in day.split('To')]
                    day_range = range(day_range_bounds[0], day_range_bounds[1] + 1)
                    self.regular_days += [DayOfWeek(i) for i in day_range]
                elif day == 'Weekend':
                    self.regular_days += [DayOfWeek(5), DayOfWeek(6)]
                else:
                    self.regular_days.append(DayOfWeek(day))

        # PeriodicDayType -- NOT IMPLIMENTED

        # ServicedOrganisationDayType -- NOT IMPLIMENTED

        # SpecialDaysOperation
        if 'SpecialDaysOperation' in element:
            if 'DaysOfNonOperation' in element['SpecialDaysOperation']:
                self.nonoperation_days = list(map(DateRange, element['SpecialDaysOperation']['DaysOfNonOperation']['DateRange']))
            if 'DaysOfOperation' in element['SpecialDaysOperation']:
                self.operation_days = list(map(DateRange, element['SpecialDaysOperation']['DaysOfOperation']['DateRange']))

        # BankHolidayOperation
        if 'BankHolidayOperation' in element:
            if 'DaysOfNonOperation' in element['BankHolidayOperation']:
                self.nonoperation_bank_holidays = list(element['BankHolidayOperation']['DaysOfNonOperation'].keys())
            else:
                self.nonoperation_bank_holidays = []
            if 'DaysOfOperation' in element['BankHolidayOperation']:
                self.operation_bank_holidays = list(element['BankHolidayOperation']['DaysOfOperation'].keys())
            else:
                self.operation_bank_holidays = []

    def __repr__(self):
        return (pprint.pformat(self.regular_days) +
            pprint.pformat(self.nonoperation_days) +
            pprint.pformat(self.operation_days) +
            pprint.pformat(self.nonoperation_bank_holidays) +
            pprint.pformat(self.operation_bank_holidays))

    def should_show(self, date):
        '''
        Should an entity with this OperatingProfile be shown fo (i.e.
        does it run on) date
        '''

        # "days of explicit non-operation should be interpreted as
        # further constraining the days of week and month of the
        # Normal Operating Profile" (3.15.2, Schema Guide 2.1)
        #...and...
        # "If conflicting dates are specified, days of non-operation
        # are given precedence (6.9.2.4, Schema Guide 2.1)
        for daterange in self.nonoperation_days:
            if daterange.contains(date):
                return False

        if date in BANK_HOLIDAYS:
            if 'AllBankHolidays' in self.nonoperation_bank_holidays:
                return False
            for bank_holiday in BANK_HOLIDAYS[date]:
                if bank_holiday in self.nonoperation_bank_holidays:
                    return False

        # "days of explicit operation should be interpreted as being
        # additive" (3.15.2, Schema Guide 2.1)
        for daterange in self.operation_days:
            if daterange.contains(date):
                return True

        if date in BANK_HOLIDAYS:
            if 'AllBankHolidays' in self.operation_bank_holidays:
                return True
            for bank_holiday in BANK_HOLIDAYS[date]:
                if bank_holiday in self.operation_bank_holidays:
                    return True

        if date.weekday() in self.regular_days:
            return True

        return False

    def defaults_from(self, defaults):
        '''
        Merge this object with a second one containing defaults according to the rules in the schema guide.
        '''
        pass
