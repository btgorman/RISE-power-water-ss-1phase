import math
import numpy as np
import matplotlib.pyplot as plt

load_data = np.genfromtxt("load_weekly_data.txt")
x = np.arange(1,len(load_data)+1)
xp = np.linspace(-1, 53, 100)

fit3 = np.polyfit(x, load_data, 3, full=True)
fit3, fit3res, _, _, _ = fit3
fit3 = np.poly1d(fit3)

fit4 = np.polyfit(x, load_data, 4, full=True)
fit4, fit4res, _, _, _ = fit4
fit4 = np.poly1d(fit4)

fit5 = np.polyfit(x, load_data, 5, full=True)
fit5, fit5res, _, _, _ = fit5
fit5 = np.poly1d(fit5)

fit6 = np.polyfit(x, load_data, 6, full=True)
fit6, fit6res, _, _, _ = fit6
fit6 = np.poly1d(fit6)

fit7 = np.polyfit(x, load_data, 7, full=True)
fit7, fit7res, _, _, _ = fit7
fit7 = np.poly1d(fit7)

plt.plot(x, load_data, label='Data')
plt.plot(xp, fit3(xp), ls=':', label="3-degree, MSE {}".format(int(fit3res)))
plt.plot(xp, fit4(xp), ls=':',  label="4-degree, MSE {}".format(int(fit4res)))
plt.plot(xp, fit5(xp), ls=':',  label="5-degree, MSE {}".format(int(fit5res)))
plt.plot(xp, fit6(xp), ls='--', label="6-degree, MSE {}".format(int(fit6res)))
plt.plot(xp, fit7(xp), ls=':',  label="7-degree, MSE {}".format(int(fit7res)))

plt.xticks(fontsize="x-large")
plt.xlabel("Week of the year", fontsize="x-large")
plt.yticks(fontsize="x-large")
plt.ylabel("Percent of annual maximum", fontsize="x-large")
plt.legend(fontsize="x-large")
plt.show()