import os
import argparse
import pandas as pd
from extractor.schedule_reader import ScheduleReader


def main(path, output):
    default_path = os.path.join(os.path.dirname(__file__), "tests/data/2020.acl-main.0.pdf")
    default_output = os.path.join(os.path.dirname(__file__), "acl2020.csv")
    _path = path if path else default_path
    _output = output if output else default_output
    reader = ScheduleReader(_path)
    papers = reader.iterate_papers()
    papers_json = [p.to_json() for p in papers]
    data = pd.DataFrame(papers_json)
    data.to_csv(_output, index=False, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="path to acl anthology", default="")
    parser.add_argument("--output", help="path to output csv", default="")
    args = parser.parse_args()
    main(args.path, args.output)
