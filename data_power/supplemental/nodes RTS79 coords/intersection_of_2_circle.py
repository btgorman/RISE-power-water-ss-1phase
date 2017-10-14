import math

def distance(center1, center2):
	x1, y1, d1 = center1
	x2, y2, d2 = center2

	distance_centers = ((x1-x2)**2 + (y1-y2)**2)**0.5
	
	if distance_centers > d1 + d2:
		print("no solutions, separate circles")
		quit()
	elif distance_centers < math.fabs(d1 - d2):
		print("no solutions, circle inside the other")
		quit()
	elif distance_centers == 0 and d1 == d2:
		print("infinite solutions")
		quit()

	return distance_centers

node1 = (0., 0., 5.5)
node9 = (3.82043, 0., 3.1)
node12 = (4.12043, -1.63224, 3.3)
node15 = (8.43127, 3.1, 3.4)
node16 = (8.43127, 1.9, (16.+27.5+15.)*.1)
node17 = (9.772911, 3.1, 7.3)
node18 = (10.77291, 3.1, 1.8)
node21 = (11.37862, 1.404974, 4.97)
node23 = (10.53784, -3.55755, 6.)

point1 = node1
point2 = node9
x1, y1, d1 = point1
x2, y2, d2 = point2

dc = distance(point1, point2)

a = (d1**2 - d2**2 + dc**2) / (2. * dc)

h = (d1**2 - a**2)**0.5

xmid = x1 + a * (x2 - x1) / dc
ymid = y1 + a * (y2 - y1) / dc

x3_0 = xmid + h * (y2 - y1) / dc
y3_0 = ymid - h * (x2 - x1) / dc

x3_1 = xmid - h * (y2 - y1) / dc
y3_1 = ymid + h * (x2 - x1) / dc

print(d1**2 - (x1-x3_0)**2 - (y1-y3_0)**2)
print(d1**2 - (x1-x3_1)**2 - (y1-y3_1)**2)
print(d2**2 - (x2-x3_0)**2 - (y2-y3_0)**2)
print(d2**2 - (x2-x3_1)**2 - (y2-y3_1)**2)

print("\nx3, y3: {}, {}".format(x3_0, y3_0))
print("x3, y3: {}, {}".format(x3_1, y3_1))