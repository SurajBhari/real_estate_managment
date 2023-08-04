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
advisors = [fake.name() for x in range(0, 80)]
customers = []
for x in range(80):
    customers.append({
        "name": fake.name(),
        "phone": fake.phone_number(),
        "address": fake.address(),
    })

data = {}
for project in projects:
    data[project] = {}
    data[project]["sectors"] = {}
    for sector in sectors:
        data[project]['sectors'][sector] = {}
        data[project]['sectors'][sector]['plots'] = {}

        for i in range(0, random.randint(51, 100)):
            date = datetime.date(random.randint(2015, 2023), random.randint(1, 12), random.randint(1, 28))
            # yyyy-MM-dd
            emi_start_date_dt = date
            emi_end_date_dt = fake.date_between(start_date=emi_start_date_dt, end_date="+5y")
            emi_start_date = emi_start_date_dt.strftime("%Y-%m-%d")
            emi_end_date = emi_end_date_dt.strftime("%Y-%m-%d")

            #print(date)
            status = random.choice(["agreement", "registered", "booked", "held", "Not for sale", "available"])
            is_emi = random.choice([True, False])
            size = [random.randint(100, 200), random.randint(100, 200)]
            rate = random.randint(350, 550)
            price = rate*size[0]*size[1]
            deal_price = price
            if is_emi:
                booking_amount = random.randint(0, deal_price)
                emi_amount = deal_price - booking_amount
                emi_months = emi_end_date_dt - emi_start_date_dt
                emi_months = emi_months.days//28
            else:
                booking_amount = deal_price
                emi_amount = 0
                emi_months = 0
            
            reciept_entry = []
            reciept_entry.append({
                "reciept_number" : reciept_numbers,
                "date": date.strftime("%Y-%m-%d"),
                "amount": booking_amount,
                "mode": "cash",
                "is_cheque": False,
            })
            reciept_numbers += 1

            if is_emi:
                for x in range(0, random.randint(1, 4)):
                    mode = random.choice(["cash", "cheque", "BT"])
                    date_ = fake.date_between(start_date=date, end_date=emi_end_date_dt).strftime("%Y-%m-%d")
                    entry = {
                        "reciept_number" : reciept_numbers,
                        "date": date_,
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
                    "amount": emi_amount,
                    "months": emi_months,
                    "start_date": emi_start_date,
                    "end_date": emi_end_date
                }
            else:
                emi_details = {}
            plot = {
                "size": size,
                "rate": rate,
                "price": price,
                "deal_price": deal_price,
                "booking_amount": booking_amount,
                "incentive": random.randint(5,15),
                "customer": random.choice(customers),
                "status": status,
                "is_emi": is_emi,
                "emi": emi_details,
                "reciept_entry": reciept_entry,
                "advisor": random.choice(advisors),
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