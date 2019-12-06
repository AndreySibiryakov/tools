'''
Animation data structure
group
    anim
        curve
            frame:value
'''

from FxStudio import *
from FxAnimation import *
# import AnalysisTextPreprocessor
# reload(AnalysisTextPreprocessor)
import os
from shutil import copyfile
import datetime


class ProcFaceGraph(object):

    def __init__(self):
        self.fx_path = ''
        # {animset_name:animset_path}
        self.fx_dir = ''
        self.cmds_path = 'u:/face/facefx/facefx_path.txt'
        self.target_dir = 'c:/SVN/content/facefx/chrs/'
        self.proc_data = {}
        self.pc = '_PC'
        self.publ_ext = '.facefx_ingame'
        self.failed_command = False
        self.print_log = 'Commands applied:\n' + fx_command + '\n\n'
        self.log_dir = 'u:/face/logs/'
        # self.not_copied = ''

    def set_console_vars(self):
        issueCommand('set -n "po_bake_events_to_curves" -v "0";')
        issueCommand('set -n "po_collapse_face_graph" -v "0";')
        issueCommand('set -n "po_remove_anim_editor_only_data " -v "1";')
        issueCommand('set -n "po_remove_phon_word_lists " -v "1";')
        issueCommand('set -n "po_remove_mapping" -v "1";')
        issueCommand('set -n "po_destination_dir" -v "%s";' % self.fx_dir)
        # For silent, no popups mode
        issueCommand('set -n "g_unattended" -v "1";')

    def load_actor(self):
        issueCommand('loadActor -file "%s"' % self.fx_path)

    def save_actor(self):
        issueCommand('saveActor -file "%s"' % self.fx_path)

    def publish_actor_go(self):
        issueCommand('publish -go;')

    def read_cmds(self):
        data = []

        with open(self.cmds_path) as g:
            for l in g:
                line = l.strip().split("\t")
                if len(line) > 1:
                    data.append(line)

        return data

    def proc_cmds(self):
        data = self.read_cmds()
        # d[0] chr name
        # d[1] path to .facefx

        for d in data:
            if self.proc_data.get(d[1]):
                self.proc_data[d[1]] += [d[0]]
            elif os.path.exists(d[1]):
                self.proc_data[d[1]] = [d[0]]
            else:
                print '# Path not exists', d[1]

    def copy(self, names):
        for name in names:
            base_name = os.path.basename(self.fx_path).split('.')[0]
            source_publ_path = os.path.join(
                self.fx_dir, base_name + self.pc + self.publ_ext)
            target_publ_path = os.path.join(
                self.target_dir, name + self.publ_ext)
            if os.path.exists(source_publ_path):
                copyfile(source_publ_path, target_publ_path)
                # self.print_log += 'Copied published file to ' + target_publ_path + '\n'
            else:
                print '# Published path not exists', source_publ_path
                continue

    def exec_command(self):

        for c in fx_command.split('\n'):
            if len(c) == 0:
                continue

            # Failed facefx commands return False
            # an True on success
            if not issueCommand('%s' % c):
                self.failed_command = True

    def proc_facefx(self):
        self.proc_cmds()

        for path, names in self.proc_data.iteritems():
            self.failed_command = False
            self.fx_path = path
            self.fx_dir = os.path.dirname(path)
            self.load_actor()
            self.set_console_vars()
            self.exec_command()
            if self.failed_command:
                print '# Not saving file due to errors.'
                self.print_log += 'Skipped ' + path + '\n'
                continue
            self.publish_actor_go()
            self.save_actor()
            self.print_log += 'Saved ' + path + '\n'
            self.copy(names)

        print self.print_log
        self.write_log()

    def write_log(self):
        now = datetime.datetime.now()
        log_name = now.strftime("%Y%m%d_%H-%M")
        log_path = os.path.join(
            self.log_dir, log_name + '_facegraph_update.log')
        with open(log_path, 'w+') as fx:
            fx.write(self.print_log)


fx_command = '''graph -editlink -from "surprise_up_suppressor" -to "surprise_up" -linkfn "corrective" -linkfnparams "Correction Factor=0.000000";
graph -editlink -from "Wonder" -to "surprise_eye_r" -linkfn "linear" -linkfnparams "m=0.5|b=0.000000";
graph -editlink -from "Wonder" -to "surprise_eye_l" -linkfn "linear" -linkfnparams "m=0.5|b=0.000000";
'''

pf = ProcFaceGraph()
pf.proc_facefx()

'''
Used fx commands log:

# Fixs sleep command
graph -addnode -nodetype "FxCombinerNode" -name "sleep" -nodex 9844 -nodey -5650;
graph -link -from "sleep" -to "Blink" -linkfn "linear";

# Fixs missing link for fear emotion
graph -link -from "fear_low_elements" -to "fear_jaw_L" -linkfn "linear";

# Decreases W, U pronounce
graph -editlink -from "phoneme_U" -to "phoneme_U_elements" -linkfn "linear" -linkfnparams "m=0.3|b=0.000000";
graph -editlink -from "phoneme_W" -to "phoneme_W_elements" -linkfn "linear" -linkfnparams "m=0.3|b=0.000000";

# Wider mouth open. Worked well for Miller
graph -editlink -from "Normalized Power" -to "jaw_open_general" -linkfn "linear" -linkfnparams "m=0.7|b=0.000000";

# For Anna only due to separate up and down W and U phonemes
graph -editlink -from "Phoneme_W_up" -to "phoneme_W_up_elements" -linkfn "linear" -linkfnparams "m=0.3|b=0.000000";
graph -editlink -from "phoneme_W" -to "phoneme_W_down_elements" -linkfn "linear" -linkfnparams "m=0.3|b=0.000000";
graph -editlink -from "Phoneme_U_up" -to "phoneme_U_up_elements" -linkfn "linear" -linkfnparams "m=0.3|b=0.000000";
graph -editlink -from "phoneme_U" -to "phoneme_U_down_elements" -linkfn "linear" -linkfnparams "m=0.3|b=0.000000";
graph -editlink -from "Normalized Power" -to "jaw_open_general" -linkfn "linear" -linkfnparams "m=0.7|b=0.000000";

# add eye blink corrective setup
graph -addnode -nodetype "FxCombinerNode" -name "mocap_eye_depressor" -nodex -3273 -nodey 4699;
graph -addnode -nodetype "FxCombinerNode" -name "eye_emotions_depressor" -nodex -3273 -nodey 4699;
graph -link -from "Blink" -to "mocap_eye_depressor" -linkfn "linear";
graph -link -from "Blink" -to "eye_emotions_depressor" -linkfn "linear";
graph -link -from "mocap_eye_depressor" -to "Eyes_widen_Up_R" -linkfn "corrective";
graph -link -from "mocap_eye_depressor" -to "Eyes_widen_Up_L" -linkfn "corrective";
graph -link -from "mocap_eye_depressor" -to "Eyes_widen_Down_R" -linkfn "corrective";
graph -link -from "mocap_eye_depressor" -to "Eyes_widen_Down_L" -linkfn "corrective";
graph -link -from "mocap_eye_depressor" -to "Eye_Squint_Up_R" -linkfn "corrective";
graph -link -from "mocap_eye_depressor" -to "Eye_Squint_Up_L" -linkfn "corrective";
graph -link -from "mocap_eye_depressor" -to "Eye_Squint_Down_R" -linkfn "corrective";
graph -link -from "mocap_eye_depressor" -to "Eye_Squint_Down_L" -linkfn "corrective";
graph -link -from "eye_emotions_depressor" -to "sadness_eye_r" -linkfn "corrective";
graph -link -from "eye_emotions_depressor" -to "sadness_eye_l" -linkfn "corrective";
graph -link -from "eye_emotions_depressor" -to "fear_eye_l" -linkfn "corrective";
graph -link -from "eye_emotions_depressor" -to "fear_eye_r" -linkfn "corrective";
graph -link -from "eye_emotions_depressor" -to "anger_eye_r" -linkfn "corrective";
graph -link -from "eye_emotions_depressor" -to "anger_eye_l" -linkfn "corrective";
graph -link -from "eye_emotions_depressor" -to "disgust_eye_r" -linkfn "corrective";
graph -link -from "eye_emotions_depressor" -to "disgust_eye_l" -linkfn "corrective";
graph -unlink -from "Anger" -to "Blink";
graph -unlink -from "happy" -to "Blink";
graph -unlink -from "disgust_eye_r" -to "Blink";

# Cleanup after previous batch
graph -removenode -name "fear_eyes_depressor";
graph -removenode -name "suprise_eyes_supressor";

#Added control for mocap blinks over other mocap eye nodes
graph -addnode -nodetype "FxCombinerNode" -name "eye_l_movement_depressor" -nodex 10902 -nodey -5560;
graph -addnode -nodetype "FxCombinerNode" -name "eye_r_movement_depressor" -nodex 10040 -nodey -5093;
setName -facegraphnode -old "mocap_eye_depressor" -new "mocap_eye_l_depressor";
graph -addnode -nodetype "FxCombinerNode" -name "mocap_eye_r_depressor" -nodex -2874 -nodey 5000;
graph -unlink -from "Blink" -to "Eye_Up_R";
graph -unlink -from "Blink" -to "Eye_Up_L";
graph -unlink -from "Blink" -to "Eye_Down_L";
graph -unlink -from "Blink" -to "Eye_In_L";
graph -unlink -from "Blink" -to "Eye_Out_L";
graph -unlink -from "Blink" -to "Eye_Out_R";
graph -unlink -from "Blink" -to "Eye_In_R";
graph -unlink -from "Blink" -to "Eye_Down_R";
graph -unlink -from "mocap_eye_l_depressor" -to "Eye_Squint_Down_L";
graph -unlink -from "mocap_eye_l_depressor" -to "Eye_Squint_Up_L";
graph -unlink -from "mocap_eye_l_depressor" -to "Eyes_widen_Down_L";
graph -unlink -from "mocap_eye_l_depressor" -to "Eyes_widen_Up_L";
graph -link -from "eye_l_movement_depressor" -to "Eye_Up_L" -linkfn "corrective";
graph -link -from "eye_l_movement_depressor" -to "Eye_Down_L" -linkfn "corrective";
graph -link -from "eye_l_movement_depressor" -to "Eye_In_L" -linkfn "corrective";
graph -link -from "eye_l_movement_depressor" -to "Eye_Out_L" -linkfn "corrective";
graph -link -from "eye_r_movement_depressor" -to "Eye_Out_R" -linkfn "corrective";
graph -link -from "eye_r_movement_depressor" -to "Eye_In_R" -linkfn "corrective";
graph -link -from "eye_r_movement_depressor" -to "Eye_Down_R" -linkfn "corrective";
graph -link -from "eye_r_movement_depressor" -to "Eye_Up_R" -linkfn "corrective";
graph -link -from "mocap_eye_r_depressor" -to "Eyes_widen_Up_L" -linkfn "corrective";
graph -link -from "mocap_eye_r_depressor" -to "Eyes_widen_Down_L" -linkfn "corrective";
graph -link -from "mocap_eye_r_depressor" -to "Eye_Squint_Up_L" -linkfn "corrective";
graph -link -from "mocap_eye_r_depressor" -to "Eye_Squint_Down_L" -linkfn "corrective";
graph -link -from "Blink" -to "mocap_eye_r_depressor" -linkfn "linear";
graph -link -from "Blink_L" -to "mocap_eye_l_depressor" -linkfn "linear";
graph -link -from "Blink_R" -to "mocap_eye_r_depressor" -linkfn "linear";
graph -link -from "Blink_L" -to "eye_l_movement_depressor" -linkfn "linear";
graph -link -from "Blink_R" -to "eye_r_movement_depressor" -linkfn "linear";
graph -link -from "Blink" -to "eye_l_movement_depressor" -linkfn "linear";
graph -link -from "Blink" -to "eye_r_movement_depressor" -linkfn "linear";

# Correct eye in extreme interest
graph -link -from "Eye_Out_R" -to "Eye_In_L" -linkfn "corrective" -linkfnparams "Correction Factor=0.38";
graph -link -from "Eyeball_R_Out" -to "Eyeball_L_In" -linkfn "corrective" -linkfnparams "Correction Factor=0.38";
graph -link -from "Eye_Out_L" -to "Eye_In_R" -linkfn "corrective" -linkfnparams "Correction Factor=0.38";
graph -link -from "Eyeball_L_Out" -to "Eyeball_R_In" -linkfn "corrective" -linkfnparams "Correction Factor=0.38";

# Replaced eye correction on self depression
graph -unlink -from "Eye_Out_R" -to "Eye_In_L";
graph -unlink -from "Eyeball_R_Out" -to "Eyeball_L_In";
graph -unlink -from "Eye_Out_L" -to "Eye_In_R";
graph -unlink -from "Eyeball_L_Out" -to "Eyeball_R_In";
graph -addnode -nodetype "FxCombinerNode" -name "eye_in_depressor" -nodex -7476 -nodey 4909;
graph -addnode -nodetype "FxCombinerNode" -name "eye_in_constant_depressor" -nodex -7623 -nodey 5000;
graph -link -from "eye_in_constant_depressor" -to "eye_in_depressor" -linkfn "linear";
graph -editlink -from "eye_in_constant_depressor" -to "eye_in_depressor" -linkfn "linear" -linkfnparams "m=-1|b=1";
graph -link -from "eye_in_depressor" -to "Eye_In_R" -linkfn "corrective" -linkfnparams "Correction Factor=0.38";
graph -link -from "eye_in_depressor" -to "Eyeball_R_In" -linkfn "corrective" -linkfnparams "Correction Factor=0.38";
graph -link -from "eye_in_depressor" -to "Eye_In_L" -linkfn "corrective" -linkfnparams "Correction Factor=0.38";
graph -link -from "eye_in_depressor" -to "Eyeball_L_In" -linkfn "corrective" -linkfnparams "Correction Factor=0.38";

#Increased correction value for inner eyes for test purposes
graph -editlink -from "eye_in_depressor" -to "Eye_In_L" -linkfn "corrective" -linkfnparams "Correction Factor=0.5";
graph -editlink -from "eye_in_depressor" -to "Eye_In_R" -linkfn "corrective" -linkfnparams "Correction Factor=0.5";
graph -editlink -from "eye_in_depressor" -to "Eyeball_L_In" -linkfn "corrective" -linkfnparams "Correction Factor=0.5";
graph -editlink -from "eye_in_depressor" -to "Eyeball_R_In" -linkfn "corrective" -linkfnparams "Correction Factor=0.5";

# Added mocap depressor while facefx phrases playing
graph -addnode -nodetype "FxCombinerNode" -name "facefx_to_mocap_depressor" -nodex -3643 -nodey 5833;
graph -addnode -nodetype "FxCombinerNode" -name "mocap_low_face_depressor" -nodex -3730 -nodey 5747;
graph -link -from "facefx_to_mocap_depressor" -to "mocap_eye_r_depressor" -linkfn "linear" -linkfnparams "m=0.5|b=0.000000";
graph -link -from "facefx_to_mocap_depressor" -to "mocap_eye_l_depressor" -linkfn "linear" -linkfnparams "m=0.5|b=0.000000";
graph -link -from "facefx_to_mocap_depressor" -to "mocap_low_face_depressor" -linkfn "linear" -linkfnparams "m=0.8|b=0.000000";
graph -link -from "mocap_low_face_depressor" -to "Mouth_swing_right" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Mouth_swing_left" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Corner_depress_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Corner_depress_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lips_Purse" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lips_funneler" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Jaw_Right" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Jaw_Left" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Jaw_Forwards" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Jaw_Backwards" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Nostril_Flare_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Nostril_Flare_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Nostril_Compress_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Nose_Down_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Nose_Down_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Chin_Upwards" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Cheeks_Blow_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Cheeks_Blow_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Cheek_Raiser_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Cheek_Raiser_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Teeth_Right" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Teeth_Left" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Teeth_Forwards" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Teeth_Backwards" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Nostril_Compress_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Tongue_Wide" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Tongue_Up" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Tongue_Rolled_Up" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Tongue_Rolled_Down" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Tongue_Pressed_Upwards" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Tongue_Narrow" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Tongue_In" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Tongue_Down" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Up_Pinch_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Up_Pinch_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Up_Open_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Up_Open_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Lower_Up_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Lower_Up_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Lower_Down_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Lower_Down_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Down_Pinch_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Down_Pinch_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Down_Open_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Down_Open_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Upper_Up_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "Lip_Upper_Up_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "LipLowerDown_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "LipLowerDown_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "MouthPress_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "MouthPress_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "MouthFrown_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "MouthFrown_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "MouthDimple_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "MouthDimple_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "LipsUpperUp_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "LipsUpperUp_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "LipsUpperClose" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "LipsStretch_R" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "LipsStretch_L" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";
graph -link -from "mocap_low_face_depressor" -to "LipsLowerClose" -linkfn "corrective" -linkfnparams "Correction Factor=1.0";

# Added suppression of faceshift animation while playing facefx phrases
graph -addnode -nodetype "FxCombinerNode" -name "mocap_emotions_depressor" -nodex 9507 -nodey 9163;
graph -link -from "mocap_emotions_depressor" -to "smile_low_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "smile_eye_r_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "smile_eye_l_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "smile_up_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "surprise_low_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "surprise_eye_l_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "surprise_eye_r_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "surprise_up_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "anger_up_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "anger_eye_r_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "anger_eye_l_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "sadness_low_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "sadness_eye_r_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "sadness_eye_l_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "sadness_up_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "anger_low_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "happiness_low_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "happinessP_eye_r_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "happinessP_eye_l_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "happiness_up_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "disgust_low_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "disgust_eye_r_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "disgust_eye_l_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "disgust_up_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "fear_low_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "fear_eye_r_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "fear_eye_l_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "fear_up_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "phoneme_P_delta_elements" -linkfn "corrective";
graph -link -from "facefx_to_mocap_depressor" -to "mocap_emotions_depressor" -linkfn "linear";
graph -link -from "Wonder" -to "mocap_emotions_depressor" -linkfn "corrective";
graph -link -from "Smile" -to "mocap_emotions_depressor" -linkfn "corrective";
graph -link -from "Anger" -to "mocap_emotions_depressor" -linkfn "corrective";
graph -link -from "Fear" -to "mocap_emotions_depressor" -linkfn "corrective";
graph -link -from "Wide_Smile" -to "mocap_emotions_depressor" -linkfn "corrective";
graph -link -from "Sadness" -to "mocap_emotions_depressor" -linkfn "corrective";
graph -link -from "Disgust" -to "mocap_emotions_depressor" -linkfn "corrective";

# Suppresses mocap eye blink while playing facefx phrases
graph -addnode -nodetype "FxCombinerNode" -name "mocap_blink_suppressor" -nodex 10179 -nodey -5836;
graph -link -from "mocap_blink_suppressor" -to "Blink_L" -linkfn "corrective";
graph -link -from "mocap_blink_suppressor" -to "Blink_R" -linkfn "corrective";
graph -link -from "Blink" -to "mocap_blink_suppressor" -linkfn "corrective";
graph -link -from "facefx_to_mocap_depressor" -to "mocap_blink_suppressor" -linkfn "linear"; 

# Restores delta P while playing lipsync
graph -addnode -nodetype "FxCombinerNode" -name "phoneme_P_delta_facefx_call" -nodex 11907 -nodey -1499;
graph -link -from "phoneme_P_delta_facefx_call" -to "phoneme_P_delta_elements" -linkfn "corrective";
graph -link -from "mocap_emotions_depressor" -to "phoneme_P_delta_facefx_call" -linkfn "linear";
graph -unlink -from "mocap_emotions_depressor" -to "phoneme_P_delta_elements";
graph -editlink -from "phoneme_P_delta" -to "phoneme_P_delta_elements" -linkfn "linear" -linkfnparams "m=1.0|b=0.000000";
graph -link -from "P" -to "phoneme_P_delta_facefx_call" -linkfn "corrective";

# Not batched
# Reduce Y phoneme for Anna-like setup (women)
graph -editlink -from "phoneme_Y" -to "phoneme_Y_up_elements" -linkfn "linear" -linkfnparams "m=0.5|b=0.000000";
graph -editlink -from "phoneme_Y" -to "phoneme_Y_down_elements" -linkfn "linear" -linkfnparams "m=0.5|b=0.000000";
graph -editlink -from "phoneme_Y_delta" -to "phoneme_Y_delta_up_elements" -linkfn "linear" -linkfnparams "m=0.5|b=0.000000";
graph -editlink -from "phoneme_Y_delta" -to "phoneme_Y_delta_down_elements" -linkfn "linear" -linkfnparams "m=0.5|b=0.000000";

# restores tongue movement
graph -unlink -from "mocap_low_face_depressor" -to "Tongue_Down";
graph -unlink -from "mocap_low_face_depressor" -to "Tongue_In";
graph -unlink -from "mocap_low_face_depressor" -to "Tongue_Narrow";
graph -unlink -from "mocap_low_face_depressor" -to "Tongue_Pressed_Upwards";
graph -unlink -from "mocap_low_face_depressor" -to "Tongue_Rolled_Down";
graph -unlink -from "mocap_low_face_depressor" -to "Tongue_Rolled_Up";
graph -unlink -from "mocap_low_face_depressor" -to "Tongue_Up";
graph -unlink -from "mocap_low_face_depressor" -to "Tongue_Wide";

# Connects Strees as low lip down trigger
graph -unlink -from "Stress" -to "Stress_inv";
graph -unlink -from "Rate of Speech Scale_inv" -to "low_lip_down_call";
graph -link -from "Stress" -to "low_lip_down" -linkfn "linear";
graph -link -from "Rate of Speech Scale_inv" -to "Stress" -linkfn "corrective";

# Added suppress for low lip down if mouth openes wide
graph -link -from "jaw_open_general" -to "low_lip_down" -linkfn "corrective";

# Removed node that triggered low lip down somehow
graph -removenode -name "low_lip_down_call";

# Added speech amplifier for shout
graph -addnode -nodetype "FxCombinerNode" -name "speech_amplifier_upper" -nodex 9052 -nodey -10703 -inputop "Multiply Inputs" -max 2.000000;
graph -addnode -nodetype "FxCombinerNode" -name "speech_amplifier_depressor" -nodex 9052 -nodey -10703;
graph -addnode -nodetype "FxCombinerNode" -name "speech_amplifier_low" -nodex 9052 -nodey -10703 -inputop "Multiply Inputs";
graph -addnode -nodetype "FxCombinerNode" -name "wide_pose" -nodex 9052 -nodey -10703;
graph -addnode -nodetype "FxCombinerNode" -name "jaw_amplifier" -nodex 9052 -nodey -10703 -max 2.000000;
graph -addnode -nodetype "FxCombinerNode" -name "amplifier_inverted" -nodex 9052 -nodey -10703;
graph -addnode -nodetype "FxCombinerNode" -name "speech_amplifier" -nodex 9052 -nodey -10703;
graph -addnode -nodetype "FxCombinerNode" -name "stress_amplifier" -nodex 9052 -nodey -10703;


// speech_amplifier_upper
// out
graph -link -from "speech_amplifier_upper" -to "anger_up_elements" -linkfn "linear" -linkfnparams "m=0.3|b=0.000000";
graph -link -from "speech_amplifier_upper" -to "anger_eye_r_elements" -linkfn "linear" -linkfnparams "m=0.25|b=0.000000";
graph -link -from "speech_amplifier_upper" -to "anger_eye_l_elements" -linkfn "linear" -linkfnparams "m=0.25|b=0.000000";
graph -link -from "speech_amplifier_upper" -to "speech_amplifier_depressor" -linkfn "corrective";
// in
graph -link -from "Stress" -to "speech_amplifier_upper" -linkfn "linear";
graph -link -from "eye_emotions_depressor" -to "speech_amplifier_upper" -linkfn "corrective";
graph -link -from "speech_amplifier" -to "speech_amplifier_upper" -linkfn "linear";


// speech_amplifier_low
// out
graph -link -from "speech_amplifier_low" -to "anger_lip_L_down" -linkfn "linear" -linkfnparams "m=0.5|b=0.000000";
graph -link -from "speech_amplifier_low" -to "anger_lip_R_down" -linkfn "linear" -linkfnparams "m=0.5|b=0.000000";
graph -link -from "speech_amplifier_low" -to "wide_pose" -linkfn "linear" -linkfnparams "m=0.3|b=0.000000";
graph -link -from "speech_amplifier_low" -to "Nose_Up_L" -linkfn "linear" -linkfnparams "m=0.8|b=0.000000";
graph -link -from "speech_amplifier_low" -to "Nose_Up_R" -linkfn "linear" -linkfnparams "m=0.8|b=0.000000";
graph -link -from "speech_amplifier_low" -to "disgust_lip_L_up" -linkfn "linear" -linkfnparams "m=0.8|b=0.000000";
graph -link -from "speech_amplifier_low" -to "disgust_lip_R_up" -linkfn "linear" -linkfnparams "m=0.8|b=0.000000";
// in
graph -link -from "Stress" -to "speech_amplifier_low" -linkfn "linear";
graph -link -from "speech_amplifier" -to "speech_amplifier_low" -linkfn "linear";
graph -link -from "P" -to "speech_amplifier_low" -linkfn "corrective";
graph -link -from "U" -to "speech_amplifier_low" -linkfn "corrective" -linkfnparams "Correction Factor=0.5"


// wide_pose
// out
graph -link -from "wide_pose" -to "wide_pose_nose_R" -linkfn "linear";
graph -link -from "wide_pose" -to "wide_pose_nose_L" -linkfn "linear";
graph -link -from "wide_pose" -to "wide_pose_lip_R_up" -linkfn "linear";
graph -link -from "wide_pose" -to "wide_pose_lip_R_down" -linkfn "linear";
graph -link -from "wide_pose" -to "wide_pose_lip_L_up" -linkfn "linear";
graph -link -from "wide_pose" -to "wide_pose_lip_L_down" -linkfn "linear";
graph -link -from "wide_pose" -to "wide_pose_jaw_R" -linkfn "linear";
graph -link -from "wide_pose" -to "wide_pose_jaw_L" -linkfn "linear";
graph -link -from "wide_pose" -to "wide_pose_cheek_R" -linkfn "linear";
graph -link -from "wide_pose" -to "wide_pose_cheek_L" -linkfn "linear";
// in
graph -link -from "stress_amplifier" -to "wide_pose" -linkfn "linear";
graph -link -from "P" -to "wide_pose" -linkfn "corrective";
graph -link -from "speech_amplifier_low" -to "wide_pose" -linkfn "linear" -linkfnparams "m=0.3|b=0.000000";


// jaw_amplifier
// out
graph -link -from "jaw_amplifier" -to "jaw_open_general" -linkfn "linear";
graph -link -from "jaw_amplifier" -to "up_lip_up" -linkfn "linear";
// in
graph -link -from "amplifier_inverted" -to "jaw_amplifier" -linkfn "linear" -linkfnparams "m=-1|b=1";


// speech_amplifier
// out
graph -link -from "speech_amplifier" -to "stress_amplifier" -linkfn "corrective";
graph -link -from "speech_amplifier" -to "speech_amplifier_low" -linkfn "linear";
graph -link -from "speech_amplifier" -to "speech_amplifier_upper" -linkfn "linear";

// stress_amplifier
// out
graph -link -from "stress_amplifier" -to "wide_pose" -linkfn "linear";
graph -link -from "stress_amplifier" -to "Lip_Up_Open_L" -linkfn "linear";
graph -link -from "stress_amplifier" -to "Lip_Up_Open_R" -linkfn "linear";
graph -link -from "stress_amplifier" -to "Lip_Up_Pinch_L" -linkfn "linear";
graph -link -from "stress_amplifier" -to "Lip_Up_Pinch_R" -linkfn "linear";
graph -link -from "stress_amplifier" -to "up_lip_up" -linkfn "linear" -linkfnparams "m=0.5|b=0.000000";
graph -link -from "stress_amplifier" -to "anger_lip_L_up" -linkfn "linear" -linkfnparams "m=0.3|b=0.000000";
graph -link -from "stress_amplifier" -to "anger_lip_R_up" -linkfn "linear" -linkfnparams "m=0.3|b=0.000000";
graph -link -from "stress_amplifier" -to "Nose_Up_L" -linkfn "linear" -linkfnparams "m=0.2|b=0.000000";
graph -link -from "stress_amplifier" -to "Nose_Up_R" -linkfn "linear" -linkfnparams "m=0.2|b=0.000000";
// in
graph -link -from "Stress" -to "stress_amplifier" -linkfn "linear";
graph -link -from "speech_amplifier" -to "stress_amplifier" -linkfn "corrective";


// speech_amplifier_depressor
// out
graph -link -from "speech_amplifier_depressor" -to "anger_up_elements" -linkfn "corrective";
graph -link -from "speech_amplifier_depressor" -to "anger_eye_l_elements" -linkfn "corrective";
graph -link -from "speech_amplifier_depressor" -to "anger_eye_r_elements" -linkfn "corrective";
// in
graph -link -from "speech_amplifier_upper" -to "speech_amplifier_depressor" -linkfn "corrective";
graph -link -from "facefx_to_mocap_depressor" -to "speech_amplifier_depressor" -linkfn "linear";
// unlink
graph -unlink -from "mocap_emotions_depressor" -to "anger_up_elements";
graph -unlink -from "mocap_emotions_depressor" -to "anger_eye_r_elements";
graph -unlink -from "mocap_emotions_depressor" -to "anger_eye_l_elements";

# Restores wonder brows, decreses eyes open
graph -editlink -from "surprise_up_suppressor" -to "surprise_up" -linkfn "corrective" -linkfnparams "Correction Factor=0.000000";
graph -editlink -from "Wonder" -to "surprise_eye_r" -linkfn "linear" -linkfnparams "m=0.5|b=0.000000";
graph -editlink -from "Wonder" -to "surprise_eye_l" -linkfn "linear" -linkfnparams "m=0.5|b=0.000000";
'''

