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

# POWER-WATER ANALYSIS
# --------------------
# pump 9
# pumps 25-28
# pumps 36 & 37
# NOT pumps 13-17
# pump 24
# pumps 1, 2, 4
# pump 34

for pipe_fid in pipe_array:
	for widx in range(0, water_sims):
		for pidx in range(0, power_sims):
			pid = subprocess.call('python analysis_power_water_n2.py {} {} {}'.format(pdf_array[pidx], wdf_array[widx], pipe_fid), shell=True)