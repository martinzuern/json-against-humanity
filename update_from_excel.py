import json
import re
from pathlib import Path

import casestyle
import pandas as pd
import xlrd
from tqdm import tqdm

FILE_NAME = './Cards Against Humanity.xls'
METADATA_DEFAULT = {
  'abbr': '',
  'name': '',
  'icon': '',
  'official': False,
  'description': '- placeholder -'
}

def col_to_md(file_name, sheet_name, col_idx, max_len=float("inf")):
  result = []
  book = xlrd.open_workbook(file_name, formatting_info=True)
  first_sheet = book.sheet_by_name(sheet_name)
  
  for row_idx in range(min(max_len, first_sheet.nrows)):
    text_cell = first_sheet.cell_value(row_idx, col_idx)
    text_cell_xf = book.xf_list[first_sheet.cell_xf_index(row_idx, col_idx)]

    # skip rows where cell is empty
    if not text_cell:
      result.append('')
      continue

    text = text_cell

    text_cell_runlist = first_sheet.rich_text_runlist_map.get((row_idx, col_idx))
    if text_cell_runlist:
      segments = []
      for segment_idx in range(len(text_cell_runlist)):
        start = text_cell_runlist[segment_idx][0]
        # the last segment starts at given 'start' and ends at the end of the string
        end = None
        if segment_idx != len(text_cell_runlist) - 1:
          end = text_cell_runlist[segment_idx + 1][0]
        segment_text = text_cell[start:end]
        segments.append({
          'text': segment_text,
          'font': book.font_list[text_cell_runlist[segment_idx][1]]
        })
      # segments did not start at beginning, assume cell starts with text styled as the cell
      if text_cell_runlist[0][0] != 0:
        segments.insert(0, {
          'text': text_cell[:text_cell_runlist[0][0]],
          'font': book.font_list[text_cell_xf.font_index]
        })
      
      text = ''
      for segment in segments:
        pad = ''
        if segment['font'].italic:
          pad += '*'
        if segment['font'].bold:
          pad += '**'
        text += pad + segment['text'] + pad

    if type(text) == float:
      text = int(text)
    text = str(text).replace('\n', '<br>').replace('\xa0', ' ')
    text = re.sub(r"_{3,}", '_', text, 0)
    result.append(text.strip())
  return result


def update_metadata(folder, new_data):
  target_file = folder / 'metadata.json'
  data = {}
  if target_file.exists():
    with open(target_file, "r") as f:
      data = json.load(f)
  
  data = {**METADATA_DEFAULT, **new_data, **data}
  assert data['abbr']
  assert data['name']

  with open(target_file, "w") as f:
    json.dump(data, f, indent=2, sort_keys=True)


def build_name(name_str):
  name = name_str.replace('CAH:', '').replace('CAH :', '').strip()
  
  abbr = re.sub(r"""pack|\(.*?\)|[^A-Z0-9]""", ' ', name, 0, re.IGNORECASE | re.VERBOSE | re.DOTALL)
  abbr = casestyle.kebabcase(abbr.strip())
  return abbr, name

####
print('Reading MAIN DECK...')
df = pd.read_excel(FILE_NAME, sheet_name='CAH Main Deck', header=None)
df[1] = col_to_md(FILE_NAME, 'CAH Main Deck', 1, max_len=len(df.index))
df = df.iloc[2:].copy()
df[2] = df[2].fillna(1).replace({'DRAW 2, PICK 3': 3, 'PICK 2': 2})

## Identify pack versions
version_idx = df.iloc[0].drop_duplicates(keep='last')[3:].dropna()

for col_idx, name in tqdm(version_idx.items()):
  abbr = 'Base-{}'.format(name)
  dest = Path('./decks') / abbr
  dest.mkdir(parents=True, exist_ok=True)

  update_metadata(dest, {
    'abbr': abbr,
    'name': 'Base Set' if name == 'US' else 'Base Set ({} Version)'.format(name),
    'icon': '',
    'official': True
  })

  df_tmp = df[~df[col_idx].isna()].iloc[:, 0:3]
  df_tmp_prompt = df_tmp[df_tmp[0] == 'Prompt'].iloc[:, 1:3]
  df_tmp_prompt.to_csv(dest / 'prompts.csv', header=False, index=False)
  df_tmp_resp = df_tmp[df_tmp[0] == 'Response'].iloc[:, 1:2]
  df_tmp_resp.to_csv(dest / 'responses.csv', header=False, index=False)
print('MAIN DECK completed.')


###
print('Reading MASTER CARDS LIST ...')
df_prompts = pd.read_excel(FILE_NAME, sheet_name='Master Cards List', header=None, usecols='A:D')
df_prompts[0] = col_to_md(FILE_NAME, 'Master Cards List', 0, max_len=len(df_prompts.index))
df_prompts = df_prompts.iloc[1:].copy()
df_prompts[1] = df_prompts[1].fillna(1).replace({'DRAW 2, PICK 3': 3, 'PICK 2': 2})
df_prompts.columns = ['Card', 'Pick', 'Set', 'Sheet']

df_prompts.dropna(subset=['Sheet'], inplace=True)
df_prompts = df_prompts[df_prompts['Sheet'] != 'CAH Main Deck']

for set_name, df in tqdm(df_prompts.groupby('Set')):
  abbr, name = build_name(set_name)
  dest = Path('./decks') / abbr
  dest.mkdir(parents=True, exist_ok=True)

  update_metadata(dest, {
    'abbr': abbr,
    'name': name,
    'official': ('CAH' in df['Sheet'].values[0])
  })

  df[['Card', 'Pick']].to_csv(dest / 'prompts.csv', header=False, index=False)

##

df_responses = pd.read_excel(FILE_NAME, sheet_name='Master Cards List', header=None, usecols='G:I')
df_responses[6] = col_to_md(FILE_NAME, 'Master Cards List', 6, max_len=len(df_responses.index))
df_responses = df_responses.iloc[1:].copy()
df_responses.columns = ['Card', 'Set', 'Sheet']

df_responses.dropna(subset=['Sheet'], inplace=True)
df_responses = df_responses[df_responses['Sheet'] != 'CAH Main Deck']

for set_name, df in tqdm(df_responses.groupby('Set')):
  abbr, name = build_name(set_name)
  dest = Path('./decks') / abbr
  dest.mkdir(parents=True, exist_ok=True)

  update_metadata(dest, {
    'abbr': abbr,
    'name': name,
    'official': ('CAH' in df['Sheet'].values[0])
  })

  df[['Card']].to_csv(dest / 'responses.csv', header=False, index=False)

print('Completed MASTER CARDS LIST')
