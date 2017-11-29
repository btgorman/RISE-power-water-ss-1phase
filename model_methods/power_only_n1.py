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

def main(dss_debug, write_cols, plf):
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

	csv_pumpload = pd.read_csv('./data_interconnection/network-interconnection/9000pump-load.csv', sep=',', header=1, index_col=None, dtype=np.float64)
	csv_tankgenerator = pd.read_csv('./data_interconnection/network-interconnection/9001tank-generator.csv', sep=',', header=1, index_col=None, dtype=np.float64)

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

	object_pumpload = ICC.PumpLoad(csv_pumpload)
	object_tankgenerator = ICC.TankGenerator(csv_tankgenerator)

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

	interconn_dict = {'pumpload': object_pumpload, 'tankgenerator': object_tankgenerator,
	'pump': object_pump, 'load': object_load, 'tank': object_tank,
	'generator': object_generator, 'junction': object_junction}

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
			templist = ['Duration', '0:00:10']
			writer.writerow(templist)
			templist = ['Hydraulic', 'Timestep', '0:00:10']
			writer.writerow(templist)
			templist = ['Quality', 'Timestep', '0:05']
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
			templist = ['Headloss', 'H-W']
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
			if errorcode != 0:
				print(4, 'ERRORCODE is', errorcode)

			for water_object in w_object_list:
				water_object.readAllENoutputs(epalib)

			errorcode = epalib.ENnextH(timestep)
			if errorcode != 0:
				print(5, 'ERRORCODE is', errorcode)

			if timestep.contents.value == 0:
				break

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


	# SIM STEP 1: SET LOAD CURVES
	# ------------------------------
	power_load_mu = -0.51385 # lognormal, AIC -9693.48
	power_load_sigma = 0.23256 # lognormal, AIC -9693.48
	power_load_lb = 0.3388
	power_load_ub = 1.0
	power_load_factor = min(np.random.lognormal(power_load_mu, power_load_sigma, size=None), power_load_ub)
	power_load_factor = max(power_load_factor, power_load_lb)
	power_load_factor = plf
	power_factor = 0.0
	object_load.multiplyLoadFactor(power_load_factor, power_factor)
	print('power load factor', power_load_factor)
	for load in object_load.matrix:
		if load[ODC.Load.ID] == 4.0 or load[ODC.Load.ID] == 20.0:
			load[ODC.Load.REAL_LOAD] = load[ODC.Load.REAL_LOAD_MAX]

	water_demand_scale = np.exp(0.0144362) # exponential, AIC = 582.27
	water_demand_lb = 0.256
	water_demand_ub = 4.21
	water_demand_factor = min(water_demand_lb+np.random.exponential(water_demand_scale, size=None), water_demand_ub)
	object_junction.multiplyLoadFactor(water_demand_factor)

	# SIM STEP 2: SET GENERATOR DISPATCH
	# ----------------------------------
	exports = 0.0 # kW
	losses = 0.0 # kW

	def fun_set_power_dispatch(object_load, object_generator, losses, exports):
		counter = 0
		lost_min = 10000000.0
		while True:
			grb_solvers.power_dispatch(object_load, object_generator, losses, exports) # unit commitment is variable
			new_loss = run_OpenDSS(0, True)
			counter += 1

			if math.fabs(losses - new_loss) > 1.0:
				if counter > 199:
					print('Dispatcher - Losses/Exports did not converge')
					sys.exit()
				elif counter > 150:
					while True:
						object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = dispatcher_max
						grb_solvers.power_dispatch_2(object_load, object_generator, losses, exports) # unit commitment is input
						new_loss = run_OpenDSS(0, True)
						counter +=1

						if math.fabs(losses - new_loss) < 1.0:
							return 0
						else:
							losses += 0.8 * (new_loss - losses)
				elif counter > 100:
					while True:
						object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = dispatcher_min
						grb_solvers.power_dispatch_2(object_load, object_generator, losses, exports) # unit commitment is input
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
	# print('exports #1', 0.5 * (object_cable.matrix[33, ODC.Cable.REAL_POWER_2] - object_cable.matrix[33, ODC.Cable.REAL_POWER_1]))
	# print('')

	base_gen_commitment = np.array(object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS], copy=True)
	base_gen_dispatch = np.array(object_generator.matrix[:, ODC.Generator.REAL_GENERATION], copy=True)
	list_gen_mint = []
	list_gen_error = []
	list_gen_post_branch_load = []
	list_gen_resp_branch_load = []

	base_branch_commitment = np.array(object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A], copy=True)
	list_branch_mint = []
	list_branch_error = []
	list_branch_post_branch_load = []
	list_branch_resp_branch_load = []

	print('Generators')
	for row in object_generator.matrix:
		object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = np.array(base_gen_commitment, copy=True)
		object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = np.array(base_gen_dispatch, copy=True)
		run_OpenDSS(0, True)

		if row[ODC.Generator.REAL_GENERATION] != 0.0:
			row[ODC.Generator.REAL_GENERATION] = 0.0
			row[ODC.Generator.OPERATIONAL_STATUS] = 0.0
			run_OpenDSS(0, True)

			branch_idx = 0
			branch_max = 0.0
			for idx in range(0, len(object_cable.matrix)):
				if abs(object_cable.matrix[idx, ODC.Cable.A_PU_CAPACITY]) > branch_max:
					branch_idx = idx
					branch_max = abs(object_cable.matrix[idx, ODC.Cable.A_PU_CAPACITY])

			list_gen_post_branch_load.append(abs(object_cable.matrix[branch_idx, ODC.Cable.A_PU_CAPACITY]))
			list_gen_mint.append(grb_solvers.contingency_response(object_load, object_generator, object_cable))
			run_OpenDSS(0, True)
			list_gen_resp_branch_load.append(abs(object_cable.matrix[branch_idx, ODC.Cable.A_PU_CAPACITY]))
			list_gen_error.append(0.5*(object_cable.matrix[34-1, ODC.Cable.REAL_POWER_2] - object_cable.matrix[34-1, ODC.Cable.REAL_POWER_1]))
	object_generator.matrix[:, ODC.Generator.OPERATIONAL_STATUS] = np.array(base_gen_commitment, copy=True)
	object_generator.matrix[:, ODC.Generator.REAL_GENERATION] = np.array(base_gen_dispatch, copy=True)
	
	print('Cables')
	for row in object_cable.matrix:
		object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A] = np.array(base_branch_commitment, copy=True)
		run_OpenDSS(0, True)
 
		if row[ODC.Cable.ID] != 10.0 or row[ODC.Cable.ID] != 100.0:
			if row[ODC.Cable.OPERATIONAL_STATUS_A] == 1.0:
				row[ODC.Cable.OPERATIONAL_STATUS_A] = 0.0
				run_OpenDSS(0, True)

				branch_idx = 0
				branch_max = 0.0
				for idx in range(0, len(object_cable.matrix)):
					if abs(object_cable.matrix[idx, ODC.Cable.A_PU_CAPACITY]) > branch_max:
						branch_idx = idx
						branch_max = abs(object_cable.matrix[idx, ODC.Cable.A_PU_CAPACITY])

				list_branch_post_branch_load.append(abs(object_cable.matrix[branch_idx, ODC.Cable.A_PU_CAPACITY]))
				list_branch_mint.append(grb_solvers.contingency_response(object_load, object_generator, object_cable))
				run_OpenDSS(0, True)
				list_branch_resp_branch_load.append(abs(object_cable.matrix[branch_idx, ODC.Cable.A_PU_CAPACITY]))
				list_branch_error.append(0.5*(object_cable.matrix[34-1, ODC.Cable.REAL_POWER_2] - object_cable.matrix[34-1, ODC.Cable.REAL_POWER_1]))
	object_cable.matrix[:, ODC.Cable.OPERATIONAL_STATUS_A] = np.array(base_branch_commitment, copy=True)
	print('')

	max_gen_mint = max(list_gen_mint)
	med_gen_mint = median(list_gen_mint)
	avg_gen_mint = sum(list_gen_mint) / len(list_gen_mint)

	max_gen_error = max(max(list_gen_error), abs(min(list_branch_error)))
	med_gen_error = median(list_gen_error)
	avg_gen_error = sum(list_gen_error) / len(list_gen_error)

	max_gen_branch_load = max(list_gen_post_branch_load)
	max_gen_branch_idx = list_gen_post_branch_load.index(max_gen_branch_load)
	max_gen_post_branch_load = list_gen_post_branch_load[max_gen_branch_idx]
	max_gen_resp_branch_load = list_gen_resp_branch_load[max_gen_branch_idx]

	max_branch_mint = max(list_branch_mint)
	med_branch_mint = median(list_branch_mint)
	avg_branch_mint = sum(list_branch_mint) / len(list_branch_mint)

	max_branch_error = max(max(list_branch_error), abs(min(list_branch_error)))
	med_branch_error = median(list_branch_error)
	avg_branch_error = sum(list_branch_error) / len(list_branch_error)

	max_branch_branch_load = max(list_branch_post_branch_load)
	max_branch_branch_idx = list_branch_post_branch_load.index(max_branch_branch_load)
	max_branch_post_branch_load = list_branch_post_branch_load[max_branch_branch_idx]
	max_branch_resp_branch_load = list_branch_resp_branch_load[max_branch_branch_idx]

	with open('gen_response.csv', 'a', newline='') as file:
		writer = csv.writer(file)
		writer.writerow([power_load_factor, max_gen_post_branch_load, max_gen_resp_branch_load, max_gen_mint, med_gen_mint, avg_gen_mint, max_gen_error, med_gen_error, avg_gen_error])

	with open('branch_response.csv', 'a', newline='') as file:
		writer = csv.writer(file)
		writer.writerow([power_load_factor, max_branch_post_branch_load, max_branch_resp_branch_load, max_branch_mint, med_branch_mint, avg_branch_mint, max_branch_error, med_branch_error, avg_branch_error])

	# counter = 0
	# for row in object_generator.matrix:
	# 	if row[ODC.Generator.REAL_GENERATION] != 0.0:
	# 		if counter == 5: # 4 5 6 # 4 5 6
	# 			# print('generator', row[ODC.Generator.ID], 'is offline!')
	# 			row[ODC.Generator.REAL_GENERATION] = 0.0
	# 			row[ODC.Generator.OPERATIONAL_STATUS] = 0.0
	# 			break
	# 		counter += 1

	# counter = 0
	# for row in object_cable.matrix:
	# 	if row[ODC.Cable.ID] != 10.0 or row[ODC.Cable.ID] != 100.0:
	# 		if counter == 17: # 12, 17
	# 			print('cable', row[ODC.Cable.ID], 'is offline!')
	# 			row[ODC.Cable.OPERATIONAL_STATUS_A] = 0.0
	# 			break
	# 	counter += 1

	# counter = 0
	# min_load_idx = 0
	# min_load = 100000000.0
	# second_min_load_idx = 0
	# second_min_load = 0.
	# for row in object_load.matrix:
	# 	if row[ODC.Load.REAL_LOAD] < min_load:
	# 		second_min_load_idx = min_load_idx
	# 		second_min_load = min_load
	# 		min_load = row[ODC.Load.REAL_LOAD]
	# 		min_load_idx = counter
	# 	counter += 1

	# run_OpenDSS(0, True)
	# print('load', object_load.matrix[min_load_idx, ODC.Load.ID], 'is offline!', object_load.matrix[min_load_idx, ODC.Load.REAL_LOAD])
	# print('second min load is', object_load.matrix[second_min_load_idx, ODC.Load.ID], object_load.matrix[second_min_load_idx, ODC.Load.REAL_LOAD])
	# object_load.matrix[min_load_idx, ODC.Load.REAL_LOAD] = 0.0

	# branch_id_to_check = 34
	# print('branch ID',object_cable.matrix[branch_id_to_check-1, ODC.Cable.ID],'has power',0.5*(object_cable.matrix[branch_id_to_check-1, ODC.Cable.REAL_POWER_2] - object_cable.matrix[branch_id_to_check-1, ODC.Cable.REAL_POWER_1]))
	# print('max line load pt1', max(np.absolute(object_cable.matrix[:, ODC.Cable.A_PU_CAPACITY])))
	
	# minutes_to_respond = grb_solvers.contingency_response(object_load, object_generator, object_cable)
	
	# run_OpenDSS(0, True)
	# print('branch',object_cable.matrix[branch_id_to_check-1, ODC.Cable.ID],'has power',0.5*(object_cable.matrix[branch_id_to_check-1, ODC.Cable.REAL_POWER_2] - object_cable.matrix[branch_id_to_check-1, ODC.Cable.REAL_POWER_1]))
	# print('exports #2', 0.5 * (object_cable.matrix[33, ODC.Cable.REAL_POWER_2] - object_cable.matrix[33, ODC.Cable.REAL_POWER_1]))
	# print('max line load pt2', max(np.absolute(object_cable.matrix[:, ODC.Cable.A_PU_CAPACITY])))
	# print('')

	# SIM STEP 3: RUN POWER-WATER SIMULATION
	# --------------------------------------
	# input_list_continuous, input_list_categorical, _, input_tensor_continuous, input_tensor_categorical, _ = run_OpenDSS(dss_debug, False)
	# input_list_continuous1, input_list_categorical1, _, input_tensor_continuous1, input_tensor_categorical1, _ = run_EPANET()
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

	power_load_factor = float(sys.argv[1])

	main(dss_debug, write_cols, power_load_factor)

























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