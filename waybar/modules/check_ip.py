#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Author: Gantimurov Alexander
Date: 2023-05-22 16:02

```json
{
  "ip": "8.8.8.8",
  "network": "8.8.8.0/24",
  "version": "IPv4",
  "city": "Mountain View",
  "region": "California",
  "region_code": "CA",
  "country": "US",
  "country_name": "United States",
  "country_code": "US",
  "country_code_iso3": "USA",
  "country_capital": "Washington",
  "country_tld": ".us",
  "continent_code": "NA",
  "in_eu": false,
  "postal": "94043",
  "latitude": 37.42301,
  "longitude": -122.083352,
  "timezone": "America/Los_Angeles",
  "utc_offset": "-0700",
  "country_calling_code": "+1",
  "currency": "USD",
  "currency_name": "Dollar",
  "languages": "en-US,es-US,haw,fr",
  "country_area": 9629091,
  "country_population": 327167434,
  "asn": "AS15169",
  "org": "GOOGLE"
}
```

Sample waybar config (script must be in PATH)

```json
"custom/ipcheck": {
    "tooltip": true,
    "interval": 60,
    "format": "{}",
    "exec": "check_ip.py",
    "return-type": "json",
    "signal": 15,
    "on-click": "pkill -RTMIN+15 waybar",
}
```

You can update module by click on them in bar or sending RTMIN signal

```sh
pkill -RTMIN+15 waybar
```

Sample style.css config (some variables already defined in theme)


```css
#custom-ipcheck {
    font-weight: bold;
    padding-left: 10px;
    padding-right: 10px;
    color: @theme_bg_color;
    background-color: @theme_selected_bg_color;
}

#custom-ipcheck.RU {
    color: @error_color;
    background-color: @theme_bg_color;
}
#custom-ipcheck.AS8342 {
    color: @error_color;
    background-color: @theme_bg_color;
}

#custom-ipcheck.error {
    /*# background-color: @error_color;*/
    animation-timing-function: linear;
    animation-iteration-count: infinite;
    animation-direction: alternate;
    animation-name: blink-critical;
    animation-duration: 2s;
    color: @error_color;
    background-color: @theme_bg_color;
}
```

Usage:

check_ip.py my
check_ip.py my -F"{flag}"
check_ip.py 8.8.8.8 -F"{city}"

"""

import argparse
import json
import tempfile
import os
import sys
import logging
from pathlib import Path
from typing import List
from datetime import datetime
from urllib import request
from urllib.error import HTTPError, URLError


logger = logging.getLogger("ipcheck")
CACHE = {}

CLASS_FLDS = (
    "version",
    "city",
    "region",
    "region_code",
    "country",
    "country_code",
    "country_code_iso3",
    "asn",
    "org",
)
TEXT_FMT = "{region_code}/{country_code} {flag}"
ALT_FMT = "{country_code}"
TOOLTIP_FMT = """IP: <b>{ip}</b>
Network: <b>{network}</b>

City: <b>{city}</b>
Country: <b>{country_name}</b>
Country Code: <b>{country_code}</b>
Flag: {flag}

ASN: <b>{asn}</b>
Provider: <b>{org}</b>

Last update: <i>{last_update}</i>"""


def get_cache_file(fname: str = "check_ip.tmp") -> Path:
    """Locate a platform-appropriate cache directory for flit to use

    Does not ensure that the cache directory exists.
    """
    # Linux, Unix, AIX, etc.
    if os.name == "posix" and sys.platform != "darwin":
        # use ~/.cache if empty OR not set
        xdg = os.environ.get("XDG_CACHE_HOME", None) or Path("~/.cache").expanduser()
        return Path(xdg, fname)

    # Mac OS
    elif sys.platform == "darwin":
        return Path.home() / "Library/Caches" / fname

    # Windows (hopefully)
    else:
        local = (
            os.environ.get("LOCALAPPDATA", None)
            or Path("~\\AppData\\Local").expanduser()
        )
        return Path(local, fname)


def prepare_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Waybar module for checking external IP"
    )

    parser.add_argument(
        "-v", "--verbosity", action="count", default=0, help="Increase output verbosity"
    )

    parser.add_argument(
        "-D", "--debug", dest="debug", help="Debug", action="store_true"
    )

    parser.add_argument(
        "--use-cache",
        help=f"Using cache from {get_cache_file()}",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "-F",
        "--text-fmt",
        help=f"Format for output text (default: {TEXT_FMT})",
        default=TEXT_FMT,
    )
    parser.add_argument(
        "--alt-fmt",
        help=f"Format for output alt (default: {ALT_FMT}). May be used for icons",
        default=ALT_FMT,
    )
    parser.add_argument(
        "--tooltip-fmt", help="Format for output tooltip", default=TOOLTIP_FMT
    )
    parser.add_argument(
        "ips",
        help="IP list to check",
        metavar="IP",
        default=["my"],
        # default=[None],
        nargs="*",
    )
    #  parser.add_argument(
    #      "-O",
    #      "--out",
    #      help="Output",
    #      metavar="FILE",
    #      type=argparse.FileType("w"),
    #  )

    return parser


def ip_request(ip: str = None) -> dict:
    qry = "https://ipapi.co/"
    if ip and ip != "my":
        # print(f"Checking IP: {ip}")
        qry = f"{qry}/{ip}"
        logger.info("requesting %s info", ip)
    else:
        logger.info("requesting my external ip info")
    qry = f"{qry}/json"
    try:
        with request.urlopen(qry) as f:
            status = f.status
            if status != 200:
                return {}
            raw = f.read()
            data = json.loads(raw.decode())
            logger.info("get info request successfull")
            logger.debug(data)
            return data
    except (HTTPError, URLError) as e:
        return dict(error=True, reason=e.reason)
    except json.JSONDecodeError:
        return dict(error=True, reason=f"JSONDecode error: {raw}")
    return None


def get_external_ip() -> dict:
    # qry = "https://ifconfig.me/all.json"
    qry = "https://ifconfig.me/ip"
    logger.debug("try to get external ip")
    try:
        with request.urlopen(qry) as fq:
            status = fq.status
            if status != 200:
                return {}
            raw = fq.read()
            return raw.decode()

    except (HTTPError, URLError, UnicodeDecodeError):
        return None


def flag_regional_indicator(code: List[str]) -> str:
    """Two letters are converted to regional indicator symbols
    :param str code: two letter ISO 3166 code
    :return: regional indicator symbols of the country flag
    :rtype: str
    """
    OFFSET = ord("🇦") - ord("A")

    return "".join([chr(ord(c.upper()) + OFFSET) for c in code])


def get_ip_data(
    ip: str = None,
    text_fmt: str = TEXT_FMT,
    alt_fmt: str = ALT_FMT,
    tooltip_fmt: str = TOOLTIP_FMT,
) -> dict:
    if not ip or ip == "my":
        ip = get_external_ip()
        logger.info("external ip: %s", ip)

    if ip and ip in CACHE:
        logger.info("found %s info in cache", ip)
        info = CACHE[ip]
    else:
        info = ip_request(ip)
        CACHE[info["ip"]] = info.copy()

    data = {}
    dt = datetime.now()
    info["last_update"] = dt
    # print(info)
    if not info:
        data["text"] = "UNK"
        data["tooltip"] = "External IP request returns nothing"
        data["class"] = "error"
        return data

    if info.get("error"):
        data["text"] = "ERR"
        data["tooltip"] = str(info.get("reason"))
        data["class"] = "error"
        return data

    info["flag"] = flag_regional_indicator(info["country_code"])
    data["text"] = text_fmt.format(**info)
    data["alt"] = alt_fmt.format(**info)
    data["tooltip"] = tooltip_fmt.format(
        full=json.dumps(info, indent=3, default=str),
        **info,
    )
    # data["class"] = info["country_code"]
    data["class"] = [str(info[k]).replace(" ", "_") for k in info if k in CLASS_FLDS]
    return data


def load_cache(fname: str) -> dict:
    fname = Path(fname)
    if not fname.exists():
        return {}
    try:
        with open(fname) as fc:
            data = json.load(fc)
        logger.info(f"cache loaded from %s, {len(CACHE)} entried", fname)
        return data
    except json.JSONDecodeError:
        return {}


def main() -> None:
    parser = prepare_argparse()
    args = parser.parse_args()
    # print(args)
    # print(get_cache_file())
    loglevel = logging.WARN
    if args.verbosity:
        loglevel = logging.INFO
    if args.debug:
        loglevel = logging.DEBUG

    logger.setLevel(loglevel)
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    global CACHE
    if args.use_cache:
        CACHE = load_cache(get_cache_file())

    for ip in args.ips:
        logger.info("get info about %s IP-address", ip)
        info = get_ip_data(ip, args.text_fmt, args.alt_fmt, args.tooltip_fmt)

        print(json.dumps(info, default=str))

    if args.use_cache:
        with open(get_cache_file(), "w") as fc:
            json.dump(CACHE, fc, indent=3, default=str)
            logger.info("save %s cache entries to %s", len(CACHE), fc.name)


if __name__ == "__main__":
    main()
