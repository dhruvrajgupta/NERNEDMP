import urllib.parse
import urllib.request
import json


def wikifier(text, lang="en", threshold=0.8):
    # Prepare the URL.
    data = urllib.parse.urlencode([
        ("text", text), ("lang", lang),
        ("userKey", "weykbdnnowmxrsbcmofhiolwllztrv"),
        ("pageRankSqThreshold", "%g" % threshold),
        ("applyPageRankSqThreshold", "true"),
        ("nTopDfValuesToIgnore", "200"), ("nWordsToIgnoreFromList", "200"),
        ("wikiDataClasses", "false"), ("wikiDataClassIds", "false"),
        ("support", "true"), ("ranges", "true"), ("minLinkFrequency", "2"),
        ("includeCosines", "false"), ("maxMentionEntropy", "3"),
        ("secondaryAnnotLanguage", "de"),
        ("maxTargetsPerMention", "3")
    ])
    url = "http://www.wikifier.org/annotate-article"
    # Call the Wikifier and read the response.
    req = urllib.request.Request(url, data=data.encode("utf8"), method="POST")
    with urllib.request.urlopen(req, timeout=60) as f:
        response = f.read()
        response = json.loads(response.decode("utf8"))

    return response
