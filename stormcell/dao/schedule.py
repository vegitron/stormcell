from datetime import date, time, timedelta


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


def get_availability(schedule, start_date, end_date, duration):
    """
    requires that the schedule be a merged schedule from merge_schedules
    """
    if end_date < start_date:
        raise Exception("End date (%s) is less than start date (%s)",
                        str(end_date),
                        str(start_date))

    days = {}
    d_obj = {}

    # This takes the stance that meetings can be scheduled between 9 and 12,
    # or between 1 and 5.  No lunch meetings!  (I expect this will need to
    # change at some point)
    midnight = time(0, 0)
    start_of_day = time(9, 0)
    noon = time(12, 0)
    after_lunch = time(13, 0)
    end_of_day = time(17, 0)
    end_midnight = time(23, 59, 59)

    # Create "booked" periods for before and after work, and lunch:
    off_limits = [
                  {"start": midnight, "end": start_of_day},
                  {"start": noon, "end": after_lunch},
                  {"start": end_of_day, "end": end_midnight},
                  ]

    # Build a schedule over the days listed that has blocked off time
    test_date = start_date
    blocked_off = []
    while test_date <= end_date:
        blocked_off.append({"date": test_date, "times": off_limits})
        test_date += timedelta(days=1)

    schedule = merge_schedules([schedule, blocked_off])

    for day in schedule:
        d_str = str(day["date"])
        d_obj[d_str] = day["date"]

        days[d_str] = sorted(day["times"], key=lambda x: x["start"])

    dates_with_availability = []

    test_date = start_date
    while test_date <= end_date:
        d_str = str(test_date)

        day_windows = []

        reached_start_of_day = False

        last_end = None
        for event in days[d_str]:
            ev_start = event["start"]
            ev_end = event["end"]

            # The first event is the midnight block.  So we can just track
            # it's end time
            if not last_end:
                last_end = ev_end
                continue

            day_windows.append({"start": last_end, "end": ev_start})
            last_end = ev_end

            # The last event of the day is the block to the final midnight,
            # So we don't need to worry about having availability after it.

        dates_with_availability.append({"date": test_date,
                                        "times": day_windows})

        test_date += timedelta(days=1)

    return dates_with_availability
