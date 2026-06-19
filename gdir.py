from concurrent.futures import ThreadPoolExecutor
import requests
import sys
import os
import random
import argparse
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from threading import Lock

start = time.perf_counter()
# color
RED = "\033[0;31m"
GREEN = "\033[0;32m"
DARK_GRAY = "\033[1;30m"
CYAN = "\033[1;36m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
END = "\033[0m"

#user-agent
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 4.1; en-US; Nexus 7 Build/JRN84D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    "Opera/9.80 (SpreadTrum; Opera Mini/4.4.31227/75.35; U; en) Presto/2.12.423 Version/12.16",
    "Mozilla/5.0 (X11; Linux i686) KHTML/4.14.6 (like Gecko) Konqueror/4.14",
    "iTunes/10.6 (Macintosh; Intel Mac OS X 10.8) AppleWebKit/531.21.8",
    "Mozilla/5.0 (Linux; U; X11; en-US; Valve Steam Tenfoot/1535576546; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0",
    "Mozilla/5.0 (Linux; Android 4.4.2; SPH-L710 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36",
    "Opera/9.63 (X11; FreeBSD 7.1-RELEASE i386; U; en) Presto/2.1.1",
    "Mozilla/5.0 (X11; U; Linux x86_64; en-us) AppleWebKit/534.35 (KHTML, like Gecko) Chrome/11.0.696.65 Safari/534.35 Puffin/2.9331AT",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0.1; Z833 Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.91 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.183 Safari/537.36 Vivaldi/1.96.1147.64",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15058",
    "Mozilla/5.0 (PlayStation Vita 3.50) AppleWebKit/537.73 (KHTML, like Gecko) Silk/3.2",
    "yacybot (/global; arm Linux 3.8.13.30; java 1.8.0_91; Europe/de) http://yacy.net/bot.html",
    "UCWEB/2.0 (Symbian; U; S60 V3; en-US; NOKIAE5-00) U2/1.0.0 UCBrowser/9.0.1.317 U2/1.0.0 Mobile",
    "UCWEB/2.0 (Java; U; MIDP-2.0; Nokia203/20.37) U2/1.0.0 UCBrowser/8.7.0.218 U2/1.0.0 Mobile",
    "SM-B311V/1.0 UP.Browser/6.2.3.8 (GUI) MMP/2.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13F69"
]


session = requests.Session()
count = 0
time_out = 0
connection_error = 0
delay = 0
lock_loop = Lock()

parse = argparse.ArgumentParser(
    prog='GhostDir',
    description='Directory & File Discovery Tool',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parse.add_argument('-u','--url',metavar="URL",required=True,help="This flag takes the target value",type=str)
parse.add_argument('-w','--wordlist',metavar="WORDLIST",required=True,type=str,help="This flag takes on the value of the brute force list")
parse.add_argument('-T',metavar="TIMEOUT",required=False,default=10,type=int,help="This flag takes a numerical value to determine the delay time")
parse.add_argument('-X', metavar="METHOD", required=False, default='GET', type=str, help="HTTP method to use (GET, POST, HEAD, OPTIONS, PUT, DELETE, PATCH)")
parse.add_argument('-t','--threads',metavar='THREADS',required=False,type=int,default=10,help="This flag takes into account the speed at which orders are sent")
parse.add_argument('-fc',metavar="FILTER CODE",required=False,default=None,type=lambda x : [int(i) for i in x.split(',')],help="This flag takes value by taking unwanted responses")
parse.add_argument('-fs',metavar="FILTER SIZE",required=False,default=None,type=lambda x: [int(i) for i in x.split(',')],help="This flag takes a value that represents the size of the pages that are not desired to be displayed")
parse.add_argument('-H',metavar="HEADERS",required=False,type=str,help="This flag takes the cost of adding a header upon request")
parse.add_argument('--cookies',required=False,default=None,type=str,metavar="COOKIE_STRING",help="Send custom cookies with requests (e.g. session=abc123; user=admin)")
parse.add_argument('-A','--agent',required=False,type=str,default=None,metavar="User Agent",help="Specify a custom User-Agent string for HTTP requests")
parse.add_argument('--random-agent',required=False,action="store_true",help="Enable random User-Agent rotation for each request")
parse.add_argument('-o',default=None,metavar="OUTPUT",required=False,type=str,help="Save discovered results to a file (e.g. results.txt)")
parse.add_argument('-e',metavar="EXTENSIONS",required=False,default=None,type=lambda x: [i.strip().lower() for i in x.split(',')],help="Filter by file extensions (e.g. php,html,asp)")
parse.add_argument('-ms',metavar="Match String",required=False,default=None,type=str,help="String used for matching or filtering results")
parse.add_argument('--proxy',metavar="PROXY", default=None,required=False,type=str,help='Route requests through a proxy (e.g. Burp Suite)')
parse.add_argument('--mode', metavar="MODE",default="burp",required=False,type=str,choices=['burp','fast'],help='Request rate mode: burp (3 requests/sec) or fast (10 requests/sec)')
arg = parse.parse_args()

# Variable
url = arg.url
wordlist = arg.wordlist
timeout = arg.T
threads = arg.threads
filter_code = arg.fc
filter_size = arg.fs
proxy = arg.proxy
mode = arg.mode
method = arg.X.upper()
header = arg.H
user_agent = arg.agent
random_agent = arg.random_agent
cookie = arg.cookies
headers = {}
output = arg.o
ms = arg.ms.lower() if arg.ms else None
ext = arg.e
file_output = []

# check target
def check_url():
    global url
    global session
    if not url.startswith(('http://','https://')):
        print(f"{RED}[-] Invalid URL: '{url}'\n[!] URL must start with http:// or https:// {END}")
        sys.exit()
    if url.endswith('/'):
        url = url[:-1]
    return url
check_url()



# check file
def check_word_list():
    global wordlist
    if not os.path.isfile(wordlist):
        print(f"{RED}[-] Wordlist file not found: {wordlist}{END}")
        sys.exit()
check_word_list()

# check method
def check_method(x):
    ALLOWED_METHODS = ['GET', 'POST', 'HEAD', 'OPTIONS', 'PUT', 'DELETE', 'PATCH']
    if method not in ALLOWED_METHODS:
        print(f"{RED}[-] Invalid method: '{method}'\n[!] Allowed: {', '.join(ALLOWED_METHODS)}{END}")
        sys.exit()
check_method(method)

# check headers
def check_header(header_user,stor_header):

    if user_agent:
        headers['User-Agent'] = user_agent
    elif random_agent:
        headers['User-Agent'] = random.choice(USER_AGENTS)
    
    if cookie:
        headers['Cookie'] = cookie

    if header_user:
        for h in header_user.split(','):
            if ':' not in h:
                continue
            key,value = h.split(':',1)
            stor_header[key.strip()] = value.strip()
check_header(header,headers)


# burp
proxies = None
def check_proxy(proxy):
    global proxies
    if proxy is not None:
        proxies = {
            "http" : proxy,
            "https" : proxy
        }
check_proxy(proxy)

# page size
def format_size(size):
    if size < 1024:
        return f"{DARK_GRAY}{size} B{END}"
    elif size < 1024 ** 2:
        return f"{GREEN}{size / 1024:.2f} KB{END}"
    elif size < 1024 ** 3:
        return f"{YELLOW}{size / (1024 ** 2):.2f} MB{END}"
    else:
        return f"{RED}{size / (1024 ** 3):.2f} GB{END}"

# check mode 
if proxy and mode == 'burp':
    threads = 3
    timeout = max(timeout, 10)
    delay = 0.1

def request(url, word):
    global session
    global count
    global connection_error
    global time_out
    is_filtered = False
    status_code = [200, 201, 204, 301, 302, 307, 403, 405, 500]

    full_path = f"{url}/{word.strip()}"

    if delay:
        time.sleep(delay)
    
    try:
        response = session.request(
            method=method,
            url=full_path,
            headers=headers,
            timeout=timeout,
            allow_redirects=True,
            proxies=proxies,
            verify=False
        )
        #count 
        with lock_loop:
            count += 1
    
        text = response.text.lower() if response.text else ""
        # Match String filter
        if ms and ms not in text:
            is_filtered = True

        if filter_size is not None and len(response.content) in filter_size:
            is_filtered = True


        if filter_code is not None and response.status_code in filter_code:
            is_filtered = True


        if not is_filtered and response.status_code in status_code and len(response.content) > 0:
            with lock_loop:
                file_output.append(
                        f"[URL] {full_path}  "
                        f"[STATUS] {response.status_code}  "
                        f"[SIZE] {len(response.content)} bytes\n"
                    )

            with lock_loop:
                print(f"\r{' ' * 100}\r{GREEN}[+] {word.strip()} [Status: {BLUE}{response.status_code}{END}] [Size: {BLUE}{format_size(len(response.content))}{END}]{END}")
        else:
            with lock_loop:
                print(
                    f'{YELLOW}\r[*] Requests sent: {count} '
                    f'|| '
                    f'Method({method}) '
                    f'|| '
                    f'ReadTimeout({time_out}) '
                    f'|| '
                    f'ConnectionError({connection_error}){END}',
                    end='',
                    flush=True
                )

    except requests.exceptions.ConnectionError:
        with lock_loop:
            connection_error += 1

    except requests.exceptions.ReadTimeout:
        with lock_loop:
            time_out += 1
    


def banner():
    optional = ""
    if headers:
        optional += f"\n{CYAN}[HEADERS]{END}     :  {', '.join(f'{k}: {v}' for k, v in headers.items())}"
    if filter_code:
        optional += f"\n{CYAN}[FILTER CODE]{END} :  {','.join(f"{fc}" for fc in filter_code)}"
    if filter_size:
        optional += f"\n{CYAN}[FILTER SIZE]{END} :  {','.join(f"{fs}" for fs in filter_size)}"
    if mode:
        optional += f"\n{CYAN}[MODE]{END}        :  {mode}"
    if proxy:
        optional += f"\n{CYAN}[PROXY]{END}       :  {proxy}"
    if output:
        optional += f"\n{CYAN}[OUTPUT]{END}      :  {output}"
    if ms:
        optional += f"\n{CYAN}[MATCH STR]{END}   :  {ms}"
    if ext:
        optional += f"\n{CYAN}[EXTENSIONS]{END}  :  {','.join(ext)}"
    if cookie:
        optional += f"\n{CYAN}[COOKIE]{END}      :  {cookie}"

    print(rf"""{CYAN}

 ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗██████╗ ██╗██████╗
██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝██╔══██╗██║██╔══██╗
██║  ███╗███████║██║   ██║███████╗   ██║   ██║  ██║██║██████╔╝
██║   ██║██╔══██║██║   ██║╚════██║   ██║   ██║  ██║██║██╔══██╗
╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   ██████╔╝██║██║  ██║
 ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═════╝ ╚═╝╚═╝  ╚═╝

{CYAN}            By: Ali Waled{END}
{GREEN}            GhostDir v1.0{END}
{YELLOW}      Directory & File Discovery Tool{END}

{CYAN}══════════════════════════════════════════════════════════════════════════════════{END}
{CYAN}[TARGET]{END}      :  {url}
{CYAN}[WORDLIST]{END}    :  {wordlist}
{CYAN}[METHOD]{END}      :  {method}
{CYAN}[TIMEOUT]{END}     :  {timeout}s
{CYAN}[THREADS]{END}     :  {threads}{optional}
{CYAN}══════════════════════════════════════════════════════════════════════════════════{END}
""")
banner()



# checking target
def check_target(url):
    global session
    print(f"{CYAN}[+] Checking target: {url}{END}")

    try:
        response = session.get(
            url,
            timeout=10,
            allow_redirects=True,
            verify=False
        )

        print(
            f"{CYAN}[+] Target is alive "
            f"[Status: {response.status_code}]{END}"
        )

        return True
    
    except requests.exceptions.ConnectionError:
        print(f"{RED}[-] Connection error: target appears unreachable{END}")
        sys.exit()

    except requests.exceptions.Timeout:
        print(f"{RED}[-] Request timed out{END}")
        sys.exit()

    except requests.exceptions.RequestException as e:
        print(f"{RED}[-] Error: {e}{END}")
        sys.exit()
check_target(url)



with open(wordlist, 'r', encoding='latin-1') as words:
    word_list = [w.strip() for w in words if w.strip()]

all_paths = []
for word in word_list:
    if ext is not None:
        for e in ext:
            all_paths.append(f"{word}.{e}")
    else:
        all_paths.append(word)

with ThreadPoolExecutor(max_workers=threads) as ex:
    for path in all_paths:
        ex.submit(request, url, path)


end = time.perf_counter()
elapsed = end - start
print(f"\n{CYAN}[*] Scan completed in {elapsed:.2f}s{END}")
print(f"{CYAN}[*] Total requests: {count} | Found: {len(file_output)}{END}")




# result loop
if output:
    with open(output, 'a', encoding='utf-8') as save:
        for line in file_output:
            save.write(line)