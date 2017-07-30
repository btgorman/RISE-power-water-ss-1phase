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

# LAST EDITED: JUNE 16, 2017
# BUILT USING PYTHON 3.6.0

import numpy as np
import pandas as pd
import math, random

class TemperatureDerating:
	condmult = 1.0
	loadmult = 1.0
	genmult = 1.0

	def condmult(cls):
		pass

	def loadmult(cls):
		pass

	def genmult(cls):
		pass

class XYCurve: #errors -1000 to -1024
	CLID = 1000
	
	ID = 0
	TYPE = 1
	X_1_COORDINATE = 2
	X_2_COORDINATE = 3
	X_3_COORDINATE = 4
	X_4_COORDINATE = 5
	X_5_COORDINATE = 6
	Y_1_COORDINATE = 7
	Y_2_COORDINATE = 8
	Y_3_COORDINATE = 9
	Y_4_COORDINATE = 10
	Y_5_COORDINATE = 11
	NPTS = 5

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
			print('POWER ERROR in XYCurve0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			for row in self.matrix:
				str_self_name = str(int(row[XYCurve.TYPE])) + '_' + str(int(row[XYCurve.ID]))

				if debug == 1:
					print('New \'XYCurve.{}\' npts=\'{}\' xarray=[{:f} {:f} {:f} {:f} {:f}] yarray=[{:f} {:f} {:f} {:f} {:f}]\n'.format(
					str_self_name, XYCurve.NPTS, row[XYCurve.X_1_COORDINATE], row[XYCurve.X_2_COORDINATE],
					row[XYCurve.X_3_COORDINATE], row[XYCurve.X_4_COORDINATE], row[XYCurve.X_5_COORDINATE], row[XYCurve.Y_1_COORDINATE],
					row[XYCurve.Y_2_COORDINATE], row[XYCurve.Y_3_COORDINATE], row[XYCurve.Y_4_COORDINATE], row[XYCurve.Y_5_COORDINATE]))

				dss.Command = 'New \'XYCurve.{}\' npts=\'{}\' xarray=[{:f} {:f} {:f} {:f} {:f}] yarray=[{:f} {:f} {:f} {:f} {:f}]'.format(
					str_self_name, XYCurve.NPTS, row[XYCurve.X_1_COORDINATE], row[XYCurve.X_2_COORDINATE],
					row[XYCurve.X_3_COORDINATE], row[XYCurve.X_4_COORDINATE], row[XYCurve.X_5_COORDINATE], row[XYCurve.Y_1_COORDINATE],
					row[XYCurve.Y_2_COORDINATE], row[XYCurve.Y_3_COORDINATE], row[XYCurve.Y_4_COORDINATE], row[XYCurve.Y_5_COORDINATE])
			return 0
		except:
			print('Error: #-1000')
			return -1000

	def addToNodesDict(self, dictionary):
		try:
			return 0
		except:
			print('Error: #-1002')
			return -1002

	def voltagesToSets(self):
		return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			return 0
		except:
			print('Error: #-1004')
			return -1004

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1006')
			return -1006

	def returnWindGenFraction(self, curve_id, wind_fraction):
		try:
			for row in self.matrix:
				if row[XYCurve.ID] == curve_id:
					gen_fraction = 0.0
					if wind_fraction < row[XYCurve.Y_1_COORDINATE]:
						gen_fraction = 0.0
					elif wind_fraction > row[XYCurve.Y_5_COORDINATE]:
						gen_fraction = 1.0
					elif wind_fraction < row[XYCurve.Y_2_COORDINATE]:
						gen_fraction = row[XYCurve.X_1_COORDINATE] + (wind_fraction - row[XYCurve.Y_1_COORDINATE]) * (row[XYCurve.X_2_COORDINATE] - row[XYCurve.X_1_COORDINATE]) / (row[XYCurve.Y_2_COORDINATE] - row[XYCurve.Y_1_COORDINATE])
					elif wind_fraction < row[XYCurve.Y_3_COORDINATE]:
						gen_fraction = row[XYCurve.X_2_COORDINATE] + (wind_fraction - row[XYCurve.Y_2_COORDINATE]) * (row[XYCurve.X_3_COORDINATE] - row[XYCurve.X_2_COORDINATE]) / (row[XYCurve.Y_3_COORDINATE] - row[XYCurve.Y_2_COORDINATE])
					elif wind_fraction < row[XYCurve.Y_4_COORDINATE]:
						gen_fraction =  row[XYCurve.X_3_COORDINATE] + (wind_fraction - row[XYCurve.Y_3_COORDINATE]) * (row[XYCurve.X_4_COORDINATE] - row[XYCurve.X_3_COORDINATE]) / (row[XYCurve.Y_4_COORDINATE] - row[XYCurve.Y_3_COORDINATE])
					else:
						gen_fraction = row[XYCurve.X_4_COORDINATE] + (wind_fraction - row[XYCurve.Y_4_COORDINATE]) * (row[XYCurve.X_5_COORDINATE] - row[XYCurve.X_4_COORDINATE]) / (row[XYCurve.Y_5_COORDINATE] - row[XYCurve.Y_4_COORDINATE])
					return gen_fraction
			print('Error: #-1007')
		except:
			print('Error: #-1008')
			return -1008

	def convertToInputTensor(self):
		try:
			return [], [], np.empty([0, 0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			print('Error: #-1009')
			return -1009

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0, 0], dtype=np.float32).flatten()
		except:
			return 0

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		pass

class RegControl: #errors -1050 to -1074
	CLID = 1100

	ID = 0
	TYPE = 1
	TRANSFORMER_ID = 2
	BANDWIDTH = 3
	CT_RATING = 4
	PT_RATIO = 5
	R1 = 6
	REGULATOR_VOLTAGE = 7
	X1 = 8
	
	def __init__(self,dframe):
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
			print('POWER ERROR in RegControl0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		return 0

	def addToNodesDict(self, dictionary):
		return 0

	def voltagesToSets(self):
		return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		return 0

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1056')
			return -1056

	def convertToInputTensor(self):
		try:
			return [], [], np.empty([0, 0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			pass

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0, 0], dtype=np.float32).flatten()
		except:
			pass

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		pass

class WireData: #errors -1100 to -1124
	CLID = 1200
	
	ID = 0
	TYPE = 1
	DIAMETER = 2
	GMR = 3
	NORMAL_AMPS = 4
	R_SCALAR = 5
	MAX_PU_CAPACITY = 6
	RESISTANCE_UNITS = 'kft'
	GMR_UNITS = 'ft'
	DIAMETER_UNITS = 'in'

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
			print('POWER ERROR in WireData0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			for row in self.matrix:
				str_self_name = str(int(row[WireData.TYPE])) + '_' + str(int(row[WireData.ID]))

				if debug == 1:
					print('New \'WireData.{}\' Diam=\'{:f}\' Radunit=\'{}\' GMRac=\'{:f}\' GMRunits=\'{}\' Rac=\'{:f}\' Runits=\'{}\' Normamps=\'{:f}\' Emergamps=\'{:f}\'\n'.format(
					str_self_name, row[WireData.DIAMETER], WireData.DIAMETER_UNITS, row[WireData.GMR],
					WireData.GMR_UNITS, row[WireData.R_SCALAR], WireData.RESISTANCE_UNITS, row[WireData.NORMAL_AMPS],
					row[WireData.NORMAL_AMPS]*row[WireData.MAX_PU_CAPACITY]))

				dss.Command = 'New \'WireData.{}\' Diam=\'{:f}\' Radunit=\'{}\' GMRac=\'{:f}\' GMRunits=\'{}\' Rac=\'{:f}\' Runits=\'{}\' Normamps=\'{:f}\' Emergamps=\'{:f}\''.format(
					str_self_name, row[WireData.DIAMETER], WireData.DIAMETER_UNITS, row[WireData.GMR],
					WireData.GMR_UNITS, row[WireData.R_SCALAR], WireData.RESISTANCE_UNITS, row[WireData.NORMAL_AMPS],
					row[WireData.NORMAL_AMPS]*row[WireData.MAX_PU_CAPACITY])
			return 0,
		except:
			print('Error: #-1100')
			return -1100

	def addToNodesDict(self, dictionary):
		try:
			return 0
		except:
			print('Error: #-1102')
			return -1102

	def voltagesToSets(self):
		return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			return 0
		except:
			print('Error: #-1104')
			return -1104

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1106')
			return -1106

	def convertToInputTensor(self):
		try:
			return [], [], np.empty([0, 0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			return 0

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0, 0], dtype=np.float32).flatten()
		except:
			return 0

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		pass

class LineCode: #errors -1125 to -1149
	CLID = 1201

	ID = 0
	TYPE = 1
	KRON_REDUCTION = 2
	NORMAL_AMPS = 3
	NUMBER_OF_PHASES = 4
	R0_SCALAR = 5
	R1_SCALAR = 6
	X0_SCALAR = 7
	X1_SCALAR = 8
	MAX_PU_CAPACITY = 23
	UNITS = 'kft'

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
			print('POWER ERROR in LineCode0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			for row in self.matrix:
				neutral_reduce = 'N'

				if row[LineCode.KRON_REDUCTION] == 1.0:
					neutral_reduce = 'Y'

				str_self_name = str(int(row[LineCode.TYPE])) + '_' + str(int(row[LineCode.ID]))

				if debug == 1:
					print('New \'LineCode.{}\' Nphases=\'{}\' R0=\'{}\' R1=\'{}\' X0=\'{}\' X1=\'{}\' Units=\'{}\' Normamps=\'{:f}\' Emergamps=\'{:f}\' Kron=\'{}\''.format(
					str_self_name, int(row[LineCode.NUMBER_OF_PHASES]), row[LineCode.R0_SCALAR], row[LineCode.R1_SCALAR],
					row[LineCode.X0_SCALAR], row[LineCode.X1_SCALAR], LineCode.UNITS, row[LineCode.NORMAL_AMPS],
					row[LineCode.NORMAL_AMPS]*row[LineCode.MAX_PU_CAPACITY], neutral_reduce))
					print('\n')

				dss.Command = 'New \'LineCode.{}\' Nphases=\'{}\' R0=\'{}\' R1=\'{}\' X0=\'{}\' X1=\'{}\' Units=\'{}\' Normamps=\'{:f}\' Emergamps=\'{:f}\' Kron=\'{}\''.format(
					str_self_name, int(row[LineCode.NUMBER_OF_PHASES]), row[LineCode.R0_SCALAR], row[LineCode.R1_SCALAR],
					row[LineCode.X0_SCALAR], row[LineCode.X1_SCALAR], LineCode.UNITS, row[LineCode.NORMAL_AMPS],
					row[LineCode.NORMAL_AMPS]*row[LineCode.MAX_PU_CAPACITY], neutral_reduce)
			return 0
		except:
			print('Error: #-1125')
			return -1125

	def addToNodesDict(self, dictionary):
		try:
			return 0
		except:
			print('Error: #-1127')
			return -1127

	def voltagesToSets(self):
		return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			return 0
		except:
			print('Error: #-1129')
			return -1129

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1131')
			return -1131

	def convertToInputTensor(self):
		try:
			return [], [], np.empty([0, 0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			print('Error: #-1132')
			return -1132

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0, 0], dtype=np.float32).flatten()
		except:
			return 0

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		pass

class Bus: #errors -1150 to -1174
	CLID = 1300

	ID = 0
	TYPE = 1
	FUNCTIONAL_STATUS = 2 # switch
	NOMINAL_LL_VOLTAGE = 3
	A = 4
	MIN_PU_VOLTAGE = 5
	MAX_PU_VOLTAGE = 6
	OPERATIONAL_STATUS = 7 # switch
	A_PU_VOLTAGE = 8
	A_VOLTAGE = 9
	A_VOLTAGE_ANGLE = 10

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
			print('POWER ERROR in Bus0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		return 0

	def addToNodesDict(self, dictionary):
		try:
			temp_dict = {row[Bus.ID]:self for row in self.matrix}
			dictionary.update(temp_dict)
			return 0
		except:
			print('Error: #-1150')
			return -1150

	def voltagesToSets(self):
		return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			for row in self.matrix:
				idxcount = 0
				dssCkt.SetActiveBus( str(int(row[Bus.TYPE])) + '_' + str(int(row[Bus.ID])) )
				var_volt_mag = list(dssActvBus.VMagAngle)
				var_volt_pu = list(dssActvBus.puVmagAngle)

				row[Bus.A_PU_VOLTAGE] = 0.0

				row[Bus.A_VOLTAGE] = var_volt_mag[idxcount*2]
				row[Bus.A_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
				row[Bus.A_PU_VOLTAGE] = var_volt_pu[idxcount*2]
				idxcount += 1
			return 0
		except:
			print('Error: #-1152')
			return -1152

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1154')
			return -1154

	def convertToInputTensor(self):
		try:
			return [], [], np.empty([0, 0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			print('Error: #-1155')
			return -1155

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['a_PU_voltage']

			for row in self.matrix:
				for elem in output_col:
					output_list.append('Bus_' + str(int(row[Bus.ID])) + '_' + elem)

			outputdf = self.convertToDataFrame()
			outputdf = outputdf[output_col]
			return output_list, outputdf.values.flatten()
		except:
			print('Error: #-1156')
			return -1156

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		try:
			row = random.randrange(0, self.num_components)
			self.matrix[row, Bus.OPERATIONAL_STATUS] = 0.0
		except:
			print('Error: #-1157')
			return -1157

class VSource: #errors -1175 to -1199
	CLID = 1301

	ID = 0
	TYPE = 1
	FUNCTIONAL_STATUS = 2 # switch
	NOMINAL_LL_VOLTAGE = 3
	A = 4
	EXPECTED_GENERATION = 5
	R0 = 6
	R1 = 7
	VOLTAGE_ANGLE = 8
	X0 = 9
	X1 = 10
	MIN_PU_VOLTAGE = 11
	MAX_PU_VOLTAGE = 12
	MAX_AREA_CONTROL_ERROR = 13
	OPERATIONAL_STATUS = 14 # switch
	A_PU_VOLTAGE = 15
	A_VOLTAGE = 16
	A_VOLTAGE_ANGLE = 17
	A_CURRENT = 18
	A_CURRENT_ANGLE = 19
	REAL_POWER = 20
	REACTIVE_POWER = 21
	AREA_CONTROL_ERROR = 22

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
			print('POWER ERROR in VSource0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			for row in self.matrix:
				str_self_name = str(int(row[VSource.TYPE])) + '_' + str(int(row[VSource.ID]))
				num_phases = 0
				mvasc1 = 100
				mvasc3 = 300

				if row[VSource.A] == 1.0:
					num_phase += 1

				if debug == 1:
					print('New \'Circuit.{}\' Basekv=\'{:f}\' phases=\'{}\' pu=\'{:f}\' Angle=\'{:f}\' Mvasc1=\'{:f}\' Mvasc3=\'{:f}\' R0=\'{:f}\' R1=\'{:f}\' X0=\'{:f}\' X1=\'{:f}\'\n'.format(
					str_self_name, row[VSource.NOMINAL_LL_VOLTAGE], num_phases, row[VSource.A_PU_VOLTAGE], row[VSource.VOLTAGE_ANGLE],
					mvasc1, mvasc3, row[VSource.R0], row[VSource.R1],
					row[VSource.X0], row[VSource.X1]))

				dss.Command = 'New \'Circuit.{}\' Basekv=\'{:f}\' phases=\'{}\' pu=\'{:f}\' Angle=\'{:f}\' Mvasc1=\'{:f}\' Mvasc3=\'{:f}\' R0=\'{:f}\' R1=\'{:f}\' X0=\'{:f}\' X1=\'{:f}\''.format(
					str_self_name, row[VSource.NOMINAL_LL_VOLTAGE], num_phases, row[VSource.A_PU_VOLTAGE], row[VSource.VOLTAGE_ANGLE],
					mvasc1, mvasc3, row[VSource.R0], row[VSource.R1],
					row[VSource.X0], row[VSource.X1])
			return 0
		except:
			print('Error: #-1175')
			return -1175

	def addToNodesDict(self, dictionary):
		try:
			temp_dict = {row[VSource.ID]:self for row in self.matrix}
			dictionary.update(temp_dict)
			return 0
		except:
			print('Error: #-1177')
			return -1177

	def voltagesToSets(self):
		return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			for row in self.matrix: # ONLY RETRIEVES THE ONE VSOURCE SOURCEBUS
				idxcount = 0
				dssCkt.SetActiveBus('sourcebus')
				dssCkt.Vsources.Name = 'source'
				var_volt_mag = list(dssActvBus.VMagAngle)
				var_volt_pu = list(dssActvBus.puVmagAngle)
				var_curr = list(dssActvElem.CurrentsMagAng)
				var_pow = list(dssActvElem.Powers)
				num_phases = dssActvElem.NumPhases
				num_conds = dssActvElem.NumConductors

				row[VSource.A_PU_VOLTAGE : VSource.AREA_CONTROL_ERROR+1] = 0.0

				if row[VSource.A] == 1.0:
					row[VSource.A_VOLTAGE] = var_volt_mag[idxcount*2]
					row[VSource.A_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[VSource.A_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[VSource.A_CURRENT] = var_curr[idxcount*2]
					row[VSource.A_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[VSource.REAL_POWER] += var_pow[idxcount*2]
					row[VSource.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[VSource.N_CURRENT] = var_curr[idxcount*2]
					row[VSource.N_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
			return 0
		except:
			print('Error: #-1179')
			return -1179

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1181')
			return -1181

	def convertToInputTensor(self):
		try:
			return [], [], np.empty([0, 0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			print('Error: #-1182')
			return -1182

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['a_PU_voltage', 'a_current']

			for row in self.matrix:
				for elem in output_col:
					output_list.append('VSource_' + str(int(row[VSource.ID])) + '_' + elem)

			outputdf = self.convertToDataFrame()
			outputdf = outputdf[output_col]
			return output_list, outputdf.values.flatten()
		except:
			print('Error: #-1183')
			return -1183

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		pass

class Generator: #errors -1200 to -1224
	CLID = 1302

	ID = 0
	TYPE = 1
	FUNCTIONAL_STATUS = 2 # switch
	NOMINAL_LL_VOLTAGE = 3
	A = 4
	B = 5
	C = 6
	GENERATION = 7 # stochastic temporary
	MIN_POWER_FACTOR = 8
	MODEL = 9
	RAMP_RATE = 10
	RATED_CAPACITY = 11
	UNIT_COMMIT_COST = 12
	UNIT_MARGINAL_COST = 13
	WATER_CONSUMPTION = 14
	WATER_DERATING = 15
	WIRING = 16
	MIN_PU_VOLTAGE = 17
	MAX_PU_VOLTAGE = 18
	OPERATIONAL_STATUS = 19 # switch
	GENERATION_TARGET = 20 # stochastic
	POWER_FACTOR_CONTROL = 21 # stochastic
	A_PU_VOLTAGE = 22
	B_PU_VOLTAGE = 23
	C_PU_VOLTAGE = 24
	A_VOLTAGE = 25
	B_VOLTAGE = 26
	C_VOLTAGE = 27
	A_VOLTAGE_ANGLE = 28
	B_VOLTAGE_ANGLE = 29
	C_VOLTAGE_ANGLE = 30
	A_CURRENT = 31
	B_CURRENT = 32
	C_CURRENT = 33
	N_CURRENT = 34
	A_CURRENT_ANGLE = 35
	B_CURRENT_ANGLE = 36
	C_CURRENT_ANGLE = 37
	N_CURRENT_ANGLE = 38
	REAL_POWER = 39
	REACTIVE_POWER = 40
	UNIT_NET_COST = 41

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 1 # temporary
		self.num_stochastic = self.num_components * 2

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('POWER ERROR in Generator0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			for row in self.matrix:
				str_bus_conn = ''
				str_conn = 'wye'
				num_phases = 0
				num_kv = row[Generator.NOMINAL_LL_VOLTAGE]
				derating = 1.0

				if row[Generator.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'
					num_phases += 1
				if row[Generator.B] == 1.0:
					str_bus_conn = str_bus_conn + '.2'
					num_phases += 1
				if row[Generator.C] == 1.0:
					str_bus_conn = str_bus_conn + '.3'
					num_phases += 1

				if num_phases == 0:
					print('Error: #-1201')

				if row[Generator.WIRING] == 0.0:
					str_conn = 'delta'
				elif num_phases == 1:
					num_kv = num_kv / math.sqrt(3.0)

				if math.fabs(row[Generator.POWER_FACTOR_CONTROL]) < math.fabs(row[Generator.MIN_POWER_FACTOR]):
					print('Error: generator#')

				if row[Generator.GENERATION] < 0.0:
					row[Generator.GENERATION] = 0.0
				elif row[Generator.GENERATION] > row[Generator.RATED_CAPACITY]:
					row[Generator.GENERATION] = row[Generator.RATED_CAPACITY]

				str_self_name = str(int(row[Generator.TYPE])) + '_' + str(int(row[Generator.ID]))

				for interconn_row in interconn_dict['tankgenerator'].matrix:
					if interconn_row[interconn_dict['tankgenerator'].classValue('CHECK_TANK_LEVEL')] ==  1.0:
						if interconn_row[interconn_dict['tankgenerator'].classValue('GENERATOR_ID')] == row[Generator.ID]:
							for tank_row in interconn_dict['tank'].matrix:
								if tank_row[interconn_dict['tank'].classValue('ID')] == interconn_row[interconn_dict['tankgenerator'].classValue('TANK_ID')]:
									if tank_row[interconn_dict['tank'].classValue('HEAD')] < tank_row[interconn_dict['tank'].classValue('MIN_LEVEL')] + 0.25*(tank_row[interconn_dict['tank'].classValue('MAX_LEVEL')] - tank_row[interconn_dict['tank'].classValue('MIN_LEVEL')]):
										derating = 1.0 - row[Generator.WATER_DERATING]
#chose 25% of MAX - MIN

				if debug == 1:
					print('New \'Generator.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Pf=\'{:f}\' Model=\'{}\' Conn=\'{}\'\n'.format(
					str_self_name, str_self_name, str_bus_conn, num_phases,
					num_kv, row[Generator.GENERATION]*derating, row[Generator.POWER_FACTOR_CONTROL], int(row[Generator.MODEL]),
					str_conn))
					if row[Generator.FUNCTIONAL_STATUS]*row[Generator.OPERATIONAL_STATUS] == 0.0:
						print('Open \'Generator.{}\' Term=1\n'.format(str_self_name))
						print('Open \'Generator.{}\' Term=2\n'.format(str_self_name))

				dss.Command = 'New \'Generator.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Pf=\'{:f}\' Model=\'{}\' Conn=\'{}\''.format(
					str_self_name, str_self_name, str_bus_conn, num_phases,
					num_kv, row[Generator.GENERATION]*derating, row[Generator.POWER_FACTOR_CONTROL], int(row[Generator.MODEL]),
					str_conn)
				if row[Generator.FUNCTIONAL_STATUS]*row[Generator.OPERATIONAL_STATUS] == 0.0:
					dss.Command = 'Open \'Generator.{}\' Term=1'.format(str_self_name)
					dss.Command = 'Open \'Generator.{}\' Term=2'.format(str_self_name)
			return 0
		except:
			print('Error: #-1200')
			return -1200

	def addToNodesDict(self, dictionary):
		try:
			temp_dict = {row[Generator.ID]:self for row in self.matrix}
			dictionary.update(temp_dict)
			return 0
		except:
			print('Error: #-1202')
			return -1202

	def voltagesToSets(self):
		try:
			return set(self.matrix[:, Generator.NOMINAL_LL_VOLTAGE])
		except:
			print('Error: #-1204')
			return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			for row in self.matrix:
				idxcount = 0
				dssCkt.SetActiveBus(str(int(row[Generator.TYPE])) + '_' + str(int(row[Generator.ID])))
				dssCkt.Generators.Name = str(int(row[Generator.TYPE])) + '_' + str(int(row[Generator.ID]))
				var_volt_mag = list(dssActvBus.VMagAngle)
				var_volt_pu = list(dssActvBus.puVmagAngle)
				var_curr = list(dssActvElem.CurrentsMagAng)
				var_pow = list(dssActvElem.Powers)
				num_phases = dssActvElem.NumPhases
				num_conds = dssActvElem.NumConductors

				row[Generator.A_PU_VOLTAGE : Generator.UNIT_NET_COST+1] = 0.0

				if row[Generator.A] == 1.0:
					row[Generator.A_VOLTAGE] = var_volt_mag[idxcount*2]
					row[Generator.A_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[Generator.A_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[Generator.A_CURRENT] = var_curr[idxcount*2]
					row[Generator.A_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Generator.REAL_POWER] += var_pow[idxcount*2]
					row[Generator.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[Generator.B] == 1.0:
					row[Generator.B_VOLTAGE] = var_volt_mag[idxcount*2]
					row[Generator.B_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[Generator.B_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[Generator.B_CURRENT] = var_curr[idxcount*2]
					row[Generator.B_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Generator.REAL_POWER] += var_pow[idxcount*2]
					row[Generator.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[Generator.C] == 1.0:
					row[Generator.C_VOLTAGE] = var_volt_mag[idxcount*2]
					row[Generator.C_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[Generator.C_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[Generator.C_CURRENT] = var_curr[idxcount*2]
					row[Generator.C_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Generator.REAL_POWER] += var_pow[idxcount*2]
					row[Generator.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[Generator.N_CURRENT] = var_curr[idxcount*2]
					row[Generator.N_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
			return 0
		except:
			print('Error: #-1206')
			return -1206

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1208')
			return -1208

	def convertToInputTensor(self):
		try:
			input_list_continuous = []
			input_list_categorical = []
			input_col_continuous = ['generation', 'power_factor_control']
			input_col_categorical = ['operational_status']

			for row in self.matrix:
				for elem in input_col_continuous:
					input_list_continuous.append('Generator_' + str(int(row[Generator.ID])) + '_' + elem)
				for elem in input_col_categorical:
					input_list_categorical.append('Generator_' + str(int(row[Generator.ID])) + '_' + elem)

			inputdf = self.convertToDataFrame()
			inputdf_continuous = inputdf[input_col_continuous]
			inputdf_categorical = inputdf[input_col_categorical]
			return input_list_continuous, input_list_categorical, inputdf_continuous.values.flatten(), inputdf_categorical.values.flatten()
		except:
			print('Error: #-1209')
			return -1209

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['a_PU_voltage', 'b_PU_voltage', 'c_PU_voltage', 'a_current', 'b_current', 'c_current', 'n_current']
			
			for row in self.matrix:
				for elem in output_col:
					output_list.append('Generator_' + str(int(Generator.ID)) + '_' + elem)

			outputdf = self.convertToDataFrame()
			outputdf = outputdf[output_col]
			return output_list, outputdf.values.flatten()
		except:
			print('Error: #-1210')
			return -1210

	def randomStochasticity(self):
		try:
			row = random.randrange(0, self.num_components)
			if random.randrange(0, 2) == 0:
				max_generation = 600.0
				rval = random.normalvariate(0, 0.5*max_generation*0.04)
				self.matrix[row, Generator.GENERATION] += rval
				if self.matrix[row, Generator.GENERATION] > max_generation:
					self.matrix[row, Generator.GENERATION] = max_generation
				elif self.matrix[row, Generator.GENERATION] < 0.0:
					self.matrix[row, Generator.GENERATION] = 0.0
			else:
				rval = random.normalvariate(0, 0.5*(1.0-self.matrix[row, Generator.MIN_POWER_FACTOR])*0.1)
				self.matrix[row, Generator.POWER_FACTOR_CONTROL] += rval
				if self.matrix[row, Generator.POWER_FACTOR_CONTROL] > 1.0:
					self.matrix[row, Generator.POWER_FACTOR_CONTROL] = 1.0
				elif self.matrix[row, Generator.POWER_FACTOR_CONTROL] < self.matrix[row, Generator.MIN_POWER_FACTOR]:
					self.matrix[row, Generator.POWER_FACTOR_CONTROL] = self.matrix[row, Generator.MIN_POWER_FACTOR]
		except:
			print('Error: #1211')
			return -1211

	def randomSwitching(self):
		try:
			row = random.randrange(0, self.num_components)
			self.matrix[row, Generator.OPERATIONAL_STATUS] = 0.0
		except:
			print('Error: #1212')
			return -1212

class Load: #errors -1225 to -1249
	CLID = 1303

	ID = 0
	TYPE = 1
	FUNCTIONAL_STATUS = 2 # switch
	NOMINAL_LL_VOLTAGE = 3
	A = 4
	B = 5
	C = 6
	DEMAND_LIMIT = 7
	MODEL = 8
	POWER_FACTOR = 9 # stochastic ?
	WIRING = 10
	ZIP_PU_VOLTAGE_CUTOFF = 11
	ZIP_REAL_POWER = 12
	ZIP_REAL_CURRENT = 13
	ZIP_REAL_IMPEDANCE = 14
	ZIP_REACTIVE_POWER = 15
	ZIP_REACTIVE_CURRENT = 16
	ZIP_REACTIVE_IMPEDANCE = 17
	DEMAND = 18 # stochastic
	MIN_PU_VOLTAGE = 19
	MAX_PU_VOLTAGE = 20
	OPERATIONAL_STATUS = 21 # switch
	A_PU_VOLTAGE = 22
	B_PU_VOLTAGE = 23
	C_PU_VOLTAGE = 24
	A_VOLTAGE = 25
	B_VOLTAGE = 26
	C_VOLTAGE = 27
	A_VOLTAGE_ANGLE = 28
	B_VOLTAGE_ANGLE = 29
	C_VOLTAGE_ANGLE = 30
	A_CURRENT = 31
	B_CURRENT = 32
	C_CURRENT = 33
	N_CURRENT = 34
	A_CURRENT_ANGLE = 35
	B_CURRENT_ANGLE = 36
	C_CURRENT_ANGLE = 37
	N_CURRENT_ANGLE = 38
	REAL_POWER = 39
	REACTIVE_POWER = 40

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 1 # temporary
		self.num_stochastic = self.num_components * 1 # temporary ?

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('POWER ERROR in Load0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			for row in self.matrix:
				str_bus_conn = ''
				str_conn = 'wye'
				num_phases = 0
				num_kv = row[Load.NOMINAL_LL_VOLTAGE]
				interconn_demand = 0.0

				if row[Load.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'
					num_phases += 1
				if row[Load.B] == 1.0:
					str_bus_conn = str_bus_conn + '.2'
					num_phases += 1
				if row[Load.C] == 1.0:
					str_bus_conn = str_bus_conn + '.3'
					num_phases += 1

				if num_phases == 0:
					print('Error: #-1226')

				if row[Load.WIRING] == 0.0:
					str_conn = 'delta'
				elif num_phases == 1:
					num_kv = num_kv / math.sqrt(3.0)

				str_self_name = str(int(row[Load.TYPE])) + '_' + str(int(row[Load.ID])) + '_' + str(int(row[Load.A])) + '_' + str(int(row[Load.B])) + '_' + str(int(row[Load.C]))
				str_bus_name = str(Bus.CLID) + '_' + str(int(row[Load.ID]))

				for interconn_row in interconn_dict['pumpload'].matrix:
					if interconn_row[interconn_dict['pumpload'].classValue('LOAD_ID')] == row[Load.ID]:
						for pump_row in interconn_dict['pump'].matrix:
							if pump_row[interconn_dict['pump'].classValue('ID')] == interconn_row[interconn_dict['pumpload'].classValue('PUMP_ID')]:
								if pump_row[interconn_dict['pump'].classValue('FUNCTIONAL_STATUS')]*pump_row[interconn_dict['pump'].classValue('OPERATIONAL_STATUS')] != 0.0:
									interconn_demand += pump_row[interconn_dict['pump'].classValue('POWER')]

				if debug == 1:
					if row[Load.MODEL] == 8.0:
						print('New \'Load.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Pf=\'{:f}\' Model=\'{}\' ZIPV=[{:f} {:f} {:f} {:f} {:f} {:f} {:f}] Conn=\'{}\' Vminpu=\'{:f}\' Vmaxpu=\'{:f}\'\n'.format(
							str_self_name, str_bus_name, str_bus_conn, num_phases,
							num_kv, row[Load.DEMAND]+interconn_demand, row[Load.POWER_FACTOR], int(row[Load.MODEL]),
							row[Load.ZIP_REAL_POWER], row[Load.ZIP_REAL_CURRENT], row[Load.ZIP_REAL_IMPEDANCE], row[Load.ZIP_REACTIVE_POWER],
							row[Load.ZIP_REACTIVE_CURRENT], row[Load.ZIP_REACTIVE_IMPEDANCE], row[Load.ZIP_PU_VOLTAGE_CUTOFF], str_conn,
							row[Load.MIN_PU_VOLTAGE], row[Load.MAX_PU_VOLTAGE]))
					else:
						print('New \'Load.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Pf=\'{:f}\' Model=\'{}\' Conn=\'{}\' Vminpu=\'{:f}\' Vmaxpu=\'{:f}\'\n'.format(
							str_self_name, str_bus_name, str_bus_conn, num_phases,
							num_kv, row[Load.DEMAND]+interconn_demand, row[Load.POWER_FACTOR], int(row[Load.MODEL]),
							str_conn, row[Load.MIN_PU_VOLTAGE], row[Load.MAX_PU_VOLTAGE]))
					if row[Load.FUNCTIONAL_STATUS]*row[Load.OPERATIONAL_STATUS] == 0.0:
						print('Open \'Load.{}\' Term=1'.format(str_self_name))
						print('Open \'Load.{}\' Term=2'.format(str_self_name))

				if row[Load.MODEL] == 8.0:
					dss.Command = 'New \'Load.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Pf=\'{:f}\' Model=\'{}\' ZIPV=[{:f} {:f} {:f} {:f} {:f} {:f} {:f}] Conn=\'{}\' Vminpu=\'{:f}\' Vmaxpu=\'{:f}\''.format(
						str_self_name, str_bus_name, str_bus_conn, num_phases,
						num_kv, row[Load.DEMAND]+interconn_demand, row[Load.POWER_FACTOR], int(row[Load.MODEL]),
						row[Load.ZIP_REAL_POWER], row[Load.ZIP_REAL_CURRENT], row[Load.ZIP_REAL_IMPEDANCE], row[Load.ZIP_REACTIVE_POWER],
						row[Load.ZIP_REACTIVE_CURRENT], row[Load.ZIP_REACTIVE_IMPEDANCE], row[Load.ZIP_PU_VOLTAGE_CUTOFF], str_conn,
						row[Load.MIN_PU_VOLTAGE], row[Load.MAX_PU_VOLTAGE])
					if row[Load.ZIP_REAL_POWER] + row[Load.ZIP_REAL_CURRENT] + row[Load.ZIP_REAL_IMPEDANCE] != 1.0 or row[Load.ZIP_REACTIVE_POWER] + row[Load.ZIP_REACTIVE_CURRENT] + row[Load.ZIP_REACTIVE_IMPEDANCE] != 1.0:
						print('Error: #-1228')
				else:
					dss.Command = 'New \'Load.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Pf=\'{:f}\' Model=\'{}\' Conn=\'{}\' Vminpu=\'{:f}\' Vmaxpu=\'{:f}\''.format(
						str_self_name, str_bus_name, str_bus_conn, num_phases,
						num_kv, row[Load.DEMAND]+interconn_demand, row[Load.POWER_FACTOR], int(row[Load.MODEL]),
						str_conn, row[Load.MIN_PU_VOLTAGE], row[Load.MAX_PU_VOLTAGE])
				if row[Load.FUNCTIONAL_STATUS]*row[Load.OPERATIONAL_STATUS] == 0.0:
					dss.Command = 'Open \'Load.{}\' Term=1'.format(str_self_name)
					dss.Command = 'Open \'Load.{}\' Term=2'.format(str_self_name)
			return 0
		except:
			print('Error: #-1225')
			return -1225

	def addToNodesDict(self, dictionary):
		try:
			temp_dict = {row[Load.ID]:self for row in self.matrix}
			# NOT ADDED TO DICT IN LIEU OF BUS
			return 0
		except:
			print('Error: #-1227')
			return -1227

	def voltagesToSets(self):
		try:
			return set(self.matrix[:, Load.NOMINAL_LL_VOLTAGE])
		except:
			print('Error: #-1229')
			return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			for row in self.matrix:
				idxcount = 0
				dssCkt.SetActiveBus(str(Bus.CLID) + '_' + str(int(row[Load.ID])))
				dssCkt.Loads.Name = str(int(row[Load.TYPE])) + '_' + str(int(row[Load.ID])) + '_' + str(int(row[Load.A])) + '_' + str(int(row[Load.B])) + '_' + str(int(row[Load.C]))
				var_volt_mag = list(dssActvBus.VMagAngle)
				var_volt_pu = list(dssActvBus.puVmagAngle)
				var_curr = list(dssActvElem.CurrentsMagAng)
				var_pow = list(dssActvElem.Powers)
				num_phases = dssActvElem.NumPhases
				num_conds = dssActvElem.NumConductors

				row[Load.A_PU_VOLTAGE : Load.REACTIVE_POWER+1] = 0.0

				if row[Load.A] == 1.0:
					row[Load.A_VOLTAGE] = var_volt_mag[idxcount*2]
					row[Load.A_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[Load.A_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[Load.A_CURRENT] = var_curr[idxcount*2]
					row[Load.A_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Load.REAL_POWER] += var_pow[idxcount*2]
					row[Load.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[Load.B] == 1.0:
					row[Load.B_VOLTAGE] = var_volt_mag[idxcount*2]
					row[Load.B_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[Load.B_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[Load.B_CURRENT] = var_curr[idxcount*2]
					row[Load.B_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Load.REAL_POWER] += var_pow[idxcount*2]
					row[Load.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[Load.C] == 1.0:
					row[Load.C_VOLTAGE] = var_volt_mag[idxcount*2]
					row[Load.C_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[Load.C_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[Load.C_CURRENT] = var_curr[idxcount*2]
					row[Load.C_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Load.REAL_POWER] += var_pow[idxcount*2]
					row[Load.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[Load.N_CURRENT] = var_curr[idxcount*2]
					row[Load.N_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
			return 0
		except:
			print('Error: #-1231')
			return -1231

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1233')
			return -1233

	def convertToInputTensor(self):
		try:
			input_list_continuous = []
			input_list_categorical = []
			input_col_continuous = ['demand']
			input_col_categorical = ['operational_status']

			for row in self.matrix:
				for elem in input_col_continuous:
					input_list_continuous.append('Load_' + str(int(row[Load.ID])) + '_' + elem)
				for elem in input_col_categorical:
					input_list_categorical.append('Load_' + str(int(row[Load.ID])) + '_' + elem)

			inputdf = self.convertToDataFrame()
			inputdf_continuous = inputdf[input_col_continuous]
			inputdf_categorical = inputdf[input_col_categorical]
			return input_list_continuous, input_list_categorical, inputdf_continuous.values.flatten(), inputdf_categorical.values.flatten()
		except:
			print('Error: #-1234')
			return -1234

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['a_PU_voltage', 'b_PU_voltage', 'c_PU_voltage', 'a_current', 'b_current', 'c_current', 'n_current']
			
			for row in self.matrix:
				for elem in output_col:
					output_list.append('Load_' + str(int(row[Load.ID])) + '_' + elem)

			outputdf = self.convertToDataFrame()
			outputdf = outputdf[output_col]
			return output_list, outputdf.values.flatten()
		except:
			print('Error: #-1235')
			return -1235

	def randomStochasticity(self):
		try:
			row = random.randrange(0, self.num_components)
			rval = random.normalvariate(0, 0.5*self.matrix[row, Load.DEMAND_LIMIT]*0.06)
			self.matrix[row, Load.DEMAND] += rval
			if self.matrix[row, Load.DEMAND] > self.matrix[row, Load.DEMAND_LIMIT]:
				self.matrix[row, Load.DEMAND] = self.matrix[row, Load.DEMAND_LIMIT]
			elif self.matrix[row, Load.DEMAND] < 0.0:
				self.matrix[row, Load.DEMAND] = 0.0
		except:
			print('Error: #1236')
			return -1236

	def randomSwitching(self):
		try:
			row = random.randrange(0, self.num_components)
			self.matrix[row, Load.OPERATIONAL_STATUS] = 0.0
		except:
			print('Error: #1237')
			return -1237

class SolarPV: #errors -1250 to -1274
	CLID = 1304

	ID = 0
	TYPE = 1 
	FUNCTIONAL_STATUS = 2 # switch
	NOMINAL_LL_VOLTAGE = 3
	A = 4
	B = 5
	C = 6
	CUT_IN_PERCENT = 7
	CUT_OUT_PERCENT = 8
	MIN_POWER_FACTOR = 9
	MODEL = 10
	PVEFF_CURVE_ID = 11
	PVTEMP_CURVE_ID = 12
	RATED_INVERTER = 13
	RATED_CAPACITY = 14
	UNIT_COMMIT_COST = 15
	UNIT_MARGINAL_COST = 16
	WIRING = 17
	IRRADIANCE = 18 # stochastic
	MIN_PU_VOLTAGE = 19
	MAX_PU_VOLTAGE = 20
	OPERATIONAL_STATUS = 21 # switch
	POWER_FACTOR_CONTROL = 22 # stochastic
	A_PU_VOLTAGE = 23
	B_PU_VOLTAGE = 24
	C_PU_VOLTAGE = 25
	A_VOLTAGE = 26
	B_VOLTAGE = 27
	C_VOLTAGE = 28
	A_VOLTAGE_ANGLE = 29
	B_VOLTAGE_ANGLE = 30
	C_VOLTAGE_ANGLE = 31
	A_CURRENT = 32
	B_CURRENT = 33
	C_CURRENT = 34
	N_CURRENT = 35
	A_CURRENT_ANGLE = 36
	B_CURRENT_ANGLE = 37
	C_CURRENT_ANGLE = 38
	N_CURRENT_ANGLE = 39
	REAL_POWER = 40
	REACTIVE_POWER = 41
	UNIT_NET_COST = 42

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 1 # temporary
		self.num_stochastic = self.num_components * 2 # temperature?

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('POWER ERROR in SolarPV0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			for row in self.matrix:
				str_bus_conn = ''
				str_conn = 'wye'
				num_phases = 0
				num_kv = row[SolarPV.NOMINAL_LL_VOLTAGE]
				value_temperature = 35.0 # Celsius

				if row[SolarPV.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'
					num_phases += 1
				if row[SolarPV.B] == 1.0:
					str_bus_conn = str_bus_conn + '.2'
					num_phases += 1
				if row[SolarPV.C] == 1.0:
					str_bus_conn = str_bus_conn + '.3'
					num_phases += 1

				if num_phases == 0:
					print('Error: #-1251')

				if row[SolarPV.WIRING] == 0.0:
					str_conn = 'delta'
				elif num_phases == 1:
					num_kv = num_kv / math.sqrt(3.0)

				if math.fabs(row[SolarPV.POWER_FACTOR_CONTROL]) < math.fabs(row[SolarPV.MIN_POWER_FACTOR]):
					print('Error: SolarPV#')

				str_bus_name = str(Bus.CLID) + '_' + str(int(row[SolarPV.ID]))
				str_self_name = str(int(row[SolarPV.TYPE])) + '_' + str(int(row[SolarPV.ID])) # NOT BASED ON PHASES LIKE LOAD COMPONENTS

				if debug == 1:
					print('New \'PVSystem.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kva={:f} Pf=\'{:f}\' Model=\'{}\' Conn=\'{}\' Vminpu=\'{:f}\' Vmaxpu=\'{:f}\' %Cutin=\'{:f}\' %Cutout=\'{:f}\' Pmpp=\'{:f}\' Irradiance=\'{:f}\' EffCurve=\'{}_{}\' Temperature=\'{:f}\' P-TCurve=\'{}_{}\'\n'.format(
					str_self_name, str_bus_name, str_bus_conn, num_phases,
					num_kv, row[SolarPV.RATED_INVERTER], row[SolarPV.POWER_FACTOR_CONTROL], int(row[SolarPV.MODEL]),
					str_conn, row[SolarPV.MIN_PU_VOLTAGE], row[SolarPV.MAX_PU_VOLTAGE], row[SolarPV.CUT_IN_PERCENT],
					row[SolarPV.CUT_OUT_PERCENT], row[SolarPV.RATED_CAPACITY], row[SolarPV.IRRADIANCE], XYCurve.CLID,
					int(row[SolarPV.PVEFF_CURVE_ID]), value_temperature, XYCurve.CLID, int(row[SolarPV.PVTEMP_CURVE_ID])))
					if row[SolarPV.FUNCTIONAL_STATUS]*row[SolarPV.OPERATIONAL_STATUS] == 0.0:
						print('Open \'PVSystem.{}\' Term=1'.format(str_self_name))
						print('Open \'PVSystem.{}\' Term=2'.format(str_self_name))

				dss.Command = 'New \'PVSystem.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kva={:f} Pf=\'{:f}\' Model=\'{}\' Conn=\'{}\' Vminpu=\'{:f}\' Vmaxpu=\'{:f}\' %Cutin=\'{:f}\' %Cutout=\'{:f}\' Pmpp=\'{:f}\' Irradiance=\'{:f}\' EffCurve=\'{}_{}\' Temperature=\'{:f}\' P-TCurve=\'{}_{}\''.format(
					str_self_name, str_bus_name, str_bus_conn, num_phases,
					num_kv, row[SolarPV.RATED_INVERTER], row[SolarPV.POWER_FACTOR_CONTROL], int(row[SolarPV.MODEL]),
					str_conn, row[SolarPV.MIN_PU_VOLTAGE], row[SolarPV.MAX_PU_VOLTAGE], row[SolarPV.CUT_IN_PERCENT],
					row[SolarPV.CUT_OUT_PERCENT], row[SolarPV.RATED_CAPACITY], row[SolarPV.IRRADIANCE], XYCurve.CLID,
					int(row[SolarPV.PVEFF_CURVE_ID]), value_temperature, XYCurve.CLID, int(row[SolarPV.PVTEMP_CURVE_ID]))
				if row[SolarPV.FUNCTIONAL_STATUS]*row[SolarPV.OPERATIONAL_STATUS] == 0.0:
					dss.Command = 'Open \'PVSystem.{}\' Term=1'.format(str_self_name)
					dss.Command = 'Open \'PVSystem.{}\' Term=2'.format(str_self_name)
			return 0
		except:
			print('Error: #-1250')
			return -1250

	def addToNodesDict(self, dictionary):
		try:
			temp_dict = {row[SolarPV.ID]:self for row in self.matrix}
			# NOT ADDED TO DICT IN LIEU OF BUS
			return 0
		except:
			print('Error: #-1252')
			return -1252

	def voltagesToSets(self):
		try:
			return set(self.matrix[:, SolarPV.NOMINAL_LL_VOLTAGE])
		except:
			print('Error: #-1254')
			return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			for row in self.matrix:
				idxcount = 0
				dssCkt.SetActiveBus(str(Bus.CLID) + '_' + str(int(row[SolarPV.ID])))
				dssCkt.PVSystems.Name = str(int(row[SolarPV.TYPE])) + '_' + str(int(row[SolarPV.ID])) # NOT BASED ON PHASES LIKE LOAD COMPONENTS
				var_volt_mag = list(dssActvBus.VMagAngle)
				var_volt_pu = list(dssActvBus.puVmagAngle)
				var_curr = list(dssActvElem.CurrentsMagAng)
				var_pow = list(dssActvElem.Powers)
				num_phases = dssActvElem.NumPhases
				num_conds = dssActvElem.NumConductors

				row[SolarPV.A_PU_VOLTAGE : SolarPV.UNIT_NET_COST+1] = 0.0

				if row[SolarPV.A] == 1.0:
					row[SolarPV.A_VOLTAGE] = var_volt_mag[idxcount*2]
					row[SolarPV.A_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[SolarPV.A_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[SolarPV.A_CURRENT] = var_curr[idxcount*2]
					row[SolarPV.A_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[SolarPV.REAL_POWER] += var_pow[idxcount*2]
					row[SolarPV.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[SolarPV.B] == 1.0:
					row[SolarPV.B_VOLTAGE] = var_volt_mag[idxcount*2]
					row[SolarPV.B_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[SolarPV.B_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[SolarPV.B_CURRENT] = var_curr[idxcount*2]
					row[SolarPV.B_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[SolarPV.REAL_POWER] += var_pow[idxcount*2]
					row[SolarPV.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[SolarPV.C] == 1.0:
					row[SolarPV.C_VOLTAGE] = var_volt_mag[idxcount*2]
					row[SolarPV.C_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[SolarPV.C_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[SolarPV.C_CURRENT] = var_curr[idxcount*2]
					row[SolarPV.C_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[SolarPV.REAL_POWER] += var_pow[idxcount*2]
					row[SolarPV.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[SolarPV.N_CURRENT] = var_curr[idxcount*2]
					row[SolarPV.N_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
			return 0
		except:
			print('Error: #-1256')
			return -1256

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1258')
			return -1258

	def convertToInputTensor(self):
		try:
			input_list_continuous = []
			input_list_categorical = []
			input_col_continuous = ['irradiance', 'power_factor_control']
			input_col_categorical = ['operational_status']

			for row in self.matrix:
				for elem in input_col_continuous:
					input_list_continuous.append('SolarPV_' + str(int(row[SolarPV.ID])) + '_' + elem)
				for elem in input_col_categorical:
					input_list_categorical.append('SolarPV_' + str(int(row[SolarPV.ID])) + '_' + elem)

			inputdf = self.convertToDataFrame()
			inputdf_continuous = inputdf[input_col_continuous]
			inputdf_categorical = inputdf[input_col_categorical]
			return input_list_continuous, input_list_categorical, inputdf_continuous.values.flatten(), inputdf_categorical.values.flatten()
		except:
			print('Error: #-1259')
			return -1259

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['a_PU_voltage', 'b_PU_voltage', 'c_PU_voltage', 'a_current', 'b_current', 'c_current', 'n_current']
			
			for row in self.matrix:
				for elem in output_col:
					output_list.append('SolarPV_' + str(int(row[SolarPV.ID])) + '_' + elem)

			outputdf = self.convertToDataFrame()
			outputdf = outputdf[output_col]
			return output_list, outputdf.values.flatten()
		except:
			print('Error: #-1260')
			return -1260

	def randomStochasticity(self):
		try:
			row = random.randrange(0, self.num_components)
			if random.randrange(0, 2) == 0:
				max_irradiance = 1050.0
				rval = random.normalvariate(0, 0.5*max_irradiance*0.07)
				self.matrix[row, SolarPV.IRRADIANCE] += rval
				if self.matrix[row, SolarPV.IRRADIANCE] > max_irradiance:
					self.matrix[row, SolarPV.IRRADIANCE] = max_irradiance
				elif self.matrix[row, SolarPV.IRRADIANCE] < 0.0:
					self.matrix[row, SolarPV.IRRADIANCE] = 0.0
			else:
				rval = random.normalvariate(0, 0.5*(1.0-self.matrix[row, SolarPV.MIN_POWER_FACTOR])*0.1)
				self.matrix[row, SolarPV.POWER_FACTOR_CONTROL] += rval
				if self.matrix[row, SolarPV.POWER_FACTOR_CONTROL] > 1.0:
					self.matrix[row, SolarPV.POWER_FACTOR_CONTROL] = 1.0
				elif self.matrix[row, SolarPV.POWER_FACTOR_CONTROL] < self.matrix[row, SolarPV.MIN_POWER_FACTOR]:
					self.matrix[row, SolarPV.POWER_FACTOR_CONTROL] = self.matrix[row, SolarPV.MIN_POWER_FACTOR]
		except:
			print('Error: #1261')
			return -1261

	def randomSwitching(self):
		try:
			row = random.randrange(0, self.num_components)
			self.matrix[row, SolarPV.OPERATIONAL_STATUS] = 0.0
		except:
			print('Error: #1262')
			return -1262

class WindTurbine: #errors -1275 to -1299
	CLID = 1305

	ID = 0
	TYPE = 1
	FUNCTIONAL_STATUS = 2 # switch
	NOMINAL_LL_VOLTAGE = 3
	A = 4
	B = 5
	C = 6
	CUT_IN_SPEED = 7
	CUT_OUT_SPEED = 8
	MODEL = 9
	POWER_FACTOR = 10
	RATED_CAPACITY = 11
	RATED_SPEED = 12
	UNIT_COMMIT_COST = 13
	UNIT_MARGINAL_COST = 14
	WIND_CURVE_ID = 15
	WIRING = 16
	WIND_SPEED = 17 # stochastic
	MIN_PU_VOLTAGE = 18
	MAX_PU_VOLTAGE = 19
	OPERATIONAL_STATUS = 20 # switch
	A_PU_VOLTAGE = 21
	B_PU_VOLTAGE = 22
	C_PU_VOLTAGE = 23
	A_VOLTAGE = 24
	B_VOLTAGE = 25
	C_VOLTAGE = 26
	A_VOLTAGE_ANGLE = 27
	B_VOLTAGE_ANGLE = 28
	C_VOLTAGE_ANGLE = 29
	A_CURRENT = 30
	B_CURRENT = 31
	C_CURRENT = 32
	N_CURRENT = 33
	A_CURRENT_ANGLE = 34
	B_CURRENT_ANGLE = 35
	C_CURRENT_ANGLE = 36
	N_CURRENT_ANGLE = 37
	REAL_POWER = 38
	REACTIVE_POWER = 39
	UNIT_NET_COST = 40

	def __init__(self, dframe, xy_object):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 1 # temporary
		self.num_stochastic = self.num_components * 1
		self.wind_object = xy_object

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('POWER ERROR in WindTurbine0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			for row in self.matrix:
				str_bus_conn = ''
				str_conn = 'wye'
				num_phases = 0
				num_kv = row[WindTurbine.NOMINAL_LL_VOLTAGE]

				if row[WindTurbine.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'
					num_phases += 1
				if row[WindTurbine.B] == 1.0:
					str_bus_conn = str_bus_conn + '.2'
					num_phases += 1
				if row[WindTurbine.C] == 1.0:
					str_bus_conn = str_bus_conn + '.3'
					num_phases += 1

				if num_phases == 0:
					print('Error: #-1274')

				if row[WindTurbine.WIRING] == 0.0:
					str_conn = 'delta'
				elif num_phases == 1:
					num_kv = num_kv / math.sqrt(3.0)

				wind_fraction = (row[WindTurbine.WIND_SPEED]-row[WindTurbine.CUT_IN_SPEED]) / (row[WindTurbine.RATED_SPEED]-row[WindTurbine.CUT_IN_SPEED])
				gen_fraction = self.wind_object.returnWindGenFraction(row[WindTurbine.WIND_CURVE_ID], wind_fraction)
				if row[WindTurbine.WIND_SPEED] > row[WindTurbine.CUT_OUT_SPEED]:
					gen_fraction = 0.0

				str_self_name = str(int(row[WindTurbine.TYPE])) + '_' + str(int(row[WindTurbine.ID]))

				if debug == 1:
					print('New \'Generator.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Pf=\'{:f}\' Model=\'{}\' Conn=\'{}\'\n'.format(
					str_self_name, str_self_name, str_bus_conn, num_phases,
					num_kv, gen_fraction*row[WindTurbine.RATED_CAPACITY], row[WindTurbine.POWER_FACTOR], int(row[WindTurbine.MODEL]),
					str_conn))

				dss.Command = 'New \'Generator.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Pf=\'{:f}\' Model=\'{}\' Conn=\'{}\''.format(
					str_self_name, str_self_name, str_bus_conn, num_phases,
					num_kv, gen_fraction*row[WindTurbine.RATED_CAPACITY], row[WindTurbine.POWER_FACTOR], int(row[WindTurbine.MODEL]),
					str_conn)
			return 0
		except:
			print('Error: #-1275')
			return -1275

	def addToNodesDict(self, dictionary):
		try:
			temp_dict = {row[WindTurbine.ID]:self for row in self.matrix}
			dictionary.update(temp_dict)
			return 0
		except:
			print('Error: #-1277')
			return -1277

	def voltagesToSets(self):
		try:
			return set(self.matrix[:, WindTurbine.NOMINAL_LL_VOLTAGE])
		except:
			print('Error: #-1279')
			return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			for row in self.matrix:
				idxcount = 0
				dssCkt.SetActiveBus(str(int(row[WindTurbine.TYPE])) + '_' + str(int(row[WindTurbine.ID])))
				dssCkt.Generators.Name = str(int(row[WindTurbine.TYPE])) + '_' + str(int(row[WindTurbine.ID]))
				var_volt_mag = list(dssActvBus.VMagAngle)
				var_volt_pu = list(dssActvBus.puVmagAngle)
				var_curr = list(dssActvElem.CurrentsMagAng)
				var_pow = list(dssActvElem.Powers)
				num_phases = dssActvElem.NumPhases
				num_conds = dssActvElem.NumConductors

				row[WindTurbine.A_PU_VOLTAGE : WindTurbine.UNIT_NET_COST+1] = 0.0

				if row[WindTurbine.A] == 1.0:
					row[WindTurbine.A_VOLTAGE] = var_volt_mag[idxcount*2]
					row[WindTurbine.A_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[WindTurbine.A_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[WindTurbine.A_CURRENT] = var_curr[idxcount*2]
					row[WindTurbine.A_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[WindTurbine.REAL_POWER] += var_pow[idxcount*2]
					row[WindTurbine.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[WindTurbine.B] == 1.0:
					row[WindTurbine.B_VOLTAGE] = var_volt_mag[idxcount*2]
					row[WindTurbine.B_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[WindTurbine.B_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[WindTurbine.B_CURRENT] = var_curr[idxcount*2]
					row[WindTurbine.B_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[WindTurbine.REAL_POWER] += var_pow[idxcount*2]
					row[WindTurbine.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[WindTurbine.C] == 1.0:
					row[WindTurbine.C_VOLTAGE] = var_volt_mag[idxcount*2]
					row[WindTurbine.C_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[WindTurbine.C_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[WindTurbine.C_CURRENT] = var_curr[idxcount*2]
					row[WindTurbine.C_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[WindTurbine.REAL_POWER] += var_pow[idxcount*2]
					row[WindTurbine.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[WindTurbine.N_CURRENT] = var_curr[idxcount*2]
					row[WindTurbine.N_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
			return 0
		except:
			print('Error: #-1281')
			return -1281

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1283')
			return -1283

	def convertToInputTensor(self):
		try:
			return [], [], np.empty([0, 0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			pass

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0, 0], dtype=np.float32).flatten()
		except:
			pass

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		pass

class DirectConnection: #errors -1400 to -1424
	CLID = 1400

	ID = 0
	TYPE = 1
	TERMINAL_1_ID = 2
	TERMINAL_2_ID = 3
	FUNCTIONAL_STATUS = 4 # switch
	A = 5
	B = 6
	C = 7
	ANGLE_DELTA_LIMIT = 8
	OPERATIONAL_STATUS = 9 # switch
	A_1_CURRENT = 10
	B_1_CURRENT = 11
	C_1_CURRENT = 12
	N_1_CURRENT = 13
	A_1_CURRENT_ANGLE = 14
	B_1_CURRENT_ANGLE = 15
	C_1_CURRENT_ANGLE = 16
	N_1_CURRENT_ANGLE = 17
	A_2_CURRENT = 18
	B_2_CURRENT = 19
	C_2_CURRENT = 20
	N_2_CURRENT = 21
	A_2_CURRENT_ANGLE = 22
	B_2_CURRENT_ANGLE = 23
	C_2_CURRENT_ANGLE = 24
	N_2_CURRENT_ANGLE = 25
	REAL_POWER_1 = 26
	REACTIVE_POWER_1 = 27
	REAL_POWER_2 = 28
	REACTIVE_POWER_2 = 29
	REAL_POWER_LOSSES = 30
	REACTIVE_POWER_LOSSES = 31
	ANGLE_DELTA = 32
	UNITS = 'ft'

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
			print('POWER ERROR in DirectConnection0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			for row in self.matrix:
				terminal_1_type = type(dictionary[row[DirectConnection.TERMINAL_1_ID]]).CLID
				terminal_2_type = type(dictionary[row[DirectConnection.TERMINAL_2_ID]]).CLID
				str_bus_conn = ''
				num_phases = int(row[DirectConnection.A] + row[DirectConnection.B] + row[DirectConnection.C])

				if row[DirectConnection.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'
				if row[DirectConnection.B] == 1.0:
					str_bus_conn = str_bus_conn + '.2'
				if row[DirectConnection.C] == 1.0:
					str_bus_conn = str_bus_conn + '.3'

				if str_bus_conn == '':
					print('Error: #-1401')

				str_self_name = str(int(row[DirectConnection.TYPE])) + '_' + str(int(row[DirectConnection.ID]))
				str_term1_name = str(terminal_1_type) + '_' + str(int(row[DirectConnection.TERMINAL_1_ID]))
				str_term2_name = str(terminal_2_type) + '_' + str(int(row[DirectConnection.TERMINAL_2_ID]))
				if terminal_1_type == VSource.CLID:
					str_term1_name = 'sourcebus'
				elif terminal_2_type == VSource.CLID:
					str_term2_name = 'sourcebus'

				if debug == 1:
					print('New \'Line.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' Phases=\'{}\' R0=\'{:f}\' R1=\'{:f}\' X0=\'{:f}\' X1=\'{:f}\' Length=\'{:f}\' Units=\'{}\' Normamps=\'{:f}\' Emergamps=\'{:f}\'\n'.format(
					str_self_name, str_term1_name, str_bus_conn, str_term2_name,
					str_bus_conn, num_phases, 0.00001, 0.00001,
					0.0001, 0.0001, 0.1, DirectConnection.UNITS,
					99999, 99999))

				dss.Command = 'New \'Line.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' Phases=\'{}\' R0=\'{:f}\' R1=\'{:f}\' X0=\'{:f}\' X1=\'{:f}\' Length=\'{:f}\' Units=\'{}\' Normamps=\'{:f}\' Emergamps=\'{:f}\''.format(
					str_self_name, str_term1_name, str_bus_conn, str_term2_name,
					str_bus_conn, num_phases, 0.00001, 0.00001,
					0.0001, 0.0001, 0.1, DirectConnection.UNITS,
					99999, 99999)
			return 0
		except:
			print('Error: #-1400')
			return -1400

	def addToNodesDict(self, dictionary):
		try:
			return 0
		except:
			print('Error: #-1402')
			return -1402

	def voltagesToSets(self):
		return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			for row in self.matrix:
				idxcount = 0
				dssCkt.Lines.Name = str(int(row[DirectConnection.TYPE])) + '_' + str(int(row[DirectConnection.ID]))
				var_bus = list(dssActvElem.BusNames)
				var_curr = list(dssActvElem.CurrentsMagAng)
				var_pow = list(dssActvElem.Powers)
				norm_amps = dssActvElem.NormalAmps
				num_phases = dssActvElem.NumPhases
				num_conds = dssActvElem.NumConductors

				row[DirectConnection.A_1_CURRENT : DirectConnection.ANGLE_DELTA+1] = 0.0

				if row[DirectConnection.A] == 1.0:
					row[DirectConnection.A_1_CURRENT] = var_curr[idxcount*2]
					row[DirectConnection.A_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[DirectConnection.REAL_POWER_1] += var_pow[idxcount*2]
					row[DirectConnection.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[DirectConnection.B] == 1.0:
					row[DirectConnection.B_1_CURRENT] = var_curr[idxcount*2]
					row[DirectConnection.B_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[DirectConnection.REAL_POWER_1] += var_pow[idxcount*2]
					row[DirectConnection.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[DirectConnection.C] == 1.0:
					row[DirectConnection.C_1_CURRENT] = var_curr[idxcount*2]
					row[DirectConnection.C_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[DirectConnection.REAL_POWER_1] += var_pow[idxcount*2]
					row[DirectConnection.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[DirectConnection.N_1_CURRENT] = var_curr[idxcount*2]
					row[DirectConnection.N_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
				if row[DirectConnection.A] == 1.0:
					row[DirectConnection.A_2_CURRENT] = var_curr[idxcount*2]
					row[DirectConnection.A_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[DirectConnection.REAL_POWER_2] += var_pow[idxcount*2]
					row[DirectConnection.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[DirectConnection.B] == 1.0:
					row[DirectConnection.B_2_CURRENT] = var_curr[idxcount*2]
					row[DirectConnection.B_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[DirectConnection.REAL_POWER_2] += var_pow[idxcount*2]
					row[DirectConnection.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[DirectConnection.C] == 1.0:
					row[DirectConnection.C_2_CURRENT] = var_curr[idxcount*2]
					row[DirectConnection.C_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[DirectConnection.REAL_POWER_2] += var_pow[idxcount*2]
					row[DirectConnection.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[DirectConnection.N_2_CURRENT] = var_curr[idxcount*2]
					row[DirectConnection.N_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]

				row[DirectConnection.REAL_POWER_LOSSES] = math.fabs(row[DirectConnection.REAL_POWER_1] + row[DirectConnection.REAL_POWER_2])
				row[DirectConnection.REACTIVE_POWER_LOSSES] = math.fabs(row[DirectConnection.REACTIVE_POWER_1] + row[DirectConnection.REACTIVE_POWER_2])
			return 0
		except:
			print('Error: #-1404')
			return -1404

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1406')
			return -1406

	def convertToInputTensor(self):
		try:
			return [], [], np.empty([0, 0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			pass

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0, 0], dtype=np.float32).flatten()
		except:
			pass

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		pass

class Cable: #errors -1425 to -1449
	CLID = 1401

	ID = 0
	TYPE = 1
	TERMINAL_1_ID = 2
	TERMINAL_2_ID = 3
	FUNCTIONAL_STATUS_A = 4 # switch
	FUNCTIONAL_STATUS_B = 5 # switch
	FUNCTIONAL_STATUS_C = 6 # switch
	A = 7
	B = 8
	C = 9
	LENGTH = 10
	LINECODE_ID = 11
	ANGLE_DELTA_LIMIT = 12
	OPERATIONAL_STATUS_A = 13 # switch
	OPERATIONAL_STATUS_B = 14 # switch
	OPERATIONAL_STATUS_C = 15 # switch
	A_1_CURRENT = 16
	B_1_CURRENT = 17
	C_1_CURRENT = 18
	N_1_CURRENT = 19
	A_1_CURRENT_ANGLE = 20
	B_1_CURRENT_ANGLE = 21
	C_1_CURRENT_ANGLE = 22
	N_1_CURRENT_ANGLE = 23
	A_2_CURRENT = 24
	B_2_CURRENT = 25
	C_2_CURRENT = 26
	N_2_CURRENT = 27
	A_2_CURRENT_ANGLE = 28
	B_2_CURRENT_ANGLE = 29
	C_2_CURRENT_ANGLE = 30
	N_2_CURRENT_ANGLE = 31
	A_PU_CAPACITY = 32
	B_PU_CAPACITY = 33
	C_PU_CAPACITY = 34
	REAL_POWER_1 = 36
	REACTIVE_POWER_1 = 36
	REAL_POWER_2 = 37
	REACTIVE_POWER_2 = 37
	REAL_POWER_LOSSES = 39
	REACTIVE_POWER_LOSSES = 40
	ANGLE_DELTA = 41
	UNITS = 'ft'

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = int(self.matrix[:, Cable.A:Cable.C+1].sum()) * 1 # temporary
		self.num_stochastic = self.num_components * 0
		self.switch_chance = (0.0, 0.0)
		self.stochastic_chance = (0.0, 0.0)

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('POWER ERROR in Cable0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			for row in self.matrix:
				terminal_1_type = type(dictionary[row[Cable.TERMINAL_1_ID]]).CLID
				terminal_2_type = type(dictionary[row[Cable.TERMINAL_2_ID]]).CLID
				str_bus_conn = ''

				if row[Cable.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'
				if row[Cable.B] == 1.0:
					str_bus_conn = str_bus_conn + '.2'
				if row[Cable.C] == 1.0:
					str_bus_conn = str_bus_conn + '.3'

				#the correct thing to do would check this sum with the number of phases for the linecode
				if str_bus_conn == '':
					print('Error: #-1426')

				str_self_name = str(int(row[Cable.TYPE])) + '_' + str(int(row[Cable.ID]))
				str_term1_name = str(terminal_1_type) + '_' + str(int(row[Cable.TERMINAL_1_ID]))
				str_term2_name = str(terminal_2_type) + '_' + str(int(row[Cable.TERMINAL_2_ID]))
				str_linec_name = str(LineCode.CLID) + '_' + str(int(row[Cable.LINECODE_ID]))
				if terminal_1_type == VSource.CLID:
					str_term1_name = 'sourcebus'
				elif terminal_2_type == VSource.CLID:
					str_term2_name = 'sourcebus'


				if debug == 1:
					print('New \'Line.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' LineCode=\'{}\' Length=\'{:f}\' Units=\'{}\'\n'.format(
					str_self_name, str_term1_name, str_bus_conn, str_term2_name,
					str_bus_conn, str_linec_name, row[Cable.LENGTH], Cable.UNITS))
					if row[Cable.A] == 1.0 and row[Cable.FUNCTIONAL_STATUS_A]*row[Cable.OPERATIONAL_STATUS_A] == 0.0:
						print('Open \'Line.{}\' Term=1 1'.format(str_self_name))
						print('Open \'Line.{}\' Term=2 1'.format(str_self_name))
					if row[Cable.B] == 1.0 and row[Cable.FUNCTIONAL_STATUS_B]*row[Cable.OPERATIONAL_STATUS_B] == 0.0:
						print('Open \'Line.{}\' Term=1 2'.format(str_self_name))
						print('Open \'Line.{}\' Term=2 2'.format(str_self_name))
					if row[Cable.C] == 1.0 and row[Cable.FUNCTIONAL_STATUS_C]*row[Cable.OPERATIONAL_STATUS_C] == 0.0:
						print('Open \'Line.{}\' Term=1 3'.format(str_self_name))
						print('Open \'Line.{}\' Term=2 3'.format(str_self_name))

				dss.Command = 'New \'Line.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' LineCode=\'{}\' Length=\'{:f}\' Units=\'{}\''.format(
					str_self_name, str_term1_name, str_bus_conn, str_term2_name,
					str_bus_conn, str_linec_name, row[Cable.LENGTH], Cable.UNITS)
				if row[Cable.A] == 1.0 and row[Cable.FUNCTIONAL_STATUS_A]*row[Cable.OPERATIONAL_STATUS_A] == 0.0:
					dss.Command = 'Open \'Line.{}\' Term=1 1'.format(str_self_name)
					dss.Command = 'Open \'Line.{}\' Term=2 1'.format(str_self_name)
				if row[Cable.B] == 1.0 and row[Cable.FUNCTIONAL_STATUS_B]*row[Cable.OPERATIONAL_STATUS_B] == 0.0:
					dss.Command = 'Open \'Line.{}\' Term=1 2'.format(str_self_name)
					dss.Command = 'Open \'Line.{}\' Term=2 2'.format(str_self_name)
				if row[Cable.C] == 1.0 and row[Cable.FUNCTIONAL_STATUS_C]*row[Cable.OPERATIONAL_STATUS_C] == 0.0:
					dss.Command = 'Open \'Line.{}\' Term=1 3'.format(str_self_name)
					dss.Command = 'Open \'Line.{}\' Term=2 3'.format(str_self_name)
			return 0
		except:
			print('Error: #-1425')
			return -1425

	def addToNodesDict(self, dictionary):
		try:
			return 0
		except:
			print('Error: #-1427')
			return -1427

	def voltagesToSets(self):
		return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			for row in self.matrix:
				idxcount = 0
				dssCkt.Lines.Name = str(int(row[Cable.TYPE])) + '_' + str(int(row[Cable.ID]))
				var_bus = list(dssActvElem.BusNames)
				var_curr = list(dssActvElem.CurrentsMagAng)
				var_pow = list(dssActvElem.Powers)
				norm_amps_inv = 1.0 / dssActvElem.NormalAmps
				num_phases = dssActvElem.NumPhases
				num_conds = dssActvElem.NumConductors

				row[Cable.A_1_CURRENT : Cable.ANGLE_DELTA+1] = 0.0

				if row[Cable.A] == 1.0:
					row[Cable.A_1_CURRENT] = var_curr[idxcount*2]
					row[Cable.A_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Cable.REAL_POWER_1] += var_pow[idxcount*2]
					row[Cable.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[Cable.B] == 1.0:
					row[Cable.B_1_CURRENT] = var_curr[idxcount*2]
					row[Cable.B_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Cable.REAL_POWER_1] += var_pow[idxcount*2]
					row[Cable.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[Cable.C] == 1.0:
					row[Cable.C_1_CURRENT] = var_curr[idxcount*2]
					row[Cable.C_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Cable.REAL_POWER_1] += var_pow[idxcount*2]
					row[Cable.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[Cable.N_1_CURRENT] = var_curr[idxcount*2]
					row[Cable.N_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
				if row[Cable.A] == 1.0:
					row[Cable.A_2_CURRENT] = var_curr[idxcount*2]
					row[Cable.A_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Cable.REAL_POWER_2] += var_pow[idxcount*2]
					row[Cable.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[Cable.B] == 1.0:
					row[Cable.B_2_CURRENT] = var_curr[idxcount*2]
					row[Cable.B_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Cable.REAL_POWER_2] += var_pow[idxcount*2]
					row[Cable.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[Cable.C] == 1.0:
					row[Cable.C_2_CURRENT] = var_curr[idxcount*2]
					row[Cable.C_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Cable.REAL_POWER_2] += var_pow[idxcount*2]
					row[Cable.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[Cable.N_2_CURRENT] = var_curr[idxcount*2]
					row[Cable.N_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]

				row[Cable.REAL_POWER_LOSSES] = math.fabs(row[Cable.REAL_POWER_1] + row[Cable.REAL_POWER_2])
				row[Cable.REACTIVE_POWER_LOSSES] = math.fabs(row[Cable.REACTIVE_POWER_1] + row[Cable.REACTIVE_POWER_2])

				row[Cable.A_PU_CAPACITY] = 0.5 * (row[Cable.A_1_CURRENT] + row[Cable.A_2_CURRENT]) * norm_amps_inv
				row[Cable.B_PU_CAPACITY] = 0.5 * (row[Cable.B_1_CURRENT] + row[Cable.B_2_CURRENT]) * norm_amps_inv
				row[Cable.C_PU_CAPACITY] = 0.5 * (row[Cable.C_1_CURRENT] + row[Cable.C_2_CURRENT]) * norm_amps_inv
			return 0
		except:
			print('Error: #-1429')
			return -1429

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1431')
			return -1431

	def convertToInputTensor(self):
		try:
			input_list_continuous = []
			input_list_categorical = []
			input_col_categorical = ['operational_status_a', 'operational_status_b', 'operational_status_c']

			for row in self.matrix:
				for elem in input_col_categorical:
					input_list_categorical.append('Cable_' + str(int(row[Cable.ID])) + '_' + elem)

			inputdf = self.convertToDataFrame()
			inputdf_categorical = inputdf[input_col_categorical]
			return input_list_continuous, input_list_categorical, np.empty([0,0], dtype=np.float32).flatten(), inputdf_categorical.values.flatten()
		except:
			print('Error: #-1432')
			return -1432

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['a_PU_capacity', 'b_PU_capacity', 'c_PU_capacity']

			for row in self.matrix:
				for elem in output_col:
					output_list.append('Cable_' + str(int(row[Cable.ID])) + '_' + elem)

			outputdf = self.convertToDataFrame()
			outputdf = outputdf[output_col]
			return output_list, outputdf.values.flatten()
		except:
			print('Error: #-1433')
			return -1433

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		try:
			flag = 0
			ridx = random.randrange(1, int(self.matrix[:, Cable.OPERATIONAL_STATUS_A:Cable.OPERATIONAL_STATUS_C+1].sum())+1)
			tempval = 0
			for row in self.matrix:
				tempval += int(row[Cable.OPERATIONAL_STATUS_A:Cable.OPERATIONAL_STATUS_C+1].sum())
				if ridx <= tempval:
					while True:
						if row[Cable.OPERATIONAL_STATUS_A] != 1.0:
							if row[Cable.OPERATIONAL_STATUS_B] != 1.0:
								if row[Cable.OPERATIONAL_STATUS_C] != 1.0:
									print('Error: #-1434')
									break
						rphase = random.randrange(0, 3)
						if row[Cable.OPERATIONAL_STATUS_A + rphase] == 1.0:
							row[Cable.OPERATIONAL_STATUS_A + rphase] = 0.0
							flag = 1
							break
					break
			if flag == 0:
				print('Error: #-1435')
		except:
			print('Error: #-1436')
			return -1435

class OverheadLine: #errors -1450 to -1474
	CLID = 1402

	ID = 0
	TYPE = 1
	TERMINAL_1_ID = 2
	TERMINAL_2_ID = 3
	FUNCTIONAL_STATUS_A = 4 # switch
	FUNCTIONAL_STATUS_B = 5 # switch
	FUNCTIONAL_STATUS_C = 6 # switch
	A = 7
	B = 8
	C = 9
	LENGTH = 10
	NEUTRAL_WIREDATA_ID = 11
	PHASE_WIREDATA_ID = 12
	SOIL_RESISTIVITY = 13
	X_A_COORDINATE = 14
	X_B_COORDINATE = 15
	X_C_COORDINATE = 16
	X_N_COORDINATE = 17
	H_A_COORDINATE = 18
	H_B_COORDINATE = 19
	H_C_COORDINATE = 20
	H_N_COORDINATE = 21
	ANGLE_DELTA_LIMIT = 22
	OPERATIONAL_STATUS_A = 23 # switch
	OPERATIONAL_STATUS_B = 24 # switch
	OPERATIONAL_STATUS_C = 25 # switch
	A_1_CURRENT = 26
	B_1_CURRENT = 27
	C_1_CURRENT = 28
	N_1_CURRENT = 29
	A_1_CURRENT_ANGLE = 30
	B_1_CURRENT_ANGLE = 31
	C_1_CURRENT_ANGLE = 32
	N_1_CURRENT_ANGLE = 33
	A_2_CURRENT = 34
	B_2_CURRENT = 35
	C_2_CURRENT = 36
	N_2_CURRENT = 37
	A_2_CURRENT_ANGLE = 38
	B_2_CURRENT_ANGLE = 39
	C_2_CURRENT_ANGLE = 40
	N_2_CURRENT_ANGLE = 41
	A_PU_CAPACITY = 42
	B_PU_CAPACITY = 43
	C_PU_CAPACITY = 44
	REAL_POWER_1 = 45
	REACTIVE_POWER_1 = 46
	REAL_POWER_2 = 47
	REACTIVE_POWER_2 = 48
	REAL_POWER_LOSSES = 49
	REACTIVE_POWER_LOSSES = 50
	ANGLE_DELTA = 51
	UNITS = 'ft'

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = int(self.matrix[:, OverheadLine.A:OverheadLine.C+1].sum()) * 1 # temporary
		self.num_stochastic = self.num_components * 0
		self.switch_chance = (0.0, 0.0)
		self.stochastic_chance = (0.0, 0.0)

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('POWER ERROR in OverheadLine0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			for row in self.matrix:
				terminal_1_type = type(dictionary[row[OverheadLine.TERMINAL_1_ID]]).CLID
				terminal_2_type = type(dictionary[row[OverheadLine.TERMINAL_2_ID]]).CLID
				str_bus_conn = ''
				num_phases = 0
				num_neutral = 1

				if row[OverheadLine.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'
					num_phases += 1
				if row[OverheadLine.B] == 1.0:
					str_bus_conn = str_bus_conn + '.2'
					num_phases += 1
				if row[OverheadLine.C] == 1.0:
					str_bus_conn = str_bus_conn + '.3'
					num_phases += 1

				if num_phases == 0:
					print('Error: #-1450')

				if row[OverheadLine.NEUTRAL_WIREDATA_ID] < 1.0:
					num_neutral = 0

				str_self_name = str(int(row[OverheadLine.TYPE])) + '_' + str(int(row[OverheadLine.ID]))
				str_term1_name = str(terminal_1_type) + '_' + str(int(row[OverheadLine.TERMINAL_1_ID]))
				str_term2_name = str(terminal_2_type) + '_' + str(int(row[OverheadLine.TERMINAL_2_ID]))
				str_pwire_name = str(WireData.CLID) + '_' + str(int(row[OverheadLine.PHASE_WIREDATA_ID]))
				str_nwire_name = str(WireData.CLID) + '_' + str(int(row[OverheadLine.NEUTRAL_WIREDATA_ID]))
				if terminal_1_type == VSource.CLID:
					str_term1_name = 'sourcebus'
				elif terminal_2_type == VSource.CLID:
					str_term2_name = 'sourcebus'

				if debug == 1:
					print('New \'LineGeometry.LG_{}\' Nconds=\'{}\' Nphases=\'{}\'\n'.format(
						int(row[OverheadLine.ID]), num_phases+num_neutral, num_phases))
					if row[OverheadLine.A] == 1.0:
						print('~ Cond=1 Wire=\'{}\' X=\'{:0.3f}\' H=\'{:0.3f}\' Units=\'{}\'\n'.format(
							str_pwire_name, row[OverheadLine.X_A_COORDINATE], row[OverheadLine.H_A_COORDINATE], OverheadLine.UNITS))
					if row[OverheadLine.B] == 1.0:
						print('~ Cond=2 Wire=\'{}\' X=\'{:0.3f}\' H=\'{:0.3f}\' Units=\'{}\'\n'.format(
							str_pwire_name, row[OverheadLine.X_B_COORDINATE], row[OverheadLine.H_B_COORDINATE], OverheadLine.UNITS))
					if row[OverheadLine.C] == 1.0:
						print('~ Cond=3 Wire=\'{}\' X=\'{:0.3f}\' H=\'{:0.3f}\' Units=\'{}\'\n'.format(
							str_pwire_name, row[OverheadLine.X_C_COORDINATE], row[OverheadLine.H_C_COORDINATE], OverheadLine.UNITS))
					if num_neutral == 1:
						print('~ Cond=4 Wire=\'{}\' X=\'{:0.3f}\' H=\'{:0.3f}\' Units=\'{}\'\n'.format(
							str_nwire_name, row[OverheadLine.X_N_COORDINATE], row[OverheadLine.H_N_COORDINATE], OverheadLine.UNITS))
					print('New \'Line.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' Phases=\'{}\' Geometry=\'LG_{}\' Length=\'{:f}\' Rho=\'{:f}\' Units=\'{}\'\n'.format(
						str_self_name, str_term1_name, str_bus_conn, str_term2_name,
						str_bus_conn, num_phases, int(row[OverheadLine.ID]), row[OverheadLine.LENGTH],
						row[OverheadLine.SOIL_RESISTIVITY], OverheadLine.UNITS))

				dss.Command = 'New \'LineGeometry.LG_{}\' Nconds=\'{}\' Nphases=\'{}\''.format(
					int(row[OverheadLine.ID]), num_phases+num_neutral, num_phases)
				if row[OverheadLine.A] == 1.0:
					dss.Command = '~ Cond=1 Wire=\'{}\' X=\'{:0.3f}\' H=\'{:0.3f}\' Units=\'{}\''.format(
							str_pwire_name, row[OverheadLine.X_A_COORDINATE], row[OverheadLine.H_A_COORDINATE], OverheadLine.UNITS)
				if row[OverheadLine.B] == 1.0:
					dss.Command = '~ Cond=2 Wire=\'{}\' X=\'{:0.3f}\' H=\'{:0.3f}\' Units=\'{}\''.format(
							str_pwire_name, row[OverheadLine.X_B_COORDINATE], row[OverheadLine.H_B_COORDINATE], OverheadLine.UNITS)
				if row[OverheadLine.C] == 1.0:
					dss.Command = '~ Cond=3 Wire=\'{}\' X=\'{:0.3f}\' H=\'{:0.3f}\' Units=\'{}\''.format(
							str_pwire_name, row[OverheadLine.X_C_COORDINATE], row[OverheadLine.H_C_COORDINATE], OverheadLine.UNITS)
				if num_neutral == 1:
					dss.Command = '~ Cond=4 Wire=\'{}\' X=\'{:0.3f}\' H=\'{:0.3f}\' Units=\'{}\''.format(
							str_nwire_name, row[OverheadLine.X_N_COORDINATE], row[OverheadLine.H_N_COORDINATE], OverheadLine.UNITS)
				dss.Command = 'New \'Line.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' Phases=\'{}\' Geometry=\'LG_{}\' Length=\'{:f}\' Rho=\'{:f}\' Units=\'{}\''.format(
						str_self_name, str_term1_name, str_bus_conn, str_term2_name,
						str_bus_conn, num_phases, int(row[OverheadLine.ID]), row[OverheadLine.LENGTH],
						row[OverheadLine.SOIL_RESISTIVITY], OverheadLine.UNITS)
			return 0
		except:
			print('Error: #-1450')
			return -1450

	def addToNodesDict(self, dictionary):
		try:
			return 0
		except:
			print('Error: #-1452')
			return -1452

	def voltagesToSets(self):
		return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			for row in self.matrix:
				idxcount = 0
				dssCkt.Lines.Name = str(int(row[OverheadLine.TYPE])) + '_' + str(int(row[OverheadLine.ID]))
				var_bus = list(dssActvElem.BusNames)
				var_curr = list(dssActvElem.CurrentsMagAng)
				var_pow = list(dssActvElem.Powers)
				norm_amps_inv = 1.0 / dssActvElem.NormalAmps
				num_phases = dssActvElem.NumPhases
				num_conds = dssActvElem.NumConductors

				row[OverheadLine.A_1_CURRENT : OverheadLine.ANGLE_DELTA+1] = 0.0

				if row[OverheadLine.A] == 1.0:
					row[OverheadLine.A_1_CURRENT] = var_curr[idxcount*2]
					row[OverheadLine.A_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[OverheadLine.REAL_POWER_1] += var_pow[idxcount*2]
					row[OverheadLine.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[OverheadLine.B] == 1.0:
					row[OverheadLine.B_1_CURRENT] = var_curr[idxcount*2]
					row[OverheadLine.B_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[OverheadLine.REAL_POWER_1] += var_pow[idxcount*2]
					row[OverheadLine.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[OverheadLine.C] == 1.0:
					row[OverheadLine.C_1_CURRENT] = var_curr[idxcount*2]
					row[OverheadLine.C_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[OverheadLine.REAL_POWER_1] += var_pow[idxcount*2]
					row[OverheadLine.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[OverheadLine.N_1_CURRENT] = var_curr[idxcount*2]
					row[OverheadLine.N_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
				if row[OverheadLine.A] == 1.0:
					row[OverheadLine.A_2_CURRENT] = var_curr[idxcount*2]
					row[OverheadLine.A_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[OverheadLine.REAL_POWER_2] += var_pow[idxcount*2]
					row[OverheadLine.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[OverheadLine.B] == 1.0:
					row[OverheadLine.B_2_CURRENT] = var_curr[idxcount*2]
					row[OverheadLine.B_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[OverheadLine.REAL_POWER_2] += var_pow[idxcount*2]
					row[OverheadLine.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[OverheadLine.C] == 1.0:
					row[OverheadLine.C_2_CURRENT] = var_curr[idxcount*2]
					row[OverheadLine.C_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[OverheadLine.REAL_POWER_2] += var_pow[idxcount*2]
					row[OverheadLine.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[OverheadLine.N_2_CURRENT] = var_curr[idxcount*2]
					row[OverheadLine.N_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]

				row[OverheadLine.REAL_POWER_LOSSES] = math.fabs(row[OverheadLine.REAL_POWER_1] + row[OverheadLine.REAL_POWER_2])
				row[OverheadLine.REACTIVE_POWER_LOSSES] = math.fabs(row[OverheadLine.REACTIVE_POWER_1] + row[OverheadLine.REACTIVE_POWER_2])

				row[OverheadLine.A_PU_CAPACITY] = 0.5 * (row[OverheadLine.A_1_CURRENT] + row[OverheadLine.A_2_CURRENT]) * norm_amps_inv
				row[OverheadLine.B_PU_CAPACITY] = 0.5 * (row[OverheadLine.B_1_CURRENT] + row[OverheadLine.B_2_CURRENT]) * norm_amps_inv
				row[OverheadLine.C_PU_CAPACITY] = 0.5 * (row[OverheadLine.C_1_CURRENT] + row[OverheadLine.C_2_CURRENT]) * norm_amps_inv
			return 0
		except:
			print('Error: #-1454')
			return -1454

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1456')
			return -1456

	def convertToInputTensor(self):
		try:
			return [], [], np.empty([0, 0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			pass

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0, 0], dtype=np.float32).flatten()
		except:
			pass

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		pass

class TwoWindingTransformer: #errors -1475 to -1499
	CLID = 1403

	ID = 0
	TYPE = 1
	TERMINAL_1_ID = 2
	TERMINAL_2_ID = 3
	FUNCTIONAL_STATUS = 4 # switch
	A = 5
	B = 6
	C = 7
	MIN_TAP = 8 
	MAX_TAP = 9
	R1 = 10
	RATED_CAPACITY = 11
	REGCONTROL_ID = 12
	TERMINAL_1_LL_VOLTAGE = 13
	TERMINAL_1_WIRING = 14
	TERMINAL_2_LL_VOLTAGE = 15
	TERMINAL_2_WIRING = 16
	X1 = 17
	ANGLE_DELTA_LIMIT = 18
	MAX_PU_CAPACITY = 19
	OPERATIONAL_STATUS = 20 # switch
	TAP_1 = 21 # stochastic
	TAP_2 = 22 # stochastic
	A_1_CURRENT = 23
	B_1_CURRENT = 24
	C_1_CURRENT = 25
	N_1_CURRENT = 26
	A_1_CURRENT_ANGLE = 27
	B_1_CURRENT_ANGLE = 28
	C_1_CURRENT_ANGLE = 29
	N_1_CURRENT_ANGLE = 30
	A_2_CURRENT = 31
	B_2_CURRENT = 32
	C_2_CURRENT = 33
	N_2_CURRENT = 34
	A_2_CURRENT_ANGLE = 35
	B_2_CURRENT_ANGLE = 36
	C_2_CURRENT_ANGLE = 37
	N_2_CURRENT_ANGLE = 38
	REAL_POWER_1 = 39
	REACTIVE_POWER_1 = 40
	REAL_POWER_2 = 41
	REACTIVE_POWER_2 = 42
	REAL_POWER_LOSSES = 43
	REACTIVE_POWER_LOSSES = 44
	ANGLE_DELTA = 45
	PU_CAPACITY = 46

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = self.num_components * 1 # temporary
		self.num_stochastic = self.num_components * 2

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('POWER ERROR in TwoWindingTransformer0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			for row in self.matrix:
				terminal_1_type = type(dictionary[row[TwoWindingTransformer.TERMINAL_1_ID]]).CLID
				terminal_2_type = type(dictionary[row[TwoWindingTransformer.TERMINAL_2_ID]]).CLID
				terminal_1_str_conn = 'wye'
				terminal_2_str_conn = 'wye'
				terminal_1_num_kv = row[TwoWindingTransformer.TERMINAL_1_LL_VOLTAGE]
				terminal_2_num_kv = row[TwoWindingTransformer.TERMINAL_2_LL_VOLTAGE]
				str_bus_conn = ''
				num_phases = 0
				num_windings = 2

				if row[TwoWindingTransformer.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'
					num_phases += 1
				if row[TwoWindingTransformer.B] == 1.0:
					str_bus_conn = str_bus_conn + '.2'
					num_phases += 1
				if row[TwoWindingTransformer.C] == 1.0:
					str_bus_conn = str_bus_conn + '.3'
					num_phases += 1

				if row[TwoWindingTransformer.TERMINAL_1_WIRING] == 0.0:
					terminal_1_str_conn = 'delta'
					if num_phases == 1:
						print('Error: #-1475')
				if row[TwoWindingTransformer.TERMINAL_2_WIRING] == 0.0:
					terminal_2_str_conn = 'delta'
					if num_phases == 1:
						print('Error: #-1475')

				if num_phases == 0:
					print('Error: #-1476')

				if num_phases == 1:
					terminal_1_num_kv = terminal_1_num_kv / math.sqrt(3.0)
					terminal_2_num_kv = terminal_2_num_kv / math.sqrt(3.0)

				str_self_name = str(int(row[TwoWindingTransformer.TYPE])) + '_' + str(int(row[TwoWindingTransformer.ID]))
				str_term1_name = str(terminal_1_type) + '_' + str(int(row[TwoWindingTransformer.TERMINAL_1_ID]))
				str_term2_name = str(terminal_2_type) + '_' + str(int(row[TwoWindingTransformer.TERMINAL_2_ID]))
				if terminal_1_type == VSource.CLID:
					str_term1_name = 'sourcebus'
				elif terminal_2_type == VSource.CLID:
					str_term2_name = 'sourcebus'

				row[TwoWindingTransformer.TAP_1] = round(row[TwoWindingTransformer.TAP_1])
				row[TwoWindingTransformer.TAP_2] = round(row[TwoWindingTransformer.TAP_2])
				row[TwoWindingTransformer.MIN_TAP] = round(row[TwoWindingTransformer.MIN_TAP])
				row[TwoWindingTransformer.MAX_TAP] = round(row[TwoWindingTransformer.MAX_TAP])

				if row[TwoWindingTransformer.TAP_1] < row[TwoWindingTransformer.MIN_TAP]:
					row[TwoWindingTransformer.TAP_1] = row[TwoWindingTransformer.MIN_TAP]
				elif row[TwoWindingTransformer.TAP_1] > row[TwoWindingTransformer.MAX_TAP]:
					row[TwoWindingTransformer.TAP_1] = row[TwoWindingTransformer.MAX_TAP]

				if row[TwoWindingTransformer.TAP_2] < row[TwoWindingTransformer.MIN_TAP]:
					row[TwoWindingTransformer.TAP_2] = row[TwoWindingTransformer.MIN_TAP]
				elif row[TwoWindingTransformer.TAP_2] > row[TwoWindingTransformer.MAX_TAP]:
					row[TwoWindingTransformer.TAP_2] = row[TwoWindingTransformer.MAX_TAP]

				if debug == 1:
					print('New \'Transformer.{}\' Phases=\'{}\' Windings=\'{}\' XHL=\'{:f}\' %LoadLoss=\'{:f}\'\n'.format(
						str_self_name, num_phases, num_windings, row[TwoWindingTransformer.X1]*0.01,
						row[TwoWindingTransformer.R1]*0.01))
					print('~ wdg=1 Bus=\'{}{}\' Kv=\'{:f}\' Tap=\'{:f}\' Kva=\'{:f}\' Conn=\'{}\'\n'.format(
						str_term1_name, str_bus_conn, terminal_1_num_kv, 1.0 + row[TwoWindingTransformer.TAP_1]*0.00625,
						row[TwoWindingTransformer.RATED_CAPACITY], terminal_1_str_conn))
					print('~ wdg=2 Bus=\'{}{}\' Kv=\'{:f}\' Tap=\'{:f}\' Kva=\'{:f}\' Conn=\'{}\'\n'.format(
						str_term2_name, str_bus_conn, terminal_2_num_kv, 1.0 + row[TwoWindingTransformer.TAP_2]*0.00625,
						row[TwoWindingTransformer.RATED_CAPACITY], terminal_2_str_conn))
					if row[TwoWindingTransformer.FUNCTIONAL_STATUS]*row[TwoWindingTransformer.OPERATIONAL_STATUS] == 0.0:
						print('Open \'Transformer.{}\' Term=1'.format(str_self_name))
						print('Open \'Transformer.{}\' Term=2'.format(str_self_name))

				dss.Command = 'New \'Transformer.{}\' Phases=\'{}\' Windings=\'{}\' XHL=\'{:f}\' %LoadLoss=\'{:f}\''.format(
						str_self_name, num_phases, num_windings, row[TwoWindingTransformer.X1]*0.01,
						row[TwoWindingTransformer.R1]*0.01)
				dss.Command = '~ wdg=1 Bus=\'{}{}\' Kv=\'{:f}\' Tap=\'{:f}\' Kva=\'{:f}\' Conn=\'{}\''.format(
						str_term1_name, str_bus_conn, terminal_1_num_kv, 1.0 + row[TwoWindingTransformer.TAP_1]*0.00625,
						row[TwoWindingTransformer.RATED_CAPACITY], terminal_1_str_conn)
				dss.Command = '~ wdg=2 Bus=\'{}{}\' Kv=\'{:f}\' Tap=\'{:f}\' Kva=\'{:f}\' Conn=\'{}\''.format(
						str_term2_name, str_bus_conn, terminal_2_num_kv, 1.0 + row[TwoWindingTransformer.TAP_2]*0.00625,
						row[TwoWindingTransformer.RATED_CAPACITY], terminal_2_str_conn)
				if row[TwoWindingTransformer.FUNCTIONAL_STATUS]*row[TwoWindingTransformer.OPERATIONAL_STATUS] == 0.0:
					dss.Command = 'Open \'Transformer.{}\' Term=1'.format(str_self_name)
					dss.Command = 'Open \'Transformer.{}\' Term=2'.format(str_self_name)
			return 0
		except:
			print('Error: #-1475')
			return -1475

	def addToNodesDict(self, dictionary):
		try:
			return 0
		except:
			print('Error: #-1477')
			return -1477

	def voltagesToSets(self):
		try:
			return set(self.matrix[:, TwoWindingTransformer.TERMINAL_1_LL_VOLTAGE]) | set(self.matrix[:, TwoWindingTransformer.TERMINAL_2_LL_VOLTAGE])
		except:
			print('Error: #-1479')
			return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			for row in self.matrix:
				idxcount = 0
				dssCkt.Transformers.Name = str(int(row[TwoWindingTransformer.TYPE])) + '_' + str(int(row[TwoWindingTransformer.ID]))
				var_bus = list(dssActvElem.BusNames)
				var_curr = list(dssActvElem.CurrentsMagAng)
				var_pow = list(dssActvElem.Powers)
				norm_amps = dssActvElem.NormalAmps
				num_phases = dssActvElem.NumPhases
				num_conds = dssActvElem.NumConductors

				row[TwoWindingTransformer.A_1_CURRENT : TwoWindingTransformer.PU_CAPACITY+1] = 0.0

				if row[TwoWindingTransformer.A] == 1.0:
					row[TwoWindingTransformer.A_1_CURRENT] = var_curr[idxcount*2]
					row[TwoWindingTransformer.A_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[TwoWindingTransformer.REAL_POWER_1] += var_pow[idxcount*2]
					row[TwoWindingTransformer.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[TwoWindingTransformer.B] == 1.0:
					row[TwoWindingTransformer.B_1_CURRENT] = var_curr[idxcount*2]
					row[TwoWindingTransformer.B_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[TwoWindingTransformer.REAL_POWER_1] += var_pow[idxcount*2]
					row[TwoWindingTransformer.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[TwoWindingTransformer.C] == 1.0:
					row[TwoWindingTransformer.C_1_CURRENT] = var_curr[idxcount*2]
					row[TwoWindingTransformer.C_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[TwoWindingTransformer.REAL_POWER_1] += var_pow[idxcount*2]
					row[TwoWindingTransformer.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[TwoWindingTransformer.N_1_CURRENT] = var_curr[idxcount*2]
					row[TwoWindingTransformer.N_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
				if row[TwoWindingTransformer.A] == 1.0:
					row[TwoWindingTransformer.A_2_CURRENT] = var_curr[idxcount*2]
					row[TwoWindingTransformer.A_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[TwoWindingTransformer.REAL_POWER_2] += var_pow[idxcount*2]
					row[TwoWindingTransformer.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[TwoWindingTransformer.B] == 1.0:
					row[TwoWindingTransformer.B_2_CURRENT] = var_curr[idxcount*2]
					row[TwoWindingTransformer.B_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[TwoWindingTransformer.REAL_POWER_2] += var_pow[idxcount*2]
					row[TwoWindingTransformer.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[TwoWindingTransformer.C] == 1.0:
					row[TwoWindingTransformer.C_2_CURRENT] = var_curr[idxcount*2]
					row[TwoWindingTransformer.C_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[TwoWindingTransformer.REAL_POWER_2] += var_pow[idxcount*2]
					row[TwoWindingTransformer.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[TwoWindingTransformer.N_2_CURRENT] = var_curr[idxcount*2]
					row[TwoWindingTransformer.N_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]

				row[TwoWindingTransformer.REAL_POWER_LOSSES] = math.fabs(row[TwoWindingTransformer.REAL_POWER_1] + row[TwoWindingTransformer.REAL_POWER_2])
				row[TwoWindingTransformer.REACTIVE_POWER_LOSSES] = math.fabs(row[TwoWindingTransformer.REACTIVE_POWER_1] + row[TwoWindingTransformer.REACTIVE_POWER_2])
				row[TwoWindingTransformer.PU_CAPACITY] = math.fabs(row[TwoWindingTransformer.A_1_CURRENT] + row[TwoWindingTransformer.B_1_CURRENT] + row[TwoWindingTransformer.C_1_CURRENT]) / (num_phases * norm_amps)
			return 0
		except:
			print('Error: #-1481')
			return -1481

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1483')
			return -1483

	def convertToInputTensor(self):
		try:
			input_list_continuous = []
			input_list_categorical = []
			input_col_continuous = ['tap_1', 'tap_2']
			input_col_categorical = ['operational_status']

			for row in self.matrix:
				for elem in input_col_continuous:
					input_list_continuous.append('TwoWindingTransformer_' + str(int(row[TwoWindingTransformer.ID])) + '_' + elem)
				for elem in input_col_categorical:
					input_list_categorical.append('TwoWindingTransformer_' + str(int(row[TwoWindingTransformer.ID])) + '_' + elem)

			inputdf = self.convertToDataFrame()
			inputdf_continuous = inputdf[input_col_continuous]
			inputdf_categorical = inputdf[input_col_categorical]
			return input_list_continuous, input_list_categorical, inputdf_continuous.values.flatten(), inputdf_categorical.values.flatten()
		except:
			print('Error: #-1484')
			return -1484

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['PU_capacity']

			for row in self.matrix:
				for elem in output_col:
					output_list.append('TwoWindingTransformer_' + str(int(row[TwoWindingTransformer.ID])) + '_' + elem)

			outputdf = self.convertToDataFrame()
			outputdf = outputdf[output_col]
			return output_list, outputdf.values.flatten()
		except:
			print('Error: #-1485')
			return -1485

	def randomStochasticity(self):
		try:
			row = random.randrange(0, self.num_components)
			rval = random.randrange(-1, 2, 2)
			if random.randrange(0, 2) == 0:
				self.matrix[row, TwoWindingTransformer.TAP_1] += rval
				if self.matrix[row, TwoWindingTransformer.TAP_1] < self.matrix[row, TwoWindingTransformer.MIN_TAP]:
					self.matrix[row, TwoWindingTransformer.TAP_1] = self.matrix[row, TwoWindingTransformer.MIN_TAP]
				elif self.matrix[row, TwoWindingTransformer.TAP_1] > self.matrix[row, TwoWindingTransformer.MAX_TAP]:
					self.matrix[row, TwoWindingTransformer.TAP_1] = self.matrix[row, TwoWindingTransformer.MAX_TAP]
			else:
				self.matrix[row, TwoWindingTransformer.TAP_2] += rval
				if self.matrix[row, TwoWindingTransformer.TAP_2] < self.matrix[row, TwoWindingTransformer.MIN_TAP]:
					self.matrix[row, TwoWindingTransformer.TAP_2] = self.matrix[row, TwoWindingTransformer.MIN_TAP]
				elif self.matrix[row, TwoWindingTransformer.TAP_2] > self.matrix[row, TwoWindingTransformer.MAX_TAP]:
					self.matrix[row, TwoWindingTransformer.TAP_2] = self.matrix[row, TwoWindingTransformer.MAX_TAP]
		except:
			print('Error: #-1486')
			return -1486

	def randomSwitching(self):
		try:
			row = random.randrange(0, self.num_components)
			self.matrix[row, TwoWindingTransformer.OPERATIONAL_STATUS] = 0.0
		except:
			print('Error: #-1487')
			return -1487

class Capacitor: #errors -1500 to -1524
	CLID = 1404

	ID = 0
	TYPE = 1
	TERMINAL_1_ID = 2
	TERMINAL_2_ID = 3
	FUNCTIONAL_STATUS = 4 # switch
	A = 5
	B = 6
	C = 7
	NOMINAL_LL_VOLTAGE = 8
	RATED_REACTIVE_POWER = 9
	WIRING = 10
	ANGLE_DELTA_LIMIT = 11
	MAX_PU_CAPACITY = 12
	OPERATIONAL_STATUS = 13 # switch
	A_1_CURRENT = 14
	B_1_CURRENT = 15
	C_1_CURRENT = 16
	N_1_CURRENT = 17
	A_1_CURRENT_ANGLE = 18
	B_1_CURRENT_ANGLE = 19
	C_1_CURRENT_ANGLE = 20
	N_1_CURRENT_ANGLE = 21
	A_2_CURRENT = 22
	B_2_CURRENT = 23
	C_2_CURRENT = 24
	N_2_CURRENT = 25
	A_2_CURRENT_ANGLE = 26
	B_2_CURRENT_ANGLE = 27
	C_2_CURRENT_ANGLE = 28
	N_2_CURRENT_ANGLE = 29
	REAL_POWER_1 = 30
	REACTIVE_POWER_1 = 31
	REAL_POWER_2 = 32
	REACTIVE_POWER_2 = 33
	REAL_POWER_LOSSES = 34
	REACTIVE_POWER_LOSSES = 35
	ANGLE_DELTA = 36
	PU_CAPACITY = 37

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
			print('POWER ERROR in Capacitor0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			for row in self.matrix:
				terminal_1_type = type(dictionary[row[Capacitor.TERMINAL_1_ID]]).CLID
				bool_terminal_2 = False
				try:
					terminal_2_type = type(dictionary[row[Capacitor.TERMINAL_2_ID]]).CLID
					bool_terminal_2 = True
				except:
					pass
				num_kv = row[Capacitor.NOMINAL_LL_VOLTAGE]
				str_conn = 'wye'
				str_bus_conn = ''
				num_phases = 0

				if row[Capacitor.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'
					num_phases += 1
				if row[Capacitor.B] == 1.0:
					str_bus_conn = str_bus_conn + '.2'
					num_phases += 1
				if row[Capacitor.C] == 1.0:
					str_bus_conn = str_bus_conn + '.3'
					num_phases += 1

				if row[Capacitor.WIRING] == 0.0:
					str_conn = 'delta'
				elif num_phases == 1:
					num_kv = num_kv / math.sqrt(3.0)
				if num_phases == 0:
					print('Error: #-1501')

				str_self_name = str(int(row[Capacitor.TYPE])) + '_' + str(int(row[Capacitor.ID]))
				str_term1_name = str(terminal_1_type) + '_' + str(int(row[Capacitor.TERMINAL_1_ID]))
				if terminal_1_type == VSource.CLID:
					str_term1_name = 'sourcebus'
				if bool_terminal_2 == True:
					str_term2_name = str(terminal_2_type) + '_' + str(int(row[Capacitor.TERMINAL_2_ID]))
					if terminal_2_type == VSource.CLID:
						str_term2_name = 'sourcebus'

				if debug == 1:
					if bool_terminal_2 == True:
						print('New \'Capacitor.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' Phases={} Kvar=\'{:f}\' Kv=\'{:f}\' Conn=\'{}\'\n'.format(
							str_self_name, str_term1_name, str_bus_conn, str_term2_name,
							str_bus_conn, num_phases, row[Capacitor.RATED_REACTIVE_POWER], num_kv,
							str_conn))
					else:
						print('New \'Capacitor.{}\' Bus1=\'{}{}\' Phases={} Kvar=\'{:f}\' Kv=\'{:f}\' Conn=\'{}\'\n'.format(
							str_self_name, str_term1_name, str_bus_conn, num_phases,
							row[Capacitor.RATED_REACTIVE_POWER], num_kv, str_conn))
					if row[Capacitor.FUNCTIONAL_STATUS]*row[Capacitor.OPERATIONAL_STATUS] == 0.0:
						print('Open \'Capacitor.{}\' Term=1'.format(str_self_name))
						print('Open \'Capacitor.{}\' Term=2'.format(str_self_name))

				if bool_terminal_2 == True:
					dss.Command = 'New \'Capacitor.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' Phases={} Kvar=\'{:f}\ Kv=\'{:f}\' Conn=\'{}\''.format(
							str_self_name, str_term1_name, str_bus_conn, str_term2_name,
							str_bus_conn, num_phases, row[Capacitor.RATED_REACTIVE_POWER], num_kv,
							str_conn)
				else:
					dss.Command = 'New \'Capacitor.{}\' Bus1=\'{}{}\' Phases={} Kvar=\'{:f}\' Kv=\'{:f}\' Conn=\'{}\''.format(
							str_self_name, str_term1_name, str_bus_conn, num_phases,
							row[Capacitor.RATED_REACTIVE_POWER], num_kv, str_conn)
				if row[Capacitor.FUNCTIONAL_STATUS]*row[Capacitor.OPERATIONAL_STATUS] == 0.0:
					dss.Command = 'Open \'Capacitor.{}\' Term=1'.format(str_self_name)
					dss.Command = 'Open \'Capacitor.{}\' Term=2'.format(str_self_name)
			return 0
		except:
			print('Error: #-1500')
			return -1500

	def addToNodesDict(self, dictionary):
		try:
			return 0
		except:
			print('Error: #-1502')
			return -1502

	def voltagesToSets(self):
		return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			for row in self.matrix:
				idxcount = 0
				dssCkt.Capacitors.Name = str(int(row[Capacitor.TYPE])) + '_' + str(int(row[Capacitor.ID]))
				var_bus = list(dssActvElem.BusNames)
				var_curr = list(dssActvElem.CurrentsMagAng)
				var_pow = list(dssActvElem.Powers)
				num_phases = dssActvElem.NumPhases
				num_conds = dssActvElem.NumConductors
				norm_amps = math.sqrt(3.0) * row[Capacitor.RATED_REACTIVE_POWER] / (num_phases * row[Capacitor.NOMINAL_LL_VOLTAGE])
				row[Capacitor.A_1_CURRENT : Capacitor.PU_CAPACITY+1] = 0.0

				if row[Capacitor.A] == 1.0:
					row[Capacitor.A_1_CURRENT] = var_curr[idxcount*2]
					row[Capacitor.A_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Capacitor.REAL_POWER_1] += var_pow[idxcount*2]
					row[Capacitor.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[Capacitor.B] == 1.0:
					row[Capacitor.B_1_CURRENT] = var_curr[idxcount*2]
					row[Capacitor.B_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Capacitor.REAL_POWER_1] += var_pow[idxcount*2]
					row[Capacitor.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[Capacitor.C] == 1.0:
					row[Capacitor.C_1_CURRENT] = var_curr[idxcount*2]
					row[Capacitor.C_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Capacitor.REAL_POWER_1] += var_pow[idxcount*2]
					row[Capacitor.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[Capacitor.N_1_CURRENT] = var_curr[idxcount*2]
					row[Capacitor.N_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
				if row[Capacitor.A] == 1.0:
					row[Capacitor.A_2_CURRENT] = var_curr[idxcount*2]
					row[Capacitor.A_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Capacitor.REAL_POWER_2] += var_pow[idxcount*2]
					row[Capacitor.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[Capacitor.B] == 1.0:
					row[Capacitor.B_2_CURRENT] = var_curr[idxcount*2]
					row[Capacitor.B_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Capacitor.REAL_POWER_2] += var_pow[idxcount*2]
					row[Capacitor.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if row[Capacitor.C] == 1.0:
					row[Capacitor.C_2_CURRENT] = var_curr[idxcount*2]
					row[Capacitor.C_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Capacitor.REAL_POWER_2] += var_pow[idxcount*2]
					row[Capacitor.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					row[Capacitor.N_2_CURRENT] = var_curr[idxcount*2]
					row[Capacitor.N_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]

				row[Capacitor.REAL_POWER_LOSSES] = math.fabs(row[Capacitor.REAL_POWER_1] + row[Capacitor.REAL_POWER_2])
				row[Capacitor.REACTIVE_POWER_LOSSES] = math.fabs(row[Capacitor.REACTIVE_POWER_1] + row[Capacitor.REACTIVE_POWER_2])

				row[Capacitor.PU_CAPACITY] = (math.fabs(row[Capacitor.A_1_CURRENT] + row[Capacitor.B_1_CURRENT] + row[Capacitor.C_1_CURRENT]) + math.fabs(row[Capacitor.A_2_CURRENT] + row[Capacitor.B_2_CURRENT] + row[Capacitor.C_2_CURRENT])) / (2.0 * num_phases * norm_amps)
			return 0
		except:
			print('Error: #-1504')
			return -1504

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1506')
			return -1506

	def convertToInputTensor(self):
		try:
			input_list_continuous = []
			input_list_categorical = []
			input_col_categorical = ['operational_status']

			for row in self.matrix:
				for elem in input_col_categorical:
					input_list_categorical.append('Capacitor_' + str(int(row[Capacitor.ID])) + '_' + elem)

			inputdf = self.convertToDataFrame()
			inputdf_categorical = inputdf[input_col_categorical]
			return input_list_continuous, input_list_categorical, np.empty([0,0], dtype=np.float32).flatten(), inputdf_categorical.values.flatten()
		except:
			print('Error: #-1507')
			return -1507

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['PU_capacity']

			for row in self.matrix:
				for elem in output_col:
					output_list.append('Capacitor_' + str(int(row[Capacitor.ID])) + '_' + elem)

			outputdf = self.convertToDataFrame()
			outputdf = outputdf[output_col]
			return output_list, outputdf.values.flatten()
		except:
			print('Error: #-1508')
			return -1508

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		try:
			row = random.randrange(0, self.num_components)
			self.matrix[row, Capacitor.OPERATIONAL_STATUS] = 0.0
		except:
			print('Error: #-1509')
			return -1509

class Reactor: #errors -1525 to -1549
	CLID = 1405
	
	ID = 0
	TYPE = 1
	TERMINAL_1_ID = 2
	TERMINAL_2_ID = 3
	FUNCTIONAL_STATUS = 4 # switch
	A = 5
	B = 6
	C = 7
	NOMINAL_LL_VOLTAGE = 8
	NORMAL_AMPS = 9
	R1 = 10
	RATED_REACTIVE_POWER = 11
	ANGLE_DELTA_LIMIT = 12
	MAX_PU_CAPACITY = 13
	OPERATIONAL_STATUS = 14 # switch
	A_1_CURRENT = 15
	B_1_CURRENT = 16
	C_1_CURRENT = 17
	N_1_CURRENT = 18
	A_1_CURRENT_ANGLE = 19
	B_1_CURRENT_ANGLE = 20
	C_1_CURRENT_ANGLE = 21
	N_1_CURRENT_ANGLE = 22
	A_2_CURRENT = 23
	B_2_CURRENT = 24
	C_2_CURRENT = 25
	N_2_CURRENT = 26
	A_2_CURRENT_ANGLE = 27
	B_2_CURRENT_ANGLE = 28
	C_2_CURRENT_ANGLE = 29
	N_2_CURRENT_ANGLE = 30
	REAL_POWER_1 = 31
	REACTIVE_POWER_1 = 32
	REAL_POWER_2 = 33
	REACTIVE_POWER_2 = 34
	REAL_POWER_LOSSES = 35
	REACTIVE_POWER_LOSSES = 36
	ANGLE_DELTA = 37
	PU_CAPACITY = 38

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
			print('POWER ERROR in Reactor0')

	def createAllDSS(self, dss, dictionary, interconn_dict, debug):
		try:
			return 0
		except:
			print('Error: #-1525')
			return -1525

	def addToNodesDict(self, dictionary):
		try:
			return 0
		except:
			print('Error: #-1527')
			return -1527

	def voltagesToSets(self):
		return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			return 0
		except:
			print('Error: #-1529')
			return -1529

	def convertToDataFrame(self):
		try:
			return pd.DataFrame(data=self.matrix, columns=self.cols)
		except:
			print('Error: #-1531')
			return -1531

	def convertToInputTensor(self):
		try:
			return [], [], np.empty([0, 0], dtype=np.float32).flatten(), np.empty([0,0], dtype=np.float32).flatten()
		except:
			pass

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0, 0], dtype=np.float32).flatten()
		except:
			pass

	def randomStochasticity(self):
		pass

	def randomSwitching(self):
		pass