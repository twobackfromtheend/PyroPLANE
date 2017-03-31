# import misc
# from misc import div
# import numpy as np
# import statistics as s
import pyroplane.config

from pyroplane.anal.aplayer import APlayer
from pyroplane.anal.ateam import ATeam

print('hi')

def set_config(config):
    envName = 'Environment Values'
    AHit.goal_x = config.getint(envName,'goal_x')
    AHit.goal_y = config.getint(envName,'goal_y')
    AHit.goal_z = config.getint(envName,'goal_z')

    AHit.shot_off_x = config.getint(envName,'shot_off_x')
    AHit.shot_off_z = config.getint(envName,'shot_off_z')

    AHit.magic_vel = config.getfloat(envName,'magic_vel')
    APosition.magic_vel = config.getfloat(envName,'magic_vel')
    magic_vel = 0.0043527

    AHit.normal_g = config.getfloat(envName,'normal_g')

    AHit.cutoff_time_to_goal = config.getfloat('Shot Detection','cutoff_time_to_goal')

