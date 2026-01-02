from ._version import NPM_PACKAGE_RANGE
from jupyter_rs_vtk import gui_utils
from pykern.pkcollections import PKDict
from traitlets import Bool, Dict, Float, Unicode
import ipywidgets
import traitlets


@ipywidgets.register
class VTK(ipywidgets.DOMWidget):
    """VTK content"""

    _view_name = Unicode("VTKView").tag(sync=True)
    _model_name = Unicode("VTKModel").tag(sync=True)
    _view_module = Unicode("jupyter_rs_vtk").tag(sync=True)
    _model_module = Unicode("jupyter_rs_vtk").tag(sync=True)
    _view_module_version = Unicode(NPM_PACKAGE_RANGE).tag(sync=True)
    _model_module_version = Unicode(NPM_PACKAGE_RANGE).tag(sync=True)

    actor_state = Dict(default_value={}).tag(sync=True)
    bg_color = ipywidgets.Color("#ffffff").tag(sync=True)
    cam_state = Dict(default_value={}).tag(sync=True)
    model_data = Dict(default_value={}).tag(sync=True)
    poly_alpha = Float(1.0).tag(sync=True)
    selected_obj_color = ipywidgets.Color("#ffffff").tag(sync=True)
    show_edges = Bool(True).tag(sync=True)
    show_marker = Bool(True).tag(sync=True)
    title = Unicode("").tag(sync=True)
    vector_color_map_name = Unicode("").tag(sync=True)

    def rsdbg(self, msg):
        # send a message to the front end to print to js console
        self.send({"type": "debug", "msg": "KERNEL: " + msg})

    def refresh(self):
        self.send({"type": "refresh"})

    def set_data(self, d):
        self.model_data = d
        self.refresh()

    def set_title(self, t):
        self.title = t

    @traitlets.default("layout")
    def _default_layout(self):
        return ipywidgets.Layout(width="50%", min_width="25%", margin="auto")

    def __init__(self, title="", bg_color="#ffffff", data=None):
        self.model_data = {} if data is None else data
        self.title = title
        self.bg_color = bg_color
        # super(VTK, self).__init__()
        super().__init__()


# Note we need to subclass VBox in the javascript as well
@ipywidgets.register
class Viewer(ipywidgets.VBox):
    """VTK viewer - includes controls to manipulate the objects"""

    _model_name = Unicode("ViewerModel").tag(sync=True)
    _view_name = Unicode("ViewerView").tag(sync=True)
    _model_module = Unicode("jupyter_rs_vtk").tag(sync=True)
    _view_module = Unicode("jupyter_rs_vtk").tag(sync=True)
    _model_module_version = Unicode(NPM_PACKAGE_RANGE).tag(sync=True)
    _view_module_version = Unicode(NPM_PACKAGE_RANGE).tag(sync=True)

    _axes = ["X", "Y", "Z"]
    # "into the screen", "out of the screen"
    _dirs = ["\u2299", "\u29bb"]

    client_props = Dict(default_value={}).tag(sync=True)
    client_prop_map = PKDict()

    def rsdbg(self, msg):
        # send a message to the front end to print to js console
        self.send({"type": "debug", "msg": "KERNEL: " + msg})

    # add data param
    def display(self):
        return self

    def refresh(self):
        # self.content.send({'type': 'refresh'})
        self.content.refresh()

    def set_data(self, data):
        # keep a local reference to the data for handlers
        # self.rsdbg("vtk setting data {}".format(data))
        # self.rsdbg("vtk setting data")
        self.model_data = data
        self.content.set_data(self.model_data)
        self._update_layout()

    # several test modes?  polyData, built-in vtk sources, etc.
    def test(self):
        self.set_data(gui_utils.get_test_obj())

    @traitlets.default("layout")
    def _default_layout(self):
        return ipywidgets.Layout(align_self="stretch")

    def _handle_change(self, change):
        self.rsdbg("{}".format(change))

    def _has_data_type(self, d_type):
        if self.model_data is None or "data" not in self.model_data:
            return False
        return gui_utils.any_obj_has_data_type(self.model_data["data"], d_type)

    # send message to content to reset camera to default position
    def _reset_view(self, b):
        # this turns into an event of type "msg:custom" with the dict attached
        # in the view add this.listenTo(this.model, "msg:custom", <handler>)
        for axis in Viewer._axes:
            self.axis_btns[axis].dir = 1
            self._set_axis_btn_desc(axis)

        self.content.send({"type": "reset"})

    # send message to vtk widget to rotate scene with the given axis pointing in or out
    # of the screen
    def _set_axis(self, b):
        a = b.description[0]
        # maps (0, 1) to (-1, 1)
        d = 1 - 2 * Viewer._dirs.index(b.description[1])
        self.content.send({"type": "axis", "axis": a, "dir": d})
        self.axis_btns[a].dir = -1 * d
        self._set_axis_btn_desc(a)

    def _set_axis_btn_desc(self, axis):
        d = self.axis_btns[axis].dir
        # maps (-1, 1) to (0, 1)
        self.axis_btns[axis].button.description = axis + Viewer._dirs[int((1 - d) / 2)]

    def _set_client_props(self, d):
        self.client_props = d["new"]
        for pn in self.client_prop_map:
            p = self.client_prop_map[pn]
            setattr(getattr(self, p["obj"]), p["attr"], self.client_props[pn])

    def _update_layout(self):
        self.poly_alpha_grp.layout.display = (
            None if self._has_data_type(gui_utils.GEOM_TYPE_POLYS) else "none"
        )
        self.obj_color_pick_grp.layout.display = (
            None if self._has_data_type(gui_utils.GEOM_TYPE_POLYS) else "none"
        )

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.model_data = data

        # don't initialize VTK with data - save until the view is ready
        self.content = VTK()

        self.reset_btn = ipywidgets.Button(
            description="Reset Camera", layout={"width": "fit-content"}
        )
        self.reset_btn.on_click(self._reset_view)

        self.axis_btns = PKDict()
        for axis in Viewer._axes:
            self.axis_btns[axis] = PKDict(
                button=ipywidgets.Button(layout={"width": "fit-content"}), dir=1
            )
            self._set_axis_btn_desc(axis)
            self.axis_btns[axis].button.on_click(self._set_axis)

        self.orientation_toggle = ipywidgets.Checkbox(
            value=False, description="Show marker"
        )
        self.edge_toggle = ipywidgets.Checkbox(value=True, description="Show edges")

        axis_btn_grp = ipywidgets.HBox(
            [self.axis_btns[a]["button"] for a in self.axis_btns],
            layout={"justify-content": "flex-end"},
        )

        # default layout has fixed width which takes up too much space
        self.bg_color_pick = ipywidgets.ColorPicker(
            concise=True, layout={"width": "max-content"}, value=self.content.bg_color
        )
        # separate label to avoid text truncation
        bg_color_pick_grp = ipywidgets.HBox(
            [ipywidgets.Label("Background color"), self.bg_color_pick]
        )

        self.obj_color_pick = ipywidgets.ColorPicker(
            concise=True,
            layout={"width": "max-content"},
            value=self.content.selected_obj_color,
        )
        self.obj_color_pick_grp = ipywidgets.HBox(
            [ipywidgets.Label("Object color"), self.obj_color_pick]
        )

        self.poly_alpha_slider = ipywidgets.FloatSlider(
            min=0.0, max=1.0, step=0.05, value=self.content.poly_alpha
        )
        self.poly_alpha_grp = ipywidgets.HBox(
            [ipywidgets.Label("Surface Alpha"), self.poly_alpha_slider]
        )

        view_props_grp = ipywidgets.HBox(
            [
                bg_color_pick_grp,
                self.obj_color_pick_grp,
                self.poly_alpha_grp,
                self.edge_toggle,
            ],
            layout={"padding": "3px 0px 3px 0px"},
        )

        # links the values of two widgets
        ipywidgets.jslink((self.bg_color_pick, "value"), (self.content, "bg_color"))

        ipywidgets.jslink(
            (self.obj_color_pick, "value"), (self.content, "selected_obj_color")
        )

        ipywidgets.jslink((self.edge_toggle, "value"), (self.content, "show_edges"))

        ipywidgets.jslink(
            (self.orientation_toggle, "value"), (self.content, "show_marker")
        )

        ipywidgets.jslink(
            (self.poly_alpha_slider, "value"), (self.content, "poly_alpha")
        )

        view_cam_grp = ipywidgets.HBox(
            [self.reset_btn, axis_btn_grp, self.orientation_toggle],
            layout={"padding": "3px 0px 3px 0px"},
        )

        controls_grp = ipywidgets.VBox(
            [view_cam_grp, view_props_grp], layout={"padding": "8px 4px 8px 4px"}
        )

        # for enabling/disabling as a whole
        self.controls = [
            self.bg_color_pick,
            self.obj_color_pick,
            self.poly_alpha_slider,
            self.reset_btn,
        ].extend([self.axis_btns[ax].button for ax in self.axis_btns])

        self.observe(self._set_client_props, names="client_props")
        self.set_data(self.model_data)
        super(Viewer, self).__init__(
            children=[
                self.content,
                controls_grp,
            ]
        )
