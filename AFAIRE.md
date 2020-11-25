# Still to be done
- Dir Inj
    - calibration
    - superposition 
- LC-MS
    - 2D pp
- 2D-MS
    - processing.py / param.mscf: raw -> msh5
        - formulaire de param
    - pp
    - easydisplay2D.ipynb
- Imaging
- CLIO

# bugs - à corriger
- peak picking is buggy when in zoom mode
- add forum in about

# todo in processing 2D
tempdir
F1_specwidth
highmass
Apex/Solarix/Auto
mp / mpi / False

# todo display2D
- get  diagonal
    - diag =  zeros(sizef2)
    - for i in len(diag):
        mz  = diag.itomz(i)
        diag[i] = 2D[F1.mztoi(mz),  F2.mztoi(mz)]

# todo géné
- tool for listing set of MS data-sets
    - using FI.filetype() and FI.build_list()