from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.utils import column_index_from_string
from openpyxl.styles import PatternFill
from openpyxl.styles import Font
from openpyxl.styles import Alignment
from openpyxl.styles import Border
from openpyxl.styles import Side
from openpyxl.styles import NamedStyle
import random
import json

file_name = "test.xlsx"
if not file_name:
    print("No file specified.")
    exit()
    
wb = load_workbook(file_name)
ws = wb.active

headings = []
for col in range(1, ws.max_column + 1):
    headings.append(ws.cell(row=1, column=col).value)

#print(headings)
known_r_no = []


with open("data.json", "r+") as f:
    data = json.load(f)

colony_name = input("Enter colony name: ")
if colony_name not in data:
    data[colony_name] = {}
    data[colony_name]["sectors"] ={}

for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):    
    s_no = row[0].value
    if not s_no:
        continue
    if row[1].font.color.rgb == "FFFF0000":
        continue
    p_no = row[1].value
    party = row[2].value
    if not party:
        continue
    address = row[3].value
    mobile_no = row[4].value
    p_size = [float(x) for x in row[5].value.split("*")]
    area = row[6].value
    if not area:
        area = p_size[0]*p_size[1]
    advisor = row[10].value
    if not advisor:
        continue
    booking_date = row[11].value

    reciepts = []
    total = 0
    col = 9
    print(s_no)
    while True:
        col += 3
        if headings[col] == "R.TOTAL":
            break
        cr_no = row[col].value
        if isinstance(cr_no, str):
            if "/" in cr_no:
                cr_no = cr_no.split("/")[0]
        if not cr_no:
            cr_no = random.randint(1000, 9999)
            while cr_no in known_r_no:
                cr_no = random.randint(1000, 9999)
        known_r_no.append(cr_no)
        date = row[col + 1].value
        amount = row[col + 2].value
        if not amount:
            continue
        if not date:
            date = headings[col+2]
        #print(cr_no, date, amount)
        total = total+amount
        if not booking_date:
            booking_date = date
        r = {
            "reciept_number": 0,
            "date": "",
            "amount": 0,
            "mode": "cash",
            "is_cheque": False
            }
        r["reciept_number"] = cr_no
        r["date"] = date.strftime("%Y-%m-%d")
        r["amount"] = amount
        reciepts.append(r)
    print(total)
    if len(reciepts) == 1:
        emi=False
    else:
        emi=True
    r_total = row[col].value
    if not total == r_total:
        print("Total mismatch")
        print(total, r_total)
        break
    t_amount = row[col+1].value
    if not t_amount:
        print("Total amount missing")
        break
    template = {
        "size": "",
        "rate": "",
        "price": "",
        "deal_price": "",
        "booking_amount": "",
        "incentive": "",
        "customer": {},
        "status": "available",
        "is_emi": "",
        "reciept_entry": "",
        "advisor": "",
        "date": "",
        "files": []
        }
    rate = t_amount/area 
    # limit rate to 2 decimal places
    rate = int(rate*100)/100
    template["size"] = p_size
    template["rate"] = rate
    template["price"] = t_amount
    template["deal_price"] = t_amount
    template["booking_amount"] = reciepts[0]["amount"]
    template["incentive"] = 10
    template["customer"]["name"] = party
    template["customer"]["address"] = address
    template["customer"]["mobile_no"] = mobile_no
    template["status"] = "booked"
    template["is_emi"] = emi
    template["reciept_entry"] = reciepts
    template["advisor"] = advisor
    template["date"] = booking_date.strftime("%Y-%m-%d")
    template["files"] = []
    #print(json.dumps(template, indent=4))
    sector = p_no.split("-")
    pno = sector[1]
    sector = sector[0]
    if sector not in data[colony_name]["sectors"]:
        data[colony_name]["sectors"][sector] = {}
        data[colony_name]["sectors"][sector]["plots"] = {}
    data[colony_name]["sectors"][sector]["plots"][pno] = template

with open("data.json", "w+") as f:
    f.write(json.dumps(data, indent=4))
print(known_r_no)
    