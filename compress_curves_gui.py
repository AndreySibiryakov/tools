import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma


class Compressor(object):
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

    def blend_normalized(self, data, blend):

        return [(norm - src) * blend + src for src, norm in zip(data, self.normalize_data(data))]

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
        cmds.floatSliderGrp(compr_slider, v=1, edit=True)
        cmds.floatSliderGrp(blend_slider, v=0, edit=True)

    def find_peaks(self, data):
        peak_id = []

        for i, d in enumerate(data):

            if i == 0 or i == len(data) - 1:
                continue

            elif data[i - 1] < d > data[i + 1]:
                peak_id.append(i)

        return peak_id

    def get_peak_chains(self, peaks, data):
        chains = []

        for peak in peaks:

            chain = []
            current_i = peak

            for i in range(len(data)):

                if 0 > current_i - 1 > len(data) - 1:
                    break

                if data[current_i - 1] < data[current_i]:
                    chain.append(current_i - 1)
                    current_i = current_i - 1

            current_i = peak

            for i in range(len(data)):
                if 0 > current_i + 1 > len(data) - 1:
                    break

                if data[current_i + 1] < data[current_i]:
                    chain.append(current_i + 1)
                    current_i = current_i + 1

            chains += sorted(chain + [peak])

        return list(set(chains))

    def compress(self, data, threshold, compr_value):
        comp_data = []

        for d in data:
            if d < threshold:
                comp_data.append(d)
                continue
            comp_d = (d - threshold) / compr_value + threshold
            comp_data.append(comp_d)

        return comp_data

    def filter_by_threshold(self, chains, src_data, proc_data):
        filtered = []

        for i, src in enumerate(src_data):
            if i in chains:
                filtered.append(proc_data[i])
            else:
                filtered.append(src_data[i])

        return filtered

    def process_curve(self):
        # self.get_data()
        threshold = cmds.floatSliderGrp(thres_slider, value=True, query=True)
        compr_value = cmds.floatSliderGrp(
            compr_slider, value=True, query=True)
        blend_value = cmds.floatSliderGrp(blend_slider, value=True, query=True)
        # Reverses the input range, as soon it is not possible to do in gui

        for curve in self.curves:
            data = self.value_data[curve]
            peaks = self.find_peaks(data)
            thres_peaks = [i for i in peaks if data[i] > threshold]
            peak_chains = self.get_peak_chains(thres_peaks, data)
            # Compressing soruce data
            filtered_values = self.compress(
                self.value_data[curve], 0, compr_value)
            # Extracting data by threshold
            filtered_values = self.filter_by_threshold(
                peak_chains, data, filtered_values)
            # Normalizing data
            filtered_values = self.blend_normalized(
                filtered_values, blend_value)

            attr = cmds.listConnections(curve, p=True)[0]
            self.add_keys(attr, self.frame_data[curve], filtered_values, None)
            cmds.keyTangent(itt='auto', ott='auto')


window_name = 'Compress Curve'
if cmds.window(window_name, exists=True):
    cmds.deleteUI(window_name)
cmds.window(window_name)
column = cmds.columnLayout(adjustableColumn=True)
cmds.text(label='Threshold', h=30)
thres_slider = cmds.floatSliderGrp(
    field=True, minValue=0, maxValue=1, fieldMinValue=0, fieldMaxValue=1, value=0.2)
cmds.text(label='Compressor', h=30)
compr_slider = cmds.floatSliderGrp(
    field=True, minValue=1, maxValue=10, fieldMinValue=1, fieldMaxValue=10, value=1)
cmds.text(label='Normalize', h=30)
blend_slider = cmds.floatSliderGrp(
    field=True, minValue=0, maxValue=1, fieldMinValue=0, fieldMaxValue=1, value=0)
ff = Compressor()
cmds.floatSliderGrp(thres_slider, dc='ff.process_curve()',
                    dragCallback='ff.get_data()', edit=True)
cmds.floatSliderGrp(compr_slider, dc='ff.process_curve()',
                    dragCallback='ff.get_data()', edit=True)
cmds.floatSliderGrp(blend_slider, dc='ff.process_curve()',
                    dragCallback='ff.get_data()', edit=True)
cmds.showWindow()
