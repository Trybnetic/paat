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

The Physical Activity Analysis Toolbox (*paat*) is a versatile Python package designed to analyze physical activity
data. It is used in research and health-related fields to process raw acceleration data collected from the hip. It
supports importing, cleaning, and preprocessing raw data, and includes algorithms for classifying time in bed and non
wear time. Furthermore, it supports estimating various physical activity levels such as moderate-to-vigorous physical
activity or sedentary behavior, with customizable thresholds from multiple metrics. These estimates can be aggregated
and used for further statistical analysis or be used direct for more sophisticated physical activity pattern analysis.
Additionally, *paat* is extensible, allowing users to add custom algorithms or modules and integrates well with other
data analysis tools within the Python ecosystem. 

# Statement of need

<!-- Measurement of physical activity -->
Physical activity is one of the strongest predictors of overall health. Its absence has been linked to various
noncommunicable diseases such as cancer, cardiovascular diseases, or diabetes as well as mental diseases like depression
or anxiety. Various methods exist to measure physical activity, including surveys or wearable devices. Acceleromters are
small body-worn sensors commonly used in research to record participants' acceleration over time. From the acceleration
signal physical activity levels and energy expenditure as well as other lifestyle-related variables such as sleep can be
estimated. By that, accelerometers provide a reasonably cheap but still more objective alternative to surveys while
simultaneously keeping the researcher and participant burden low. 

<!-- Accelerometry -->
Over decades, the raw acceleration as measured in ms$^{−2}$ has been transformed into summary metrics like activity
counts [@neishabouri_quantification_2022]. More recently, the raw acceleration itself became into the focus of method
development [@van_hees_challenges_2016]. Most method development has focused on the wrist during its common use in many
large-scale surveillance studies, which also lead to the development of the popular accelerometer analysis package GGIR
[@migueles_ggir_2019]. Today, a plethora of accelerometer packages exist each fulfilling different purposes, for
instance, to analyze actigraphy and light exposure data [@hammad_pyactigraphy_2021] or processing the UK Biobank data
[@chan_actipy_2024]. However, none of these packages focuses on acceleration data collected from the hip even though the
interest in hip-specific methods is increasing. New methods have been developed or validated recently
[@syed_evaluating_2020;@syed_novel_2021;@weitz_automatic_2024] as well as various large-scale population studies using
hip-based accelerometry to measure physical activity [@hopstock_seventh_2022;@weber_large_scale_2024]. 

![Visualization of the results obtained from *paat*. (A) The package can be used
to load and process the raw data (upper row). The loaded data can then be annotated by a variety of methods. The
implemented non-wear time and time in bed algorithm exploit raw acceleration data directly. To estimate physical
activity, the raw data is reduced to the ENMO of the signal (lower row). Alternatively, also other metrics like MAD can
be estimated and used for further processing. (B) Aggregated daily or average (Ø) results can be obtained and then be
used for further analyzes. \label{fig:processing}](img/paper_fig1.png) 
<!-- The need for the package -->
For many recently developed methods, corresponding code was even available on Github, but was often difficult to use due
to no existing dependency management and missing maintenance. However, easy accessibility of these methods seems
particularly important to foster validation and application, especially as openly available data and standardized
benchmarking procedures are scarce in the field [@palotti_benchmark_2019;@sadeh_role_2011]. Reasons for this might be
the sensitive nature, but also the high costs of collecting of the data and might potentially compromise the adoption of
machine learning based methods which are known to struggle to generalize. External validation of methods is an
alternative to standardized benchmarking and is commonly done in this field
[@palotti_benchmark_2019;@syed_evaluating_2020;@skovgaard_generalizability_2023] and should, thus, be facilitated.

<!-- PAAT -->
For that reason, we collected various methods to analyze raw acceleration data from the hip in this package to
facilitate validation and application of the included methods. We designed the package in a way that all methods can be
run in isolation, but can also be combined to design reproducible analysis pipelines. Additionally, we designed the
package to be extensible allowing users to easily add custom algorithms or use algorithms from other packages in the
same pipeline by structuring it according to the respective applications (io, calibration, preprocessing, features, wear
time, sleep, estimation; which are described in more detail below). By doing that, we also want to facilitate the
integration into existing packages and ecosystems.

# Implementation and structure

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

## Non-wear time

To identify Non-Wear Time (NWT), several functions are implemented in *paat*: `detect_non_wear_time_naive` implements a very simple
standard deviation based approach to NWT. The improved Van Hees NWT algorithm [@van_hees_estimation_2011;
@hees_separating_2013] is implemented in the `detect_non_wear_time_hees2011` function. The
`detect_non_wear_time_syed2021` function implements the CNN-based NWT approach proposed by @syed_novel_2021.

## Sleep/Time in bed

To detect the time in bed (TiB) the algorithm of @weitz_automatic_2024 is implemented in the
`detect_time_in_bed_weitz2024` function.

## Physical activity levels

Physical activity level estimation as implemented `calculate_pa_levels`. It provides sedentary behavior (SB), light
physical activity (LPA) and moderate-to-vigorous physical activity (MVPA) estimates based on a MVPA (`mvpa_cutpoint`)
and a sedentary (`sb_cutpoint`) cutpoint. 

## Different metrics

While *paat* has been developed with primary focus on Euclidean Norm Minus One (ENMO) based physical activity
estimation, several other metrics have been included in the `paat.features` module as well. The Median Amplitude
Deviation (MAD) [@vaha-ypya_universal_2015] can be calculated with the `calculate_mad` function. Brønd activity counts
[@brond_generating_2017] can be calculated with the `calculate_brond_counts` and ActiGraph activity counts
[@neishabouri_quantification_2022] with the `calculate_actigraph_counts` function. However, the latter function only
interfaces the corresponding function from the agcounts package [@actigraph_llc_agcounts_2022] and provides a Pandas
DataFrame in the same style as *paat*.

# Use in research

*paat* has already been used in various studies. @syed_evaluating_2020, for instance, developed and used the general
gt3x reading functionality and implemented and used the NWT algorithm from @van_hees_estimation_2011 for a comparison
study of different NWT algorithms. @syed_novel_2021 also used the functions to develop a new non-wear time algorithm
which is now included in *paat*. @weitz_influence_2024 used the package to load and process the acceleration data to
investigate the effect of accelerometer calibration on physical activity in general and MVPA in particular.
@weitz_automatic_2024 used the package to load and process the data in order to train a machine learning model to
identify time-in-bed episodes. The developed method is now also included in this package.

# Acknowledgements

This work was supported by the High North Population Studies at UiT The Arctic University of Norway. Furthermore, the
authors thank all [contributors on GitHub](https://github.com/Trybnetic/paat/graphs/contributors).

# References
