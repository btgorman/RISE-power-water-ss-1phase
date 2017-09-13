import math
import numpy as np
import matplotlib.pyplot as plt

def lognormal_pdf(x, mu, sigma):
	return np.exp(-(np.log(x) - mu)**2 / (2. * sigma**2)) / (sigma * x * np.sqrt(2. * np.pi))

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

print(len(winter_mults) - 8*7*24 - (1+52-44)*7*24)
print(len(summer_mults) - (1+30-18)*7*24)
print(len(equinox_mults))

count, bins, ignored = plt.hist([winter_mults, summer_mults, equinox_mults], 50, rwidth=1., stacked=True, label=['winter', 'summer', 'spring or fall'])
sumcount = sum(count[-1]) * math.fabs(bins[0] - bins[1])
print("sumcount is {}".format(sumcount)) # sumcount = 115.52268

x = np.arange(0.2, 1.1, 0.02)
lnorm_mu = -0.515408
lnorm_sigma = 0.238325
plt.plot(x, lognormal_pdf(x, lnorm_mu, lnorm_sigma) * sumcount, label="lognormal, AIC -9266.47")

plt.xticks(fontsize="x-large")
plt.xlabel("Percent of annual maximum", fontsize="x-large")
plt.yticks(fontsize="x-large")
plt.ylabel("Number of occurrances in a year", fontsize="x-large")
plt.title("Histogram of hourly load factors for the year", fontsize="x-large")
plt.legend(fontsize="x-large")
plt.show()