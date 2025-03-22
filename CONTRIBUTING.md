
`ipyautoui` uses [pixi](https://pixi.sh/v0.42.1/#installation) for package management and development. Once installed:

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
pixi run build
hatch publish -u __token__ -a <your-pypi-token>  # publishes to pypi
```
