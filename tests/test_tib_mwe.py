import pandas as pd 
import numpy as np 
import paat 

def test_tib_mwe():
    """
    Test whether the MWE suggested by Lukas Adamowicz (@LukasAdamowicz) runs without error. See https://github.com/openjournals/joss-reviews/issues/8136#issuecomment-2976494558 
    """
    n_min = 3
    fs = 64

    t0 = pd.to_datetime("2025-06-10 13:04:57")
    td = pd.to_timedelta(np.arange(0, n_min * 60, 1/fs), unit='s')

    time = t0 + td

    acc = np.random.default_rng().normal(size=(time.size, 3))
    acc[:, 1] += 1

    df = pd.DataFrame(data=acc, columns=['X', 'Y', 'Z'])
    df.index = time

    df.head(3)

    df.loc[:, "Non Wear Time"] = paat.detect_non_wear_time_hees2011(df, 64)

    df.loc[:, "Time in Bed"] = paat.detect_time_in_bed_weitz2024(df, 64)

    df