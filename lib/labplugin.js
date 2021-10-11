var plugin = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'jupyter_rs_vtk',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'jupyter_rs_vtk',
          version: plugin.version,
          exports: plugin
      });
  },
  autoStart: true
};
