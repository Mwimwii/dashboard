from app_logging import *
from scapy.all import *
import datetime
import sqlite3
import pickle
import requests
from app_smtp import *

# GLOBAL VARIABLES
APROX_TIME_DELTA = 0.000012
TIMEOUT = 0.2
NON_RESPONSE_DELAY_MINUTES = 3
EMAIL_TIME_DELAY = 60*2

def generate_html_td(site, date):
    html = f"""
                 <tr>
                <td>{site}</td>
                <td>{date:%B %d, %Y - %H:%M:%S%z}</td>
                 </tr>
            """
    return html

def generate_html_email(html):
    with open('email_start.html', 'r') as f:
        email_template_start = f.read()
    with open('email_end.html', 'r') as f:
        email_template_end = f.read()
    html_template = email_template_start + html + email_template_end
    return html_template

# DATABSE OPERATIONS
def add_site(site):
    try:
        c.execute('INSERT INTO sites (name, url, port, protocol) VALUES(?,?,?,?)',  site)
    except Exception:
        print(f'Table {site} already exists')
    conn.commit()

def add_status(status):
    c.executemany(
        'INSERT INTO status (status, timestamp, url_id) VALUES(?,?,?)', status)
    conn.commit()

def get_sites():
    rows = c.execute('SELECT * FROM sites')
    conn.commit()
    return list(dict(url=x[2], url_id=x[0], port=x[3], protocol=x[4]) for x in rows)

def get_status():
    for row in c.execute('SELECT * FROM status'):
        print(row)
    conn.commit()

def gen_sites():
    add_site(("E-Payslip","www.epayslip.grz.gov.zm", "443", "https"))
    add_site(("RTSA","www.rtsa.org.zm", "443", "https"))
    add_site(("Smart Zambia","www.szi.gov.zm", "443", "https"))

# DATETIME OPERATIONS
def get_timestamp():
    timestamp = datetime.datetime.utcnow()
    return timestamp

def get_datetime(minutes):
    datetime_utc_now = datetime.timedelta(APROX_TIME_DELTA*minutes*60)
    return datetime_utc_now

def utc_to_local(dt):
    local_datetime_converted = dt + (datetime.datetime.now() - datetime.datetime.utcnow())
    return local_datetime_converted

def local_to_utc(dt):
    UTC_datetime_converted = dt - (datetime.datetime.now() - datetime.datetime.utcnow())
    return UTC_datetime_converted

# FILE OPERATIONS
def load_down_sites():
    with open("down_sites.txt", "rb") as f_pickle:
        data = pickle.load(f_pickle)
    return data

def save_down_sites(data):
    with open("down_sites.txt", "wb") as f_pickle:
        pickle.dump(data, f_pickle)

def test_ds():
    global down_sites
    save_down_sites({"Hello": "World"})
    down_sites = load_down_sites()
    print(down_sites)
    save_down_sites({"New": "World"})
    down_sites = load_down_sites()
    print(down_sites)

try:
    down_sites = load_down_sites()
except:
    save_down_sites({})

down_sites = load_down_sites()
log = Logger()


# TCP/IP OPERATIONS    

def test_site_icmp(site):
    # Send a packet to the webpage for a response
    try:
        icmp = IP(dst=site)/ICMP()
    except Exception:
        icmp = None
    response = sr1(icmp, timeout=TIMEOUT)
    return response

def test_site_http(site, port, protocol):
    # Need to change the request.get 'https' to only
    # retrieve the site. Avoid hardcoding text into 
    # the system.
    try:
        response = requests.get(f"{protocol}://{site}:{port}", verify=False,timeout=1).status_code
    except Exception:
        response = None 
    return response

# UTILITY FUNCTIONS
def sum_of(l):
    return sum([True for x in l if x])

def test_site(site, url_id, port, protocol, loop=5):
    """
    Pings the site url or ip of choice with
    the option to loop or infinitely check whether 
    the site is on or off
    """
    global down_sites
    try_icmp = []
    try_http = []
    timestamp = get_timestamp()

    # Try accessing the sites five times on both
    # icmp and http and append them into
    # a boolean array
    for i in range(5):
        try_icmp.append(test_site_icmp(site))
        try_http.append(test_site_http(site,port,protocol))

    # If the sum of either array is greater that 0
    # this yields a truth value. 
    # Anything greater than 0 is the equivalent to True.
    response = None
    if sum_of(try_icmp) or sum_of(try_http):
        response = "ON, 200"
    
    target_site_port = f"{site}:{port}"
    if response is None:
        down_site_timestamp = down_sites.get(target_site_port, 0)
        # If the site has been down for the first time
        if down_site_timestamp == 0:
            down_sites[target_site_port] = timestamp
            status = ("NR", timestamp, url_id)
            log.logger("NR", status)
        # If the site has been unresponsive for less than 10 minutes
        elif get_datetime(NON_RESPONSE_DELAY_MINUTES) > (datetime.datetime.utcnow() - down_site_timestamp):
            status = ("NR", timestamp, url_id)
            log.logger("NR", status)
        # If the site has been unresponsive for more than 10 minutes
        elif get_datetime(NON_RESPONSE_DELAY_MINUTES) < (datetime.datetime.utcnow() - down_site_timestamp):
            status = ("OFF", timestamp, url_id)
            log.logger("OFF", status)
    else:
        status = ("ON", timestamp, url_id)
        log.logger("ON", status)
        if down_sites.get(target_site_port, 0) :
            down_sites.pop(target_site_port)
    

if __name__ == "__main__":
    conn = sqlite3.connect('app.sqlite')
    c = conn.cursor()
    # gen_sites()    
    sites = get_sites()
    for site in sites:
        test_site(*site.values())
    site_status = log.get_logs(clear=True)
    add_status(site_status)

    # EMAIL LOGIC
    temp_ds = down_sites
    html_td = ""
    to_send = False
    for site, timestamp in temp_ds.items():
        if get_datetime(10) > (datetime.datetime.utcnow() - timestamp):
            # print(f"less than 1 min {(datetime.datetime.utcnow() - timestamp)}")
            to_send = True
        elif get_datetime(EMAIL_TIME_DELAY) < (datetime.datetime.utcnow() - timestamp):
            # print(f"Greater than 10 mins {(datetime.datetime.utcnow() - timestamp)}")
            down_sites[site] = datetime.datetime.utcnow()
            to_send = True
        html_td += generate_html_td(site, utc_to_local(timestamp))
    html = generate_html_email(html_td)
    save_down_sites(down_sites)
    conn.close()

    if to_send == True:
        admins = [
            'lubunda.musonda@szi.gov.zm',
                    'lawrence.kasonde@szi.gov.zm',
                    'morton.nyemba@szi.gov.zm',
                    'haambayi.mudenda@szi.gov.zm',
                    'mwila.nyirongo@szi.gov.zm',
                    'daniel.chirwa@szi.gov.zm'
        ]

        # for admin in admins:
        #     send_email(f'{admin}',
        #             'Your website is down',
        #             html)