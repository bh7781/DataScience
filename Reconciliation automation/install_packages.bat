virtualenv venv

call venv\Scripts\activate

python.exe -m pip install pandas --index-url http://odyssey.apps.csintra.net/artifactory/api/pypi/pypi-release/simple --trusted-host odyssey.apps.csintra.net

python.exe -m pip install xlrd --index-url http://odyssey.apps.csintra.net/artifactory/api/pypi/pypi-release/simple --trusted-host odyssey.apps.csintra.net

python.exe -m pip install openpyxl --index-url http://odyssey.apps.csintra.net/artifactory/api/pypi/pypi-release/simple --trusted-host odyssey.apps.csintra.net

PAUSE