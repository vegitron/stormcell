from datetime import date, time, timedelta, datetime
from dateutil.parser import parse
from apiclient.discovery import build
import httplib2
import re
from stormcell.models import GoogleOauth, CredentialsModel
from oauth2client.django_orm import Storage


def get_availability_for_users(users, days):
    start = datetime.utcnow()
    end = start + timedelta(days=7)

    schedules = []
    for user in users:
        google_access_tokens = GoogleOauth.objects.filter(user=user)
        for token in google_access_tokens:
            schedule = get_google_schedule(token, start, end)
            schedules.append(schedule)

    merged = merge_schedules(schedules)
    return get_availability(merged, start.date(), end.date(), 30)


def get_google_schedule(token, start, end):
    http = httplib2.Http()
    credential_id = token.credential_id
    storage = Storage(CredentialsModel,
                      'id',
                      credential_id,
                      'credential')

    credential = storage.get()
    credential.authorize(http)
    service = build('calendar', 'v3', http=http)

    now = start.isoformat()+'Z'
    end = end.isoformat()+'Z'

    base_data = {}

    page_token = None
    while True:
        calendar_list = service.calendarList().list(
            pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            cal_id = calendar_list_entry['id']
            next_events_token = None
            # Skip the holiday calendars
            if re.match('.*#holiday@group.v.calendar.google.com', cal_id):
                continue
            if re.match('.*@holiday.calendar.google.com', cal_id):
                continue

            # Skip the birthdays calendar
            if '#contacts@group.v.calendar.google.com' == cal_id:
                continue

            # get all the events for this calendar
            while True:
                events = service.events().list(
                    calendarId=cal_id, timeMin=now, timeMax=end,
                    singleEvents=True, orderBy='startTime',
                    pageToken=next_events_token).execute()

                next_events_token = events.get('nextPageToken')
                for event in events.get('items', []):
                    _add_google_event_to_basic_hash(event, base_data)

                if not next_events_token:
                    break

        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    return _turn_basic_hash_into_schedule(base_data)


def _turn_basic_hash_into_schedule(data):
    schedule = []
    for key in sorted(data):
        schedule.append(data[key])

    return schedule


def _add_google_event_to_basic_hash(event, data):
    start = event['start'].get('dateTime')
    end = event['end'].get('dateTime')

    if not start or not end:
        # TODO - handle all day events
        print("Doesn't handle all day events yet :(")
        return

    start_obj = parse(start)
    end_obj = parse(end)

    start_date = start_obj.date()
    end_date = end_obj.date()

    if (start_date != end_date):
        # TODO - handle spanning events
        print("Doesn't handle events spanning days yet")
        return

    date_str = str(start_date)
    if date_str not in data:
        data[date_str] = {"date": start_date, "times": []}

    data[date_str]["times"].append({"start": start_obj.time(),
                                    "end": end_obj.time()})


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
    new_days = {}
    # Merge each day's events
    for day in days:
        new_days[day] = merge_day(days[day])
        # Put the per-day data back into schedule format
        merged_schedule.append({
                                "date": d_obj[day],
                                "times": new_days[day],
                                })

    return merged_schedule


def merge_day(day):
    by_time = sorted(day, key=lambda x: x["start"])

    ranges = []

    current_range = None
    for meeting in by_time:
        if not current_range:
            current_range = {"start": meeting["start"], "end": meeting["end"]}
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
