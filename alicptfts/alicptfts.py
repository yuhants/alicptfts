
import sys
sys.path.append(r'../lib')

import MC2000B_COMMAND_LIB as mc2000b
from newportxps import NewportXPS, XPSException

import traceback
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
        self.source = None
        self.chopper = None
        self.newportxps = None
        self.state = FTSState.NOTINIT

    def initialize(self, **kwargs):
        """Establish connection with each part.
        
        Parameters
        ----------
        host : string
            IP address of the XPS controller.

        port : int
            Port number of the XPS controller (default is 5001).

        timeout : int
            Receive timeout of the XPS in milliseconds 
            (default is 1000). Note that send timeout is set to
            1000 milliseconds.

        username : string (default is Administrator)

        password : string (default is Administrator)

        """
        self.check_sys_status('initialize')

        # TODO
        # Current implementation only considers the XPS controller
        self.source = IR518()
        self.chopper = MC2000B()
        try:
            self.newportxps = NewportXPS(**kwargs)
        except XPSException:
            pass
        except:
            pass

        self.state = FTSState.INIT

    def configure(self, positions, relative=False):
        """Configure the stages so that the FTS is ready to scan.
        
        Parameters
        ----------
        positions : array of float
            Target coordinates of the pointing mirror in (position, angle).

        relative : bool
            If relative is True, the pointing mirror is configured to the
            original coordinates plus "positions" (default is False).
        """
        # TODO: check the moving mirror and other parts
        # through "check_sys_status"
        self.check_sys_status('configure')
        try:
            self.newportxps.configure_pointing(positions=positions, relative=relative)
        except XPSException:
            pass
        except:
            pass

        self.state = FTSState.CONFIG

    def scan(self, scan_params=None, scan_range=None, repeat=15):
        """Perform a scan with the configured stages.
        
        Parameters
        ----------
        scan_params : array of float, optional
            Scan parameters for the SGamma profile (see Newport XPS-D
            feature manual pp. 8-9). Use format
            [vel, acc, min_jerk_time, max_jerk_time]. Simply put not-
            specificed parameters as "None".
            Will use default values if not specificed (None).
    
        scan_range : array of float, optional
            Minimum and maximum target positions. Use format 
            [min_target, max_target].
            Will use default values if not specified (None).

        repeat : int
            Number of full back-and-forth scans (default is 15).
        """
        self.check_sys_status('scan')
        try:
            self.newportxps.set_scan_params(scan_params)
        except:
            pass
        
        self.state = FTSState.SCANNING
        try:
            timestamps = self.newportxps.scan(scan_range=scan_range, repeat=repeat)
        except XPSException:
            pass
        except:
            # self.state = FTSState.NOTINIT
            pass
        else:
            self.state = FTSState.FINISH
            return timestamps

    def save(self, timestamps=None, tname='TIMESTAMPS.DAT', fname='GATHERING.DAT'):
        """Save the gathering data and timestamps after a scan.
        
        Parameters
        ----------
        timestamps: array of float
            Timestamps for data points reported by the "scan()" 
            function. If None then no timestamps will be saved.

        tname: string
            Name of the file storing the timestamps (default is
            'TIMESTAMPS.DAT'). May specify absolute path.

        fname: string
            Name of the file storing the gathering data, including
            encoder positions and velocities (default is 
            'GATHEIRNG.DAT'). May specify absolute path.
        """
        self.check_sys_status('save')
        try:
            self.newportxps.save_gathering(fname)
        except:
            pass

        if timestamps is not None:
            self.save_timestamps(timestamps, tname)

    def reboot(self):
        self.check_sys_status('reboot')
        pass

    def stop(self):
        self.check_sys_status('stop')
        try:
            self.newportxps.stop_all()
        except:
                pass
    
    def pause(self):
        self.check_sys_status('pause')
        try:
            self.newportxps.pause_all()
        except:
            pass

    def resume(self):
        self.check_sys_status('resume')
        try:
            self.newportxps.resume_all()
        except:
            pass

    def status(self):
        self.check_sys_status('status')
        pass

    def check_sys_status(self, command):
        pass

    def save_timestamps(self, timestamps, tname):
        np.savetxt(tname, np.array(timestamps), delimiter=' ')

    def close(self):
        pass

if __name__ == '__main__':
    fts = AlicptFTS()
    fts.initialize()
    fts.status()
    fts.configure(position=[50.0, 35.0], relative=False)
    timestamps = fts.scan()
    fts.save(timestamps=timestamps)
    fts.close()
