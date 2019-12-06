import sys
sys.path.extend(['u:/face/scripts/facefx_batch/'])
import SetAnimation
reload(SetAnimation)

sa = SetAnimation.SetAnimation()
sa.proc_mocap()
