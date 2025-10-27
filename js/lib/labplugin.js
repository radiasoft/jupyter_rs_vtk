import {VTKModel, VTKView, ViewerModel, ViewerView, version} from './index';
import {IJupyterWidgetRegistry} from '@jupyter-widgets/base';

export const vtkWidgetPlugin = {
  id: 'jupyter_rs_vtk:plugin',
  requires: [IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'jupyter_rs_vtk',
          version: version,
          exports: { VTKModel, VTKView, ViewerModel, ViewerView }
      });
  },
  autoStart: true
};

export default vtkWidgetPlugin;
