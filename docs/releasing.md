# Release and PyPI setup

The distribution is `integral-compass`; the import is `integral_compass`.
Repository/homepage: https://github.com/wyb20080315-cyber/integral-compass.

## One-time account setup

GitHub access does not grant access to PyPI. The PyPI account owner must sign in
and configure a pending trusted publisher for this new project at
https://pypi.org/manage/account/publishing/ . PyPI may require email verification
and two-factor authentication. Do not paste passwords or API tokens into chat.

Enter these exact values:

| Setting | Value |
| --- | --- |
| PyPI project name | `integral-compass` |
| Owner | `wyb20080315-cyber` |
| Repository | `integral-compass` |
| Workflow filename | `publish.yml` |
| Environment name | `pypi` |

Configure the GitHub repository's `pypi` environment as desired. The workflow uses
OIDC short-lived credentials; it does not need a long-lived PyPI token.
For an existing PyPI project, add this publisher from that project's Publishing settings.

## Publish a version

1. Ensure the version in `pyproject.toml`, `__init__.py` and the changelog agree.
2. Run tests, lint, `python -m build`, `python -m twine check dist/*`, and clean-wheel install.
3. Push the corresponding Git tag (e.g. `v0.1.0`). Tags must be reviewed release commits.
4. Run **Publish to PyPI** from GitHub Actions with `version_tag=v0.1.0`, or:

   ```bash
   gh workflow run publish.yml --ref main -f version_tag=v0.1.0
   ```

5. Inspect the workflow result, then verify the actual index page and fresh installation:

   ```bash
   python -m venv /tmp/compass-index-check
   /tmp/compass-index-check/bin/python -m pip install integral-compass==0.1.0
   /tmp/compass-index-check/bin/integral-compass 'x*exp(x)'
   ```

Only mark “published” after the upload and independent installation succeed.
The release workflow is manual, so ordinary development pushes do not publish packages.
PyPI versions are immutable; use a new version to replace an uploaded release.

References: [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/),
[pending publishers](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).
