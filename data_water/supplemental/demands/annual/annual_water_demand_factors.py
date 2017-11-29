import matplotlib.pyplot as plt
import numpy as np
import math

# source: page 30 of https://www.jmp.com/support/downloads/pdf/jmp9/quality_and_reliability_methods.pdf
def weibull_pdf(x, scale, shape):
	return (shape/scale) * (x/scale)**(shape-1) * np.exp(-(x/scale)**shape)

def weibull_cdf(x, scale, shape):
	return 1. - np.exp(-(x/scale)**shape)

def lognormal_pdf(x, mu, sigma):
	return np.exp(-(np.log(x) - mu)**2 / (2. * sigma**2)) / (sigma * x * np.sqrt(2. * np.pi))

def exponential_pdf(x, rate):
	return rate * np.exp(-rate*x)

def frechet_pdf(x, location, scale, shape):
	return (shape/scale) * ((x-location)/scale)**(-1.-shape) * np.exp(-((x-location)/scale)**(-shape))

def loglogistic_pdf(x, scale, shape):
	return ((shape/scale) * (x/scale)**(shape-1.)) / (1. + (x/scale)**(shape))**2

def sev_pdf(x, mu, sigma):
	return (1./sigma) * np.exp( (x-mu)/sigma - np.exp((x-mu)/sigma) )
			
def normal_pdf(x, mu, sigma):
	return 1./(sigma * np.sqrt(2. * np.pi)) * np.exp(- (x - mu)**2 / (2.*sigma**2))

def lev_pdf(x, mu, sigma):
	return (1./sigma) * np.exp( -(x-mu)/sigma - np.exp(-(x-mu)/sigma) )

def logistic_pdf(x, location, scale):
	return np.exp(-(x-location) / scale) / (scale * (1. + np.exp(-(x-location) / scale))**2)

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

# hourly_equinox_demand_scalar = {
# 1: 075., 
# 2: 070., 
# 3: 065., 
# 4: 073., 
# 5: 080., 
# 6: 094., 
# 7: 108., 
# 8: 124., 
# 9: 140., 
# 10: 142., 
# 11: 133., 
# 12: 117., 
# 13: 100., 
# 14: 096., 
# 15: 093., 
# 16: 108., 
# 17: 125., 
# 18: 142., 
# 19: 158., 
# 20: 168., 
# 21: 178., 
# 22: 168., 
# 23: 158., 
# 24: 075., 
# }

hourly_equinox_demand_scalar = {
1: 54.,
2: 51.,
3: 47.,
4: 53.,
5: 58.,
6: 68.,
7: 78.,
8: 90.,
9: 101.,
10: 103.,
11: 96.,
12: 85.,
13: 72.,
14: 69.,
15: 67.,
16: 78.,
17: 90.,
18: 103.,
19: 114.,
20: 121.,
21: 129.,
22: 121.,
23: 114.,
24: 54.
}

hourly_demand_scalar= {
1: hourly_winter_demand_scalar,
2: hourly_winter_demand_scalar,
3: hourly_equinox_demand_scalar,
4: hourly_equinox_demand_scalar,
5: hourly_equinox_demand_scalar,
6: hourly_summer_demand_scalar,
7: hourly_summer_demand_scalar,
8: hourly_summer_demand_scalar,
9: hourly_equinox_demand_scalar,
10: hourly_equinox_demand_scalar,
11: hourly_equinox_demand_scalar,
12: hourly_winter_demand_scalar
}

total_hourly_demands = []
summer_hourly_demands = []
winter_hourly_demands = []
equinox_hourly_demands = []

for month in range(1, len(monthly_seasonal_demand_scalar)+1):
	for hour in range(1, len(hourly_equinox_demand_scalar)+1):
		if month == 1 or month == 2 or month == 12:
			alpha = monthly_seasonal_demand_scalar[month] * 0.01
			beta = hourly_demand_scalar[month][hour] * 0.01
			winter_hourly_demands.append(alpha*beta)
			total_hourly_demands.append(alpha*beta)
		elif month == 3 or month == 4 or month == 5 or month == 9 or month == 10 or month == 11:
			alpha = monthly_seasonal_demand_scalar[month] * 0.01
			beta = hourly_demand_scalar[month][hour] * 0.01
			equinox_hourly_demands.append(alpha*beta)
			total_hourly_demands.append(alpha*beta)
		else:
			alpha = monthly_seasonal_demand_scalar[month] * 0.01
			beta = hourly_demand_scalar[month][hour] * 0.01
			summer_hourly_demands.append(alpha*beta)
			total_hourly_demands.append(alpha*beta)

# annual_hourly_demands = np.array(total_hourly_demands)
# np.savetxt('waterdemands288.csv', annual_hourly_demands, fmt='%.6f', delimiter=',', newline='\n')
print('min', min(total_hourly_demands))
print('max', max(total_hourly_demands))

count, bins, ignored = plt.hist([winter_hourly_demands, summer_hourly_demands, equinox_hourly_demands], int(288/8), stacked=True, label=['winter', 'summer', 'spring/fall'])
sumcount = sum(count[-1]) * math.fabs(bins[0] - bins[1])

# x = np.arange(0.0, max(total_hourly_demands), 0.08)
x = np.arange(0.0, max(total_hourly_demands) - min(total_hourly_demands), 0.08) # for exponential distribution

# weib_shape = 1./0.52599695
# weib_scale = np.exp(0.34368128)
# plt.plot(x, weibull_pdf(x, weib_scale, weib_shape) * sumcount, color="teal", label="weibull")

# lnorm_mu = -0.13181
# lnorm_sigma = 0.5054088
# plt.plot(x, lognormal_pdf(x, lnorm_mu, lnorm_sigma) * sumcount, label="lognormal")

exp_rate = 1./np.exp(-0.4559995)
plt.plot(x+min(total_hourly_demands), exponential_pdf(x, exp_rate) * sumcount, label="exponential")

# frech_shape = 1./0.42136022
# frech_scale = np.exp(-0.3719968)
# frech_loc = 0.
# plt.plot(x, frechet_pdf(x, frech_loc, frech_scale, frech_shape) * sumcount, label="frechet")

# llog_shape = 1./0.29436175
# llog_scale = np.exp(-0.1624727)
# plt.plot(x, loglogistic_pdf(x, llog_scale, llog_shape) * sumcount, label="log-logistic")

# sev_mu = 1.2354205
# sev_sigma = 0.6650083
# plt.plot(x, sev_pdf(x, sev_mu, sev_sigma) * sumcount, label="sev")

# norm_mu = 1.00406644
# norm_sigma = 0.57272733
# plt.plot(x, normal_pdf(x, norm_mu, norm_sigma) * sumcount, label="normal")

# lev_mu = 0.76293197
# lev_sigma = 0.37014512
# plt.plot(x, lev_pdf(x, lev_mu, lev_sigma) * sumcount, color="red", label="lev")

# log_loc = 0.91335971
# log_scale = 0.29913738
# plt.plot(x, logistic_pdf(x, log_loc, log_scale) * sumcount, label="logistic")

arialfont = {'fontname': 'Arial'}
plt.xticks(fontsize="large", **arialfont)
plt.xlabel("Water demand factors throughout the year", fontsize="x-large", **arialfont)
plt.yticks(fontsize="large", **arialfont)
plt.ylabel("Frequency", fontsize="x-large", **arialfont)
plt.legend(fontsize='large', loc=1)
plt.show()