import os
import shutil
import numpy as np
import subprocess
from scipy.optimize import differential_evolution
import matplotlib.pyplot as plt
import scienceplots


snake = 0
pre = '/home/zhurh/new_folder/'
cell_length = 630
pz = [200, 210, 190] #range(194, 197) #[200, 210, 190]
cal_disp = 1


def minimize(x, *args):
    init_dir = pre
    os.chdir(init_dir)
    present_dir = pre + 'closed_orbit/' + ','.join([str(i) for i in x])
    if os.path.exists(present_dir):
        #print('file exsits')
        present_dir = '/home/zhurh/new_folder/' + ','.join([str(i+np.random.uniform(0,1)) for i in x])
    try:
        os.makedirs(present_dir)
    except:
        return np.random.uniform(100,200)
    shutil.copy(init_dir + 'closed_orbit.g4bl', present_dir)
    #shutil.copy(init_dir + 'coil.dat', present_dir)
    #shutil.copy(init_dir + 'testcoil2.dat', present_dir)
    shutil.copy(init_dir + 'beam.dat', present_dir)
    #shutil.copy(init_dir + 'for040.dat', present_dir)
    os.chdir(present_dir)
    with open('beam.dat', 'r') as f:
        out = f.readlines()
    element = out[3].split()
    element[0] = str(x[0])
    element[1] = str(x[1])
    element[2] = str(cell_length)
    if snake:
        element[3] = str(x[2])
        element[4] = str(x[3])
    else:
        element[3] = str(0) 
        element[4] = str(0) 
    element[5] = str(args[0][args[1]])
    out[3] = ' '.join(element)
    os.remove('beam.dat')
    with open('beam.dat', 'w') as f:
        f.writelines(out)
    g4bl_cmd = subprocess.Popen('g4bl '+'closed_orbit.g4bl > print.out',cwd='./',shell=True)
    g4bl_cmd.wait()
    with open('final.txt', 'r') as f:
        out = f.readlines()
    if len(out)==3:
        x_final = float(out[2].split()[0])
        y_final = float(out[2].split()[1])
        px_final = float(out[2].split()[3])
        py_final = float(out[2].split()[4])
        os.chdir(init_dir)
        shutil.rmtree(present_dir)
        if snake:
            return (x[0]-x_final)**2 + (x[1]-y_final)**2 + (px_final-x[2])**2 + (py_final-x[3])**2
        else:
            return (x[0]-x_final)**2 + (x[1]-y_final)**2 + px_final**2 + py_final**2
    else:
        os.chdir(init_dir)
        shutil.rmtree(present_dir)
        return np.random.uniform(100,200)

if __name__ == '__main__':
    dir = '/home/zhurh/new_folder/'
    x_off_list =[]
    y_off_list = []
    os.chdir(dir)
    if snake:
        bounds = [(-50,50),(-50,50),(-20,20),(-20,20)]
        psize = 20
    else:
        bounds = [(-10,2),(-10,2)]
        psize = 10
    
    
    for i in range(len(pz)):
        print('now is ' + str(pz[i]))
        result = differential_evolution(minimize, args=(pz, i), popsize=psize, maxiter=20, bounds=bounds, disp=True, polish=False,workers=16)
        x_off_list.append(result.x[0])
        y_off_list.append(result.x[1])

        if cal_disp:
            with open('beam.dat', 'r+') as f:
                out = f.readlines()
            element = out[3].split()
            element[0] = str(result.x[0])
            element[1] = str(result.x[1])
            element[2] = str(cell_length)
            if snake:
                element[3] = str(result.x[2])
                element[4] = str(result.x[3])
            else:
                element[3] = str(0) 
                element[4] = str(0) 
            element[5] = str(pz[i])
            out[3] = ' '.join(element)
            os.remove('beam.dat')
            with open('beam.dat', 'w') as f:
                f.writelines(out)
            g4bl_cmd = subprocess.Popen('g4bl '+'closed_orbit.g4bl > print.out',cwd='./',shell=True)
            g4bl_cmd.wait()
            if not os.path.exists('Ev1Trk1_' + str(i) + '.txt'):
                os.rename('Ev1Trk1.txt', 'Ev1Trk1_' + str(i) + '.txt')
            else:
                os.remove('Ev1Trk1_' + str(i) + '.txt')
                os.rename('Ev1Trk1.txt', 'Ev1Trk1_' + str(i) + '.txt')
    if not cal_disp:
        np.save(pre + 'x_off_list',x_off_list)
        np.save(pre + 'y_off_list',y_off_list)
    print(x_off_list)
    print(y_off_list)

    if cal_disp:  
        label = ['200 MeV/c','210 MeV/c','190 MeV/c']
        color = ['g','k','b']
        x = []
        y = []
        px = []
        py = []
        closed_orbit_data = []
        with plt.style.context(['science', 'no-latex']):
          plt.figure(dpi=200)
          #plt.subplot(1,2,1)
          for i in range(len(pz)):
              x_sub = []
              y_sub = []
              px_sub = []
              py_sub = []
              z = []
              with open('Ev1Trk1_' + str(i) + '.txt', 'r') as f:
                  out = f.readlines()
              for j in range(3,len(out)):
                  if abs(float(out[j].split()[2]) - 2*cell_length) < 2: #0.1:
                      index = j
                      break
              for j in range(3,index+1):
                  x_sub.append(float(out[j].split()[0]))
                  y_sub.append(float(out[j].split()[1]))
                  px_sub.append(float(out[j].split()[3]))
                  py_sub.append(float(out[j].split()[4]))
                  z.append(float(out[j].split()[2])/1000)
              plt.plot([i-z[0] for i in z],x_sub,color=color[i],label=label[i])
              plt.plot([i-z[0] for i in z],y_sub,color=color[i],linestyle='--')
              x.append(x_sub)
              y.append(y_sub)
              px.append(px_sub)
              py.append(py_sub)
              if i==0:
                  closed_orbit_data = np.vstack((np.array(x_sub).T, np.array(y_sub).T))
              else:
                  closed_orbit_data = np.vstack((closed_orbit_data, np.array(x_sub).T, np.array(y_sub).T))
          np.savetxt(pre + 'closed_orbit_data.txt', closed_orbit_data.T)
          plt.legend(loc='upper right',fontsize=10, frameon=True, fancybox=False, edgecolor='black')
          plt.xlabel('z (m)', fontsize=12)
          plt.ylabel('Closed orbit (mm)', fontsize=12)
          plt.show()
          Dx_all = []
          Dy_all = []
          Dpx_all = []
          Dpy_all = []
          for i in range(1,len(pz)):
              Dx_all_sub = []
              Dy_all_sub = []
              Dpx_all_sub = []
              Dpy_all_sub = []
              for j in range(len(z)):
                  Dx_all_sub.append((x[i][j] - x[0][j])/((pz[i]-pz[0])/pz[0]))
                  Dy_all_sub.append((y[i][j] - y[0][j])/((pz[i]-pz[0])/pz[0]))
                  Dpx_all_sub.append(px[i][j]/pz[i]-px[0][j]/pz[0])
                  Dpy_all_sub.append(py[i][j]/pz[i]-py[0][j]/pz[0])
              Dx_all.append(Dx_all_sub)
              Dy_all.append(Dy_all_sub)
              Dpx_all.append(Dpx_all_sub)
              Dpy_all.append(Dpy_all_sub)
          Dx_all_np = np.array(Dx_all)
          Dy_all_np = np.array(Dy_all)
          Dx = np.mean(Dx_all_np, axis=0)
          Dy = np.mean(Dy_all_np, axis=0)
          Dpx_all_np = np.array(Dpx_all)
          Dpy_all_np = np.array(Dpy_all)
          Dpx = np.mean(Dpx_all_np, axis=0)
          Dpy = np.mean(Dpy_all_np, axis=0)
          print('Dx='+str(Dx[0]))
          print('Dy='+str(Dy[0]))
          dispersion_data = np.vstack((np.array(z).T, np.array(Dx).T, np.array(Dy).T))
          np.savetxt(pre + 'dispersion_data.txt', dispersion_data.T)
          #plt.subplot(1,2,2)
          plt.plot([i-z[0] for i in z],Dx,color='r',label='Dx')
          plt.plot([i-z[0] for i in z],Dy,color='b',label='Dy')
          plt.legend(loc='upper right',fontsize=10, frameon=True, fancybox=False, edgecolor='black')
          plt.xlabel('z (m)', fontsize=12)
          plt.ylabel('Dispersion (mm)', fontsize=12)
          plt.show()
  
          plt.plot([i-z[0] for i in z],Dpx,color='r',label='Dpx')
          plt.plot([i-z[0] for i in z],Dpy,color='b',label='Dpy')
          plt.legend(loc='upper right',fontsize=10, frameon=True, fancybox=False, edgecolor='black')
          plt.xlabel('z (m)')
          plt.ylabel('angular dispersion')
          plt.show()