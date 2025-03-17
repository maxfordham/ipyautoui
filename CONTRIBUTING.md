
`ipyautoui` uses [pixi]() for package management and development. To install `pixi`:

```sh
$ git clone https://github.com/maxfordham/ipyautoui
$ cd ipyautoui

# assuming that you have `pixi` installed:
$ pixi run tests

# view other pixi commands
$ pixi run list
```

## Packaging

```sh
#  NOTE: restricted to core-maintainers only
mamba create -n hatcher python hatch 
mamba activate hatcher # or conda env with hatch installed
hatch build  # builds to local folder
hatch publish -u __token__ -a <your-pypi-token>  # publishes to pypi
```
