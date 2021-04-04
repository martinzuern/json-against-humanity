import json
import re
from pathlib import Path

import pandas as pd
from tqdm import tqdm


white = []
black = []
packs = []

def get_metadata(folder):
  target_file = folder / 'metadata.json'
  with open(target_file, "r") as f:
    return json.load(f)


def append_white(card):
  if card in white:
    return white.index(card)
  white.append(card)
  return len(white) - 1


def append_black(card):
  for i in range(len(black)):
    if black[i]['text'] == card['text']:
        return i
  black.append(card)
  return len(black) - 1


deck_folders = list(Path('../decks').glob('*'))
for deck in tqdm(deck_folders):
  pack = get_metadata(deck)
  
  prompts_file = deck / 'prompts.csv'
  if(prompts_file.exists()):
    prompts = pd.read_csv(prompts_file, header=None, index_col=False)
    pack['black'] = list(map(lambda row: append_black({'text': row[0], 'pick': row[1]}), prompts.values.tolist()))
  else: 
    pack['black'] = []

  responses_file = deck / 'responses.csv'
  if(responses_file.exists()):
    responses = pd.read_csv(responses_file, header=None, index_col=False)
    pack['white'] = list(map(lambda row: append_white(row[0]), responses.values.tolist()))
  else: 
    pack['white'] = []

  packs.append(pack)

with open('../cah-all-compact.json', "w") as f:
  data = {
    'white': white,
    'black': black,
    'packs': packs
  }
  json.dump(data, f)

