from scipy.optimize import differential_evolution, NonlinearConstraint
from scipy.integrate import solve_ivp,trapz,RK45,odeint,ode
from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt

reference_momentum_all = [170, 200, 224] #[155, 200, 230] #[170, 200, 220] #[160, 200, 225] #[155, 200, 230] #[160,200,240] #[170,200,230] 
pre = 'D:/real_design/'
with open('field_cell.dat','r') as f:
    out = f.readlines()
field_on_axis = []
z_position = []
for i in range(4,len(out)):
    numbers = [float(x) for x in out[i].strip().split()]
    if numbers[0]==0 and numbers[1]==0:
        field_on_axis.append(numbers[5])
        z_position.append(numbers[2]/1000)
start = z_position[0]
z_position = [x-start for x in z_position] #[:101]
field_on_axis = field_on_axis #[:101]
func = interp1d(z_position,field_on_axis,kind='cubic')

def beta_evolve(t,y,*args):
    Bs = func(t)
    reference_momentum = reference_momentum_all[args[0]]
    k = Bs*299792458/(reference_momentum*10**6)
    return [y[1],(4-k**2*y[0]**2+y[1]**2)/(2*y[0])]


points_num = 150
def minimize(x, *args):
    beta0,beta_p0 = x
    solution = solve_ivp(beta_evolve,args=(args[0],),t_span=(z_position[0],z_position[-1]),y0=[beta0,beta_p0],max_step=(z_position[-1]-z_position[0])/points_num)
    beta = solution.y[0]
    beta_p = solution.y[1]
    #z = solution.t
    return (beta[-1]-beta0)**2 + (beta_p[-1]-beta_p0)**2

if __name__ == '__main__':
    bounds = [(0.00001,1),(0.000001,1)]
    beta_all  = []
    phi_all = []
    beta_middle = []
    for i in range(3):
        result = differential_evolution(minimize, args=(i,), bounds=bounds, workers=16, disp=False, maxiter=50)
        beta0,beta_p0 = result.x
        solution = solve_ivp(beta_evolve,args=(i,),t_span=(z_position[0],z_position[-1]),y0=[beta0,beta_p0],max_step=(z_position[-1]-z_position[0])/points_num)
        phi = trapz(1/solution.y[0],solution.t)
        beta_middle.append(solution.y[0][int(len(solution.y[0])/2)])
        beta_all.append(beta0)
        phi_all.append(phi)
    np.save('beta',beta_all)
    np.save('beta_middle',beta_middle)
    np.save('phi',phi_all)

   



