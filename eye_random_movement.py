import random

'''
# Far blend
# In frames
blend = (0, 3)
# In frames
duration = (7, 15)
# In angles
intencity_vertical = (-3.5, 3.5)
# More horizontal movement over vertical
intencity_horizontal = (-4.5, 4.5)

# Close blend
# In frames
blend = (0, 3)
# In frames
duration = (5, 12)
# In angles
intencity_vertical = (-2, 2)
# More horizontal movement over vertical
intencity_horizontal = (-3, 3)
'''

# In frames
blend = (0, 3)
# In frames
duration = (5, 10)
# In angles
intencity_vertical = (-2, 2)
# More horizontal movement over vertical
intencity_horizontal = (-5, 5)
start, end = f.get_timeline()
# start, end = 0, 100
attr_x = ['bn_eye_{}.rotateX'.format(side) for side in ['r', 'l']]
attr_z = ['bn_eye_{}.rotateZ'.format(side) for side in ['r', 'l']]
frame_value_data = {}
blend_val = 0
duration_val = 0
intencity_val_x = 0
intencity_val_z = 0
# Generates key values over time
for frame in xrange(start, end + 1):
    # If duration with with static key value ended, but blend not added
    if duration_val == 0 and blend_val != 0:
        frame_value_data[frame] = None
        blend_val -= 1
        continue
    # Both duration and blend added to data
    elif duration_val == 0 and blend_val == 0:
        intencity_val_x = random.uniform(*intencity_vertical)
        intencity_val_z = random.uniform(*intencity_horizontal)
        blend_val = round(random.uniform(*blend), 0)
        duration_val = round(random.uniform(*duration), 0)

    duration_val -= 1
    frame_value_data[frame] = [intencity_val_x, intencity_val_z]

for frame, value in frame_value_data.iteritems():
    if not value:
        continue
    cmds.setKeyframe(attr_x, time=frame, value=value[0])
    cmds.setKeyframe(attr_z, time=frame, value=value[1])
