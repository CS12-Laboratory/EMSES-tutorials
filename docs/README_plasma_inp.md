## key for ```emout``` library
- **`!!key dx=[0.5]`**: grid spacing in physical units [m]
- **`!!key to_c=[10000.0]`**: conversion factor to speed-of-light units

### &esorem
- **`emflag`**  
  - `1` ⇒ Full-electromagnetic treatment  
  - `0` ⇒ Electrostatic approximation  

### &jobcon
- **`jobnum`**: flag indicating whether this is a continuous job (`1`) or not (`0`)  
- **`nstep`**: total number of time steps  

### &digcon
- **`hdfdigstart`**: step at which HDF diagnostics begin (`0` ⇒ from step 1)  
- **`ifdiag`**: interval (in steps) between **field** data outputs  
  - e.g. `100 000` ⇒ write electric/magnetic field, potential, density every 100 000 steps  
- **`ijdiag`**: interval (in steps) between **current** data outputs  
  - e.g. `100 000` ⇒ write current density every 100 000 steps  
- **`daverg`**: averaging flag for diagnostics (`1` ⇒ time-averaged)  
- **`ipahdf(1:3)`**: HDF output axes selection (0 = off)  
- **`ipadig(1:3)`**: diagnostic grid size for in-situ outputs (`1024,1024,1024`)  
- **`ipaxyz`**: mask array for X/Y/Z outputs (18‐element flag vector)  
- **`ifxyz(1:7)`**: substep flags for particle diagnostics in X/Y/Z  
- **`ijxyz(1:3)`**: output flags for current in X/Y/Z  
- **`intfoc`**: focus interval for integrated diagnostics (`100`)

### &plasma
- **`wp(1:2)`**: electron and ion plasma frequencies (EMSES-U)  
- **`wc`**: electron cyclotron frequency (EMSES-U)  
- **`cv`**: speed of light (EMSES-U)  

### &tmgrid
- **`dt`**: time step width (EMSES-U)  
- **`nx, ny, nz`**: number of grid points in the _x_, _y_, and _z_ directions  

### &intp
- **`nspec`**: number of plasma species  
- **`nfbnd, npbnd`**: boundary treatment flags for fields and particles  
  - `0` ⇒ periodic  
  - `2` ⇒ free  
- **`mtd_vbnd`**: boundary condition for potential  
  - `0` ⇒ periodic  
  - `1` ⇒ Dirichlet  
  - `2` ⇒ Neumann  
- **`qm(1:2)`**: charge-to-mass ratios (EMSES-U)  
- **`npin(1:2)`**: initial number of macro-particles per species  
- **`np(1:2)`**: total macro-particles buffer size per species
- **`path(1:2)`**: thermal velocities along the static _B_-field (EMSES-U)  
- **`peth(1:2)`**: thermal velocities perpendicular to the _B_-field (EMSES-U)  
- **`vdri(1:2)`**: magnitudes of bulk flow velocities (EMSES-U)  
- **`vdthz(1:2), vdthxy(1:2)`**: flow direction angles (degrees)  

### &ptcond
- **`npc`**: number of solid bodies  
- **`npcg`**: number of conducting bodies  
- **`pcgs, ccgs`**: grouping definitions for bodies forming a single conductor  
- **`mtd_vchg`**: treatment of body potential  
  - `0` ⇒ floating  
  - `−1` ⇒ fixed  
- **`pfixed`**: fixed body potential (used when `mtd_vchg = -1`) (EMSES-U)  
- **`geotype`**: body shape  
  - `0`, `1` ⇒ rectangular  
  - `2` ⇒ cylinder  
  - `3` ⇒ sphere  
- **`bdyalign, bdyradius, bdyedge, bdycoord`**: parameters defining cylinder/sphere geometry  
- **`{x,y,z}{l,u}pc`**: lower/upper coordinates for rectangular geometry  

- **`boundary_type`**: inner boundary geometry  
  - `"flat-surface"` (others: `"rectangle-hole"`, `"cylinder-hole"`, …)  
- **`zssurf`**: ground surface _z_-height
- **`xlrechole(1:2), xurechole(1:2)`, …**: hole limits for rectangular hole
- **`rcurv`**: hyperboloid curvature ratio

### &mpi
- **`nodes(1:3)`**: number of MPI processes along the _x_, _y_, and _z_ axes  

### &gradema
- **`grad_coef`**: acceleration coefficient for surface charging
