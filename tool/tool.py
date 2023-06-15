import streamlit as st
import json
import utilities
import requests
from readability import Document
import pandas as pd

text_mappings = None
fetched_wikifier_texts = {}
new_text = None
wikifier_response = None

st.set_page_config(layout="wide")


def make_db():
    sentences = None
    with open("tool_input.txt", "r") as file:
        sentences = file.readlines()

    with open("tool_db.jsonl", "w") as outfile:
        for doc_id, sentence in enumerate(sentences):
            title = sentence[:25]+" ..."
            text = sentence
            json.dump({
                "doc_id": doc_id,
                "title": title,
                "text": text
            }, outfile)
            outfile.write("\n")


def read_sentences():
    records = []
    with st.spinner('Loading Saved Texts ...'):
        with open("tool_db.jsonl", "r") as file:
            for line in file.readlines():
                line = json.loads(line)
                records.append(line)
    return pd.DataFrame.from_dict(records)


def read_pre_fetched_wikifiers():
    with st.spinner('Loading Saved Wikifiers ...'):
        with open("tool_fetched_wikifier.jsonl", "r") as file:
            for line in file.readlines():
                line = json.loads(line)
                doc_id = line["doc_id"]
                fetched_wikifier_texts[doc_id] = line["wikifier_response"]


def get_wikifier(doc_id):
    # Check JSON available, if not API Call
    if doc_id in fetched_wikifier_texts.keys():
        return fetched_wikifier_texts[doc_id]
    else:
        with st.spinner("Fetching Wikifier Response ..."):
            return utilities.wikifier(text_mappings.iloc[doc_id]["text"])


def get_valid_tabs(wikifier_check):
    valid_tabs = []
    if wikifier_check:
        valid_tabs.append("Wikifier JSON")

    return valid_tabs


def get_cleaned_html(text):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(text, features="lxml")
    for a in soup.findAll('a'):
        a.replaceWithChildren()
    for h in soup.findAll(['h1', 'h2', 'h3']):
        if h.name == 'h1':
            h.name = 'h2'
        elif h.name == 'h2':
            h.name = 'h3'
        elif h.name == 'h3':
            h.name = 'h4'

    return str(soup)


# def make_anchor_tags(text, wikifier_response):
#     orig_text = text
#     generated_text = ""
#     start_pos = 0
#     end_pos = 0
#     for annotation in wikifier_response["annotations"]:
#         for support in annotation["support"]:
#             ann_start_pos = support["chFrom"]
#             ann_end_pos = support["chTo"]+1
#
#             generated_text += orig_text[current_pos:ann_start_pos] + \
#                 f"<a href=''>{orig_text[ann_start_pos:ann_end_pos]}</a>"
#             current_pos = ann_end_pos
#
#     return generated_text


def main():

    with st.sidebar:
        new_text_ckbox = st.checkbox("Add New Text")
        selected_text = st.radio("Saved Texts", tuple(
            list(text_mappings["doc_id"])),
            format_func=lambda x: text_mappings.iloc[x]["title"],
            key="selected_text_radio", disabled=new_text_ckbox)

    if new_text_ckbox:
        text_from = st.radio(
            "Source", ("Add URL", "Text Input"), horizontal=True)

        if text_from == "Add URL":
            st.text_input(
                "Add URL", "",
                placeholder="http://www.example.com/article.com",
                key="add_url")

            if st.button("Fetch Text"):
                if len(st.session_state.add_url) > 0:
                    with st.spinner(f"Fetching text from {st.session_state.add_url}"):
                        response = requests.get(st.session_state.add_url)
                        st.write(f"Status Code: {response.status_code}")
                        if response.status_code == 200:
                            text = Document(response.content)
                            title = text.title()
                            text = text.summary()

                            st.header(title)
                            st.markdown(get_cleaned_html(text),
                                        unsafe_allow_html=True)

        if text_from == "Text Input":
            st.text_area("Enter Text", "", placeholder="An example text ...")
            st.button("Process Text")

    else:
        orig_text = text_mappings.iloc[selected_text]["text"]
        showing_text = text_mappings.iloc[selected_text]["text"]
        main_col, ent_col = st.columns([4, 1], gap="large")

        with main_col:

            st.subheader(text_mappings.iloc[selected_text]["title"])
            st.markdown(showing_text)

            wikifier_check = st.checkbox('Wikifier JSON')

            tabs = []
            tab_texts = []
            if wikifier_check:
                tab_texts = get_valid_tabs(wikifier_check)
                tabs = st.tabs(tab_texts)

            if len(tab_texts) > 0:
                for tab_id in range(len(tab_texts)):
                    if tab_texts[tab_id] == "Wikifier JSON":
                        with tabs[tab_id]:
                            wikifier_response = get_wikifier(selected_text)
                            st.json(wikifier_response,
                                    expanded=False)

        with ent_col:
            st.write("Entity Info")


if __name__ == "__main__":
    # make_db()
    text_mappings = read_sentences()
    read_pre_fetched_wikifiers()
    main()
