import numpy as np

load_data = np.genfromtxt("load_summer_hourly_data.txt")
load_data = np.array(sorted(load_data))

index = np.where( load_data == 81.)
index = index[0][0]

load_data_low = load_data[0:index+1]
load_data_high = load_data[index+1:len(load_data)+1]

np.savetxt("load_summer_hourly_data_low.txt", load_data_low, fmt="%.1f")
np.savetxt("load_summer_hourly_data_high.txt", load_data_high, fmt="%.1f")