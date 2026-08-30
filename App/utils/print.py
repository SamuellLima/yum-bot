from datetime import datetime

import colorama

colorama.init()


class Print:
    @staticmethod
    def _log(color: str, tag: str, message: object) -> None:
        now = datetime.now().strftime("%H:%M:%S")
        print(color, tag, now, " ", message, colorama.Fore.RESET)

    @staticmethod
    def success(message: object) -> None:
        Print._log(colorama.Fore.GREEN, "[SUCCESS]", message)

    @staticmethod
    def error(message: object) -> None:
        Print._log(colorama.Fore.RED, "[FAIL]", message)

    @staticmethod
    def warning(message: object) -> None:
        Print._log(colorama.Fore.YELLOW, "[WARNING]", message)

    @staticmethod
    def info(message: object) -> None:
        Print._log(colorama.Fore.BLUE, "[INFO]", message)
