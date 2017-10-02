import math
import numpy as np
import matplotlib.pyplot as plt

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

week_load_scalar = {
1: 86.2,
2: 90.,
3: 87.8,
4: 83.4,
5: 88.,
6: 84.1,
7: 83.2,
8: 80.6,
9: 74.,
10: 73.7,
11: 71.5,
12: 72.7,
13: 70.4,
14: 75.,
15: 72.1,
16: 80.,
17: 75.4,
18: 83.7,
19: 87.,
20: 88.,
21: 85.6,
22: 81.1,
23: 90.,
24: 88.7,
25: 89.6,
26: 86.1,
27: 75.5,
28: 81.6,
29: 80.1,
30: 88.,
31: 72.2,
32: 77.6,
33: 80.,
34: 72.9,
35: 72.6,
36: 70.5,
37: 78.,
38: 69.5,
39: 72.4,
40: 72.4,
41: 74.3,
42: 74.4,
43: 80.,
44: 88.1,
45: 88.5,
46: 90.9,
47: 94.,
48: 89.,
49: 94.2,
50: 97.,
51: 100.,
52: 95.2
}

day_load_scalar = {
1: 93.,
2: 100.,
3: 98.,
4: 96.,
5: 94.,
6: 77.,
7: 75.,
}

hour_winter_weekday_load_scalar = {
1: 67.,
2: 63.,
3: 60.,
4: 59.,
5: 59.,
6: 60.,
7: 74.,
8: 86.,
9: 95.,
10: 96.,
11: 96.,
12: 95.,
13: 95.,
14: 95.,
15: 93.,
16: 94.,
17: 99.,
18: 100.,
19: 100.,
20: 96.,
21: 91.,
22: 83.,
23: 73.,
24: 63.
}

hour_winter_weekend_load_scalar = {
1: 78.,
2: 72.,
3: 68.,
4: 66.,
5: 64.,
6: 65.,
7: 66.,
8: 70.,
9: 80.,
10: 88.,
11: 90.,
12: 91.,
13: 90.,
14: 88.,
15: 87.,
16: 87.,
17: 91.,
18: 100.,
19: 99.,
20: 97.,
21: 94.,
22: 92.,
23: 87.,
24: 81.
}

hour_summer_weekday_load_scalar = {
1: 64.,
2: 60.,
3: 58.,
4: 56.,
5: 56.,
6: 58.,
7: 64.,
8: 76.,
9: 87.,
10: 95.,
11: 99.,
12: 100.,
13: 99.,
14: 100.,
15: 100.,
16: 97.,
17: 96.,
18: 96.,
19: 93.,
20: 92.,
21: 92.,
22: 93.,
23: 87.,
24: 72.
}

hour_summer_weekend_load_scalar = {
1: 74.,
2: 70.,
3: 66.,
4: 65.,
5: 64.,
6: 62.,
7: 62.,
8: 66.,
9: 81.,
10: 86.,
11: 91.,
12: 93.,
13: 93.,
14: 92.,
15: 91.,
16: 91.,
17: 92.,
18: 94.,
19: 95.,
20: 95.,
21: 100.,
22: 93.,
23: 88.,
24: 80.,
}

hour_equinox_weekday_load_scalar = {
1: 63.,
2: 62.,
3: 60.,
4: 58.,
5: 59.,
6: 65.,
7: 72.,
8: 85.,
9: 95.,
10: 99.,
11: 100.,
12: 99.,
13: 93.,
14: 92.,
15: 90.,
16: 88.,
17: 90.,
18: 92.,
19: 96.,
20: 98.,
21: 96.,
22: 90.,
23: 80.,
24: 70.
}

hour_equinox_weekend_load_scalar = {
1: 75.,
2: 73.,
3: 69.,
4: 66.,
5: 65.,
6: 65.,
7: 68.,
8: 74.,
9: 83.,
10: 89.,
11: 92.,
12: 94.,
13: 91.,
14: 90.,
15: 90.,
16: 86.,
17: 85.,
18: 88.,
19: 92.,
20: 100.,
21: 97.,
22: 95.,
23: 90.,
24: 85.,
}

hour_mults = []
winter_mults = []
summer_mults = []
equinox_mults = []

for week in range(1, len(week_load_scalar)+1):
	for day in range(1, len(day_load_scalar)+1):
		for hour in range(1, 24+1):
			alpha = week_load_scalar[week]*0.01
			beta = day_load_scalar[day]*0.01

			if week < 9 or week > 43:
				if day < 6:
					gamma = hour_winter_weekday_load_scalar[hour]
				else:
					gamma = hour_winter_weekend_load_scalar[hour]
			elif 17 < week < 31:
				if day < 6:
					gamma = hour_summer_weekday_load_scalar[hour]
				else:
					gamma = hour_summer_weekend_load_scalar[hour]
			else:
				if day < 6:
					gamma = hour_equinox_weekday_load_scalar[hour]
				else:
					gamma = hour_equinox_weekend_load_scalar[hour]

			gamma = gamma*0.01
			hour_mults.append(alpha*beta*gamma)

for i in range(0, len(hour_mults)):
	if i <= 8*24*len(day_load_scalar) or i > 43*24*len(day_load_scalar):
		winter_mults.append(hour_mults[i])
	elif 17*24*len(day_load_scalar) < i <= 30*24*len(day_load_scalar):
		summer_mults.append(hour_mults[i])
	else:
		equinox_mults.append(hour_mults[i])

count, bins, ignored = plt.hist([winter_mults, summer_mults, equinox_mults], 50, rwidth=1., stacked=True, label=['winter', 'summer', 'spring or fall'])
sumcount = sum(count[-1]) * math.fabs(bins[0] - bins[1])

x = np.arange(0.0, 1.0, 0.02)

# weib_shape = 1./0.20784994
# weib_scale = np.exp(-0.399369)
# plt.plot(x, weibull_pdf(x, weib_scale, weib_shape) * sumcount, color="teal", label="weibull, AIC -9329.38")

# lnorm_mu = -0.5138005
# lnorm_sigma = 0.2327611
# plt.plot(x, lognormal_pdf(x, lnorm_mu, lnorm_sigma) * sumcount, label="lognormal, AIC -9651.107")

exp_rate = 1./np.exp(-1.2886227)
exp_x = np.array([i for i in x if i <= max(x)-min(hour_mults)])
plt.plot(exp_x + min(hour_mults), exponential_pdf(exp_x, exp_rate) * sumcount, label="exponential, AIC -5039.66")

# frech_shape = 1./0.22285012
# frech_scale = np.exp(-0.6312738)
# frech_loc = -0.
# plt.plot(x, frechet_pdf(x, frech_loc, frech_scale, frech_shape) * sumcount, label="frechet, AIC -8520.865")

# llog_shape = 1./0.13933323
# llog_scale = np.exp(-0.596069)
# plt.plot(x, loglogistic_pdf(x, llog_scale, llog_shape) * sumcount, label="log-logistic, AIC -9013.92")

# sev_mu = 0.68587809
# sev_sigma = 0.13706715
# plt.plot(x, sev_pdf(x, sev_mu, sev_sigma) * sumcount, label="sev, AIC -8134.44")

# norm_mu = 0.61439957
# norm_sigma = 0.14054943
# plt.plot(x, normal_pdf(x, norm_mu, norm_sigma) * sumcount, label="normal, AIC -9487.79")

# lev_mu = 0.54590407
# lev_sigma = 0.12268245
# plt.plot(x, lev_pdf(x, lev_mu, lev_sigma) * sumcount, color="red", label="lev, AIC -9428.09")

# log_location = 0.61025576
# log_scale = 0.08402914
# plt.plot(x, logistic_pdf(x, log_location, log_scale) * sumcount, label="logistic, AIC -8861.96")

plt.xticks(fontsize="x-large")
plt.xlabel("Power load factors throughout the year", fontsize="x-large")
plt.yticks(fontsize="x-large")
plt.ylabel("Frequency", fontsize="x-large")
plt.title("Histogram and PDF for hourly power loads", fontsize="x-large")
plt.legend(fontsize="x-large")
plt.show()