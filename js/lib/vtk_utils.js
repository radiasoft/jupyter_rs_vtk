

// Load the rendering pieces we want to use (for both WebGL and WebGPU)
import '@kitware/vtk.js/Rendering/Profiles/Geometry';

import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkCubeSource from '@kitware/vtk.js/Filters/Sources/CubeSource';
import vtkCylinderSource from '@kitware/vtk.js/Filters/Sources/CylinderSource';
import vtkDataArray from '@kitware/vtk.js/Common/Core/DataArray';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkPolyData from '@kitware/vtk.js/Common/DataModel/PolyData';

import * as rsUtils from './rs_utils';

export const GEOM_TYPE_LINES = 'lines';
export const GEOM_TYPE_POLYS = 'polygons';
export const GEOM_TYPE_VECTS = 'vectors';
export const GEOM_OBJ_TYPES = [GEOM_TYPE_LINES, GEOM_TYPE_POLYS];
export const GEOM_TYPES = [GEOM_TYPE_LINES, GEOM_TYPE_POLYS, GEOM_TYPE_VECTS];

function pickPoint(customFn) {


    customFn();
}

export function getTestBox() {
    let s = vtkCubeSource.newInstance({
        xLength: 20, yLength: 20, zLength: 20,
        center: [0, 0, 0],
    });
    let m = vtkMapper.newInstance({
        static: true,
    });
    m.setInputConnection(s.getOutputPort());
    let a = vtkActor.newInstance({
        mapper: m,
    });
    a.getProperty().setColor(0, 1, 0);
    a.getProperty().setEdgeVisibility(true);
    return a;
}

export function getTestCylinder() {
    let s = vtkCylinderSource.newInstance({
        radius: 5, height: 30, center: [20, 0, 0]
    });
    let m = vtkMapper.newInstance({
        static: true,
    });
    m.setInputConnection(s.getOutputPort());
    let a = vtkActor.newInstance({
        mapper: m
    });
    a.getProperty().setColor(1, 0, 0);
    a.getProperty().setEdgeVisibility(true);
    return a;
}

export function objBounds(json) {

    let mins = [Number.MAX_VALUE, Number.MAX_VALUE, Number.MAX_VALUE];
    let maxs = [-Number.MAX_VALUE, -Number.MAX_VALUE, -Number.MAX_VALUE];

    GEOM_TYPES.forEach(function (type) {
        if (! json[type]) {
            return;
        }
        let pts = json[type].vertices;
        // for performance purposes, simple loops and ifs
        for (let i = 0; i < pts.length; i += 3) {
            for (let j = 0; j < 3; ++j) {
                const p = pts[i + j]
                if (p < mins[j]) {
                    mins[j] = p;
                }
                if (p > maxs[j]) {
                    maxs[j] = p;
                }
            }
        }
    });
    return [mins[0], maxs[0], mins[1], maxs[1], mins[2], maxs[2]];
}

export function objToPolyData(json, includeTypes) {
    let colors = [];
    let points = [];
    let tData = {};

    if (! includeTypes || includeTypes.length === 0) {
        includeTypes = GEOM_TYPES;
    }

    const typeInfo = {};
    GEOM_TYPES.forEach(function (type, tIdx) {
        typeInfo[type] = {};
        if (includeTypes.indexOf(type) < 0) {
            return;
        }

        let t = json[type];
        if (! t || json[type].vertices.length === 0) {
            rsUtils.rsdbg('No data for requested type', type);
            return;
        }

        // may not always be colors in the data
        let c = t.colors || [];
        for (let i = 0; i < c.length; i++) {
            colors.push(Math.floor(255 * c[i]));
            if (i % 3 === 2) {
                colors.push(255);
            }
        }

        let tArr = [];
        let tOffset = points.length / 3;
        typeInfo[type].offset = tOffset;
        for (let i = 0; i < t.vertices.length; i++) {
            points.push(t.vertices[i]);
        }
        let tInd = 0;
        let tInds = rsUtils.indexArray(t.vertices.length / 3);
        for (let i = 0; i < t.lengths.length; i++) {
            let len = t.lengths[i];
            tArr.push(len);
            for (let j = 0; j < len; j++) {
                tArr.push(tInds[tInd++] + tOffset);
            }
        }
        if (tArr.length) {
            tData[type] = new window.Uint32Array(tArr);
        }

    });

    points = new window.Float32Array(points);

    let pd = vtkPolyData.newInstance();
    pd.getPoints().setData(points, 3);

    if (tData.lines) {
        pd.getLines().setData(tData.lines);
    }
    if (tData.polygons) {
        pd.getPolys().setData(tData.polygons, 1);
    }

    pd.getCellData().setScalars(vtkDataArray.newInstance({
        numberOfComponents: 4,
        values: colors,
        dataType: vtkDataArray.VtkDataTypes.UNSIGNED_CHAR
    }));

    pd.buildCells();

    return {data: pd, typeInfo: typeInfo};
}

function vectorsToPolyData(json) {
    let points = new window.Float32Array(json.vectors.vertices);
    let pd = vtkPolyData.newInstance();
    pd.getPoints().setData(points, 3);
    return pd;
}
