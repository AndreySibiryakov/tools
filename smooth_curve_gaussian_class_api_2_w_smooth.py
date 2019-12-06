import scipy.ndimage as sp
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import numpy as np
import scipy.interpolate as si


def bspline(cv, n=100, degree=3, periodic=False):
    """ Calculate n samples on a bspline

        cv :      Array ov control vertices
        n  :      Number of samples to return
        degree:   Curve degree
        periodic: True - Curve is closed
                  False - Curve is open
    """

    # If periodic, extend the point array by count+degree+1
    cv = np.asarray(cv)
    count = len(cv)

    if periodic:
        factor, fraction = divmod(count + degree + 1, count)
        cv = np.concatenate((cv,) * factor + (cv[:fraction],))
        count = len(cv)
        degree = np.clip(degree, 1, degree)

    # If opened, prevent degree from exceeding count-1
    else:
        degree = np.clip(degree, 1, count - 1)

    # Calculate knot vector
    kv = None
    if periodic:
        kv = np.arange(0 - degree, count + degree + degree - 1)
    else:
        kv = np.clip(np.arange(count + degree + 1) - degree, 0, count - degree)

    # Calculate query range
    u = np.linspace(periodic, (count - degree), n)

    # Calculate result
    return np.array(si.splev(u, (kv, cv.T, degree))).T


class Gaussian(object):
    def __init__(self, blend=10):
        self.blend = blend
        self.curves = []
        self.frame_data = {}
        self.value_data = {}
        self.id_data = {}

    def normalize_value(self, v, min_v, max_v):
        '''Normalizes single curve value.
        Used for processing "Stress" internal facefx curve.

        Args:
            v (float): curve value
            min_v (float): minimum value
            max_v (float): maximum value

        Returns:
            float: 
        '''
        # range2 = y - x;
        # a = (a * range2) + x;
        return (v - min_v) / (max_v - min_v)

    def normalize_data(self, data):
        min_v = min(data) if min(data) > 0 else 0
        max_v = max(data)
        return [self.normalize_value(d, min_v, max_v) for d in data]

    def restore_normalized_value(self, v, min_v, max_v):
        return min_v + v * (max_v - min_v)

    def restore_normalized_data(self, src_data, norm_data):
        min_v = min(src_data) if min(src_data) > 0 else 0
        max_v = max(src_data)
        return [self.restore_normalized_value(d, min_v, max_v) for d in norm_data]

    def add_keys(self, plugName, times, values, changeCache=None):
        # Get the plug to be animated.
        sel = om.MSelectionList()
        sel.add(plugName)
        plug = om.MPlug()
        sel.getPlug(0, plug)
        # Create the animCurve.
        animfn = oma.MFnAnimCurve(plug)
        timeArray = om.MTimeArray()
        valueArray = om.MDoubleArray()

        for i in range(len(times)):
            timeArray.append(om.MTime(times[i], om.MTime.uiUnit()))
            valueArray.append(values[i])
        # Add the keys to the animCurve.
        animfn.addKeys(
            timeArray,
            valueArray,
            oma.MFnAnimCurve.kTangentGlobal,
            oma.MFnAnimCurve.kTangentGlobal,
            False,
            changeCache
        )

    def delete_node(self, node):
        try:
            cmds.delete(cmds.listConnections(node)[0])
        except:
            return

    def calc_blend_val(self, orig_val, proc_val, multi):
        diff_val = (orig_val - proc_val) * multi
        return orig_val - diff_val

    def set_blend(self, init_values, filt_values):
        # Keeps blend length revelant to list length
        if len(init_values) / 2 < self.blend:
            self.blend = len(init_values) / 2

        gradient_range = [p / float(self.blend)
                          for p in range(0, self.blend)][1:]

        for i, multi in enumerate(gradient_range):
            rev_i = -(i + 1)
            filt_values[i] = self.calc_blend_val(
                init_values[i], filt_values[i], multi)
            filt_values[rev_i] = self.calc_blend_val(
                init_values[rev_i], filt_values[rev_i], multi)

        return filt_values

    def group_by_increasing(data):
        res = [[data[0]]]

        for i in range(1, len(data)):

            if data[i - 1] + 1 == data[i]:
                res[-1].append(data[i])

            else:
                res.append([data[i]])

        return res

    def get_data(self):
        self.curves = cmds.keyframe(query=True, name=True)

        for curve in self.curves:
            frame_data = cmds.keyframe(curve, sl=True, query=True)
            if not frame_data:
                frame_data = cmds.keyframe(curve, query=True)
            self.frame_data[curve] = frame_data

            value_data = cmds.keyframe(
                curve, sl=True, valueChange=True, query=True)
            if not value_data:
                value_data = cmds.keyframe(
                    curve, valueChange=True, query=True)
            self.value_data[curve] = value_data

        # Resets slider value to default
        cmds.floatSlider(power_sl, v=0, edit=True)

    def process_curve(self):
        # self.get_data()
        power = cmds.floatSlider(power_sl, value=True, query=True)
        # Reverses the input range, as soon it is not possible to do in gui

        for curve in self.curves:

            if cmds.checkBox(b_spline, v=True, q=True):
                filtered_values = bspline(self.value_data[curve], n=len(
                    self.value_data[curve]), degree=int(power))
            else:
                filtered_values = self.gaussian(self.value_data[curve], power)
                filtered_values = [float(v) for v in filtered_values]
                filtered_values = self.set_blend(
                    self.value_data[curve], filtered_values)

            if cmds.checkBox(cbx, v=True, q=True):
                filtered_values = self.normalize_data(filtered_values)
                filtered_values = self.restore_normalized_data(
                    self.value_data[curve], filtered_values)

            attr = cmds.listConnections(curve, p=True)[0]
            self.add_keys(attr, self.frame_data[curve], filtered_values, None)
            cmds.keyTangent(itt='auto', ott='auto')

    def normalize_only(self):
        self.get_data()
        # Reverses the input range, as soon it is not possible to do in gui

        for curve in self.curves:
            filtered_values = self.normalize_data(self.value_data[curve])
            attr = cmds.listConnections(curve, p=True)[0]
            self.add_keys(attr, self.frame_data[curve], filtered_values, None)
            cmds.keyTangent(itt='auto', ott='auto')

    def gaussian(self, data, power):
        return sp.filters.gaussian_filter1d(data, power)


window_name = 'Gaussian'
if cmds.window(window_name, exists=True):
    cmds.deleteUI(window_name)
cmds.window(window_name)
column = cmds.columnLayout(adjustableColumn=True)
# cmds.label('Power')
# text = cmds.text(label='Size', h=30)
cbx = cmds.checkBox(label='Normalize',
                    value=False,
                    ann='Normalyze curves or not')
b_spline = cmds.checkBox(label='B-spline',
                         value=False,
                         ann='Simplify curve with B-spline')
power_sl = cmds.floatSlider(
    min=0, max=20, step=1, w=250, h=30)
cmds.button(label='Normalize Only',
            command='gg.normalize_only()')
gg = Gaussian()
cmds.floatSlider(power_sl, dc='gg.process_curve()',
                 dragCallback='gg.get_data()', edit=True)
cmds.showWindow()
