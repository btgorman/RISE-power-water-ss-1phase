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

import subprocess
import sys
import numpy as np

water_demand_lb = 0.372453
water_demand_ub = 2.984
water_sims = 8

power_load_lb = 0.3388
power_load_ub = 1.0
power_sims = 201

wdf_array = np.linspace(water_demand_lb, water_demand_ub, water_sims)
pdf_array = np.linspace(power_load_lb, power_load_ub, power_sims)

pipe_array = [9.0, 25.0, 24.0]
pipe_array.remove(25.0)
pipe_array.remove(24.0)

alpha_array = [1.0]

municipal_junction_array = [1.0, 2.0, 3.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 13.0, 14.0, 15.0, 16.0, 18.0, 19.0, 28.0]
municipal_junction_array.remove(28.0) # tuscon exports
municipal_junction_array.remove(18.0) # base model
municipal_junction_array = [18.0]
print(municipal_junction_array)

for junction in municipal_junction_array:
	for pipe_fid in pipe_array:
		for alpha in alpha_array:
			for widx in [0]:#range(0, water_sims):
				for pidx in [0]:#range(0, power_sims):
					pid = subprocess.call('python analysis_power_water_n1.py {} {} {} {} {}'.format(pdf_array[pidx], wdf_array[widx], alpha, pipe_fid, junction), shell=True)