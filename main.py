from flask import Flask, render_template, request, redirect, url_for, session,flash, jsonify, send_file
import re
import openpyxl

import sqlite3
import time
from copy import deepcopy
from datetime import datetime
import json

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '1a2b3c4d5e6d7g8h9i10'

conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

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
try:
    cursor.execute('''
        CREATE TABLE accounts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
except Exception as e:
    # fetch all the data from the table
    cursor.execute('SELECT * FROM accounts')
    rows = cursor.fetchall()
    pass
else:
    cursor.execute('''
        INSERT INTO accounts(username, email, password) VALUES('admin', 'password', 'admin@gmail.com')
    ''')
    conn.commit()



# http://localhost:5000/login/ - this will be the login page, we need to use both GET and POST requests

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Fetch data using a tuple since the result is a tuple
        cursor.execute('SELECT * FROM accounts WHERE username=?', (username, ))
        account = cursor.fetchone()

        if account[2] == password:
            session['loggedin'] = True
            session['id'] = account[0]  # Use the index position to get the values from the tuple
            session['username'] = account[1]
            session['lastused'] = time.time()
            return redirect(url_for('home'))
        else:
            cursor.execute('SELECT * FROM accounts WHERE username=?', (username,))
            account = cursor.fetchone()
            flash("Incorrect username/password!", "danger")

    return render_template('auth/login.html', title="Login")

def _get_available_status():
    return available_status

@app.route("/get_available_status")
def get_available_status():
    return jsonify(_get_available_status())

@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')

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
        if lastused + 100 < time.time():
            session['loggedin'] = False
            # delete the session and all the info 
            return redirect(url_for('login'), code=302)
        
    if 'loggedin' in session:
        if not session['loggedin']:
            return redirect(url_for('login'), code=302)
        session['lastused'] = time.time()


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
    unique_months = []
    for project in data:
        for sector in data[project]['sectors']:
            for plot in data[project]['sectors'][sector]['plots']:
                if data[project]['sectors'][sector]['plots'][plot]['status'].lower() in ["available", "not for sale", "held"]:
                    continue
                month = "-".join(data[project]['sectors'][sector]['plots'][plot]['date'].split('-')[:2])
                if month and month not in unique_months:
                    unique_months.append(month)
    unique_months.sort()
    return render_template(
        'home/incentive.html', 
        data=tabular_data,
        advisors= _get_advisors(),
        months = unique_months,
    )


@app.route("/download/<month>/<radvisor>")
@app.route('/download/<month>')
@app.route('/download/')
def download(month=None, radvisor=None):
    data = get_data()
    
    workbook = openpyxl.Workbook()
    if month:
        if not month[0].isnumeric():
            radvisor = month
            month = None
    worksheet = workbook.active
    for advisor in _get_advisors():
        if radvisor:
            if radvisor != advisor:
                continue
        tabular_data = []
        uncollected = []
        for project in data:
            for sector in data[project]['sectors']:
                for plot in data[project]['sectors'][sector]['plots']:
                    if data[project]['sectors'][sector]['plots'][plot]['status'].lower() in ["available", "not for sale", "held"]:
                        continue
                    if advisor != data[project]['sectors'][sector]['plots'][plot]['advisor']:
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
                                incentive_percent
                                ]
                        )
                    if is_emi:
                        start_date = data[project]['sectors'][sector]['plots'][plot]['emi']['start_date']
                        end_date = data[project]['sectors'][sector]['plots'][plot]['emi']['end_date']
                        start_date = datetime.strptime(start_date, "%Y-%m-%d")
                        end_date = datetime.strptime(end_date, "%Y-%m-%d")
                        if not month:
                            continue
                        dt_month = datetime.strptime(month, "%Y-%m")
                        if not (dt_month >= start_date and dt_month <= end_date):
                            continue
                        have_emi_for_this_month = False
                        for reciept in reciept_entries:
                            reciept_Date = datetime.strptime(reciept['date'], "%Y-%m-%d")
                            if reciept_Date.month == dt_month.month and reciept_Date.year == dt_month.year:
                                have_emi_for_this_month = True
                                break
                        if not have_emi_for_this_month:
                            kisht = int(data[project]['sectors'][sector]['plots'][plot]['emi']['amount']) / int(data[project]['sectors'][sector]['plots'][plot]['emi']['months'])
                            kisht = int(kisht)
                            incentive = int(kisht * incentive_percent / 100)
                            customer_name = data[project]['sectors'][sector]['plots'][plot]['customer']['name']
                            uncollected.append(
                                [
                                    project,
                                    sector,
                                    plot,
                                    adv,
                                    customer_name,
                                    start_date.strftime("%Y-%m-%d"),
                                    kisht,
                                    incentive,
                                    incentive_percent
                                    ]
                            )
        if not tabular_data:
            continue
        worksheet.append(["COLLECTED", advisor])

        worksheet.append(["Project", "Sector", "Plot", "Reciept No", "Advisor", "Customer Name", "Date", "Amount", "Incentive", "Incentive Percent"])
        total_incentive = 0

        for x in tabular_data:
            total_incentive += int(x[8])
            worksheet.append(x)
    
        worksheet.append(["", "", "", "", "", "", "", "", "", ""])
        worksheet.append([total_incentive])
        worksheet.append(["", "", "", "", "", "", "", "", "", ""])
        worksheet.append(["", "", "", "", "", "", "", "", "", ""])
        worksheet.append(["UNCOLLECTED", advisor])
        worksheet.append(["Project", "Sector", "Plot", "Advisor", "Customer Name", "Date", "Amount", "Incentive", "Incentive Percent"])
        total_incentive = 0
        for x in uncollected:
            total_incentive += int(x[7])
            worksheet.append(x)
        worksheet.append(["", "", "", "", "", "", "", "", "", ""])
        worksheet.append([total_incentive*-1])
        worksheet.append(["", "", "", "", "", "", "", "", "", ""])
        worksheet.append(["", "", "", "", "", "", "", "", "", ""])

    file_name = f"./incentive_reports/Incentive-{month}.xlsx"
    workbook.save(file_name)
    return send_file(file_name, as_attachment=True)
        
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
                            incentive_percent
                            ]
                    )
                if is_emi:
                    if not month:
                        continue
                    if advisor:
                        if advisor != adv:
                            continue
                    dt_month = datetime.strptime(month, "%Y-%m")
                    emi_start = data[project]['sectors'][sector]['plots'][plot]['emi']['start_date']
                    emi_end = data[project]['sectors'][sector]['plots'][plot]['emi']['end_date']
                    emi_start = datetime.strptime(emi_start, "%Y-%m-%d")
                    emi_end = datetime.strptime(emi_end, "%Y-%m-%d")
                    if not (dt_month >= emi_start and dt_month <= emi_end):
                        continue
                    have_emi_for_this_month = False               
                    for reciept in reciept_entries:
                        
                        reciept_Date = datetime.strptime(reciept['date'], "%Y-%m-%d")
                        if reciept_Date.month == dt_month.month and reciept_Date.year == dt_month.year:
                            have_emi_for_this_month = True
                            break
                    
                    if not have_emi_for_this_month:
                        # year and month from dt_month and day from emi_statrt
                        x = datetime(dt_month.year, dt_month.month, emi_start.day)
                        kisht = int(data[project]['sectors'][sector]['plots'][plot]['emi']['amount']) / int(data[project]['sectors'][sector]['plots'][plot]['emi']['months'])
                        kisht = int(kisht)
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
                                incentive_percent
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
    unique_months.sort()
    return unique_months
@app.route("/search")
def search():
    data = get_data()
    unique_advisors = []
    for project in data:
        for sector in data[project]['sectors']:
            for plot in data[project]['sectors'][sector]['plots']:
                if data[project]['sectors'][sector]['plots'][plot]['advisor'] not in unique_advisors:
                    unique_advisors.append(data[project]['sectors'][sector]['plots'][plot]['advisor'])
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
                        files
                    ]
                )
    
    # if there is a '' in any of the data remove it 
    for x in unique_rate:
        if x == "":
            unique_rate.remove(x)
    for x in unique_price:
        if x == "":
            unique_price.remove(x)
    for x in unique_size:
        if x == "":
            unique_size.remove(x)
    for x in unique_date:
        if x == "":
            unique_date.remove(x)
    for x in unique_status:
        if x == "":
            unique_status.remove(x)
    for x in unique_customer_names:
        if x == "":
            unique_customer_names.remove(x)
    for x in unique_advisors:
        if x == "":
            unique_advisors.remove(x)
    for x in unique_months:
        if x == "":
            unique_months.remove(x)

    unique_advisors.sort()
    unique_months.sort()
    unique_customer_names.sort()
    unique_status.sort()
    unique_date.sort()
    unique_size.sort()
    unique_rate.sort()
    unique_price.sort()
    plot_identifications.sort()    
    return render_template(
        'home/search.html', 
        data=data,
        plot_identifications = plot_identifications,
        unique_advisors=unique_advisors, 
        unique_months=unique_months,
        unique_customer_names=unique_customer_names,
        unique_status=unique_status,
        unique_emi=["true", "false"],
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
        if data["emi"]:
            emi = {
                "amount": data['emi_amount'],
                "months": data['emi_duration'],
                "start_date": data['emi_start_date'],
                "end_date": data['emi_end_date']
            }
            json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['is_emi'] = True
            json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['emi'] = emi
        else:
            json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['emi'] = {}
            json_data[data['project']]["sectors"][data['sector']]["plots"][data['plot']]['is_emi'] = False
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
                emi_start_date = datetime.strptime(data[project]['sectors'][sector]['plots'][plot]['emi']['start_date'], "%Y-%m-%d")
                emi_end_date = datetime.strptime(data[project]['sectors'][sector]['plots'][plot]['emi']['end_date'], "%Y-%m-%d")
                if not (dt_month >= emi_start_date and dt_month <= emi_end_date):
                    continue
                reciept_entries = data[project]['sectors'][sector]['plots'][plot]['reciept_entry']
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
                                data[project]['sectors'][sector]['plots'][plot]['emi']['amount'],
                                data[project]['sectors'][sector]['plots'][plot]['advisor']
                            ]
                        )

                if not have_this_month_emi:
                    kisht = int(data[project]['sectors'][sector]['plots'][plot]['emi']['amount']) / int(data[project]['sectors'][sector]['plots'][plot]['emi']['months'])
                    kisht = int(kisht)
                    uncollected.append(
                        [
                            project,
                            sector,
                            plot,
                            data[project]['sectors'][sector]['plots'][plot]['customer']['name'],
                            dt_month.strftime("%Y-%m-%d"),
                            kisht,
                            data[project]['sectors'][sector]['plots'][plot]['emi']['amount'],
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
@app.route("/receipt/", methods=["GET", "POST"])
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
            "amount": form_data["amount"],
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
        title="Reciept"
    )


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

@app.route('/profile')
def profile():
    return render_template('auth/profile.html', username=session['username'],title="Profile") 

if __name__ =='__main__':
	app.run(debug=True, port=80, host="0.0.0.0")
