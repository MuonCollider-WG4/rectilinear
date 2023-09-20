# rectilinear
These are lattice files containing 10 stages rectilinear cooling channel. These files are the basis for my future NIMA paper.
1. Folder name: 
For example, 'stage1_2300mm_beta_35cm' means that the length each cooling cell in stage1 is 2300mm and the beta value at the wedge is 35cm.
2. Lattice file:  
The 'param -unset first' and 'param -unset last' are used to control the event number because I write a parallel computing code in Python which needs these two params. You may want to comment these two in the 'beam' command to run the code.
The fringe field of the dipole magnet is a simple quadratic function now.
'param mode' means the number of solenoid pairs in one cell. Since for now each cell has only one pair of solenoids, the mode is one.
The window material for wedge and RF are Be.
3. Emittance output file:
Its name is 'ecalc9f_...' obtained from the program 'Ecalc9f' which is used in MAP.
