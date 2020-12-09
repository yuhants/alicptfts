# Part of the code is adapated from Matthew Newville's package
# https://github.com/pyepics/newportxps 

## TODO: Remove the following two lines after development
import sys
sys.path.append(r'../lib')

import os
import time
from collections import OrderedDict
from configparser import ConfigParser
from sftpwrapper import SFTPWrapper

# Load Python.Net
# CLR namespaces are recognized as Python packages
import clr
from System import String
from System.Collections import *
clr.AddReference('Newport.XPS.CommandInterface')
from CommandInterfaceXPS import *

class NewportXPS:
    def __init__(self, host, port=5001, 
                 timeout=1000,
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
        self.stages = dict()    
        self.groups = dict()    # {'PointingLinear' : {GroupInfo},
                                #  'PointingRotary' : {GroupInfo},
                                #  'MovingLinear'   : {GroupInfo}}

        # Connect the controller and stages
        self.connected, self.initialized = False, False
        self.connect()
        if self.connected:
            self.initialize()

    def connect(self):
        ## TODO: error handling
        # Establish connection with XPS
        op = self._xps.OpenInstrument(self.host,
                                      self.port,
                                      self.timeout)
        log, err_log = self._xps.Login(self.username, self.password, str())

        res, ver, err_firmware = self._xps.FirmwareVersionGet(str(), str())
                                           # TODO: or InstallerVersionGet?
        self.firmware_ver = ver
        
        # Read group info from system.ini through SFTP
        self.ftpconn = SFTPWrapper()
        try:
            self.read_systemini()
        except:
            print('Cannot read system.ini!')
            return
        
        self.connected = True
            
    def read_systemini(self):
        """Get group info from system.ini
        
        Parse info to self.groups and self.stages
        """
        connected = self.ftpconn.connect(**self.ftpargs)
        if not connected:
            return False

        self.ftpconn.cwd(os.path.join(self.ftphome, 'Config'))
        lines = self.ftpconn.getlines('system.ini')
        self.ftpconn.close()

        # Rarse system.ini just read in
        conf = ConfigParser()
        conf.read_string('\n'.join(lines))

        # Register the group info
        for gtype, glist in conf.items('GROUPS'):
            if len(glist) > 0:
                for gname in glist.split(','):
                    gname = gname.strip()
                    self.groups[gname] = dict()
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
            ret, vel, acc, err = self._xps.PositionerMaximumVelocityAndAccelerationGet(sname,
                                                                                       float(), float(),
                                                                                       str())
            try:
                self.stages[sname]['max_velocity']  = vel
                self.stages[sname]['max_acceleration'] = acc
            except:
                print('Could not set max velocity/accleration for {0}'.format(sname))

            ## Travel limits can be set by PositionerUserTravelLimitsSet
            ret, min_target, max_target, err = self._xps.PositionerUserTravelLimitsGet(sname,
                                                                                       float(), float(),
                                                                                       str())
            try:
                self.stages[sname]['min_target'] = min_target
                self.stages[sname]['max_target'] = max_target
            except:
                print('Could not set travel limit for {0}'.format(sname))

    def save_file(self, rm_path, rm_fname, fname):
        connected = self.ftpconn.connect(**self.ftpargs)
        if not connected:
            return False

        self.ftpconn.cwd(os.path.join(self.ftphome, rm_path))
        self.ftpconn.save(rm_fname, fname)
        self.ftpconn.close()
    
    def upload_file(self, rm_path, rm_fname, fname):
        connected = self.ftpconn.connect(**self.ftpargs)
        if not connected:
            return False

        self.ftpconn.cwd(os.path.join(self.ftphome, rm_path))
        self.ftpconn.put(rm_fname, fname)
        self.ftpconn.close()
    
    def save_systemini(self):
        self.save_file('Config', 'system.ini', 'system.ini')

    def save_stagesini(self):
        self.save_file('Config', 'stages.ini', 'stages.ini')

    def upload_systemini(self):
        self.upload_file('Config', 'system.ini', 'system.ini')

    def upload_stagesini(self):
        self.upload_file('Config', 'stages.ini', 'stages.ini')

    def initialize(self):
        # Establish the motion groups, home the stages, etc.
        # Assume we have 3 SingleAxisGroup in self._groups
        for g in self.groups:
            self.kill_group(group=g)

        for g in self.groups:
            self.initialize_group(group=g, with_encoder=True, homing=True)

    def status(self):
        pass

    def configure_pointing(position, relative):
        """Configure the pointing mirror"""
        try:
            pos, ang = position[0], position[1]
        except:
            print('Error: "position" is an iterable containing position/angle')
            return False

        res0, err0 = self.move_group('PointingLinear', pos, 1, relative)
        if res0 != 0:
            print('Error:', err0)
            return False
        res1, err1 = self.move_group('PointingRotary', ang, 1, relative)
        if res1 != 0:
            print('Error:', err1)
            return False

        return True

    def scan(scan_range, repeat):
        """Perform a scan with data gathering"""
        positioner = self.get_positioner('MovingLinear')    # group and axis in string

        # Get the reference points
        # "plus", "minus", and "origin"
        if scan_range is None:
            minus = self.stages[positioner]['min_target']
            plus = self.stages[positioner]['max_target']
        else:
            try:
                minus, plus = scan_range[0], scan_range[1]
            except:
                print('Error: "scan_range" is an iterable ', end='')
                print('specifying the plus/minus limit')
                return False
            else:
                if minus < self.stages[positioner]['min_target'] or plus  > self.stages[positioner]['max_target']:
                    print('Error: invalid scan range')
                    return False

        origin = self.get_setpoint_position('MovingLinear', 1)[0]

        # TODO
        begin, end = None, None
        res, err = self._xps.GatheringConfigurationSet(positioner+'.CurrentPosition', 
                                                       positioner+'.CurrentVelocity',
                                                       positioner+'.CurrentAcceleration',
                                                       str())
        begin = time.time()
        self._xps.GatheringRun(100000, 8)   # num of data sets, time interval in servo cycles
                                            # TODO: find the right numbers
        
        # TODO: handle the error
        self.move_group('MovingLinear', plus, 1, false)
        for i in range(repeat):
            self.move_group('MovingLinear', minus, 1, false)
            self.move_group('MovingLinear', plus, 1, false)
        self.move_group('MovingLinear', minus, 1, false)
        self.move_group('MovingLinear', origin, 1, false)

        self._xps.GatheringStop()
        end = time.time()
        self._xps.GatheringStopAndSave()

        return True, begin, end

    def move_group(self, grp_name, value, nb_item, relative=False):
        group = self.get_group(grp_name)
        method = 'GroupMoveAbsolute'
        if relative:
            method = 'GroupMoveRelative'
        
        move = getattr(self._xps, method)
        res, err = move(group, [value], nb_item, str())
        return res, err

    def get_setpoint_position(self, grp_name, nb_item):
        group = self.get_group(grp_name)
        res, pos, err = self._xps.GroupPositionSetpointGet(group,
                                    [0.0],
                                    # [0.0 for i in range(nb_item)], # TODO
                                                                     # Change to this if not working
                                    nb_item, str())
        if res == 0:
            return pos
        else:
            pass

    ### Group actions
    def _group_action(self, method, group):
        exec_method = getattr(self._xps, method)
        res, err = exec_method(group, str())
        pass    # TODO: handle the error string

    def kill_group(self, grp_name):
        group = self.get_group(grp_name)
        method = 'GroupKill'
        self._group_action(method=method, group=group)

    def initialize_group(self, grp_name, with_encoder=True, homing=True):
        group = self.get_group(grp_name)
        method = 'GroupInitialize'
        if with_encoder:
            method = 'GroupInitializeWithEncoderCalibration'
        self._group_action(method=method, group=group)

        if homing:
            self.home_group(group=group)

    def home_group(self, grp_name):
        group = self.get_group(grp_name)
        method = 'GroupHomeSearch'
        self._group_action(method=method, group=group)
        
    def check_error(self):
        pass

    def set_scan_params(self, scan_params):
        # Set scan params if doesn't match with current values
        if scan_params is None:
            pass
        pass

    def get_group(self, grp_name):
        pass

    def get_positioner(self, grp_name):
        pass

if __name__ == '__main__':
    xps = NewportXPS(host='164.54.160.000', port=5001, timeout=10)
        