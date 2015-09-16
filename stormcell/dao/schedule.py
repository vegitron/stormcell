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


def merge_schedules(schedule_list):
    # Start by combining all events for a day into a list
    days = {}
    d_obj = {}
    for schedule in schedule_list:
        for day in schedule:
            d_str = str(day["date"])
            d_obj[d_str] = day["date"]
            if d_str not in days:
                days[d_str] = []

            days[d_str].extend(day["times"])

    merged_schedule = []
    # Merge each day's events
    for day in days:
        days[day] = merge_day(days[day])
        # Put the per-day data back into schedule format
        merged_schedule.append({
                                "date": d_obj[day],
                                "times": days[day],
                                })

    return merged_schedule


def merge_day(day):
    by_time = sorted(day, key=lambda x: x["start"])

    ranges = []

    current_range = None
    for meeting in by_time:
        if not current_range:
            current_range = meeting
        else:
            if meeting["start"] > current_range["end"]:
                ranges.append(current_range)
                current_range = meeting
            elif meeting["end"] > current_range["end"]:
                current_range["end"] = meeting["end"]

    if current_range:
        ranges.append(current_range)

    return ranges
