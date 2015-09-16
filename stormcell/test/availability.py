from django.test import TestCase
from datetime import date, time
from stormcell.dao.schedule import merge_schedules


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
