import os
import subprocess
import numpy as np
import shutil
from scipy.optimize import differential_evolution

pre = '/home/zhurh/new_folder/'
filename = 'real_closed_orbit_fringe_gas.g4bl'
ref_momentum_list = range(194, 197)



def minimize(x, *args):
    init_dir = pre
    os.chdir(init_dir)
    present_dir = pre + 'data_rf/' + ','.join([str(i) for i in x])
    if os.path.exists(present_dir):
        #print('file exsits')
        present_dir = pre + 'data_rf/' + ','.join([str(i+np.random.uniform(0,1)) for i in x])
    try:
        os.makedirs(present_dir)
    except:
        return 10
    shutil.copy(init_dir + filename, present_dir)
    shutil.copy(init_dir + 'find_real_closed_orbit_de.py', present_dir)
    shutil.copy(init_dir + 'beam.dat', present_dir)
    os.chdir(present_dir)
    parameters = ['rf_grad', 'rf_ph']
    with open(filename, 'r') as f:
        out = f.readlines()
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
    #cmd1 = subprocess.Popen('g4bl '+'closed_orbit.g4bl > print.out',cwd='./',shell=True)
    #cmd1.wait()
    cmd2 = subprocess.Popen('python3.8 '+'find_real_closed_orbit_de.py', cwd='./', shell=True)
    cmd2.wait()
    x = np.load('x.npy')
    y = np.load('y.npy')
    dev = np.load('target.npy')
    os.chdir(init_dir)
    shutil.rmtree(present_dir)
    target = (x[0]-args[1])**2 + (y[0]-args[2])**2 + dev[0]**2
    with open(init_dir + str(args[0]) + 'MeV_target_rf.txt', 'a+') as f:
        f.write(str(x[0]) + '\t' + str(y[0]) + '\t' + str(target) + '\t' + present_dir + '\n')
    return target


if __name__ == '__main__':
    x_off_list = np.load(pre + 'x_off_list.npy')
    y_off_list = np.load(pre + 'y_off_list.npy')
    
    bounds = [(22,32), (10,30)]

    k = 0
    for ref_momentum in ref_momentum_list:
        print('now is ' + str(ref_momentum))
        with open(pre + filename, 'r') as f:
            out = f.readlines()
        for i in range(len(out)):
            if 'ref_momentum' in out[i]:
                elements = out[i].strip().split('=')
                elements[-1] = str(ref_momentum)
                out[i] = '='.join(elements) + '\n'
                break
        os.remove(pre + filename)
        with open(pre + filename, 'w') as f:
            f.writelines(out)
        with open(pre + 'beam.dat', 'r+') as f:
            out = f.readlines()
        element = out[3].split()
        
        element[2] = str(0)
        element[3] = str(0)
        element[4] = str(0)
        element[5] = str(ref_momentum)
        out[3] = ' '.join(element)
        os.remove(pre + 'beam.dat')
        with open(pre + 'beam.dat', 'w') as f:
            f.writelines(out)
        with open(pre + filename ,'r') as f:
            out = f.readlines()
        result = differential_evolution(minimize, args=(ref_momentum, x_off_list[k], y_off_list[k]), bounds=bounds, popsize=12, polish=False, workers=10, maxiter=7, disp=True,updating='deferred')
        k = k+1

