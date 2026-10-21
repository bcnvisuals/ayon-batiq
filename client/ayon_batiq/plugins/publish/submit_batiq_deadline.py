"""Send a BATIQ Write to Deadline when its render target is *Farm rendering*.

The Deadline add-on stays host-agnostic: this plugin subclasses its
``AbstractSubmitDeadline``, and its own collectors and *Submit Publish Job* do
the rest (job info from ``deadline/publish/CollectJobInfo`` profiles, then a
publish job that waits for the render). The farm job uses the Deadline plugin
named in ``batiq/publish/SubmitBatiqDeadline`` (default ``BATIQ``), which takes
``ProjectFile`` and ``WriteNode`` and renders that Write to its own path.
"""
import pyblish.api

# Import the module, not the class: pyblish collects every plugin class in this
# module's namespace and would try to run the abstract base too.
try:
    from ayon_deadline import abstract_submit_deadline
except ImportError:  # no Deadline add-on: Validate Farm Rendering reports it
    abstract_submit_deadline = None

if abstract_submit_deadline is not None:

    class SubmitBatiqDeadline(abstract_submit_deadline.AbstractSubmitDeadline):
        label = "Submit BATIQ to Deadline"
        hosts = ["batiq"]
        families = ["render", "prerender", "image"]
        targets = ["local"]
        # After Integrate, as Nuke's: the farm renders the published workfile, which
        # must exist by then.
        order = pyblish.api.IntegratorOrder + 0.1
        settings_category = "batiq"

        # Overridden by batiq/publish/SubmitBatiqDeadline settings.
        deadline_plugin = "BATIQ"

        def process(self, instance):
            if not instance.data.get("farm"):
                self.log.debug("Not a farm render, skipping Deadline submission.")
                return
            super().process(instance)

        def get_job_info(self, job_info=None, **kwargs):
            data = self._instance.data
            job_info.Plugin = self.deadline_plugin
            # A custom range from the Publisher is already in Frames.
            if not job_info.Frames:
                job_info.Frames = f"{int(data['frameStartHandle'])}-{int(data['frameEndHandle'])}"
            return job_info

        def get_plugin_info(self, **kwargs):
            return {
                "ProjectFile": self.scene_path,
                # The id, not the name: names can repeat, the id cannot.
                "WriteNode": str(self._instance.data["writeNodeId"]),
            }
