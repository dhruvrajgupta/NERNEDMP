import urllib.parse, urllib.request, json

def CallWikifier(text, lang="en", threshold=0.8):
    # Prepare the URL.
    data = urllib.parse.urlencode([
        ("text", text), ("lang", lang),
        ("userKey", "weykbdnnowmxrsbcmofhiolwllztrv"),
        ("pageRankSqThreshold", "%g" % threshold), ("applyPageRankSqThreshold", "true"),
        ("nTopDfValuesToIgnore", "200"), ("nWordsToIgnoreFromList", "200"),
        ("wikiDataClasses", "true"), ("wikiDataClassIds", "false"),
        ("support", "true"), ("ranges", "false"), ("minLinkFrequency", "2"),
        ("includeCosines", "false"), ("maxMentionEntropy", "3"), ("secondaryAnnotLanguage", "de")
        ])
    url = "http://www.wikifier.org/annotate-article"
    # Call the Wikifier and read the response.
    req = urllib.request.Request(url, data=data.encode("utf8"), method="POST")
    with urllib.request.urlopen(req, timeout = 60) as f:
        response = f.read()
        response = json.loads(response.decode("utf8"))
        print(json.dumps(response, indent=2))

        # Pretty Print
        print("="*100)
        print(f"TEXT : {text}")
        for rank, annotation_json in enumerate(response["annotations"]):
            chFrom = annotation_json['support'][0]['chFrom']
            chTo = annotation_json['support'][-1]['chTo']
            print(f"MENTION : {text[chFrom:chTo+1]}")
            print(json.dumps(annotation_json['support'],indent=2))
            print()
            print(f"Rank: {rank+1}")
            print(f"WP Title: {annotation_json['title']}")
            print(f"PageRank: {annotation_json['pageRank']}")
            print(f"{annotation_json['url']}")

            if annotation_json.get('secTitle', None) is not None:
                print(f"SecTitle: {annotation_json['secTitle']}")
                print(f"SecURL: {annotation_json['secUrl']}")

            qid = annotation_json.get('wikiDataItemId', 'NA')
            print(f"QID: {qid}")
            print()
            print()

    # Output the annotations.
    # for annotation in response["annotations"]:
    #     print("%s (%s)" % (annotation["title"], annotation["url"]))

CallWikifier("Syria's foreign minister has said Damascus is ready " +
    "to offer a prisoner exchange with rebels.")

# CallWikifier("His eldest son Akash Ambani, 30, took over as chairman of the board of directors. Ambani, however, will continue to be the chairman of Jio Platforms, the parent company of Reliance Jio Infocomm that owns all Jio digital services brands.")
# CallWikifier("Hermann H. Dieter (* 19. January 1945 in Spaichingen) is a German biochemist and toxicologist who has mainly dealt with the toxicology of drinking water ingredients. Until January 2012, he was head of the department 'Toxicology of drinking and bathing pool water' in the German Federal Environment Agency, before that of the Institute for Water, Soil and Air Hygiene of the Federal Health Office, which was dissolved in 1994.")
# CallWikifier("Michael Douglas Henry 'Mike Kroeger' (* 25. June 1972 in Hanna, Alberta) is a founding member of the Canadian rock band Nickelback, in which he still works as a bassist. Previously, he was already active with some of today's members of Nickelback in the band The Village Idiots.")
# CallWikifier("Sheikh Khalifa bin Hamad Al Thani, the grandfather of the current emir, was born on September 17, 1932. He was the sixth ruler of Qatar and the second ruler of the Al Thani dynasty.")
