from colorama import Fore


class Menu:
    def __init__(self, title, items):
        self.title = title
        self.items = items

    @property
    def text(self):
        result = [self.title]

        for item in self.items:
            result.append(f"{self.items.index(item)+1}. {item}")

        return '\n'.join(result) + '\n'

    def select(self, index):
        return self.items[index-1]



    def __str__(self):
        return self.text


main_menu = Menu(f'\n{Fore.CYAN}Главное меню.{Fore.LIGHTWHITE_EX} Доступные модули:',
                 [
                     'Панель аккаунтов',
                     'Чекер аккаунтов',
                     'Спам репостом',
                     'Прямой спам',
                     'Парсинг',
                     'Инвайтинг',
                     'Репортер'
                 ])

