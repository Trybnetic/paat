---
title: 'PAAT: Physical Activity Analysis Toolbox for the analysis of hip-worn raw accelerometer data in Python'
tags:
  - physical-activity
  - accelerometers
  - ActiGraph
  - hip
  - methods
authors:
  - name: Marc Weitz
    orcid: 0009-0006-8225-833X
    corresponding: true # (This is how to denote the corresponding author)
    equal-contrib: false
    affiliation: "1" # (Multiple affiliations must be quoted)
  - name: Shaheen Syed
    orcid: 0000-0001-5462-874X
    equal-contrib: false # (This is how you can denote equal contributions between multiple authors)
    affiliation: "1"
  - name: Alexander Horsch
    orcid: 0000-0001-7745-0139
    affiliation: "1"
affiliations:
 - name: Department of Computer Science, UiT The Arctic University of Norway, Tromsø, Norway
   index: 1
date: 01 May 2024
bibliography: paper.bib

---

# Summary

The *paat* package contains implementations of many algorithms recently developed 
in our lab for raw data accelerometer analysis. Additionally, several reimplementations
of existing methods are included that have been used to perform, for instance, validation
experiments where no original implementation was easily accessible. The methods contained
in this package include various non-wear time algorithms, a time in bed 
algorithm, as well as general processing functions to estimate raw data moderate-to-vigorous
physical activity (MVPA) from the Eucledean Norm Minus One (ENMO) and Mean Amplitude 
Deviation (MAD) of the raw acceleration signal.

# Statement of need

Accelerometers have become a popular assessment tool of physical activity over the last 
decades. The small body-worn sensors provide an easy and more objective alternative 
to classic questionaire-based assessment while simultaneously keeping the researcher and
participant burden low. Especially, the field of raw data accelerometry and the analysis of 
the raw acceleration signals measured in g (1 g = 9.806 65 m s−2) have received great focus
over the last years and is a rapidly advancing field. Many algorithms have been proposed
the last years; Also by our lab. Simultaneously, openly available data to benchmark algorithms on 
is scarce due to privacy concerns. Nevertheless, new algorithms can only be adopted in 
research after rigorous external validation. 

While publishing code and, in the context of machine learning, trained models has become
more common, this often does not automatically imply that the published code is easily 
usable for validation. In fact, reimplementations are often necessary, even though 
they increase potential biases by incorrect implementation. For that reason, we developed 
*paat* as a simple and easy to use package to facilitate
replicating and validating of our findings. The package is structured according to the 
respective applications (io, calibration, preprocessing, features, wear time, sleep, 
estimation) and the methods easily applicable also in isolation.

# Related work

By now, several packages exist to analyze (raw) acceleration data. The by far most popular 
packages is certainly the *GGIR* R-package [@migueles_ggir_2019]. GGIR combines a variety
of methods that were primarily developed for the analysis of wrist-worn accelerometer 
data and provides a complete analysis pipeline to facilitate easily replicable analysis 
requiring now to little programming experience. Another accelerometer data analysis package 
named *PyActigraphy* has been provided by @hammad_pyactigraphy_2021. This package focuses 
especially on the analysis of circadian rest-activity cycles and sleep patterns and not on 
physical activity. 
<!-- *Actipy* [@chan_actipy_2024], on the other hand, has a similar scope, but was neither 
available when we started with *paat*, nor has it a comparably extensive functionality. -->

![Visualization of the results obtained from *paat*. (A) The package can be used to load and process the raw data
(upper row). The implemented non-wear time and time in bed algorithm exploit raw acceleration data directly. To 
estimate physical activity, the raw data is reduced to the ENMO of the signal (lower row). (B) Aggregated daily 
or average (Ø) results can be obtained and then be used for further analyzes.
\label{fig:processing}](img/paper_fig1.png)


# Implementation

While *paat* can process multiday recordings of accelerometer data (see \autoref{fig:processing}), it has also been 
developed to use various functionalities in isolation. For that reason, the package is organized into different 
submodules according to the respective functions. The most important high-level functions are also exposed on package 
level to facilitate the usage of the package. Further, more low-level functions are included in the respective 
submodules and can be found in the package's documentation. In this section, we briefly introduce the respective 
submodules and their most important functions.

## File reading 

ActiGraph's GT3X files can be read using the `read_gt3x` function which behaves similar to the IO functions known from 
pandas. However, it also provides the sampling frequency as this can be relevant for further processing. If additional 
metadata is required, this can be read either by setting `metadata=True` or using the `read_metadata` function.

<!-- ## Autocalibration

A comparable autocalibration estimation procedure to GGIR is not yet implemented in this package. Previous work using *paat*, estimated the autocalibration coefficients independently using GGIR and used these estimates to calibrate the data using the `calibrate` function [@weitz_influence_2024]. -->

## Non-wear time

To identify NWT, several functions are implemented in *paat*: `detect_non_wear_time_naive` implements a very simple 
standard deviation based approach to NWT. The improved Van Hees NWT algorithm 
[@van_hees_estimation_2011; @hees_separating_2013] is implemented in the `detect_non_wear_time_hees2011` function. 
The `detect_non_wear_time_syed2021` function implements the CNN-based NWT approach proposed by @syed_novel_2021.

## Sleep/Time in bed

To detect the time in bed (TiB) the algorithm of @weitz_automatic_2024 is implemented in the 
`detect_time_in_bed_weitz2024` function.

## Physical activity levels

Physical activity level estimation as implemented `calculate_pa_levels`. It provides sedentary behavior (SB), light 
physical activity (LPA) and MVPA estimates based on a MVPA (`mvpa_cutpoint`) and a sedentary (`sb_cutpoint`) cutpoint. 

## Different metrics

While *paat* has been developed with primary focus on ENMO-based physical activity estimation, several other metrics 
have been included in the `paat.features` module as well. MAD [@vaha-ypya_universal_2015] can be calculated with the 
`calculate_mad` function. Brønd counts [@brond_generating_2017] can be calculated with the `calculate_brond_counts` and 
ActiGraph counts [@neishabouri_quantification_2022] with the `calculate_actigraph_counts` function.

# Use in research

*paat* has already been used in various studies. @syed_evaluating_2020, for instance, developed and used the general 
gt3x reading functionality and implemented and used the NWT algorithm from @van_hees_estimation_2011 for a comparison 
study of different NWT algorithms. @syed_novel_2021 also used the functions to develop a new non-wear time algorithm 
which is now included in *paat*. @weitz_influence_2024 used the package to load and process the acceleration data to 
investigate the effect of accelerometer calibration on physical activity in general and MVPA in particular. 
@weitz_automatic_2024 used the package to load and process the data in order to train a machine learning model to 
identify time-in-bed episodes. The developed method is now also included in this package.




# Acknowledgements

This work was supported by the High North Population Studies at UiT The Arctic University 
of Norway. Furthermore, the authors thank all 
[contributors on GitHub](https://github.com/Trybnetic/paat/graphs/contributors).

# References
