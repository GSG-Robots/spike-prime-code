# competition-programs

The code OTTWO runs on in competitions.

Contributors:

* [GSG-Robots](https://github.com/GSG-Robots)
* [Meganton](https://github.com/Meganton)
* [J0J0HA](https://github.com/J0J0HA)
* [E-r-i-c-Gepard](https://github.com/E-r-i-c-Gepard)
* [FINNtastisch007](https://github.com/FINNtastisch007)

## How to use

To upload the code to the robot, you need to install the dependencies manually, which are listed in the `pyproject.toml` file.

If you have poetry, run the following command:

```bash
poetry install
```

### Quick start

To upload the code to the robot, run the following command:

```bash
poetry run python ./tools/upload.py ./src/main.py 0
```

This will upload the code to the slot 0 on the robot. If you want to upload the code to a different slot, change the `0` to the desired slot number.


### Generating the code

If you don't want to upload the code automatically, you can run the following command to generate the code and save it to a file:

```bash
poetry run python ./tools/spike_prime_compyne.py ./src/main.py 0 > ./main.cpyd.py
```

This will generate the code and save it to a file called `main.cpyd.py`. You can then copy the contents of this file and inspect or upload it manually.
