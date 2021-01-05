# Part of the code is adapated from Matthew Newville's package
# https://github.com/pyepics/newportxps 

import os
import time
from collections import OrderedDict
from configparser import ConfigParser
from sftpwrapper import SFTPWrapper

import sys
sys.path.append(r'../lib')

# Load Python.Net
# CLR namespaces are recognized as Python packages
import clr
from System import String
from System.Collections import *
clr.AddReference('Newport.XPS.CommandInterface')
from CommandInterfaceXPS import *

import numpy as np

class XPSException(Exception):
    pass

class NewportXPS:
    def __init__(self, host, port=5001, timeout=1000,
                 username='Administrator',
                 password='Administrator'):
        self.host = host                # IP address
        self.port = port
        self.timeout = timeout
        self.username = username
        self.password = password

        self.ftphome = ''
        self.ftpconn = None
        self.ftpargs = dict(host=self.host,
                            username=self.username,
                            password=self.password)
        
        self._xps = XPS()
        self.firmware_ver = None
        self.stages = OrderedDict()    
        self.groups = OrderedDict()     # {'PointingLinear' : {GroupInfo},
                                        #  'PointingRotary' : {GroupInfo},
                                        #  'MovingLinear'   : {GroupInfo}}

        # Connect the controller and stages
        try:
            self.connect()
        except Exception:
            raise
        try:
            self.initialize()
        except Exception:
            raise

    def connect(self):
        """Connect to the XPS and read system.ini"""
        # Establish connection with XPS
        op = self._xps.OpenInstrument(self.host,
                                      self.port,
                                      self.timeout)
        try:
            self.check_error(op, 'Error: could not open XPS')
        except XPSException:
            raise
        else:
            print('Open {0} : {1}'.format(self.host, self.port))

        log, err_log = self._xps.Login(self.username, self.password, str())
        try:
            self.check_error(log, err_log)
        except XPSException:
            raise

        res, ver, err_firmware = self._xps.FirmwareVersionGet(str(), str())
                                           # TODO: or InstallerVersionGet?
        try:
            self.check_error(res, err_firmware)
        except XPSException:
            raise

        self.firmware_ver = ver
        
        # Read group info from system.ini through SFTP
        self.ftpconn = SFTPWrapper()
        try:
            self.read_systemini()
        except Exception:
            print('Error: could not read system.ini')
            raise
            
    def read_systemini(self):
        """Get group info from the system.ini file
        
        Parse info to self.groups and self.stages
        """
        try:
            self.ftpconn.connect(**self.ftpargs)
        except:
            raise
        try:
            self.ftpconn.cwd(os.path.join(self.ftphome, 'Config'))
        except IOError:
            raise
        try:
            lines = self.ftpconn.getlines('system.ini')
        except:
            raise
        self.ftpconn.close()

        # Rarse system.ini just read in
        conf = ConfigParser()
        try:
            conf.read_string('\n'.join(lines))
        except:
            print('Error: Could not parse lines from system.ini')
            raise

        # Register the group info
        for gtype, glist in conf.items('GROUPS'):
            if len(glist) > 0:
                for gname in glist.split(','):
                    gname = gname.strip()
                    self.groups[gname] = OrderedDict()
                    self.groups[gname]['category'] = gtype.strip()
                    self.groups[gname]['positioners'] = []

        for section in conf.sections():
            if section in ('DEFAULT', 'GENERAL', 'GROUPS'):
                continue
            items = conf.options(section)
            if section in self.groups:      # a group section
                poslist = conf.get(section, 'positionerinuse')
                posnames = [a.strip() for a in poslist.split(',')]
                self.groups[section]['positioners'] = posnames
            elif 'plugnumber' in items:     # a stage
                self.stages[section] = {'stagetype': conf.get(section, 'stagename')}
        
        for sname in self.stages:
            r_vel_acc, vel, acc, err_vel_acc = self._xps.PositionerMaximumVelocityAndAccelerationGet(sname, 
                                                                                                     float(), float(),
                                                                                                     str())
            try:
                self.check_error(r_vel_acc, err_vel_acc)
            except XPSException:
                raise
                
            try:
                self.stages[sname]['max_velocity']  = vel
                self.stages[sname]['max_acceleration'] = acc
            except:
                print('Error: Could not set max velocity/accleration for {0}'.format(sname))
                raise

            ## Travel limits can be set by PositionerUserTravelLimitsSet
            r_lim, min_target, max_target, err_lim = self._xps.PositionerUserTravelLimitsGet(sname,
                                                                                             float(), float(),
                                                                                             str())
            try:
                self.check_error(r_lim, err_lim)
            except:
                raise

            try:
                self.stages[sname]['min_target'] = min_target
                self.stages[sname]['max_target'] = max_target
            except:
                print('Error: Could not set travel limit for {0}'.format(sname))
                raise

    def initialize(self):
        """Establish the motion groups and optionally home the stages
        
        Currently implementation assumes three SingleAxisGroups
        in self._groups
        """
        for g in self.groups:
            try:
                self.kill_group(group=g)
            except Exception:
                print('Error: could not kill group {0} during initialization'.format(g))
                raise

        for g in self.groups:
            try:
                self.initialize_group(group=g, with_encoder=True, homing=True)
            except Exception:
                print('Error: could not initialize group {0}'.format(g))
                raise

    def configure_pointing(self, positions, relative):
        """Configure the pointing mirror
        
        Parameters
        ----------
        positions : array of float
            Target coordinates of the pointing mirror in (position, angle).

        relative : bool
            If relative is True, the pointing mirror is configured to the
            original coordinates plus "positions".
        """
        try:
            pos, ang = positions[0], positions[1]
        except Exception:
            print('Error: Could not set the position and angle')
            raise

        try:
            self.move_group('PointingLinear', pos, 1, relative, True)
        except Exception:
            raise

        try:
            self.move_group('PointingRotary', ang, 1, relative, True)
        except Exception:
            raise

    def scan(self, scan_range, repeat, gathering_params=(100000, 8)):
        """Perform a scan with data gathering
        
        Parameters
        ----------
        scan_range : array of float
            Minimum and maximum target positions. Use format 
            [min_target, max_target].
            Will use default values if None.

        repeat : int
            Number of full back-and-forth scans (default is 15).
        """
        try:
            positioner = self.get_positioner('MovingLinear')    # group and axis in string
        except:
            print('Error: Invalid group/positioner name')
            raise

        # Get the reference points (plus and minus ends)
        if scan_range is None:
            minus = self.stages[positioner]['min_target']
            plus = self.stages[positioner]['max_target']
        else:
            try:
                minus, plus = float(scan_range[0]), float(scan_range[1])
            except Exception:
                print('Error: Unable to get the plus and minus limits')
                raise
            else:
                if minus < self.stages[positioner]['min_target'] or plus  > self.stages[positioner]['max_target']:
                    raise ValueError('Error: Invalid scan range')

        # Get the origin (SetPointPosition of the homed stage)
        # Home the stage if not homed
        try:
            status = self.get_group_status('MovingLinear')
        except Exception:
            raise
        # Ready state from homing; see XPS Programming
        # Manual Sec. 8.8
        if status != 11:
            try:
                self.home_group('MovingLinear')
            except:
                raise
        try:
            origin = self.get_setpoint_position('MovingLinear', 1)[0]
        except Exception:
            print('Error: Unable to get the origin')
            raise

        # Begin scaning and data gathering
        timestamps = np.zeros(2*repeat + 4)
        res_confg, err_confg = self._xps.GatheringConfigurationSet(positioner+'.CurrentPosition', 
                                                                   positioner+'.CurrentVelocity',
                                                                   positioner+'.CurrentAcceleration',
                                                                   str())
        try:
            self.check_error(res_confg, err_confg)
        except XPSException:
            raise

        timestamps[0] = time.time()                             # First timestamp
                                                                # beginning of the scan
        res_run, err_run = self._xps.GatheringRun(gathering_params[0], gathering_params[1], str())
                                                  # num of data sets & time interval in servo cycles
                                                  # TODO: find the right/appropriate numbers
        try:
            self.check_error(res_run, err_run)
        except XPSException:
            raise
        
        try:
            moving_linear = self.get_group('MovingLinear')              # Get group for later use
        except:
            print('Error: Could not get the group of the MovingLinear stage')
            raise
        try:
            self.move_group(moving_linear, plus, 1, False, False)       # Move to the plus end
        except Exception:
            raise
        for i in range(repeat):                                         # Back-and-forth scans
            timestamps[2*i+1] = time.time()
            try:
                self.move_group(moving_linear, minus, 1, False, False)
            except Exception:
                raise
            timestamps[2*i+2] = time.time()
            try:
                self.move_group(moving_linear, plus, 1, False, False)
            except Exception:
                raise
        timestamps[-3] = time.time()
        try:
            self.move_group(moving_linear, minus, 1, False, False)     # minus end (for symmetry only...)
        except Exception:
            raise
        timestamps[-2] = time.time()
        try:
            self.move_group(moving_linear, origin, 1, False, False)    # Back to the origin
        except Exception:
            raise

        timestamps[-1] = time.time()
        res_stop, err_stop = self._xps.GatheringStop()
        try:
            self.check_error(res_stop, err_stop)
        except XPSException:
            raise
        res_save, err_save = self._xps.GatheringStopAndSave()
        try:
            self.check_error(res_save, err_save)
        except XPSException:
            raise

        return timestamps

    def move_group(self, grp_name, value, nb_item, relative=False, get_group=True):
        """Move a SingleAxisGroup"""
        if not get_group:
            try:
                group = self.get_group(grp_name)
            except:
                raise
        else:
            group = grp_name

        method = 'GroupMoveAbsolute'
        if relative:
            method = 'GroupMoveRelative'
        try:
            move = getattr(self._xps, method)
        except AttributeError:
            raise

        res, err = move(group, [value], nb_item, str())
        try:
            self.check_error(res, err)
        except XPSException:
            raise

    def get_setpoint_position(self, grp_name, nb_item):
        try:
            group = self.get_group(grp_name)
        except:
            raise

        res, pos, err = self._xps.GroupPositionSetpointGet(group,
                                    [0.0],
                                    # [0.0 for i in range(nb_item)], # TODO
                                                                     # Change to this if not working
                                    nb_item, str())
        try:
            self.check_error(res, err)
        except XPSException:
            raise

    ### Group actions
    def _group_action(self, method, group):
        try:
            exec_method = getattr(self._xps, method)
        except AttributeError:
            raise
        res, err = exec_method(group, str())
        try:
            self.check_error(res, err)
        except XPSException:
            raise

    def kill_group(self, grp_name):
        try:
            group = self.get_group(grp_name)
        except:
            raise

        method = 'GroupKill'
        try:
            self._group_action(method=method, group=group)
        except:
            raise

    def initialize_group(self, grp_name, with_encoder=True, homing=True):
        try:
            group = self.get_group(grp_name)
        except:
            raise

        method = 'GroupInitialize'
        if with_encoder:
            method = 'GroupInitializeWithEncoderCalibration'
        try:
            self._group_action(method=method, group=group)
        except:
            raise

        if homing:
            try:
                self.home_group(group=group)
            except:
                raise

    def home_group(self, grp_name):
        try:
            group = self.get_group(grp_name)
        except:
            raise

        method = 'GroupHomeSearch'
        try:
            self._group_action(method=method, group=group)
        except:
            raise

    def get_group_status(self, grp_name):
        try:
            group = self.get_group(grp_name)
        except Exception:
            raise

        res, status, err_status = self._xps.GroupStatusGet(group, 0, str())
        try:
            self.check_error(res, err_status)
        except XPSException:
            print('Error: Unable to check the group status')
            raise

        return status
        
    def check_error(self, res, err_string):
        if res != 0:
            raise XPSException(err_string)

    def save_file(self, rm_path, rm_fname, fname):
        """Save remote file to the current path"""
        try:
            self.ftpconn.connect(**self.ftpargs)
        except:
            raise
        try:
            self.ftpconn.cwd(os.path.join(self.ftphome, rm_path))
        except IOError:
            raise
        try:
            self.ftpconn.save(rm_fname, fname)
        except IOError:
            raise

        self.ftpconn.close()
    
    def upload_file(self, rm_path, rm_fname, fname):
        """Upload file to the remote path"""
        try:
            self.ftpconn.connect(**self.ftpargs)
        except:
            raise
        try:
            self.ftpconn.cwd(os.path.join(self.ftphome, rm_path))
        except:
            raise
        try:
            self.ftpconn.put(rm_fname, fname)
        except:
            raise

        self.ftpconn.close()
    
    def save_systemini(self):
        try:
            self.save_file('Config', 'system.ini', 'system.ini')
        except:
            raise

    def save_stagesini(self):
        try:
            self.save_file('Config', 'stages.ini', 'stages.ini')
        except:
            raise

    def save_gathering(self, fname):
        try:
            self.save_file('Public', 'GATHERING.DAT', fname)
        except:
            raise

    def upload_systemini(self):
        try:
            self.upload_file('Config', 'system.ini', 'system.ini')
        except:
            raise

    def upload_stagesini(self):
        try:
            self.upload_file('Config', 'stages.ini', 'stages.ini')
        except:
            raise

    ## TODO
    def set_scan_params(self, scan_params):
        # Set scan params if doesn't match with current values
        if scan_params is None:
            pass
        pass

    def get_group(self, grp_name):
        # print('Error: Invalid group name')
        pass

    def get_positioner(self, grp_name):
        pass

    def stop_all(self):
        """Abort any ongoing motions"""
        for g in self.groups:
            try:
                self.stop_group(g)
            except Exception:
                raise

    def pause_all(self):
        for g in self.groups:
            try:
                self.disable_group(g)
            except Exception:
                raise

    def resume_all(self):
        for g in self.groups:
            try:
                self.enable_group(g)
            except Exception:
                raise

    def _group_motion_state(self, method, group, msg):
        try:
            exec_method = getattr(self._xps, method)
        except AttributeError:
            raise

        res, err = exec_method(group, str())
        if res == -22:
            print(msg)
            return
        else:
            try:
                self.check_error(res, err)
            except XPSException:
                raise

    def stop_group(self, grp_name):
        try:
            group = self.get_group(grp_name)
        except:
            raise
        
        # Message for null result (doing nothing; not raising an exception)
        msg = 'Not aborting {0}: Group status not MOVING or JOGGING'.format(group)
        try:
            self._group_motion_state('GroupMoveAbort', group, msg)
        except Exception:
            raise

    def disable_group(self):
        try:
            group = self.get_group(grp_name)
        except:
            raise
        
        msg = 'Not disabling {0}: Group status not READY'.format(group)
        try:
            self._group_motion_state('GroupMotionDisable', group, msg)
        except Exception:
            raise

    def enable_group(self):
        try:
            group = self.get_group(grp_name)
        except:
            raise
        
        msg = 'Not enabling {0}: Group status not DISABLE'.format(group)
        try:
            self._group_motion_state('GroupMotionEnable', group, msg)
        except Exception:
            raise

    def status(self):
        pass

if __name__ == '__main__':
    xps = NewportXPS(host='164.54.160.000', port=5001, timeout=10)
        