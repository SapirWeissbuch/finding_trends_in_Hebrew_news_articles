import pandas as pd
import re
import string
import itertools
import json

FILE_PATH = "../data/parsed_data/news_paragraphs.json"
OUT_FILE_PATH = "../data/processed_data/processed_before_NEMO.json"

# regexes
WEATHER_REGEXES = [
    "(תחזית\s)*מזג\s*(-|\s+)\s*האוויר\s*(:|-|,|;)(.|\n)*",
    "תחזית מזג\s*(-|\s+)\s*האוויר(.|\n)*",
    "(תחזית\s)*מזג\s*(-|\s+)\s*האוויר ל(.|\n)*",
    "(תחזית\s)*מזג\s*(-|\s+)\s*האוויר מחר(.|\n)*",
    "ו*התחזית",
    "(תחזית\s)*מזג\s*(-|\s+)\s*האוויר הלילה(.|\n)*",
    "(תחזית\s)*מזג\s*(-|\s+)\s*האוויר הערב(.|\n)*",
]

TRAFFIC_REGEXES = ["עדכוני תנועה(.|\n)*"]

TEMPLATE_REGEXES = [
    'גלי\s*(\s+|-)\s*(צהל|צה"ל),*\s+השעה\s+.*\n',
    "אלה החדשות (שעורכים|שעורך|שערך|שעורכת|שערכו).*",
    "אלה החדשות.*",
]

# OUR_REPORTER_REGEXES = ['כתב(י|ת)*נו.* (מוסרת*|מספרת*)*']

OTHER_REGEXES = ["ב*בוקר טוב ישראל"]

CUSTOM_STOPWORDS = [
    "בעקבות",
    "נמסר",
    "כתבתנו",
    "כתבנו",
    "הבוקר",
    "הלילה",
    "אמש",
    "לענייני",
    "מוסר",
    "מוסרת",
    "מוסרת",
    "כי",
    "כתב",
    "כתבת",
]

MIN_LENGTH = 5

HEB_STOPWORDS_PATH = "../added_material/heb_stopwords.txt"

def clean_notes_and_inserts(s):
    notes = ["(--", "--)", "----" "<<<", ">>>", "<<<"]
    lines = re.split("\n+", s)
    good_lines = []
    for line in lines:
        if not any(note in line for note in notes):
            good_lines.append(line)
    return "\n".join(good_lines)


def clean_punctuation(s):
    s = re.sub("[\.:]+", "\n", s)
    s = re.sub("[-᠆‑₋—−–]+", " ", s)
    s = s.translate(str.maketrans("", "", string.punctuation))
    return s


def remove_too_short_paragraphs(df):
    too_short_bool = df["paragraph"].str.split().apply(len) > MIN_LENGTH
    return df[too_short_bool]


def remove_regexes(s, regexes_list):
    for r in regexes_list:
        s = re.sub(r, " ", s)
    return s


def remove_stopwords(s, stopwords):
    word_list = s.split()
    output = [w for w in word_list if not w in stopwords]
    return " ".join(output)


def main():
    df = pd.read_json(FILE_PATH)
    dti = pd.to_datetime(df[["year", "month", "day", "hour"]], errors="coerce")
    df["time"] = dti

    # Remove noise regexes
    all_regexes = list(
        itertools.chain.from_iterable(
            [WEATHER_REGEXES, TRAFFIC_REGEXES, TEMPLATE_REGEXES, OTHER_REGEXES]
        )
    )
    df.loc[:, "paragraph"] = df.paragraph.apply(
        lambda x: remove_regexes(x, all_regexes)
    )

    df.loc[:, "paragraph"] = df.paragraph.apply(lambda x: clean_notes_and_inserts(x))

    df = df[~df.paragraph.str.isspace()]


    df.to_json(OUT_FILE_PATH)


if __name__ == "__main__":
    main()
