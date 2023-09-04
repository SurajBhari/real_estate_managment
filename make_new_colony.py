import json

# if data.json doesn't exist make one 
try:
    open("data.json", "r").close()
except FileNotFoundError:
    input("data.json not found. Press enter to create one.")
    with open("data.json", "w") as f:
        json.dump({}, f)

with open("data.json", "r") as f:
    data = json.load(f)


project_name = input("Enter project name: ")
if project_name in data:
    print("Project already exists")
    exit()

alphabets = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
data[project_name] = {}
data[project_name]["sectors"] = {}
sectors = []
sector_index = 0
while True:
    sector_alphabet = alphabets[sector_index]
    number = input(f"Enter number of sectors in {sector_alphabet}: or enter -1 to exit: ")
    if number == "0":
        sector_index += 1
        continue
    if number == "-1":
        break
    try:
        number = int(number)
    except ValueError:
        print("Invalid input")
        continue
    if number < 0:
        print("Invalid input")
        continue
    sector_alphabet = alphabets[sector_index]
    data[project_name]["sectors"][sector_alphabet] = {}
    data[project_name]['sectors'][sector_alphabet]['plots'] = {}
    for i in range(1, number+1):
        data[project_name]['sectors'][sector_alphabet]['plots'][i] = {
            "size": "",
            "rate": "",
            "price": "",
            "deal_price": "",
            "booking_amount": "",
            "customer": {},
            "status": "Not for sale",
            "is_emi": "",
            "reciept_entry": "",
            "advisor": "",
            "date": "",
            "files": []
            }
    sector_index += 1

with open("data.json", "w") as f:
    json.dump(data, f, indent=4)
