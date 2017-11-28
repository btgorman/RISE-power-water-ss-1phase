import math

water_node_coords = {
1: (0.0, 0.0),
2: (0.0, -24.0),
3: (368.918528, 239.78976),
104: (176.0, 172.774),
204: (176.0, 172.774),
5: (176.0, 0.0),
6: (329.6344, -256.309072),
7: (-32.11296, -193.28946),
8: (-32.11296, -65.28946),
9: (305.6344, 0.0),
10: (305.6344, -130.57892),
11: (384.3914, -232.3986),
12: (577.3952, -132.1365),
13: (374.8928, -390.67088),
14: (559.56864, -30.89096),
15: (674.5016, 248.0),
16: (674.5016, 152.0),
17: (550.6213, -200.7599),
18: (861.83288, 248.0),
19: (720.59408, 32.586944),
120: (799.8152, -172.6544),
220: (799.8152, -172.6544),
21: (838.0272, -213.75),
22: (0.0, 297.9609),
23: (525.2384, -307.9051),
24: (60.9741, -155.5429),
25: (130.0642, 39.0259),
26: (535.9741, -275.0),
27: (739.0259, -575.9741),
28: (1166.8068, -519.1932),
29: (200.0, -217.9305),
30: (133.5887, -156.517),
31: (118.533, 237.7912),
32: (643.4957, -405.9851),
33: (835.5014, -410.4837),
34: (674.5576, -325.329),
35: (914.9742, -221.3459),
36: (919.8488, -260.5014),
37: (363.7738, -188.2386),
38: (696.4755, -121.4755)
}

connection_list = [
(1, 22, 31),
(2, 31, 104),
(4, 204, 9),
(6, 9, 14),
(13, 14, 38),
(14, 38, 120),
(15, 220, 35),
(16, 35, 36),
(17, 36, 28),
(23, 5, 25),
(24, 10, 5),
(25, 37, 10),
(26, 17, 37),
(27, 12, 17),
(28, 21, 12),
(29, 21, 34),
(30, 34, 32),
(31, 21, 33),
(32, 33, 27),
(33, 33, 32),
(34, 32, 13),
(35, 17, 26),
(36, 23, 11),
(37, 11, 6),
(41, 6, 29),
(42, 29, 30),
(43, 30, 24),
(5, 9, 3),
(8, 16, 15),
(9, 14, 16),
(10, 15, 18),
(11, 16, 19),
(12, 19, 18),
(18, 5, 1),
(19, 1, 2),
(20, 2, 8),
(21, 8, 7),
(22, 7, 5),
(38, 13, 6),
(39, 6, 14),
(40, 13, 14)
]

for row in connection_list:
	connection_id, node_1, node_2 = row

	node_1_x, node_1_y = water_node_coords[node_1]
	node_2_x, node_2_y = water_node_coords[node_2]
	distance = math.sqrt((node_1_x-node_2_x)**2 + (node_1_y-node_2_y)**2) / 8.

	print('Branch ID {} is {:.2f} mi. long'.format(connection_id, distance))