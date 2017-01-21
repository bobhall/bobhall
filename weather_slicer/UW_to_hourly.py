import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_name = 'data.csv'
df = pd.read_csv(file_name,
                 index_col=[0],
                 usecols=[0,3,6,11,13],
                 parse_dates=True,
                 delim_whitespace=True)



import pdb; pdb.set_trace();
m = 33
