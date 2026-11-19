from pathlib import Path
import getpass
import paramiko


SSH_ALIAS = "master1-root"


def open_ssh() -> paramiko.SSHClient:
    ssh_dir = Path.home() / ".ssh"

    config_path = ssh_dir / "config"
    known_hosts_path = ssh_dir / "known_hosts"

    if not config_path.is_file():
        raise FileNotFoundError(
            f"SSH-конфигурация отсутствует: {config_path}"
        )

    if not known_hosts_path.is_file():
        raise FileNotFoundError(
            f"Файл известных серверов отсутствует: "
            f"{known_hosts_path}"
        )

    config = paramiko.SSHConfig.from_path(
        str(config_path)
    )

    settings = config.lookup(SSH_ALIAS)

    hostname = settings.get("hostname", SSH_ALIAS)
    username = settings.get("user", getpass.getuser())
    port = int(settings.get("port", 22))

    identity_files = [
        str(Path(path).expanduser())
        for path in settings.get("identityfile", [])
    ]

    client = paramiko.SSHClient()

    client.load_system_host_keys(
        str(known_hosts_path)
    )

    client.set_missing_host_key_policy(
        paramiko.RejectPolicy()
    )

    try:
        client.connect(
            hostname=hostname,
            port=port,
            username=username,
            key_filename=identity_files or None,
            allow_agent=True,
            look_for_keys=True,
            timeout=10,
            auth_timeout=15,
            banner_timeout=15,
        )

    except Exception:
        client.close()
        raise

    return client


if __name__ == "__main__":
    with open_ssh() as client:
        _, stdout, stderr = client.exec_command(
            "hostname",
            timeout=10
        )

        hostname = stdout.read().decode(
            "utf-8",
            errors="replace"
        ).strip()

        error_text = stderr.read().decode(
            "utf-8",
            errors="replace"
        )

        status = stdout.channel.recv_exit_status()

        if status != 0:
            raise RuntimeError(
                f"Удалённая команда завершилась с кодом "
                f"{status}: {error_text}"
            )

        print("SSH-соединение установлено")
        print(f"Удалённый сервер: {hostname}")