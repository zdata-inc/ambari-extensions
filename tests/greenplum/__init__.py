import sys, os

sys.path.append(os.path.join(os.environ['AMBARI_SOURCE'], 'ambari-common/src/test/python'))
sys.path.append(os.path.join(os.environ['AMBARI_SOURCE'], 'ambari-common/src/main/python'))
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/services/GREENPLUM/package/scripts')))
