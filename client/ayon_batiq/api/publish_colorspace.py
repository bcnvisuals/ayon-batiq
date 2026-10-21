"""The project's OCIO name for a BATIQ Write colorspace, for publishing."""
from __future__ import annotations

from ayon_core.pipeline.colorspace import (
    get_colorspace_settings_from_publish_context,
    get_ocio_config_colorspaces,
)

from ayon_batiq.colorspace import to_ocio


def ocio_colorspace(batiq_name, context, log):
    """The OCIO name for ``batiq_name`` in the publish context's config, or None."""
    if not batiq_name:
        return None
    config_data, _file_rules = get_colorspace_settings_from_publish_context(context.data)
    if not config_data:
        return None  # colour management is off for this project
    colorspaces = get_ocio_config_colorspaces(config_data["path"])["colorspaces"]
    rules = context.data["project_settings"].get("batiq", {}).get("colorspace", {}).get("rules")
    ocio_name = to_ocio(batiq_name, colorspaces, rules)
    if not ocio_name:
        log.warning(
            f"BATIQ colorspace {batiq_name!r} has no match in {config_data['path']}; add a rule"
            " under batiq/colorspace. The render is published without colorspace data."
        )
    return ocio_name
