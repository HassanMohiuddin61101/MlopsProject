"""
Windows-compatible Airflow webserver startup script
"""
import sys
import os

# CRITICAL: Patch Unix-only modules FIRST, before ANY other imports
# This must happen before Airflow or Gunicorn try to import fcntl
class MockPwd:
    """Mock pwd module for Windows"""
    @staticmethod
    def getpwnam(name):
        class Passwd:
            pw_uid = 0
            pw_gid = 0
            pw_dir = os.path.expanduser("~")
            pw_shell = os.environ.get("SHELL", "cmd.exe")
        return Passwd()

class MockResource:
    """Mock resource module for Windows"""
    RLIMIT_CPU = 0
    RLIMIT_FSIZE = 1
    RLIMIT_DATA = 2
    RLIMIT_STACK = 3
    RLIMIT_CORE = 4
    RLIMIT_RSS = 5
    RLIMIT_NPROC = 6
    RLIMIT_NOFILE = 7
    RLIMIT_MEMLOCK = 8
    RLIMIT_AS = 9
    RLIMIT_LOCKS = 10
    RLIMIT_SIGPENDING = 11
    RLIMIT_MSGQUEUE = 12
    RLIMIT_NICE = 13
    RLIMIT_RTPRIO = 14
    RLIMIT_RTTIME = 15
    
    @staticmethod
    def getrlimit(resource):
        return (float('inf'), float('inf'))
    
    @staticmethod
    def setrlimit(resource, limits):
        pass

# Create mock modules in sys.modules BEFORE any imports
# Order matters: fcntl must be patched FIRST before Gunicorn imports
sys.modules['pwd'] = MockPwd()
sys.modules['resource'] = MockResource()

# Mock fcntl module (Unix-only, needed by Gunicorn) - MUST BE FIRST
class MockFcntl:
    """Mock fcntl module for Windows"""
    LOCK_EX = 2
    LOCK_SH = 1
    LOCK_NB = 4
    LOCK_UN = 8
    
    @staticmethod
    def flock(fd, operation):
        pass
    
    @staticmethod
    def lockf(fd, operation, length=0, start=0, whence=0):
        pass

# Patch fcntl IMMEDIATELY - before any other module imports it
sys.modules['fcntl'] = MockFcntl()

# Create complete mock daemon module with submodules
import types

# Mock daemon.pidfile submodule
mock_pidfile = types.ModuleType('daemon.pidfile')
class TimeoutPIDLockFile:
    def __init__(self, *args, **kwargs):
        pass
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
mock_pidfile.TimeoutPIDLockFile = TimeoutPIDLockFile
sys.modules['daemon.pidfile'] = mock_pidfile

# Mock daemon module
mock_daemon = types.ModuleType('daemon')
mock_daemon.DaemonContext = type('DaemonContext', (), {
    '__init__': lambda self, **kwargs: None,
    '__enter__': lambda self: self,
    '__exit__': lambda self, *args: None,
})
mock_daemon.pidfile = mock_pidfile
sys.modules['daemon'] = mock_daemon

# Set environment variables
os.environ.setdefault('AIRFLOW_HOME', os.path.join(os.getcwd(), 'airflow'))

# Now import and run Airflow webserver
if __name__ == "__main__":
    # For Windows, use standalone mode which is more compatible
    # OR use the webserver with explicit configuration
    import sys
    
    # Try using standalone instead (better Windows support)
    print("Starting Airflow webserver in Windows-compatible mode...")
    print("Note: For better Windows compatibility, consider using: python start_airflow_windows.py")
    print()
    
    # Use Airflow's CLI system
    from airflow.cli import cli_parser
    
    # Parse arguments - just port, let Airflow handle the rest
    parser = cli_parser.get_parser()
    args = parser.parse_args(['webserver', '--port', '8080'])
    
    # Call the webserver function
    args.func(args)

