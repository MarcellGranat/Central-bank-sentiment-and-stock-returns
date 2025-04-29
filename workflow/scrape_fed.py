import json
from pprint import pprint as print

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

json_path = "https://www.federalreserve.gov/json/ne-speeches.json"

speeches_meta: str = requests.get(json_path).content.decode("utf-8-sig")

metas: list = json.loads(speeches_meta)

for meta in tqdm(metas, desc="Downloading speeches", colour="green"):
    try:
        response = requests.get("https://www.federalreserve.gov" + meta.get("l"))
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = [p.get_text() for p in soup.find_all("p")]
            content = "\n\n".join(paragraphs)
            # * append to meta only if the content is available
            with open("data/fed_speeches_meta.jsonl", "a") as file:
                file.write(json.dumps(meta) + "\n")
            with open("data/fed_speeches_body.jsonl", "a") as file:
                file.write(json.dumps({"content": content}) + "\n")
        else:
            print(f"Failed to download {meta.get('l')}: {response.status_code}")
    except Exception as e:
        print(f"Error processing {meta.get('l')}: {e}")
