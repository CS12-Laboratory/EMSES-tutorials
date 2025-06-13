# EMSES Parameter File: `plasma.inp`

**Note:** Include the following unit-conversion key directive at the very top of `plasma.inp` to normalize grid spacing and light speed:

```fortran
!!key dx=[0.5], to_c=[10000.0]
```

---

## Table of Contents

1. [Unit System and Conversion](#unit-system-and-conversion)
2. [Namelist Groups Overview](#namelist-groups-overview)
3. [Detailed Parameter Reference](#detailed-parameter-reference)

   * [\&esorem](#esorem)
   * [\&jobcon](#jobcon)
   * [\&digcon](#digcon)
   * [\&plasma](#plasma)
   * [\&tmgrid](#tmgrid)
   * [\&mpi](#mpi)
   * [\&intp](#intp)
   * [\&ptcond](#ptcond)
   * [\&gradema](#gradema)
   * [\&dipole](#dipole)
   * [\&emissn](#emissn)
4. [Finbound Extension (Additional Parameters)](#finbound-extension-additional-parameters)
5. [Example `plasma.inp`](#example-plasmainp)

---

## Unit System and Conversion

EMSES uses a normalized unit system to simplify computations and reduce numerical cost. Four primary conversions are fixed:

* **Grid spacing** (`dx`) \[m] → 1
* **Speed of light** (`cv`) \[m/s] → 10000
* **Vacuum permittivity** (`epsilon_0`) \[F/m] → 1
* **Electron charge-to-mass ratio** (`q/m`) \[C/kg] → –1

All other physical quantities scale consistently according to these base units. Conversion formula:

```text
X_EMSES = X_phys × C
```

where `C` derives from the chosen normalizations. See the `emout` conversion module or Excel sheet for explicit coefficients.

---

## Namelist Groups Overview

* `&esorem`: Field solver mode
* `&jobcon`: Job control
* `&digcon`: Diagnostic output control
* `&plasma`: Plasma properties
* `&tmgrid`: Time & spatial grid
* `&mpi`: MPI decomposition
* `&intp`: Particle integration & initialization
* `&ptcond`: Surface/conductor boundary parameters
* `&gradema`: Surface charging acceleration
* `&dipole`: Embedded dipole source
* `&emissn`: Particle emission

---

## Detailed Parameter Reference

### \&esorem

**Defined in `namels.f90`.**

* `emflag` (integer): `1`=full EM, `0`=electrostatic

### \&jobcon

* `jobnum(2)` (integer): `[new/continue, always 1]`
* `nstep` (integer): total time steps

### \&digcon

Controls diagnostics (HDF5, current, particle, etc.). Key parameters:

* `hdfdigstart`, `hdfdigend` (integer): start/end step for HDF output
* `ifdiag`, `ijdiag` (integer): field/current output intervals
* `ipadig(1:3)` (integer): in-situ grid size
* `ipahdf(1:3)`, `ipaxyz(18)`, `ifxyz(1:7)`, `ijxyz(1:3)` (integer arrays): masks and flags
* `isort`, `itchck` (integer): sorted output, checkpoint interval
* `ildig`, `ikdiag`, `ivdiag`, `irhsp`, `imdig` (integer): specialized diagnostics

### \&plasma

Fundamental plasma parameters (in EMSES units):

* `wp(1:nspec)` (real): plasma frequency per species
* `wc` (real): cyclotron frequency
* `cv` (real): normalized light speed

### \&tmgrid

Time & spatial grid:

* `dt` (real): time-step size
* `nx, ny, nz` (integer): grid points
* `dx` (real): grid spacing

### \&mpi

MPI domain decomposition:

* `nodes(1:3)` (integer): processes along x, y, z

### \&intp

Particle integration & initialization:

* `nspec` (integer): number of species
* `nfbnd, npbnd` (integer): field/particle boundary (`0`=periodic, `2`=free)
* `mtd_vbnd` (integer): potential BC (`0`=periodic, `1`=Dirichlet, `2`=Neumann)
* `qm(1:nspec)`, `npin(1:nspec)`, `np(1:nspec)` (real/integer arrays): q/m, initial/buffer particle counts
* `path(1:nspec)`, `peth(1:nspec)` (real arrays): thermal velocities
* `vdri(1:nspec)`, `vdthz(1:nspec)`, `vdthxy(1:nspec)` (real arrays): bulk-flow magnitudes & angles

### \&ptcond

Surface & conductor boundaries.

#### Basic Settings

* `npc`, `npcg` (integer): counts of solid/conductor bodies
* `pcgs`, `ccgs` (integer arrays): conductor grouping
* `mtd_vchg` (integer): potential treatment (`0`=float, `-1`=fixed)
* `pfixed` (real): fixed potential value

#### Body Geometry

* `geotype` (integer): `0/1`=rectangular, `2`=cylinder, `3`=sphere
* `bdyalign` (integer): cylinder axis (`1`=x, `2`=y, `3`=z)
* `bdyradius`, `bdyedge`, `bdycoord` (real arrays): shape parameters
* `{x,y,z}{l,u}pc` (real): rectangular bounds

#### Finbound Extension

*(See next section)*

### \&gradema

* `grad_coef` (real): acceleration coef. for surface charging

### \&dipole

Embedded magnetic dipole source:

* `md` (real): dipole field magnitude
* `mdx, mdy, mdz` (integer): grid indices of dipole center
* `mddir` (integer): orientation (`1`=x, `2`=y, `3`=z)

### \&emissn

Particle emission settings:

* `nflag_emit` (integer): `0`=external, `1/2`=internal
* `nepl` (integer): # of emission surfaces
* `curf` (real): base current density
* `curfs(1:nepl)` (real): per-surface overrides
* `nemd` (integer): direction/surface (`±1`=x, `±2`=y, `±3`=z)
* `xmaxe, xmine, ymaxe, ymine, zmaxe, zmine` (integer arrays): emission-region bounds
* `pe_ray_cast` (integer): solar-illumination-driven emission flag

---

## Finbound Extension (Additional Parameters)

All following parameters belong to the **\&ptcond** group and are implemented via the `finbound` module (see `allcom.f90` and `particle_collision.f90`). They enable precise control over complex inner boundary geometries.

* **boundary\_type** (character(30))

  * Specifies the overall inner-boundary geometry for each body.
  * Supported values:

    * `none` (no special inner boundary)
    * `flat-surface` (planar cut)
    * `rectangle-hole`, `cylinder-hole`, `hyperboloid-hole`, `ellipsoid-hole` (hole through a surface)
    * `rectanglex`, `rectangley`, `rectanglez` (rectangular prism in X/Y/Z)
    * `circlex`, `circley`, `circlez` (cylindrical cut aligned with an axis)
    * `cuboid` (axis-aligned block)
    * `diskx`, `disky`, `diskz` (flat disk perpendicular to an axis)
    * `complex` (user-defined or combined shapes)

* **nboundary\_types** (integer)

  * Defines the maximum number of distinct sub-boundary regions (default: 10).
  * Determines the fixed size of all geometry arrays below.

* **boundary\_types(1\:nboundary\_types)** (character(30) array)

  * Parsed tokens from `boundary_type`, e.g. splitting `rectangle-hole` into `"rectangle"` and `"hole"`.
  * Unused entries default to `"none"`.

**Geometry Parameter Arrays** (each dimensioned by `nboundary_types`):

* **cylinder\_origin(3, nbt)**

  * Center coordinates `[x, y, z]` of each cylindrical sub-boundary.

* **cylinder\_radius(nbt)**

  * Radius of each cylinder.

* **cylinder\_height(nbt)**

  * Height (extent along axis) of each cylinder.

* **rectangle\_shape(6, nbt)**

  * Six-element array: `(x_lower, x_upper, y_lower, y_upper, z_lower, z_upper)`, defining each rectangular prism.

* **cuboid\_shape(6, nbt)**

  * Same format as `rectangle_shape`, used interchangeably for cuboid bodies.

* **sphere\_origin(3, nbt)**

  * Center `[x, y, z]` of each spherical sub-boundary.

* **sphere\_radius(nbt)**

  * Radius of each sphere.

* **circle\_origin(3, nbt)**

  * Center `[x, y, z]` of each circular hole (disk) or cylindrical cut.

* **circle\_radius(nbt)**

  * Radius of each circular feature.

* **disk\_origin(3, nbt)**

  * Center `[x, y, z]` of each flat disk surface.

* **disk\_height(nbt)**

  * Plane position (thickness) at which each disk lies.

* **disk\_radius(nbt)**

  * Outer radius of each disk.

* **disk\_inner\_radius(nbt)**

  * Inner radius (hole) of each annular disk.

* **plane\_with\_circle\_hole\_zlower(nbt)**

  * Lower z-coordinate of the plane containing a circular hole.

* **plane\_with\_circle\_hole\_height(nbt)**

  * Thickness of that plane region.

* **plane\_with\_circle\_hole\_radius(nbt)**

  * Radius of the circular hole in the plane.

*(Here, `nbt` denotes `nboundary_types`.)*

---

## Example `plasma.inp`

```fortran
&esorem
  emflag = 0
&end

&jobcon
  jobnum = 0, 1
  nstep  = 100000
&end

&plasma
  wp = 0.5950738d0, -1.0d0
  wc = 0.0d0
  cv = 10000.0d0
&end

&tmgrid
  dt = 0.01d0
  nx = 128; ny = 128; nz = 128
  dx = 1.0d0
&end

... (continued)
```

Refer to the EMSES user guide and source-code comments for further configuration details and advanced options.
