import argparse


def percentage(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "Процент должен быть целым числом"
        ) from error

    if not 1 <= number <= 100:
        raise argparse.ArgumentTypeError(
            "Процент должен находиться в диапазоне 1–100"
        )

    return number


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Настройка проверки ресурсов сервера"
    )

    parser.add_argument(
        "server",
        help="Имя проверяемого сервера"
    )

    parser.add_argument(
        "-t",
        "--threshold",
        type=percentage,
        default=80,
        metavar="PERCENT",
        help="Порог заполнения диска, по умолчанию 80"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Вывести дополнительные сведения"
    )

    args = parser.parse_args()

    print(f"Сервер: {args.server}")
    print(f"Порог заполнения: {args.threshold}%")

    if args.verbose:
        print("Подробный режим включён")
        print("Параметры успешно обработаны")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())