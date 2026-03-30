from Prompts.Activity_description.Gears import gears_description
from Prompts.Activity_description.three_d_Volume import three_d_volume_description

def get_activity_description(activity):

    if(activity == 'Gears Activity'):

        return gears_description()
    else:

        return three_d_volume_description()
