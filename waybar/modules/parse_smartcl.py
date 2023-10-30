#!/usr/bin/env python3

"""
{
  "local_time": {
    "time_t": 1691563310,
    "asctime": "Wed Aug  9 09:41:50 2023 MSK"
  },
  "device": {
    "name": "/dev/disk/by-uuid/058ec761-48af-4849-9cc2-74af6f674f63",
    "info_name": "/dev/disk/by-uuid/058ec761-48af-4849-9cc2-74af6f674f63 [USB NVMe JMicron]",
    "type": "sntjmicron",
    "protocol": "NVMe"
  },
  "model_name": "Netac MobileDataStar",
  "serial_number": "AA202207020051207046",
  "firmware_version": "V0323A0",
  "nvme_pci_vendor": {
    "id": 4719,
    "subsystem_id": 4719
  },
  "nvme_ieee_oui_identifier": 1,
  "nvme_controller_id": 1,
  "nvme_version": {
    "string": "1.3",
    "value": 66304
  },
  "nvme_number_of_namespaces": 1,
  "nvme_namespaces": [
    {
      "id": 1,
      "size": {
        "blocks": 488397168,
        "bytes": 250059350016
      },
      "capacity": {
        "blocks": 488397168,
        "bytes": 250059350016
      },
      "utilization": {
        "blocks": 488397168,
        "bytes": 250059350016
      },
      "formatted_lba_size": 512,
      "eui64": {
        "oui": 1,
        "ext_id": 0
      }
    }
  ],
  "user_capacity": {
    "blocks": 488397168,
    "bytes": 250059350016
  },
  "logical_block_size": 512,
  "smart_support": {
    "available": true,
    "enabled": true
  },
  "smart_status": {
    "passed": true,
    "nvme": {
      "value": 0
    }
  },
  "nvme_smart_health_information_log": {
    "critical_warning": 0,
    "temperature": 54,
    "available_spare": 100,
    "available_spare_threshold": 10,
    "percentage_used": 0,
    "data_units_read": 883023,
    "data_units_written": 1342430,
    "host_reads": 10061480,
    "host_writes": 13428264,
    "controller_busy_time": 432,
    "power_cycles": 62,
    "power_on_hours": 355,
    "unsafe_shutdowns": 17,
    "media_errors": 0,
    "num_err_log_entries": 0,
    "warning_temp_time": 0,
    "critical_comp_time": 0
  },
  "temperature": {
    "current": 54
  },
  "power_cycle_count": 62,
  "power_on_time": {
    "hours": 355
  }
}
"""
import argparse
import json
from pprint import pprint

TEXT_FMT = "{temperature[current]}"
ALT_FMT = TEXT_FMT
TOOLTIP_FMT = """Device: {device[name]}
Protocol: {device[protocol]}
Model: <b>{model_name}</b>
Serial: <b>{serial_number}</b>

Temperature: <b>{temperature[current]}</b>

Power cycle count: {power_cycle_count}
Power on time: {power_on_time[hours]}

Last update: <i>{local_time[asctime]}</i>"""


def prepare_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parsing smartcl for waybar")

    parser.add_argument(
        "-v", "--verbosity", action="count", default=0, help="Increase output verbosity"
    )

    parser.add_argument(
        "-D", "--debug", dest="debug", help="Debug", action="store_true"
    )

    parser.add_argument(
        "-L",
        "--limit",
        type=int,
        help="Temperature limit - warning",
        default=60,
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
        "-f",
        "--file",
        help="File with smartcl info (may use '-' for stdin)",
        metavar="FILE",
        type=argparse.FileType("r"),
    )

    return parser


def format_smartcl(
    info: dict,
    limit: int,
    text_fmt: str = TEXT_FMT,
    alt_fmt: str = ALT_FMT,
    tooltip_fmt: str = TOOLTIP_FMT,
) -> dict:
    data = {
        "text": text_fmt.format(**info),
        "tooltip": tooltip_fmt.format(
            full=json.dumps(info, indent=3, default=str), **info
        ),
        "alt": alt_fmt.format(**info),
    }
    temperature = info["temperature"]["current"]
    if temperature > limit:
        data["class"] = "error"
        with open("/tmp/smartctl_error.txt", "w") as fo:
            json.dump(info, fo, indent=3, default=str)
    return data


def main() -> None:
    parser = prepare_argparse()
    args = parser.parse_args()

    info = json.load(args.file)
    info = format_smartcl(
        info, args.limit, args.text_fmt, args.alt_fmt, args.tooltip_fmt
    )

    print(json.dumps(info, default=str))


if __name__ == "__main__":
    main()
