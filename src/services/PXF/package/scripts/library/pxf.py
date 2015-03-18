import utilities

def is_running(pidFile):
  try:
    with open(pidFile, 'r') as filehandle:
      pid = int(filehandle.readlines()[0])
      return utilities.is_process_running(pidFile, pid)

  except IOError:
    return False
