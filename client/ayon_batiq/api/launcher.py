"""Which BATIQ executable headless renders run."""
from __future__ import annotations

import os
from typing import Mapping


def render_launcher(template: str | None, fallback: str | None, env: Mapping[str, str] | None = None) -> str | None:
    """The studio rez package's launcher when it exists, else ``fallback``.

    ``template`` may use ``{rez_root}`` and ``{version}``: the rez ``batiq``
    package BATIQ was launched from (``REZ_BATIQ_ROOT`` / ``REZ_BATIQ_VERSION``,
    inherited by the publish helper). That launcher unpacks BATIQ into the
    user's runtime on first use, so it also works on machines that never ran
    BATIQ; the running app's own executable only exists where it runs. The
    app's version is no use here: BATIQ's updater moves a runtime to newer
    releases in place, so it can differ from the package version.
    """
    env = os.environ if env is None else env
    keys = {"rez_root": env.get("REZ_BATIQ_ROOT", ""), "version": env.get("REZ_BATIQ_VERSION", "")}
    if template:
        try:
            path = template.format(**keys)
        except (KeyError, IndexError, ValueError):
            path = ""
        needed = [key for key in keys if "{" + key + "}" in template]
        if path and all(keys[key] for key in needed) and os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return fallback
