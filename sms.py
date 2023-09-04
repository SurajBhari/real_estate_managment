import json
import datetime
import pytz

# Get the current timezone
current_timezone = pytz.timezone('Asia/Kolkata')  # Replace 'YOUR_TIMEZONE_HERE' with your timezone

# Get the current datetime in the current timezone
today_date = datetime.datetime.now(current_timezone)
print("Current datetime (with timezone):", today_date)



with open("data.json", "r") as f:
    data = json.load(f)

for project in data:
    for sector in data[project]['sectors']:
        for plot in data[project]['sectors'][sector]['plots']:
            is_emi = data[project]['sectors'][sector]['plots'][plot]['is_emi']
            if not is_emi:
                continue
            emi_start = datetime.datetime.strptime(data[project]['sectors'][sector]['plots'][plot]['emi']['start_date'], "%Y-%m-%d")
            emi_end = datetime.datetime.strptime(data[project]['sectors'][sector]['plots'][plot]['emi']['end_date'], "%Y-%m-%d")
            # if the current month falls between the start and end date
            current_year = today_date.year
            current_month = today_date.month
            if emi_start.year <= current_year <= emi_end.year and emi_start.month <= current_month <= emi_end.month:
                # how many days 
                days_left = emi_end.date().day - today_date.date().day
                if days_left < 0:
                    continue
                if days_left > 6:
                    continue
                print(project, sector, plot)
                print(days_left)
                print("Send SMS to", data[project]['sectors'][sector]['plots'][plot]['customer']['phone'])
