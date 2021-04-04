import json
import re
from pathlib import Path

from autocorrect import Speller
import pandas as pd
from tqdm import tqdm

spell = Speller()

deck_folders = list(Path('../decks').glob('*'))
for deck in tqdm(deck_folders):
  
  prompts_file = deck / 'prompts.csv'
  if(prompts_file.exists()):
    df = pd.read_csv(prompts_file, header=None, index_col=False)
    df[1] = df[0].str.count('_').clip(lower=1)
    df[0] = df[0].apply(spell)
    df.to_csv(prompts_file, header=False, index=False)


  responses_file = deck / 'responses.csv'
  if(responses_file.exists()):
    df = pd.read_csv(responses_file, header=None, index_col=False)
    df[0] = df[0].apply(spell)
    df.to_csv(responses_file, header=False, index=False)
  

