import tkinter as tk

from module1 import FirstPageDialog
from module1_page2 import SecondPageDialog
from module2 import GroupDialog


class Work1Workflow:
    """Управляет переходами между двумя диалоговыми окнами Робота1."""

    def __init__(self, parent: tk.Misc) -> None:
        self._parent = parent

    def run(self) -> str | None:
        page = 1
        while True:
            if page == 1:
                action = FirstPageDialog(self._parent).show()
                if action == "next":
                    page = 2
                else:
                    return None
            else:
                action = SecondPageDialog(self._parent).show()
                if action == "back":
                    page = 1
                elif action == "accept":
                    return "Підтверджено"
                else:
                    return None


class LabApplication:
    """Головне вікно та меню лабораторної роботи."""

    def __init__(self) -> None:
        self._window = tk.Tk()
        self._window.title("Lab1 - модульне програмування")
        self._window.geometry("600x220")
        self._window.resizable(False, False)
        self._result_label = tk.Label(
            self._window,
            text='Виберіть пункт меню «Робота1» або «Робота2».',
            anchor="w",
        )
        self._result_label.pack(fill="x", padx=20, pady=20)
        self._work1 = Work1Workflow(self._window)
        self._create_menu()

    def _create_menu(self) -> None:
        menu_bar = tk.Menu(self._window)
        work_menu = tk.Menu(menu_bar, tearoff=False)
        work_menu.add_command(label="Робота1", command=self._run_work1)
        work_menu.add_command(label="Робота2", command=self._run_work2)
        menu_bar.add_cascade(label="Робота", menu=work_menu)
        menu_bar.add_command(label="Вихід", command=self._window.destroy)
        self._window.config(menu=menu_bar)

    def _show_result(self, work_name: str, value: str | None) -> None:
        if value is not None:
            self._result_label.config(text=f"{work_name}: {value}")

    def _run_work1(self) -> None:
        self._show_result("Робота1", self._work1.run())

    def _run_work2(self) -> None:
        self._show_result("Робота2", GroupDialog(self._window).show())

    def run(self) -> None:
        self._window.mainloop()


if __name__ == "__main__":
    LabApplication().run()