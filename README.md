
# Real Estate Management System

Experience a comprehensive system with both frontend and backend capabilities designed to streamline the management of real estate sales.

Each plot is characterized by three key properties:
1. Plot Number
2. Sector
3. Colony

## Download

Download the latest version from the automatic build:

[![Package Application with Pyinstaller](https://github.com/SurajBhari/real_estate_managment/actions/workflows/build.yml/badge.svg)](https://github.com/SurajBhari/real_estate_managment/actions/workflows/build.yml)

## Login
![Login Image](https://github.com/SurajBhari/real_estate_managment/assets/45149585/b76210f9-a1ff-442f-a284-3fb6ea4bfdbb)

If using the default hash, the password will be displayed in the console.

*Optional (but recommended):*
Change the hash [here](https://github.com/SurajBhari/real_estate_managment/blob/f180d941e2dbe36947687d5649467675497b3465/validate.py#L5) and use [PyOTP](https://github.com/pyauth/pyotp#google-authenticator-compatible) to enhance security by adding it to your Google Authenticator app.

## Design Choice
The system, designed for single-user local management, avoids unnecessary complications by opting for a single-user approach without usernames.

## Search
![Search Image](https://github.com/SurajBhari/real_estate_managment/assets/45149585/ab6c0b13-89e1-435a-b99b-3cd5c8246a53)

The search functionality offers nine columns for filtering. For instance, you can search for an advisor like "John Harris" with the status "booked."

## New Sale
![New Sale Image](https://github.com/SurajBhari/real_estate_managment/assets/45149585/e1e73b5a-4d00-4552-94b8-7db27455cf13)

The new sale or modification feature allows for easy property status changes, and opting for "available" or "not for sale" removes all associated attributes.

## Receipt
![Receipt Image](https://github.com/SurajBhari/real_estate_managment/assets/45149585/ff080408-e2a4-4399-9c27-9f430f3d9151)

Each entry of money received from the buyer is recorded as a receipt. It provides insights into pending and received amounts.

## Incentive
![Incentive Image](https://github.com/SurajBhari/real_estate_managment/assets/45149585/b4af55dc-dac1-437e-9c7e-678e515182f4)

Advisors receive a percentage of the sale as an incentive, calculated based on the date of receipt. The system also tracks uncollected incentives.

## EMI
![EMI Image](https://github.com/SurajBhari/real_estate_managment/assets/45149585/2b639236-4e84-4b0c-893c-d25aab5f4105)

EMI details showcase received amounts for a specific advisor in a given month, with uncollected payments highlighted in red.

## Global Features
- Export options for EMI, Incentive, and Receipt entries in xlsx format.
- Manual backup option on the home page, ensuring data integrity.
- Changes in data trigger an automatic backup.

## Future Plans
While future updates may include statistical insights into company and sales growth, the current focus is on stability and core functionality.

## Compiling
1. Install requirements from `requirements.txt` using `pip install -r requirements.txt`.
2. Install `pyinstaller` with `pip install pyinstaller`.
3. Compile using the command: `pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" --add-data "scripts;scripts" main.py`.
4. Move `backup`, `export` folders, and `data.json` to the newly created `dist` folder.
5. Use `main.exe` from the `dist` folder.

## Note
This system was designed for local use and has not been exposed to the internet. While some security measures are in place, responsible usage is advised.

---
