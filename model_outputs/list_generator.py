import csv
import collections
import itertools

with open('list_set_of_set.csv', 'r') as file:
	reader = csv.reader(file)
	new_list = list(reader)

listid = []
listid.append(1)
listlist = [[]]
listset = [set()]
incr = 1 # track when pipeid changes
idx = 0 # listlist idx

for row in new_list:
	pipeid = int(row[1])
	if pipeid != incr:
		listid.append(pipeid)
		listlist.append([])
		listset.append(set())
		incr = pipeid
		idx += 1
	listlist[idx].append(tuple(map(int, tuple(filter(None, row[2::])))))

for itemidx in range(0, len(listlist)):
	for elem in listlist[itemidx]:
		listset[itemidx].update(elem)

# print(listlist[0])
# print(listset[0])
# print('')

totalcomb = [[]]
totalperm = [[]]
comb_counter = [{}]

for idx in range(0, len(listlist)):
	if idx > 0:
		totalcomb.append([])
		totalperm.append([])
		comb_counter.append({})

	for num_combs in range(1, 4+1):
		if num_combs <= len(listset[idx]):
			totalcomb[idx] += itertools.combinations(list(listset[idx]), num_combs)

	for elem in listlist[idx]:
		for num_perms in range(1, len(elem)+1):
			totalperm[idx] += itertools.permutations(elem, num_perms)

	c = collections.Counter(totalperm[idx])

	for elem in totalcomb[idx]:
		comb_counter[idx][elem] = c[elem]

checkidx = 37
print(listid[checkidx])
print(listlist[checkidx])
print(listset[checkidx])
print('')

print(totalcomb[checkidx])
print(totalperm[checkidx])
print(comb_counter[checkidx])

with open('critical_junctions.csv', 'w', newline='') as file:
	writer = csv.writer(file)
	for idx in range(0, len(listlist)):
		for key,value in comb_counter[idx].items():
			writer.writerow([listid[idx], list(key), value])
