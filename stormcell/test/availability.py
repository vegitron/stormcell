from django.test import TestCase
from datetime import date, time
from stormcell.dao.schedule import merge_schedules
from stormcell.dao.schedule import get_availability


class TestCombo(TestCase):
    """
    Tests that we collapse sets of meetings into correct availability info.
    """
    def test_merging_events(self):
        d1 = date(2015, 9, 16)

        t0 = time(9, 0)
        t1 = time(11, 0)
        t2 = time(12, 0)
        t3 = time(14, 0)
        t4 = time(15, 0)
        t5 = time(16, 0)

        s1 = [{"date": d1, "times": [
                                     {"start": t0, "end": t2},
                                     ]
               },
              ]

        s2 = [{"date": d1, "times": [
                                     {"start": t3, "end": t5},
                                     ]
               },
              ]

        s3 = [{"date": d1, "times": [
                                     {"start": t1, "end": t4},
                                     ]
               },
              ]

        merged = merge_schedules((s1, s2, s3))
        self.assertEquals(len(merged), 1)
        self.assertEquals(merged[0]["date"], d1)
        self.assertEquals(len(merged[0]["times"]), 1)
        self.assertEquals(merged[0]["times"][0]["start"], t0)
        self.assertEquals(merged[0]["times"][0]["end"], t5)

    def test_no_meetings(self):
        d1 = date(2015, 9, 16)

        t0 = time(6, 0)
        t1 = time(7, 0)

        s1 = [{"date": d1, "times": []}]

        # Find times for a 30 minute meeting
        available = get_availability(s1, d1, d1, 30)
        self.assertEquals(len(available), 1)
        self.assertEquals(available[0]["date"], d1)
        self.assertEquals(len(available[0]["times"]), 2)
        self.assertEquals(available[0]["times"][0]["start"], time(9, 0))
        self.assertEquals(available[0]["times"][0]["end"], time(12, 0))
        self.assertEquals(available[0]["times"][1]["start"], time(13, 0))
        self.assertEquals(available[0]["times"][1]["end"], time(17, 0))

    def test_early_meeting_only(self):
        d1 = date(2015, 9, 16)

        t0 = time(6, 0)
        t1 = time(7, 0)

        s1 = [{"date": d1, "times": [
                                     {"start": t0, "end": t1},
                                     ]}]

        # Find times for a 30 minute meeting
        available = get_availability(s1, d1, d1, 30)
        self.assertEquals(len(available), 1)
        self.assertEquals(available[0]["date"], d1)
        self.assertEquals(len(available[0]["times"]), 2)
        self.assertEquals(available[0]["times"][0]["start"], time(9, 0))
        self.assertEquals(available[0]["times"][0]["end"], time(12, 0))
        self.assertEquals(available[0]["times"][1]["start"], time(13, 0))
        self.assertEquals(available[0]["times"][1]["end"], time(17, 0))

    def test_early_meeting_ending_after_start_of_day_only(self):
        d1 = date(2015, 9, 16)

        t0 = time(6, 0)
        t1 = time(10, 0)

        s1 = [{"date": d1, "times": [
                                     {"start": t0, "end": t1},
                                     ]}]

        # Find times for a 30 minute meeting
        available = get_availability(s1, d1, d1, 30)
        self.assertEquals(len(available), 1)
        self.assertEquals(available[0]["date"], d1)
        self.assertEquals(len(available[0]["times"]), 2)
        self.assertEquals(available[0]["times"][0]["start"], time(10, 0))
        self.assertEquals(available[0]["times"][0]["end"], time(12, 0))
        self.assertEquals(available[0]["times"][1]["start"], time(13, 0))
        self.assertEquals(available[0]["times"][1]["end"], time(17, 0))

    def test_early_meeting_ending_after_lunch_only(self):
        d1 = date(2015, 9, 16)

        t0 = time(6, 0)
        t1 = time(14, 0)

        s1 = [{"date": d1, "times": [
                                     {"start": t0, "end": t1},
                                     ]}]

        # Find times for a 30 minute meeting
        available = get_availability(s1, d1, d1, 30)
        self.assertEquals(len(available), 1)
        self.assertEquals(available[0]["date"], d1)
        self.assertEquals(len(available[0]["times"]), 1)
        self.assertEquals(available[0]["times"][0]["start"], time(14, 0))
        self.assertEquals(available[0]["times"][0]["end"], time(17, 0))

    def test_morning_meeting(self):
        d1 = date(2015, 9, 16)

        t0 = time(10, 0)
        t1 = time(11, 0)

        s1 = [{"date": d1, "times": [
                                     {"start": t0, "end": t1},
                                     ]}]

        # Find times for a 30 minute meeting
        available = get_availability(s1, d1, d1, 30)
        self.assertEquals(len(available), 1)
        self.assertEquals(available[0]["date"], d1)
        self.assertEquals(len(available[0]["times"]), 3)
        self.assertEquals(available[0]["times"][0]["start"], time(9, 0))
        self.assertEquals(available[0]["times"][0]["end"], time(10, 0))
        self.assertEquals(available[0]["times"][1]["start"], time(11, 0))
        self.assertEquals(available[0]["times"][1]["end"], time(12, 0))
        self.assertEquals(available[0]["times"][2]["start"], time(13, 0))
        self.assertEquals(available[0]["times"][2]["end"], time(17, 0))

    def test_three_empty_days(self):
        d1 = date(2015, 9, 16)
        d2 = date(2015, 9, 17)
        d3 = date(2015, 9, 18)

        s1 = []
        available = get_availability(s1, d1, d3, 30)
        self.assertEquals(len(available), 3)
        self.assertEquals(available[0]["date"], d1)
        self.assertEquals(available[1]["date"], d2)
        self.assertEquals(available[2]["date"], d3)
        self.assertEquals(len(available[0]["times"]), 2)
        self.assertEquals(available[0]["times"][0]["start"], time(9, 0))
        self.assertEquals(available[0]["times"][0]["end"], time(12, 0))
        self.assertEquals(available[0]["times"][1]["start"], time(13, 0))
        self.assertEquals(available[0]["times"][1]["end"], time(17, 0))

        self.assertEquals(len(available[1]["times"]), 2)
        self.assertEquals(available[1]["times"][0]["start"], time(9, 0))
        self.assertEquals(available[1]["times"][0]["end"], time(12, 0))
        self.assertEquals(available[1]["times"][1]["start"], time(13, 0))
        self.assertEquals(available[1]["times"][1]["end"], time(17, 0))

        self.assertEquals(len(available[2]["times"]), 2)
        self.assertEquals(available[2]["times"][0]["start"], time(9, 0))
        self.assertEquals(available[2]["times"][0]["end"], time(12, 0))
        self.assertEquals(available[2]["times"][1]["start"], time(13, 0))
        self.assertEquals(available[2]["times"][1]["end"], time(17, 0))

    def test_several_days_unsorted(self):
        schedule = [{'date': date(2015, 9, 24),
                     'times': [{'start': time(9, 45), 'end': time(12, 0)}]},
                    {'date': date(2015, 9, 18),
                     'times': [{'start': time(9, 45), 'end': time(10, 0)},
                               {'start': time(11, 0), 'end': time(12, 0)}]},
                    {'date': date(2015, 9, 19),
                     'times': [{'start': time(8, 0), 'end': time(17, 0)}]},
                    {'date': date(2015, 9, 21),
                     'times': [{'start': time(9, 30), 'end': time(10, 30)},
                               {'start': time(15, 30), 'end': time(16, 30)}]},
                    {'date': date(2015, 9, 23),
                     'times': [{'start': time(9, 45), 'end': time(10, 0)}]},
                    {'date': date(2015, 9, 22),
                     'times': [{'start': time(9, 45), 'end': time(10, 0)},
                               {'start': time(11, 30), 'end': time(13, 30)}]}]

        d1 = date(2015, 9, 18)
        d2 = date(2015, 9, 25)

        available = get_availability(schedule, d1, d2, 30)

        self.assertEquals(len(available), 8)
        self.assertEquals(available[0]["date"], date(2015, 9, 18))
        self.assertEquals(available[1]["date"], date(2015, 9, 19))
        self.assertEquals(available[2]["date"], date(2015, 9, 20))
        self.assertEquals(available[3]["date"], date(2015, 9, 21))
        self.assertEquals(available[4]["date"], date(2015, 9, 22))
        self.assertEquals(available[5]["date"], date(2015, 9, 23))
        self.assertEquals(available[6]["date"], date(2015, 9, 24))
        self.assertEquals(available[7]["date"], date(2015, 9, 25))

        self.assertEquals(len(available[0]["times"]), 3)
