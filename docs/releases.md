# How-To Release

A release can be done when a number of changes come together that are stable or there is a bugfix that needs to
be addressed.

The version number should follow best practices of [semantic versioning](https://semver.org/).

When it is decided to release and the `develop` branch should include all commits and merge requests that should be
released.  It is then merged into the main branch. On the main branch there are only two changes to make: Bump the
version in `setup.py` and `matrix_registration_bot/__init__.py` and commit this with `Bump version to v1.0.0`

Then create a git tag and push it to GitHub
```bash
git tag -a v1.0.0 -m "Releasing version v1.0.0"
git push origin v1.0.0
```
Afterwards you should mark the tag as release and include a changelog. Try to use a similar structure as previous
releases.

