import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm

def shotRegression(shots_data):
    y = shots_data[:, 0]
    X = shots_data[:, 1:]
    X2 = sm.add_constant(X)
    est = sm.OLS(y, X2)
    est2 = est.fit()
    print (est2.summary())
    return est2.params
    # shots_data contains the number of shots for each team in a game and the player contributions in the game
    # such as won_contest, aerial_lost, red_card, total_pass etc
    # we model the log of total shots as a linear function of these contributions

def shotRate(contributions):
    # contributions contain data regarding a team's players contributions during a game based on the same
    # as used in the regression model. By taking the coefficients obtained in the regression model
    # an estimate of the expected number of shots during the game is returned
    pass