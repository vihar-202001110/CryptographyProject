
import numpy as np
import sympy as smp
from scipy.integrate import odeint


# intially passsing both angles theta_1_initial,theta_2_initial and both angular velocities w1 and w2
def getCoordinates(total_time: float=40, total_samples:int=1001, theta1_initial:float=1, angularVelocity_initial_1:float=-3, theta2_intial:float=-1, angularVelocity_initial_2:float=5, mass1:float=2, mass2:float=1, length_1:float=2, length_2:float=1, gravity:float=9.81):
    t, g = smp.symbols('t g')
    m1, m2 = smp.symbols('m1 m2')
    L1, L2 = smp.symbols('L1, L2')

    # theta_1 and theta_2 are functions of time (which we will eventually solve for). We need to define them carefully.

    the1, the2 = smp.symbols(r'\theta_1, \theta_2', cls=smp.Function) # type: ignore

    # Explicitly write them as functions of time $t$:

    the1 = the1(t)
    the2 = the2(t)

    # Define derivatives and second derivatives

    the1_d = smp.diff(the1, t)
    the2_d = smp.diff(the2, t)
    the1_dd = smp.diff(the1_d, t)
    the2_dd = smp.diff(the2_d, t)

    # Define $x_1$, $y_1$, $x_2$, and $y_2$ written in terms of the parameters above.

    x1 = L1*smp.sin(the1)
    y1 = -L1*smp.cos(the1)
    x2 = L1*smp.sin(the1)+L2*smp.sin(the2)
    y2 = -L1*smp.cos(the1)-L2*smp.cos(the2)

    """Then use these to define kinetic and potential energy for each mass. Obtain the Lagrangian"""

    # Kinetic
    T1 = 1/2 * m1 * (smp.diff(x1, t)**2 + smp.diff(y1, t)**2)
    T2 = 1/2 * m2 * (smp.diff(x2, t)**2 + smp.diff(y2, t)**2)
    T = T1+T2
    # Potential
    V1 = m1*g*y1
    V2 = m2*g*y2
    V = V1 + V2
    # Lagrangian
    L = T-V

    """Get Lagrange's equations

    $$\frac{partial L}{partial theta_1} - \frac{d}{dt}\frac{partial L}{partial dot{theta_1}} = 0$$
    $$\frac{partial L}{partial theta_2} - \frac{d}{dt}\frac{partial L}{partial dot{theta_2}} = 0$$
    """

    LE1 = smp.diff(L, the1) - smp.diff(smp.diff(L, the1_d), t).simplify()
    LE2 = smp.diff(L, the2) - smp.diff(smp.diff(L, the2_d), t).simplify()

    """Solve Lagranges equations (this assumes that `LE1` and `LE2` are both equal to zero)"""

    sols = smp.solve([LE1, LE2], (the1_dd, the2_dd),
                     simplify=False, rational=False)


    dz1dt_f = smp.lambdify(
        (t, g, m1, m2, L1, L2, the1, the2, the1_d, the2_d), sols[the1_dd])
    dz2dt_f = smp.lambdify(
        (t, g, m1, m2, L1, L2, the1, the2, the1_d, the2_d), sols[the2_dd])
    dthe1dt_f = smp.lambdify(the1_d, the1_d)
    dthe2dt_f = smp.lambdify(the2_d, the2_d)

    """Now define $\vec{S} = (\theta_1, z_1, \theta_2, z_2)$. IF we're going to use an ODE solver in python, we need to write a function that takes in $\vec{S}$ and $t$ and returns $d\vec{S}/dt$. In other words, we need to define $d\vec{S}/dt (\vec{S}, t)$

    * Our system of ODEs can be fully specified using $d\vec{S}/dt$ and depends only on $\vec{S}$ and $t$
    """
    
    def dSdt(S, t, g, m1, m2, L1, L2):
        the1, z1, the2, z2 = S
        return [
            dthe1dt_f(z1),
            dz1dt_f(t, g, m1, m2, L1, L2, the1, the2, z1, z2),
            dthe2dt_f(z2),
            dz2dt_f(t, g, m1, m2, L1, L2, the1, the2, z1, z2),
        ]

    """Solvint the system of ODEs using scipys `odeint` method"""

    t = np.linspace(0, total_time, total_samples)
    g = gravity
    m1 = mass1
    m2 = mass2
    L1 = length_1
    L2 = length_2
    ans = odeint(dSdt, y0=[theta1_initial, angularVelocity_initial_1, theta2_intial, angularVelocity_initial_2],
                 t=t, args=(g, m1, m2, L1, L2))

    """Can obtain $\theta_1(t)$ and $\theta_2(t)$ from the answer"""

    the1 = ans.T[0]
    the2 = ans.T[2]
    
    """Here's a function that takes in $\theta_1$ and $\theta_2$ and returns the location (x,y) of the two masses."""
    
    x1 = L1 * np.sin(the1)
    y1 = -L1 * np.cos(the1)
    x2 = L1 * np.sin(the1) + L2 * np.sin(the2)
    y2 = -L1 * np.cos(the1) - L2 * np.cos(the2)

    """Then we can make an animation"""

    return x1, y1, x2, y2