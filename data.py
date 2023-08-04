import json
import random
import datetime
from faker import Faker
fake = Faker() 

projects = ["Monarch Residency", "Aashiyana", "Eden Garden"]
sectors = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
sectors = list(sectors)[:5]

data_count = 0
reciept_numbers = 1
data = {}
for project in projects:
    data[project] = {}
    data[project]["sectors"] = {}
    for sector in sectors:
        data[project]['sectors'][sector] = {}
        data[project]['sectors'][sector]['plots'] = {}

        for i in range(0, random.randint(51, 100)):
            date = datetime.datetime(random.randint(2015, 2023), random.randint(1, 12), random.randint(1, 28))
            # yyyy-MM-dd
            date = date.strftime("%Y-%m-%d")
            emi_start_date = datetime.datetime(random.randint(2019, 2020), random.randint(1, 12), random.randint(1, 28))
            emi_start_date = emi_start_date.strftime("%Y-%m-%d")

            emi_end_date = datetime.datetime(random.randint(2019, 2020), random.randint(1, 12), random.randint(1, 28))
            emi_end_date = emi_end_date.strftime("%Y-%m-%d")

            #print(date)
            status = random.choice(["agreement", "registered", "booked", "held", "Not for sale", "available"])
            is_emi = random.choice([True, False])
            
            if is_emi:
                reciept_entry = []
                for x in range(0, random.randint(1, 4)):
                    mode = random.choice(["cash", "cheque", "BT"])
                    date = datetime.datetime(random.randint(2019, 2020), random.randint(1, 12), random.randint(1, 28))
                    date = date.strftime("%Y-%m-%d")
                    entry = {
                        "reciept_number" : reciept_numbers,
                        "date": date,
                        "amount": random.randint(1000, 2000),
                        "mode": mode,
                        "is_cheque": True if mode == "cheque" else False,
                    }
                    reciept_numbers += 1
                    if mode == "cheque":
                        entry['cheque'] = {
                            "bank": "HDFC",
                            "cheque_no": "123456",
                        }
                    reciept_entry.append(entry)
                emi_details = {
                    "amount": random.randint(1000, 2000),
                    "months": random.randint(1, 12),
                    "start_date": emi_start_date,
                    "end_date": emi_end_date
                }
            else:
                emi_details = {}
                reciept_entry = []
            plot = {
                "size": [random.randint(100, 200), random.randint(100, 200)],
                "rate": random.randint(1000, 2000),
                "price": random.randint(100000, 200000),
                "deal_price": random.randint(100000, 200000),
                "booking_amount": random.randint(100000, 200000),
                "incentive": random.randint(5,15),
                "customer":{
                    "name": fake.name(),
                    "phone": fake.phone_number(),
                    "address": fake.address(),
                },
                "status": status,
                "is_emi": is_emi,
                "emi": emi_details,
                "reciept_entry": reciept_entry,
                "advisor": fake.name(),
                "date": f"{date}",
                "files": []
            }
            if status in ["Not for sale", "available"]:
                for x in plot:
                    plot[x] = ""
                plot["files"] = []
                plot["customer"] = {}
                plot["status"] = status
            data[project]['sectors'][sector]['plots'][i] = plot
            data_count += 1

with open("data.json", "w") as f:
    json.dump(data, f, indent=4)

print(f"generated {data_count} plots")