from tqdm import tqdm
import requests
import pandas as pd
import io
from NEMO.nemo import read_lattice

INP_FN = "data/processed_data/processed_before_NEMO.json"
OUT_FN = "data/processed_data/processed_after_NEMO.json"

def get_NEMO_lemmatization(texts_list):
    lemmatized_texts = []
    nemo_statuses = []
    for text in tqdm(texts_list):
        text = text.replace("<", "")
        text = text.replace(">", "")
        headers = {'accept': 'application/json',
                   'Content-Type': 'application/json'}
        params = {}
        payload = {'sentences': text,
                   }
        try:
            res = requests.post('http://localhost:8090/morph_hybrid_align_tokens', params=params, json=payload,
                                headers=headers).json()
            lemmatized_text = " ".join(read_lattice(res[0]["md_lattice"])['lemma'])
            nemo_status = True
        except Exception as e:
            print("Error in text {}".format(text))
            print(e)
            lemmatized_text = ""
            nemo_status = False
        lemmatized_texts.append(lemmatized_text)
        nemo_statuses.append(nemo_status)

    return lemmatized_texts, nemo_statuses


def main():
    df = pd.read_json(INP_FN)
    lemmatized_texts, nemo_statuses = get_NEMO_lemmatization(df.paragraph.values.tolist())
    df["lemmatized_text"] = lemmatized_texts
    df["nemo_status"] = nemo_statuses
    df.to_json(OUT_FN)


if __name__ == "__main__":
    main()