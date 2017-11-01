import matplotlib.pyplot as plt
import numpy as np
import math

monthly_annual_demand_scalar = {
 1: 064., 
 2: 065., 
 3: 070., 
 4: 090., 
 5: 110., 
 6: 140., 
 7: 153., 
 8: 130., 
 9: 120., 
 10: 100., 
 11: 080., 
 12: 074., 
}

monthly_seasonal_demand_scalar = {
 1: 0.,
 2: 0.,
 3: 0.,
 4: 0.,
 5: 0.,
 6: 0.,
 7: 0.,
 8: 0.,
 9: 0.,
 10: 0.,
 11: 0.,
 12: 0.,
}

monthly_summer_average = 0.01*(monthly_annual_demand_scalar[6] + monthly_annual_demand_scalar[7] + monthly_annual_demand_scalar[8]) / 3
monthly_winter_average = 0.01*(monthly_annual_demand_scalar[1] + monthly_annual_demand_scalar[2] + monthly_annual_demand_scalar[12]) / 3
monthly_spring_average = 0.01*(monthly_annual_demand_scalar[2] + monthly_annual_demand_scalar[4] + monthly_annual_demand_scalar[5]) / 3
monthly_fall_average = 0.01*(monthly_annual_demand_scalar[9] + monthly_annual_demand_scalar[10] + monthly_annual_demand_scalar[11]) / 3

for item in monthly_seasonal_demand_scalar:
	if item == 6 or item == 7 or item == 8:
		monthly_seasonal_demand_scalar[item] = monthly_annual_demand_scalar[item] / monthly_summer_average
	if item == 12 or item == 1 or item == 2:
		monthly_seasonal_demand_scalar[item] = monthly_annual_demand_scalar[item] / monthly_winter_average
	if item == 3 or item == 4 or item == 5:
		monthly_seasonal_demand_scalar[item] = monthly_annual_demand_scalar[item] / monthly_spring_average
	if item == 9 or item == 10 or item == 11:
		monthly_seasonal_demand_scalar[item] = monthly_annual_demand_scalar[item] / monthly_fall_average

print(monthly_seasonal_demand_scalar)

hourly_summer_demand_scalar = {
1: 100.,
2: 095.,
3: 090.,
4: 100.,
5: 110.,
6: 130.,
7: 150.,
8: 175.,
9: 200.,
10: 210.,
11: 200.,
12: 175.,
13: 150.,
14: 147.,
15: 145.,
16: 170.,
17: 200.,
18: 225.,
19: 250.,
20: 263.,
21: 275.,
22: 263.,
23: 250.,
24: 100.,
}

hourly_winter_demand_scalar = {
1: 050.,
2: 045.,
3: 040.,
4: 045.,
5: 050.,
6: 058.,
7: 065.,
8: 073.,
9: 080.,
10: 073.,
11: 065.,
12: 058.,
13: 050.,
14: 045.,
15: 040.,
16: 045.,
17: 050.,
18: 058.,
19: 065.,
20: 073.,
21: 080.,
22: 073.,
23: 065.,
24: 050.,
}

hourly_equinox_demand_scalar = {
1: 075.,
2: 070.,
3: 065.,
4: 073.,
5: 080.,
6: 094.,
7: 108.,
8: 124.,
9: 140.,
10: 142.,
11: 133.,
12: 117.,
13: 100.,
14: 096.,
15: 093.,
16: 108.,
17: 125.,
18: 142.,
19: 158.,
20: 168.,
21: 178.,
22: 168.,
23: 158.,
24: 075.,
}

avg_summer = 0.
avg_winter = 0.
avg_spring = 0.
avg_fall = 0

for item in hourly_summer_demand_scalar:
	avg_summer += 0.01 * hourly_summer_demand_scalar[item] / len(hourly_summer_demand_scalar)

for item in hourly_winter_demand_scalar:
	avg_winter += 0.01 * hourly_winter_demand_scalar[item] / len(hourly_winter_demand_scalar)

for item in hourly_equinox_demand_scalar:
	avg_spring += 0.007225 * hourly_equinox_demand_scalar[item] / len(hourly_equinox_demand_scalar)

for item in hourly_equinox_demand_scalar:
	avg_fall += 0.007225 * hourly_equinox_demand_scalar[item] / len(hourly_equinox_demand_scalar)

avg_annual = (avg_summer + avg_winter + avg_spring + avg_fall) / 4

print('average summer:', avg_summer)
print('average winter:', avg_winter)
print('average spring:', avg_spring)
print('average fall:', avg_fall)
print('average annual:', avg_annual)
print('')

avg_monthly = 0.
for item in monthly_annual_demand_scalar:
	avg_monthly += 0.01 * monthly_annual_demand_scalar[item] / len(monthly_annual_demand_scalar)

print('average monthly:', avg_monthly)
print('')

avg_hourly = 0.
num_hourly = 1./ (12 * 24)
for item in monthly_seasonal_demand_scalar:
	for hour in range(1, 24+1):
		if item == 6 or item == 7 or item == 8:
			avg_hourly += monthly_seasonal_demand_scalar[item] * hourly_summer_demand_scalar[hour] * 0.01 * num_hourly
		if item == 12 or item == 1 or item == 2:
			avg_hourly += monthly_seasonal_demand_scalar[item] * hourly_winter_demand_scalar[hour] * 0.01 * num_hourly
		if item == 3 or item == 4 or item == 5:
			avg_hourly += monthly_seasonal_demand_scalar[item] * hourly_equinox_demand_scalar[hour] * 0.007225 * num_hourly
		if item == 9 or item == 10 or item == 11:
			avg_hourly += monthly_seasonal_demand_scalar[item] * hourly_equinox_demand_scalar[hour] * 0.007225 * num_hourly

print('average hourly:', avg_hourly)