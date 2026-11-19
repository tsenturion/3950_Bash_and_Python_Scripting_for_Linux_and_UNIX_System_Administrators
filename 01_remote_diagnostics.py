from pathlib import Path

from ssh_connection import open_ssh


COMMANDS = [
    ("Имя сервера", "hostname"),
    ("Текущий пользователь", "id -un"),
    ("Время работы системы", "uptime"),
    ("Дисковое пространство", "df -h /"),
]


def run_remote_command(client, command: str) -> tuple:
    stdin, stdout, stderr = client.exec_command(
        command,
        timeout=15
    )

    stdin.close()

    output = stdout.read().decode(
        "utf-8",
        errors="replace"
    ).strip()

    errors = stderr.read().decode(
        "utf-8",
        errors="replace"
    ).strip()

    exit_code = stdout.channel.recv_exit_status()

    return exit_code, output, errors


def main():
    base_dir = Path(__file__).resolve().parent

    report_dir = base_dir / "reports"
    report_dir.mkdir(exist_ok=True)

    report_lines = []

    with open_ssh() as client:
        for title, command in COMMANDS:
            print(f"Выполняется: {command}")

            code, output, errors = run_remote_command(
                client,
                command
            )

            if code != 0:
                print(
                    f"Ошибка команды {command}: {errors}"
                )
                raise SystemExit(1)

            report_lines.append(f"=== {title} ===")
            report_lines.append(output)
            report_lines.append("")

    report = "\n".join(report_lines)

    report_file = report_dir / "master1-system.txt"

    report_file.write_text(
        report,
        encoding="utf-8"
    )

    print("\n" + report)
    print(f"Локальный отчёт: {report_file}")


if __name__ == "__main__":
    main()