# Source: https://goo.gl/LGKWcv
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

# [START vendor]
import imp
import inspect
import os

from google.appengine.ext import vendor

# Add any libraries installed in the "lib" folder.
vendor.add('lib')

# === ADDED ===
if not os.environ.get('GAE_ENV'):
    # Set up SSL for local testing
    from google.appengine.tools.devappserver2.python.runtime import sandbox

    sandbox._WHITE_LIST_C_MODULES += ['_ssl', '_socket']

    RUNTIME_PATH = os.path.realpath(inspect.getsourcefile(inspect))
    RUNTIME_DIR = os.path.dirname(RUNTIME_PATH)

    # Patch and reload the socket module implementation.
    SYSTEM_SOCKET = os.path.join(RUNTIME_DIR, 'socket.py')
    imp.load_source('socket', SYSTEM_SOCKET)

    # Patch and reload the ssl module implementation.
    SYSTEM_SSL = os.path.join(RUNTIME_DIR, 'ssl.py')
    imp.load_source('ssl', SYSTEM_SSL)
#=============
# [END vendor]
