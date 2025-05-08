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
supports importing, cleaning, and preprocessing raw data, and includes algorithms to classify time in bed and non wear
time. Furthermore, it supports estimating various physical activity levels such as moderate-to-vigorous physical
activity or sedentary behavior, with customizable thresholds from multiple metrics. These estimates can be aggregated
and used for further statistical analysis or be used directly for more sophisticated physical activity pattern analysis.
Additionally, *paat* is extensible, allowing users to add custom algorithms or modules, and it integrates well with
other data analysis tools within the Python ecosystem. 

# Statement of need

<!-- Measurement of physical activity -->
Physical activity is one of the strongest predictors of overall health. Its absence has been linked to various
noncommunicable diseases such as cancer, cardiovascular diseases, or diabetes as well as mental diseases like depression
or anxiety. Various methods exist to measure physical activity. One of these methods use accelerometers to estimate
physical activity. Accelerometers are small body-worn sensors which measure acceleration over time. They have become a
popular assessment tool in research and public health as they provide a reasonably cheap but still more objective
alternative to surveys while simultaneously keeping the researcher and participant burden low. Accelerometers measure the raw acceleration in ms$^{−2}$ often also expressed as multiples of Earth's gravitation ($1g =  9.80665ms^{−2}$). However, due to historic limitations of on-device storage, the raw acceleration has often been processed to summary metrics like activity counts [@neishabouri_quantification_2022]. However, over the last decade the raw acceleration itself has also gotten into the focus of method development [@van_hees_challenges_2016]. A fundamental limitation of accelerometry is that many methods are only applicable to a certain wear location and demographic group and often do not generalize beyond that. Therefore, separate sets of methods have been developed for different populations and study protocols.

<!-- Accelerometry packages -->
Today, a plethora of accelerometer packages exist each fulfilling different purposes. The most popular package is GGIR [@migueles_ggir_2019] which provides a broad set of well validated raw data methods mainly focusing on wrist-based accelerometry in R. @hammad_pyactigraphy_2021 implemented *pyactigraphy* to analyze accelerometer activity count and light exposure data. *Actipy* provides various file reading and autocalibration functions, but only provide a limited set of methods for the further data analysis [@chan_actipy_2024]. *SciKit Digital Health (SKDH)* provides a variety of algorithms for deriving clinical features of gait, sit to stand, physical activity, and sleep [@adamowicz_scikit_2022]. *Paat* is more specific in its focus on 

![Visualization of the results obtained from *paat*. (A) The package can be used to load and process the raw data (upper row). The loaded data can then be annotated by a variety of methods. The implemented non-wear time and time in bed algorithm exploit raw acceleration data directly. To estimate physical activity, the raw data is reduced to the ENMO of the signal (lower row). Alternatively, also other metrics like MAD can be estimated and used for further processing. (B) Aggregated daily or average (Ø) results can be obtained and then be used for further analyzes. \label{fig:processing}](img/paper_fig1.png) 

hip-placed accelerometer data, but some methods might be also interesting for other packages once they are validated and used more commonly in application. 

<!-- PAAT -->
For that reason, *paat* contains various methods to analyze raw acceleration data from the hip. As many of the methods have only recently been proposed, the primary objective of *paat* is to facilitate validation of these methods on external data. Therefore, we designed the package in a way that all methods can be run in isolation, but can also be combined to create reproducible analysis pipelines. Additionally, we designed the package to be extensible allowing users to easily add custom algorithms or use algorithms from other packages in the same pipeline by structuring it according to the respective applications. By doing that, we also want to facilitate the integration into existing packages and ecosystems.

# Use in research

*paat* has already been used in various studies. @syed_evaluating_2020, for instance, developed and used the general
gt3x reading functionality and implemented and used the NWT algorithm from @van_hees_estimation_2011 for a comparison
study of different NWT algorithms. @syed_novel_2021 also used the functions to develop a new non-wear time algorithm
which is now included in *paat*. @weitz_influence_2024 used the package to load and process the acceleration data to
investigate the effect of accelerometer calibration on physical activity in general and MVPA in particular.
@weitz_automatic_2025 used the package to load and process the data in order to train a machine learning model to
identify time-in-bed episodes. The developed method is now also included in this package.

# Acknowledgements

This work was supported by the High North Population Studies at UiT The Arctic University of Norway. Furthermore, the
authors thank all [contributors on GitHub](https://github.com/Trybnetic/paat/graphs/contributors).

# References
