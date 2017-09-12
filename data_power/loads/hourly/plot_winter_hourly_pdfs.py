import math
import numpy as np
import matplotlib.pyplot as plt

load_data_low = np.genfromtxt("data/load_winter_hourly_data_low.txt")
load_data_high = np.genfromtxt("data/load_winter_hourly_data_high.txt")
x = np.arange(50., 110.)

count, bins, ignored = plt.hist(load_data_low)
sumcount_low = sum(count) * math.fabs(bins[0] - bins[1])

count, bins, ignored = plt.hist(load_data_high)
sumcount_high = sum(count) * math.fabs(bins[0] - bins[1])

# source: page 30 of https://www.jmp.com/support/downloads/pdf/jmp9/quality_and_reliability_methods.pdf
def weibull(x, scale, shape):
	return (shape/scale) * (x/scale)**(shape-1) * np.exp(-(x/scale)**shape)

def weibullcdf(x, scale, shape):
	return 1. - np.exp(-(x/scale)**shape)

def normal(x, mu, sigma):
	return 1./(sigma * np.sqrt(2. * np.pi)) * np.exp(- (x - mu)**2 / (2.*sigma**2))

def lognormal(x, mu, sigma):
	return np.exp(-(np.log(x) - mu)**2 / (2. * sigma**2)) / (sigma * x * np.sqrt(2. * np.pi))

def frechet(x, location, scale, shape):
	return (shape/scale) * ((x-location)/scale)**(-1.-shape) * np.exp(-((x-location)/scale)**(-shape))

def logistic(x, location, scale):
	return np.exp(-(x-location) / scale) / (scale * (1. + np.exp(-(x-location) / scale))**2)

def loglogistic(x, scale, shape):
	return ((shape/scale) * (x/scale)**(shape-1.)) / (1. + (x/scale)**(shape))**2

def sev(x, mu, sigma):
	return (1./sigma) * np.exp( (x-mu)/sigma - np.exp((x-mu)/sigma) )

def lev(x, mu, sigma):
	return (1./sigma) * np.exp( -(x-mu)/sigma - np.exp(-(x-mu)/sigma) )

weib_shape = 1./0.045905
weib_scale = np.exp(4.552238)
plt.plot(x, weibull(x, weib_scale, weib_shape) * sumcount_high, color="teal", label="weibull, AIC 185.34")

# norm_mu = 81.8615
# norm_sigma = 7.9495
# plt.plot(x, normal(x, norm_mu, norm_sigma) * sumcount, label="normal, AIC 367.42")

# lnorm_mu = 4.2014
# lnorm_sigma = 0.0902616
# plt.plot(x, lognormal(x, lnorm_mu, lnorm_sigma) * sumcount_low, label="log-normal, AIC 120.55")

# frech_shape = 1./0.085515
# frech_scale = np.exp(4.35252)
# frech_loc = -0.
# plt.plot(x, frechet(x, frech_loc, frech_scale, frech_shape) * sumcount, label="frechet, AIC 368.29")

# log_location = 81.71352
# log_scale = 4.8068
# plt.plot(x, logistic(x, log_location, log_scale) * sumcount, label="logistic, AIC 371.68")

# llog_shape = 1./0.058874
# llog_scale = np.exp(4.4002)
# plt.plot(x, loglogistic(x, llog_scale, llog_shape) * sumcount, label="log-logistic, AIC 371.23")

lev_mu = 64.1546
lev_sigma = 4.9592
plt.plot(x, lev(x, lev_mu, lev_sigma) * sumcount_low, color="red", label="lev, AIC 119.50")

plt.xticks(fontsize="x-large")
plt.xlabel("Percent of daily maximum", fontsize="x-large")
plt.yticks(fontsize="x-large")
plt.ylabel("Occurrences in 2 days", fontsize="x-large")
plt.title("Winter", fontsize="x-large")
plt.legend(fontsize="x-large")
plt.show()