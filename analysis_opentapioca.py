from urllib.request import urlopen
import json

import time
from datetime import timedelta

import spacy
nlp = spacy.blank('en')
nlp.add_pipe('opentapioca')

start_time = time.monotonic()

def wp_from_wd_id(qid, lang="en"):
    link = f"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=sitelinks/urls&ids={qid}&sitefilter={lang}wiki"

    response = urlopen(link)
    data_json = json.loads(response.read())

    sitelinks = data_json['entities'][qid]['sitelinks']
    url = sitelinks.get(lang+'wiki', None)

    if url is None:
        return "No WP URL"
    else:
        return url['url']
    # print(json.dumps(data_json, indent=2))

def call_open_tapioca(text):

    doc = nlp(text)
    # for span in doc.ents:
    #     print((span.text, span.kb_id_, span.label_, span._.description, span._.score))
    # ('Christian Drosten', 'Q1079331', 'PERSON', 'German virologist and university teacher', 3.6533377082098895)
    # ('Germany', 'Q183', 'LOC', 'sovereign state in Central Europe', 2.1099332471902863)
    # Check also span._.types, span._.aliases, span._.rank

    raw_annotations = doc._.annotations

    print("="*100)
    print(f"TEXT: {text}")

    for substr_obj in raw_annotations:
        start = substr_obj['start']
        end = substr_obj['end']

        if substr_obj['tags'][0]['rank'] > 0:
            print(f"MENTION: {text[start:end]}")
            print()

            for rank, candidate in enumerate(substr_obj['tags']):
                if candidate['rank'] < 0:
                    break
                if rank == 3:
                    break
                print(f"Rank: {rank+1}")
                print(f"Label: {candidate['label']}")
                print(f"WD-rank: {candidate['rank']}")
                print(wp_from_wd_id(candidate['id']))
                print(f"QID: {candidate['id']}")

                print()
    print("\n\n")

# call_open_tapioca('Christian Drosten works in Germany.')
call_open_tapioca("His eldest son Akash Ambani, 30, took over as chairman of the board of directors. Ambani, however, will continue to be the chairman of Jio Platforms, the parent company of Reliance Jio Infocomm that owns all Jio digital services brands.")
call_open_tapioca("Hermann H. Dieter (* 19. January 1945 in Spaichingen) is a German biochemist and toxicologist who has mainly dealt with the toxicology of drinking water ingredients. Until January 2012, he was head of the department 'Toxicology of drinking and bathing pool water' in the German Federal Environment Agency, before that of the Institute for Water, Soil and Air Hygiene of the Federal Health Office, which was dissolved in 1994.")
call_open_tapioca("Michael Douglas Henry 'Mike Kroeger' (* 25. June 1972 in Hanna, Alberta) is a founding member of the Canadian rock band Nickelback, in which he still works as a bassist. Previously, he was already active with some of today's members of Nickelback in the band The Village Idiots.")
call_open_tapioca("Sheikh Khalifa bin Hamad Al Thani, the grandfather of the current emir, was born on September 17, 1932. He was the sixth ruler of Qatar and the second ruler of the Al Thani dynasty.")

end_time = time.monotonic()
print(timedelta(seconds=end_time - start_time))