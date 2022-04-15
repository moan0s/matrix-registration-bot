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

### Test docker image creation

Test the build of the docker file with the version from Test-PyPI, you can use the following `Dockerfile` and `docker build .`
```Dockerfile
FROM python:latest
MAINTAINER Julian-Samuel Gebühr

RUN apt-get update && apt-get install -y pip
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -i https://test.pypi.org/simple/ matrix-registration-bot
CMD ["matrix-registration-bot"]
```

## Release

Create a git tag and push it to GitHub
```bash
git tag -a v1.0.0 -m "Releasing version v1.0.0"
git push origin v1.0.0
```
Afterwards you should mark the tag as release and include a changelog. Try to use a similar structure as previous
releases.

## Upload to PyPi
```
$ python -m build
$ twine upload dist/* 
```

## Docker

```bash
docker build .
docker login
docker push moanos/matrix-registration-bot:latest
```
