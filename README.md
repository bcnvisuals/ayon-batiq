# AYON-BATIQ

AYON-BATIQ 0.1.13 is the separately installed AYON host add-on for BATIQ. It is
not bundled into BATIQ: without this add-on, BATIQ keeps its generic embedded
`import batiq` API and starts with no AYON menus, Qt process, or AYON imports.

## Package and install

Use Python 3.9 or newer from the repository root:

```sh
python create_package.py
```

This uses AYON's standard package workflow and writes the server-installable
archive under `package/`. In AYON Server, open **Studio Settings → Bundles →
Install addon**, choose that archive, then enable BATIQ 0.1.13 in a bundle.

The add-on requires AYON Server `>=1.8.4,<2.0.0`, AYON Core
`>=1.9.10-bcn.1` (including final `1.9.10` and newer), and
BATIQ with the embedded Python/project-format-v30 host API. In AYON's
Applications add-on, configure the BATIQ executable as a host application with
host name `batiq`; that host name is what scopes this add-on's launch
environment to BATIQ alone.

## Settings

`ayon+settings://batiq`:

- `workfile/apply_context_on_launch`: apply the task's frame range (with
  handles), fps, resolution and pixel aspect to a new unsaved project on launch.
- `colorspace/rules`: map BATIQ colorspaces to names in the project's OCIO
  config, overriding the built-in table (loading and publishing).
- `publish/ValidateBatiqContextSettings`: enabled / optional / active.
- `publish/SubmitBatiqDeadline`: farm rendering on or off, and the Deadline
  plugin farm jobs run (`deadline_plugin`, default `BATIQ`).
- `publish/ExtractReviewIntermediates`: review frames baked by BATIQ with its
  ACES 2.0 output transform (sRGB display, SDR 100 nits).

## Farm rendering

Render, Prerender and Image offer three render targets: *Local machine
rendering*, *Farm rendering* and *Use existing frames*. With *Farm rendering*
the Publisher sends the Write to Deadline and the Deadline add-on's publish
job publishes the frames once the render finishes. The Deadline add-on needs
no BATIQ code; it needs:

- A Deadline plugin that renders a BATIQ project: it receives `ProjectFile`
  (the published workfile, or the work file) and `WriteNode` (the Write's
  id), and renders that Write to its own path with `batiq-headless`. Its name
  is `publish/SubmitBatiqDeadline/deadline_plugin` (default `BATIQ`).
- A `deadline/publish/CollectJobInfo` profile matching host `batiq` (pool,
  group, chunk size). The 3D Set node needs a GPU worker with Vulkan.
- For a review: `deadline/publish/ProcessSubmittedJobOnFarm/aov_filter` with
  host `batiq` and pattern `.*`, and a core Extract Review profile for host
  `batiq`. Only PNG/JPEG Writes are reviewed on the farm: they are already
  display-referred. EXR farm renders publish without a review.

## Loading

- **Load Image or Movie** makes a Read: EXR, PNG, JPEG and movies, with the
  version's frame range and handles and its colorspace mapped to BATIQ's.
- **Load USD into Set** makes a Set (BATIQ's 3D scene node) referencing the
  published USD (`.usd`, `.usda`, `.usdc`, `.usdz`) or Alembic file, as Nuke's
  GeoReference loader does. Like Nuke's USD loaders it takes any product type.
  The Set renders through the scene's first camera unless another is picked.
  A version update swaps the file it loaded, wherever it sits in the Set's
  list, and keeps any other files and the artist's edits to the file's prims.
  The Set reads the file at the project frame (BATIQ has no offset for it), so
  the version's frame range and fps are only recorded on the container.

## Review

As in the Nuke add-on, the host bakes the review source and core **Extract
Review** encodes it. The core settings need an Extract Review profile with host
`batiq` and product base type `render`, for example an H.264 output tagged
`burnin` and `ftrackreview`. Leave out `-apply_trc gamma22` (used in Nuke's
EXR-based profile): BATIQ's review frames are already display-referred.

See `CHANGELOG.md` for what changed in each version.

## Tests

The tests run against a checked-out AYON Core client and the AYON dependency
package on `PYTHONPATH`:

```sh
PYTHONPATH=.:client:<ayon-core>/client:<dependencies> python -m pytest tests
```

## Development mode

1. Run `python create_package.py` once and install the generated ZIP on AYON Server.
2. Add and enable BATIQ 0.1.13 in a development bundle.
3. Enable the add-on custom path and point its client path at `<path-to-ayon-batiq>/client`.
4. Start AYON Launcher with that development bundle (or `--use-dev`).
5. Launch the configured BATIQ application.

For production bundles, configure the BATIQ application executable for each
platform in the Applications add-on, keep its host name set to `batiq`, and
launch it with an AYON project, folder, and task selected.

When AYON launches BATIQ, this add-on appends its client directory to
`BATIQ_PYTHONPATH` and `ayon_batiq.startup.bootstrap` to
`BATIQ_STARTUP_MODULES`. Startup is Qt-free; it starts an authenticated
localhost bridge and native BATIQ AYON menu. Selecting a menu starts one
persistent AYON Qt helper through `AYON_EXECUTABLE` and `ayon addon batiq
ui-helper`. The session token is only the first JSON line on stdin, never an
argument.
