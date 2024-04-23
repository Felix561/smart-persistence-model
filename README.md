# smart persistence model (SPM) Implementation 

### Goal: 
easy and Standartesierte Python implimenatiton of the smart persistence model to use as a Benchmark Model for short term PV-Power forcast. This is one of the most used Refferenz models in the short term PV Power Forcast Research. [1]-[4]
My Implimentation aims to Standatesise the Benchmarking of Forcast Models in thise Field because i cant find an easy implimentation on github so fare... 


### About the smart persistence model:
(Diese Erklärung wurde aus der Doktorarbeit von Yuhao Nie [1] entnommen. Es wurden allerdings teile verändert und ergänzt.)

Smart persistence model is the mostly used reference model in solar forecasting, which assumes the relative output, measured as the ratio of the actual PV output to the theoretical PV output under clear sky conditions, stays unchanged for the forecast horizon (denoted as T for illustration below):

\[ k_{clr} = \frac{P(t + T)}{P_{clr}(t + T)} = \frac{P(t)}{P_{clr}(t)} \] (1)

where \( k_{clr} \) represents the relative output, or formally named as clear sky index, \( P \) is the actual PV output, and \( P_{clr} \) is the theoretical PV output.

At any given time stamp, \( P_{clr} \) can be estimated by a clear sky model based on sun angles and PV panel orientations [5]:

\[ P_{clr}(t) = I_m A_e \{ \cos \epsilon \cos \chi(t) + \sin \epsilon \sin \chi(t) \cos[\xi(t) - \zeta] \} \] (2)

Where \( I_m \) is the maximum solar irradiance; \( A_e \) is the effective PV panel area, which can be obtained from a least square fit with the real panel output of 12 clear sky days (details can be found in study by Sun [4]); \( \epsilon \) and \( \zeta \) are elevation and azimuth angles of the solar PV arrays; \( \chi(t) \) and \( \xi(t) \) are the zenith and azimuth angle of the sun, which can be estimated for any minute of the year from the empirical functions provided in the textbook by da Rosa [5]. Alternertevlie the zenith and azimuth angle can be estimated using the NREL SPA algorithm [6] witch can be implementet in python using the pvlib Libary. [7]

Based on Equation 2, T-minute-ahead PV output can be estimated by smart persistence model as:

\[ \hat{P}(t + T) = \frac{P(t)}{P_{clr}(t)} \times P_{clr}(t + T) \] (3)









Quellen:

[1] Yuhao Nie, "Short-term solar forecasting from all-sky images using deep learning," Stanford University Libraries, 2023. Verfügbar unter: [https://purl.stanford.edu/bm790hj4850](https://purl.stanford.edu/bm790hj4850).

[2] Yuhao Nie, Eric Zelikman, Andrea Scott, Quentin Paletta, Adam Brandt, "SkyGPT: Probabilistic ultra-short-term solar forecasting using synthetic sky images from physics-constrained VideoGPT," Advances in Applied Energy, Volume 14, 2024, 100172, ISSN 2666-7924. Verfügbar unter: [https://doi.org/10.1016/j.adapen.2024.100172](https://doi.org/10.1016/j.adapen.2024.100172).

[3] Yuchi Sun, Vignesh Venugopal, Adam R. Brandt, "Short-term solar power forecast with deep learning: Exploring optimal input and output configuration," Solar Energy, Volume 188, 2019, Seiten 730-741, ISSN 0038-092X. Verfügbar unter: [https://doi.org/10.1016/j.solener.2019.06.041](https://doi.org/10.1016/j.solener.2019.06.041). 

[4] Yuchi Sun, "Short-term solar forecast using convolutional neural networks with sky images," Stanford University Libraries, 2019. Verfügbar unter: [Link zur Ressource](https://purl.stanford.edu/fm704js1179).

[5] Aldo da Rosa. *Fundamentals of Renewable Energy Processes.* 2009. ISBN 9780123746399. doi: [10.1016/B978-0-12-374639-9.X0001-2](https://doi.org/10.1016/B978-0-12-374639-9.X0001-2).

[6] Reda, I., & Andreas, A. Solar Position Algorithm for Solar Radiation Applications (Revised). United States: N. p., 2008. Web. doi:[10.2172/15003974](https://doi.org/10.2172/15003974).

[7] W. F. Holmgren, C. W. Hansen, & M. A. Mikofski, “pvlib python: a python package for modeling solar energy systems,” Journal of Open Source Software, Jg. 3, Nr. 29, S. 884, 2018. doi: [10.21105/joss.00884](https://doi.org/10.21105/joss.00884).

