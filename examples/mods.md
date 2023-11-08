Projekt pisany dla python3.9
Projekt zawiera pakiet "modules", w nim umieszczone jest wiele klas publicznych w ich własnych modułach.
Nazwy klas rozpoczynają się od przedrostka 'Mod'. Moduły zawierają również ich klasy prywatne, nieistotna w tym pytaniu.
Wszystkie klasy, ktych nazwa zaczyna się od 'Mod', dziedziczą ze wspólnego interfejsu, więc udostępniają identyczny zestaw
metod, różnią się oczywiście tylko realizowanymi zadaniami. Wywołanie konstruktora tych metod jest
również identyczne, dla ułatwienia załóżmy, że ich konstruktor przyjmuje tylko jeden argument,
który jest domyślnie pustym ciągiem znaków:
`def __init__(self, name: str = '')`
Klasy któych nazwa zaczyna się od 'Mod' dziedziczą również z biblioteki 'threading.Threads' i wykonywane są jako
osobne wątki.
W celu lepszego zobrazowania zadania załóżmy, że importowane klasy 'Mod' to:
ModA, ModB, ModC, ModD, ModE, ModF.

W głównym wątku programu mam zmienną, której wartość pochodzi wczytanej konfiguracji programu:

```
self.modules_to_run = ['ModA', 'ModD', 'ModF']
```

Przykładowy program:
```
from typing import List


class App:
    """"""

    def __init__(self):
        """Constructor."""
        self.modules_to_run = []
        # initialization of other valiables

        # get module list
        self.modules_to_run = self.__load_configuration()

    def __load_configuration(self) -> List:
        """Get the configured module list."""
        # for example
        return ["ModA", "ModD", "ModF"]

    def __init_modules_to_run(self) -> List:
        """Returns a list of initialized objects of the configured classes."""
        # import classes from module package
        from modules import *

        # list of objects to run
        tmp = []

        for item_str in self.modules_to_run:
            # create object from class name string
            # and append it to tmp list
            class_object = # init module class
            if class_object:
                tmp.append(class_object)

        return tmp

    def run(self) -> None:
        """Main procedure."""
        # Thread objects
        th_to_run = self.__init_modules_to_run()

        for th in th_to_run:
            # run the module
            th.start()

        # continuation of the procedure
```

Jak powinna wyglądać pętla `for` w metodzie `def __init_modules_to_run()`, która
ze skonfigurowanej listy nazw klas spróbuje stworzyć ich instancje i, jeśli
zakończy się to sukcesem, doda je do listy `tmp`?

Odp nr 1:
```
def __init_modules_to_run(self) -> List:
    """Returns a list of initialized objects of the configured classes."""
    # Import classes from the 'modules' package
    from modules import Mod_A, Mod_B, Mod_C, Mod_D, Mod_E, Mod_F

    # Mapping of class names to class objects
    class_mapping = {
        'Mod_A': Mod_A,
        'Mod_B': Mod_B,
        'Mod_C': Mod_C,
        'Mod_D': Mod_D,
        'Mod_E': Mod_E,
        'Mod_F': Mod_F
    }

    # List of objects to run
    tmp = []

    for item_str in self.modules_to_run:
        # Check if the class name is in the class mapping
        if item_str in class_mapping:
            # Create an object of the specified class and append it to tmp list
            class_object = class_mapping[item_str]()
            tmp.append(class_object)

    return tmp
```

Odp nr 2:
```
import importlib
from typing import List

class App:
    # ... (inne metody i inicjalizacja)

    def __init_modules_to_run(self) -> List:
        """Returns a list of initialized objects of the configured classes."""
        # List of objects to run
        tmp = []

        for item_str in self.modules_to_run:
            # Dynamically import the module containing the class
            module_name = f"modules.{item_str.lower()}"
            try:
                module = importlib.import_module(module_name)
            except ModuleNotFoundError:
                print(f"Module {module_name} not found.")
                continue

            # Get the class object from the imported module
            if hasattr(module, item_str):
                class_object = getattr(module, item_str)()
                tmp.append(class_object)
            else:
                print(f"Class {item_str} not found in module {module_name}.")

        return tmp

# ... (kontynuacja kodu)
```
