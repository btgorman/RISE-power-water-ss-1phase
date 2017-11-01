import matplotlib.pyplot as plt 

summer = [100,
95,
90,
100,
110,
130,
150,
175,
200,
210,
200,
175,
150,
147,
145,
170,
200,
225,
250,
263,
275,
263,
250,
100
]

winter = [50,
45,
40,
45,
50,
58,
65,
73,
80,
73,
65,
58,
50,
45,
40,
45,
50,
58,
65,
73,
80,
73,
65,
50
]

equinox = [54,
51,
47,
53,
58,
68,
78,
90,
101,
103,
96,
85,
72,
69,
67,
78,
90,
103,
114,
121,
129,
121,
114,
54
]

annualaverage = [100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100,
100
]

x = [1,
2,
3,
4,
5,
6,
7,
8,
9,
10,
11,
12,
13,
14,
15,
16,
17,
18,
19,
20,
21,
22,
23,
24
]

plt.plot(x, summer, label='summer curve')
plt.plot(x, winter, label='winter curve')
plt.plot(x, equinox, label='spring and fall curves')
plt.plot(x, annualaverage, color='black', label='annual average')

plt.legend()
plt.xlabel('hour of the day')
plt.ylabel('percent of annual average')

plt.xlim(1,24)

plt.show()