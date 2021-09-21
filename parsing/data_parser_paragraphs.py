import os
import re
import json
import zipfile

from tqdm import tqdm

import docx2txt


PARAGRAPH_SEPARATOR = "אות מעבר"
END_NOTES = ["אות ס י ו ם", "אות סיום"]
YEARS_DIR_PATHS = {
    "2019": r"/Users/sapir/PycharmProjects/hebnlp_project/data/2019",
    "2020": r"/Users/sapir/PycharmProjects/hebnlp_project/data/2020",
    "2021": r"/Users/sapir/PycharmProjects/hebnlp_project/data/2021",
}
HOUR_DIRS_AND_TITLES = {"20-00": "2100", "6-8": "0800"}
ALL_HOUR_STRINGS = [
    "0000",
    "0100",
    "0200",
    "0300",
    "0400",
    "0500",
    "0600",
    "0700",
    "0730",
    "0800",
    "0900",
    "1000",
    "1100",
    "1200",
    "1300",
    "1400",
    "1500",
    "1600",
    "1700",
    "1800",
    "1900",
    "2000",
    "2100",
    "2200",
    "2300",
]


class DocumentParser:
    """
    Parser of 1 news document.
    """

    def parse_document(self, doc_path, paragraph_separator, start_title, end_notes):
        """
        Parses news document
        :param doc_path:
        :return: Clean paragraphs
        """
        text = docx2txt.process(doc_path)
        start_idx = text.find(start_title)
        if start_idx == -1:
            return []
        end_idx = self.__find_end_note(text, start_idx, end_notes)
        text = text[start_idx:end_idx]
        text = self.__clean_text(text)
        paras = text.split(paragraph_separator)
        if len(paras) == 1:
            return []
        return paras

    def __clean_text(self, text):
        text = self.__remove_overhead(text)
        # Remove added numbers in the beginning of paragraphs if exist
        text = re.sub("\nd+", "\n", text)
        return text

    @staticmethod
    def __remove_overhead(text):
        """
        Removes headline and template lines (first and last), and excessive line breaks.
        :param text:
        :return:
        """
        lines = list(filter(None, re.split("\n+", text)))
        return "\n".join(lines[2:-1])


    @staticmethod
    def __find_end_note(text, start_idx, end_notes):
        # find location of end note if exists
        end_indices = []  # possible end locations
        for e in end_notes:
            end_idx = text.find(e, start_idx)
            if end_idx != -1:
                end_indices.append(text.find(e, start_idx))

        # find index of next headline
        m_next_headline = re.search("\d\d\d0\s*\n", text[start_idx + 10 :])
        next_headline_idx = len(text) - 1
        if m_next_headline:
            next_headline_idx = m_next_headline.start() + start_idx + 3

        end_indices.append(next_headline_idx)

        return min(end_indices)


def get_subdirectories_full_path(dir_path):
    contents = [os.path.join(dir_path, i) for i in os.listdir(dir_path)]
    return list(filter(os.path.isdir, contents))


def get_subfiles_full_path(dir_path):
    contents = [os.path.join(dir_path, i) for i in os.listdir(dir_path)]
    return list(filter(os.path.isfile, contents))


def scrape(year_dirs, hour_dirs_and_titles):
    """
    :param year_dirs: dict with directories of years
    :param hour_dirs_and_titles: dict with hour directory names paired with hour title string
    :return: List of news docs. Each contains:
            List of paragraphs (text), hour, date, year
    """

    doc_parser = DocumentParser()
    news_docs = []
    dates_so_far = set()  # handle date duplicates
    for year_str, year_dir in tqdm(year_dirs.items()):
        for hour_dir, hour_str in hour_dirs_and_titles.items():
            month_paths = get_subdirectories_full_path(os.path.join(year_dir, hour_dir))
            for month_path in month_paths:
                document_files = [
                    file
                    for file in get_subfiles_full_path(month_path)
                    if file.endswith("docx")
                ]
                for file in document_files:

                    try:
                        paragraphs = doc_parser.parse_document(
                            file, PARAGRAPH_SEPARATOR, hour_str, END_NOTES
                        )
                    except (zipfile.BadZipfile, UnicodeDecodeError) as e:
                        continue

                    m = re.search("\d{6}", file)
                    if not m:
                        print("Skipped file {} - no date in name".format(file))
                        continue
                    else:
                        date = m.group(0)
                        if date[-2:] != year_str[-2:]:
                            continue
                        date_and_hour = "{} {}".format(date, hour_str)
                        if date_and_hour in dates_so_far:
                            continue
                        dates_so_far.add(date_and_hour)
                    file_paragraphs = [
                        {
                            "paragraph": paragraph,
                            "hour": hour_str[:2],
                            "day": date[:2],
                            "month": date[2:4],
                            "year": year_str,
                            "filename": file,
                        }
                        for paragraph in paragraphs
                    ]
                    news_docs.extend(file_paragraphs)

    return news_docs


def main():
    news_docs = scrape(YEARS_DIR_PATHS, HOUR_DIRS_AND_TITLES)
    with open("../parsed_data/news_paragraphs.json", "w+") as f:
        json.dump(news_docs, f)


if __name__ == "__main__":
    main()
