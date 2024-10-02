import sys
from colorama import Fore, Back, Style

class Logger:    
    def WARNING(msg):
        print(f"{Back.YELLOW}WARNING{Style.RESET_ALL} :: {Fore.YELLOW}" + str(msg) + f"{Style.RESET_ALL}")
    def ERROR(msg):
        print(f"{Back.RED}ERROR{Style.RESET_ALL} :: {Fore.RED}" + str(msg) + f"{Style.RESET_ALL}")
        sys.exit()
    def INFO(msg):
        print(f"{Back.GREEN}INFO{Style.RESET_ALL} :: {Fore.GREEN}" + str(msg) + f"{Style.RESET_ALL}")

