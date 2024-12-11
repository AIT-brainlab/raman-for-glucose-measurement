# PILOT dataset

This is the dataset contains a raman spectra of the OGTT experiment.

The structure of the dataset is followed `s<id>/`.
Inside the folder contains raman spectra with the name format of `<prefix>_<grating>_<laser_wavelength> nm_<exposure> s_<accumulation>_<year>_<month>_<day>_<hour>_<minute>_<second>_01.txt`.

The glucose concentration (glycemic) of each participant can be found in `s<id>.csv`.
The file is a tabular data with two columns as `time` and `glucose`.

Please note that each OGTT experiment do not have the save number of data points and resolution.

- `s1` has 26 data points of both Raman and glycemic.
- `s2` has 32 data points of Raman and 11 of glycemic.


The raman is collected with this configuration

| Item             | Parameter     |
|------------------|---------------|
| Laser wavelength | 785 nm        |
| Laser Power      | 10.0 / 358 mW |
| Lens             | 10x           |
| Slit width       | 0.625 mm      |
| Grating          | 600           |
| Exposure         | 60 s          |
| Accumuation      | 1             |

Measurement site is the tip of index, middle, or ring finger of either left or right hand.