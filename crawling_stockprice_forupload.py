# 사용할 라이브러리들을 가져옵니다
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 주가와 증권사 목표주가를 가져오는 함수를 만듭니다
def crawling_investment_opinion_box(stock_id):
    url = f"https://finance.naver.com/item/main.naver?code={stock_id}"
    req = requests.get(url)
    req.raise_for_status()

    soup = BeautifulSoup(req.content, 'html.parser')

    # current_stock_price
    stock_price = soup.select_one('.no_today .blind').text
    stock_price = int(stock_price.replace(',', ''))

    # investment_opinion_target_price
    investment_opinion_box_contents = soup.select('.rwidth em')
    target_price_element = investment_opinion_box_contents[1].text
    target_price_element = int(target_price_element.replace(',', ''))

    return target_price_element, stock_price


# 날짜를 설정합니다
now = datetime.now()
date_to_compare = datetime.strptime('20230802', "%Y%m%d")
date_diff = now - date_to_compare

# 지정된 스프레드시트에 데이터 전송합니다
# Authenticate with Google Sheets API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('{auth 파일이 있는 경로 주소를 여기에 입력해 주세요}', scope)
client = gspread.authorize(creds)

# Open the spreadsheet and select the worksheet by name
spreadsheet = client.open_by_key('{여기에 데이터가 자동 입력되게 하고자 하는 스프레드시트 ID를 입력해 주세요}')
worksheet = spreadsheet.worksheet('{여기에 데이터가 입력되게 하고자 하는 시트(sheet)명을 입력해 주세요}')

stock_id_list = [str(each) for each in worksheet.row_values(1) if len(each)]
print(stock_id_list)
goal_price_list, stock_price_list = [], []

for stock_id in stock_id_list:
    print(stock_id)
    target_price, stock_price = crawling_investment_opinion_box(stock_id)
    goal_price_list.append(target_price)
    stock_price_list.append(stock_price)

print(goal_price_list)

# Update a cell's value
for idx, price in enumerate(goal_price_list):

    # current_stock_price
    row_num = 6
    col_num = idx + 3
    cell = worksheet.cell(row_num, col_num)
    # cell.value = 'New Value'
    worksheet.update_cell(row_num, col_num, stock_price_list[idx])

    # goal_price
    row_num = 8 + date_diff.days
    col_num = idx + 3
    cell = worksheet.cell(row_num, col_num)
    # cell.value = 'New Value'
    worksheet.update_cell(row_num, col_num, price)