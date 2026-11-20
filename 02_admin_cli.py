import argparse
import sys

import paramiko

from ssh_connection import open_ssh
from remote_utils import remote_output, root_disk_percent


def build_parser():
    parser = argparse.ArgumentParser(
        description="CLI для диагностики сервера master1"
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True,
        help="Административная операция"
    )

    commands.add_parser(
        "host",
        help="Показать имя удалённого сервера"
    )

    disk_parser = commands.add_parser(
        "disk",
        help="Проверить заполнение диска"
    )

    disk_parser.add_argument(
        "-t",
        "--threshold",
        type=int,
        default=80,
        metavar="PERCENT",
        help="Порог заполнения диска, по умолчанию 80"
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "disk":
        if not 1 <= args.threshold <= 100:
            parser.error(
                "Порог должен находиться в диапазоне 1–100"
            )

    try:
        with open_ssh() as client:

            if args.command == "host":
                hostname = remote_output(
                    client, "hostname"
                )

                print(f"Удалённый сервер: {hostname}")
                return 0

            if args.command == "disk":
                used = root_disk_percent(client)

                print(f"Диск заполнен на {used}%")
                print(f"Порог: {args.threshold}%")

                if used >= args.threshold:
                    print("Превышен установленный порог")
                    return 1

                print("Показатель в допустимых пределах")
                return 0

    except (
        OSError,
        RuntimeError,
        ValueError,
        paramiko.SSHException
    ) as error:
        print(
            f"Ошибка диагностики: {error}",
            file=sys.stderr
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())