def remote_output(client, command: str) -> str:
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

    status = stdout.channel.recv_exit_status()

    if status != 0:
        raise RuntimeError(
            f"Команда завершилась с кодом {status}: "
            f"{errors}"
        )

    return output


def root_disk_percent(client) -> int:
    output = remote_output(client, "df -P /")

    lines = output.splitlines()

    if len(lines) < 2:
        raise ValueError(
            "Некорректный результат команды df"
        )

    fields = lines[-1].split()

    if len(fields) < 6:
        raise ValueError(
            "Недостаточно полей в результате df"
        )

    return int(fields[-2].rstrip("%"))