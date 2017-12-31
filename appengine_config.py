# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import imp
import inspect
import os

# [START vendor]
from google.appengine.ext import vendor
from google.appengine.tools.devappserver2.python.runtime import sandbox

# Add any libraries installed in the "lib" folder.

sandbox._WHITE_LIST_C_MODULES += ['_ssl', '_socket']

runtime_path = os.path.realpath(inspect.getsourcefile(inspect))
runtime_dir = os.path.dirname(runtime_path)

# Patch and reload the socket module implementation.
system_socket = os.path.join(runtime_dir, 'socket.py')
imp.load_source('socket', system_socket)

# Patch and reload the ssl module implementation.
system_ssl = os.path.join(runtime_dir, 'ssl.py')
imp.load_source('ssl', system_ssl)

vendor.add('lib')
