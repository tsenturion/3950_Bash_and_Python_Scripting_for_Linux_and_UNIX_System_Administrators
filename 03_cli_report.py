import argparse
import json
import sys

from datetime import datetime, timezone
from pathlib import Path

import paramiko

from ssh_connection import open_ssh
from remote_utils import remote_output, root_disk_percent


def build_parser():
    parser = argparse.ArgumentParser(
        description="Экспорт диагностики master1"
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json"],
        default="json",
        help="Формат отчёта"
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Путь к итоговому файлу"
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Разрешить перезапись существующего файла"
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    output = args.output.expanduser()

    if output.exists() and not args.overwrite:
        parser.error(
            "Файл уже существует. "
            "Используйте --overwrite для перезаписи"
        )

    try:
        with open_ssh() as client:
            hostname = remote_output(
                client, "hostname"
            )

            disk_percent = root_disk_percent(client)

            load_output = remote_output(
                client, "cat /proc/loadavg"
            )

            load_average = float(
                load_output.split()[0]
            )

        report = {
            "server": hostname,
            "checked_at": datetime.now(
                timezone.utc
            ).isoformat(timespec="seconds"),
            "disk_used_percent": disk_percent,
            "load_average_1m": load_average
        }

        if args.format == "json":
            content = json.dumps(
                report,
                ensure_ascii=False,
                indent=4
            )

        else:
            content = (
                f"Сервер: {report['server']}\n"
                f"Время: {report['checked_at']}\n"
                f"Диск: {report['disk_used_percent']}%\n"
                f"Нагрузка: {report['load_average_1m']}\n"
            )

        output.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output.write_text(
            content,
            encoding="utf-8"
        )

    except (
        OSError,
        RuntimeError,
        ValueError,
        paramiko.SSHException
    ) as error:
        print(
            f"Ошибка формирования отчёта: {error}",
            file=sys.stderr
        )
        return 1

    print(f"Отчёт сохранён: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())