import json


def get_section_links(text, section_link_offsets, section_link_lengths, target_page_ids):
    for offset, length, target_page_id in zip(
            section_link_offsets,
            section_link_lengths,
            target_page_ids
    ):
        anchor_text = text[offset: offset + length]
        print('{} -> {}'.format(anchor_text, target_page_id))


def read_jsonl_file():
    i = 0
    with open("data/link_annotated_text.jsonl", "r") as f:
        for line in f:
            if i == 5:
                break
            i += 1
            line = json.loads(line)
            print('page_id: ', line['page_id'])
            section = line['sections'][0]
            print('section name: ', section['name'])
            print('section text: ', section['text'])
            print('section link_offsets: ', section['link_offsets'])
            print('section link_lengths: ', section['link_lengths'])
            print('section target_page_ids: ', section['target_page_ids'])
            get_section_links(section['text'], section['link_offsets'], section['link_lengths'],
                              section['target_page_ids'])
            print()
        print()


def main():
    read_jsonl_file()


if __name__ == '__main__':
    main()
