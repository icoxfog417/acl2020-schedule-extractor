import unittest
from datetime import datetime
import pytest
from extractor.schedule_reader import ScheduleReader
from extractor.schedule_reader import Paper, PaperIndex


@pytest.mark.usefixtures("path_to_anthology")
class TestScheduleReader(unittest.TestCase):

    def test_day(self):
        index = PaperIndex()
        text = "Monday, July 6, 2020 UTC+0 (continued)"
        self.assertTrue(index.set_day(text))

    def test_time(self):
        index = PaperIndex()
        index.day = datetime(year=2020, month=1, day=3)
        text = "05:15–06:00"
        self.assertTrue(index.set_time(text))
        self.assertEqual(index.day.hour, 5)
        self.assertEqual(index.day.minute, 15)

    def test_paper(self):
        text = "\n".join(["[Long] A Study of Non-autoregressive Model for Sequence Generation",
                          "Yi Ren, Jinglin Liu, Xu Tan, Zhou Zhao, sheng zhao and Tie-Yan Liu"])
        paper = Paper.parse(text)
        self.assertTrue(paper is not None)
        self.assertEqual(paper.title, "A Study of Non-autoregressive Model for Sequence Generation")
        self.assertEqual(paper.kind, "Long")
        self.assertEqual(paper.authors, "Yi Ren, Jinglin Liu, Xu Tan, Zhou Zhao, sheng zhao and Tie-Yan Liu")

    def test_schedule_read(self):
        reader = ScheduleReader(self._path)
        papers = reader.iterate_papers(start_page=76, end_page=77)
        for p in papers:
            print(p.to_json())
        self.assertEqual(len(papers), 19)
