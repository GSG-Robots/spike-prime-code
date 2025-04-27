Dev Environment einrichten
==========================

Schritt 1: VSCode, Git & Python installieren
------------------------------------

- VSCode installieren: https://code.visualstudio.com/download
- Git installieren: https://git-scm.com/downloads
- Python installieren: https://www.python.org/downloads/ (Neuste verfügbare Version 3.13.x)

  - Aktiviere "Add Python to PATH".
  - Deaktiviere "Install Python Launcher".

Schritt 2: Poetry installieren
------------------------------------------------

Öffne Powershell und führe die folgenden Befehle aus:

.. code::
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    poetry config virtualenvs.in-project true
    [Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Users\johan\AppData\Roaming\Python\Scripts", "User")

Schritt 3: Repository klonen
------------------------------------------------

- Öffne VSCode
- Klicke unten links auf die Account-Optionen und melde dich mit deinem GitHub-Account an.
- Nutze die Tastenkombination :code:`Strg + Shift + P`, gebe "clone" ein und drücke zweimal :code:`Enter`.
- Gebe "GSG-Robots/competition-programs" ein und wähle den Ordner aus, in dem du das Repository speichern möchtest.
- Sobald der vorgang abgeschlossen ist, klicke auf "Öffnen".
- Klicke dann auf "Vertrauen".
  
Schritt 4: Abhängigkeiten installieren
------------------------------------------------

- Öffne das Terminal in VSCode mit :code:`Strg + Ö`.
- Gebe den folgenden Befehl ein und drücke :code:`Enter`:
  .. code::
    poetry install --no-root --with dev
- Warte dann, bis der Vorgang abgeschlossen ist.

Schritt 5: VSCode konfigurieren
------------------------------------------------

- Installiere die folgenden Erweiterungen:

  - `Python <vscode:extension/ms-python.python>`_
  - `Pylance <vscode:extension/ms-python.vscode-pylance>`_
  - `Ruff <vscode:extension/charliermarsh.ruff>`_
  - `Python Docstring Highlighter <vscode:extension/rodolphebarbanneau.python-docstring-highlighter>`_
  - `Python Poetry <vscode:extension/zeshuaro.vscode-python-poetry>`_
  - `F5 Anything <vscode:extension/discretegames.f5anything>`_
  
  Wenn du auch an der Dokumentation arbeiten willst:

  - `reStructuredText <vscode:extension/lextudio.restructuredtext>`_
  - `reStructuredText Syntax Highlighting <vscode:extension/trond-snekvik.simple-rst>`_

- Drücke :code:`Strg + Shift + P` und suche nach "Python: Select Interpreter" ein.
- Wähle :code:`3.13.x ('.venv')`.
