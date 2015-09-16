from datetime import date, time


def get_availability_for_users(users, days):
    s1 = time(8, 0)
    e1 = time(11, 0)

    s2 = time(14, 15)
    e2 = time(16, 54)

    d1 = date(2015, 9, 16)
    return [{
                "date": d1,
                "times": [{"start": s1, "end": e1},
                          {"start": s2, "end": e2}]
             }]
