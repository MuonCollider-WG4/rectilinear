import os
import shutil
import numpy as np
import subprocess
import multiprocessing

pre = '/home/zhurh/new_frequency_after_merge/more_space/stage8_780mm_beta_4cm/'
original_result_filename = 'target_rf.txt'
ref_momentum_list = range(198,196,-1)

target_max =0.5
eps = 0.5
cores_num = 16

def get_all_dirs(present_dir):
    for _,dirs_names,_ in os.walk(present_dir):
        return dirs_names


ncells = 60
region = 55
cells_list = [1, region]
beam_filename = 'beam_stage8.beam'
g4bl_filename = 'cooling_stage8.g4bl'
event_id = []
with open(pre + beam_filename, 'r') as f:
    out = f.readlines()
events_num = len(out) - 3

temp = [1]
for i in range(cores_num):
    if i != cores_num-1:
        temp.append(temp[i] + int(events_num/cores_num))
    else:
        temp.append(events_num)
cores_events = []
for i in range(cores_num):
    cores_events.append([temp[i],temp[i+1]-1])

def run_g4bl(present_dir, events):
    new_loc = present_dir + 'events' + str(events[0])
    os.makedirs(new_loc)
    shutil.copy(present_dir + beam_filename, new_loc)
    shutil.copy(present_dir + g4bl_filename, new_loc)
    os.chdir(new_loc)
    g4bl_cmd = subprocess.Popen('g4bl '+ g4bl_filename + ' first=' + str(events[0]) + ' last=' + str(events[1]) + ' > print.out',cwd='./',shell=True)
    g4bl_cmd.wait()

def find_index(dire):
    index_start_list = []
    index_end_list = []
    with open(dire + 'particles_info.txt', 'r') as f:
        out = f.readlines()
    #for i in range(1,ncells+2):
    for i in cells_list:
        flag1 = 0
        flag2 = 0
        if i!=ncells+1:
            for j in range(4,len(out)):
                if int(out[j-1].strip().split()[0])==0 and int(out[j].strip().split()[4])==i:
                
                    index_start_list.append(j)
                    flag1 = 1
                if int(out[j].strip().split()[4])==i and int(out[j+1].strip().split()[0])==0:
                
                    index_end_list.append(j)
                    flag2 = 1
                if flag1==1 and flag2==1:
                    break
        else:
            for j in range(4,len(out)):
                if int(out[j-1].strip().split()[0])==0 and int(out[j].strip().split()[4])==i:
                
                    index_start_list.append(j)
            index_end_list.append(len(out)-1)
    return index_start_list, index_end_list

def check_regn(path):
    flag1 = 0
    with open(path + 'particles_info.txt', 'r') as f:
        out = f.readlines()
    regn_index = []
    for i in range(3,len(out)):
        regn_index.append(int(out[i].strip().split()[4]))
    if max(regn_index)==ncells + 1:
        flag1 = 1
    flag2 = 1
    with open(path + 'print.out', 'r') as f:
        out = f.readlines()
    for i in range(len(out)):
        if 'G4Exception: No reference' in out[i]:
            flag2 = 0
        if 'G4Exception: Element Error' in out[i]:
            flag2 = 0
    return flag1*flag2
    


def run(present_dir):
    #pool = Pool(cores_num)
    #pool.map(partial(run_g4bl,present_dir), cores_events)
    #pool.close()
    #pool.join()
    process_list = list()
    cores_num = 16
    for i in range(cores_num):
        process_list.append(multiprocessing.Process(target=run_g4bl, args=(present_dir,cores_events[i])))
        
    for process in process_list:
        process.start()
    for process in process_list:
        process.join()
    content = ['#NTuple/Z0 \n', '#Units are ns, meters, GeV/c, Tesla, and V/m \n', '#IEVT IPNUM IPTYP IPFLG JSRG T X Y Z Px Py Pz Bx By Bz Weight Ex Ey Ez SARC POLx POLy POLz \n']
    pre_list = [present_dir + 'events' + str(cores_events[i][0]) + '/' for i in range(cores_num)]
    index_start_list_all = []
    index_end_list_all = []
    flag = 1
    for i in range(len(pre_list)):
        temp = check_regn(pre_list[i])
        flag = flag*temp
    if flag==1:
        for dire in pre_list:
            index_start_list, index_end_list = find_index(dire)
            index_start_list_all.append(index_start_list)
            index_end_list_all.append(index_end_list)
        #for i in range(ncells+1):
        for i in range(len(cells_list)):
            for j in range(len(pre_list)):
                with open(pre_list[j] + 'particles_info.txt', 'r') as f:
                    out = f.readlines()
                if j==0:
                    for k in range(index_start_list_all[j][i]-1, index_end_list_all[j][i]+1):
                        content.append(out[k])
                else:
                    for k in range(index_start_list_all[j][i], index_end_list_all[j][i]+1):
                        content.append(out[k])
        if os.path.exists(present_dir + 'for009.dat'):
            os.remove(present_dir + 'for009.dat')
        with open(present_dir + 'for009.dat', 'w+') as f:
            f.writelines(content)
        os.chdir(pre)
        for dire in pre_list:
            shutil.rmtree(dire)
        cmd = subprocess.Popen('ecalc9f > out.txt', cwd=present_dir, shell=True)
        cmd.wait()
        os.remove(present_dir + 'for009.dat')
        with open(present_dir + 'ecalc9f.dat', 'r') as f:
            out = f.readlines()
        emit_t_start = float(out[13].strip().split()[3])
        emit_l_start = float(out[13].strip().split()[4])
        emit_6d_start = float(out[13].strip().split()[5])
        particles_num_start = float(out[14].strip().split()[12])
        #emit_t_regn = float(out[14+region].strip().split()[3])
        #emit_l_regn = float(out[14+region].strip().split()[4])
        #particles_num_regn = float(out[14+region].strip().split()[12])
        #emit_6d_regn = float(out[14+region].strip().split()[5])
        #pz_regn = float(out[14+region].strip().split()[7])
        emit_t_regn = float(out[-1].strip().split()[3])
        emit_l_regn = float(out[-1].strip().split()[4])
        particles_num_regn = float(out[-1].strip().split()[12])
        emit_6d_regn = float(out[-1].strip().split()[5])
        pz_regn = float(out[-1].strip().split()[7])
        with open(pre + 'select.txt', 'a+') as f:
            target = emit_6d_regn/emit_6d_start + particles_num_start/particles_num_regn
            f.write(str(target) + '\t' + str(emit_t_regn) + '\t' + str(emit_l_regn) + '\t' + str(emit_6d_regn) + '\t' + str(pz_regn) + '\t' + str(particles_num_regn) + '\t' + present_dir + '\n')
        return target
    else:
        os.chdir(pre)
        
        shutil.rmtree(present_dir)
        return np.random.uniform(1000,2000)

def score_func(x):
    ref_momentum = x[-1]
    init_dir = pre 
    present_dir = init_dir + str(ref_momentum) + 'MeV/' + ','.join([str(i) for i in x[:2]]) + '/'
    if os.path.exists(present_dir):
        #print('file exsits')
        present_dir = pre + str(ref_momentum) + 'MeV/' + ','.join([str(i+np.random.uniform(0,1)) for i in x]) + '/'
    try:
        os.makedirs(present_dir)
    except:
        return np.random.uniform(100,200)
    shutil.copy(init_dir + beam_filename, present_dir)
    shutil.copy(init_dir + g4bl_filename, present_dir)
    shutil.copy(init_dir + 'ecalc9f', present_dir)
    shutil.copy(init_dir + 'ecalc9f.inp', present_dir)
    with open(present_dir + g4bl_filename, 'r') as f:
        out = f.readlines()
    parameters = ['rf_grad', 'rf_ph', 'x_off', 'y_off']
    for i in range(len(parameters)):
        for j in range(len(out)):
            if parameters[i] in out[j]:
                elements = out[j].strip().split('=')
                elements[-1] = str(x[i])
                out[j] = '='.join(elements) + '\n'
                break
    os.remove(present_dir + g4bl_filename)
    with open(present_dir + g4bl_filename, 'w') as f:
        f.writelines(out)
    
    run(present_dir)

if __name__ == '__main__':
    for ref_momentum in ref_momentum_list:
        print('now is ' + str(ref_momentum))
        with open(pre + g4bl_filename, 'r') as f:
            out = f.readlines()
        for i in range(len(out)):
            if 'ref_momentum' in out[i]:
                elements = out[i].strip().split('=')
                elements[-1] = str(ref_momentum)
                out[i] = '='.join(elements) + '\n'
                break
        os.remove(pre + g4bl_filename)
        with open(pre + g4bl_filename, 'w') as f:
            f.writelines(out)
        result_filename = str(ref_momentum) + 'MeV_' + original_result_filename
        file_num = 0
        with open(pre + result_filename, 'r') as f:
            out = f.readlines()
        files_before = []
        files_before_index = []
        if not os.path.exists(pre + str(ref_momentum) + 'MeV/'):
            os.makedirs(pre + str(ref_momentum) + 'MeV/')
        dirs = get_all_dirs(pre + str(ref_momentum) + 'MeV/')
        #for i in range(len(dirs)):
            #files_before.append(dirs[i])
        for i in range(len(out)):
            flag = 0
            current_dir_name = out[i].strip().split()[3].split('/')[-1]
            if float(out[i].strip().split()[2]) < target_max:
                if len(files_before)==0:
                    files_before.append(current_dir_name)
                    files_before_index.append(i)
                    file_num+=1
                else:
                    for j in range(len(dirs)):
                        if dirs[j]==current_dir_name:
                            flag = 1
                            break
                    for j in range(len(files_before)):
                        if abs(float(current_dir_name.split(',')[0])-float(files_before[j].split(',')[0])) < eps and abs(float(current_dir_name.split(',')[1])-float(files_before[j].split(',')[1])) < eps:
                            flag = 1
                            break
                    if flag==0:
                        files_before.append(current_dir_name)
                        files_before_index.append(i)
                        file_num+=1
        print(str(len(files_before)) + ' files')
        #print(files_before)
        k = 0
        turn = 0
        while k<len(files_before):
            turn+=1
            print('now turn '+str(turn))
            cores_files = []
            index_end = k+10
            if index_end > len(files_before):
                index_end = len(files_before)
            for i in range(k, index_end):
                cores_files.append([float(files_before[i].split(',')[0]), float(files_before[i].split(',')[1]), float(out[files_before_index[i]].strip().split()[0]), float(out[files_before_index[i]].strip().split()[1]), ref_momentum])
            process_list = list()

            for i in range(len(cores_files)):
                process_list.append(multiprocessing.Process(target=score_func, args=(cores_files[i],), daemon=False))
    
            for process in process_list:
                process.start()
            for process in process_list:
                process.join()
            k+=10

                  



