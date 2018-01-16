# Copyright 2017 Brandon T. Gorman

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# BUILT USING PYTHON 3.6.0

'''
import subprocess
for i in range(1, 1+1):
	returncode = subprocess.call('python ./Inputs/Net1.py')
	subprocess.call('del /Q /A:-R *.*', shell=True)
	print(i)
'''
import ctypes as ct
import pandas as pd
import numpy as np
import random

import classes_power as ODC

class ENnodeparam(object): # different for QUALITY SOURCES
	ELEVATION = ct.c_int(0)
	BASEDEMAND = ct.c_int(1)
	PATTERN = ct.c_int(2)
	EMITTER = ct.c_int(3)
	INITQUAL = ct.c_int(4)
	SOURCEQUAL = ct.c_int(5)
	SOURCEPAT = ct.c_int(6)
	SOURCETYPE = ct.c_int(7)
	TANKLEVEL = ct.c_int(8)
	DEMAND = ct.c_int(9)
	HEAD = ct.c_int(10)
	PRESSURE = ct.c_int(11)
	QUALITY = ct.c_int(12)
	SOURCEMASS = ct.c_int(13)

class ENlinkparam(object):
	DIAMETER = ct.c_int(0)
	LENGTH = ct.c_int(1)
	ROUGHNESS = ct.c_int(2)
	MINORLOSS = ct.c_int(3)
	INITSTATUS = ct.c_int(4)
	INITSETTING = ct.c_int(5)
	KBULK = ct.c_int(6)
	KWALL = ct.c_int(7)
	FLOW = ct.c_int(8)
	VELOCITY = ct.c_int(9)
	HEADLOSS = ct.c_int(10)
	STATUS = ct.c_int(11)
	SETTING = ct.c_int(12)
	ENERGY = ct.c_int(13)

#---NETWORK COMPONENTS---
# TITLE

# JUNCTIONS
# RESERVOIRS
# TANKS

# PIPES
# PUMPS
# VALVES
# EMITTERS

#---SYSTEM OPERATION---
# CURVES
# PATTERNS
# ENERGY
# STATUS
# DEMANDS
# CONTROLS
# RULES

#---WATER QUALITY---
# QUALITY
# REACTIONS
# SOURCES
# MIXING

#---OPTIONS & REPORTING---
# OPTIONS
# TIMES
# REPORT

class Curve:
	CLID = 2000

	# INPUTS
	ID = 0
	TYPE = 1
	X_VALUE = 2
	Y_VALUE = 3
	# INPUT VARIABLES
	# RELIABILITY
	# CONTROLS
	# OUTPUTS

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 0
		self.num_stochastic = self.num_components * 0
		self.switch_chance = (0.0, 0.0)
		self.stochastic_chance = (0.0, 0.0)

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('WATER ERROR in Curve0')

	def createAllEN(self, txtwriter, interconn_dict):
		try:
			txtwriter.writerow(['[CURVES]'])

			for row in self.matrix:
				templist = [int(row[Curve.ID]), row[Curve.X_VALUE], row[Curve.Y_VALUE]]
				txtwriter.writerow(templist)

			txtwriter.writerow('')
		except:
			print('WATER ERROR in Curve1')

	def readAllENoutputs(self, ENlib):
		try:
			pass
		except:
			print('WATER ERROR in Curve2')

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('WATER ERROR in Curve3')

	def convertToInputTensor(self):
		try:
			# inputcols = ['ID', 'type', 'x_value', 'y_value']
			# inputdf = self.convertToDataFrame()
			# inputdf = inputdf[inputcols]
			return [], [], np.empty([0,0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			print('WATER ERROR in Curve4')
			return -1

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0,0], dtype=np.float32).flatten()
		except:
			print('WATER ERROR in Curve5')
			return -1

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		pass

class Junction:
	CLID = 2100

	# INPUTS
	ID = 0
	TYPE = 1
	FUNCTIONAL_STATUS = 2 # switch
	BASE_DEMAND = 3 # stochastic
	ELEVATION = 4
	# INPUT VARIABLES
	BASE_DEMAND_AVERAGE = 5
	PATTERN_ID = 6
	INTERCONNECTION_DISPATCH_DEMAND = 7
	INTERCONNECTION_RESPONSE_DEMAND = 8
	# RELIABILITY
	MIN_PRESSURE = 9
	# CONTROLS
	# OUTPUTS
	DEMAND = 10
	HEAD = 11
	PERCENT_DEMAND = 12
	PERCENT_PRESSURE = 13
	PRESSURE = 14
	QUALITY = 15

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 0 # temporary
		self.num_stochastic = self.num_components * 1

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('WATER ERROR in Junction0')

	def createAllEN(self, txtwriter, interconn_dict):
		try:
			txtwriter.writerow(['[JUNCTIONS]'])

			for row in self.matrix:
				pattern = ''
				if row[Junction.PATTERN_ID] != 0.0:
					pattern = int(row[Junction.PATTERN_ID])

				templist = [int(row[Junction.ID]), row[Junction.ELEVATION], row[Junction.BASE_DEMAND]+row[Junction.INTERCONNECTION_DISPATCH_DEMAND]+row[Junction.INTERCONNECTION_RESPONSE_DEMAND], pattern]
				txtwriter.writerow(templist)

			txtwriter.writerow('')
		except:
			print('WATER ERROR in Junction1')

	def readAllENoutputs(self, ENlib):
		try:
			for row in self.matrix:
				EN_ID = ct.c_char_p(str(int(row[Junction.ID])).encode('utf-8'))
				EN_idx = ct.pointer(ct.c_int(0))
				EN_val = ct.pointer(ct.c_float(0.0))

				errorcode = ENlib.ENgetnodeindex(EN_ID, EN_idx)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Junction2')
					break

				errorcode = ENlib.ENgetnodevalue(EN_idx.contents, ENnodeparam.DEMAND, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Junction2')
					break
				row[Junction.DEMAND] = EN_val.contents.value

				errorcode = ENlib.ENgetnodevalue(EN_idx.contents, ENnodeparam.HEAD, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Junction2')
					break
				row[Junction.HEAD] = EN_val.contents.value

				errorcode = ENlib.ENgetnodevalue(EN_idx.contents, ENnodeparam.PRESSURE, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Junction2')
					break
				row[Junction.PRESSURE] = EN_val.contents.value

				errorcode = ENlib.ENgetnodevalue(EN_idx.contents, ENnodeparam.QUALITY, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Junction2')
					break
				row[Junction.QUALITY] = EN_val.contents.value

				if row[Junction.BASE_DEMAND] > 0.0:
					row[Junction.PERCENT_DEMAND] = row[Junction.DEMAND] / row[Junction.BASE_DEMAND] # "fail" if 0 or less
				else:
					row[Junction.PERCENT_DEMAND] = 1.0					

				if row[Junction.MIN_PRESSURE] > 0.0:
					row[Junction.PERCENT_PRESSURE] = row[Junction.PRESSURE] / row[Junction.MIN_PRESSURE] # "fail" if less than 1
				else:
					row[Junction.PERCENT_PRESSURE] = 1.0
		except:
			print('WATER ERROR in Junction2')

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('WATER ERROR in Junction3')

	def convertToInputTensor(self):
		try:
			input_list_continuous = []
			input_list_categorical = []
			input_col_continuous = ['base_demand']

			for row in self.matrix:
				for elem in input_col_continuous:
					input_list_continuous.append('Junction_' + str(int(row[Junction.ID])) + '_' + elem)

			inputdf = self.convertToDataFrame()
			inputdf_continuous = inputdf[input_col_continuous]
			return input_list_continuous, input_list_categorical, inputdf_continuous.values.flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			print('WATER ERROR in Junction4')
			return -1

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['head', 'percent_demand', 'percent_pressure', 'quality']

			for row in self.matrix:
				for elem in output_col:
					output_list .append('Junction_' + str(int(row[Junction.ID])) + '_' + elem)

			outputdf = self.convertToDataFrame()
			outputdf = outputdf[output_col]
			return output_list, outputdf.values.flatten()
		except:
			print('WATER ERROR in Junction5')
			return -1

	def randomStochasticity(self):
		try:
			row = random.randrange(0, self.num_components)
			max_demand = 3.5
			min_demand = 0.0
			rval = random.normalvariate(0, 0.5*max_demand*0.06)
			self.matrix[row, Junction.BASE_DEMAND] += rval
			if self.matrix[row, Junction.BASE_DEMAND] > max_demand:
				self.matrix[row, Junction.BASE_DEMAND] = max_demand
			elif self.matrix[row, Junction.BASE_DEMAND] < min_demand:
				self.matrix[row, Junction.BASE_DEMAND] = min_demand
		except:
			print('WATER ERROR in Junction6')
			return -1

	def randomSwitching(self):
		pass

	def multiplyLoadFactor(self, demand_factor):
		try:
			self.matrix[:, Junction.BASE_DEMAND] = self.matrix[:, Junction.BASE_DEMAND_AVERAGE] * demand_factor
		except:
			print('WATER ERROR in Junction7')
			return -1

	def setInterconnectionDemand(self, interconn_dict, reserves_dict):
		try:
			object_generator = interconn_dict['generator']

			self.matrix[:, Junction.INTERCONNECTION_DISPATCH_DEMAND] = 0.0
			self.matrix[:, Junction.INTERCONNECTION_RESPONSE_DEMAND] = 0.0

			for junction in self.matrix:
				for generator in object_generator.matrix:
					if junction[Junction.ID] == generator[ODC.Generator.JUNCTION_ID]:
						junction[Junction.INTERCONNECTION_DISPATCH_DEMAND] += generator[ODC.Generator.OPERATIONAL_STATUS]*generator[ODC.Generator.REAL_GENERATION]*generator[ODC.Generator.WATER_CONSUMPTION]*0.001
						junction[Junction.INTERCONNECTION_RESPONSE_DEMAND] += reserves_dict[generator[ODC.Generator.ID]]*generator[ODC.Generator.WATER_CONSUMPTION]*0.001

		except:
			print('WATER ERROR in Junction8')
			return -1

class Reservoir:
	CLID = 2101

	# INPUTS
	ID = 0
	TYPE = 1
	FUNCTIONAL_STATUS = 2 # switch
	TOTAL_HEAD = 3
	# INPUT VARIABLES
	# RELIABILITY
	# CONTROLS
	# OUTPUTS
	DEMAND = 4
	HEAD = 5
	PRESSURE = 6

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 0 # temporary
		self.num_stochastic = self.num_components * 0
		self.switch_chance = (0.0, 0.0)
		self.stochastic_chance = (0.0, 0.0)

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('WATER ERROR in Reservoir0')

	def createAllEN(self, txtwriter, interconn_dict):
		try:
			txtwriter.writerow(['[RESERVOIRS]'])

			for row in self.matrix:
				pattern = ''

				templist = [int(row[Reservoir.ID]), row[Reservoir.TOTAL_HEAD], pattern]
				txtwriter.writerow(templist)

			txtwriter.writerow('')
		except:
			print('WATER ERROR in Reservoir1')

	def readAllENoutputs(self, ENlib):
		try:
			for row in self.matrix:
				EN_ID = ct.c_char_p(str(int(row[Reservoir.ID])).encode('utf-8'))
				EN_idx = ct.pointer(ct.c_int(0))
				EN_val = ct.pointer(ct.c_float(0.0))

				errorcode = ENlib.ENgetnodeindex(EN_ID, EN_idx)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Reservoir2')
					break

				errorcode = ENlib.ENgetnodevalue(EN_idx.contents, ENnodeparam.DEMAND, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Reservoir2')
					break
				row[Reservoir.DEMAND] = EN_val.contents.value

				errorcode = ENlib.ENgetnodevalue(EN_idx.contents, ENnodeparam.HEAD, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Reservoir2')
					break
				row[Reservoir.HEAD] = EN_val.contents.value

				errorcode = ENlib.ENgetnodevalue(EN_idx.contents, ENnodeparam.PRESSURE, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Reservoir2')
					break
				row[Reservoir.PRESSURE] = EN_val.contents.value
		except:
			print('WATER ERROR in Reservoir2')

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('WATER ERROR in Reservoir3')

	def convertToInputTensor(self):
		try:
			return [], [], np.empty([0,0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			print('WATER ERROR in Reservoir4')
			return -1

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['demand', 'head', 'pressure']

			for row in self.matrix:
				for elem in output_col:
					output_list.append('Reservoir_' + str(int(row[Reservoir.ID])) + '_' + elem)

			outputdf = self.convertToDataFrame()
			outputdf = outputdf[output_col]
			return output_list, outputdf.values.flatten()
		except:
			print('WATER ERROR in Reservoir5')
			return -1

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		pass

class Tank:
	CLID = 2102

	# INPUTS
	ID = 0
	TYPE = 1
	FUNCTIONAL_STATUS = 2 # switch
	DIAMETER = 3
	ELEVATION = 4
	INITIAL_LEVEL = 5 # stochastic
	MAX_LEVEL = 6
	MIN_VOLUME = 7
	# INPUT VARIABLES
	# RELIABILITY
	MIN_LEVEL = 8
	# CONTROLS
	# OUTPUTS
	DEMAND = 9
	HEAD = 10
	PERCENT_LEVEL = 11
	PRESSURE = 12
	QUALITY = 13

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 0 # temporary
		self.num_stochastic = self.num_components * 1

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('WATER ERROR in Tank0')

	def createAllEN(self, txtwriter, interconn_dict):
		try:
			txtwriter.writerow(['[TANKS]'])

			for row in self.matrix:
				templist = [int(row[Tank.ID]), row[Tank.ELEVATION], row[Tank.INITIAL_LEVEL], row[Tank.MIN_LEVEL],
				row[Tank.MAX_LEVEL], row[Tank.DIAMETER], row[Tank.MIN_VOLUME]]
				txtwriter.writerow(templist)

			txtwriter.writerow('')
		except:
			print('WATER ERROR in Tank1')

	def readAllENoutputs(self, ENlib):
		try:
			for row in self.matrix:
				EN_ID = ct.c_char_p(str(int(row[Tank.ID])).encode('utf-8'))
				EN_idx = ct.pointer(ct.c_int(0))
				EN_val = ct.pointer(ct.c_float(0.0))

				errorcode = ENlib.ENgetnodeindex(EN_ID, EN_idx)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Tank2')
					break

				errorcode = ENlib.ENgetnodevalue(EN_idx.contents, ENnodeparam.DEMAND, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Tank2')
					break
				row[Tank.DEMAND] = EN_val.contents.value

				errorcode = ENlib.ENgetnodevalue(EN_idx.contents, ENnodeparam.HEAD, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Tank2')
					break
				row[Tank.HEAD] = EN_val.contents.value

				errorcode = ENlib.ENgetnodevalue(EN_idx.contents, ENnodeparam.PRESSURE, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Tank2')
					break
				row[Tank.PRESSURE] = EN_val.contents.value

				errorcode = ENlib.ENgetnodevalue(EN_idx.contents, ENnodeparam.QUALITY, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Tank2')
					break
				row[Tank.QUALITY] = EN_val.contents.value

				if row[Tank.MAX_LEVEL] == 0.0:
					row[Tank.PERCENT_LEVEL] = 0.0
					print('empty')
				else:
					row[Tank.PERCENT_LEVEL] = (row[Tank.HEAD] - row[Tank.MIN_LEVEL] - row[Tank.ELEVATION]) / row[Tank.MAX_LEVEL] # "fail" is less than 0
		except:
			print('WATER ERROR in Tank2')

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('WATER ERROR in Tank3')

	def convertToInputTensor(self):
		try:
			return [], [], np.empty([0,0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			print('WATER ERROR in Tank4')
			return -1

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['demand', 'head', 'percent_level', 'pressure', 'quality']
			
			for row in self.matrix:
				for elem in output_col:
					output_list.append('Tank_' + str(int(row[Tank.ID])) + '_' + elem)

			outputdf = self.convertToDataFrame()
			outputdf = outputdf[output_col]
			return output_list, outputdf.values.flatten()
		except:
			print('WATER ERROR in Tank5')
			return -1

	def randomStochasticity(self):
		try:
			row = random.randrange(0, self.num_components)
			rval = random.normalvariate(0, 0.5*self.matrix[row, Tank.MAX_LEVEL]*0.06)
			self.matrix[row, Tank.INITIAL_LEVEL] += rval
			if self.matrix[row, Tank.INITIAL_LEVEL] > self.matrix[row, Tank.MAX_LEVEL]:
				self.matrix[row, Tank.INITIAL_LEVEL] = self.matrix[row, Tank.MAX_LEVEL]
			elif self.matrix[row, Tank.INITIAL_LEVEL] < self.matrix[row, Tank.MIN_LEVEL]:
				self.matrix[row, Tank.INITIAL_LEVEL] = self.matrix[row, Tank.MIN_LEVEL]
		except:
			print('WATER ERROR in Tank6')
			return -1

	def randomSwitching(self):
		pass

class Pipe:
	CLID = 2200

	# INPUTS
	ID = 0
	TYPE = 1
	TERMINAL_1_ID = 2
	TERMINAL_2_ID = 3
	FUNCTIONAL_STATUS = 4 # switch
	DIAMETER = 5
	LENGTH = 6
	LOSS_COEFFICIENT = 7
	ROUGHNESS = 8
	# INPUT VARIABLES
	# RELIABILITY
	MAX_VELOCITY = 9
	# CONTROLS
	OPERATIONAL_STATUS = 10 # switch
	CV_STATUS = 11
	# OUTPUTS
	FLOW = 12
	HEADLOSS = 1

	PERCENT_VELOCITY = 14
	VELOCITY = 15

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 1 # temporary
		self.num_stochastic = self.num_components * 0
		self.switch_chance = (0.0, 0.0)
		self.stochastic_chance = (0.0, 0.0)

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('WATER ERROR in Pipe0')

	def createAllEN(self, txtwriter, interconn_dict):
		try:
			txtwriter.writerow(['[PIPES]'])

			for row in self.matrix:
				status = 'CLOSED'
				if row[Pipe.OPERATIONAL_STATUS] == 1.0:
					if row[Pipe.CV_STATUS] == 1.0:
						status = 'CV'
					else:
						status = 'OPEN'

				templist = [int(row[Pipe.ID]), int(row[Pipe.TERMINAL_1_ID]), int(row[Pipe.TERMINAL_2_ID]), row[Pipe.LENGTH],
				row[Pipe.DIAMETER], row[Pipe.ROUGHNESS], row[Pipe.LOSS_COEFFICIENT], status]
				txtwriter.writerow(templist)

			txtwriter.writerow('')
		except:
			print('WATER ERROR in Pipe1')

	def readAllENoutputs(self, ENlib):
		try:
			for row in self.matrix:
				EN_ID = ct.c_char_p(str(int(row[Pipe.ID])).encode('utf-8'))
				EN_idx = ct.pointer(ct.c_int(0))
				EN_val = ct.pointer(ct.c_float(0.0))

				errorcode = ENlib.ENgetlinkindex(EN_ID, EN_idx)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Pipe2')
					break

				errorcode = ENlib.ENgetlinkvalue(EN_idx.contents, ENlinkparam.FLOW, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Pipe2')
					break
				row[Pipe.FLOW] = EN_val.contents.value

				errorcode = ENlib.ENgetlinkvalue(EN_idx.contents, ENlinkparam.HEADLOSS, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Pipe2')
					break
				row[Pipe.HEADLOSS] = EN_val.contents.value

				errorcode = ENlib.ENgetlinkvalue(EN_idx.contents, ENlinkparam.VELOCITY, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Pipe2')
					break
				row[Pipe.VELOCITY] = EN_val.contents.value

				row[Pipe.PERCENT_VELOCITY] = row[Pipe.VELOCITY] / row[Pipe.MAX_VELOCITY] # "fail" if greater than 1
		except:
			print('WATER ERROR in Pipe2')

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('WATER ERROR in Pipe3')

	def convertToInputTensor(self):
		try:
			input_list_continuous = []
			input_list_categorical = []
			input_col_categorical = ['operational_status', 'cv_status']

			for row in self.matrix:
				for elem in input_col_categorical:
					input_list_categorical.append('Pipe_' + str(int(row[Pipe.ID])) + '_' + elem)

			inputdf = self.convertToDataFrame()
			inputdf_categorical = inputdf[input_col_categorical]
			return input_list_continuous, input_list_categorical, np.empty([0,0], dtype=np.float32).flatten(), inputdf_categorical.values.flatten() 
		except:
			print('WATER ERROR in Pipe4')
			return -1

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['flow', 'headloss', 'percent_velocity']

			for row in self.matrix:
				for elem in output_col:
					output_list.append('Pipe_' + str(int(row[Pipe.ID])) + '_' + elem)

			outputdf = self.convertToDataFrame()
			outputdf = outputdf[output_col]
			return output_list, outputdf.values.flatten()
		except:
			print('WATER ERROR in Pipe5')
			return -1

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		try:
			row = random.randrange(0, self.num_components)
			self.matrix[row, Pipe.OPERATIONAL_STATUS] = 0.0
		except:
			print('WATER ERROR in Pipe6')

class Pump:
	CLID = 2201

	# INPUTS
	ID = 0
	TYPE = 1
	TERMINAL_1_ID = 2
	TERMINAL_2_ID = 3
	FUNCTIONAL_STATUS = 4 # switch
	CURVE_ID = 5
	POWER = 6
	SPEED = 7 # stochastic
	LOAD_ID = 8
	# INPUT VARIABLES
	# RELIABILITY
	# CONTROLS
	OPERATIONAL_STATUS = 9 # switch
	# OUTPUTS
	POWER_CONSUMPTION = 10
	FLOW = 11
	HEADLOSS = 12
	VELOCITY = 13

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 1 # temporary
		self.num_stochastic = self.num_components * 1

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('WATER ERROR in Pump0')

	def createAllEN(self, txtwriter, interconn_dict):
		try:
			txtwriter.writerow(['[PUMPS]'])

			for row in self.matrix:
				if row[Pump.CURVE_ID] != 0.0:
					templist = [int(row[Pump.ID]), int(row[Pump.TERMINAL_1_ID]), int(row[Pump.TERMINAL_2_ID]), 'HEAD',
					int(row[Pump.CURVE_ID]), 'SPEED', row[Pump.OPERATIONAL_STATUS]*row[Pump.SPEED]]
					txtwriter.writerow(templist)
				else:
					templist = [int(row[Pump.ID]), int(row[Pump.TERMINAL_1_ID]), int(row[Pump.TERMINAL_2_ID]), 'POWER',
					row[Pump.POWER], 'SPEED', row[Pump.OPERATIONAL_STATUS]*row[Pump.SPEED]]
					txtwriter.writerow(templist)

			txtwriter.writerow('')
		except:
			print('WATER ERROR in Pump1')

	def readAllENoutputs(self, ENlib):
		try:
			for row in self.matrix:
				EN_ID = ct.c_char_p(str(int(row[Pump.ID])).encode('utf-8'))
				EN_idx = ct.pointer(ct.c_int(0))
				EN_val = ct.pointer(ct.c_float(0.0))

				errorcode = ENlib.ENgetlinkindex(EN_ID, EN_idx)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Pump2')
					break

				errorcode = ENlib.ENgetlinkvalue(EN_idx.contents, ENlinkparam.ENERGY, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Pump2')
					break
				row[Pump.POWER_CONSUMPTION] = EN_val.contents.value

				errorcode = ENlib.ENgetlinkvalue(EN_idx.contents, ENlinkparam.FLOW, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Pump2')
					break
				row[Pump.FLOW] = EN_val.contents.value

				errorcode = ENlib.ENgetlinkvalue(EN_idx.contents, ENlinkparam.HEADLOSS, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Pump2')
					break
				row[Pump.HEADLOSS] = EN_val.contents.value

				errorcode = ENlib.ENgetlinkvalue(EN_idx.contents, ENlinkparam.VELOCITY, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Pump2')
					break
				row[Pump.VELOCITY] = EN_val.contents.value
		except:
			print('WATER ERROR in Pump2')

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('WATER ERROR in Pump3')

	def convertToInputTensor(self):
		try:
			input_list_continuous = []
			input_list_categorical = []
			input_col_continuous = ['speed']
			input_col_categorical = ['operational_status']

			for row in self.matrix:
				for elem in input_col_continuous:
					input_list_continuous.append('Pump_' + str(int(row[Pump.ID])) + '_' + elem)
				for elem in input_col_categorical:
					input_list_categorical.append('Pump_' + str(int(row[Pump.ID])) + '_' + elem)

			inputdf = self.convertToDataFrame()
			inputdf_continuous = inputdf[input_col_continuous]
			inputdf_categorical = inputdf[input_col_categorical]
			return input_list_continuous, input_list_categorical, inputdf_continuous.values.flatten(), inputdf_categorical.values.flatten() 
		except:
			print('WATER ERROR in Pump4')
			return -1

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['power_consumption', 'flow', 'headloss', 'velocity']

			for row in self.matrix:
				for elem in output_col:
					output_list.append('Pump_' + str(int(row[Pump.ID])) + '_' + elem)

			outputdf = self.convertToDataFrame()
			outputdf = outputdf[output_col]
			return output_list, outputdf.values.flatten()
		except:
			print('WATER ERROR in Pump5')
			return -1

	def randomStochasticity(self):
		try:
			row = random.randrange(0, self.num_components)
			rval = random.normalvariate(0, 0.5*1.0*0.06)
			self.matrix[row, Pump.SPEED] += rval
			if self.matrix[row, Pump.SPEED] > 1.1:
				self.matrix[row, Pump.SPEED] = 1.1
			elif self.matrix[row, Pump.SPEED] < 0.04:
				self.matrix[row, Pump.SPEED] = 0.04
		except:
			print('WATER ERROR in Pump6')
			return -1

	def randomSwitching(self):
		try:
			row = random.randrange(0, self.num_components)
			self.matrix[row, Pump.OPERATIONAL_STATUS] = 0.0
		except:
			print('WATER ERROR in Pump7')

class Valve:
	CLID = 2202

	# INPUTS
	ID = 0
	TYPE = 1
	TERMINAL_1_ID = 2
	TERMINAL_2_ID = 3
	FUNCTIONAL_STATUS = 4 # switch
	DIAMETER = 5
	HEADLOSS = 6
	LOSS_COEFFICIENT = 7
	MODEL = 8
	SETTING = 9
	# INPUT VARIABLES
	# RELIABILITY
	# CONTROLS
	OPERATIONAL_STATUS = 10 # switch
	# OUTPUTS
	FLOW = 11
	HEADLOSS = 12
	VELOCITY = 13

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 1 # temporary "FIXED STATUS" also?
		self.num_stochastic = self.num_components * 0
		self.switch_chance = (0.0, 0.0)
		self.stochastic_chance = (0.0, 0.0)

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('WATER ERROR in Valve0')

	def createAllEN(self, txtwriter, interconn_dict):
		try:
			txtwriter.writerow(['[VALVES]'])

			for row in self.matrix:
				multiplier = 1

				# if self.valveType(row[Valve.MODEL] == 'FCV'):
				# 	multiplier = 0

				templist = [int(row[Valve.ID]), int(row[Valve.TERMINAL_1_ID]), int(row[Valve.TERMINAL_2_ID]), row[Valve.DIAMETER],
				self.valveType(row[Valve.MODEL]), multiplier*row[Valve.SETTING], row[Valve.LOSS_COEFFICIENT]]
				txtwriter.writerow(templist)

			txtwriter.writerow('')
		except:
			print('WATER ERROR in Valve1')

	def readAllENoutputs(self, ENlib):
		try:
			for row in self.matrix:
				EN_ID = ct.c_char_p(str(int(row[Valve.ID])).encode('utf-8'))
				EN_idx = ct.pointer(ct.c_int(0))
				EN_val = ct.pointer(ct.c_float(0.0))

				errorcode = ENlib.ENgetlinkindex(EN_ID, EN_idx)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Valve2')
					break

				errorcode = ENlib.ENgetlinkvalue(EN_idx.contents, ENlinkparam.FLOW, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Valve2')
					break
				row[Valve.FLOW] = EN_val.contents.value

				errorcode = ENlib.ENgetlinkvalue(EN_idx.contents, ENlinkparam.HEADLOSS, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Valve2')
					break
				row[Valve.HEADLOSS] = EN_val.contents.value

				errorcode = ENlib.ENgetlinkvalue(EN_idx.contents, ENlinkparam.VELOCITY, EN_val)
				if errorcode != 0:
					print('WATER ERRORCODE', errorcode, 'in Valve2')
					break
				row[Valve.VELOCITY] = EN_val.contents.value
		except:
			print('WATER ERROR in Valve2')

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('WATER ERROR in Valve3')

	def valveType(self, floatval):
		try:
			tempdict = {0.0: 'PRV', 1.0: 'PSV', 2.0: 'PBV', 3.0: 'FCV',
			4.0: 'TCV', 5.0: 'GPV'}
			return tempdict[floatval]
		except:
			print('WATER ERROR in Valve4')

	def convertToInputTensor(self):
		try:
			return [], [], np.empty([0,0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			print('WATER ERROR in Valve5')
			return -1

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0,0], dtype=np.float32).flatten()
		except:
			print('WATER ERROR in Valve6')
			return -1

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		pass

class Emitter:
	CLID = 2203

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 0
		self.num_stochastic = self.num_components * 0
		self.switch_chance = (0.0, 0.0)
		self.stochastic_chance = (0.0, 0.0)

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('WATER ERROR in Emitter0')

	def createAllEN(self, txtwriter, interconn_dict):
		try:
			pass
		except:
			print('WATER ERROR in Emitter1')

	def readAllENoutputs(self, ENlib):
		try:
			pass
		except:
			print('WATER ERROR in Emitter2')

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('WATER ERROR in Emitter3')

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		pass