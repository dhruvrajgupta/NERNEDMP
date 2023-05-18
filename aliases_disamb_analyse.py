import json
from collections import Counter
from pathlib import Path

import pandas as pd
from tabulate import tabulate
from tqdm import tqdm

NUM_KLAT_LINES = 5343564  # link_annotated_text.jsonl
NUM_PAGE_LINES = 5362174  # page.csv
MAX_PAGES = max(NUM_KLAT_LINES, NUM_PAGE_LINES)  # change this to a smaller integer for faster runs
MAX_PAGES = 1000
kdwd_path = Path("data")


def text_normalizer(text):
    return text.strip().lower()


class KdwdLinkAnnotatedText:
    def __init__(self, file_path):
        self.file_path = file_path

    def __iter__(self):
        with open(self.file_path) as fp:
            for line in fp:
                yield json.loads(line)


class AnchorTargetStats:

    def __init__(
            self,
            at_count_df,
            text_normalizer,
    ):
        """Anchor-target statistics

        Args:
            at_count_df: (normalized_anchor_text, target_page) counts and metadata
            text_normalizer: text cleaning function for anchor texts
        """
        self._at_count_df = at_count_df
        self.text_normalizer = text_normalizer

    def get_aliases_from_page_id(self, page_id):
        """Return anchor strings used to refer to entity"""
        bool_mask = self._at_count_df['target_page_id'] == page_id
        return (
            self._at_count_df.
            loc[bool_mask].copy().
            sort_values('p_anchor_given_target', ascending=False)
        )

    def get_disambiguation_candidates_from_text(self, text):
        """Return candidate entities for input text"""
        normalized_text = self.text_normalizer(text)
        bool_mask = self._at_count_df['normalized_anchor_text'] == normalized_text
        return (
            self._at_count_df.
            loc[bool_mask].copy().
            sort_values('p_target_given_anchor', ascending=False)
        )


def link_annotated_text_stats():
    file_path = kdwd_path / "link_annotated_text.jsonl"
    klat = KdwdLinkAnnotatedText(file_path)

    anchor_target_counts = Counter()
    for page in tqdm(
            klat,
            total=NUM_KLAT_LINES,
            desc='calculating anchor-target counts'
    ):
        for section in page['sections']:
            spans = [
                (offset, offset + length) for offset, length in
                zip(section['link_offsets'], section['link_lengths'])]
            anchor_texts = [section['text'][ii:ff] for ii, ff in spans]
            keys = [
                (anchor_text, target_page_id) for anchor_text, target_page_id in
                zip(anchor_texts, section['target_page_ids'])]
            anchor_target_counts.update(keys)

    at_count_df = pd.DataFrame([
        (row[0][0], row[0][1], row[1]) for row in anchor_target_counts.most_common()],
        columns=['anchor_text', 'target_page_id', 'anchor_target_count'])

    at_count_df["normalized_anchor_text"] = at_count_df["anchor_text"].apply(text_normalizer)
    at_count_df = at_count_df.loc[at_count_df['normalized_anchor_text'].str.len() > 0, :]

    at_count_df = (
        at_count_df.
        groupby(["normalized_anchor_text", "target_page_id"])["anchor_target_count"].
        sum().
        to_frame("anchor_target_count").
        sort_values('anchor_target_count', ascending=False).
        reset_index()
    )

    page_df = pd.read_csv(kdwd_path / "page.csv")

    at_count_df = pd.merge(
        at_count_df,
        page_df,
        how="inner",
        left_on="target_page_id",
        right_on="page_id")

    at_count_df = at_count_df.rename(columns={
        'title': 'target_page_title',
        'item_id': 'target_item_id',
        'views': 'target_page_views'})

    at_count_df = at_count_df[[
        "normalized_anchor_text",
        "target_page_id",
        "target_item_id",
        "target_page_title",
        "target_page_views",
        "anchor_target_count"]]

    norm = at_count_df.groupby("target_page_id")["anchor_target_count"].transform("sum")
    at_count_df["p_anchor_given_target"] = at_count_df["anchor_target_count"] / norm
    norm = at_count_df.groupby("normalized_anchor_text")["anchor_target_count"].transform("sum")
    at_count_df["p_target_given_anchor"] = at_count_df["anchor_target_count"] / norm

    at_count_df.to_csv(kdwd_path / 'link_annotated_text_stats.csv')


def some_anchor_stats():
    at_count_df = pd.read_csv(kdwd_path / "link_annotated_text_stats.csv")
    anchor_target_stats = AnchorTargetStats(at_count_df, text_normalizer)
    stats_header = ["id", "normalized_anchor_text", "target_page_id", "target_item_id", "target_page_title",
                    "target_page_views", "anchor_target_count", "p_anchor_given_target", "p_target_given_anchor"
                    ]

    page_id = 18717338  # https://en.wikipedia.org/wiki/United_States_dollar
    aliases = anchor_target_stats.get_aliases_from_page_id(page_id)
    print(tabulate(aliases, headers=stats_header, tablefmt="psql"))

    page_id = 651269  # https://en.wikipedia.org/wiki/S&P_Global
    aliases = anchor_target_stats.get_aliases_from_page_id(page_id)
    print(tabulate(aliases, headers=stats_header, tablefmt="psql"))

    page_id = 32544339  # https://en.wikipedia.org/wiki/Hydraulic_fracturing
    aliases = anchor_target_stats.get_aliases_from_page_id(page_id)
    print(tabulate(aliases, headers=stats_header, tablefmt="psql"))

    page_id = 58900  # https://en.wikipedia.org/wiki/Unmanned_aerial_vehicle
    aliases = anchor_target_stats.get_aliases_from_page_id(page_id)
    print(tabulate(aliases, headers=stats_header, tablefmt="psql"))

    page_id = 25226624  # https://en.wikipedia.org/wiki/Patient_Protection_and_Affordable_Care_Act
    aliases = anchor_target_stats.get_aliases_from_page_id(page_id)
    print(tabulate(aliases, headers=stats_header, tablefmt="psql"))

    text = "chicago"
    disambigs = anchor_target_stats.get_disambiguation_candidates_from_text(text)
    print(tabulate(disambigs, headers=stats_header, tablefmt="psql"))

    text = "point"
    disambigs = anchor_target_stats.get_disambiguation_candidates_from_text(text)
    print(tabulate(disambigs, headers=stats_header, tablefmt="psql"))

    text = 'pound'
    disambigs = anchor_target_stats.get_disambiguation_candidates_from_text(text)
    print(tabulate(disambigs, headers=stats_header, tablefmt="psql"))

    text = 'abc'
    disambigs = anchor_target_stats.get_disambiguation_candidates_from_text(text)
    print(tabulate(disambigs, headers=stats_header, tablefmt="psql"))

    text = 'aca'
    disambigs = anchor_target_stats.get_disambiguation_candidates_from_text(text)
    print(tabulate(disambigs, headers=stats_header, tablefmt="psql"))


def main():
    # link_annotated_text_stats()
    some_anchor_stats()


if __name__ == "__main__":
    main()
