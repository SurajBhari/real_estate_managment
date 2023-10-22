# Real Estate Managment System
A fully fledged system with frontend and backend helping you manage sales in a real estate </br>
Each plot have 3 properties -> 1. Its number, 2. The sector it is in, 3. The Colony it is in.</br>

# Download
Download fom latest automatic build from here - >
[![Package Application with Pyinstaller](https://github.com/SurajBhari/real_estate_managment/actions/workflows/build.yml/badge.svg)](https://github.com/SurajBhari/real_estate_managment/actions/workflows/build.yml)

# Login
![image](https://github.com/SurajBhari/real_estate_managment/assets/45149585/b76210f9-a1ff-442f-a284-3fb6ea4bfdbb)
If you are using the default hash then you will get the password in console.

Optional (you should) </br>
Change the hash from [here](https://github.com/SurajBhari/real_estate_managment/blob/f180d941e2dbe36947687d5649467675497b3465/validate.py#L5) </br> 
and then use [PyOTP](https://github.com/pyauth/pyotp#google-authenticator-compatible) to add it to your google authenticator app on your phone. </br>

Design choice</br> 
Why not use username password approach</br>
-> The system is meant for only 1 user to use at a time. and is used only by managers mostly locally. so adding a username password is just adding complications. </br>

# Search
![image](https://github.com/SurajBhari/real_estate_managment/assets/45149585/ab6c0b13-89e1-435a-b99b-3cd5c8246a53)</br>
Search consists of 9 columns. on which you can apply filter with each other at same time. </br>
ex. Advisor `John Harris` having the status of `booked`.</br>

# New Sale
![image](https://github.com/SurajBhari/real_estate_managment/assets/45149585/e1e73b5a-4d00-4552-94b8-7db27455cf13)</br>
New sale or modification allows you to change property of a field. changing this to `available` or `not for sale` will remove every attribute.</br>

Previously I had option to allow entering how many EMI months an EMI can be. </br>
but later decided to only store whether it is EMI or not. if it is then you can get an estimate of how much money is left from the user to be paid. </br>

# Receipt 
![image](https://github.com/SurajBhari/real_estate_managment/assets/45149585/ff080408-e2a4-4399-9c27-9f430f3d9151)</br>
A receipt is every entry of money recieved from the buyer. each booking amount will have receipt. each EMI payment will have a receipt. if done correctly then each receipt numbers are sequential. </br>
Allows you to see list of receipts generated and mode of it. also gives you insight how much is yet to be recieved and how much of it is already recieved.</br>

# Incentive 
![image](https://github.com/SurajBhari/real_estate_managment/assets/45149585/b4af55dc-dac1-437e-9c7e-678e515182f4)</br>
Each sell the company gives a x % of the sale to the advisor as incentive. this x can vary on many factors so its often dynamic.</br>
The Incentive is calculated based of the date of receipt. regardless of the sale date. A % is also given on EMI amount recieved. if the advisor missed any EMI amount to be recieved. it would be shown in `Uncollected` Section</br>

# EMI
![image](https://github.com/SurajBhari/real_estate_managment/assets/45149585/2b639236-4e84-4b0c-893c-d25aab5f4105)</br>
EMI details tells how much EMI amount we have received for a said advisor in a said month. advisor can be none to show all.</br>
The red one means uncollected.</br>


# Global Features
Each of `EMI` `Incentive` `Receipt` have option to export to xlsx format later to be printed.</br>
Backup feature on Home page allows you to manually call for a backup that is stored in the `backup` directory.</br>
alongside this any change in data is done after a backup is taken. </br>
only 1 backup per minute is permitted to prevent clogging of data.</br>

# Future 
I really want to make some statistics out of this. showcasing the growth of company and sales but am currently busy</br>


# Compiling 
1. Install requirements from requirements.txt `pip install -r requirements.txt`</br>
2. Install `pyinstaller` `pip install pyinstaller`</br>
3. `pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" --add-data "scripts;scripts" main.py`</br>
4. Move `backup`, `export` folder AND `data.json`to newly created `dist` folder.</br>
5. Use `main.exe` from `dist` folder.</br>

# Note
This system was never exposed to the internet nor it was made with keeping that in mind. although some security measures are there but that doesn't ensure it. please use responsibily.
