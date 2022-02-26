import datetime

from persiantools.jdatetime import JalaliDateTime


def jalali_to_gregorian(jalali_date_time: str):
    list_date_time = jalali_date_time.split(" ")
    date = list_date_time[0]
    time = list_date_time[1]
    year_month_day = date.split("-")
    hour_minute_second = time.split(":")
    return str(JalaliDateTime.to_gregorian(JalaliDateTime(year=int(year_month_day[0]),
                                                          month=int(year_month_day[1]),
                                                          day=int(year_month_day[2]),
                                                          hour=int(hour_minute_second[0]),
                                                          minute=int(hour_minute_second[1]),
                                                          second=int(hour_minute_second[2]),
                                                          microsecond=0)))


def gregorian_to_jalali(gregorian_date_time: str):
    list_date_time = gregorian_date_time.split(" ")
    date = list_date_time[0]
    time = list_date_time[1]
    year_month_day = date.split("-")
    hour_minute_second = time.split(":")
    return str(JalaliDateTime.to_jalali(year=int(year_month_day[0]),
                                        month=int(year_month_day[1]),
                                        day=int(year_month_day[2]),
                                        hour=int(hour_minute_second[0]),
                                        minute=int(hour_minute_second[1]),
                                        second=int(hour_minute_second[2]),
                                        microsecond=0))


def jalali_now():
    return str(JalaliDateTime.to_jalali(datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))


def gregorian_now():
    return str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    print(jalali_to_gregorian(jalali_date_time="1400-11-25 14:06:15"))
    print(gregorian_to_jalali(gregorian_date_time="2022-02-14 14:06:15"))
    print(jalali_now())
    print(gregorian_now())
