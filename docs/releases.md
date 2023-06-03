# How-To Release


## General
A release can be done when a number of changes come together that are stable or there is a bugfix that needs to
be addressed.

The version number should follow best practices of [semantic versioning](https://semver.org/).

When it is decided to release and the `develop` branch should include all commits and merge requests that should be
released. Create the `README.rst` (for PyPi) with `pandoc --from=markdown --to=rst --output=README.rst README.md `. 
Commit and then merge into the main branch. On the main branch there are only two changes to make: Bump the
version in `matrix_registration_bot/__init__.py` and commit this with `Bump version to v1.0.0`

## Test a release

### Build

```bash
python -m build
```

### Test & Upload to Test-PyPI

```bash
twine check dist/*
twine upload -r testpypi dist/*
```


## Release

Create a git tag and push it to GitHub

```bash
git tag -a v1.0.0 -m "Releasing version v1.0.0"
git push origin v1.0.0
```
Afterward, you should mark the tag as release and include a changelog. Try to use a similar structure as previous
releases.

## Upload to PyPi

```bash
$ python -m build
$ twine upload dist/* 
```

## Docker

First build the latest docker version and test it.
```bash
docker build . --tag moanos/matrix-registration-bot:latest
docker run -e "CONFIG_PATH=/config/config.yml" --mount type=bind,src=./config.yml,dst=/config/config.yml,ro moanos/matrix-registration-bot:latest
```

If that looks good you can tag it with the appropriate docker version. Docker versions should follow the versioning
of `<package-version>-0` where 0 ist the docker iteration and is increased by one for each docker build of the same
package version. This helps if the package is okay but the docker build has an error.

Publish the image with
```bash
docker login
docker push moanos/matrix-registration-bot:1.2.2-0
```
and don't forget to update [spantaleev/matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/ddbbd42718b15172cdf409f2c1050362d42c3151/roles/custom/matrix-bot-matrix-registration-bot/defaults/main.yml#L11).
