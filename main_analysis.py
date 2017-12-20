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

import ctypes as ct
import pandas as pd
import numpy as np
import random, csv, sys, os
import math
import time

from statistics import median

import classes_water as ENC
import classes_power as ODC
import classes_interconnection as ICC
import grb_solvers

from comtypes import automation
import win32com.client
# from win32com.client import makepy
# sys.argv = ['makepy', 'OpenDSSEngine.DSS']
# makepy.main()

from operator import itemgetter

def main(dss_debug, write_cols, power_df, water_df):
	idx_tank_15 = 11
	flag_water_power_worst_case = 0

	tank_15_w = 0.0
	tank_16_w = 0.0
	tank_18_w = 0.0
	tank_19_w = 0.0

	tank_15_p_w = 0.0
	tank_16_p_w = 0.0
	tank_18_p_w = 0.0
	tank_19_p_w = 0.0

	pipe_9_deficits_w_n1 = 0.0
	pipe_9_deficits_pw_n1 = 0.0

	os_username = os.getlogin()

	# --------------
	# READ CSV FILES
	# --------------

	csv_curve = pd.read_csv('./data_water/network-water/2000curve.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_junction = pd.read_csv('./data_water/network-water/2100junction.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_reservoir = pd.read_csv('./data_water/network-water/2101reservoir.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_tank = pd.read_csv('./data_water/network-water/2102tank.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_pipe = pd.read_csv('./data_water/network-water/2200pipe.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_pump = pd.read_csv('./data_water/network-water/2201pump.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_valve = pd.read_csv('./data_water/network-water/2202valve.csv', sep=',', header=1, index_col=None, dtype=np.float64)

	csv_xycurve = pd.read_csv('./data_power/network-power/1000xycurve.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_regcontrol = pd.read_csv('./data_power/network-power/1100regcontrol.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_wiredata = pd.read_csv('./data_power/network-power/1200wiredata.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_linecode = pd.read_csv('./data_power/network-power/1201linecode.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_bus = pd.read_csv('./data_power/network-power/1300bus.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_vsource = pd.read_csv('./data_power/network-power/1301vsource.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_generator = pd.read_csv('./data_power/network-power/1302generator.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_load = pd.read_csv('./data_power/network-power/1303load.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_solarpv = pd.read_csv('./data_power/network-power/1304solarpv.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_windturbine = pd.read_csv('./data_power/network-power/1305windturbine.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_directconnection = pd.read_csv('./data_power/network-power/1400directconnection.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_cable = pd.read_csv('./data_power/network-power/1401cable.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_overheadline = pd.read_csv('./data_power/network-power/1402overheadline.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_twowindingtransformer = pd.read_csv('./data_power/network-power/1403twowindingtransformer.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_capacitor = pd.read_csv('./data_power/network-power/1404capacitor.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_reactor = pd.read_csv('./data_power/network-power/1405reactor.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	# csv_allcolumns= pd.read_csv('./data_power/network-power/allcolumns.csv', sep=',', header=1, index_col=None, dtype=np.float64)

	# -----------------
	# CREATE COMPONENTS
	# -----------------

	object_curve = ENC.Curve(csv_curve)
	object_junction = ENC.Junction(csv_junction)
	object_reservoir = ENC.Reservoir(csv_reservoir)
	object_tank = ENC.Tank(csv_tank)
	object_pipe = ENC.Pipe(csv_pipe)
	object_pump = ENC.Pump(csv_pump)
	object_valve = ENC.Valve(csv_valve)

	object_xycurve = ODC.XYCurve(csv_xycurve)
	object_regcontrol = ODC.RegControl(csv_regcontrol)
	object_wiredata = ODC.WireData(csv_wiredata)
	object_linecode = ODC.LineCode(csv_linecode)
	object_bus = ODC.Bus(csv_bus)
	object_vsource = ODC.VSource(csv_vsource)
	object_generator = ODC.Generator(csv_generator)
	object_load = ODC.Load(csv_load)
	object_solarpv = ODC.SolarPV(csv_solarpv)
	object_windturbine = ODC.WindTurbine(csv_windturbine, object_xycurve)
	object_directconnection = ODC.DirectConnection(csv_directconnection)
	object_cable = ODC.Cable(csv_cable)
	object_overheadline = ODC.OverheadLine(csv_overheadline)
	object_twowindingtransformer = ODC.TwoWindingTransformer(csv_twowindingtransformer)
	object_capacitor = ODC.Capacitor(csv_capacitor)
	object_reactor = ODC.Reactor(csv_reactor)

	# -----------------------
	# ADD COMPONENTS TO LISTS
	# -----------------------

	w_object_list = [object_junction, object_reservoir, object_tank, # Water NODES
	object_pipe, object_pump, object_valve, # Water LINKS
	object_curve] # Water SYSTEM OPS

	object_list = [object_vsource, object_bus, object_generator, object_load, object_solarpv, object_windturbine, #NODES
	object_xycurve, object_wiredata, object_linecode, #OTHERS
	object_directconnection, object_cable, object_overheadline, object_twowindingtransformer, object_capacitor, object_reactor, # CONNECTIONS
	object_regcontrol] # CONTROLS

	interconn_dict = {'generator': object_generator, 'load': object_load, 'pump': object_pump, 'junction': object_junction}

	# ---------
	# RUN EPANET and OPENDSS
	# ---------

	def run_EPANET():
		filedir = 'C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/data_water/en-inputs/en-input.inp'
		with open(filedir, 'w', newline='\n') as csvfile:
			writer = csv.writer(csvfile, delimiter=' ')
			templist = ['[TITLE]']
			writer.writerow(templist)
			writer.writerow('')

			for water_object in w_object_list:
				water_object.createAllEN(writer, interconn_dict)

			templist = ['[ENERGY]']
			writer.writerow(templist)
			templist = ['Global', 'Efficiency', 75]
			writer.writerow(templist)
			templist = ['Global', 'Price', 0]
			writer.writerow(templist)
			templist = ['Demand', 'Charge', 0]
			writer.writerow(templist)
			writer.writerow('')

			templist = ['[REACTIONS]']
			writer.writerow(templist)
			templist = ['Order', 'Bulk', 1]
			writer.writerow(templist)
			templist = ['Order', 'Tank', 1]
			writer.writerow(templist)
			templist = ['Order', 'Wall', 1]
			writer.writerow(templist)
			templist = ['Global', 'Bulk', 0]
			writer.writerow(templist)
			templist = ['Global', 'Wall', 0]
			writer.writerow(templist)
			templist = ['Limiting', 'Potential', 0]
			writer.writerow(templist)
			templist = ['Roughness', 'Correlation', 0]
			writer.writerow(templist)
			writer.writerow('')

			templist = ['[TIMES]']
			writer.writerow(templist)
			templist = ['Duration', '1:00']
			writer.writerow(templist)
			templist = ['Hydraulic', 'Timestep', '1:00']
			writer.writerow(templist)
			templist = ['Quality', 'Timestep', '0:06']
			writer.writerow(templist)
			templist = ['Pattern', 'Timestep', '1:00']
			writer.writerow(templist)
			templist = ['Pattern', 'Start', '0:00']
			writer.writerow(templist)
			templist = ['Report', 'Timestep', '1:00']
			writer.writerow(templist)
			templist = ['Report', 'Start', '0:00']
			writer.writerow(templist)
			templist = ['Start', 'ClockTime', 12, 'am']
			writer.writerow(templist)
			templist = ['Statistic', 'NONE']
			writer.writerow(templist)
			writer.writerow('')

			templist = ['[REPORT]']
			writer.writerow(templist)
			templist = ['Status', 'No']
			writer.writerow(templist)
			templist = ['Summary', 'No']
			writer.writerow(templist)
			templist = ['Page', 0]
			writer.writerow(templist)
			writer.writerow('')

			templist = ['[OPTIONS]']
			writer.writerow(templist)
			templist = ['Units', 'GPM'] #GPM is US Customary units
			writer.writerow(templist)
			templist = ['Headloss', 'C-M']
			writer.writerow(templist)
			templist = ['Specific', 'Gravity', 1]
			writer.writerow(templist)
			templist = ['Viscosity', 1]
			writer.writerow(templist)
			templist = ['Trials', 40]
			writer.writerow(templist)
			templist = ['Accuracy', 0.001]
			writer.writerow(templist)
			templist = ['CHECKFREQ', 2]
			writer.writerow(templist)
			templist = ['MAXCHECK', 10]
			writer.writerow(templist)
			templist = ['DAMPLIMIT', 0]
			writer.writerow(templist)
			templist = ['Unbalanced', 'Continue', 10]
			writer.writerow(templist)
			templist = ['Pattern', 1]
			writer.writerow(templist)
			templist = ['Demand', 'Multiplier', 1.0]
			writer.writerow(templist)
			templist = ['Emitter', 'Exponent', 0.5]
			writer.writerow(templist)
			templist = ['Quality', 'None', 'mg/L']
			writer.writerow(templist)
			templist = ['Diffusivity', 1]
			writer.writerow(templist)
			templist = ['Tolerance', 0.01]
			writer.writerow(templist)
			writer.writerow('')

			templist=['[END]']
			writer.writerow(templist)

		epalib = ct.cdll.LoadLibrary('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/data_water/epanet2mingw64.dll')

		# Byte objects
		en_input_file = ct.c_char_p(filedir.encode('utf-8'))
		en_report_file = ct.c_char_p(str('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/data_water/en-outputs/out.rpt').encode('utf-8'))
		en_byte_file = ct.c_char_p(''.encode('utf-8'))

		# Send strings as char* to the epalib function
		errorcode = epalib.ENopen(en_input_file, en_report_file, en_byte_file)
		if errorcode != 0:
			print(1, 'ERRORCODE is', errorcode)

		errorcode = epalib.ENopenH()
		if errorcode != 0:
			print(2, 'ERRORCODE is', errorcode)

		init_flag = ct.c_int(0)
		errorcode = epalib.ENinitH(init_flag)
		if errorcode != 0:
			print(3, 'ERRORCODE is', errorcode)

		time = ct.pointer(ct.c_long(1))
		timestep = ct.pointer(ct.c_long(1))
		while True:
			errorcode = epalib.ENrunH(time)
			# if errorcode != 0:
			# 	print(4, 'ERRORCODE is', errorcode)

			errorcode = epalib.ENnextH(timestep)
			if errorcode != 0:
				print(5, 'ERRORCODE is', errorcode)

			if timestep.contents.value == 0:
				break

		for water_object in w_object_list:
			water_object.readAllENoutputs(epalib)

			if water_object.CLID == 2102:
				for tank in water_object.matrix:
					calc_tank_GPM = math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD]) / (60*60*0.002228)
					max_tank_GPM = math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.INITIAL_LEVEL]) / (60*60*0.002228)
					
					if calc_tank_GPM < -0.03 or calc_tank_GPM > max_tank_GPM + 0.03:
						print('Tank GPM error', calc_tank_GPM, max_tank_GPM)
					
					# if tank[ENC.Tank.DEMAND] != 0.0:
					# 	print('Tank', tank[ENC.Tank.ID]-1000.0, 'actual GPM demand', tank[ENC.Tank.DEMAND], 'calculated GPM demand', math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD]) / (60*60*0.002228), 'max GPM demand', math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.INITIAL_LEVEL]) / (60*60*0.002228))

			# if water_object.CLID == 2100:
			# 	for junction in water_object.matrix:
			# 		print('Junction', junction[ENC.Junction.ID], 'has pressure', junction[ENC.Junction.PRESSURE], junction[ENC.Junction.PERCENT_PRESSURE])
			# 		if math.fabs(junction[ENC.Junction.DEMAND] - junction[ENC.Junction.BASE_DEMAND]) > 1.0:
			# 			print('junction', junciton[ENC.Junction.ID], 'has demand ratio of', junction[ENC.Junction.DEMAND] / junction[ENC.Junction.BASE_DEMAND])

			# if water_object.CLID == 2101:
			# 	for reservoir in water_object.matrix:
			# 		if reservoir[ENC.Reservoir.DEMAND] != 0.0:
			# 			print('Reservoir', reservoir[ENC.Reservoir.ID], 'has GPM flow of', reservoir[ENC.Reservoir.DEMAND])

		errorcode = epalib.ENcloseH()
		if errorcode != 0:
			print(6, 'ERRORCODE is', errorcode)

		errorcode = epalib.ENclose()
		if errorcode != 0:
			print(7, 'ERRORCODE is', errorcode)

		input_list_continuous = []
		input_list_categorical = []
		input_tensor_continuous = np.empty([0,0], dtype=np.float64).flatten()
		input_tensor_categorical = np.empty([0,0], dtype=np.float64).flatten()
		for object in w_object_list:
			list_continuous, list_categorical, tensor_continuous, tensor_categorical = object.convertToInputTensor()
			input_list_continuous = input_list_continuous + list_continuous
			input_list_categorical = input_list_categorical + list_categorical
			input_tensor_continuous = np.concatenate((input_tensor_continuous, tensor_continuous), axis=0)
			input_tensor_categorical = np.concatenate((input_tensor_categorical, tensor_categorical), axis=0)

		output_list = []
		output_tensor = np.empty([0,0], dtype=np.float64).flatten()
		for object in w_object_list:
			o_list, o_tensor = object.convertToOutputTensor()
			output_list = output_list + o_list
			output_tensor = np.concatenate((output_tensor, o_tensor), axis=0)

		return input_list_continuous, input_list_categorical, output_list, input_tensor_continuous, input_tensor_categorical, output_tensor

	def run_OpenDSS(dss_debug, solverFlag):
		# SET SOURCEBUS
		# VsourceClass.sourcebus = vsourceobj.id[1]
		dssObj = win32com.client.Dispatch('OpenDSSEngine.DSS') # OPENDSS COMPORT

		dssObj.AllowForms = False
		dssText = dssObj.Text
		dssCkt = dssObj.ActiveCircuit
		dssSolution = dssCkt.Solution
		dssActvElem = dssCkt.ActiveCktElement
		dssActvBus = dssCkt.ActiveBus

		dssText.Command = 'Clear'

		dssText.Command = 'Set DataPath=\'C:\\Users\\'+os_username+'\\Documents\\OpenDSS'
		dssText.Command = 'Set DefaultBaseFrequency=60'

		for object in object_list:
			object.createAllDSS(dssText, interconn_dict, dss_debug)

		set_voltagebase = set()
		for object in object_list:
			set_voltagebase = set_voltagebase | object.voltagesToSets()

		dssText.Command = 'Set VoltageBases={}'.format(list(set_voltagebase))
		dssText.Command = 'CalcVoltageBases'
		dssText.Command = 'Solve BaseFrequency=60 MaxIter=300'

		variant_buses = automation.VARIANT()
		variant_voltages_mag = automation.VARIANT()
		variant_voltages_pu = automation.VARIANT()
		variant_currents = automation.VARIANT()
		variant_powers = automation.VARIANT()

		for object in object_list:
			object.readAllDSSOutputs(dssCkt, dssActvElem, dssActvBus, variant_buses, variant_voltages_mag, variant_voltages_pu, variant_currents, variant_powers)

		if solverFlag == False:
			# dssText.Command = 'Save Circuit'
			# dssText.Command = 'Export Summary (summary.csv)'
			# dssText.Command = 'Export Currents (currents.csv)'
			# dssText.Command = 'Export Voltages (voltages.csv)'
			# dssText.Command = 'Export Overloads (overloads.csv)'
			# dssText.Command = 'Export Powers kVA (powers.csv)'

			input_list_continuous = []
			input_list_categorical = []
			input_tensor_continuous = np.empty([0,0], dtype=np.float64).flatten()
			input_tensor_categorical = np.empty([0,0], dtype=np.float64).flatten()
			for object in object_list:
				list_continuous, list_categorical, tensor_continuous, tensor_categorical = object.convertToInputTensor()
				input_list_continuous = input_list_continuous + list_continuous
				input_list_categorical = input_list_categorical + list_categorical
				input_tensor_continuous = np.concatenate((input_tensor_continuous, tensor_continuous), axis=0)
				input_tensor_categorical = np.concatenate((input_tensor_categorical, tensor_categorical), axis=0)

			output_list = []
			output_tensor = np.empty([0,0], dtype=np.float64).flatten()
			for object in object_list:
				o_list, o_tensor = object.convertToOutputTensor()
				output_list = output_list + o_list
				output_tensor = np.concatenate((output_tensor, o_tensor), axis=0)

			return input_list_continuous, input_list_categorical, output_list, input_tensor_continuous, input_tensor_categorical, output_tensor
		else:
			losses = dssCkt.Losses
			return float(losses[0])*0.001 # kW


	# SIM STEP 1: SET LOAD AND DEMAND CURVES
	# ------------------------------
	power_load_mu = -0.51385 # lognormal, AIC -9693.48
	power_load_sigma = 0.23256 # lognormal, AIC -9693.48
	power_load_lb = 0.3388
	power_load_ub = 1.0
	power_load_factor = min(np.random.lognormal(power_load_mu, power_load_sigma, size=None), power_load_ub)
	power_load_factor = max(power_load_factor, power_load_lb)
	power_factor = 0.0
	power_load_factor = power_df
	object_load.multiplyLoadFactor(power_load_factor, power_factor)
	print('power load factor', power_load_factor)

	water_demand_scale = np.exp(-0.4559995) # exponential, AIC = 314.27
	water_demand_lb = 0.372453
	water_demand_ub = 2.984
	water_demand_factor = min(water_demand_lb+np.random.exponential(water_demand_scale, size=None), water_demand_ub)
	water_demand_factor = water_df
	object_junction.multiplyLoadFactor(water_demand_factor)
	print('water demand factor', water_demand_factor)

	for row in object_reservoir.matrix:
		if row[ENC.Reservoir.ID] < 1000.0:
			row[ENC.Reservoir.TOTAL_HEAD] = max(1.0, water_demand_factor) * row[ENC.Reservoir.TOTAL_HEAD]

	# SIM STEP 2: SET LOAD INTERCONNECTIONS
	# ----------------------------------
	object_load.setInterconnectionLoad(interconn_dict)

	# SIM STEP 3: SET GENERATOR DISPATCH
	# ----------------------------------
	exports = 0.0 # kW
	losses = 0.0 # kW

	# def fun_set_power_dispatch(object_load, object_generator, losses, exports):
	# 	counter = 0
	# 	lost_min = 10000000.0
	# 	while True:
	# 		grb_solvers.unit_commitment_priority_list(object_load, object_generator, losses, exports) # unit commitment is variable
	# 		new_loss = run_OpenDSS(0, True)
	# 		counter += 1

	# 		if math.fabs(losses - new_loss) > 1.0:
	# 			if counter > 199:
	# 				print('Dispatcher - Losses/Exports did not converge')
	# 				sys.exit()
	# 			elif counter > 150:
	# 				while True:
	# 					object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = dispatcher_max
	# 					grb_solvers.unit_commitment_priority_list_2(object_load, object_generator, losses, exports) # unit commitment is input
	# 					new_loss = run_OpenDSS(0, True)
	# 					counter +=1

	# 					if math.fabs(losses - new_loss) < 1.0:
	# 						return 0
	# 					else:
	# 						losses += 0.8 * (new_loss - losses)
	# 			elif counter > 100:
	# 				while True:
	# 					object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = dispatcher_min
	# 					grb_solvers.unit_commitment_priority_list_2(object_load, object_generator, losses, exports) # unit commitment is input
	# 					new_loss = run_OpenDSS(0, True)
	# 					counter +=1

	# 					if math.fabs(losses - new_loss) < 1.0:
	# 						return 0
	# 					else:
	# 						losses += 0.8 * (new_loss - losses)
	# 			elif counter > 50:
	# 				if math.fabs(new_loss) < math.fabs(lost_min):
	# 					lost_min = new_loss
	# 					dispatcher_min = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
	# 				else:
	# 					dispatcher_max = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
	# 			losses += 0.8*(new_loss - losses)
	# 		else:
	# 			return 0

	node_list_constraint = []
	node_water_constraint = {1.0: 0.0,
	2.0: 0.0,
	7.0: 0.0,
	13.0: 0.0,
	15.0: 0.0,
	16.0: 0.0,
	18.0: 0.0,
	22.0: 0.0,
	33.0: 0.0}
	
	def fun_set_power_dispatch(object_load, object_generator, losses, exports):
		counter = 0
		lost_min = 10000000.0
		while True:
			grb_solvers.unit_commitment_priority_list_water(object_load, object_generator, losses, exports, node_list_constraint, node_water_constraint) # unit commitment is variable
			new_loss = run_OpenDSS(0, True)
			counter += 1
			# print(counter)

			if math.fabs(losses - new_loss) > 1.0:
				if counter > 199:
					print('Dispatcher - Losses/Exports did not converge')
					sys.exit()
				elif counter > 150:
					while True:
						object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = dispatcher_max
						grb_solvers.unit_commitment_priority_list_water_2(object_load, object_generator, losses, exports, node_list_constraint, node_water_constraint) # unit commitment is input
						new_loss = run_OpenDSS(0, True)
						counter +=1

						if math.fabs(losses - new_loss) < 1.0:
							return 0
						else:
							losses += 0.8 * (new_loss - losses)
				elif counter > 100:
					while True:
						object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = dispatcher_min
						grb_solvers.unit_commitment_priority_list_water_2(object_load, object_generator, losses, exports, node_list_constraint, node_water_constraint) # unit commitment is input
						new_loss = run_OpenDSS(0, True)
						counter +=1

						if math.fabs(losses - new_loss) < 1.0:
							return 0
						else:
							losses += 0.8 * (new_loss - losses)
				elif counter > 50:
					if math.fabs(new_loss) < math.fabs(lost_min):
						lost_min = new_loss
						dispatcher_min = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
					else:
						dispatcher_max = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
				losses += 0.8*(new_loss - losses)
			else:
				return 0

	fun_set_power_dispatch(object_load, object_generator, losses, exports)
	print('exports #1', 0.5 * (object_cable.matrix[33, ODC.Cable.REAL_POWER_2] - object_cable.matrix[33, ODC.Cable.REAL_POWER_1]))
	print('')

	# SIM STEP 4: SET JUNCTION INTERCONNECTIONS
	# -----------------------------------------
	object_junction.setInterconnectionDemand(interconn_dict)

	# SIM STEP 5:
	# Set water tank levels
	# Set water valve flow control
	# ----------------------------
	object_tank.matrix[:, ENC.Tank.INITIAL_LEVEL] = 0.0
	object_tank.matrix[:, ENC.Tank.MAX_LEVEL] = 0.0

	for junction in object_junction.matrix:
		max_groundwater_flow = 12399.0

		for tank in object_tank.matrix:
			if tank[ENC.Tank.ID] - 1000.0 == junction[ENC.Junction.ID]:
				level_inc = round(junction[ENC.Junction.BASE_DEMAND]*60.0*0.133681 / (math.pi * (0.5*tank[ENC.Tank.DIAMETER])**2), 2)
				tank[ENC.Tank.INITIAL_LEVEL] += level_inc
				tank[ENC.Tank.MAX_LEVEL] += level_inc

				for generator in object_generator.matrix:
					if generator[ODC.Generator.JUNCTION_ID] == junction[ENC.Junction.ID]:
						level_inc = round(generator[ODC.Generator.OPERATIONAL_STATUS]*generator[ODC.Generator.REAL_GENERATION]*generator[ODC.Generator.WATER_CONSUMPTION]*0.001*60*0.133681 / (math.pi * (0.5*tank[ENC.Tank.DIAMETER])**2), 2)
						tank[ENC.Tank.INITIAL_LEVEL] += level_inc
						tank[ENC.Tank.MAX_LEVEL] += level_inc

		for valve in object_valve.matrix:
			if valve[ENC.Valve.ID] - 2000.0 == junction[ENC.Junction.ID]:
				# valve[ENC.Valve.SETTING] = min(junction[ENC.Junction.BASE_DEMAND], max_groundwater_flow)
				valve[ENC.Valve.SETTING] = max_groundwater_flow

	# ANALYSIS STEP 5: Water N-1 and track base worst-case
	# ----------------------------------------------------
	worst_case_system_deficit = 0.0
	worst_case_subset_deficit = 0.0
	worst_case_subset_deficit_priority = []

	system_deficit = 0.0
	temp_system_deficit = 0.0

	subset_junction = [1.0, 2.0, 7.0, 13.0, 15.0, 16.0, 18.0, 33.0]
	subset_deficit = 0.0
	subset_deficit_priority = []
	temp_subset_deficit = 0.0
	temp_subset_deficit_priority = []

	base_pipe_status = np.array(object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS], copy=True)
	base_tank_matrix = np.array(object_tank.matrix, copy=True)

	for row in object_pipe.matrix:
		if row[ENC.Pipe.ID] < 1000.0:
			# print('SHUT DOWN PIPE:', row[ENC.Pipe.ID])

			object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
			object_tank.matrix = base_tank_matrix

			row[ENC.Pipe.OPERATIONAL_STATUS] = 0.0

			run_EPANET()

			temp_subset_deficit = 0.0
			temp_system_deficit = 0.0
			temp_subset_deficit_priority = []

			for tank in object_tank.matrix:
				temp_system_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
				if tank[ENC.Tank.ID]-1000.0 in subset_junction:
					if math.fabs(tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL] - tank[ENC.Tank.HEAD]) > 1.0:
						temp_subset_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
						temp_subset_deficit_priority.append((tank[ENC.Tank.ID]-1000.0, math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])))

			if row[ENC.Pipe.ID] == 9.0:
				pipe_9_deficits_w_n1 += math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
				pipe_9_deficits_w_n1 += math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
				pipe_9_deficits_w_n1 += math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
				pipe_9_deficits_w_n1 += math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

				tank_15_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
				tank_16_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
				tank_18_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
				tank_19_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

			if temp_system_deficit > system_deficit and len(temp_subset_deficit_priority) > 0:
				subset_deficit = temp_subset_deficit
				subset_deficit_priority = sorted(temp_subset_deficit_priority, key=itemgetter(1), reverse=True)
				
				system_deficit = temp_system_deficit

	object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
	object_tank.matrix = base_tank_matrix

	# ANALYSIS STEP 6: Combined power-water N-1 and track worst-case
	# --------------------------------------------------------------
	temp_system_deficit = 0.0
	temp_subset_deficit = 0.0
	temp_subset_deficit_priority = []

	base_gen_commitment = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
	base_gen_dispatch = np.array(object_generator.matrix[:, ODC.Generator.REAL_GENERATION], copy=True)
	base_branch_commitment = np.array(object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A], copy=True)

	print('Generators')
	for row in object_generator.matrix:
		object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = np.array(base_gen_commitment, copy=True)
		object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = np.array(base_gen_dispatch, copy=True)
		run_OpenDSS(0, True)

		if row[ODC.Generator.REAL_GENERATION] != 0.0:
			print('GEN ID', row[ODC.Generator.ID])
			row[ODC.Generator.REAL_GENERATION] = 0.0
			row[ODC.Generator.OPERATIONAL_STATUS] = 0.0
			run_OpenDSS(0, True)

			minutes = grb_solvers.contingency_response(object_load, object_generator, object_cable)

			if minutes > 10.01:
				with open('minute_errors.csv', 'a', newline='') as file:
					writer = csv.writer(file)
					writer.writerow([power_load_factor, water_demand_factor, minutes])

			object_junction.setInterconnectionDemand(interconn_dict)

			for row in object_pipe.matrix:
				if row[ENC.Pipe.ID] < 1000.0:
					# print('SHUT DOWN PIPE:', row[ENC.Pipe.ID])

					object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
					object_tank.matrix = base_tank_matrix

					row[ENC.Pipe.OPERATIONAL_STATUS] = 0.0

					run_EPANET()

					temp_subset_deficit = 0.0
					temp_system_deficit = 0.0
					temp_subset_deficit_priority = []

					for tank in object_tank.matrix:
						temp_system_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
						if tank[ENC.Tank.ID]-1000.0 in subset_junction:
							if math.fabs(tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL] - tank[ENC.Tank.HEAD]) > 1.0:
								temp_subset_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
								temp_subset_deficit_priority.append((tank[ENC.Tank.ID]-1000.0, math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])))

					if row[ENC.Pipe.ID] == 9.0:
						pipe_9_deficits = math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
						pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
						pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
						pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

						if pipe_9_deficits > pipe_9_deficits_w_n1:
							pipe_9_deficits_w_n1 = pipe_9_deficits
							tank_15_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
							tank_16_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
							tank_18_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
							tank_19_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

					if temp_system_deficit > system_deficit and len(temp_subset_deficit_priority) > 0:
						flag_water_power_worst_case = 1
						subset_deficit = temp_subset_deficit
						subset_deficit_priority = sorted(temp_subset_deficit_priority, key=itemgetter(1), reverse=True)
						
						system_deficit = temp_system_deficit
			object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
			object_tank.matrix = base_tank_matrix
	object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = np.array(base_gen_commitment, copy=True)
	object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = np.array(base_gen_dispatch, copy=True)

	print('Cables')
	for row in object_cable.matrix:
		object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A] = np.array(base_branch_commitment, copy=True)
		run_OpenDSS(0, True)
 
		if row[ODC.Cable.ID] != 10.0 or row[ODC.Cable.ID] != 100.0:
			if row[ODC.Cable.OPERATIONAL_STATUS_A] == 1.0:
				print('CABLE ID', row[ODC.Cable.ID])
				row[ODC.Cable.OPERATIONAL_STATUS_A] = 0.0
				run_OpenDSS(0, True)

				minutes = grb_solvers.contingency_response(object_load, object_generator, object_cable)

				if minutes > 10.01:
					with open('minute_errors.csv', 'a', newline='') as file:
						writer = csv.writer(file)
						writer.writerow([power_load_factor, water_demand_factor, minutes])

				object_junction.setInterconnectionDemand(interconn_dict)

			for row in object_pipe.matrix:
				if row[ENC.Pipe.ID] < 1000.0:
					# print('SHUT DOWN PIPE:', row[ENC.Pipe.ID])

					object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
					object_tank.matrix = base_tank_matrix

					row[ENC.Pipe.OPERATIONAL_STATUS] = 0.0

					run_EPANET()

					temp_subset_deficit = 0.0
					temp_system_deficit = 0.0
					temp_subset_deficit_priority = []

					for tank in object_tank.matrix:
						temp_system_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
						if tank[ENC.Tank.ID]-1000.0 in subset_junction:
							if math.fabs(tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL] - tank[ENC.Tank.HEAD]) > 1.0:
								temp_subset_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
								temp_subset_deficit_priority.append((tank[ENC.Tank.ID]-1000.0, math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])))

					if row[ENC.Pipe.ID] == 9.0:
						pipe_9_deficits = math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
						pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
						pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
						pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

						if pipe_9_deficits > pipe_9_deficits_w_n1:
							pipe_9_deficits_w_n1 = pipe_9_deficits
							tank_15_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
							tank_16_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
							tank_18_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
							tank_19_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

					if temp_system_deficit > system_deficit and len(temp_subset_deficit_priority) > 0:
						flag_water_power_worst_case = 1
						subset_deficit = temp_subset_deficit
						subset_deficit_priority = sorted(temp_subset_deficit_priority, key=itemgetter(1), reverse=True)
						
						system_deficit = temp_system_deficit
			object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
			object_tank.matrix = base_tank_matrix
	object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A] = np.array(base_branch_commitment, copy=True)
	print('')

	with open('main_analysis_power_only.csv', 'a', newline='') as file:
		writer = csv.writer(file)
		writer.writerow([power_load_factor, water_demand_factor, system_deficit, subset_deficit_priority, tank_15_w, tank_16_w, tank_18_w, tank_19_w, flag_water_power_worst_case])

	# ANALYSIS STEP 7: Re-dispatch to reduce maximum water deficit
	# -----------------------------------------------------

	object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = 0.0

	for sdp_idx in range(0, len(subset_deficit_priority)):
		sdp_id, sdp_val = subset_deficit_priority[sdp_idx]
		node_list_constraint.append(sdp_id)
	
	node_water_constraint = {1.0: 0.0,
	2.0: 0.0,
	7.0: 0.0,
	13.0: 0.0,
	15.0: 0.0,
	16.0: 0.0,
	18.0: 0.0,
	22.0: 0.0,
	33.0: 0.0}
	
	def fun_set_power_dispatch(object_load, object_generator, losses, exports):
		counter = 0
		lost_min = 10000000.0
		while True:
			nres, ares = grb_solvers.unit_commitment_priority_list_water(object_load, object_generator, losses, exports, node_list_constraint, node_water_constraint) # unit commitment is variable
			new_loss = run_OpenDSS(0, True)
			counter += 1
			# print(counter)

			if math.fabs(losses - new_loss) > 1.0:
				if counter > 199:
					print('Dispatcher - Losses/Exports did not converge')
					sys.exit()
				elif counter > 150:
					while True:
						object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = dispatcher_max
						nres, ares = grb_solvers.unit_commitment_priority_list_water_2(object_load, object_generator, losses, exports, node_list_constraint, node_water_constraint) # unit commitment is input
						new_loss = run_OpenDSS(0, True)
						counter +=1

						if math.fabs(losses - new_loss) < 1.0:
							return nres, ares
						else:
							losses += 0.8 * (new_loss - losses)
				elif counter > 100:
					while True:
						object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = dispatcher_min
						nres, ares = grb_solvers.unit_commitment_priority_list_water_2(object_load, object_generator, losses, exports, node_list_constraint, node_water_constraint) # unit commitment is input
						new_loss = run_OpenDSS(0, True)
						counter +=1

						if math.fabs(losses - new_loss) < 1.0:
							return nres, ares
						else:
							losses += 0.8 * (new_loss - losses)
				elif counter > 50:
					if math.fabs(new_loss) < math.fabs(lost_min):
						lost_min = new_loss
						dispatcher_min = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
					else:
						dispatcher_max = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
				losses += 0.8*(new_loss - losses)
			else:
				return nres, ares

	needed_reserves, avail_reserves = fun_set_power_dispatch(object_load, object_generator, losses, exports)
	print('exports #1', 0.5 * (object_cable.matrix[33, ODC.Cable.REAL_POWER_2] - object_cable.matrix[33, ODC.Cable.REAL_POWER_1]))

	# ANALYSIS STEP 8: SET JUNCTION INTERCONNECTIONS
	# -----------------------------------------
	object_junction.setInterconnectionDemand(interconn_dict)

	# ANALYSIS STEP 9:
	# Set water tank levels
	# Set water valve flow control
	# ----------------------------
	object_tank.matrix[:, ENC.Tank.INITIAL_LEVEL] = 0.0
	object_tank.matrix[:, ENC.Tank.MAX_LEVEL] = 0.0

	for junction in object_junction.matrix:
		max_groundwater_flow = 12399.0

		for tank in object_tank.matrix:
			if tank[ENC.Tank.ID] - 1000.0 == junction[ENC.Junction.ID]:
				level_inc = round(junction[ENC.Junction.BASE_DEMAND]*60.0*0.133681 / (math.pi * (0.5*tank[ENC.Tank.DIAMETER])**2), 2)
				tank[ENC.Tank.INITIAL_LEVEL] += level_inc
				tank[ENC.Tank.MAX_LEVEL] += level_inc

				for generator in object_generator.matrix:
					if generator[ODC.Generator.JUNCTION_ID] == junction[ENC.Junction.ID]:
						level_inc = round(generator[ODC.Generator.OPERATIONAL_STATUS]*generator[ODC.Generator.REAL_GENERATION]*generator[ODC.Generator.WATER_CONSUMPTION]*0.001*60*0.133681 / (math.pi * (0.5*tank[ENC.Tank.DIAMETER])**2), 2)
						tank[ENC.Tank.INITIAL_LEVEL] += level_inc
						tank[ENC.Tank.MAX_LEVEL] += level_inc

		for valve in object_valve.matrix:
			if valve[ENC.Valve.ID] - 2000.0 == junction[ENC.Junction.ID]:
				# valve[ENC.Valve.SETTING] = min(junction[ENC.Junction.BASE_DEMAND], max_groundwater_flow)
				valve[ENC.Valve.SETTING] = max_groundwater_flow

	# ANALYSIS STEP 10:
	# -----------------

	system_deficit = 0.0
	subset_deficit = 0.0
	subset_deficit_priority = []

	temp_system_deficit = 0.0
	temp_subset_deficit = 0.0
	temp_subset_deficit_priority = []

	base_pipe_status = np.array(object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS], copy=True)
	base_tank_matrix = np.array(object_tank.matrix, copy=True)

	base_gen_commitment = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
	base_gen_dispatch = np.array(object_generator.matrix[:, ODC.Generator.REAL_GENERATION], copy=True)
	base_branch_commitment = np.array(object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A], copy=True)

	print('Generators')
	for row in object_generator.matrix:
		object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = np.array(base_gen_commitment, copy=True)
		object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = np.array(base_gen_dispatch, copy=True)
		run_OpenDSS(0, True)

		if row[ODC.Generator.REAL_GENERATION] != 0.0:
			print('GEN ID', row[ODC.Generator.ID])
			row[ODC.Generator.REAL_GENERATION] = 0.0
			row[ODC.Generator.OPERATIONAL_STATUS] = 0.0
			run_OpenDSS(0, True)

			# max_val = 0.0
			# max_id = 0
			# for cabidx in range(0, len(object_cable.matrix)):
			# 	if object_cable.matrix[cabidx, ODC.Cable.A_PU_CAPACITY] > max_val:
			# 		max_val = object_cable.matrix[cabidx, ODC.Cable.A_PU_CAPACITY]
			# 		max_id = object_cable.matrix[cabidx, ODC.Cable.ID]

			# print('max id', max_id)
			# print('max pu', max_val)

			minutes = grb_solvers.contingency_response(object_load, object_generator, object_cable)

			if minutes > 10.01:
				with open('minute_errors.csv', 'a', newline='') as file:
					writer = csv.writer(file)
					writer.writerow([power_load_factor, water_demand_factor, minutes])

			object_junction.setInterconnectionDemand(interconn_dict)

			for pipe in object_pipe.matrix:
				if pipe[ENC.Pipe.ID] < 1000.0:
					# print('SHUT DOWN PIPE:', pipe[ENC.Pipe.ID])

					object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
					object_tank.matrix = base_tank_matrix

					pipe[ENC.Pipe.OPERATIONAL_STATUS] = 0.0

					run_EPANET()

					temp_subset_deficit = 0.0
					temp_system_deficit = 0.0
					temp_subset_deficit_priority = []

					for tank in object_tank.matrix:
						temp_system_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
						if tank[ENC.Tank.ID]-1000.0 in subset_junction:
							if math.fabs(tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL] - tank[ENC.Tank.HEAD]) > 1.0:
								temp_subset_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
								temp_subset_deficit_priority.append((tank[ENC.Tank.ID]-1000.0, math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])))

					if row[ENC.Pipe.ID] == 9.0:
						pipe_9_deficits = math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
						pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
						pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
						pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

						if pipe_9_deficits > pipe_9_deficits_pw_n1:
							pipe_9_deficits_pw_n1 = pipe_9_deficits
							tank_15_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
							tank_16_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
							tank_18_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
							tank_19_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

					if temp_system_deficit > system_deficit and len(temp_subset_deficit_priority) > 0:
						subset_deficit = temp_subset_deficit
						subset_deficit_priority = sorted(temp_subset_deficit_priority, key=itemgetter(1), reverse=True)
						
						system_deficit = temp_system_deficit
			object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
			object_tank.matrix = base_tank_matrix
	object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = np.array(base_gen_commitment, copy=True)
	object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = np.array(base_gen_dispatch, copy=True)

	print('Cables')
	for row in object_cable.matrix:
		object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A] = np.array(base_branch_commitment, copy=True)
		run_OpenDSS(0, True)
 
		if row[ODC.Cable.ID] != 10.0 or row[ODC.Cable.ID] != 100.0:
			if row[ODC.Cable.OPERATIONAL_STATUS_A] == 1.0:
				print('CABLE ID', row[ODC.Cable.ID])
				row[ODC.Cable.OPERATIONAL_STATUS_A] = 0.0
				run_OpenDSS(0, True)

				minutes = grb_solvers.contingency_response(object_load, object_generator, object_cable)

				if minutes > 10.01:
					with open('minute_errors.csv', 'a', newline='') as file:
						writer = csv.writer(file)
						writer.writerow([power_load_factor, water_demand_factor, minutes])

				object_junction.setInterconnectionDemand(interconn_dict)

			for pipe in object_pipe.matrix:
				if pipe[ENC.Pipe.ID] < 1000.0:
					# print('SHUT DOWN PIPE:', pipe[ENC.Pipe.ID])

					object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
					object_tank.matrix = base_tank_matrix

					pipe[ENC.Pipe.OPERATIONAL_STATUS] = 0.0

					run_EPANET()

					temp_subset_deficit = 0.0
					temp_system_deficit = 0.0
					temp_subset_deficit_priority = []

					for tank in object_tank.matrix:
						temp_system_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
						if tank[ENC.Tank.ID]-1000.0 in subset_junction:
							if math.fabs(tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL] - tank[ENC.Tank.HEAD]) > 1.0:
								temp_subset_deficit += math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])
								temp_subset_deficit_priority.append((tank[ENC.Tank.ID]-1000.0, math.pi * ((0.5*tank[ENC.Tank.DIAMETER])**2) * (tank[ENC.Tank.ELEVATION]+tank[ENC.Tank.INITIAL_LEVEL]-tank[ENC.Tank.HEAD])))

					if row[ENC.Pipe.ID] == 9.0:
						pipe_9_deficits = math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
						pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
						pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
						pipe_9_deficits += math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

						if pipe_9_deficits > pipe_9_deficits_pw_n1:
							pipe_9_deficits_pw_n1 = pipe_9_deficits
							tank_15_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15, ENC.Tank.HEAD])
							tank_16_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+1, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+1, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+1, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+1, ENC.Tank.HEAD])
							tank_18_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+2, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+2, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+2, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+2, ENC.Tank.HEAD])
							tank_19_p_w = math.pi * ((0.5* object_tank.matrix[idx_tank_15+3, ENC.Tank.DIAMETER])**2) * (object_tank.matrix[idx_tank_15+3, ENC.Tank.ELEVATION]+object_tank.matrix[idx_tank_15+3, ENC.Tank.INITIAL_LEVEL]-object_tank.matrix[idx_tank_15+3, ENC.Tank.HEAD])

					if temp_system_deficit > system_deficit and len(temp_subset_deficit_priority) > 0:
						subset_deficit = temp_subset_deficit
						subset_deficit_priority = sorted(temp_subset_deficit_priority, key=itemgetter(1), reverse=True)
						
						system_deficit = temp_system_deficit
			object_pipe.matrix[:, ENC.Pipe.OPERATIONAL_STATUS] = base_pipe_status
			object_tank.matrix = base_tank_matrix
	object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A] = np.array(base_branch_commitment, copy=True)
	print('')

	with open('main_analysis_power_water.csv', 'a', newline='') as file:
		writer = csv.writer(file)
		writer.writerow([power_load_factor, water_demand_factor, system_deficit, subset_deficit_priority, tank_15_p_w, tank_16_p_w, tank_18_p_w, tank_19_p_w])

	# SIM STEP 6: RUN POWER-WATER SIMULATION
	# --------------------------------------
	# Interconnections have no effect
	# input_list_continuous, input_list_categorical, output_list, input_tensor_continuous, input_tensor_categorical, output_tensor = run_OpenDSS(dss_debug, False)
	# input_list_continuous1, input_list_categorical1, output_list1, input_tensor_continuous1, input_tensor_categorical1, output_tensor1 = run_EPANET()
	# Interconnections have an effect
	# _, _, output_list, _, _, output_tensor = run_OpenDSS(dss_debug, False)
	# _, _, output_list1, _, _, output_tensor1 = run_EPANET()

	# RESULTS STEP 1: FORMAT INPUT/OUTPUT TENSORS
	# -------------------------------------------
	# input_list_continuous = input_list_continuous + input_list_continuous1
	# input_list_categorical = input_list_categorical + input_list_categorical1
	# output_list = output_list + output_list1

	# input_tensor_continuous = np.concatenate((input_tensor_continuous, input_tensor_continuous1), axis=0)
	# input_tensor_categorical = np.concatenate((input_tensor_categorical, input_tensor_categorical1), axis=0)
	# output_tensor = np.concatenate((output_tensor, output_tensor1), axis=0)

	# RESULTS STEP 2: WRITE INPUT/OUTPUT TENSORS TO FILE
	# --------------------------------------------------
	# if write_cols:
	# 	with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/tensor_outputs/input_list_continuous_columns.csv', 'w') as f:
	# 		writer = csv.writer(f, delimiter=',')
	# 		writer.writerow(input_list_continuous)
	# 	with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/tensor_outputs/input_list_categorical_columns.csv', 'w') as f:
	# 		writer = csv.writer(f, delimiter=',')
	# 		writer.writerow(input_list_categorical)
	# 	with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/tensor_outputs/output_list_columns.csv', 'w') as f:
	# 		writer = csv.writer(f, delimiter=',')
	# 		writer.writerow(output_list)

	# with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/tensor_outputs/input_tensor_continuous.csv', 'ab') as f:
	# 	np.savetxt(f, input_tensor_continuous[None, :], fmt='%0.6f', delimiter=' ', newline='\n')
	# with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/tensor_outputs/input_tensor_categorical.csv', 'ab') as f:
	# 	np.savetxt(f, input_tensor_categorical[None, :], fmt='%0.6f', delimiter=' ', newline='\n')
	# with open('C:/Users/'+os_username+'/Documents/git/RISE-power-water-ss-1phase/tensor_outputs/output_tensor.csv', 'ab') as f:
	# 	np.savetxt(f, output_tensor[None, :], fmt='%0.6f', delimiter=' ', newline='\n')

	# END
	# ---

if __name__ == '__main__':
	write_cols = False # Write column names to seperate file
	dss_debug = 0


	power_df = float(sys.argv[1])
	water_df = float(sys.argv[2])

	main(dss_debug, write_cols, power_df, water_df)

























# ///////////////////////////////////////////////////////////////////////////////////
# OLD STUFF
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	# ------------------------
	# STOCHASTICITY PARAMETERS
	# ------------------------

	# water_num_switch = 0
	# water_num_stochastic = 0
	# power_num_switch = 0
	# power_num_stochastic = 0
	# for object in w_object_list:
	# 	water_num_switch += object.num_switches
	# 	water_num_stochastic += object.num_stochastic
	# for object in object_list:
	# 	power_num_switch += object.num_switches
	# 	power_num_stochastic += object.num_stochastic
	
	# def calc_probabilities():
		# temp = 0.0
		# switch_chanceval = 0.0
		# stochastic_chanceval = 0.0
		# for object in w_object_list:
		# 	if object.num_switches == 0:
		# 		object.switch_chance = (0.0, 0.0)
		# 	else:
		# 		try:
		# 			temp = switch_chanceval
		# 			switch_chanceval += object.num_switches / water_num_switch
		# 			object.switch_chance = (temp, switch_chanceval)
		# 		except:
		# 			object.switch_chance = (0.0, 0.0)
		# 	if object.num_stochastic == 0:
		# 		object.stochastic_chance = (0.0, 0.0)
		# 	else:
		# 		try:
		# 			temp = stochastic_chanceval
		# 			stochastic_chanceval += object.num_stochastic / water_num_stochastic
		# 			object.stochastic_chance = (temp, stochastic_chanceval)
		# 		except:
		# 			object.stochastic_chance = (0.0, 0.0)
		
		# temp = 0.0
		# switch_chanceval = 0.0
		# stochastic_chanceval = 0.0
		# for object in object_list:
		# 	if object.num_switches == 0:
		# 		object.switch_chance = (0.0, 0.0)
		# 	else:
		# 		try:
		# 			temp = switch_chanceval
		# 			switch_chanceval += object.num_switches / power_num_switch
		# 			object.switch_chance = (temp, switch_chanceval)
		# 		except:
		# 			object.switch_chance = (0.0, 0.0)
		# 	if object.num_stochastic == 0:
		# 		object.stochastic_chance = (0.0, 0.0)
		# 	else:
		# 		try:
		# 			temp = stochastic_chanceval
		# 			stochastic_chanceval += object.num_stochastic / power_num_stochastic
		# 			object.stochastic_chance = (temp, stochastic_chanceval)
		# 		except:
		# 			object.stochastic_chance = (0.0, 0.0)

	# def run_stochasticity(stoch_num):
	# 	# STOCHASTIC VALUES (e.g., demand)
	# 	for i in range(0, stoch_num):
	# 		if random.randrange(1, water_num_stochastic+power_num_stochastic+1) <= water_num_stochastic:
	# 			rval = random.random()
	# 			for object in w_object_list: # water list
	# 				lower, upper = object.stochastic_chance
	# 				if lower <= rval <= upper:
	# 					pass
	# 					# object.randomStochasticity()
	# 		else:
	# 			rval = random.random()
	# 			for object in object_list: # power list
	# 				lower, upper = object.stochastic_chance
	# 				if lower <= rval <= upper:
	# 					pass
	# 					# object.randomStochasticity()

	# 	# SWITCHING VALUES (e.g., on/off)
	# 	if random.random() <= 0.65: # 65% chance to shutoff
	# 		if random.randrange(1, water_num_switch+power_num_switch+1) <= water_num_switch:
	# 			rval = random.random()
	# 			for object in w_object_list: # water list
	# 				lower, upper = object.switch_chance
	# 				if lower <= rval <= upper:
	# 					pass
	# 					# object.randomSwitching()
	# 		else:
	# 			rval = random.random()
	# 			for object in object_list: # power list
	# 				lower, upper = object.switch_chance
	# 				if lower <= rval <= upper:
	# 					pass
	# 					# object.randomSwitching()

	# # SIM STEP 1: CALCULATE UNIFORM PROBABILITIES FOR COMPONENTS
	# calc_probabilities()

	# # SIM STEP 2: STOCHASTICITY OF OBJECT CONTROLS AND "FAILURE"
	# run_stochasticity(stoch_num)