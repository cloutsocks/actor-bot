import pprint
import random
import json
import sys

import gspread
import os

from oauth2client.service_account import ServiceAccountCredentials


#sheet = worksheet.get_all_values()

# print(sheet)
# #
# # for col in sheet:
# #     print(col)


def load_8ball_answers(bot_id):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('../config/puppypost-dae4df89a47e.json', scope)
    with open('../config/config_8ball.json') as f:
        config_8ball = json.load(f)

    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(config_8ball['sheet_key'])
    worksheet = spreadsheet.worksheet('8ball')

    try:
        cell = worksheet.find(str(bot_id))
    except gspread.exceptions.CellNotFound:
        print(f"Couldn't load 8ball values for id {bot_id}")
        return []

    answers = worksheet.col_values(cell.col)
    return [a for a in answers[2:] if a]

print(load_8ball_answers(727389526221389845))
