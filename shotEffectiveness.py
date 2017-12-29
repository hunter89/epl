import numpy as np


def estimateProbabilities(total_shots, total_goals, total_onTarget, total_saves, total_blocks):
    
    # estimated probability of goal given shot attempted, Pg_s
    P_goal_s = total_goals/total_shots

    # esitmated probability of shot_onTarget given shot attempted
    P_ontarget_s = total_onTarget/total_shots

    # estimated probability of save or block given shot on target
    P_save_or_block_ontarget = (total_saves + total_blocks)/total_onTarget

    probabilities = [P_goal_s, P_ontarget_s, P_save_or_block_ontarget]
    return probabilities
    