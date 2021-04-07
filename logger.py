from time import gmtime, strftime
import os

LOG_DIR = "/nw/meraki/automation-scripts/update_meraki_rules/logs/"
DATE_FORMAT = "[%a, %d/%b/%Y %H:%M:%S +0000]"
NAME_FORMAT = "%Y%m%d.log"


def send_wr_log(log_message):
    # write to a log file
    log_date = strftime(DATE_FORMAT, gmtime())
    log_line = "{} - {}".format(log_date, log_message)
    log_filename = "{}{}".format(LOG_DIR, strftime(NAME_FORMAT, gmtime()))
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    with open(log_filename, "a") as f:
        f.write("\n" + log_line)
