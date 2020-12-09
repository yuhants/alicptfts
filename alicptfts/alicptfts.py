
import sys
#sys.path.append(r'C:\Windows\Microsoft.NET\assembly\GAC_64\Newport.XPS.CommandInterface\v4.0_2.2.1.0__9a267756cf640dcf')
sys.path.append(r'../lib')

import MC2000B_COMMAND_LIB as mc2000b
from newportxps import NewportXPS

from enum import Enum
class FTSState(Enum):
    NOTINIT = 0
    INIT = 1
    CONFIG = 2
    SCANNING = 3
    PAUSE = 4
    FINISH = 5

class IR518:
    def __init__(self):
        pass

class MC2000B:
    def __init__(self):
        pass

class AlicptFTS:
    def __init__(self):
        self._source = None
        self._chopper = None
        self._newportxps = None
        self._state = FTSState.NOTINIT

    def initialize(self, **kwargs):
        """Establish connection with each part"""
        self.check_sys_status('initialize')

        # TODO
        self._source = IR518()
        self._chopper = MC2000B()
        self._newportxps = NewportXPS(**kwargs)

        self._state = FTSState.INIT

    def configure(self, position, relative):
        """Configure the stages so that the FTS is ready to scan."""
        self.check_sys_status('configure')

        done = self._newportxps.configure_pointing(position=position,
                                                   relative=relative)
        if done:
            self._state = FTSState.CONFIG

    def scan(self, scan_params=None, scan_range=None, repeat=15):
        """Perform a scan with the configured stages.
        
        Parameters
        ----------
        scan_params : array of float, optional
            Scan parameters for the SGamma profile (see Newport XPS-D
            feature manual pp. 8-9). Use format
            [vel, acc, min_jerk_time, max_jerk_time]. Put not
            specificed parameters as "None".
            Will use default values if not specificed (None).
    
        scan_range : array of float, optional
            Minimum and maximum target positions. Use format 
            [min_target, max_target]. Put not specified parameters
            as "None".
            Will use default values if not specified (None).

        repeat : int
            Number of full back-and-forth scans (default is 15)
        """
        self.check_sys_status('scan')
        self._newportxps.set_scan_params(scan_params)
        
        self._state = FTSState.SCANNING
        done, begin, end = self._newportxps.scan(scan_range=scan_range, repeat=repeat)
        if done:
            self._state = FTSState.FINISH

    def save(self):
        """Save the gathered data after a scan"""
        self.check_sys_status('scan')

        pass

    def reboot(self):
        pass

    def status(self):
        pass

    def stop(self):
        self.check_sys_status('stop')

        stop = self._newportxps.action('ALL', 'STOP')
        if stop:
            self._state = FTSState.NOTINIT
    
    def pause(self):
        self.check_sys_status('pause')

        pause = self._newportxps.action('ALL', 'PAUSE')
        if pause:
            self._state = FTSState.PAUSE

    def resume(self):
        self.check_sys_status('resume')
        pass

    def check_sys_status(self, command):
        pass

    def close(self):
        pass

if __name__ == '__main__':
    fts = AlicptFTS()
    fts.initialize()
    fts.status()
    fts.configure(position=[50.0, 35.0], relative=False)
    fts.scan()
    fts.save()
    fts.close()
