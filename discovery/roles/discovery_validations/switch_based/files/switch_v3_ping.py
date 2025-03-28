#  Copyright 2024 Dell Inc. or its subsidiaries. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import platform
import subprocess
import sys
import ipaddress

host = sys.argv[1]

def validate_ip(host):
    """
    Returns True if host is a valid IP address.
    """
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False

def ping():
    """
    Returns True if host (str) responds to a ping request.
    """
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    # Validate the IP address
    if not validate_ip(host):
        sys.exit(f"'{host}' is not a valid IP address.")
    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0



ping_op = ping()
if not ping_op:
    print(host)
    sys.exit(" is not pingable. Please provide reachable switches in switch based discovery.")