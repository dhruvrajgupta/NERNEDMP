import blink.main_dense as main_dense
import argparse
import blink.ner as NER
import time
from datetime import timedelta
import wikipediaapi
from urllib.request import urlopen
import json

models_path = "models/" # the path where you stored the BLINK models
id_from_page_url = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageprops&titles={title}"
wiki_wiki = wikipediaapi.Wikipedia('en')

def wikidata_id_of_wikipage(wikidata_title_normalized):
    """
    If the ids on the page and wikidata match many references will available for the entity
    != Akash Ambani, Mukesh Ambani

    :returns wikidata_id of the WikiPage
    """

    idurl = id_from_page_url.format(title=wikidata_title_normalized)
    response = urlopen(idurl)
    data_json = json.loads(response.read())

    pages_dict = data_json["query"]["pages"]
    pageid = list(pages_dict.keys())[-1]
    page_wikidata_id = pages_dict[pageid]["pageprops"]["wikibase_item"]

    return page_wikidata_id

config = {
    "test_entities": None,
    "test_mentions": None,
    "interactive": False,
    "top_k": 3,
    "biencoder_model": models_path+"biencoder_wiki_large.bin",
    "biencoder_config": models_path+"biencoder_wiki_large.json",
    "entity_catalogue": models_path+"entity.jsonl",
    "entity_encoding": models_path+"all_entities_large.t7",
    "crossencoder_model": models_path+"crossencoder_wiki_large.bin",
    "crossencoder_config": models_path+"crossencoder_wiki_large.json",
    "fast": True, # set this to be true if speed is a concern
    "output_path": "logs/", # logging directory
    # "show_url" : True,
    # "interactive": True,
    # "faiss_index": "flat",
    # "index_path": models_path+"faiss_flat_index.pkl"
}

args = argparse.Namespace(**config)

print("Loading model...")
models = main_dense.load_models(args, logger=None)
print("Model Loaded...")

print("Loading NER...")
ner_model = NER.get_model()
print("NER Loaded...")

print("Starting Analysis ...")
start_time = time.monotonic()

x = []
x.append("Bert and Ernie are two Muppets who appear together in numerous skits on the popular children's television show of the United States, Sesame Street.")
# x.append("Christopher Columbus was the first man who wanted to find a direct rout to Asia. He stumbled on a new World called America.")

for text in x:
    print("=" * 100)
    print(f"TEXT: {text}")
    data_to_link = main_dense._annotate(ner_model, [text])
    _, _, _, _, _, predictions, scores, = main_dense.run(args, None, *models, test_data=data_to_link)
    spans_annotations_values = {}
    for data, pred, score in zip(data_to_link, predictions, scores):
        mention = data["mention"]
        print(f"MENTION: \t {mention} \n")
        for rank, (p, s) in enumerate(zip(pred,score)):
            print(f"Rank: {rank+1}")
            print(f"WP Title: {p}")
            print(f"Score: {round(s, 2)}")
            page_py = wiki_wiki.page(p)
            full_url = page_py.fullurl
            can_url_last = full_url.split("/")[-1]
            qid = wikidata_id_of_wikipage(can_url_last)
            print(full_url)
            print(f"QID: {qid}")
            print()
    print("\n")
    print()

end_time = time.monotonic()
print(timedelta(seconds=end_time - start_time))