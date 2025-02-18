# competition-programs

The code OTTWO runs on in competitions.

Contributors:

* [GSG-Robots](https://github.com/GSG-Robots)
* [Meganton](https://github.com/Meganton)
* [J0J0HA](https://github.com/J0J0HA)
* [E-r-i-c-Gepard](https://github.com/E-r-i-c-Gepard)
* [FINNtastisch007](https://github.com/FINNtastisch007)

## How to upload & run

To upload the code to the robot, you need to install the dependencies manually, which are listed in the `pyproject.toml` file.

If you have poetry, run the following command:

```bash
poetry install
```

### Quick start

To upload the code to the robot, run the following command:

```bash
poetry run spike-prime-connect upload ./src/main.py --slot 0 --start --read
```

This will upload the code to the slot 0 on the robot. If you want to upload the code to a different slot, change the `0` to the desired slot number.

> [!TIP]  
> If you use VSCode, you can press `F5` to run this command automatically. If you are bothered by the Debug Menu opening every time, you can install the "F5 Anything" plugin and use `Crtl + F5` to run.

### Generating the code

> [!WARNING]
> Outdated

If you don't want to upload the code automatically, you can run the following command to generate the code and save it to a file:

```bash
poetry run python ./tools/spike_prime_compyne.py ./src/main.py 0 > ./main.cpyd.py
```

This will generate the code and save it to a file called `main.cpyd.py`. You can then copy the contents of this file and inspect or upload it manually.

## How to use

### Defining runs

Add a file in the "runs" folder. The order of appereance in the menu is alphabetically by the filename.

The file should look like this:

```python
from gsgr.enums import Color
from gsgr.run import run

display_as = 1
color = Color.RED

def run():
    print(1)

```

The code in the `run` function is executed when the run is selected.
The variables `display_as` and `color` represent the symbol to show and the color to light the button with, respectively.
To add special config values to a run, you can additionally use the `config` variable like this:

```python
from gsgr.enums import Color
from gsgr.configuration import config

config_override = config(p_correction=1000)  # Make the robot dance
display_as = 1
color = Color.RED

def run():
    print(1)

```

[WIP]

To build docs:

```bash
poetry install --with dev
poetry run make html
```
