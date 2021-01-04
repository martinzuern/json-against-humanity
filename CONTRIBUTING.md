# Contributor Guide

I will be vigilant of Pull Requests, that is my prefered method of contribution. I'm willing to help as well! Open an issue with any concerns as well.

Dependencies for the python tools are managed through [pipenv](https://pypi.org/project/pipenv/). After installing it, go to the tools folder and run `pipenv install`.

## Updating Cards from Google Sheet

To update the cards from [this Google Sheet](https://docs.google.com/spreadsheet/ccc?key=0Ajv9fdKngBJ_dHFvZjBzZDBjTE16T3JwNC0tRlp6Wnc&usp=sharing#gid=55), download as Excel file, open and save it to `xls` format within the tools directory.

Then, run `pipenv run update_from_excel `

## Adding Decks manually

Make a directory in `./decks` with these files:
 - `metadata.json` - With the name, abbreviation, [icon](http://fontawesome.io/icons/ "Font Awesome"), description, and whether or not the pack is official
 - `prompts.csv` - Two columns (text and number of cards to pick)
 - `responses.csv` - The texts for the response cards

Run `pipenv run compile_decks` to generate the JSON file .

