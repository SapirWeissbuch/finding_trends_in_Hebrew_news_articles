from tqdm import tqdm
import requests
import pandas as pd
import io
from NEMO.nemo import read_lattice

AFTER_NEMO_FN =  "data/processed_data/processed_after_NEMO.json"
OUT_FN = "data/processed_data/fixed_processed_after_NEMO.json"


def get_NEMO_lemmatization(texts_list, current_nemo_statuses, existing_lemmatized_texts):
    lemmatized_texts = []
    new_nemo_statuses = []
    for text, current_nemo_status, lemmatized_text in tqdm(zip(texts_list, current_nemo_statuses, existing_lemmatized_texts), total=len(texts_list)):
        if not current_nemo_status:
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
                new_lemmatized_text = " ".join(read_lattice(res[0]["md_lattice"])['lemma'])
                new_nemo_status = True
                print("fixed text")
            except Exception as e:
                print("Error in text {}".format(text))
                print(e)
                new_lemmatized_text = ""
                new_nemo_status = False
        else:
            new_nemo_status = current_nemo_status
            new_lemmatized_text = lemmatized_text
        lemmatized_texts.append(new_lemmatized_text)
        new_nemo_statuses.append(new_nemo_status)

    return lemmatized_texts, new_nemo_statuses


def main():
    df_after_nemo = pd.read_json(AFTER_NEMO_FN)
    lemmatized_texts, nemo_statuses = get_NEMO_lemmatization(df_after_nemo.paragraph.values.tolist(), df_after_nemo.nemo_status.values.tolist(),
                                                             df_after_nemo.lemmatized_text.values.tolist())

    df_after_nemo["lemmatized_text"] = lemmatized_texts
    df_after_nemo["nemo_status"] = nemo_statuses
    df_after_nemo.to_json(OUT_FN)


if __name__ == "__main__":
    main()