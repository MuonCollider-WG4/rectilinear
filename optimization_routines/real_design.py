import os
import subprocess
import numpy as np
import shutil
from scipy.optimize import differential_evolution,NonlinearConstraint
import math as mat

u0 = 4*mat.pi*10**(-7)
pi = mat.pi
mode = 3
cell_length =780
rf_length_max = 80
Ri = 0.05
Rf = 0.13
Ri2 = 0.16
Rf2 = 0.31
Ri3 = 0.34
Rf3 = 0.54
Ri4 = 0.31
Rf4 = 0.51


def minimize(x):
    init_dir = '/home/zhurh/new_folder/'
    os.chdir(init_dir)
    present_dir = '/home/zhurh/new_folder/data_beta/' + ','.join([str(i) for i in x])
    if os.path.exists(present_dir):
        #print('file exsits')
        present_dir = '/home/zhurh/new_folder/data_beta/' + ','.join([str(i+np.random.uniform(0,1)) for i in x])
    try:
        os.makedirs(present_dir)
    except:
        return 10
    shutil.copy(init_dir + 'beta_and_dispersion.g4bl', present_dir)
    shutil.copy(init_dir + 'beta_and_dispersion_stress.g4bl', present_dir)
    shutil.copy(init_dir + 'scan_beta.py', present_dir)
    os.chdir(present_dir)
    if mode==1:
        parameters = ['solpos1', 'coil_length1', 'current1']
        
    if mode==2:
        parameters = ['solpos1', 'coil_length1', 'current1', 'solpos2', 'coil_length2', 'current2']
        
    if mode==3:
        parameters = ['solpos1', 'coil_length1', 'current1', 'solpos2', 'coil_length2', 'current2', 'solpos3', 'coil_length3', 'current3']
        
    if mode==4:
        parameters = ['solpos1', 'coil_length1', 'current1', 'solpos2', 'coil_length2', 'current2', 'solpos3', 'coil_length3', 'current3', 'solpos4', 'coil_length4', 'current4']
        
    with open('beta_and_dispersion.g4bl', 'r') as f:
        out = f.readlines()
    for i in range(len(parameters)):
        for j in range(len(out)):
            if parameters[i] in out[j]:
                elements = out[j].strip().split('=')
                elements[-1] = str(x[i])
                out[j] = '='.join(elements) + '\n'
                break
    os.remove('beta_and_dispersion.g4bl')
    with open('beta_and_dispersion.g4bl', 'w') as f:
        f.writelines(out)
    cmd1 = subprocess.Popen('g4bl '+'beta_and_dispersion.g4bl > print.out',cwd='./',shell=True)
    cmd1.wait()
    with open('print.out', 'r') as f:
        out = f.readlines()
    for i in range(len(out)):
        if 'Failed to achieve required accuracy' in out[i]:
            os.chdir(init_dir)
            shutil.rmtree(present_dir)
            return np.random.uniform(80,90)

    with open('beta_and_dispersion_stress.g4bl', 'r') as f:
        out = f.readlines()
    for i in range(len(parameters)):
        for j in range(len(out)):
            if parameters[i] in out[j]:
                elements = out[j].strip().split('=')
                elements[-1] = str(x[i])
                out[j] = '='.join(elements) + '\n'
                break
    os.remove('beta_and_dispersion_stress.g4bl')
    with open('beta_and_dispersion_stress.g4bl', 'w') as f:
        f.writelines(out)
    cmd2 = subprocess.Popen('g4bl '+'beta_and_dispersion_stress.g4bl > print.out',cwd='./',shell=True)
    cmd2.wait()
    with open('field_cell_stress.dat','r') as f:
        out = f.readlines()
    B1 = float(out[4].strip().split()[5])
    B2 = float(out[5].strip().split()[5])
    hoop_stress = hoop_stress_Wilson(Ri, Rf, x[2]*10**6, B1, B2)
    radial_stress = rad_stress(Ri, Rf, x[2]*10**6, B1, B2)[1]
    
    if mode==3 or mode==4:
        with open('field_cell_stress2.dat','r') as f:
            out = f.readlines()
        B1 = float(out[4].strip().split()[5])
        B2 = float(out[5].strip().split()[5])
        hoop_stress2 = hoop_stress_Wilson(Ri2, Rf2, x[5]*10**6, B1, B2)
        radial_stress2 = rad_stress(Ri2, Rf2, x[5]*10**6, B1, B2)[1]
        
    if mode==4:
        with open('field_cell_stress3.dat','r') as f:
            out = f.readlines()
        B1 = float(out[4].strip().split()[5])
        B2 = float(out[5].strip().split()[5])
        hoop_stress3 = hoop_stress_Wilson(Ri3, Rf3, x[8]*10**6, B1, B2)
        radial_stress3 = rad_stress(Ri3, Rf3, x[8]*10**6, B1, B2)[1]
    
    cmd3 = subprocess.Popen('python3.8 '+'scan_beta.py', cwd='./', shell=True)
    cmd3.wait()
    beta = np.load('beta.npy')
    beta_middle = np.load('beta_middle.npy')
    phi = np.load('phi.npy')
    os.chdir(init_dir)
    shutil.rmtree(present_dir)
    #if phi[0] > 2*np.pi:
    #    target1 = 10*(phi[0] - 2*np.pi)
    #if phi[0] > 4:
    #    target1 = phi[0] - 2*np.pi
    #else:
    #    target1 = 10*(2*np.pi - phi[0])
    #if phi[-1] < np.pi:
    #    target2 = 10*(np.pi - phi[-1])
    #if phi[-1] < 4:
    #    target2 = np.pi - phi[-1]
    #else:
    #    target2 = 10*(phi[-1] - np.pi)
    #target = target1 + target2
    if mode==3:
        target = 100*(phi[0]-2*np.pi)**2 + 100*(phi[-1]-np.pi)**2 + 200*(beta[1]-0.03)**2 #+ hoop_stress/10 + hoop_stress2/10
    if mode==4:
        target = 100*(phi[0]-2*np.pi)**2 + 100*(phi[-1]-np.pi)**2 + 200*(beta[1]-0.027)**2 #+ hoop_stress/10 + hoop_stress2/10 + hoop_stress3/10
    else:
        target = 100*(phi[0]-2*np.pi)**2 + 100*(phi[-1]-np.pi)**2 + 200*(beta[1]-0.06)**2 #+ hoop_stress/10 #100*(phi[0]-np.pi)**2 + (100*(beta[1]-0.35))**2 + (100*(beta[0]-beta_middle[0]))**2 + hoop_stress/10   
        #target = 100*(phi[0]-np.pi)**2 + (100*(beta[1]-0.7))**2 + (100*(beta[0]-beta_middle[0]))**2 #+ hoop_stress/10
    
    if mode==3:
        with open(init_dir + 'target_beta.txt', 'a+') as f:
            f.write(str(beta[1]) + '\t' + str(phi[0]) + '\t' + str(phi[-1]) + '\t' + str(hoop_stress) + '\t' + str(hoop_stress2) + '\t' + str(radial_stress) + '\t'+ str(radial_stress2) + '\t' + str(target) + '\t' + present_dir + '\n')
    if mode==4:
        with open(init_dir + 'target_beta.txt', 'a+') as f:
            f.write(str(beta[1]) + '\t' + str(phi[0]) + '\t' + str(phi[-1]) + '\t' + str(hoop_stress) + '\t' + str(hoop_stress2) + '\t' + str(hoop_stress3) + '\t' + str(radial_stress) + '\t'+ str(radial_stress2) + '\t' + str(radial_stress3) + '\t' + str(target) + '\t' + present_dir + '\n')
    else:
        with open(init_dir + 'target_beta.txt', 'a+') as f:
            f.write(str(beta[1]) + '\t' + str(phi[0]) + '\t' + str(phi[-1]) + '\t' + str(hoop_stress) + '\t' + str(radial_stress) + '\t' + str(target) + '\t' + present_dir + '\n')
    return target

def magneticEnergyDensity_MJm3_1Coil(R_i, R_f, length, J):
   # Em is proportaional to I^2 * L, I is current, L is inductance
   # I^2 is proportional to the (tape cross section)^2, L^2 is proportional to 1/(tape cross section)^2, so these cancel!
   # So can write the equation in a way to ignore these tape dimension terms. 
   
    thickness = R_f - R_i
    # 1. Calculate the Inductance/N^2 (Inductance L is proportional to N^2.. leaving this term out lets us ignore tape dimensions )
    # Very Accurate when dimensions of cross section are very small relative to mean radius, otherwise errors seen up to 5%
    # Rosa, Edward Bennett, and Frederick Warren Grover.?Formulas and tables for the calculation of mutual and self-inductance. No. 169. 
    # US Government Printing Office, 1948.
    # Eq. 86 pg 136 
    R = 0.2235*(length + thickness) 
    a = R_i + thickness/2.0               # book notation
    induct_coil_SI_perSquareTapeCross = u0*a* (length*thickness)**2 *(mat.log(8*a/R) * (1 + (3*R**2)/(16*a**2)) - (2 + (R**2)/(16*a**2)))  # *N**2 
    
    
    # 2. Calculate Stored Magnetic Energy
    I_perTapeCross = J # I in a tape = J * (tape cross section)
    Em = 0.5 * induct_coil_SI_perSquareTapeCross * I_perTapeCross **2
    
    coilV = pi*((R_i + thickness)**2 - R_i**2)*length
    
    return Em/coilV/10**6 # MJ/m3 

nu = 0.34    # poisson ratio ~ copper (SS around 0.3)

def hoop_stress_Wilson(Ri, Rf, J, B1, B2):
    # From Wilson - also agreed well with Case Studies formula 3.77b
    # Bb and Ba (B2 and B1) are Bz at Rf and Bz at Ri in midplane
    r     = Ri     # compute just at inner radius, where hoop stress is a maximum!
    alpha = Rf/Ri
    a1    = Ri     #  naming convention in Case Studies

    K   = (alpha * B1 - B2)*J * a1 / (alpha - 1)
    eps = r/a1
    M   = (B1 - B2)*J * a1 / (alpha - 1)
    
    term1  = K/3.0*(2+nu)/(alpha + 1)
    term2  = alpha**2 + alpha + 1. + alpha**2/eps**2 - eps*((1+2*nu)*(alpha+1))/(2+nu)
    term3  = M/8.0*(3+nu)
    term4  = alpha**2 + 1 + alpha**2/eps**2 - eps**2 * (1+3*nu)/(3+nu)
    sigma_theta = term1 * term2 - term3*term4
    

    return sigma_theta/10**6 # MPa

def rad_stress(Ri, Rf, J, B1, B2): 
    # from Case Studies Eq. 3.77a
    # B2 and B1 are B at Rf and B at Ri in midplane of coil
    
    rspace = np.arange(Ri, Rf, 0.001) # compute over range to find maximum and minimum, 1 mm resolution

    sigma_rs = list()
    for r in rspace:
        rho   = r/Ri
        alpha = Rf/Ri
        a1    = Ri     #  naming convention in Case Studies
        # winding current density lambd*J
        # Magnetic field varies linearly inside coil from Bz(r=a1)= B1 to Bz(r=a2)=B2
        lambd = 1.0   # lambda*J = current density
        kap   = B2/B1  #-0.1  # just given in text
        
        term1  = (lambd*J*B1*a1)/(alpha - 1)
        term2  = (alpha - kap)*(2. + nu)/(3.0)*((alpha**2 + alpha + 1 - alpha**2/rho**2)/(alpha+1.)-rho)
        term3  = (1.0 - kap)*(3. + nu)/(8.) * (alpha**2 + 1.0 - alpha**2/rho**2 - rho**2)
        sigma_r = term1 * (term2 - term3)
        sigma_rs.append(sigma_r)

    min_sigma_r = min(sigma_rs)
    max_sigma_r = max(sigma_rs)
    
    return [min_sigma_r/10**6, max_sigma_r/10**6]

def coil_constrain1(x):
    return (x[0]*cell_length)-(x[1]/2)

def coil_constrain2(x):
    return (cell_length-4*(rf_length_max+6))/2-((x[0]*cell_length)+(x[1]/2))
    
def coil_constrain3(x):
    return cell_length/2-(x[0]*cell_length+(x[1]/2))
  
def coil_energy1(x):
    return magneticEnergyDensity_MJm3_1Coil(Ri, Rf, x[1]/1000, x[2]*10**6)  
    
def coil_constrain4(x):
    return (x[3]*cell_length)-(x[4]/2)
    
def coil_constrain5(x):
    return cell_length/2-(x[3]*cell_length+(x[4]/2))


def coil_energy2(x):
    return magneticEnergyDensity_MJm3_1Coil(Ri2, Rf2, x[4]/1000, x[5]*10**6) 


def coil_constrain6(x):
    return (cell_length-4*(rf_length_max+6))/2-((x[3]*cell_length)+(x[4]/2))


def coil_constrain7(x):
    return (x[6]*cell_length)-(x[7]/2)
    
def coil_constrain8(x):
    return cell_length/2-(x[6]*cell_length+(x[7]/2))

def coil_constrain8_c(x):
    return (cell_length-3*(rf_length_max+6))/2-((x[6]*cell_length)+(x[7]/2))
    
def coil_energy3(x):
    return magneticEnergyDensity_MJm3_1Coil(Ri3, Rf3, x[7]/1000, x[8]*10**6) 
    
def coil_constrain9(x):
    return (x[9]*cell_length)-(x[10]/2)
    
def coil_constrain10(x):
    return cell_length/2-(x[9]*cell_length+(x[10]/2))  
    
def coil_energy4(x):
    return magneticEnergyDensity_MJm3_1Coil(Ri4, Rf4, x[9]/1000, x[10]*10**6) 
    
if __name__ == '__main__':
    if mode==1:
        nlc1 = NonlinearConstraint(coil_constrain1,10,+np.inf)
        
        nlc3 = NonlinearConstraint(coil_constrain3,10,+np.inf)
        nlc4 = NonlinearConstraint(coil_energy1,0,150)
        
        bounds = [(0.12,0.22), (300,600), (50,150)]
        constrain = (nlc1, nlc3, nlc4)
        result = differential_evolution(minimize, constraints=constrain, bounds=bounds, popsize=20, polish=False, workers=10, maxiter=250, disp=True)
        
    if mode==2:
        nlc1 = NonlinearConstraint(coil_constrain1,15,+np.inf)
        nlc2 = NonlinearConstraint(coil_constrain2,30,+np.inf)
        
        nlc4 = NonlinearConstraint(coil_constrain4,15,+np.inf)
        nlc5 = NonlinearConstraint(coil_constrain6,30,+np.inf)
        nlc6 = NonlinearConstraint(coil_energy2,0,150)
        nlc7 = NonlinearConstraint(coil_energy1,0,150)
        bounds = [(0.05,0.15), (50,150), (150,300), (0.05,0.25), (100,250), (100,200)]
        constrain = (nlc1, nlc2, nlc4, nlc5, nlc6, nlc7)
        result = differential_evolution(minimize, constraints=constrain, bounds=bounds, popsize=40, polish=False, workers=10, maxiter=250, disp=True)
        
        
    if mode==3:
        nlc1 = NonlinearConstraint(coil_constrain1,15,+np.inf)
        nlc2 = NonlinearConstraint(coil_constrain2,30,+np.inf)
        
        nlc4 = NonlinearConstraint(coil_constrain4,15,+np.inf)
        nlc5 = NonlinearConstraint(coil_constrain5,15,+np.inf)
        nlc6 = NonlinearConstraint(coil_constrain6,30,+np.inf)
        nlc7 = NonlinearConstraint(coil_constrain7,15,+np.inf)
        nlc8 = NonlinearConstraint(coil_constrain8,15,+np.inf)
        nlc9 = NonlinearConstraint(coil_energy3,0,150)
        nlc10 = NonlinearConstraint(coil_energy2,0,150)
        bounds = [(0.06,0.15), (50,150), (150,300), (0.1,0.25), (50,200), (100,250), (0.2,0.35), (150,350), (50,200)]
        constrain = (nlc1, nlc2, nlc4, nlc6, nlc7, nlc8, nlc9, nlc10)
        result = differential_evolution(minimize, constraints=constrain, bounds=bounds, popsize=54, polish=False, workers=10, maxiter=250, disp=True)
    
    if mode==4:
        nlc1 = NonlinearConstraint(coil_constrain1,5,+np.inf)
        nlc2 = NonlinearConstraint(coil_constrain2,10,+np.inf)
        
        nlc4 = NonlinearConstraint(coil_constrain4,5,+np.inf)
        
        nlc6 = NonlinearConstraint(coil_constrain6,10,+np.inf)
        nlc7 = NonlinearConstraint(coil_constrain7,5,+np.inf)
        nlc8 = NonlinearConstraint(coil_constrain8,5,+np.inf)
        nlc9 = NonlinearConstraint(coil_constrain9,5,+np.inf)
        nlc10 = NonlinearConstraint(coil_constrain10,5,+np.inf)
        
        nlc11 = NonlinearConstraint(coil_energy4,0,150)
        nlc12 = NonlinearConstraint(coil_energy3,0,150)
        nlc13 = NonlinearConstraint(coil_energy2,0,150)
        bounds = [(0.06,0.2), (30,200), (100,400), (0.06,0.2), (30,200), (100,300), (0.06,0.35), (40,200), (100,300), (0.06,0.35), (40,300), (50,300)]
        constrain = (nlc1, nlc2, nlc4, nlc6, nlc7, nlc8, nlc9, nlc10, nlc11, nlc12, nlc13)
        result = differential_evolution(minimize, constraints=constrain, bounds=bounds, popsize=72, polish=False, workers=10, maxiter=250, disp=True)
    np.savetxt('result.txt', result.x)

