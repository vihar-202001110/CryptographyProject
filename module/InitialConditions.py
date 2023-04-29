
import random
from datetime import datetime
from math import pi


def generateInitialConditions():
    random.seed(datetime.now().timestamp())
    total_time = random.randint(40,100)      							# range - 40 to 100
    theta1_initial = (random.random() * 2 * pi) - pi					# range - -pi to pi
    theta2_intial = (random.random() * 2 * pi) - pi   					# range - -pi to pi
    angularVelocity_initial_1 = (random.random() * 10 * pi) - (5 * pi)	# range - -5pi to 5pi
    angularVelocity_initial_2 = (random.random() * 10 * pi) - (5 * pi)	# range - -5pi to 5pi
    mass1 = 2                                 		# range -
    mass2 = 1                                 		# range - 
    length_1 = 2                              		# range - 0 to 7
    length_2 = 1                              		# range - 0 to 7
    gravity=9.81                            		# range - 5 to 10


print(generateInitialConditions())