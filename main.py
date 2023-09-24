from flask import Flask, render_template, request, redirect, url_for, session,flash, jsonify, send_file
import re
import openpyxl
import os
import webbrowser

from validate import validate_otp as validate
import sqlite3
import time
from copy import deepcopy
from datetime import datetime
import json

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '1a2b3c4d5e6d7g8h9i10'


available_status = ["available", "Not for sale", "held", "booked", "registered", "agreement"]

# create a table accounts if not exists. if the table didn't existed before, add a entry to the table
"""
CREATE TABLE accounts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(255) NOT NULL,   
  email VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL
); 
"""
global LOCK
LOCK = False
template = {
    "size": [
        0,
        0
    ],
    "rate": 0,
    "price": 0,
    "deal_price": 0,
    "booking_amount": 0,
    "customer": {
        "name": "",
        "phone": "",
        "address": ""
    },
    "status": "available",
    "is_emi": False,
    "emi": {},
    "reciept_entry": [],
    "advisor": "",
    "date": ""
}


# http://localhost:5000/login/ - this will be the login page, we need to use both GET and POST requests

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'password' in request.form:
        password = request.form['password']
        if validate(password):
            session['loggedin'] = True
            session['username'] = 'admin'
            session['lastused'] = time.time()
            return redirect(url_for('home'))
        else:
            flash("Incorrect password!", "danger")

    return render_template('auth/login.html', title="Login")

def _get_available_status():
    return available_status

@app.route("/get_available_status")
def get_available_status():
    return jsonify(_get_available_status())

@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')

@app.route('/scripts/<script_name>')
def script(script_name):
    return send_file(f'scripts/{script_name}')

def backup() -> str:
    file_name = f"backup/data-{datetime.now().strftime('%Y-%m-%d-%H-%M')}.json"
    with open(file_name, "w") as f:
        json.dump(get_data(), f, indent=4)
    print(f"Took a Backup {file_name}")
    return f"Took a Backup {file_name}"

@app.route("/backup")
def backup_route():
    return backup()

@app.before_request
def before_request():
    # if the request is from the login page, don't check the session
    if request.endpoint in ['login', 'static', 'favicon', 'favicon.ico']:
        return None
    try:
        lastused = session['lastused']
    except KeyError:
        return redirect(url_for('login', title="Login"), code=302)
    else:
        if lastused + 500 < time.time():
            session['loggedin'] = False
            # delete the session and all the info 
            return redirect(url_for('login'), code=302)
        
    if 'loggedin' in session:
        if not session['loggedin']:
            return redirect(url_for('login'), code=302)
        session['lastused'] = time.time()
    # if POST
    if request.method == "POST":
        print(backup())
                

@app.route('/logout')
def logout():
    session['loggedin'] = False
    session.pop('id', None)
    session.pop('username', None)
    session.pop('lastused', None)

    return redirect(url_for('login'))

def get_data():
    with open('data.json', "r") as f:
        data = json.load(f)
    return data

@app.route("/incentive")
def incentive():
    data = get_data()
    tabular_data = []
    unique_months = _get_unique_months()
    unique_months.sort()
    return render_template(
        'home/incentive.html', 
        data=tabular_data,
        advisors= _get_advisors(),
        months = unique_months,
    )

@app.route("/export", methods=["POST", "GET"])
def export():
    LOCK = True
    data = json.loads(request.data.decode("utf-8"))
    # write to a text file and send it to the user
    headers = data['headers']
    tdata = data['data']
    try:
        extra = data['extra']
    except KeyError:
        extra = ""
    location = request.environ.get('HTTP_REFERER').split("/")[-1].upper()
    dt = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
    wb = openpyxl.Workbook()
    sheet = wb.active
    #sheet.append([location, dt]) no need to pass cuz file name contains info like that 
    for x in range(len(headers)):
        sheet.append(headers[x])
        tdata[x][1] = [h if 'select' not in h.lower() else ' ' for h in tdata[x][1]]
        for row in tdata[x]:
            is_empty = True
            for y in row:
                if y:
                    is_empty = False
            if is_empty:
                continue
            sheet.append(row)
        for y in range(2):
            sheet.append(list("--"*len(headers[x])))
    if extra:
        for r in extra.split('\n'):
            sheet.append([r])
    file_name = f"exports/export-{location}-{dt}.xlsx"
    open(file_name,"w+").close()
    wb.save(file_name)
    wb.close()
    alert = f"Exported to {file_name} ✅"
    return alert
        
@app.route("/get_incentive/<month>/<advisor>")
@app.route("/get_incentive/<month>")
@app.route("/get_incentive/")
def get_incentive(month=None, advisor=None):
    data = get_data()
    # if there is no number in the month then it is advisor and the month is None
    if month:
        have_number = False
        if not month[0].isnumeric():
            advisor = month
            month = None
    incentive = {}
    tabular_data = []
    uncollected = []
    for project in data:
        for sector in data[project]['sectors']:
            for plot in data[project]['sectors'][sector]['plots']:
                if data[project]['sectors'][sector]['plots'][plot]['status'].lower() in ["available", "not for sale", "held"]:
                    continue
                incentive_percent = int(data[project]['sectors'][sector]['plots'][plot]['incentive']) # in percentage
                adv = data[project]['sectors'][sector]['plots'][plot]['advisor']
                reciept_entries = data[project]['sectors'][sector]['plots'][plot]['reciept_entry']
                is_emi = data[project]['sectors'][sector]['plots'][plot]['is_emi']
                total_amount_recieved = 0
                for reciept in reciept_entries:
                    if month:
                        if month not in reciept['date']:
                            continue
                    if advisor:
                        if advisor != adv:
                            continue
                    reciept_no = reciept['reciept_number']
                    total_amount_recieved += int(reciept['amount'])
                    incentive = int(int(reciept['amount']) * incentive_percent / 100)
                    customer_name = data[project]['sectors'][sector]['plots'][plot]['customer']['name']
                    tabular_data.append(
                        [
                            project,
                            sector,
                            plot,
                            reciept_no,
                            adv,
                            customer_name,
                            reciept['date'],
                            reciept['amount'],
                            incentive,
                            incentive_percent,
                            is_emi
                            ]
                    )
                if is_emi:
                    if not month:
                        continue
                    if advisor:
                        if advisor != adv:
                            continue
                    dt_month = datetime.strptime(month, "%Y-%m")
                    have_emi_for_this_month = False
                    for reciept in reciept_entries:    
                        reciept_Date = datetime.strptime(reciept['date'], "%Y-%m-%d")
                        if reciept_Date.month == dt_month.month and reciept_Date.year == dt_month.year:
                            have_emi_for_this_month = True
                            break
                    
                    if not have_emi_for_this_month:
                        # year and month from dt_month and day from emi_statrt
                        x = datetime(dt_month.year, dt_month.month, dt_month.day)
                        collected_amount = sum([int(x['amount']) for x in reciept_entries if x['amount']])
                        kisht = int(data[project]['sectors'][sector]['plots'][plot]['deal_price']) - collected_amount
                        if not kisht:
                            continue
                        incentive = int(kisht * incentive_percent / 100)
                        customer_name = data[project]['sectors'][sector]['plots'][plot]['customer']['name']
                        uncollected.append(
                            [
                                project,
                                sector,
                                plot,
                                adv,
                                customer_name,
                                x.strftime("%Y-%m-%d"),
                                kisht,
                                incentive,
                                incentive_percent,
                                is_emi
                                ]
                        )
    return jsonify([tabular_data, uncollected])
def _get_unique_months():
    data = get_data()
    unique_months = []
    for project in data:
        for sector in data[project]['sectors']:
            for plot in data[project]['sectors'][sector]['plots']:
                if "-".join(data[project]['sectors'][sector]['plots'][plot]['date'].split('-')[1:]) not in unique_months:
                    date = "-".join(data[project]['sectors'][sector]['plots'][plot]['date'].split('-')[:2])
                    if date and date not in unique_months:
                        unique_months.append(date)
                for receipt in data[project]['sectors'][sector]['plots'][plot]['reciept_entry']:
                    if "-".join(receipt['date'].split('-')[1:]) not in unique_months:
                        date = "-".join(receipt['date'].split('-')[:2])
                        if date and date not in unique_months:
                            unique_months.append(date)
    unique_months.sort()
    return unique_months
@app.route("/search")
def search():
    data = get_data()
    unique_advisors = []
    unique_months = _get_unique_months()
    # tabular form of data
    # Project | Sector | Plot | Advisor | Customer Name | Status | EMI | Date | Size | Rate | Price |

    tabular_data = []
    unique_advisors = []
    unique_customer_names = []
    unique_status = []
    unique_date = []
    unique_size = []
    unique_rate = []
    unique_price = []
    plot_identifications = []
    [plot_identifications.append(str(x)) for x in data.keys()]
    for project in data:
        for sector in data[project]['sectors']:
            for plot in data[project]['sectors'][sector]['plots']:
                plot_identification = f"{project}-{sector}-{plot}"
                advisor = data[project]['sectors'][sector]['plots'][plot]['advisor']
                customer_name = data[project]['sectors'][sector]['plots'][plot]['customer']['name'] if data[project]['sectors'][sector]['plots'][plot]['customer'] else ""
                status = data[project]['sectors'][sector]['plots'][plot]['status']
                emi = str(data[project]['sectors'][sector]['plots'][plot]['is_emi']).lower()
                date = data[project]['sectors'][sector]['plots'][plot]['date']
                size = data[project]['sectors'][sector]['plots'][plot]['size']
                size = f"{size[0]}x{size[1]}" if size else ''
                rate = data[project]['sectors'][sector]['plots'][plot]['rate']
                price = data[project]['sectors'][sector]['plots'][plot]['price']
                files = data[project]['sectors'][sector]['plots'][plot]['files']
                if advisor not in unique_advisors:
                    unique_advisors.append(advisor)
                if customer_name not in unique_customer_names:
                    unique_customer_names.append(customer_name)
                if status not in unique_status:
                    unique_status.append(status)
                if size not in unique_size:
                    unique_size.append(size)
                if rate not in unique_rate:
                    unique_rate.append(rate)
                if price not in unique_price:
                    unique_price.append(price)
                if plot_identification not in plot_identifications:
                    plot_identifications.append(plot_identification)
                gained_amount = sum([r['amount'] for r in data[project]['sectors'][sector]['plots'][plot]['reciept_entry'] if r['amount']])
                if not price:
                    price = 0
                remaining_amount = price-gained_amount
                g_r = f"{gained_amount}/{remaining_amount}"
                tabular_data.append(
                    [
                        plot_identification,
                        advisor,
                        customer_name,
                        status,
                        emi,
                        date,
                        size,
                        rate,
                        price,
                        g_r,
                        files
                    ]
                )
    
    # if there is a '' in any of the data remove it 
    unique_rate = [str(x) for x in unique_rate]
    unique_price = [str(x) for x in unique_price]
    unique_size = [str(x) for x in unique_size]
    unique_status.append("")
    unique_months.append("")

    unique_advisors.sort()
    unique_months.sort()
    unique_customer_names.sort()
    unique_status.sort()
    unique_date.sort()
    unique_size.sort()
    unique_rate.sort()
    unique_price.sort()
    #plot_identifications.sort()    
    return render_template(
        'home/search.html', 
        data=data,
        plot_identifications = plot_identifications,
        unique_advisors=unique_advisors, 
        unique_months=unique_months,
        unique_customer_names=unique_customer_names,
        unique_status=unique_status,
        unique_emi=["", "true", "false"],
        unique_date=unique_date,
        unique_size=unique_size,
        unique_rate=unique_rate,
        unique_price=unique_price,
        tabular_data=tabular_data,
        title="Search"
    )

@app.route("/get_backend_data/<project>/<sector>/<plot>")
def get_backend_data(project, sector, plot):
    data = get_data()
    return jsonify(data[project]['sectors'][sector]['plots'][plot])

@app.route("/get_advisor_projects/<advisor>")
@app.route("/get_advisor_projects/")
def get_advisor_projects(advisor="None"):
    data = get_data()
    projects = []
    for project in data:
        for sector in data[project]['sectors']:
            for plot in data[project]['sectors'][sector]['plots']:
                if data[project]['sectors'][sector]['plots'][plot]['advisor'] == advisor:
                    customer_name = data[project]['sectors'][sector]['plots'][plot]['customer']['name']
                    date = data[project]['sectors'][sector]['plots'][plot]['date']
                    projects.append(f"{project}-{sector}-{plot} TO {customer_name} On {date}")
    if not projects:
        projects.append("No Projects Found")
    return jsonify(projects)

@app.route("/get_month_sale/<month>/<year>")
def get_month_sale(month, year):
    data = get_data()
    month_sale = ""
    ammount = 0
    for project in data:
        for sector in data[project]['sectors']:
            for plot in data[project]['sectors'][sector]['plots']:
                if "-".join(data[project]['sectors'][sector]['plots'][plot]['date'].split('-')[1:]) == month+"-"+year:
                    month_sale += f"{project} {sector} {plot} {data[project]['sectors'][sector]['plots'][plot]['price']} by {data[project]['sectors'][sector]['plots'][plot]['advisor']}\n"
                    ammount += int(data[project]['sectors'][sector]['plots'][plot]['price'])

    month_sale  = f"Total Sale: {ammount}" + "\n" + month_sale
    month_sale = month_sale.split('\n')
    return jsonify(month_sale)

@app.route("/new_sale", methods=["GET", "POST"])
def new_sale():
    if request.method == "POST":
        # get the data from the form
        json_data = get_data()
        data = dict(request.form)
        data['emi'] = True if data.get('emi') else False
        if data['status'] == "available":
            json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']] = template
            with open('data.json', "w") as f:
                json.dump(json_data, f, indent=4)
            return "Success removed an entry"
        uploads = request.files.getlist('upload')
        uploads = [x for x in uploads if x]
        
        # save the uplaoded files to pdfs folder with name scheme project-sector-plot-n.pdf
        # get the data from the form
        '''
        for x in data:
            if "emi" in x or "advisor" in x:
                continue
            if not data[x]:
                return f"Please fill all the fields {x}"'''
        # get the data from the json file
        # update the json data
        # if status is changed to available then reset the value
        
        json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['customer'] = {
            "name": data['customer_name'],
            "phone": data['customer_phone'],
            "address": data['customer_address']
        }
        json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['status'] = data['status']
        json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['is_emi'] = data['emi']
        json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['reciept_entry'] = []
        json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['advisor'] = data['newadvisor'] if data['newadvisor'] else data['advisor']
        json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['date'] = data['date']
        json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['size'] = [int(data['size_width']), int(data['size_length'])]
        json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['rate'] = int(data['rate'])
        json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['price'] = int(data['price'])
        json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['deal_price'] = int(data['deal_price'])
        json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['booking_amount'] = int(data['booking_amount'])
        json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['incentive'] = int(data['incentive'])
        for number,file in enumerate(uploads):
            if not file:
                break
            file_name = f"{data['project']}-{data['sector']}-{data['plot']}-{number}.pdf"
            with open("pdf/"+file_name, "wb") as f:
                f.write(file.read())
            if file_name not in json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['files']:
                json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['files'].append(file_name)

        with open('data.json', "w") as f:
            json.dump(json_data, f, indent=4)
        return "Success"
    # return data of the plots that are available or "Not for sale" or "held"
    data = get_data()           
    return render_template(
        'home/new_sale.html', 
        data=data,
        available_status=_get_available_status(), 
        availalbe_emi_status = ["true", "false"],
        title="New Sale",
        advisors = _get_advisors()
        )

@app.route("/get_month_emi/<yearmonth>/<project>")
@app.route("/get_month_emi/<yearmonth>")
def get_month_emi(yearmonth=None, project=None):
    data = get_data()
    
    if not yearmonth or yearmonth == "0":
        yearmonth = datetime.now().strftime("%Y-%m")
    tabular_data = []
    uncollected = []
    dt_month = datetime.strptime(yearmonth, "%Y-%m")
    for project in data:
        if project:
            if project != project:
                continue
        for sector in data[project]['sectors']:
            for plot in data[project]['sectors'][sector]['plots']:
                if data[project]['sectors'][sector]['plots'][plot]['status'].lower() in ["available", "not for sale", "held"]:
                    continue
                if not data[project]['sectors'][sector]['plots'][plot]['is_emi']:
                    continue
                reciept_entries = data[project]['sectors'][sector]['plots'][plot]['reciept_entry']
                kisht = int(data[project]['sectors'][sector]['plots'][plot]['deal_price']) - sum([int(x['amount']) for x in reciept_entries if x['amount']])
                collected_amount = sum([int(x['amount']) for x in reciept_entries if x['amount']])
                have_this_month_emi = False
                for reciept in reciept_entries:
                    reciept_Date = datetime.strptime(reciept['date'], "%Y-%m-%d")
                    if reciept_Date.month == dt_month.month and reciept_Date.year == dt_month.year:
                        have_this_month_emi = True
                        tabular_data.append(
                            [
                                project,
                                sector,
                                plot,
                                reciept['reciept_number'],
                                data[project]['sectors'][sector]['plots'][plot]['customer']['name'],
                                reciept['date'],
                                reciept['amount'],
                                kisht,
                                data[project]['sectors'][sector]['plots'][plot]['advisor']
                            ]
                        )
                if not have_this_month_emi:
                    # kisht would be deal price minus total amount of receipt done
                    if not kisht:
                        continue
                    uncollected.append(
                        [
                            project,
                            sector,
                            plot,
                            data[project]['sectors'][sector]['plots'][plot]['customer']['name'],
                            dt_month.strftime("%Y-%m-%d"),
                            collected_amount,
                            kisht,
                            data[project]['sectors'][sector]['plots'][plot]['advisor']
                        ]
                    )
    return jsonify([tabular_data, uncollected])



@app.route('/emi')
def emi():
    return render_template(
        '/home/emi.html', 
        title="EMI",
        months = _get_unique_months(),
        projects = _get_projects()
    )

def _get_projects():
    data = get_data()
    projects = []
    for project in data:
        projects.append(project)
    return projects

@app.route("/print_receipt/<rnumber>")
def print_receipt(rnumber:int):
    # first find the reciept number in the json file
    data = get_data()
    found = False
    for project in data:
        for sector in data[project]['sectors']:
            for plot in data[project]['sectors'][sector]['plots']:
                for receipt in data[project]['sectors'][sector]['plots'][plot]['reciept_entry']:
                    if str(receipt['reciept_number']) == str(rnumber):
                        found = True
                        rno = receipt['reciept_number']
                        ammount = receipt['amount']
                        mode = receipt['mode']
                        if mode == "cheque":
                            mode = f"Cheque {receipt['cheque']['bank']}/{receipt['cheque']['cheque_no']}"
                        date = receipt['date']
                        size = [str(x) for x in data[project]['sectors'][sector]['plots'][plot]['size']]
                        size = "X".join(size)
                        try:
                            address = data[project]['address']
                        except KeyError:
                            address = ""
                        mobile_no = "9610449712"
                        company_name = "Monarch Buildestate Pvt. Ltd."
                        project_name = project
                        customer = data[project]['sectors'][sector]['plots'][plot]['customer']['name']
                        
                        
                        return render_template(
                            'home/print_receipt.html',
                            receipt=receipt,
                            mobile_no=mobile_no,
                            company_name=company_name,
                            project_name=project_name,
                            address=address,
                            rno=rno,
                            ammount=ammount,
                            mode=mode,
                            date=date,
                            sector=sector,
                            plot=plot,
                            size=size,
                            customer=customer,
                            title="Print Receipt"
                        )
                        
    if not found:
        return "No Receipt Found"
    


@app.route("/receipt", methods=["GET", "POST"])
def receipt():
    if request.method == "POST":
        # get the data from the form
        json_data = get_data()
        form_data = dict(request.form)
        for x in form_data:
            if not form_data[x]:
                if form_data["mode"] != "cheque" and (x=="bank" or x=="cheque_no"):
                    continue
                return f"Please fill all the fields Missing Field: {x}"
        data = {
            "mode": form_data["mode"],
            "date": form_data["receiptDate"],
            "amount": int(form_data["amount"]),
            "is_cheque": True if form_data["mode"] == "cheque" else False,     
            "reciept_number": form_data['receiptnumber']           
        }
        if data["is_cheque"]:
            data["cheque"] = {
                "bank": form_data["bank"],
                "cheque_no": form_data["cheque_no"]
            }
        json_data[form_data['project']]["sectors"][form_data['sector']]["plots"][form_data['plot']]['reciept_entry'].append(data)
        with open('data.json', "w") as f:
            json.dump(json_data, f, indent=4)

        return "Success"
    data = get_data()

    new_data = deepcopy(data)
    for project in data:
        for sector in data[project]['sectors']:
            for plot in data[project]['sectors'][sector]['plots']:
                if data[project]['sectors'][sector]['plots'][plot]['status'].lower() in ["available", "not for sale", "held"]:
                    del new_data[project]['sectors'][sector]['plots'][plot]
    available_payment_method = ["cash", "cheque", "BT"]
    return render_template(
        'home/receipt.html', 
        data=new_data,
        available_payment_method=available_payment_method,
        next_reciept_number = _get_next_reciept_number(),
        title="Reciept"
    )

def _get_next_reciept_number():
    data = get_data()
    reciept_numbers = []
    for project in data:
        for sector in data[project]['sectors']:
            for plot in data[project]['sectors'][sector]['plots']:
                for reciept in data[project]['sectors'][sector]['plots'][plot]['reciept_entry']:
                    reciept_numbers.append(int(reciept['reciept_number']))
    if not reciept_numbers:
        return 1
    return max(reciept_numbers) + 1

def _get_advisors():
    data = get_data()
    advisors = []
    for project in data:
        for sector in data[project]['sectors']:
            for plot in data[project]['sectors'][sector]['plots']:
                if data[project]['sectors'][sector]['plots'][plot]['advisor'] not in advisors:
                    if data[project]['sectors'][sector]['plots'][plot]['advisor']:
                        advisors.append(data[project]['sectors'][sector]['plots'][plot]['advisor'])

    advisors.sort()
    return advisors

@app.route("/get_advisors")
def get_advisors():
    return jsonify(_get_advisors())


@app.route("/pdf/<file_name>")
def pdf(file_name):
    # return the file with the file_name
    return send_file("pdf\\"+file_name)

@app.route('/')
def home():
    return render_template('home/home.html', username=session['username'],title="Home")

if __name__ =='__main__':
    # open localhost in browser 
    #webbrowser.open('http://localhost')
    app.run(debug=True, port=80, host="0.0.0.0")
