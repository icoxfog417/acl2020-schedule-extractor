import re
from datetime import datetime
from extractor.pdf_reader import PDFReader


class ScheduleReader():
    """
    Extract schedule from ACL2020 anthology.
    Link: https://acl2020.org/schedule/
    """

    def __init__(self, acl_schedule_path):
        self.path = acl_schedule_path
        self.start_default = 74
        self.end_default = None

    def iterate_papers(self, start_page=-1, end_page=None):
        start = start_page if start_page > 0 else self.start_default
        end = end_page if end_page is not None else self.end_default
        reader = PDFReader(self.path)

        index = PaperIndex()
        papers = []
        next_is_session = False
        for texts in reader.iterate_page_texts(start, end):
            for t in texts:
                line = t.strip()
                if index.set_day(line):
                    continue
                elif index.set_time(line):
                    remain = line.replace(index.time, "").strip()
                    if len(remain) > 2:
                        index.set_session(remain)
                        next_is_session = False
                    else:
                        next_is_session = True
                    continue
                elif next_is_session and line:
                    if line.startswith("["):
                        next_is_session = False
                    else:
                        index.set_session(line)
                        next_is_session = False
                        continue

                paper = Paper.parse(t, index.clone())
                if paper is not None:
                    papers.append(paper)

        return papers


class Paper():

    def __init__(self, title, kind, authors, index=None):
        self.title = title
        self.kind = kind
        self.authors = authors
        self.index = index

    @classmethod
    def parse(cls, text, index=None):
        kind = re.match(r"\[.+?\]", text)
        if kind is None:
            return None

        kind = kind.group(0)
        title_authors = text.strip().split("\n")
        title_authors = [t for t in title_authors if t.strip()]
        border = -1
        if len(title_authors) > 2:
            for t in reversed(title_authors):
                if len(t.split(", ")) > 2:
                    border = border - 1

        title = " ".join(title_authors[:border]).strip()
        authors = " ".join(title_authors[border:]).strip()
        if authors[0].islower():
            remain_title_and_authors = authors.split(", ")
            remain = remain_title_and_authors[0].split(" ")
            remain = " ".join(remain[:-2])
            title = title[:-1] + remain
            authors = authors.replace(remain, "").strip()
        title = title.replace(kind, "").strip()
        kind = kind.replace("[", "").replace("]", "")
        return cls(title, kind, authors, index)

    def to_json(self, include_time_to_day=False):
        info = {
            "title": self.title,
            "kind": self.kind,
            "authors": self.authors
        }
        if self.index is not None:
            if include_time_to_day:
                info["day"] = self.index.day.strftime("%Y/%m/%d %H:%M")
            else:
                info["day"] = self.index.day.strftime("%Y/%m/%d")
                info["time"] = self.index.time

            info["session"] = self.index.session
            info["category"] = self.index.category
        return info


class PaperIndex():

    def __init__(self, day=None, time=None, session=None):
        self.day = day
        self.time = time
        self.session = session

    @property
    def category(self):
        if self.session is None:
            return None
        elif not self.session.startswith("Session"):
            return ""
        else:
            category = self.session.split(" ")[2:]
            category = " ".join(category).split("-")
            category = category[0]
            return category

    def clone(self):
        return PaperIndex(self.day, self.time, self.session)

    def is_full(self):
        indexes = (self.day, self.time, self.session)
        has_indexes = [1 if x is not None else 0 for x in indexes]
        if sum(has_indexes) == len(indexes):
            return True
        else:
            return False

    def set_day(self, text):
        utc = "UTC+0"
        if utc not in text:
            return None
        _text = text[:(text.index(utc) + len(utc) - 2)]
        day = None
        try:
            day = datetime.strptime(_text, "%A, %B %d, %Y %Z")
            self.day = day
            self.time = None
            self.session = None
        except Exception as ex:
            day = None
        return (day is not None)

    def set_time(self, text):
        matched = re.match(r"\d\d\:\d\d–\d\d\:\d\d", text)
        if matched is not None:
            text = matched.group(0)
            time = text.strip()
            start, end = time.split("–")
            hour, minute = start.split(":")
            if self.day is not None:
                self.day = self.day.replace(hour=int(hour), minute=int(minute))
            self.time = time
            self.session = None
            return True
        else:
            return False

    def set_session(self, text):
        self.session = text.strip()
