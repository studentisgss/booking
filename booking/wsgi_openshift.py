import sys
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "booking.settings")

virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')

try:
    exec_namespace = dict(__file__=virtualenv)
    with open(virtualenv, 'rb') as exec_file:
        file_contents = exec_file.read()
    compiled_code = compile(file_contents, virtualenv, 'exec')
    exec(compiled_code, exec_namespace)
except IOError:
    pass

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
