[python-broadlink-smart-plug-mini](#python-broadlink-smart-plug-mini)
- [Summary](#summary)
- [Quick start](#quick-start)
- [Background](#background)
- [python\_broadlink\_smart\_plug\_mini\_info.py](#python_broadlink_smart_plug_mini_infopy)
  - [Example standard output of python\_broadlink\_smart\_plug\_mini\_info.py](#example-standard-output-of-python_broadlink_smart_plug_mini_infopy)
- [smart\_plug\_mini.cfg](#smart_plug_minicfg)
- [smart\_plug\_mini.py](#smart_plug_minipy)
  - [Example standard output of smart\_plug\_mini.py](#example-standard-output-of-smart_plug_minipy)
- [csv\_to\_google\_sheet.py](#csv_to_google_sheetpy)
- [Configuration of gspread for "python csv\_to\_google\_sheet.py"](#configuration-of-gspread-for-python-csv_to_google_sheetpy)
- [Example crontab to run hourly on Raspberry Pi or another linux system](#example-crontab-to-run-hourly-on-raspberry-pi-or-another-linux-system)
- [Sniffing the e-Control App](#sniffing-the-e-control-app)
  - [Month request/response](#month-requestresponse)
    - [Month request](#month-request)
    - [Month response](#month-response)
  - [24 hour request/response](#24-hour-requestresponse)
    - [24 hour request](#24-hour-request)
    - [24 hour response](#24-hour-response)
  - [Playing around with the server API](#playing-around-with-the-server-api)

---
# Summary

Get history kWh consumption of broadlink Smart Plug Mini (tested with model SP3S-EU) using the broadlink server and append later kWh measurements to a .csv file format per device.

I have 2 times model Smart plug SP3S-EU and tested with those.
Probably this also works for other broadlink SP mini models.

---
# Quick start

- Make sure you have installed Python 3.9 or higher. [Here is more information about installing Python](https://realpython.com/installing-python/)
- see [requirements.txt](https://raw.githubusercontent.com/ZuinigeRijder/python-broadlink-smart-plug-mini/main/requirements.txt) for extra needed packages
- To get the MAC addresses for your Smart Plug Mini, run script [python_broadlink_smart_mini_info.py](#python_broadlink_smart_plug_mini_infopy) which uses the library [python-broadlink](https://github.com/mjg59/python-broadlink). Instead of using this tool, you can also look up the connected devices MAC addresses in your router, then you do not need to install the library python-broadlink.
- Configure [smart_plug_mini.cfg](#smart_plug_minicfg), e.g. MAC addresses
- Run the [smart_plug_mini.py](#smart_plug_minipy) to generate per configured device a DEVICE_NAME.csv file from the configured datetime onwards
- optionally run [csv_to_google_sheet.py](#csv_to_google_sheetpy), but then you have to install and [configure package gspread](#configuration-of-gspread-for-python-csv_to_google_sheetpy)

A short video of how csv_to_google_sheet.py can look on an Android phone, [can be found here](https://www.youtube.com/shorts/p4IWoX7yNpE).
Of course you can also view the Google Spreadsheet on your computer or tablet, e.g. Windows or Mac.

<a href="http://www.youtube.com/watch?feature=player_embedded&v=p4IWoX7yNpE" target="_blank"><img src="http://img.youtube.com/vi/p4IWoX7yNpE/0.jpg" alt="Broadlink Smart Plug Mini showing csv results in Google Spreadsheet" width="240" height="180" border="10" /></a>

---
# Background

I am using 2 Smart plug SP3S-EU since 2018. The e-control App was limited in functionality/views. One of the strange things is e.g. the fact that you cannot see the month December of the year before the current year. So I was looking around if someone already had a better solution. I found the library [python-broadlink](https://github.com/mjg59/python-broadlink), but this was only for local access to your broadlink smart plug devices (get direct power measurements). So I decided to try to [sniff the e-Control app, see here](#sniffing-the-e-control-app).

In short, it appeared way easier to get the historical data of my smart plug mini than expected. You do not even have to login, you only need the server name and MAC address of the smart plug mini. Oops, so simple ;-)

So I started making [a simple standalone python script smart_plug_mini.py which appends the history data per hour in a csv file for each device](#smart_plug_minipy) and made [some parts configurable](#smart_plug_minicfg).
Also the tool writes the Day, Weeks, Months and Years summaries to separate .csv files per device.

---
# python_broadlink_smart_plug_mini_info.py

All the credits goes to [python-broadlink library](https://github.com/mjg59/python-broadlink).
This small program just outputs the information from the library of the detected smart plug devices.
The MAC addresses are needed for the configuration of the real tool.

Note: Instead of using this tool, you can also look up the connected devices MAC addresses in your router, then you do not need to install the library python-broadlink.


## Example standard output of python_broadlink_smart_plug_mini_info.py

```
C:\Users\Rick\git\broadlink>python python_broadlink_smart_plug_mini_info.py
device: Badkamer (Broadlink SP3S-EU 0x947a / 192.168.178.214:80 / 32:AA:31:72:63:43)
device: Lader (Broadlink SP3S-EU 0x947a / 192.168.178.234:80 / 32:AA:31:72:62:40)
```

Remarks for this example output:
- the MAC addresses are not my real SP3S-EU MAC addresses (I changed them, also in the rest of the examples)
- you have to configure the MAC addresses 32:AA:31:72:63:43 and 32:AA:31:72:62:40 in [smart_plug_mini.cfg](#smart_plug_minicfg)

---
# smart_plug_mini.cfg

[This configuration file](https://raw.githubusercontent.com/ZuinigeRijder/python-broadlink-smart-plug-mini/main/smart_plug_mini.cfg) needs to be configured once for the smart_plug_mini.py script.

```
[smart_plug_mini]
local_timezone = Europe/Amsterdam
server = https://0000000000000000000000007a940000rtasquery.ibroadlink.com
device_names = Room1, Room2
device_macs = 32:AA:31:72:62:40, 32:AA:31:72:63:43
report_types = fw_spminielec_v1, fw_spminielec_v1
start_dates = 2023-01-01 00:00, 2023-01-01 00:00
time_filter = "timefilter":{}
```

Remarks to the configuration:
- local_timezone: change into your local_timezone, see [Wiki column "TZ database name" for valid entries](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
- server: this is the only server I am now aware of, but made it configurable in case you need another server
- device_names: comma separated list of names per device, if you have only one device, just mention one name without comma
- device_macs:  comma separated list of MAC address per device
- report_types: comma separated list of report type per device, you do not need to change this
- start_dates: comma separated list of date per device you want to start filling the history in .csv files (note: when .csv file already exists, the start_date is ignored and last entry of csv file is taken for later measurements)
- time_filter: this is the timefilter for hourly measurements, maybe you want to play with this setting

---
# smart_plug_mini.py

Simple Python3 script retrieve (history) kWh values for the configured Smart Plug mini devices.

Usage:
```
python smart_plug_mini.py
```
INPUTFILE:
- smart_plug_mini.cfg

Standard output:
- progress of what is done

OUTPUTFILES (for each configured DEVICE_NAME):
- DEVICE_NAME.csv: appended with later kWh data, [example](https://raw.githubusercontent.com/ZuinigeRijder/python-broadlink-smart-plug-mini/main/examples/Badkamer.csv)
- DEVICE_NAME.days.csv: days summary, [example](https://raw.githubusercontent.com/ZuinigeRijder/python-broadlink-smart-plug-mini/main/examples/Badkamer.days.csv)
- DEVICE_NAME.weeks.csv: weeks summary, [example](https://raw.githubusercontent.com/ZuinigeRijder/python-broadlink-smart-plug-mini/main/examples/Badkamer.weeks.csv)
- DEVICE_NAME.months.csv: months summary, [example](https://raw.githubusercontent.com/ZuinigeRijder/python-broadlink-smart-plug-mini/main/examples/Badkamer.months.csv)
- DEVICE_NAME.years.csv: years summary, [example](https://raw.githubusercontent.com/ZuinigeRijder/python-broadlink-smart-plug-mini/main/examples/Badkamer.years.csv)

---
## Example standard output of smart_plug_mini.py

```
C:\Users\Rick\git\broadlink>python smart_plug_mini.py
##### Lader.csv ######################################
last line Lader.csv: 2023-02-04 12:00, 4349.84, 0.00,  0.00,  18.43,  0.02,  71.98
                  2023-02-04 12:00
date_start local: 2023-02-04 13:00:00+01:00
now local       : 2023-02-04 14:12:00+01:00
Lader: from 2023-02-04 13:00:00+01:00 to 2023-03-04 13:00:00+01:00
Opening Lader.csv
Lader.csv: 2023-02-04 13:00, 4349.84, 0.00,  0.00,  18.43,  0.02,  71.98
Lader.csv: 2023-02-04 14:00, 4349.84, 0.00,  0.00,  18.43,  0.02,  71.98
Closing Lader.csv
##### Badkamer.csv ######################################
last line Badkamer.csv: 2023-02-04 12:00, 649.65, 0.06,  0.52,  5.09,  3.13,  30.66
                  2023-02-04 12:00
date_start local: 2023-02-04 13:00:00+01:00
now local       : 2023-02-04 14:12:00+01:00
Badkamer: from 2023-02-04 13:00:00+01:00 to 2023-03-04 13:00:00+01:00
Opening Badkamer.csv
Badkamer.csv: 2023-02-04 13:00, 649.76, 0.11,  0.63,  5.20,  3.24,  30.77
Badkamer.csv: 2023-02-04 14:00, 649.76, 0.00,  0.63,  5.20,  3.24,  30.77
Closing Badkamer.csv
```

Some remarks from this example:
- the Lader.csv and Badkamer.csv were already filled with data from 2018 onwards till 2023-02-04 12:00 localtime
- running this script again after 2 hours shows that only after this time (1 hour later) new history is requested and 2 new hourly measurements are added

Example part of e.g. Badkamer.csv:
```
Date, Cumulative kWh, Delta +kWh, Days +kWh, Weeks +kWh, Months +kWh, Years +kWh
.....
2023-02-02 21:00, 647.83, 0.00,  0.49,  3.27,  1.31,  28.84
2023-02-02 22:00, 648.13, 0.30,  0.79,  3.57,  1.61,  29.14
2023-02-02 23:00, 648.13, 0.00,  0.79,  3.57,  1.61,  29.14
2023-02-03 00:00, 648.13, 0.00,  0.00,  3.57,  1.61,  29.14
2023-02-03 01:00, 648.13, 0.00,  0.00,  3.57,  1.61,  29.14
2023-02-03 02:00, 648.13, 0.00,  0.00,  3.57,  1.61,  29.14
2023-02-03 03:00, 648.13, 0.00,  0.00,  3.57,  1.61,  29.14
2023-02-03 04:00, 648.13, 0.00,  0.00,  3.57,  1.61,  29.14
2023-02-03 05:00, 648.13, 0.00,  0.00,  3.57,  1.61,  29.14
2023-02-03 06:00, 648.13, 0.00,  0.00,  3.57,  1.61,  29.14
2023-02-03 07:00, 648.51, 0.38,  0.38,  3.95,  1.99,  29.52
2023-02-03 08:00, 648.51, 0.00,  0.38,  3.95,  1.99,  29.52
2023-02-03 09:00, 648.51, 0.00,  0.38,  3.95,  1.99,  29.52
2023-02-03 10:00, 648.51, 0.00,  0.38,  3.95,  1.99,  29.52
2023-02-03 11:00, 648.51, 0.00,  0.38,  3.95,  1.99,  29.52
2023-02-03 12:00, 648.85, 0.34,  0.72,  4.29,  2.33,  29.86
2023-02-03 13:00, 648.85, 0.00,  0.72,  4.29,  2.33,  29.86
2023-02-03 14:00, 648.85, 0.00,  0.72,  4.29,  2.33,  29.86
2023-02-03 15:00, 648.85, 0.00,  0.72,  4.29,  2.33,  29.86
2023-02-03 16:00, 648.85, 0.00,  0.72,  4.29,  2.33,  29.86
2023-02-03 17:00, 648.85, 0.00,  0.72,  4.29,  2.33,  29.86
2023-02-03 18:00, 648.85, 0.00,  0.72,  4.29,  2.33,  29.86
2023-02-03 19:00, 648.85, 0.00,  0.72,  4.29,  2.33,  29.86
2023-02-03 20:00, 648.85, 0.00,  0.72,  4.29,  2.33,  29.86
2023-02-03 21:00, 648.85, 0.00,  0.72,  4.29,  2.33,  29.86
```

Some remarks from this example:
- 2023-02-02 22:00 you see that 0.3 kWh has been used in one hour
- cumulative day value is increased to 0.79 kWh
- cumulative week value is increased to 3.57 kWh
- cumulative month value is increased to 1.61 kWh
- cumulative year value is increased to 29.14 kWh
- 2023-02-03 00:00 the day value is reset to 0 kWh (new day)

A screenshot for [example spreadsheet Badkamer.xlsx](https://raw.githubusercontent.com/ZuinigeRijder/python-broadlink-smart-plug-mini/main/examples/Badkamer.xlsx) which has imported a larger Badkamer.csv:
- ![alt text](https://raw.githubusercontent.com/ZuinigeRijder/python-broadlink-smart-plug-mini/main/examples/Badkamer.xlsx.jpg)

---
# csv_to_google_sheet.py

Simple Python3 script to read the smart_plug_mini.py generated csv files and write a summary for each device to a separate Google spreadsheet.

Note: you need to install the package gspread and configure gspread, [see here for the configuration](#configuration-of-gspread-for-python-csv_to_google_sheetpy)

Usage:
```
python csv_to_google_sheet.py
```
INPUTFILES:
- smart_plug_mini.cfg
- for each configured DEVICE_NAME:
- - DEVICE_NAME.csv
- - DEVICE_NAME.days.csv
- - DEVICE_NAME.weeks.csv
- - DEVICE_NAME.months.csv
- - DEVICE_NAME.years.csv

Standard output:
- progress of what is done

OUTPUT SPREADSHEET:
- DEVICE_NAME.SP (for each configured DEVICE_NAME)

So the smart_plug_mini.py tool runs on my Raspberry Pi server, but I want to look at the results, without having to login to my server. So another tool has been made, which copies a summary to a google spreadsheet for each device: csv_to_google_sheet.py

The Google spreadsheet contains kWh usage, including nice diagrams, when you [copy the example Google spreadsheet Room.SP and rename it to DEVICE_NAME.SP](https://docs.google.com/spreadsheets/d/1SwFmaei27NlpJ6eP104U_PIEgxJK9A3VBEeYZHahY4g/edit?usp=sharing)):
- last written Date, Time, kWh, Hour, Day, Week, Month, Year
- last 48 hours
- last 32 days
- last 27 weeks
- last 25 months
- last 25 years ;-)

A short video of how it can look on an Android phone, [can be found here](https://www.youtube.com/shorts/p4IWoX7yNpE).
Of course you can also view the Google Spreadsheet on your computer or tablet, e.g. Windows or Mac.

<a href="http://www.youtube.com/watch?feature=player_embedded&v=p4IWoX7yNpE" target="_blank"><img src="http://img.youtube.com/vi/p4IWoX7yNpE/0.jpg" alt="Broadlink Smart Plug Mini showing csv results in Google Spreadsheet" width="240" height="180" border="10" /></a>

---
# Configuration of gspread for "python csv_to_google_sheet.py"
For updating a Google Spreadsheet, csv_to_google_sheet.py is using the package gspread.
For Authentication with Google Spreadsheet you have to configure authentication for gspread.
This [authentication configuration is described here](https://docs.gspread.org/en/latest/oauth2.html)

The csv_to_google_sheet.py script uses access to the Google spreadsheets on behalf of a bot account using Service Account.

Follow the steps in this link above, here is the summary of these steps:
- Enable API Access for a Project
- - Head to [Google Developers Console](https://console.developers.google.com/) and create a new project (or select the one you already have).
- - In the box labeled "Search for APIs and Services", search for "Google Drive API" and enable it.
- - In the box labeled "Search for APIs and Services", search for "Google Sheets API" and enable it
- For Bots: Using Service Account
- - Go to "APIs & Services > Credentials" and choose "Create credentials > Service account key".
- - Fill out the form
- - Click "Create" and "Done".
- - Press "Manage service accounts" above Service Accounts.
- - Press on : near recently created service account and select "Manage keys" and then click on "ADD KEY > Create new key".
- - Select JSON key type and press "Create".
- - You will automatically download a JSON file with credentials
- - Remember the path to the downloaded credentials json file. Also, in the next step you will need the value of client_email from this file.
- - Move the downloaded json file to ~/.config/gspread/service_account.json. Windows users should put this file to %APPDATA%\gspread\service_account.json.
- Setup a Google Spreasheet to be updated by csv_to_google_sheet.py (for each device one google spreadsheet)
- - In Google Spreadsheet, create an empty Google Spreadsheet with the name: DEVICE_NAME.SP or [copy the example Google spreadsheet Room.SP and rename it to DEVICE_NAME.SP](https://docs.google.com/spreadsheets/d/1SwFmaei27NlpJ6eP104U_PIEgxJK9A3VBEeYZHahY4g/edit?usp=sharing))
- - Go to your spreadsheet and share it with the client_email from the step above (inside service_account.json)
- run "python csv_to_google_sheet.py" and if everything is correct, the DEVICE_NAME.SP will be updated with a summary of the .csv files
- configure to run "python csv_to_google_sheet.py" regularly, after having run "python smart_plug_mini.py"

---
# Example crontab to run hourly on Raspberry Pi or another linux system

Example script [run_smart_plug_mini_once.sh](https://raw.githubusercontent.com/ZuinigeRijder/python-broadlink-smart-plug-mini/main/examples/run_smart_plug_mini_once.sh) to run smart_plug_mini.py on a linux based system.

Steps:
- create a directory smart_plug_mini in your home directory
- copy run_smart_plug_mini_once.sh, smart_plug_mini.cfg and smart_plug_mini.py in this smart_plug_mini directory
- change inside smart_plug_mini.cfg the smart_plug_mini settings
- chmod + x run_smart_plug_mini_once.sh
- optionally: add running "python csv_to_google_sheet.py" to this script

Add the following line in your crontab -e to run it once per hour 9 minutes later (crontab -e):
```
9 * * * * ~/smart_plug_mini/run_smart_plug_mini_once.sh >> ~/smart_plug_mini/run_smart_plug_mini_once.log 2>&1
```

---
# Sniffing the e-Control App

For the ones who also want to be able to sniff the calls from e-Control the App, this is how I did it (do it at your own risk):

- Installed NoxPlayer emulator in Windows 10 and emulate Android 5
- Installed Burp Suite Community Edition on Windows 10
- Then followed this guide without installing e-Control App yet: [Android App Traffic Decryption using Nox Player - Windows Guide](https://archive.ph/k1hIG)
- installed e-Control App and login with my credentials
- Enabled proxy and opened e-Control App and in the Burp Suite the decoded https requests/responses were available

I was mainly interested in the "My Energy" information from the e-Control App.

## Month request/response
### Month request

```
POST /dataservice/v2/device/stats HTTP/1.1
Content-Length: 386
Content-Type: text/plain; charset=UTF-8
Host: 0000000000000000000000007a940000rtasquery.ibroadlink.com
Connection: close
Expect: 100-continue

{
  "credentials": {
    "userid": "123",
    "loginsession": "456",
    "licenseid": "e9a19a0e0d099eb8288d878687b4883a"
  },
  "report": "fw_spminielec_v1",
  "device": [
    {
      "did": "0000000000000000000032aa31726240",
      "start": "2022-12-31_00:00:00",
      "end": "2023-01-31_23:59:00",
      "params": [
        "elec"
      ],
      "timefilter": {
        "timepoint": [
          "22:00:00",
          "06:00:00"
        ],
        "loffset": "29m",
        "roffset": "30m"
      }
    }
  ]
}
```

Following observations:
- the date-time format is in the timezone "Asia/Shanghai", so the e-Control App converts from/to your local timezone
- params "elec" is apparently to get the cumulative kWh counter values
- the timefilter apparently specifies which values you will get back
- fw_spminielec_v1 is a report type, as mentioned in [this broadlink App SDK](https://docs.ibroadlink.com/public/appsdk_en/appsdk_05/)

Mentioned types are:
- fw_currentstate_v1: Device attribute (default report)
- fw_energystatus_v1: History data (general electrical)
- fw_energystats_v1: Power measurements (general electrical)
- fw_spminielec_v1: SP mini power measurement
- fw_spminiswitch_v1: SP mini on/off history
- fw_s1push_v1: push notifications

I did not try these, only used fw_spminielec_v1.

### Month response

```
HTTP/1.1 100 Continue

HTTP/1.1 200 OK
Server: nginx/1.4.6 (Ubuntu)
Date: Tue, 31 Jan 2023 20:52:00 GMT
Content-Type: text/plain; charset=utf-8
Content-Length: 1257
Connection: close

{
  "status": 0,
  "msg": "ok",
  "report": "fw_spminielec_v1",
  "table": [
    {
      "did": "0000000000000000000032aa31726240",
      "total": 22,
      "cnt": 22,
      "values": [
        {
          "elec": 4299.56,
          "occurtime": "2023-01-21_22:00:00"
        },
        {
          "elec": 4291.36,
          "occurtime": "2023-01-21_06:00:00"
        },
        {
          "elec": 4320.54,
          "occurtime": "2023-01-22_22:00:00"
        },
        {
          "elec": 4299.58,
          "occurtime": "2023-01-22_06:00:00"
        },
        {
          "elec": 4320.57,
          "occurtime": "2023-01-23_22:00:00"
        },
        {
          "elec": 4320.56,
          "occurtime": "2023-01-23_06:00:00"
        },
        {
          "elec": 4320.57,
          "occurtime": "2023-01-24_22:00:00"
        },
        {
          "elec": 4320.57,
          "occurtime": "2023-01-24_06:00:00"
        },
        {
          "elec": 4320.57,
          "occurtime": "2023-01-25_22:00:00"
        },
        {
          "elec": 4320.57,
          "occurtime": "2023-01-25_06:00:00"
        },
        {
          "elec": 4320.57,
          "occurtime": "2023-01-26_22:00:00"
        },
        {
          "elec": 4320.57,
          "occurtime": "2023-01-26_06:00:00"
        },
        {
          "elec": 4320.57,
          "occurtime": "2023-01-27_22:00:00"
        },
        {
          "elec": 4320.57,
          "occurtime": "2023-01-27_06:00:00"
        },
        {
          "elec": 4320.57,
          "occurtime": "2023-01-28_22:00:00"
        },
        {
          "elec": 4320.57,
          "occurtime": "2023-01-28_06:00:00"
        },
        {
          "elec": 4320.57,
          "occurtime": "2023-01-29_22:00:00"
        },
        {
          "elec": 4320.57,
          "occurtime": "2023-01-29_06:00:00"
        },
        {
          "elec": 4349.81,
          "occurtime": "2023-01-30_22:00:00"
        },
        {
          "elec": 4331.41,
          "occurtime": "2023-01-30_06:00:00"
        },
        {
          "elec": 4349.81,
          "occurtime": "2023-01-31_22:00:00"
        },
        {
          "elec": 4349.81,
          "occurtime": "2023-01-31_06:00:00"
        }
      ]
    }
  ]
}
```

Following observations:
- "elec" is the cumulative kWh since the beginning of configuring/using the device
- the "occurtime" is in the timezone "Asia/Shanghai", so the e-Control App converts from/to your local timezone
- the timefilter apparently steers to give back only at 6:00 and 22:00 Asia/SHanghai time

## 24 hour request/response

### 24 hour request

```
POST /dataservice/v2/device/status HTTP/1.1
Content-Length: 320
Content-Type: text/plain; charset=UTF-8
Host: 0000000000000000000000007a940000rtasquery.ibroadlink.com
Connection: close
Expect: 100-continue

{
  "credentials": {
    "userid": "123",
    "loginsession": "456",
    "licenseid": "e9a19a0e0d099eb8288d878687b4883a"
  },
  "report": "fw_spminielec_v1",
  "device": [
    {
      "did": "0000000000000000000032aa31726240",
      "start": "2023-01-31_05:09:58",
      "end": "2023-02-01_05:09:58",
      "params": [
        "power"
      ],
      "timefilter": {}
    }
  ]
}
```

Following observations:
- the params "power" is given, which is different than the "elec" from the month view
- an empty timefilter is given

### 24 hour response

```
HTTP/1.1 100 Continue

HTTP/1.1 200 OK
Server: nginx/1.4.6 (Ubuntu)
Date: Tue, 31 Jan 2023 20:57:04 GMT
Content-Type: text/plain; charset=utf-8
Connection: close
Content-Length: 13366

{
  "status": 0,
  "msg": "ok",
  "report": "fw_spminielec_v1",
  "table": [
    {
      "did": "0000000000000000000034ea34796940",
      "total": 283,
      "cnt": 283,
      "values": [
        {
          "occurtime": "2023-01-31_05:10:00",
          "power": 0
        },
        {
          "occurtime": "2023-01-31_05:15:00",
          "power": 0
        },
        {
          "occurtime": "2023-01-31_05:20:00",
          "power": 0
        },
        {
          "occurtime": "2023-01-31_05:25:00",
          "power": 0
        },
        {
          "occurtime": "2023-01-31_05:30:00",
          "power": 0
        },
        .....
        }
      ]
    }
  ]
}
```

Following observations:
- Apparently the "power" without timefilter gives back the power (kW) per 5 minutes
- This power view is less interesting for my purpose

## Playing around with the server API

- it appeared that "did" was the MAC adres, zero padded, lower case and with ":" stripped: "0000000000000000000032aa31726240"
- the credentials did contain a userid, loginsession and licenseid, so I thought I needed to login to get the first 2, but after playing around, it turned out that only licenseid was mandatory, the userid and loginsession can be left out, the server did not check these. Probably because the specific Host does not have access to this information and is only for giving back fast history information.
- apparently the licenceid and MAC address decoded "did" is all you need!
- when "elec" and empty timefilter is given as parameter, you get back the cumulative kWh value per hour, perfect
- I do not know if the host 0000000000000000000000007a940000rtasquery.ibroadlink.com is different for other countries or other devices, but apparently the server stores the cumulative values for my SP3S-EU devices (Europe)
- If another server is needed, you have to sniff yourself ;-)
- No problem to ask for a month of data without timefilter for every hour
- The e-Control App restricts you in asking the month values for only the current year, but I could go back for the information from the beginning till now, so all data is kept on the broadlink server since the beginning!