from llmlong.ollama_extract import structured_extract_from_longtext
from json import loads, dumps
from tqdm import tqdm
from pydantic import BaseModel


class FedSpeech(BaseModel):
    hawkish_sentiment: int
    relevance: int

    @classmethod
    def validate(cls, values):
        if not (0 <= values.get("hawkish_sentiment", 0) <= 100):
            raise ValueError("hawkish_sentiment must be between 0 and 100")
        if not (0 <= values.get("relevance", 0) <= 100):
            raise ValueError("relevance must be between 0 and 100")
        return values


prompt = """Determine whether the central bank statement reflects a hawkish or dovish stance, considering inflation, economic output, growth, employment, monetary policy tools, cyclical position and global economic conditions. Evaluate how relevant the text is to a central bank's core monetary policy decisions such as interest rate announcements or forward guidance, versus unrelated or economically insignificant events (e.g., charity appearances). Focus on the event's context and market message using a scale from 0 (irrelevant) to 100 (highly relevant)."""


with open("data/fed_speeches_body.jsonl", "r") as file:
    speeches = [loads(line).get("content") for line in file]

with open("data/fed_speeches_meta.jsonl", "r") as file:
    dates = [loads(line).get("d") for line in file]

with open(snakemake.output[0], "a") as file:
    file.truncate(0)
    for speech, date in tqdm(zip(speeches, dates), desc="Ollama sentiment", colour="yellow", total=len(speeches)):
        try:
            sentiment = structured_extract_from_longtext(prompt=prompt, text=speech, structure=FedSpeech)
            speech_dict: dict = {
                "date": date,
                "sentiment": sentiment
            }
            file.write(dumps(speech_dict) + "\n")

        except Exception as e:
            print(f"Error processing speech: {e}")
            file.write(
                dumps({"date": date, "sentiment": None}) + "\n"
            )

