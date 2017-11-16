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

import numpy as np
import pandas as pd
import math, random

SQRTTHREE = math.sqrt(3.)

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

	def createAllDSS(self, dss, interconn_dict, debug):
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
			return [], [], np.empty([0, 0], dtype=np.float64).flatten(), np.empty([0,0], dtype=np.float64).flatten()
		except:
			print('Error: #-1009')
			return -1009

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0, 0], dtype=np.float64).flatten()
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

	def createAllDSS(self, dss, interconn_dict, debug):
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
			return [], [], np.empty([0, 0], dtype=np.float64).flatten(), np.empty([0,0], dtype=np.float64).flatten()
		except:
			pass

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0, 0], dtype=np.float64).flatten()
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

	def createAllDSS(self, dss, interconn_dict, debug):
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
			return [], [], np.empty([0, 0], dtype=np.float64).flatten(), np.empty([0,0], dtype=np.float64).flatten()
		except:
			return 0

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0, 0], dtype=np.float64).flatten()
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
	NUMBER_OF_PHASES = 3
	R0_SCALAR = 4
	R1_SCALAR = 5
	X0_SCALAR = 6
	X1_SCALAR = 7
	C0_SCALAR = 8
	C1_SCALAR = 9
	B0_SCALAR = 10
	B1_SCALAR = 11
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

	def createAllDSS(self, dss, interconn_dict, debug):
		try:
			for row in self.matrix:
				neutral_reduce = 'N'

				if row[LineCode.KRON_REDUCTION] == 1.0:
					neutral_reduce = 'Y'

				str_self_name = str(int(row[LineCode.TYPE])) + '_' + str(int(row[LineCode.ID]))

				if row[LineCode.C0_SCALAR] != 0.0 or row[LineCode.C1_SCALAR] != 0.0:
					str_impedance = 'R0=\'{:f}\' R1=\'{:f}\' X0=\'{:f}\' X1=\'{:f}\' C0=\'{:f}\' C1=\'{:f}\''.format(
						row[LineCode.R0_SCALAR], row[LineCode.R1_SCALAR], row[LineCode.X0_SCALAR], row[LineCode.X1_SCALAR],
						row[LineCode.C0_SCALAR], row[LineCode.C1_SCALAR])
				elif row[LineCode.B0_SCALAR] != 0.0 or row[LineCode.B1_SCALAR] != 0.0:
					str_impedance = 'R0=\'{:f}\' R1=\'{:f}\' X0=\'{:f}\' X1=\'{:f}\' B0=\'{:f}\' B1=\'{:f}\''.format(
						row[LineCode.R0_SCALAR], row[LineCode.R1_SCALAR], row[LineCode.X0_SCALAR], row[LineCode.X1_SCALAR],
						row[LineCode.B0_SCALAR], row[LineCode.B1_SCALAR])
				else:
					str_impedance = 'R0=\'{:f}\' R1=\'{:f}\' X0=\'{:f}\' X1=\'{:f}\''.format(
						row[LineCode.R0_SCALAR], row[LineCode.R1_SCALAR], row[LineCode.X0_SCALAR], row[LineCode.X1_SCALAR])

				if debug == 1:
					print('New \'LineCode.{}\' Nphases=\'{}\' {} Units=\'{}\' Kron=\'{}\''.format(
					str_self_name, int(row[LineCode.NUMBER_OF_PHASES]), str_impedance, LineCode.UNITS,
					neutral_reduce))
					print('\n')

				dss.Command = 'New \'LineCode.{}\' Nphases=\'{}\' {} Units=\'{}\' Kron=\'{}\''.format(
					str_self_name, int(row[LineCode.NUMBER_OF_PHASES]), str_impedance, LineCode.UNITS,
					neutral_reduce)
			return 0
		except:
			print('Error: #-1125')
			return -1125

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
			return [], [], np.empty([0, 0], dtype=np.float64).flatten(), np.empty([0,0], dtype=np.float64).flatten()
		except:
			print('Error: #-1132')
			return -1132

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0, 0], dtype=np.float64).flatten()
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

	def createAllDSS(self, dss, interconn_dict, debug):
		return 0

	def voltagesToSets(self):
		return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			for row in self.matrix:
				idxcount = 0
				dssCkt.SetActiveBus( str(Bus.CLID) + '_' + str(int(row[Bus.ID])) )
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
			return [], [], np.empty([0, 0], dtype=np.float64).flatten(), np.empty([0,0], dtype=np.float64).flatten()
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

	def createAllDSS(self, dss, interconn_dict, debug):
		try:
			for row in self.matrix:
				str_self_name = str(int(row[VSource.TYPE])) + '_' + str(int(row[VSource.ID]))
				num_phases = 0
				mvasc1 = 100
				mvasc3 = 300
				init_volt_pu = 1.0
				voltage_rating = row[VSource.NOMINAL_LL_VOLTAGE]

				if row[VSource.A] == 1.0:
					num_phases += 1

				if num_phases == 1:
					voltage_rating = voltage_rating / math.sqrt(3.0)

				if debug == 1:
					print('New \'Circuit.{}\' Basekv=\'{:f}\' phases=\'{}\' pu=\'{:f}\' Angle=\'{:f}\' Mvasc1=\'{:f}\' Mvasc3=\'{:f}\' R0=\'{:f}\' R1=\'{:f}\' X0=\'{:f}\' X1=\'{:f}\'\n'.format(
					str_self_name, voltage_rating, num_phases, init_volt_pu, row[VSource.VOLTAGE_ANGLE],
					mvasc1, mvasc3, row[VSource.R0], row[VSource.R1],
					row[VSource.X0], row[VSource.X1]))

				dss.Command = 'New \'Circuit.{}\' Basekv=\'{:f}\' phases=\'{}\' pu=\'{:f}\' Angle=\'{:f}\' Mvasc1=\'{:f}\' Mvasc3=\'{:f}\' R0=\'{:f}\' R1=\'{:f}\' X0=\'{:f}\' X1=\'{:f}\''.format(
					str_self_name, voltage_rating, num_phases, init_volt_pu, row[VSource.VOLTAGE_ANGLE],
					mvasc1, mvasc3, row[VSource.R0], row[VSource.R1],
					row[VSource.X0], row[VSource.X1])
			return 0
		except:
			print('Error: #-1175')
			return -1175

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
			return [], [], np.empty([0, 0], dtype=np.float64).flatten(), np.empty([0,0], dtype=np.float64).flatten()
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
	REAL_GENERATION = 5 # stochastic, temporary
	REACTIVE_GENERATION = 6
	MODEL = 7
	RAMP_RATE = 8
	REAL_GENERATION_MIN_RATING = 9
	REAL_GENERATION_MAX_RATING = 10
	REACTIVE_GENERATION_MIN_RATING = 11
	REACTIVE_GENERATION_MAX_RATING = 12
	WATER_CONSUMPTION = 13
	WATER_DERATING = 14
	WIRING = 15
	MIN_PU_VOLTAGE = 16
	MAX_PU_VOLTAGE = 17
	OPERATIONAL_STATUS = 18 # switch
	REAL_GENERATION_CONTROL = 19 # stochastic TODO unused
	REACTIVE_GENERATION_CONTROL = 20 # stochastic TODO unused
	A_PU_VOLTAGE = 21
	A_VOLTAGE = 22
	A_VOLTAGE_ANGLE = 23
	A_CURRENT = 24
	A_CURRENT_ANGLE = 25
	REAL_POWER = 26
	REACTIVE_POWER = 27

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

# TO DO: Code ramp up and down change
	def createAllDSS(self, dss, interconn_dict, debug):
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

				if num_phases == 0:
					print('Error: #-1201')

				if row[Generator.WIRING] == 0.0:
					str_conn = 'delta'
				elif num_phases == 1:
					num_kv = num_kv / math.sqrt(3.0)

				if row[Generator.REAL_GENERATION] > row[Generator.REAL_GENERATION_MAX_RATING]:
					row[Generator.REAL_GENERATION] = row[Generator.REAL_GENERATION_MAX_RATING]
				elif row[Generator.REAL_GENERATION] < row[Generator.REAL_GENERATION_MIN_RATING]:
					row[Generator.REAL_GENERATION] = row[Generator.REAL_GENERATION_MIN_RATING]

				if row[Generator.REACTIVE_GENERATION] > row[Generator.REACTIVE_GENERATION_MAX_RATING]:
					row[Generator.REACTIVE_GENERATION] = row[Generator.REACTIVE_GENERATION_MAX_RATING]
				elif row[Generator.REACTIVE_GENERATION] < row[Generator.REACTIVE_GENERATION_MIN_RATING]:
					row[Generator.REACTIVE_GENERATION] = row[Generator.REACTIVE_GENERATION_MIN_RATING]

				busid = int(row[Generator.ID]) % 100
				str_self_name = str(int(row[Generator.TYPE])) + '_' + str(int(row[Generator.ID]))
				str_bus_name = str(Bus.CLID) + '_' + str(busid)

				for interconn_row in interconn_dict['tankgenerator'].matrix:
					if interconn_row[interconn_dict['tankgenerator'].classValue('CHECK_TANK_LEVEL')] ==  1.0:
						if interconn_row[interconn_dict['tankgenerator'].classValue('GENERATOR_ID')] == row[Generator.ID]:
							for tank_row in interconn_dict['tank'].matrix:
								if tank_row[interconn_dict['tank'].classValue('ID')] == interconn_row[interconn_dict['tankgenerator'].classValue('TANK_ID')]:
									if tank_row[interconn_dict['tank'].classValue('HEAD')] < tank_row[interconn_dict['tank'].classValue('MIN_LEVEL')] + 0.25*(tank_row[interconn_dict['tank'].classValue('MAX_LEVEL')] - tank_row[interconn_dict['tank'].classValue('MIN_LEVEL')]):
										derating = 1.0 - row[Generator.WATER_DERATING]
# TO DO: chose 50% of MAX - MIN

				if debug == 1:
					print('New \'Generator.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Kvar=\'{:f}\' Model=\'{}\' Conn=\'{}\'\n'.format(
					str_self_name, str_bus_name, str_bus_conn, num_phases,
					num_kv, row[Generator.REAL_GENERATION]*derating, row[Generator.REACTIVE_GENERATION]*derating, int(row[Generator.MODEL]),
					str_conn))
					if row[Generator.FUNCTIONAL_STATUS]*row[Generator.OPERATIONAL_STATUS] == 0.0:
						print('Disable \'Generator.{}\''.format(str_self_name))

				dss.Command = 'New \'Generator.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Kvar=\'{:f}\' Model=\'{}\' Conn=\'{}\''.format(
					str_self_name, str_bus_name, str_bus_conn, num_phases,
					num_kv, row[Generator.REAL_GENERATION]*derating, row[Generator.REACTIVE_GENERATION]*derating, int(row[Generator.MODEL]),
					str_conn)
				if row[Generator.FUNCTIONAL_STATUS]*row[Generator.OPERATIONAL_STATUS] == 0.0:
					dss.Command = 'Disable \'Generator.{}\''.format(str_self_name)
			return 0
		except:
			print('Error: #-1200')
			return -1200

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
				busid = int(row[Generator.ID]) % 100
				dssCkt.SetActiveBus(str(Bus.CLID) + '_' + str(busid))
				dssCkt.Generators.Name = str(int(row[Generator.TYPE])) + '_' + str(int(row[Generator.ID]))
				var_volt_mag = list(dssActvBus.VMagAngle)
				var_volt_pu = list(dssActvBus.puVmagAngle)
				var_curr = list(dssActvElem.CurrentsMagAng)
				var_pow = list(dssActvElem.Powers)
				num_phases = dssActvElem.NumPhases
				num_conds = dssActvElem.NumConductors

				row[Generator.A_PU_VOLTAGE : Generator.REACTIVE_POWER+1] = 0.0

				if row[Generator.A] == 1.0:
					row[Generator.A_VOLTAGE] = var_volt_mag[idxcount*2]
					row[Generator.A_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[Generator.A_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[Generator.A_CURRENT] = var_curr[idxcount*2]
					row[Generator.A_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Generator.REAL_POWER] += var_pow[idxcount*2]
					row[Generator.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
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
			input_col_continuous = ['real_generation', 'reactive_generation']
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
			output_col = ['a_PU_voltage', 'a_current']
			
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
				real_generation_max = self.matrix[row, Generator.REAL_GENERATION_MAX_RATING]
				real_generation_min = self.matrix[row, Generator.REAL_GENERATION_MIN_RATING]
				rval = random.normalvariate(0, 0.5 * (real_generation_max - real_generation_min) * 0.04)
				self.matrix[row, Generator.REAL_GENERATION] += rval
				if self.matrix[row, Generator.REAL_GENERATION] > real_generation_max:
					self.matrix[row, Generator.REAL_GENERATION] = real_generation_max
				elif self.matrix[row, Generator.REAL_GENERATION] < real_generation_min:
					self.matrix[row, Generator.REAL_GENERATION] = real_generation_min
			else:
				reactive_generation_max = self.matrix[row, Generator.REACTIVE_GENERATION_MAX_RATING]
				reactive_generation_min = self.matrix[row, Generator.REACTIVE_GENERATION_MIN_RATING]
				rval = random.normalvariate(0, 0.5 * (reactive_generation_max - reactive_generation_min) * 0.04)
				self.matrix[row, Generator.POWER_FACTOR_CONTROL] += rval
				if self.matrix[row, Generator.POWER_FACTOR_CONTROL] > reactive_generation_max:
					self.matrix[row, Generator.POWER_FACTOR_CONTROL] = reactive_generation_max
				elif self.matrix[row, Generator.POWER_FACTOR_CONTROL] < reactive_generation_min:
					self.matrix[row, Generator.POWER_FACTOR_CONTROL] = reactive_generation_min
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
	REAL_LOAD_MAX = 5
	REACTIVE_LOAD_MAX = 6
	MODEL = 7
	WIRING = 8
	REAL_LOAD = 9
	REACTIVE_LOAD = 10
	MIN_PU_VOLTAGE = 11
	MAX_PU_VOLTAGE = 12
	OPERATIONAL_STATUS = 13 # switch
	A_PU_VOLTAGE = 14
	A_VOLTAGE = 15
	A_VOLTAGE_ANGLE = 16
	A_CURRENT = 17
	A_CURRENT_ANGLE = 18
	REAL_POWER = 19
	REACTIVE_POWER = 20

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

	def createAllDSS(self, dss, interconn_dict, debug):
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

				if num_phases == 0:
					print('Error: #-1226')

				if row[Load.WIRING] == 0.0:
					str_conn = 'delta'
				elif num_phases == 1:
					num_kv = num_kv / math.sqrt(3.0)

				str_self_name = str(int(row[Load.TYPE])) + '_' + str(int(row[Load.ID])) + '_' + str(int(row[Load.A]))
				str_bus_name = str(Bus.CLID) + '_' + str(int(row[Load.ID]))

				for interconn_row in interconn_dict['pumpload'].matrix:
					if interconn_row[interconn_dict['pumpload'].classValue('LOAD_ID')] == row[Load.ID]:
						for pump_row in interconn_dict['pump'].matrix:
							if pump_row[interconn_dict['pump'].classValue('ID')] == interconn_row[interconn_dict['pumpload'].classValue('PUMP_ID')]:
								if pump_row[interconn_dict['pump'].classValue('FUNCTIONAL_STATUS')]*pump_row[interconn_dict['pump'].classValue('OPERATIONAL_STATUS')] != 0.0:
									interconn_demand += pump_row[interconn_dict['pump'].classValue('POWER')]
									# TO DO: verify that interonn_demand is in kW

				if row[Load.REAL_LOAD] < 0.0:
					row[Load.REAL_LOAD] = 0.0
				elif row[Load.REAL_LOAD] > row[Load.REAL_LOAD_MAX]:
					row[Load.REAL_LOAD] = row[Load.REAL_LOAD_MAX]

				if row[Load.REACTIVE_LOAD] < 0.0:
					row[Load.REACTIVE_LOAD] = 0.0
				elif row[Load.REACTIVE_LOAD] > row[Load.REACTIVE_LOAD_MAX]:
					row[Load.REACTIVE_LOAD] = row[Load.REACTIVE_LOAD_MAX]

				if debug == 1:
					if row[Load.MODEL] == 8.0:
						print('Zip model not included!\n')
						print('New \'Load.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Kvar=\'{:f}\' Model=\'{}\' ZIPV=[{:f} {:f} {:f} {:f} {:f} {:f} {:f}] Conn=\'{}\' Vminpu=\'{:f}\' Vmaxpu=\'{:f}\'\n'.format(
							str_self_name, str_bus_name, str_bus_conn, num_phases,
							num_kv, row[Load.REAL_LOAD]+interconn_demand, row[Load.REACTIVE_LOAD], int(row[Load.MODEL]),
							row[Load.ZIP_REAL_POWER], row[Load.ZIP_REAL_CURRENT], row[Load.ZIP_REAL_IMPEDANCE], row[Load.ZIP_REACTIVE_POWER],
							row[Load.ZIP_REACTIVE_CURRENT], row[Load.ZIP_REACTIVE_IMPEDANCE], row[Load.ZIP_PU_VOLTAGE_CUTOFF], str_conn,
							row[Load.MIN_PU_VOLTAGE], row[Load.MAX_PU_VOLTAGE]))
					else:
						print('New \'Load.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Kvar=\'{:f}\' Model=\'{}\' Conn=\'{}\' Vminpu=\'{:f}\' Vmaxpu=\'{:f}\'\n'.format(
							str_self_name, str_bus_name, str_bus_conn, num_phases,
							num_kv, row[Load.REAL_LOAD]+interconn_demand, row[Load.REACTIVE_LOAD], int(row[Load.MODEL]),
							str_conn, row[Load.MIN_PU_VOLTAGE], row[Load.MAX_PU_VOLTAGE]))
					if row[Load.FUNCTIONAL_STATUS]*row[Load.OPERATIONAL_STATUS] == 0.0:
						print('Disable \'Load.{}\''.format(str_self_name))

				if row[Load.MODEL] == 8.0:
					dss.Command = 'New \'Load.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Kvar=\'{:f}\' Model=\'{}\' ZIPV=[{:f} {:f} {:f} {:f} {:f} {:f} {:f}] Conn=\'{}\' Vminpu=\'{:f}\' Vmaxpu=\'{:f}\''.format(
						str_self_name, str_bus_name, str_bus_conn, num_phases,
						num_kv, row[Load.REAL_LOAD]+interconn_demand, row[Load.REACTIVE_LOAD], int(row[Load.MODEL]),
						row[Load.ZIP_REAL_POWER], row[Load.ZIP_REAL_CURRENT], row[Load.ZIP_REAL_IMPEDANCE], row[Load.ZIP_REACTIVE_POWER],
						row[Load.ZIP_REACTIVE_CURRENT], row[Load.ZIP_REACTIVE_IMPEDANCE], row[Load.ZIP_PU_VOLTAGE_CUTOFF], str_conn,
						row[Load.MIN_PU_VOLTAGE], row[Load.MAX_PU_VOLTAGE])
					if row[Load.ZIP_REAL_POWER] + row[Load.ZIP_REAL_CURRENT] + row[Load.ZIP_REAL_IMPEDANCE] != 1.0 or row[Load.ZIP_REACTIVE_POWER] + row[Load.ZIP_REACTIVE_CURRENT] + row[Load.ZIP_REACTIVE_IMPEDANCE] != 1.0:
						print('Error: #-1228')
				else:
					dss.Command = 'New \'Load.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Kvar=\'{:f}\' Model=\'{}\' Conn=\'{}\' Vminpu=\'{:f}\' Vmaxpu=\'{:f}\''.format(
						str_self_name, str_bus_name, str_bus_conn, num_phases,
						num_kv, row[Load.REAL_LOAD]+interconn_demand, row[Load.REACTIVE_LOAD], int(row[Load.MODEL]),
						str_conn, row[Load.MIN_PU_VOLTAGE], row[Load.MAX_PU_VOLTAGE])
				if row[Load.FUNCTIONAL_STATUS]*row[Load.OPERATIONAL_STATUS] == 0.0:
					dss.Command = 'Disable \'Load.{}\''.format(str_self_name)
			return 0
		except:
			print('Error: #-1225')
			return -1225

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
				dssCkt.Loads.Name = str(int(row[Load.TYPE])) + '_' + str(int(row[Load.ID])) + '_' + str(int(row[Load.A]))
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
			input_col_continuous = ['real_load', 'reactive_load']
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
			output_col = ['a_PU_voltage', 'a_current']
			
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
			rval = random.normalvariate(0, 0.5*self.matrix[row, Load.REAL_LOAD_MAX]*0.06)
			self.matrix[row, Load.REAL_LOAD] += rval
			if self.matrix[row, Load.REAL_LOAD] > self.matrix[row, Load.REAL_LOAD_MAX]:
				self.matrix[row, Load.REAL_LOAD] = self.matrix[row, Load.REAL_LOAD_MAX]
			elif self.matrix[row, Load.REAL_LOAD] < 0.0:
				self.matrix[row, Load.REAL_LOAD] = 0.0
		except:
			print('Error: #-1236')
			return -1236

	def randomSwitching(self):
		try:
			row = random.randrange(0, self.num_components)
			self.matrix[row, Load.OPERATIONAL_STATUS] = 0.0
		except:
			print('Error: #-1237')
			return -1237

	def multiplyLoadFactor(self, real_load_factor, reactive_load_factor):
		try:
			if real_load_factor < 0. or real_load_factor > 1. or reactive_load_factor < 0. or reactive_load_factor > 1.:
				print('Error: #DirectConnection')
			self.matrix[:, Load.REAL_LOAD] = self.matrix[:, Load.REAL_LOAD_MAX] * real_load_factor
			if reactive_load_factor == 0.:
				self.matrix[:, Load.REACTIVE_LOAD] = self.matrix[:, Load.REACTIVE_LOAD_MAX] * real_load_factor
			else:
				self.matrix[:, Load.REACTIVE_LOAD] = self.matrix[:, Load.REAL_LOAD] * (math.sqrt(1.0**2 - reactive_load_factor**2) / reactive_load_factor)
		except:
			print('Error: #-1238')
			return -1238

class SolarPV: #errors -1250 to -1274
	CLID = 1304

	ID = 0
	TYPE = 1 
	FUNCTIONAL_STATUS = 2 # switch
	NOMINAL_LL_VOLTAGE = 3
	A = 4
	CUT_IN_PERCENT = 5
	CUT_OUT_PERCENT = 6
	MIN_POWER_FACTOR = 7
	MODEL = 8
	PVEFF_CURVE_ID = 9
	PVTEMP_CURVE_ID = 10
	RATED_INVERTER = 11
	RATED_CAPACITY = 12
	WIRING = 13
	IRRADIANCE = 14 # stochastic
	MIN_PU_VOLTAGE = 15
	MAX_PU_VOLTAGE = 16
	OPERATIONAL_STATUS = 17 # switch
	POWER_FACTOR_CONTROL = 18 # stochastic
	A_PU_VOLTAGE = 19
	A_VOLTAGE = 20
	A_VOLTAGE_ANGLE = 21
	A_CURRENT = 22
	A_CURRENT_ANGLE = 23
	REAL_POWER = 24
	REACTIVE_POWER = 25

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

	def createAllDSS(self, dss, interconn_dict, debug):
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
						print('Disable \'PVSystem.{}\''.format(str_self_name))

				dss.Command = 'New \'PVSystem.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kva={:f} Pf=\'{:f}\' Model=\'{}\' Conn=\'{}\' Vminpu=\'{:f}\' Vmaxpu=\'{:f}\' %Cutin=\'{:f}\' %Cutout=\'{:f}\' Pmpp=\'{:f}\' Irradiance=\'{:f}\' EffCurve=\'{}_{}\' Temperature=\'{:f}\' P-TCurve=\'{}_{}\''.format(
					str_self_name, str_bus_name, str_bus_conn, num_phases,
					num_kv, row[SolarPV.RATED_INVERTER], row[SolarPV.POWER_FACTOR_CONTROL], int(row[SolarPV.MODEL]),
					str_conn, row[SolarPV.MIN_PU_VOLTAGE], row[SolarPV.MAX_PU_VOLTAGE], row[SolarPV.CUT_IN_PERCENT],
					row[SolarPV.CUT_OUT_PERCENT], row[SolarPV.RATED_CAPACITY], row[SolarPV.IRRADIANCE], XYCurve.CLID,
					int(row[SolarPV.PVEFF_CURVE_ID]), value_temperature, XYCurve.CLID, int(row[SolarPV.PVTEMP_CURVE_ID]))
				if row[SolarPV.FUNCTIONAL_STATUS]*row[SolarPV.OPERATIONAL_STATUS] == 0.0:
					dss.Command = 'Disable \'PVSystem.{}\''.format(str_self_name)
			return 0
		except:
			print('Error: #-1250')
			return -1250

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

				row[SolarPV.A_PU_VOLTAGE : SolarPV.REACTIVE_POWER+1] = 0.0

				if row[SolarPV.A] == 1.0:
					row[SolarPV.A_VOLTAGE] = var_volt_mag[idxcount*2]
					row[SolarPV.A_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[SolarPV.A_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[SolarPV.A_CURRENT] = var_curr[idxcount*2]
					row[SolarPV.A_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[SolarPV.REAL_POWER] += var_pow[idxcount*2]
					row[SolarPV.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
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
			output_col = ['a_PU_voltage', 'a_current']
			
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
	CUT_IN_SPEED = 7
	CUT_OUT_SPEED = 8
	MODEL = 9
	POWER_FACTOR = 10
	RATED_CAPACITY = 11
	RATED_SPEED = 12
	WIND_CURVE_ID = 15
	WIRING = 16
	WIND_SPEED = 17 # stochastic
	MIN_PU_VOLTAGE = 18
	MAX_PU_VOLTAGE = 19
	OPERATIONAL_STATUS = 20 # switch
	A_PU_VOLTAGE = 21
	A_VOLTAGE = 24
	A_VOLTAGE_ANGLE = 27
	A_CURRENT = 30
	A_CURRENT_ANGLE = 34
	REAL_POWER = 38
	REACTIVE_POWER = 39

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

	def createAllDSS(self, dss, interconn_dict, debug):
		try:
			for row in self.matrix:
				str_bus_conn = ''
				str_conn = 'wye'
				num_phases = 0
				num_kv = row[WindTurbine.NOMINAL_LL_VOLTAGE]

				if row[WindTurbine.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'
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
				str_bus_name = str(Bus.CLID) + '_' + str(int(row[WindTurbine.ID]))

				if debug == 1:
					print('New \'Generator.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Pf=\'{:f}\' Model=\'{}\' Conn=\'{}\'\n'.format(
					str_self_name, str_bus_name, str_bus_conn, num_phases,
					num_kv, gen_fraction*row[WindTurbine.RATED_CAPACITY], row[WindTurbine.POWER_FACTOR], int(row[WindTurbine.MODEL]),
					str_conn))
					if row[WindTurbine.FUNCTIONAL_STATUS]*row[WindTurbine.OPERATIONAL_STATUS] == 0.0:
						print('Disable \'Generator.{}\''.format(str_self_name))

				dss.Command = 'New \'Generator.{}\' Bus1=\'{}{}\' Phases=\'{}\' Kv=\'{:f}\' Kw=\'{:f}\' Pf=\'{:f}\' Model=\'{}\' Conn=\'{}\''.format(
					str_self_name, str_bus_name, str_bus_conn, num_phases,
					num_kv, gen_fraction*row[WindTurbine.RATED_CAPACITY], row[WindTurbine.POWER_FACTOR], int(row[WindTurbine.MODEL]),
					str_conn)
				if row[WindTurbine.FUNCTIONAL_STATUS]*row[WindTurbine.OPERATIONAL_STATUS] == 0.0:
						dss.Command = 'Disable \'Generator.{}\''.format(str_self_name)
			return 0
		except:
			print('Error: #-1275')
			return -1275

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
				dssCkt.SetActiveBus(str(Bus.CLID) + '_' + str(int(row[WindTurbine.ID])))
				dssCkt.Generators.Name = str(int(row[WindTurbine.TYPE])) + '_' + str(int(row[WindTurbine.ID]))
				var_volt_mag = list(dssActvBus.VMagAngle)
				var_volt_pu = list(dssActvBus.puVmagAngle)
				var_curr = list(dssActvElem.CurrentsMagAng)
				var_pow = list(dssActvElem.Powers)
				num_phases = dssActvElem.NumPhases
				num_conds = dssActvElem.NumConductors

				row[WindTurbine.A_PU_VOLTAGE : WindTurbine.REACTIVE_POWER+1] = 0.0

				if row[WindTurbine.A] == 1.0:
					row[WindTurbine.A_VOLTAGE] = var_volt_mag[idxcount*2]
					row[WindTurbine.A_VOLTAGE_ANGLE] = var_volt_mag[idxcount*2 + 1]
					row[WindTurbine.A_PU_VOLTAGE] = var_volt_pu[idxcount*2]
					row[WindTurbine.A_CURRENT] = var_curr[idxcount*2]
					row[WindTurbine.A_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[WindTurbine.REAL_POWER] += var_pow[idxcount*2]
					row[WindTurbine.REACTIVE_POWER] += var_pow[idxcount*2 + 1]
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
			# TO DO:
			return [], [], np.empty([0, 0], dtype=np.float64).flatten(), np.empty([0,0], dtype=np.float64).flatten()
		except:
			pass

	def convertToOutputTensor(self):
		try:
			# TO DO:
			return [], np.empty([0, 0], dtype=np.float64).flatten()
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
	ANGLE_DELTA_LIMIT = 6
	OPERATIONAL_STATUS = 7 # switch
	A_1_CURRENT = 8
	A_1_CURRENT_ANGLE = 9
	A_2_CURRENT = 10
	A_2_CURRENT_ANGLE = 11
	REAL_POWER_1 = 12
	REACTIVE_POWER_1 = 13
	REAL_POWER_2 = 14
	REACTIVE_POWER_2 = 15
	REAL_POWER_LOSSES = 16
	REACTIVE_POWER_LOSSES = 17
	ANGLE_DELTA = 18
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

	def createAllDSS(self, dss, interconn_dict, debug):
		try:
			for row in self.matrix:
				terminal_1_type = Bus.CLID
				terminal_2_type = Bus.CLID
				str_bus_conn = ''
				num_phases = 0

				if row[DirectConnection.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'
					num_phases += 1

				if str_bus_conn == '':
					print('Error: #-1401')

				str_self_name = str(int(row[DirectConnection.TYPE])) + '_' + str(int(row[DirectConnection.ID]))
				str_term1_name = str(terminal_1_type) + '_' + str(int(row[DirectConnection.TERMINAL_1_ID]))
				str_term2_name = str(terminal_2_type) + '_' + str(int(row[DirectConnection.TERMINAL_2_ID]))
				if row[DirectConnection.TERMINAL_1_ID] < 1:
					str_term1_name = 'sourcebus'
				elif row[DirectConnection.TERMINAL_2_ID] < 1:
					str_term2_name = 'sourcebus'

				if debug == 1:
					print('New \'Line.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' Phases=\'{}\' R0=\'{:f}\' R1=\'{:f}\' X0=\'{:f}\' X1=\'{:f}\' Length=\'{:f}\' Units=\'{}\' Normamps=\'{}\' Emergamps=\'{}\'\n'.format(
					str_self_name, str_term1_name, str_bus_conn, str_term2_name,
					str_bus_conn, num_phases, 0.00001, 0.00001,
					0.0001, 0.0001, 0.1, DirectConnection.UNITS,
					9999, 9999))

				dss.Command = 'New \'Line.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' Phases=\'{}\' R0=\'{:f}\' R1=\'{:f}\' X0=\'{:f}\' X1=\'{:f}\' Length=\'{:f}\' Units=\'{}\' Normamps=\'{}\' Emergamps=\'{}\''.format(
					str_self_name, str_term1_name, str_bus_conn, str_term2_name,
					str_bus_conn, num_phases, 0.00001, 0.00001,
					0.0001, 0.0001, 0.1, DirectConnection.UNITS,
					9999, 9999)
			return 0
		except:
			print('Error: #-1400')
			return -1400

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
				if num_conds > num_phases:
					# row[DirectConnection.N_1_CURRENT] = var_curr[idxcount*2]
					# row[DirectConnection.N_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
				if row[DirectConnection.A] == 1.0:
					row[DirectConnection.A_2_CURRENT] = var_curr[idxcount*2]
					row[DirectConnection.A_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[DirectConnection.REAL_POWER_2] += var_pow[idxcount*2]
					row[DirectConnection.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					# row[DirectConnection.N_2_CURRENT] = var_curr[idxcount*2]
					# row[DirectConnection.N_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1

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
			return [], [], np.empty([0, 0], dtype=np.float64).flatten(), np.empty([0,0], dtype=np.float64).flatten()
		except:
			pass

	def convertToOutputTensor(self):
		try:
			return [], np.empty([0, 0], dtype=np.float64).flatten()
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
	A = 5
	LENGTH = 6
	LINECODE_ID = 7
	ANGLE_DELTA_LIMIT = 8
	NORMAL_RATING = 9
	MAX_PU_CAPACITY = 10
	OPERATIONAL_STATUS_A = 1 # switch
	A_1_CURRENT = 12
	A_1_CURRENT_ANGLE = 13
	A_2_CURRENT = 14
	A_2_CURRENT_ANGLE = 15
	A_PU_CAPACITY = 16
	REAL_POWER_1 = 17
	REACTIVE_POWER_1 = 18
	REAL_POWER_2 = 19
	REACTIVE_POWER_2 = 20
	REAL_POWER_LOSSES = 21
	REACTIVE_POWER_LOSSES = 22
	ANGLE_DELTA = 23
	UNITS = 'ft'

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = int(self.matrix[:, Cable.A].sum()) * 1 # temporary
		self.num_stochastic = self.num_components * 0
		self.switch_chance = (0.0, 0.0)
		self.stochastic_chance = (0.0, 0.0)

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('POWER ERROR in Cable0')

	def createAllDSS(self, dss, interconn_dict, debug):
		try:
			for row in self.matrix:
				terminal_1_type = Bus.CLID
				terminal_2_type = Bus.CLID
				str_bus_conn = ''

				if row[Cable.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'

				#the correct thing to do would check this sum with the number of phases for the linecode
				if str_bus_conn == '':
					print('Error: #-1426')

				str_self_name = str(int(row[Cable.TYPE])) + '_' + str(int(row[Cable.ID]))
				str_term1_name = str(terminal_1_type) + '_' + str(int(row[Cable.TERMINAL_1_ID]))
				str_term2_name = str(terminal_2_type) + '_' + str(int(row[Cable.TERMINAL_2_ID]))
				str_linec_name = str(LineCode.CLID) + '_' + str(int(row[Cable.LINECODE_ID]))
				if row[Cable.TERMINAL_1_ID] < 1:
					str_term1_name = 'sourcebus'
				elif row[Cable.TERMINAL_2_ID] < 1:
					str_term2_name = 'sourcebus'

				if row[Cable.NORMAL_RATING] <= 100000.0:
					normal_amps = row[Cable.NORMAL_RATING] / 138.0
				else:
					normal_amps = row[Cable.NORMAL_RATING] / 230.0
				emerg_amps = normal_amps * row[Cable.MAX_PU_CAPACITY]

				if debug == 1:
					print('New \'Line.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' LineCode=\'{}\' Length=\'{:f}\' Units=\'{}\' Normamps=\'{:f}\' Emergamps=\'{:f}\'\n'.format(
					str_self_name, str_term1_name, str_bus_conn, str_term2_name,
					str_bus_conn, str_linec_name, row[Cable.LENGTH], Cable.UNITS,
					normal_amps, emerg_amps))
					if row[Cable.A] == 1.0 and row[Cable.FUNCTIONAL_STATUS_A]*row[Cable.OPERATIONAL_STATUS_A] == 0.0:
						print('Open \'Line.{}\' Term=1 1'.format(str_self_name))
						print('Open \'Line.{}\' Term=2 1'.format(str_self_name))

				dss.Command = 'New \'Line.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' LineCode=\'{}\' Length=\'{:f}\' Units=\'{}\' Normamps=\'{:f}\' Emergamps=\'{:f}\''.format(
					str_self_name, str_term1_name, str_bus_conn, str_term2_name,
					str_bus_conn, str_linec_name, row[Cable.LENGTH], Cable.UNITS,
					normal_amps, emerg_amps)
				if row[Cable.A] == 1.0 and row[Cable.FUNCTIONAL_STATUS_A]*row[Cable.OPERATIONAL_STATUS_A] == 0.0:
					dss.Command = 'Open \'Line.{}\' Term=1 1'.format(str_self_name)
					dss.Command = 'Open \'Line.{}\' Term=2 1'.format(str_self_name)
			return 0
		except:
			print('Error: #-1425')
			return -1425

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
				num_phases = dssActvElem.NumPhases
				num_conds = dssActvElem.NumConductors

				row[Cable.A_1_CURRENT : Cable.ANGLE_DELTA+1] = 0.0

				if row[Cable.A] == 1.0:
					row[Cable.A_1_CURRENT] = var_curr[idxcount*2]
					row[Cable.A_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Cable.REAL_POWER_1] += var_pow[idxcount*2]
					row[Cable.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					# row[Cable.N_1_CURRENT] = var_curr[idxcount*2]
					# row[Cable.N_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
				if row[Cable.A] == 1.0:
					row[Cable.A_2_CURRENT] = var_curr[idxcount*2]
					row[Cable.A_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Cable.REAL_POWER_2] += var_pow[idxcount*2]
					row[Cable.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					# row[Cable.N_2_CURRENT] = var_curr[idxcount*2]
					# row[Cable.N_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1

				row[Cable.REAL_POWER_LOSSES] = math.fabs(row[Cable.REAL_POWER_1] + row[Cable.REAL_POWER_2])
				row[Cable.REACTIVE_POWER_LOSSES] = math.fabs(row[Cable.REACTIVE_POWER_1] + row[Cable.REACTIVE_POWER_2])
				if emerg_power != 0.0:
					row[Cable.A_PU_CAPACITY] = 0.5*(row[Cable.REAL_POWER_2] - row[Cable.REAL_POWER_1]) / (row[Cable.NORMAL_RATING]*row[Cable.MAX_PU_CAPACITY])
				else:
					row[Cable.A_PU_CAPACITY] = 0.0
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
			input_col_categorical = ['operational_status_a']

			for row in self.matrix:
				for elem in input_col_categorical:
					input_list_categorical.append('Cable_' + str(int(row[Cable.ID])) + '_' + elem)

			inputdf = self.convertToDataFrame()
			inputdf_categorical = inputdf[input_col_categorical]
			return input_list_continuous, input_list_categorical, np.empty([0,0], dtype=np.float64).flatten(), inputdf_categorical.values.flatten()
		except:
			print('Error: #-1432')
			return -1432

	def convertToOutputTensor(self):
		try:
			output_list = []
			output_col = ['a_PU_capacity']

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
			ridx = random.randrange(1, int(self.matrix[:, Cable.OPERATIONAL_STATUS_A].sum())+1)
			tempval = 0
			for row in self.matrix:
				tempval += int(row[Cable.OPERATIONAL_STATUS_A].sum())
				if ridx <= tempval:
					while True:
						if row[Cable.OPERATIONAL_STATUS_A] != 1.0:
							print('Error: #-1434')
							break
						# rphase = random.randrange(0, 3)
						if row[Cable.OPERATIONAL_STATUS_A] == 1.0:
							row[Cable.OPERATIONAL_STATUS_A] = 0.0
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
	A = 5
	LENGTH = 6
	NEUTRAL_WIREDATA_ID = 7
	PHASE_WIREDATA_ID = 8
	SOIL_RESISTIVITY = 9
	X_A_COORDINATE = 10
	X_N_COORDINATE = 11
	H_A_COORDINATE = 12
	H_N_COORDINATE = 13
	ANGLE_DELTA_LIMIT = 14
	OPERATIONAL_STATUS_A = 15 # switch
	A_1_CURRENT = 16
	A_1_CURRENT_ANGLE = 17
	A_2_CURRENT = 18
	A_2_CURRENT_ANGLE = 19
	A_PU_CAPACITY = 20
	REAL_POWER_1 = 21
	REACTIVE_POWER_1 = 22
	REAL_POWER_2 = 23
	REACTIVE_POWER_2 = 24
	REAL_POWER_LOSSES = 25
	REACTIVE_POWER_LOSSES = 26
	ANGLE_DELTA = 27
	UNITS = 'ft'

	def __init__(self, dframe):
		self.cols = list(dframe.columns)
		self.matrix = dframe.values
		self.num_components = len(dframe.index)
		self.num_switches = int(self.matrix[:, OverheadLine.A].sum()) * 1 # temporary
		self.num_stochastic = self.num_components * 0
		self.switch_chance = (0.0, 0.0)
		self.stochastic_chance = (0.0, 0.0)

	def classValue(cls, str):
		try:
			return getattr(cls, str)
		except:
			print('POWER ERROR in OverheadLine0')

	def createAllDSS(self, dss, interconn_dict, debug):
		try:
			for row in self.matrix:
				terminal_1_type = Bus.CLID
				terminal_2_type = Bus.CLID
				str_bus_conn = ''
				num_phases = 0
				num_neutral = 1

				if row[OverheadLine.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'
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
				if row[OverheadLine.TERMINAL_1_ID] < 1:
					str_term1_name = 'sourcebus'
				elif row[OverheadLine.TERMINAL_2_ID] < 1:
					str_term2_name = 'sourcebus'

				if debug == 1:
					print('New \'LineGeometry.LG_{}\' Nconds=\'{}\' Nphases=\'{}\'\n'.format(
						int(row[OverheadLine.ID]), num_phases+num_neutral, num_phases))
					if row[OverheadLine.A] == 1.0:
						print('~ Cond=1 Wire=\'{}\' X=\'{:0.3f}\' H=\'{:0.3f}\' Units=\'{}\'\n'.format(
							str_pwire_name, row[OverheadLine.X_A_COORDINATE], row[OverheadLine.H_A_COORDINATE], OverheadLine.UNITS))
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
				if num_conds > num_phases:
					# row[OverheadLine.N_1_CURRENT] = var_curr[idxcount*2]
					# row[OverheadLine.N_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
				if row[OverheadLine.A] == 1.0:
					row[OverheadLine.A_2_CURRENT] = var_curr[idxcount*2]
					row[OverheadLine.A_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[OverheadLine.REAL_POWER_2] += var_pow[idxcount*2]
					row[OverheadLine.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					# row[OverheadLine.N_2_CURRENT] = var_curr[idxcount*2]
					# row[OverheadLine.N_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount +=1

				row[OverheadLine.REAL_POWER_LOSSES] = math.fabs(row[OverheadLine.REAL_POWER_1] + row[OverheadLine.REAL_POWER_2])
				row[OverheadLine.REACTIVE_POWER_LOSSES] = math.fabs(row[OverheadLine.REACTIVE_POWER_1] + row[OverheadLine.REACTIVE_POWER_2])

				row[OverheadLine.A_PU_CAPACITY] = 0.5 * (row[OverheadLine.A_1_CURRENT] + row[OverheadLine.A_2_CURRENT]) * norm_amps_inv
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
			# TO DO:
			return [], [], np.empty([0, 0], dtype=np.float64).flatten(), np.empty([0,0], dtype=np.float64).flatten()
		except:
			pass

	def convertToOutputTensor(self):
		try:
			# TO DO:
			return [], np.empty([0, 0], dtype=np.float64).flatten()
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
	MIN_TAP = 6
	MAX_TAP = 7
	R1 = 8
	RATED_CAPACITY = 9
	REGCONTROL_ID = 10
	TERMINAL_1_LL_VOLTAGE = 11
	TERMINAL_1_WIRING = 12
	TERMINAL_2_LL_VOLTAGE = 13
	TERMINAL_2_WIRING = 14
	X1 = 15
	ANGLE_DELTA_LIMIT = 16
	MAX_PU_CAPACITY = 17
	OPERATIONAL_STATUS = 18 # switch
	TAP_1 = 19 # stochastic
	TAP_2 = 20 # stochastic
	A_1_CURRENT = 21
	A_1_CURRENT_ANGLE = 22
	A_2_CURRENT = 23
	A_2_CURRENT_ANGLE = 24
	REAL_POWER_1 = 25
	REACTIVE_POWER_1 = 26
	REAL_POWER_2 = 27
	REACTIVE_POWER_2 = 28
	REAL_POWER_LOSSES = 29
	REACTIVE_POWER_LOSSES = 30
	ANGLE_DELTA = 31
	PU_CAPACITY = 32

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

	def createAllDSS(self, dss, interconn_dict, debug):
		try:
			for row in self.matrix:
				terminal_1_type = Bus.CLID
				terminal_2_type = Bus.CLID
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

				if row[TwoWindingTransformer.TERMINAL_1_WIRING] == 0.0:
					terminal_1_str_conn = 'delta'
					if num_phases == 1:
						print('Error: #-1475')
				if row[TwoWindingTransformer.TERMINAL_2_WIRING] == 0.0:
					terminal_2_str_conn = 'delta'
					if num_phases == 1:
						print('Error: #-1475')

				if num_phases == 0:
					print('Transformer {} has {} phases not {}'.format(row[TwoWindingTransformer.ID], num_phases, row[TwoWindingTransformer.A]))
					print('Error: #-1476')

				if num_phases == 1:
					terminal_1_num_kv = terminal_1_num_kv / math.sqrt(3.0)
					terminal_2_num_kv = terminal_2_num_kv / math.sqrt(3.0)

				str_self_name = str(int(row[TwoWindingTransformer.TYPE])) + '_' + str(int(row[TwoWindingTransformer.ID]))
				str_term1_name = str(terminal_1_type) + '_' + str(int(row[TwoWindingTransformer.TERMINAL_1_ID]))
				str_term2_name = str(terminal_2_type) + '_' + str(int(row[TwoWindingTransformer.TERMINAL_2_ID]))
				if row[TwoWindingTransformer.TERMINAL_1_ID] < 1:
					str_term1_name = 'sourcebus'
				elif row[TwoWindingTransformer.TERMINAL_2_ID] < 1:
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
					print('New \'Transformer.{}\' Phases=\'{}\' Windings=\'{}\' XHL=\'{:f}\' %R=\'{:f}\'\n'.format(
						str_self_name, num_phases, num_windings, row[TwoWindingTransformer.X1],
						row[TwoWindingTransformer.R1]))
					print('~ wdg=1 Bus=\'{}{}\' Kv=\'{:f}\' Tap=\'{:f}\' Kva=\'{:f}\' Conn=\'{}\'\n'.format(
						str_term1_name, str_bus_conn, terminal_1_num_kv, 1.0 + row[TwoWindingTransformer.TAP_1]*0.00625,
						row[TwoWindingTransformer.RATED_CAPACITY], terminal_1_str_conn))
					print('~ wdg=2 Bus=\'{}{}\' Kv=\'{:f}\' Tap=\'{:f}\' Kva=\'{:f}\' Conn=\'{}\'\n'.format(
						str_term2_name, str_bus_conn, terminal_2_num_kv, 1.0 + row[TwoWindingTransformer.TAP_2]*0.00625,
						row[TwoWindingTransformer.RATED_CAPACITY], terminal_2_str_conn))
					if row[TwoWindingTransformer.FUNCTIONAL_STATUS]*row[TwoWindingTransformer.OPERATIONAL_STATUS] == 0.0:
						print('Open \'Transformer.{}\' Term=1'.format(str_self_name))
						print('Open \'Transformer.{}\' Term=2'.format(str_self_name))

				dss.Command = 'New \'Transformer.{}\' Phases=\'{}\' Windings=\'{}\' XHL=\'{:f}\' %R=\'{:f}\''.format(
						str_self_name, num_phases, num_windings, row[TwoWindingTransformer.X1],
						row[TwoWindingTransformer.R1])
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
				if num_conds > num_phases:
					# row[TwoWindingTransformer.N_1_CURRENT] = var_curr[idxcount*2]
					# row[TwoWindingTransformer.N_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
				if row[TwoWindingTransformer.A] == 1.0:
					row[TwoWindingTransformer.A_2_CURRENT] = var_curr[idxcount*2]
					row[TwoWindingTransformer.A_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[TwoWindingTransformer.REAL_POWER_2] += var_pow[idxcount*2]
					row[TwoWindingTransformer.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					# row[TwoWindingTransformer.N_2_CURRENT] = var_curr[idxcount*2]
					# row[TwoWindingTransformer.N_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1

				row[TwoWindingTransformer.REAL_POWER_LOSSES] = math.fabs(row[TwoWindingTransformer.REAL_POWER_1] + row[TwoWindingTransformer.REAL_POWER_2])
				row[TwoWindingTransformer.REACTIVE_POWER_LOSSES] = math.fabs(row[TwoWindingTransformer.REACTIVE_POWER_1] + row[TwoWindingTransformer.REACTIVE_POWER_2])
				row[TwoWindingTransformer.PU_CAPACITY] = math.fabs(row[TwoWindingTransformer.A_1_CURRENT]) / (num_phases * norm_amps)
				# TO DO: fix above to 3x phase A current??
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
	NOMINAL_LL_VOLTAGE = 6
	REACTIVE_POWER_MIN_RATING = 7
	REACTIVE_POWER_MAX_RATING = 8
	WIRING = 9
	NUMBER_OF_STAGES = 10
	ANGLE_DELTA_LIMIT = 11
	MAX_PU_CAPACITY = 12
	STAGE_ONE = 13 # switch
	STAGE_TWO = 14 # switch
	STAGE_THREE = 15 # switch
	STAGE_FOUR = 16 # switch
	STAGE_FIVE = 17 # switch
	A_1_CURRENT = 18
	A_1_CURRENT_ANGLE = 19
	A_2_CURRENT = 20
	A_2_CURRENT_ANGLE = 21
	REAL_POWER_1 = 22
	REACTIVE_POWER_1 = 23
	REAL_POWER_2 = 24
	REACTIVE_POWER_2 = 25
	REAL_POWER_LOSSES = 26
	REACTIVE_POWER_LOSSES = 27
	ANGLE_DELTA = 28
	PU_CAPACITY = 29

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

	def createAllDSS(self, dss, interconn_dict, debug):
		try:
			for row in self.matrix:
				reactive_power_generation = row[Capacitor.REACTIVE_POWER_MIN_RATING]
				if row[Capacitor.REACTIVE_POWER_MAX_RATING] < row[Capacitor.REACTIVE_POWER_MIN_RATING]:
					print('Error: #1502')
				reactive_power_per_stage = math.fabs(row[Capacitor.REACTIVE_POWER_MAX_RATING] - row[Capacitor.REACTIVE_POWER_MIN_RATING]) / row[Capacitor.NUMBER_OF_STAGES]
				terminal_1_type = Bus.CLID
				bool_terminal_2 = False
				if row[Capacitor.TERMINAL_2_ID] > 0.0:
					terminal_2_type = Bus.CLID
					bool_terminal_2 = True

				num_kv = row[Capacitor.NOMINAL_LL_VOLTAGE]
				str_conn = 'wye'
				str_bus_conn = ''
				num_phases = 0

				if row[Capacitor.A] == 1.0:
					str_bus_conn = str_bus_conn + '.1'
					num_phases += 1

				if row[Capacitor.WIRING] == 0.0:
					str_conn = 'delta'
				elif num_phases == 1:
					num_kv = num_kv / math.sqrt(3.0)
				if num_phases == 0:
					print('Error: #-1501')

				if row[Capacitor.STAGE_ONE] == 1.0 and row[Capacitor.NUMBER_OF_STAGES] >= 1.0:
					reactive_power_generation += reactive_power_per_stage
					if row[Capacitor.STAGE_TWO] == 1.0 and row[Capacitor.NUMBER_OF_STAGES] >= 2.0:
						reactive_power_generation += reactive_power_per_stage
						if row[Capacitor.STAGE_THREE] == 1.0 and row[Capacitor.NUMBER_OF_STAGES] >= 3.0:
							reactive_power_generation += reactive_power_per_stage
							if row[Capacitor.STAGE_FOUR] == 1.0 and row[Capacitor.NUMBER_OF_STAGES] >= 4.0:
								reactive_power_generation += reactive_power_per_stage
								if row[Capacitor.STAGE_FIVE] == 1.0 and row[Capacitor.NUMBER_OF_STAGES] >= 5.0:
									reactive_power_generation += reactive_power_per_stage

				str_self_name = str(int(row[Capacitor.TYPE])) + '_' + str(int(row[Capacitor.ID]))
				str_term1_name = str(terminal_1_type) + '_' + str(int(row[Capacitor.TERMINAL_1_ID]))
				if row[Capacitor.TERMINAL_1_ID] < 1:
					str_term1_name = 'sourcebus'
				if bool_terminal_2 == True:
					str_term2_name = str(terminal_2_type) + '_' + str(int(row[Capacitor.TERMINAL_2_ID]))
					if row[Capacitor.TERMINAL_2_ID] < 1:
						str_term2_name = 'sourcebus'

				if debug == 1:
					if bool_terminal_2 == True:
						print('New \'Capacitor.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' Phases={} Kvar=\'{:f}\' Kv=\'{:f}\' Conn=\'{}\'\n'.format(
							str_self_name, str_term1_name, str_bus_conn, str_term2_name,
							str_bus_conn, num_phases, reactive_power_generation, num_kv,
							str_conn))
					else:
						print('New \'Capacitor.{}\' Bus1=\'{}{}\' Phases={} Kvar=\'{:f}\' Kv=\'{:f}\' Conn=\'{}\'\n'.format(
							str_self_name, str_term1_name, str_bus_conn, num_phases,
							reactive_power_generation, num_kv, str_conn))
					if row[Capacitor.FUNCTIONAL_STATUS] == 0.0:
						print('Open \'Capacitor.{}\' Term=1'.format(str_self_name))
						print('Open \'Capacitor.{}\' Term=2'.format(str_self_name))

				if bool_terminal_2 == True:
					dss.Command = 'New \'Capacitor.{}\' Bus1=\'{}{}\' Bus2=\'{}{}\' Phases={} Kvar=\'{:f}\ Kv=\'{:f}\' Conn=\'{}\''.format(
							str_self_name, str_term1_name, str_bus_conn, str_term2_name,
							str_bus_conn, num_phases, reactive_power_generation, num_kv,
							str_conn)
				else:
					dss.Command = 'New \'Capacitor.{}\' Bus1=\'{}{}\' Phases={} Kvar=\'{:f}\' Kv=\'{:f}\' Conn=\'{}\''.format(
							str_self_name, str_term1_name, str_bus_conn, num_phases,
							reactive_power_generation, num_kv, str_conn)
				if row[Capacitor.FUNCTIONAL_STATUS] == 0.0:
					dss.Command = 'Open \'Capacitor.{}\' Term=1'.format(str_self_name)
					dss.Command = 'Open \'Capacitor.{}\' Term=2'.format(str_self_name)
			return 0
		except:
			print('Error: #-1500')
			return -1500

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
				norm_amps = math.sqrt(3.0) * max(math.fabs(row[Capacitor.REACTIVE_POWER_MAX_RATING]), math.fabs(row[Capacitor.REACTIVE_POWER_MIN_RATING])) / (num_phases * row[Capacitor.NOMINAL_LL_VOLTAGE])
				row[Capacitor.A_1_CURRENT : Capacitor.PU_CAPACITY+1] = 0.0

				if row[Capacitor.A] == 1.0:
					row[Capacitor.A_1_CURRENT] = var_curr[idxcount*2]
					row[Capacitor.A_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Capacitor.REAL_POWER_1] += var_pow[idxcount*2]
					row[Capacitor.REACTIVE_POWER_1] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					# row[Capacitor.N_1_CURRENT] = var_curr[idxcount*2]
					# row[Capacitor.N_1_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1
				if row[Capacitor.A] == 1.0:
					row[Capacitor.A_2_CURRENT] = var_curr[idxcount*2]
					row[Capacitor.A_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					row[Capacitor.REAL_POWER_2] += var_pow[idxcount*2]
					row[Capacitor.REACTIVE_POWER_2] += var_pow[idxcount*2 + 1]
					idxcount += 1
				if num_conds > num_phases:
					# row[Capacitor.N_2_CURRENT] = var_curr[idxcount*2]
					# row[Capacitor.N_2_CURRENT_ANGLE] = var_curr[idxcount*2 + 1]
					idxcount += 1

				row[Capacitor.REAL_POWER_LOSSES] = math.fabs(row[Capacitor.REAL_POWER_1] + row[Capacitor.REAL_POWER_2])
				row[Capacitor.REACTIVE_POWER_LOSSES] = math.fabs(row[Capacitor.REACTIVE_POWER_1] + row[Capacitor.REACTIVE_POWER_2])

				row[Capacitor.PU_CAPACITY] = (math.fabs(row[Capacitor.A_1_CURRENT]) + math.fabs(row[Capacitor.A_2_CURRENT])) / (2.0 * num_phases * norm_amps)
					# TO DO: fix above to 3x phase a current?
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
			input_col_categorical = ['stage_one', 'stage_two', 'stage_three', 'stage_four', 'stage_five']

			for row in self.matrix:
				for elem in input_col_categorical:
					input_list_categorical.append('Capacitor_' + str(int(row[Capacitor.ID])) + '_' + elem)

			inputdf = self.convertToDataFrame()
			inputdf_categorical = inputdf[input_col_categorical]
			return input_list_continuous, input_list_categorical, np.empty([0,0], dtype=np.float64).flatten(), inputdf_categorical.values.flatten()
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
	NOMINAL_LL_VOLTAGE = 6
	NORMAL_AMPS = 7
	R1 = 8
	RATED_REACTIVE_POWER = 9
	ANGLE_DELTA_LIMIT = 10
	MAX_PU_CAPACITY = 11
	OPERATIONAL_STATUS = 12 # switch
	A_1_CURRENT = 13
	A_1_CURRENT_ANGLE = 14
	A_2_CURRENT = 15
	A_2_CURRENT_ANGLE = 16
	REAL_POWER_1 = 17
	REACTIVE_POWER_1 = 18
	REAL_POWER_2 = 19
	REACTIVE_POWER_2 = 20
	REAL_POWER_LOSSES = 21
	REACTIVE_POWER_LOSSES = 22
	ANGLE_DELTA = 23
	PU_CAPACITY = 24

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

	def createAllDSS(self, dss, interconn_dict, debug):
		try:
			# TO DO:
			return 0
		except:
			print('Error: #-1525')
			return -1525

	def voltagesToSets(self):
		return set()

	def readAllDSSOutputs(self, dssCkt, dssActvElem, dssActvBus, var_bus, var_volt_mag, var_volt_pu, var_curr, var_pow):
		try:
			# TO DO:
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
			# TO DO:
			return [], [], np.empty([0, 0], dtype=np.float64).flatten(), np.empty([0,0], dtype=np.float64).flatten()
		except:
			pass

	def convertToOutputTensor(self):
		try:
			# TO DO:
			return [], np.empty([0, 0], dtype=np.float64).flatten()
		except:
			pass

	def randomStochasticity(self):
		# TO DO:
		pass

	def randomSwitching(self):
		# TO DO:
		pass