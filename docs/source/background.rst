Background 
==========

Accelerometers have become a popular assessment tool of physical activity over the last 
decades. The small body-worn sensors provide an easy and more objective alternative 
to classic questionaire-based assessment while simultaneously keeping the researcher and
participant burden low. Especially, the field of raw data accelerometry, the analysis of 
the raw acceleration signals measured in g (1 g = 9.806 65 m s−2), has received great focus
over the last years and is a rapidly advancing field. Many algorithms have been proposed
the last years; Also by our lab. Simultaneously, openly available data to benchmark algorithms on 
is scarce due to privacy concerns. Nevertheless, new algorithms can only be adopted in 
research after rigorous external validation. 

While publishing code and, in the context of machine learning, trained models has become
more common, this often does not automatically imply that the published code is easily 
usable for validation. Effectively, often reimplementations are necessary, even though 
they increase potential biases by incorrect implementation. For that reason, we developed 
*paat* as a simple and easy to use package to facilitate replicating and validating of our 
findings and prospectively to apply the algorithms in research. The package is structured 
according to the respective applications (io, preprocessing, features, wear time, sleep, 
estimation) and the methods easily applicable also in isolation. An overview over the 
different submodules can be found in the :doc:`API Documentation <paat>`.

However, *paat* has already been used in various studies. Syed et al. [1]_, for 
instance, developed and used the general gt3x reading functionality and implemented 
and used the NWT algorithm from Van Hees et al. [2]_ for a comparison study of 
different NWT algorithms. Syed et al. [3]_ also used the functions to develop a new 
non-wear time algorithm which is now included in *paat*. Weitz et al. [4]_ used 
the package to load and process the acceleration data to investigate the effect of 
accelerometer calibration on physical activity in general and MVPA in particular. 
Weitz et al. [5]_ used the package to load and process the data in order to train a 
machine learning model to identify time-in-bed episodes.

If you are using *paat* in research, feel free to cite it as

    Weitz, M., Syed, S., & Horsch, A. (2024). PAAT: Physical Activity Analysis Toolbox. Zenodo. https://doi.org/10.5281/zenodo.13885749


If you are using BibTex you may want to use this example BibTex entry::

        @misc{weitz_paat_2024,
                title = {{PAAT}: {Physical} {Activity} {Analysis} {Toolbox}},
                url = {https://doi.org/10.5281/zenodo.13885749},
                publisher = {Zenodo},
                author = {Weitz, Marc and Syed, Shaheen and Horsch, Alexander},
                year = {2024},
                doi = {10.5281/zenodo.13885749},
        }

This also helps us to keep this page up to date.


----

.. [1] Syed, S., Morseth, B., Hopstock, L. A., & Horsch, A. (2020). Evaluating the 
        performance of raw and epoch non-wear algorithms using multiple accelerometers 
        and electrocardiogram recordings. *Scientific Reports*, 10(1), 1–18. 
        https://doi.org/10.1038/s41598-020-62821-2

.. [2] Van Hees VT, Renström F, Wright A, Gradmark A, Catt M, et al. (2011) Estimation 
        of Daily Energy Expenditure in Pregnant and Non-Pregnant Women Using a Wrist-Worn 
        Tri-Axial Accelerometer. *PLOS ONE*, 6(7): e22922. 
        https://doi.org/10.1371/journal.pone.0022922

.. [3] Syed, S., Morseth, B., Hopstock, L. A., & Horsch, A. (2021). A novel algorithm to 
        detect non-wear time from raw accelerometer data using deep convolutional neural 
        networks. *Scientific Reports*, 11(1), 8832. 
        https://doi.org/10.1038/s41598-021-87757-z

.. [4] Weitz, M., Morseth, B., Hopstock, L. A., & Horsch, A. (2024). Influence of 
        Accelerometer Calibration on the Estimation of Objectively Measured Physical 
        Activity: The Tromsø Study. *Journal for the Measurement of Physical Behaviour*, 7(1).
        https://doi.org/10.1123/jmpb.2023-0019

.. [5] Weitz, M., Syed, S., Hopstock, L. A., Morseth, B., Henriksen, A., & Horsch, A. 
        (2025). Automatic time in bed detection from hip-worn accelerometers for large 
        epidemiological studies: The Tromsø Study. *PLOS ONE*, 20(5), e0321558. 
        https://doi.org/10.1371/journal.pone.0321558

