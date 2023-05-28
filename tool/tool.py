import streamlit as st
import json
import utilities

text_mappings = {}
fetched_wikifier_texts = {}
new_text = None

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
    with st.spinner('Loading Saved Texts ...'):
        with open("tool_db.jsonl", "r") as file:
            for line in file.readlines():
                line = json.loads(line)
                text_mappings[line["doc_id"]] = {
                    "title": line["title"],
                    "text": line["text"]
                }


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
            return utilities.wikifier(text_mappings[doc_id])


def get_valid_tabs(wikifier_check):
    valid_tabs = []
    if wikifier_check:
        valid_tabs.append("Wikifier JSON")

    return valid_tabs


def main():

    with st.sidebar:
        new_text_ckbox = st.checkbox("Add New Text")
        selected_text = st.radio("Saved Texts", tuple(
            list(text_mappings.keys())),
            format_func=lambda x: text_mappings[x]["title"],
            key="selected_text_radio")
        # Disable Saved Texts Radio
        # From URL

        # From Text Box
        pass

    if new_text_ckbox:
        text_from = st.radio(
            "Source", ("Add URL", "Text Input"), horizontal=True)

        if text_from == "Add URL":
            st.text_input(
                "Add URL", "", placeholder="http://www.example.com/article.com")
            st.button("Fetch Text")

        if text_from == "Text Input":
            st.text_area("Enter Text", "", placeholder="An example text ...")
            st.button("Process Text")

    else:

        main_col, ent_col = st.columns([5, 1], gap="large")

        with main_col:

            st.subheader(text_mappings[selected_text]["title"])
            st.markdown(text_mappings[selected_text]["text"])

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
                            st.json(get_wikifier(selected_text),
                                    expanded=False)

        with ent_col:
            st.write("Entity Info")


if __name__ == "__main__":
    # make_db()
    read_sentences()
    read_pre_fetched_wikifiers()
    main()
