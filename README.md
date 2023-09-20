# rectilinear (Edited by Ruihu Zhu)
These are lattice files for a 10-stage rectilinear cooling channel. These files are the basis for my future NIMA paper. G4Beamline-3.08 is used.
The whole simulation is done stage by stage. Once you have run the simulation for a stage, you will get a 'for009.dat'-type file and then you can use ecalc9f to analyze the beam properties.

1. Folder name: 
For example, 'stage1_2300mm_beta_35cm' means that the length of each cooling cell in stage1 is 2300mm and the beta value at the wedge is 35cm.

2. Lattice file:  
The 'param -unset first' and 'param -unset last' are used to control the event number because I write a parallel computing code in Python which needs these two params. You may want to comment these two in the 'beam' command to run the code.
The fringe field of the dipole magnet is a simple quadratic function now.
'param mode' means the number of solenoid pairs in one cell. Since for now each cell has only one pair of solenoids, the mode is one.
The window material for wedge and RF are Be.

3.Input beam file for each stage:
Its name is 'beam_stage.... .beam'. Please note the input beam file of the next stage is extracted from a certain region of the former stage. The extracted region index in the ecalc9f file for the 10 stages is 26, 35, 46, 45, 76, 78, 75, 67, 70, 56.

4. Emittance output file for each stage:
Its name is 'ecalc9f_...' obtained from the program 'ecalc9f' which is used in MAP. Same as the input beam, you should only look at the emittance from region 1 to the extracted region index as shown above.

5. for009.dat for each stage:
This type of file is the output beam at the end of each cooling cell. It can be used to calculate the emittance by ecalc9f and obtain the input beam for the next stage by extreg9

