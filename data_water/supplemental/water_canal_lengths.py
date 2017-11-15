import math

water_node_coords = {
1: (0.0, 0.0),
2: (0.0, -24.0),
3: (368.918528, 239.78976),
4: (176.0, 172.774),
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
20: (799.8152, -172.6544),
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
37: (363.7738, -188.2386)
}

connection_list = [
(1, 22, 31),
(2, 31, 4),
(3, 4, 9),
(4, 9, 3),
(5, 9, 14),
(6, 14, 16),
(7, 16, 15),
(8, 15, 17),
(9, 17, 18),
(10, 18, 19),
(11, 19, 16),
(12, 14, 16),
(13, 9, 14),
(14, 14, 5),
(15, 5, 20),
(16, 20, 35),
(17, 35, 36),
(18, 36, 28),
(19, 21, 12),
(20, 12, 17),
(21, 17, 37),
(22, 37, 10),
(23, 17, 26),
(24, 21, 33),
(25, 33, 27),
(26, 21, 34),
(27, 34, 32),
(28, 33, 32),
(29, 32, 13),
(30, 13, 6),
(31, 6, 29),
(32, 29, 30),
(33, 30, 24),
(34, 23, 11),
(35, 11, 6),
(36, 10, 5),
(37, 5, 25),
(38, 5, 7),
(39, 7, 8),
(40, 8, 2),
(41, 2, 1),
(42, 1, 5)
]

for row in connection_list:
	connection_id, node_1, node_2 = row

	node_1_x, node_1_y = water_node_coords[node_1]
	node_2_x, node_2_y = water_node_coords[node_2]
	distance = math.sqrt((node_1_x-node_2_x)**2 + (node_1_y-node_2_y)**2) / 8.

	print('Branch ID {} is {:.2f} mi. long'.format(connection_id, distance))