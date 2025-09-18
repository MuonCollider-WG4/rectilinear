import os
import shutil
import numpy as np
import subprocess
from scipy.optimize import differential_evolution, NonlinearConstraint

filename = 'real_closed_orbit_fringe_gas.g4bl'


def minimize(x):
    init_dir = os.getcwd()
    os.chdir(init_dir)
    present_dir = init_dir + '/closed_orbit/' + ','.join([str(i) for i in x])
    if os.path.exists(present_dir):
        #print('file exsits')
        present_dir = init_dir + '/closed_orbit/' + ','.join([str(i+np.random.uniform(0,1)) for i in x])
    try:
        os.makedirs(present_dir)
    except:
        return 10
    shutil.copy(init_dir + '/' + filename, present_dir)
    shutil.copy(init_dir + '/beam.dat', present_dir)
    #shutil.copy(init_dir + '/coil.dat', present_dir)
    os.chdir(present_dir)
    with open('beam.dat', 'r+') as f:
        out = f.readlines()
    element = out[3].split()
    element[0] = str(x[0])
    element[1] = str(x[1])
    #element[2] = str(0)
    #element[3] = str(0)
    #element[4] = str(0)
    #element[5] = str(args[0][args[1]])
    out[3] = ' '.join(element)
    os.remove('beam.dat')
    with open('beam.dat', 'w') as f:
        f.writelines(out)
    with open(filename ,'r') as f:
        out = f.readlines()
    parameters = ['x_off', 'y_off']
    for i in range(len(parameters)):
        for j in range(len(out)):
            if parameters[i] in out[j]:
                elements = out[j].strip().split('=')
                elements[-1] = str(x[i])
                out[j] = '='.join(elements) + '\n'
                break
    os.remove(filename)
    with open(filename, 'w') as f:
        f.writelines(out)
    g4bl_cmd = subprocess.Popen('g4bl '+filename + ' > print.out',cwd='./',shell=True)
    g4bl_cmd.wait()
    with open('final.txt', 'r') as f:
        out = f.readlines()
    if len(out)==6:
        pz_start = float(out[4].split()[5])
        x_final = float(out[5].split()[0])
        y_final = float(out[5].split()[1])
        px_final = float(out[5].split()[3])
        py_final = float(out[5].split()[4])
        pz_final = float(out[5].split()[5])
        os.chdir(init_dir)
        shutil.rmtree(present_dir)
        return (x[0]-x_final)**2 + (x[1]-y_final)**2 + px_final**2 + py_final**2 + (pz_final-pz_start)**2
    else:
        os.chdir(init_dir)
        shutil.rmtree(present_dir)
        return np.random.uniform(100,200)

if __name__ == '__main__':
    bounds = [(-10,-0.01),(-10,-0.01)]
    
    x = []
    y = []
    target = []
    
    result = differential_evolution(minimize, popsize=12, maxiter=20, bounds=bounds, disp=False, polish=False,workers=16,updating='deferred')
    x.append(result.x[0])
    y.append(result.x[1])
    target.append(result.fun)
    np.save('x',x)
    np.save('y',y)
    np.save('target',target)