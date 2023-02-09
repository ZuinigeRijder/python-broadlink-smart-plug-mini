# == smart_plug_mini.py Author: Zuinige Rijder ==============================
"""
Simple Python3 script to get history kWh consumption of broadlink Smart Plug Mini
using the broadlink server and append later kWh measurements to a
.csv file format per device.

Also write the days, weeks, months and years summaries to separate csv files.

I have 2 times model Smart plug SP3S-EU and tested with those.
Probably this also works for other broadlink SP mini models.

Do not forget to configure smart_plug_mini.cfg
"""

import configparser
from dataclasses import dataclass, field
from datetime import datetime
from io import TextIOWrapper
from zoneinfo import ZoneInfo
import json
import os
from pathlib import Path
import socket
import sys
import time
import traceback
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from dateutil.relativedelta import relativedelta


def arg_has(string: str) -> bool:
    """arguments has string"""
    for i in range(1, len(sys.argv)):
        if sys.argv[i].lower() == string:
            return True
    return False


D = arg_has("debug")


def dbg(line: str) -> bool:
    """print line if debugging"""
    if D:
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: {line}')
    return D  # just to make a lazy evaluation expression possible


@dataclass
class FileInfo:
    """helper dataclass to store file information"""

    postfix: str
    path: Path = field(init=False)
    file: TextIOWrapper = field(init=False)
    header: str = field(default="Date, Cumulative kWh, Delta +kWh")
    opened: bool = field(default=False)


CSV_GLOBAL = FileInfo(
    postfix="",
    header="Date, Cumulative kWh, Delta +kWh, Days +kWh, Weeks +kWh, Months +kWh, Years +kWh",  # noqa
)
CSV_DAYS = FileInfo(postfix=".days")
CSV_WEEKS = FileInfo(postfix=".weeks")
CSV_MONTHS = FileInfo(postfix=".months")
CSV_YEARS = FileInfo(postfix=".years")

FILES = [CSV_GLOBAL, CSV_DAYS, CSV_WEEKS, CSV_MONTHS, CSV_YEARS]


LICENSE_ID = "e9a19a0e0d099eb8288d878687b4883a"

parser = configparser.ConfigParser()
parser.read("smart_plug_mini.cfg")
sp3s_settings = dict(parser.items("smart_plug_mini"))


LOCAL_TIMEZONE = sp3s_settings["local_timezone"].strip()
SERVER = sp3s_settings["server"].strip()
DEVICE_NAMES = sp3s_settings["device_names"].strip()
DEVICE_MACS = sp3s_settings["device_macs"].strip()
REPORT_TYPES = sp3s_settings["report_types"].strip()
START_DATES = sp3s_settings["start_dates"].strip()
TIME_FILTER = sp3s_settings["time_filter"].strip()

ZONE_INFO_SERVER = ZoneInfo("Asia/Shanghai")
ZONE_INFO_LOCAL = ZoneInfo(LOCAL_TIMEZONE)

_ = D and dbg(
    f"SERVER: {SERVER}\nDEVICE_NAMES: [{DEVICE_NAMES}]\nDEVICE_MACS: [{DEVICE_MACS}]\nREPORT_TYPES: [{REPORT_TYPES}]\nSTART_DATES: {START_DATES}\nTIME_FILTER: {TIME_FILTER}"  # noqa
)

# these will be filled in a loop per device
DEVICE_NAME = ""
DEVICE_TYPE = ""
DEVICE_ID = ""
DATE_START = ""


def log(msg: str) -> None:
    """log a message prefixed with a date/time format yyyymmdd hh:mm:ss"""
    print(datetime.now().strftime("%Y%m%d %H:%M:%S") + ": " + msg)


def same_year(d_1: datetime, d_2: datetime) -> bool:
    """return if same year"""
    return d_1.year == d_2.year


def same_month(d_1: datetime, d_2: datetime) -> bool:
    """return if same month"""
    if d_1.month != d_2.month:
        return False
    return d_1.year == d_2.year


def same_week(d_1: datetime, d_2: datetime) -> bool:
    """return if same week"""
    if d_1.isocalendar().week != d_2.isocalendar().week:
        return False
    return d_1.year == d_2.year


def same_day(d_1: datetime, d_2: datetime) -> bool:
    """return if same day"""
    if d_1.day != d_2.day:
        return False
    if d_1.month != d_2.month:
        return False
    return d_1.year == d_2.year


# == post ====================================================================
def execute_request(url, data, headers) -> str:
    """execute request and handle errors"""
    if D:
        print(f"execute_request url={url}")
        print(f"execute_request post_data={data}")
        print(f"execute_request headers={headers}")
        print()

    retries = 2
    while retries > 0:
        retries -= 1
        request = Request(url, data=data, headers=headers)

        errorstring = ""
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read()
                content = body.decode("utf-8")
                _ = D and dbg(f"execute_request content: {content}\n")
                return content
        except HTTPError as error:
            errorstring = str(error.status) + ": " + error.reason
        except URLError as error:
            errorstring = str(error.reason)
        except TimeoutError:
            errorstring = "Request timed out"
        except socket.timeout:
            errorstring = "Socket timed out"
        except Exception as ex:  # pylint: disable=broad-except
            errorstring = "urlopen exception: " + str(ex)
            traceback.print_exc()

        log("ERROR: " + url + " -> " + errorstring)
        time.sleep(60)  # retry after 1 minute
    return "ERROR"


def get_last_line(filename: Path) -> str:
    """get last line of filename"""
    last_line = ""
    if filename.is_file():
        with open(filename.name, "rb") as file:
            try:
                file.seek(-2, os.SEEK_END)
                while file.read(1) != b"\n":
                    file.seek(-2, os.SEEK_CUR)
            except OSError:
                file.seek(0)
            last_line = file.readline().decode().strip()
    print(f"last line {filename.name}: {last_line}")
    return last_line


def close_files() -> None:
    """close files"""
    for fileinfo in FILES:
        if fileinfo.opened:
            print(f"Closing {fileinfo.path.name}")
            fileinfo.file.close()
            fileinfo.opened = False


def write_line(fileinfo: FileInfo, line: str) -> None:
    """write line"""
    if not fileinfo.opened:
        write_header = False
        fileinfo.path = Path(f"{DEVICE_NAME}{fileinfo.postfix}.csv")
        if not fileinfo.path.is_file():
            fileinfo.path.touch()
            write_header = True
        print(f"Opening {fileinfo.path.name}")
        fileinfo.file = fileinfo.path.open("a", encoding="utf-8")
        fileinfo.opened = True
        if write_header:
            print(fileinfo.header)
            fileinfo.file.write(fileinfo.header)
            fileinfo.file.write("\n")

    print(f"{fileinfo.path.name}: {line}")
    fileinfo.file.write(line)
    fileinfo.file.write("\n")


def get_kwh_counters(date_start_str: str, date_end_str: str) -> dict:
    """get_kwh_counters"""
    post = f"{SERVER}/dataservice/v2/device/stats"
    headers = {
        "Content-Type": "text/plain; charset=UTF-8",
        "Connection": "close",
        "Expect": "100-continue",
    }
    post_data = f'{{"credentials":{{"licenseid":"{LICENSE_ID}"}},"report":"{DEVICE_TYPE}","device":[{{"did":"{DEVICE_ID}","start":"{date_start_str}","end":"{date_end_str}","params":["elec"],{TIME_FILTER}}}]}}'  # noqa
    content = execute_request(post, post_data.encode("utf-8"), headers)
    if content == "ERROR":
        log(f"month_stats error: {post_data}")
        return {}

    result = json.loads(content)
    if result["msg"] != "ok":
        log(f"get_kwh_counters error: {result}")
        return {}

    table = result["table"]
    _ = D and dbg(f"get_kwh_counters table = {table}")
    if len(table) == 0:
        return {}

    values = table[0]["values"]
    _ = D and dbg(f"get_kwh_counters values = {values}")
    return values


def get_last_info_from_csv(
    csv_filename: Path,
) -> tuple[datetime, float, float, float, float, float]:
    """get_last_info_from_csv"""
    date_start_server = datetime.strptime(DATE_START, "%Y-%m-%d %H:%M")
    date_start_server = date_start_server.replace(tzinfo=ZONE_INFO_LOCAL).astimezone(
        ZONE_INFO_SERVER
    )
    last_kwh = 0.0
    last_d = 0.0
    last_w = 0.0
    last_m = 0.0
    last_y = 0.0

    log(f"##### {csv_filename} ######################################")
    last_line = get_last_line(csv_filename)
    if last_line != "":
        splitted = last_line.split(",")
        last_date_str = splitted[0].strip()
        if last_date_str.startswith("20") and len(splitted) == 7:
            last_kwh = float(splitted[1].strip())
            last_d = float(splitted[3].strip())
            last_w = float(splitted[4].strip())
            last_m = float(splitted[5].strip())
            last_y = float(splitted[6].strip())
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d %H:%M")
            last_date_server = last_date.replace(tzinfo=ZONE_INFO_LOCAL).astimezone(
                ZONE_INFO_SERVER
            )
            if last_date_server > date_start_server:
                date_start_server = last_date_server
                log(f"                  {last_date_str}")

    return date_start_server, last_kwh, last_d, last_w, last_m, last_y


def compute(
    fixed: tuple[float, float, datetime],  # delta_kwh, prev_kwh, prev_date
    cum_x: float,
    no_change: bool,
    fileinfo: FileInfo,
) -> float:
    """compute"""
    delta_kwh = fixed[0]
    new_delta_x = 0.0
    if no_change:
        new_delta_x = cum_x + delta_kwh
        _ = D and dbg(
            f"delta_kwh: {delta_kwh:.2f} delta_x: {cum_x:.2f} new_delta_x: {new_delta_x:.2f}"  # noqa
        )
    else:
        new_delta_x = delta_kwh
        _ = D and dbg(
            f"Change: delta_kwh: {delta_kwh:.2f} delta_x: {cum_x:.2f} new_delta_x: {new_delta_x:.2f}"  # noqa
        )
        # append the previous day/week/month/year value to the summary csv file
        prev_kwh = fixed[1]
        prev_date = fixed[2]
        line = f"{local_dt_str(prev_date)}, {prev_kwh:.2f}, {cum_x:.2f}"
        write_line(fileinfo, line)

    return new_delta_x


def local_dt_str(date: datetime) -> str:
    """local_dt_str"""
    date_str = date.astimezone(ZONE_INFO_LOCAL).strftime("%Y-%m-%d %H:%M")
    return date_str


def do_kwh_counters() -> None:
    """do_kwh_counters"""
    now_server = (
        datetime.now(tz=ZONE_INFO_LOCAL)
        .replace(second=0, microsecond=0)
        .astimezone(ZONE_INFO_SERVER)
    )
    (
        date_start_server,
        prev_kwh,
        cum_d,
        cum_w,
        cum_m,
        cum_y,
    ) = get_last_info_from_csv(Path(f"{DEVICE_NAME}.csv"))
    prev_date = date_start_server.astimezone(ZONE_INFO_LOCAL)
    date_start_server += relativedelta(hours=1)  # start with next hour
    log(f"date_start local: {date_start_server.astimezone(ZONE_INFO_LOCAL)}")
    log(f"now local       : {now_server.astimezone(ZONE_INFO_LOCAL)}")
    while date_start_server < now_server:
        date_end_server = date_start_server + relativedelta(months=1)
        log(
            f"{DEVICE_NAME}: from {date_start_server.astimezone(ZONE_INFO_LOCAL)} to {date_end_server.astimezone(ZONE_INFO_LOCAL)}"  # noqa
        )
        result = get_kwh_counters(
            date_start_server.strftime("%Y-%m-%d_%H:%M:%S"),
            date_end_server.strftime("%Y-%m-%d_%H:%M:%S"),
        )
        date_start_server = date_end_server
        date_start_server += relativedelta(hours=1)  # start with next hour
        if result is None:
            log("no results")
            continue

        for entry in result:
            _ = D and dbg(f"month_stats entry = {entry}")
            kwh = entry["elec"]
            occurtime = entry["occurtime"]
            # convert the occurtime to local timezone time
            date = (
                datetime.strptime(occurtime, "%Y-%m-%d_%H:%M:%S")
                .replace(tzinfo=ZoneInfo("Asia/Shanghai"))  # add timezone info
                .astimezone()  # to local timezone
            )
            delta_kwh = kwh - prev_kwh
            _ = D and dbg(
                f"kwh: {kwh:.2f}, prev: {prev_kwh:.2f}, delta: {delta_kwh:.2f}"
            )
            if delta_kwh < 0.0:  # damned, previous entry should be corrected?
                log(
                    f"WARNING: delta_elec < 0: current: {date} {kwh} prev: {prev_date} {prev_kwh}"  # noqa
                )

            _ = D and dbg(
                f"prev_date: {local_dt_str(prev_date)}\ncurr_date: {local_dt_str(date)}"  # noqa
            )

            fixed = (delta_kwh, prev_kwh, prev_date)
            cum_d = compute(fixed, cum_d, same_day(prev_date, date), CSV_DAYS)
            cum_w = compute(fixed, cum_w, same_week(prev_date, date), CSV_WEEKS)
            cum_m = compute(fixed, cum_m, same_month(prev_date, date), CSV_MONTHS)
            cum_y = compute(fixed, cum_y, same_year(prev_date, date), CSV_YEARS)

            line = f"{local_dt_str(date)}, {kwh:.2f}, {delta_kwh:.2f},  {cum_d:.2f},  {cum_w:.2f},  {cum_m:.2f},  {cum_y:.2f}"  # noqa
            write_line(CSV_GLOBAL, line)

            prev_kwh = kwh
            prev_date = date

    close_files()


def main() -> None:
    """main"""
    global DEVICE_NAME, DEVICE_TYPE, DEVICE_ID, DATE_START  # noqa pylint: disable=global-statement
    for index, mac in enumerate(DEVICE_MACS.split(",")):
        DEVICE_NAME = DEVICE_NAMES.split(",")[index].strip()
        DEVICE_TYPE = REPORT_TYPES.split(",")[index].strip()
        DEVICE_ID = mac.strip().replace(":", "").lower().rjust(32, "0")
        DATE_START = START_DATES.split(",")[index].strip()
        _ = D and dbg(
            f"main(): DEVICE_NAME: {DEVICE_NAME}, DEVICE_TYPE: {DEVICE_TYPE}, DEVICE_ID: {DEVICE_ID}, DATE_START: {DATE_START}"  # noqa
        )
        do_kwh_counters()


main()
