from pathlib import Path
from datetime import datetime, timezone

from ssh_connection import open_ssh


def main():
    base_dir = Path(__file__).resolve().parent

    data_dir = base_dir / "data"
    downloads_dir = base_dir / "downloads"

    data_dir.mkdir(exist_ok=True)
    downloads_dir.mkdir(exist_ok=True)

    # Подготовка локального файла
    local_file = data_dir / "server-note.txt"

    content = (
        "server=master1\n"
        "source=windows\n"
        f"created_at={datetime.now(timezone.utc).isoformat()}\n"
    )

    local_file.write_text(
        content,
        encoding="utf-8"
    )

    remote_dir = "/root/paramiko-course-training"
    remote_file = f"{remote_dir}/server-note.txt"

    downloaded_file = (
        downloads_dir / "server-note-from-master1.txt"
    )

    with open_ssh() as client:
        with client.open_sftp() as sftp:

            # Подготовка каталога на сервере
            try:
                sftp.stat(remote_dir)

            except FileNotFoundError:
                sftp.mkdir(remote_dir)

            # Передача файла с Windows на Linux
            sftp.put(
                str(local_file),
                remote_file
            )

            print(f"Файл отправлен: {remote_file}")

            # Получение метаданных удалённого файла
            remote_stat = sftp.stat(remote_file)

            print(
                f"Размер удалённого файла: "
                f"{remote_stat.st_size} байт"
            )

            # Скачивание файла обратно на Windows
            sftp.get(
                remote_file,
                str(downloaded_file)
            )

            print(f"Файл получен: {downloaded_file}")

    # Проверка содержимого
    original = local_file.read_bytes()
    downloaded = downloaded_file.read_bytes()

    if original == downloaded:
        print("Проверка успешна: содержимое совпадает")
    else:
        raise SystemExit(
            "Ошибка: содержимое файлов различается"
        )


if __name__ == "__main__":
    main()