# Repository Guidelines

## Quick Rules

### Communication

- Odpowiadaj w języku polskim lub w języku użytkownika.
- Zachowuj zwięzłą, techniczną formę odpowiedzi zgodną z konwencjami projektu.
- Komentarze i dokumentację w repozytorium zapisuj po angielsku.

### Change Management

- Przy zmianach obejmujących wiele plików przedstaw plan i poproś o akceptację.
- ZAWSZE aktualizuj dokumentację po zmianach w kodzie.
- ZAWSZE przeprowadzaj versioning projektu po zmianach w kodzie.

### Git Policy

- NEVER execute `git push`.
- NEVER execute `git commit`.
- NEVER execute `git add`.
- Dozwolone są wyłącznie operacje odczytu, np. `git status`, `git diff`, `git log`.

Powód: użytkownik samodzielnie weryfikuje i publikuje zmiany.

## Project Structure

- `aasd.py` - główny punkt startowy.
- `bin/aasd` - wrapper do uruchamiania demona.
- `server/` - kod wykonawczy.
- `libs/` - współdzielone biblioteki.
- `modules/com/` - komunikacja z użytkownikiem.
- `modules/run/` - zadania cykliczne i reaktywne.
- `tests/` - testy.
- `docs/`, `examples/` - dłuższa dokumentacja i przykłady.

## Development Workflow

### Preferred Tooling

Do lokalnej pracy używaj Poetry.

- `poetry install` - instaluje zależności z `pyproject.toml`.
- `poetry run python aasd.py` - uruchamia demona z katalogu repozytorium.
- `poetry run pytest` - uruchamia testy z `tests/`.
- `poetry run black .` - formatuje kod Python.
- `npx prettier --write "*.md"` - formatuje dokumentację Markdown.
- `poetry run pycodestyle .` - sprawdza zgodność stylu.
- `poetry run pydocstyle .` - sprawdza zgodność docstringów.
- `poetry run mypy libs/` - uruchamia statyczną analizę typów.

Jeżeli Poetry nie jest dostępne, `requirements.txt` wystarcza do podstawowej instalacji runtime, ale prace deweloperskie powinny korzystać z Poetry.

### Development Commands

#### Poetry

```bash
# Instalacja zależności
poetry install

# Dodanie nowej zależności
poetry add package-name
poetry add --group dev package-name

# Aktualizacja zależności
poetry update

# Uruchomienie komend w virtualenv
poetry run python script.py
poetry run pytest
poetry run black .
```

#### Formatting And Linting

```bash
# Formatowanie kodu
poetry run black .
poetry run black libs/ tests/
npx prettier --write "*.md"

# Sprawdzanie stylu
poetry run pycodestyle libs/

# Type checking
poetry run mypy libs/
```

#### Testing

```bash
# Uruchomienie wszystkich testów
poetry run pytest

# Uruchomienie z pokryciem
poetry run pytest --cov=libs

# Uruchomienie konkretnego testu
poetry run pytest tests/test_module.py::TestClass::test_method

# Verbose mode
poetry run pytest -v
```

## Coding Standards

### General Style

- Projekt celuje w Python 3.10+.
- Stosuj formatowanie zgodne z Black i wcięcia 4-spacjowe.
- Zachowuj czytelny podział importów.
- Pliki modułów zapisuj w `snake_case`.
- Klasy zapisuj w `PascalCase`.
- Metody testowe nazywaj w stylu `test_01_feature`.
- Zachowuj obecny styl nagłówków plików i kodowanie UTF-8 tam, gdzie już występują.

### Language Rules

- Docstringi muszą być po angielsku.
- Komentarze w kodzie muszą być po angielsku.
- Dokumentacja projektu musi być po angielsku.
- Dotyczy to w szczególności `README.md`, `docs/*` oraz dokumentacji wewnątrz modułów projektu.

### Class Structure

#### Mandatory Requirements

1. Kod klasy musi być podzielony na sekcje oddzielone separatorami.
2. Separator musi mieć format `# #[SECTION NAME]#####...` i długość 80 znaków.
3. Metody i właściwości w każdej sekcji muszą być posortowane alfabetycznie.
4. Wszystkie metody i właściwości muszą posiadać pełne typowanie.

#### Required Section Order

1. `CONSTANTS`
2. `CONSTRUCTOR`
3. `PUBLIC PROPERTIES`
4. `PROTECTED PROPERTIES`
5. `PRIVATE PROPERTIES`
6. `PUBLIC METHODS`
7. `PROTECTED METHODS`
8. `PRIVATE METHODS`
9. `STATIC/CLASS METHODS`
10. `EOF` - ostatnia linia tekstu w pliku modułu

#### `EOF` Clarification

- `EOF` oznacza wyłącznie ostatnią linię pliku modułu.
- Nie dodawaj sekcji `EOF` na końcu każdej klasy.
- W pliku może istnieć tylko jeden znacznik `# #[EOF]...` i powinien znajdować się na końcu modułu.

#### Separator Example

```python
# #[PUBLIC METHODS]####################################################################
```

## Docstring Standards

### Global Requirements

- Wszystkie docstringi muszą być po angielsku.
- Format modułu musi zawierać `Author:`, `Created: YYYY-MM-DD`, `Purpose:`.
- Format funkcji i metod musi zawierać krótkie streszczenie oraz opcjonalne sekcje `### Arguments`, `### Returns`, `### Raises`.
- We wszystkich modułach obowiązuje jednolity autor:
  `Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>`

### Section Rules

#### `### Arguments:`

- WYMAGANA dla metod z parametrami innymi niż `self` lub `cls`.
- WYMAGANA dla setterów.
- WYMAGANA dla `__init__`, jeśli przyjmuje parametry.
- WYMAGANA dla pozostałych metod magicznych z parametrami, np. `__setitem__`, `__getitem__`.
- NIEWYMAGANA dla getterów bez parametrów.
- NIEWYMAGANA dla comparatorów: `__lt__`, `__le__`, `__gt__`, `__ge__`, `__eq__`, `__ne__`.

#### `### Returns:`

- WYMAGANA dla getterów, `get_*`, `is_*`, `has_*` i `@property`.
- OPCJONALNA dla metod `-> None`, np. setterów i `__init__`.

#### `### Raises:`

- OPCJONALNA, tylko gdy metoda faktycznie rzuca wyjątki.

#### Formatting Rules

- Zapisuj nagłówki sekcji bez spacji przed dwukropkiem, np. `### Arguments:`.
- Pliki `__init__.py` mogą mieć uproszczone docstringi bez pełnej struktury `Author/Created/Purpose`.

## Testing Rules

### General Requirements

- Nowe testy zapisuj w `tests/` w plikach `test_*.py`.
- Obecna baza testów opiera się na `unittest`.
- Klasy testowe dziedziczą po `unittest.TestCase`.
- Zestaw uruchamiaj przez `poetry run pytest`.
- Dodawaj testy regresyjne dla zmian w bibliotekach, parserach i logice modułów przed modyfikacją zachowania demona.
- Zachowuj istniejące osłony dla zachowań zależnych od FreeBSD.
- Zapewnij pokrycie testami każdej nowej funkcjonalności.
- Uruchamiaj testy przed commitem: `poetry run pytest`.
- Sprawdzaj pokrycie testami: `poetry run pytest --cov=libs`.

## Configuration And Operations

- Demon jest przeznaczony do uruchamiania pod nadzorem menedżera usług.
- Konfiguracja jest czytana z `/etc/aasd.conf`.
- Dla buildów `DEV` konfiguracja może być czytana z `/var/tmp/aasd.conf`.
- Nie zapisuj w repozytorium sekretów, prawdziwych danych uwierzytelniających ani lokalnych ścieżek środowiskowych w przykładach, testach i dokumentacji.

## Documentation Maintenance

### Mandatory Update Order

1. Najpierw sprawdź i zaktualizuj docstringi w kodzie źródłowym.
2. Następnie regeneruj dokumentację API, np. `make docs` lub równoważnym generatorem.
3. Na końcu zaktualizuj dokumentację Markdown.

### Scope Rule

Jeśli polecenie nie wskazuje konkretnego modułu lub klasy, przeprowadź aktualizację dla całego projektu.

### Documentation Checklist

- [ ] Docstringi w kodzie źródłowym
- [ ] Dokumentacja API
- [ ] `README.md`
- [ ] `docs/*.md`
- [ ] `CHANGELOG.md`

### Patterns To Verify In Documentation

1. `ReadOnlyClass` - trzy wzorce kluczy: `__Keys`, `_Keys`, `NazwaKeys` w `libs/keys.py`, jeśli używasz JskToolBox.
2. `Raise.error()` - zawsze z `raise`, jeśli używasz JskToolBox.
3. `BClasses properties` - `_c_name` i `_f_name` nie są deklarowane, jeśli używasz JskToolBox.
4. `Lazy imports` - preferowane krótkie formy, jeśli używasz JskToolBox.
5. `BData methods` - nowe zasady 2024:
   - typ rejestrowany tylko w `_set_data()` przez `set_default_type`,
   - `_get_data()` nie używa `set_default_type`,
   - typ raz ustawiony jest niezmienny,
   - `set_default_type=None` zachowuje istniejący typ,
   - obsługa `Optional[T]`, `Dict[K, V]`, `List[T]`, `Union` i zagnieżdżeń.

## Project Versioning

### Semantic Versioning Rules

Format wersji: `X.Y.Z` (`MAJOR.MINOR.PATCH`).

#### Mandatory Rules

1. Zmiany w kodzie projektu wymagają aktualizacji wersji zgodnie z Semantic Versioning.
2. Zmiany obejmujące wyłącznie dokumentację projektową lub developerską nie wymagają zmiany wersji.
3. Przy zwiększeniu `Y` (`MINOR`) należy zresetować `Z` do `0`.
4. Przy zwiększeniu `X` (`MAJOR`) należy zresetować `Y` i `Z` do `0`.

#### Examples

```text
Current: 0.2.3
- Bug fix       -> 0.2.4
- New feature   -> 0.3.0
- Breaking API  -> 1.0.0
```

#### Version Meaning

- `X` (`MAJOR`) - breaking changes, incompatible API changes.
- `Y` (`MINOR`) - new features, backward-compatible additions.
- `Z` (`PATCH`) - bug fixes, small improvements, refactoring.

### Documentation And Non-Code Changes

- Zmiany wyłącznie w dokumentacji projektowej, dokumentacji developerskiej, planach prac lub zasadach repozytorium nie wymagają podniesienia wersji.
- Takie zmiany nadal należy odnotować w odpowiedniej sekcji `CHANGELOG.md`.
- Jeśli zmiana łączy modyfikację kodu i dokumentacji, obowiązuje versioning wynikający ze zmiany kodu.

### Files To Update

Przy zmianie wersji zawsze aktualizuj oba pliki:

1. `pyproject.toml`

   ```toml
   [tool.poetry]
   version = "0.2.0"
   ```

2. `server/__init__.py`

   ```python
   __version_info__: tuple[int, int, int] = (0, 2, 0)
   ```

### Versioning Checklist

- [ ] Określ, czy zmiana obejmuje kod czy wyłącznie dokumentację / metadane developerskie
- [ ] Jeśli zmiana obejmuje kod: określ typ zmiany `MAJOR`, `MINOR`, `PATCH`
- [ ] Jeśli zmiana obejmuje kod: zaktualizuj obie wersje tak, aby były zgodne
- [ ] Zawsze dopisz zmianę do właściwej sekcji `CHANGELOG.md`
- [ ] Jeśli zmiana obejmuje kod: przygotuj commit message `chore: bump version to X.Y.Z`
- [ ] Jeśli zmiana obejmuje kod: przygotuj tag `git tag vX.Y.Z`

## Architecture Patterns

### JskToolBox Usage

Projekt wykorzystuje bibliotekę `jsktoolbox` jako fundament, jeśli dany moduł jest na niej oparty.

### Base Classes From `basetool`

- Klasy z modułu `jsktoolbox.basetool` są klasami bazowymi do dziedziczenia.
- Nie posiadają własnego konstruktora i nie wymagają `super().__init__()`.
- Dodają właściwości i metody do klas pochodnych.
- `ThBaseObject` zawiera deklaracje wymagane dla `threading.Thread`.
- Zamiast `class Worker(threading.Thread)` używaj `class Worker(ThBaseObject, Thread)`.

### `ReadOnlyClass` For Immutable Keys

#### Purpose

Celem jest minimalizacja błędów literówek w nazwach kluczy słowników `BData`. Docelowo wszystkie stałe klucze słownikowe powinny być definiowane przez `ReadOnlyClass`.

#### Pattern Selection

| Zasięg       | Wzorzec                     | Nazwa klasy | Lokalizacja     |
| ------------ | --------------------------- | ----------- | --------------- |
| Jedna klasa  | `__Keys`                    | `__Keys`    | wewnątrz klasy  |
| Cały moduł   | `_Keys`                     | `_Keys`     | nagłówek modułu |
| Cały projekt | publiczna klasa `NazwaKeys` | `NazwaKeys` | `libs/keys.py`  |

#### Pattern 1: Private `__Keys`

Używaj, gdy klucze są wykorzystywane wyłącznie przez jedną klasę.

```python
class MyClass(BData):
    class __Keys(object, metaclass=ReadOnlyClass):
        DATA: str = "__data__"
        COUNT: str = "__count__"

    def __init__(self) -> None:
        self._set_data(key=self.__Keys.DATA, value=None, set_default_type=Optional[str])
```

Python stosuje tu name mangling: `self.__Keys` przechodzi do `self._NazwaKlasy__Keys`, co eliminuje przysłanianie między klasami dziedziczącymi lub mixinami.

#### Pattern 2: Module-Level `_Keys`

Używaj, gdy kilka klas w tym samym module współdzieli te same klucze.

```python
class _Keys(object, metaclass=ReadOnlyClass):
    CONFIG: str = "__config__"
    STATE: str = "__state__"

class ClassA(BData):
    def setup(self) -> None:
        self._set_data(key=_Keys.CONFIG, value={}, set_default_type=Dict)

class ClassB(BData):
    def get_state(self) -> Optional[str]:
        return self._get_data(key=_Keys.STATE)
```

#### Pattern 3: Project-Wide `NazwaKeys`

Używaj, gdy klucze są współdzielone celowo w całym projekcie.

```python
# libs/keys.py
class ResponseDbQueryStatusKeys(object, metaclass=ReadOnlyClass):
    OK: str = "ok"
    ERROR: str = "error"

# usage
from libs.keys import ResponseDbQueryStatusKeys

status = ResponseDbQueryStatusKeys.OK
```

#### Decision Rule

```text
Klucz używany tylko w jednej klasie? -> __Keys
Klucz współdzielony przez klasy w module? -> _Keys
Klucz współdzielony w całym projekcie? -> NazwaKeys w libs/keys.py
```

### `BData` Typed Storage

Klasa `BData` zapewnia bezpieczny kontener słownikowy z kontrolą typów.

#### Core Rules

1. Typ rejestruj w setterach przez `set_default_type` w `_set_data()`.
2. `_get_data()` nie używa `set_default_type`.
3. Typ raz ustawiony jest niezmienny i wymaga `_delete_data()` przed zmianą.
4. `set_default_type=None` zachowuje istniejący typ.
5. Obsługiwane są typy złożone, w tym `Optional[T]`, `Dict[K, V]`, `List[T]`, `Union` i zagnieżdżenia.

#### Preferred Usage

```python
# Setter rejestruje typ
self._set_data("key", 42, set_default_type=int)

# Getter bez rejestracji typu
value = self._get_data("key", default_value=0)

# Aktualizacja z zachowaniem typu
self._set_data("key", 100)
```

#### Complex Types

```python
from typing import Dict, List, Optional

self._set_data("key", "text", set_default_type=Optional[str])
self._set_data("config", {"a": 1}, set_default_type=Dict[str, int])
self._set_data("items", ["a", "b"], set_default_type=List[str])
```

#### Additional Methods

- `_copy_data(key)` - deep copy wartości
- `_delete_data(key)` - usuwa wartość i constraint typu
- `_clear_data(key)` - usuwa wartość, zachowuje constraint

#### Required `Optional[T]` Handling In Getters

`_get_data(key)` zawsze zwraca `Optional[T]`. Jeśli getter ma zwracać ścisły typ `T`, należy jawnie obsłużyć `None`.

```python
@property
def my_property(self) -> int:
    value: Optional[int] = self._get_data(key=self._Keys.MY_KEY)
    if value is None:
        raise Raise.error(
            "Value for MY_KEY is None",
            ValueError,
            self._c_name,
            currentframe(),
        )
    return value
```

Można również użyć `default_value`, jeśli logika inicjalizacji tego wymaga.

```python
@property
def my_property(self) -> str:
    value: Optional[str] = self._get_data(
        key=self._Keys.MY_KEY,
        default_value="abc",
    )
    if value is None:
        return ""
    return value
```

### Lazy Imports

Preferowane są krótkie formy importów z `__init__.py`.

```python
# Preferred
from jsktoolbox.configtool import Config
from jsktoolbox.logstool import LoggerClient
from jsktoolbox.netaddresstool import Address, Network

# Avoid when short import exists
from jsktoolbox.configtool.main import Config
```

Sprawdzaj `__init__.py` w danym module, aby poznać dostępne lazy imports.

### Error Handling

Do zgłaszania wyjątków używaj `raise Raise.error()`.

```python
from inspect import currentframe
from jsktoolbox.raisetool import Raise

raise Raise.error(
    "Invalid value",
    ValueError,
    class_name=self._c_name,
    currentframe=currentframe(),
)
```

Niepoprawny wzorzec:

```python
Raise.error("Invalid value", ValueError)
```

`Raise.error()` tworzy wyjątek, ale go nie rzuca. Słowo kluczowe `raise` jest obowiązkowe.

## Git Workflow

### Branch Naming Convention

- `main` lub `master` - produkcja
- `develop` - rozwój
- `feature/nazwa-funkcji` - nowe funkcjonalności
- `bugfix/nazwa-bledu` - poprawki błędów
- `hotfix/nazwa-poprawki` - pilne poprawki produkcyjne

### Commit Messages

Format:

```text
<type>: <subject>
```

Dozwolone typy:

- `feat` - nowa funkcjonalność
- `fix` - poprawka błędu
- `docs` - zmiany w dokumentacji
- `style` - formatowanie i podobne poprawki niesemantyczne
- `refactor` - refaktoryzacja kodu
- `test` - dodanie lub modyfikacja testów
- `chore` - zmiany w narzędziach i konfiguracji

Przykłady:

- `feat: add user authentication`
- `fix: correct data validation in form`
- `docs: update README with installation instructions`

### Pull Request Expectations

Pull request powinien zawierać:

- cel zmiany,
- listę zmodyfikowanych modułów lub dokumentów,
- wynik `poetry run pytest`,
- informacje o założeniach konfiguracyjnych lub platformowych,
- przykładową konfigurację lub fragment logów, jeśli zmiana wpływa na operacje.

## Templates

### Module-Level Docstring Template

```python
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: YYYY-MM-DD

Purpose: Short, one-line summary of the module's purpose.

[Optional: More detailed description of the module's functionality,
its components, and how they fit into the larger project.]
"""
```

Pliki `__init__.py` mogą mieć uproszczone docstringi bez pełnej struktury.

### Class-Level Docstring Template

```python
"""Short, one-line summary of the class's purpose.

[Optional: More detailed description of the class's responsibilities,
design choices, and its role.]
"""
```

### Function/Method Docstring Template

```python
"""Short, one-line summary of what the function does.

[Optional: More detailed explanation of the function's logic,
its use cases, or important algorithms.]

### Arguments:
* arg1: type - Description of the first argument.
* arg2: Optional[type] - Description of the second argument. Defaults to DefaultValue.

### Returns:
type - Description of the returned value.

### Raises:
* ExceptionType: Description of the condition that causes this exception.
"""
```

Dla metod zwracających `None`, sekcja `### Returns:` może zostać pominięta lub zapisana jako `None - short description`.

### Markdown Documentation Template

````markdown
# [Module Name] Module

**Source:** `[path/to/module.py]`

**[High-Level Introduction]:**
_(A user-friendly paragraph explaining what this module helps the user accomplish.)_

## Getting Started

_(Explanation of how to import and perform initial setup, if any.)_

```python
from libs.module import Class1, Class2
```

---

## `[ClassName]` Class

**[Class Introduction]:**
_(Description of the class's role and responsibilities.)_

### `[ClassName].[MethodName]()`

**[Detailed Description]:**
_(Full paragraph explaining the method's purpose and use cases.)_

**Signature:**

```python
[Full method signature]
```

- **Arguments:**
  - `arg1: type` - [Description]
- **Returns:**
  - `type` - [Description]
- **Raises:**
  - `ExceptionType`: [Condition]

**Usage Example:**

```python
# Clear, commented example
result = ClassName.method_name(argument="value")
print(result)
```

---
````

### Project-Specific Rules Placeholder

Poniższa sekcja pozostaje jako miejsce na przyszłe rozszerzenia projektu.

```python
# Add project-specific examples and patterns here
```

## Contact And Resources

- Repository: <https://github.com/Szumak75/AASd>
- Issue Tracker: <https://github.com/Szumak75/AASd/issues>
- Maintainer: Jacek 'Szumak' Kotlarski <szumak@virthost.pl>

## Changelog

Plik `CHANGELOG.md` zawiera szczegółową historię zmian projektu zgodnie z Semantic Versioning, z podziałem na typy zmian i odniesieniami do commitów lub pull requestów.
