import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('new_test.json', scope)
client = gspread.authorize(creds)

sheet = client.open('new test').sheet1

pp = pprint.PrettyPrinter()
# pp.pprint(sheet.get_all_records())
print sheet.row_count
print sheet.row_values(1)
print sheet.col_values(1)
print sheet.cell(1, 1).value
sheet.delete_row(1)
row = ["this", "is", "working!"]
sheet.insert_row(row, 1)





