import ctypes
import enum
from multiprocessing import shared_memory
from PySide6.QtCore import QCoreApplication

PLUGIN_INTERFACE_VERSION: int = 4

PLUGIN_MAXDISPLAYTEXT: int = 20
PLUGIN_MAXERRORTEXT: int = 100
PLUGIN_MAXERRORTEXTLONG: int = 201

class PluginStatus(enum.Enum):
    PLUGIN_NOSTATUS = 0  # Nothing interesting for BurnInTest to know about
    PLUGIN_STARTUP = 1  # Not used - for future use
    PLUGIN_ALLOCATE = 2  # Not used - for future use
    PLUGIN_WRITING = 3  # Not used - for future use
    PLUGIN_READING = 4  # Not used - for future use
    PLUGIN_VERIFYING = 5  # Not used - for future use
    PLUGIN_WAITING = 6  # Not used - for future use
    PLUGIN_CLEANUP = 7  # Not used - for future use
    PLUGIN_ERROR = 8  # Not used - for future use
    PRE_TEST_PLUGIN_COMPLETED = 9  # If this is flagged in status then BurnInTest will close the interface to the Plugin and continue - for a pre-test plugin
    PLUGIN_MAXVAL = 10  # Must always be one bigger than the last value
    
    PLUGIN_NOTUSED = -1

# Error severity
class ErrorSeverity(enum.Enum):
    ERRORNONE = 0
    ERRORINFORMATION = 1
    ERRORWARNING = 2
    ERRORSERIOUS = 3
    ERRORCRITICAL = 4
    ERRORTERM = 5

class BitInterfaceStructure(ctypes.Structure):
  _fields_ = [
    # Data sent to plugin from BIT
    ('test_running', ctypes.c_int),
    ('duty_cycle', ctypes.c_int),
    # Data sent to BIT from plugin
    ('interface_version', ctypes.c_int),

    ('window_title', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),
    ('cycle', ctypes.c_uint),
    ('status', ctypes.c_int),
    ('status_message', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),

    ('error_count', ctypes.c_int),
    ('error_message', ctypes.c_char * PLUGIN_MAXERRORTEXT),
    ('error_severity', ctypes.c_int),

    ('write_operations_text', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),
    ('write_operations', ctypes.c_int64),

    ('read_operations_text', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),
    ('read_operations', ctypes.c_int64),
    
    ('verify_operations_text', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),
    ('verify_operations', ctypes.c_int64),

    ('user_defined_1_used', ctypes.c_bool),
    ('user_defined_1_text', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),
    ('user_defined_1_value', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),

    ('user_defined_2_used', ctypes.c_bool),
    ('user_defined_2_text', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),
    ('user_defined_2_value', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),

    #Event flags
    ('new_display_text', ctypes.c_bool),
    ('new_error', ctypes.c_bool),
    ('new_status', ctypes.c_bool),
    ('new_user_defined_1_value', ctypes.c_bool),
    ('new_user_defined_2_value', ctypes.c_bool),
    ('test_stopped', ctypes.c_bool),

    # V# of Interface. BurnInTest 6.0.1000 (BIT601000.0005)
    # Data sent to BIT from plugin
    ('user_defined_3_used', ctypes.c_bool),
    ('user_defined_3_text', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),
    ('user_defined_3_value', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),

    ('user_defined_4_used', ctypes.c_bool),
    ('user_defined_4_text', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),
    ('user_defined_4_value', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),

    ('user_defined_5_used', ctypes.c_bool),
    ('user_defined_5_text', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),
    ('user_defined_5_value', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),

    ('user_defined_6_used', ctypes.c_bool),
    ('user_defined_6_text', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),
    ('user_defined_6_value', ctypes.c_char * PLUGIN_MAXDISPLAYTEXT),

    # V4 of Interface. BurnInTest 7.0.1000
    ('error_message_long', ctypes.c_char * PLUGIN_MAXERRORTEXTLONG),
  ]

class BitInterface:
    def __init__(self, key: str, window_title: str):
        self._mem = shared_memory.SharedMemory(key, False)
        self._struct = BitInterfaceStructure.from_buffer(self._mem.buf)

        self._struct.interface_version = PLUGIN_INTERFACE_VERSION

        self._struct.cycle = 0
        self._struct.error_count = 0
        self._struct.error_severity = ErrorSeverity.ERRORNONE.value
        self._struct.status = PluginStatus.PLUGIN_NOSTATUS.value

        self._struct.write_operations = -1
        self._struct.read_operations = -1
        self._struct.verify_operations = -1

        self._struct.new_error = False
        self._struct.new_status = False
        self._struct.test_stopped = False

        self._struct.window_title = window_title.encode('utf-8')
        self._struct.status_message = "Starting".encode('utf-8')
        self._struct.error_message = "".encode('utf-8')
        self._struct.write_operations_text = "Write:".encode('utf-8')
        self._struct.read_operations_text = "Read:".encode('utf-8')
        self._struct.verify_operations_text = "Verify:".encode('utf-8')
        self._struct.new_display_text = True

    @property
    def test_running(self) -> bool:
        return bool(self._struct.test_running == 1)

    @property
    def duty_cycle(self) -> int:
        return int(self._struct.duty_cycle)
    
    @property
    def cycle(self) -> int:
        return int(self._struct.cycle)
    
    @cycle.setter
    def cycle(self, value: int) -> None:
        self._struct.cycle = value

    @property
    def error_count(self) -> int:
        return self._struct.error_count 

    @property
    def write_operations_text(self) -> str:
        return self._struct.write_operations_text.decode('utf-8')
    
    @write_operations_text.setter
    def write_operations_text(self, value: str) -> None:
        self._struct.write_operations_text = value.encode('utf-8')

    @property
    def write_operations(self) -> int:
        return self._struct.write_operations
    
    @write_operations.setter
    def write_operations(self, value: int) -> None:
        self._struct.write_operations = value

    @property
    def read_operations_text(self) -> str:
        return self._struct.read_operations_text.decode('utf-8')
    
    @read_operations_text.setter
    def read_operations_text(self, value: str) -> None:
        self._struct.read_operations_text = value.encode('utf-8')

    @property
    def read_operations(self) -> int:
        return self._struct.read_operations
    
    @read_operations.setter
    def read_operations(self, value: int) -> None:
        self._struct.read_operations = value

    @property
    def verify_operations_text(self) -> str:
        return self._struct.verify_operations_text.decode('utf-8')

    @verify_operations_text.setter
    def verify_operations_text(self, value: str) -> None:
        self._struct.verify_operations_text = value.encode('utf-8')

    @property
    def verify_operations(self) -> int:
        return self._struct.verify_operations
    
    @verify_operations.setter
    def verify_operations(self, value: int) -> None:
        self._struct.verify_operations = value

    def set_status(self, status: PluginStatus, message: str, wait: bool = False) -> None:
        if len(message) > PLUGIN_MAXDISPLAYTEXT:
            raise ValueError("Status message too long")

        self._wait_for_status()
        self._struct.status = status.value
        self._struct.status_message = message.encode('utf-8')
        self._struct.new_status = True

        if wait:
            self._wait_for_status()

    def set_error(self, severity: ErrorSeverity, message: str, wait: bool = False) -> None:
        if len(message) > PLUGIN_MAXERRORTEXT:
            raise ValueError("Error message too long")

        self._wait_for_error()

        if severity.value > ErrorSeverity.ERRORWARNING.value:
            self._struct.error_count += 1

        self._struct.error_severity = severity.value
        self._struct.error_message = message.encode('utf-8')
        self._struct.new_error = True

        if wait:
            self._wait_for_error()

    def set_pretest_complete(self, wait: bool = False) -> None:
        self._struct.status = PluginStatus.PRE_TEST_PLUGIN_COMPLETED.value
        self._struct.new_status = True

        if wait:
            self._wait_for_status()
    
    def _wait_for_error(self) -> None:
        while self.test_running and self._struct.new_error:
            QCoreApplication.processEvents()

    def _wait_for_status(self) -> None:
        while self.test_running and self._struct.new_status:
            QCoreApplication.processEvents()

    def __del__(self):
        self._wait_for_error()
        self._wait_for_status()
        self._mem.close()
        self._mem.unlink()
