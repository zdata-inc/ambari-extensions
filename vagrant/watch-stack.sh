if ! type pip &>/dev/null; then
    curl https://bootstrap.pypa.io/get-pip.py | sudo python
fi

if ! type watchmedo &>/dev/null; then
    sudo pip install watchdog
fi

cat | python <<'EOF'
import sys
import time
import logging
from watchdog.observers.polling import PollingObserver
from watchdog.events import LoggingEventHandler
from watchdog.tricks import ShellCommandTrick

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
event_handler = ShellCommandTrick(
    shell_command='sudo cp -R /vagrant/1.0.0.zData/ /var/lib/ambari-agent/cache/stacks/HDP/ && date',
    patterns='*',
    ignore_patterns='',
    ignore_directories=False,
    wait_for_process=True,
    drop_during_process=False
)

observer = PollingObserver()
observer.schedule(event_handler, '/vagrant/1.0.0.zData/', recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
EOF

# watchmedo shell-command --interval 3 --patterns="*.py" --recursive --command "echo 'HHHHHHH'" --drop /vagrant/1.0.0.zData