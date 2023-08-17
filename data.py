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
    data[project]['address'] = fake.address()
    for sector in sectors:
        data[project]['sectors'][sector] = {}
        data[project]['sectors'][sector]['plots'] = {}

        for i in range(0, random.randint(1, 5)):
            date = datetime.date(random.randint(2015, 2023), random.randint(1, 12), random.randint(1, 28))
            #print(date)
            status = random.choice(["agreement", "registered", "booked", "held", "Not for sale", "available"])
            is_emi = random.choice([True, False])
            size = [random.randint(10, 25), random.randint(25, 50)]
            rate = random.randint(100, 250)
            price = rate*size[0]*size[1]
            boooking_amount = random.randint(0, price) if is_emi else price
            deal_price = price
            reciept_entry = []
            reciept_entry.append({
                "reciept_number" : reciept_numbers,
                "date": date.strftime("%Y-%m-%d"),
                "amount": boooking_amount,
                "mode": "cash",
                "is_cheque": False,
            })
            reciept_numbers += 1

            plot = {
                "size": size,
                "rate": rate,
                "price": price,
                "deal_price": deal_price,
                "booking_amount": boooking_amount,
                "incentive": random.randint(5,15),
                "customer": random.choice(customers),
                "status": status,
                "is_emi": is_emi,
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