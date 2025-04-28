## key for ```emout``` library
- **<mark>`!!key dx=[0.5]`</mark>**: grid spacing in physical units [m]
- **<mark>`!!key to_c=[10000.0]`</mark>**: conversion factor to speed-of-light units

### &esorem
- **`emflag`**  
  - `1` ⇒ Full-electromagnetic treatment  
  - `0` ⇒ Electrostatic approximation  

### &jobcon
- **<mark>`jobnum`</mark>**: flag indicating whether this is a continuous job (`1`) or not (`0`)  
- **<mark>`nstep`</mark>**: total number of time steps  

### &digcon
- **`hdfdigstart`**: step at which HDF diagnostics begin (`0` ⇒ from step 1)  
- **<mark>`ifdiag`</mark>**: interval (in steps) between **field** data outputs  
  - e.g. `100 000` ⇒ write electric/magnetic field, potential, density every 100 000 steps  
- **<mark>`ijdiag`</mark>**: interval (in steps) between **current** data outputs  
  - e.g. `100 000` ⇒ write current density every 100 000 steps  
- **`daverg`**: averaging flag for diagnostics (`1` ⇒ time-averaged)  
- **`ipahdf(1:3)`**: HDF output axes selection (0 = off)  
- **`ipadig(1:3)`**: diagnostic grid size for in-situ outputs (`1024,1024,1024`)  
- **`ipaxyz`**: mask array for X/Y/Z outputs (18‐element flag vector)  
- **`ifxyz(1:7)`**: substep flags for particle diagnostics in X/Y/Z  
- **`ijxyz(1:3)`**: output flags for current in X/Y/Z  
- **`intfoc`**: focus interval for integrated diagnostics (`100`)

### &plasma
- **<mark>`wp(1:2)`</mark>**: electron and ion plasma frequencies (EMSES-U)  
- **<mark>`wc`</mark>**: electron cyclotron frequency (EMSES-U)  
- **`cv`**: speed of light (EMSES-U)  

### &tmgrid
- **<mark>`dt`</mark>**: time step width (EMSES-U)  
- **<mark>`nx, ny, nz`</mark>**: number of grid points in the _x_, _y_, and _z_ directions  

### &intp
- **<mark>`nspec`</mark>**: number of plasma species  
- **<mark>`nfbnd, npbnd`</mark>**: boundary treatment flags for fields and particles  
  - `0` ⇒ periodic  
  - `2` ⇒ free  
- **<mark>`mtd_vbnd`</mark>**: boundary condition for potential  
  - `0` ⇒ periodic  
  - `1` ⇒ Dirichlet  
  - `2` ⇒ Neumann  
- **<mark>`qm(1:2)`</mark>**: charge-to-mass ratios (EMSES-U)  
- **<mark>`npin(1:2)`</mark>**: initial number of macro-particles per species  
- **`np(1:2)`**: total macro-particles buffer size per species
- **<mark>`path(1:2)`</mark>**: thermal velocities along the static _B_-field (EMSES-U)  
- **<mark>`peth(1:2)`</mark>**: thermal velocities perpendicular to the _B_-field (EMSES-U)  
- **<mark>`vdri(1:2)`</mark>**: magnitudes of bulk flow velocities (EMSES-U)  
- **<mark>`vdthz(1:2), vdthxy(1:2)`</mark>**: flow direction angles (degrees)  

### &ptcond
#### <mark>Geotype Boundaries</mark>
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

#### [finbound](https://github.com/Nkzono99/finbound) Boundaries
- **`boundary_type`**: inner boundary geometry  
  - `"flat-surface"` (others: `"rectangle-hole"`, `"cylinder-hole"`, …)  
- **`zssurf`**: ground surface _z_-height
- **`xlrechole(1:2), xurechole(1:2)`, …**: hole limits for rectangular hole
- **`rcurv`**: hyperboloid curvature ratio

### &mpi
- **<mark>`nodes(1:3)`</mark>**: number of MPI processes along the _x_, _y_, and _z_ axes  

### &gradema
- **`grad_coef`**: acceleration coefficient for surface charging
