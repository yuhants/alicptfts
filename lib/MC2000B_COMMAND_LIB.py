from ctypes import *

#region import dll functions
MC2000BLib = cdll.LoadLibrary("./lib/MC2000CommandLibWin64.dll")

"""comman command
"""
List = MC2000BLib.List
List.restype = c_int
List.argtypes = [c_char_p]

#GetPorts = MC2000BLib.GetPorts
#GetPorts.restype = c_int
#GetPorts.argtypes = [c_char_p]

Open = MC2000BLib.Open
Open.restype = c_int
Open.argtypes = [c_char_p,c_int,c_int]

IsOpen = MC2000BLib.IsOpen
IsOpen.restype = c_int
IsOpen.argtypes = [c_char_p]

Close = MC2000BLib.Close
Close.restype = c_int
Close.argtypes = [c_int]

"""device command
"""

SetFrequency = MC2000BLib.SetFrequency
SetFrequency.restype = c_int
SetFrequency.argtypes = [c_int,c_int]

GetFrequency = MC2000BLib.GetFrequency
GetFrequency.restype = c_int
GetFrequency.argtypes = [c_int, POINTER(c_int)]

SetBladeType = MC2000BLib.SetBladeType
SetBladeType.restype = c_int
SetBladeType.argtypes = [c_int,c_int]

GetBladeType = MC2000BLib.GetBladeType
GetBladeType.restype = c_int
GetBladeType.argtypes = [c_int,POINTER(c_int)]

SetHarmonicMultiplier = MC2000BLib.SetHarmonicMultiplier
SetHarmonicMultiplier.restype = c_int
SetHarmonicMultiplier.argtypes = [c_int,c_int]

GetHarmonicMultiplier = MC2000BLib.GetHarmonicMultiplier
GetHarmonicMultiplier.restype = c_int
GetHarmonicMultiplier.argtypes = [c_int,POINTER(c_int)]

SetHarmonicDivider = MC2000BLib.SetHarmonicDivider
SetHarmonicDivider.restype = c_int
SetHarmonicDivider.argtypes = [c_int,c_int]

GetHarmonicDivider = MC2000BLib.GetHarmonicDivider
GetHarmonicDivider.restype = c_int
GetHarmonicDivider.argtypes = [c_int,POINTER(c_int)]

SetPhase = MC2000BLib.SetPhase
SetPhase.restype = c_int
SetPhase.argtypes = [c_int,c_int]

GetPhase = MC2000BLib.GetPhase
GetPhase.restype = c_int
GetPhase.argtypes = [c_int,POINTER(c_int)]

SetEnable = MC2000BLib.SetEnable
SetEnable.restype = c_int
SetEnable.argtypes = [c_int,c_int]

GetEnable = MC2000BLib.GetEnable
GetEnable.restype = c_int
GetEnable.argtypes = [c_int,POINTER(c_int)]

SetReference = MC2000BLib.SetReference
SetReference.restype = c_int
SetReference.argtypes = [c_int,c_int]

GetReference = MC2000BLib.GetReference
GetReference.restype = c_int
GetReference.argtypes = [c_int,POINTER(c_int)]

SetReferenceOutput = MC2000BLib.SetReferenceOutput
SetReferenceOutput.restype = c_int
SetReferenceOutput.argtypes = [c_int,c_int]

GetReferenceOutput = MC2000BLib.GetReferenceOutput
GetReferenceOutput.restype = c_int
GetReferenceOutput.argtypes = [c_int,POINTER(c_int)]

SetDisplayIntensity = MC2000BLib.SetDisplayIntensity
SetDisplayIntensity.restype = c_int
SetDisplayIntensity.argtypes = [c_int,c_int]

GetDisplayIntensity = MC2000BLib.GetDisplayIntensity
GetDisplayIntensity.restype = c_int
GetDisplayIntensity.argtypes = [c_int,POINTER(c_int)]

GetReferenceFrequency = MC2000BLib.GetReferenceFrequency
GetReferenceFrequency.restype = c_int
GetReferenceFrequency.argtypes = [c_int,POINTER(c_int)]

Restore = MC2000BLib.Restore
Restore.restype = c_int
Restore.argtypes = [c_int]

GetVerbose = MC2000BLib.GetVerbose
GetVerbose.restype = c_int
GetVerbose.argtypes = [c_int,POINTER(c_int)]

SetVerbose = MC2000BLib.SetVerbose
SetVerbose.restype = c_int
SetVerbose.argtypes = [c_int,c_int]

SetLanguage = MC2000BLib.SetLanguage
SetLanguage.restype = c_int
SetLanguage.argtypes = [c_int,c_int]

GetLocked = MC2000BLib.GetLocked
GetLocked.restype = c_int
GetLocked.argtypes = [c_int,POINTER(c_int)]

GetCycleAdjust = MC2000BLib.GetCycleAdjust
GetCycleAdjust.restype = c_int
GetCycleAdjust.argtypes = [c_int,POINTER(c_int)]

SetCycleAdjust = MC2000BLib.SetCycleAdjust
SetCycleAdjust.restype = c_int
SetCycleAdjust.argtypes = [c_int,c_int]

GetReferenceOutFrequency = MC2000BLib.GetReferenceOutFrequency
GetReferenceOutFrequency.restype = c_int
GetReferenceOutFrequency.argtypes = [c_int,POINTER(c_int)]


#region command for MC2000B
def MC2000BListDevices():
    """ List all connected MC2000B devices
    Returns: 
       The MC2000B device list, each deice item is [serialNumber, MC2000BType]
    """
    str = create_string_buffer(1024, '\0')
    result = List(str)
    devicesStr = str.raw.decode("utf-8").rstrip('\x00').split(',')
    length = len(devicesStr)
    i = 0
    devices = []
    devInfo = ["",""]
    while(i < length):
        str = devicesStr[i]
        if (i % 2 == 0):
            if str != '':
                devInfo[0] = str
            else:
                i+=1
        else:
                if(str.find("MC2000B") >= 0):
                    isFind = True
                devInfo[1] = str
                devices.append(devInfo.copy())
        i+=1
    return devices

def MC2000BOpen(serialNo, nBaud, timeout):
    """ Open MC2000B device
    Args:
        serialNo: serial number of MC2000B device
        nBaud: bit per second of port
        timeout: set timeout value in (s)
    Returns: 
        non-negative number: hdl number returned Successful; negative number: failed.
    """
    return Open(serialNo.encode('utf-8'), nBaud, timeout)

def MC2000BIsOpen(serialNo):
    """ Check opened status of MC2000B device
    Args:
        serialNo: serial number of MC2000B device
    Returns: 
        0: MC2000B device is not opened; 1: MC2000B device is opened.
    """
    return IsOpen(serialNo.encode('utf-8'))

def MC2000BClose(hdl):
    """ Close opened MC2000B device
    Args:
        hdl: the handle of opened MC2000B device
    Returns: 
        0: Success; negative number: failed.
    """
    return Close(hdl)


def MC2000BSetFrequency(hdl,frequency):
    """ Set the desired internal reference frequency.
    Args:
        hdl: the handle of opened MC2000B device
        frequency:desired internal reference frequency
    Returns: 
        0: Success; negative number: failed.
    """
    return SetFrequency(hdl,frequency)

def MC2000BGetFrequency(hdl,frequency):
    """  Get the internal reference frequency
    Args:
        hdl: the handle of opened MC2000B device
        frequency:get internal reference frequency
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetFrequency(hdl,val)
    frequency[0] = val.value
    return ret

def MC2000BSetBladeType(hdl,bladetype):
    """ Set the blade type
    Args:
        hdl: the handle of opened MC2000B device
        bladetype: desired blade type
    Returns: 
        0: Success; negative number: failed.
    """
    return SetBladeType(hdl,bladetype)

def MC2000BGetBladeType(hdl, bladetype):
    """ Get the blade type
    Args:
        hdl: the handle of opened MC2000B device
        bladetype: pointer to the blade type
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetBladeType(hdl,val)
    bladetype[0] = val.value
    return ret

def MC2000BSetHarmonicMultiplier(hdl,nharmonic):
    """ Set Harmonic Multiplier applied to external reference frequency
    Args:
        hdl: the handle of opened MC2000B device
        nharmonic: desired harmonic multiplier
    Returns: 
        0: Success; negative number: failed.
    """
    return SetHarmonicMultiplier(hdl,nharmonic)

def MC2000BGetHarmonicMultiplier(hdl, nharmonic):
    """ Get Harmonic Multiplier applied to external reference frequency
    Args:
        hdl: the handle of opened MC2000B device
        nharmonic: pointer to the harmonic multiplier
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetHarmonicMultiplier(hdl,val)
    nharmonic[0] = val.value
    return ret

def MC2000BSetHarmonicDivider(hdl,dharmonic):
    """ Set the Harmonic Divider applied to external reference frequency
    Args:
        hdl: the handle of opened MC2000B device
        dharmonic: desired harmonic divider applied to external reference frequency
    Returns: 
        0: Success; negative number: failed.
    """
    return SetHarmonicDivider(hdl,dharmonic)

def MC2000BGetHarmonicDivider(hdl,dharmonic):
    """ Get the Harmonic Divider applied to external reference frequency
    Args:
        hdl: the handle of opened MC2000B device
        dharmonic: pointer to the harmonic divider applied to external reference frequency
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetHarmonicDivider(hdl,val)
    dharmonic[0] = val.value
    return ret

def MC2000BSetPhase(hdl,phase):
    """ Set the Phase adjust
    Args:
        hdl: the handle of opened MC2000B device
        phase: desired phase adjust
    Returns: 
        0: Success; negative number: failed.
    """
    return SetPhase(hdl,phase)

def MC2000BGetPhase(hdl,phase):
    """ Get the Phase adjust
    Args:
        hdl: the handle of opened MC2000B device
        phase: pointer to the phase adjust
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetPhase(hdl,val)
    phase[0] = val.value
    return ret

def MC2000BSetEnable(hdl,enable):
    """ Set enable or disable state of device
    Args:
        hdl: the handle of opened MC2000B device
        enable: enable state 1:enable, 0:disable.
    Returns: 
        0: Success; negative number: failed.
    """
    return SetEnable(hdl,enable)

def MC2000BGetEnable(hdl,enable):
    """ Get enable or disable state of device
    Args:
        hdl: the handle of opened MC2000B device
        enable: pointer to enable state 1:enable, 0:disable
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetEnable(hdl,val)
    enable[0] = val.value
    return ret

def MC2000BSetReference(hdl,ref):
    """ Set the reference mode
    Args:
        hdl: the handle of opened MC2000B device
        ref: reference mode 1:external, 0:internal
             reference high pre
    Returns: 
        0: Success; negative number: failed.
    """
    return SetReference(hdl,ref)

def MC2000BGetReference(hdl,ref):
    """ Get the reference mode
    Args:
        hdl: the handle of opened MC2000B device
        ref: pointer to reference mode 1:external, 0:internal
                        reference high precision mode 0:InternalOuter 1:InternalInner 2:ExternalOuter 3:ExternalInner    
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetReference(hdl,val)
    ref[0] = val.value
    return ret

def MC2000BSetReferenceOutput(hdl,output):
    """ Set the output reference mode
    Args:
        hdl: the handle of opened MC2000B device
        output: output mode 1:actual, 0:target
    Returns: 
        0: Success; negative number: failed.
    """
    return SetReferenceOutput(hdl,output)

def MC2000BGetReferenceOutput(hdl,output):
    """ Get the output reference mode
    Args:
        hdl: the handle of opened MC2000B device
        output: pointer to the output mode 1:actual, 0:target
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetReferenceOutput(hdl,val)
    output[0] = val.value
    return ret

def MC2000BSetDisplayIntensity(hdl,intensity):
    """ Set the display intensity (1-10).
    Args:
        hdl: the handle of opened MC2000B device
        intensity: display intensity (1-10)
    Returns: 
        0: Success; negative number: failed.
    """
    return SetDisplayIntensity(hdl,intensity)

def MC2000BGetDisplayIntensity(hdl,intensity):
    """  Get the display intensity (1-10).
    Args:
        hdl: the handle of opened MC2000B device
        intensity: pointer to display intensity (1-10)
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetDisplayIntensity(hdl,val)
    intensity[0] = val.value
    return ret

def MC2000BGetReferenceFrequency(hdl,frequence):
    """ Get the current supplied external reference frequency.
    Args:
        hdl: the handle of opened MC2000B device
        frequence: pointer to the current supplied external reference frequency.
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetReferenceFrequency(hdl,val)
    frequence[0] = val.value
    return ret

def MC2000BRestore(hdl):
    """ Restore the factory default parameters.
    Args:
        hdl: the handle of opened MC2000B device
    Returns: 
        0: Success; negative number: failed.
    """
    return Restore(hdl)

def MC2000BGetVerbose(hdl,verbose):
    """ Get the verbose mode.
    Args:
        hdl: the handle of opened MC2000B device
        verbose: verbose mode
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetVerbose(hdl,val)
    verbose[0] = val.value
    return ret

def MC2000BSetVerbose(hdl,verbose):
    """ Set the verbose mode.
    Args:
        hdl: the handle of opened MC2000B device
        verbose: verbose mode. When verbose mode is set to 1, status messages are output on the USB
    Returns: 
        0: Success; negative number: failed.
    """
    return SetVerbose(hdl,verbose)


def MC2000BSetLanguage(hdl,lang):
    """ Set display language in the device.
    Args:
        hdl: the handle of opened MC2000B device
        lang: language mode. 1: English, 0: Chinese
    Returns: 
        0: Success; negative number: failed.
    """
    return SetLanguage(hdl,lang)

def MC2000BGetLocked(hdl,lock):
    """ Get the lock state.
    Args:
        hdl: the handle of opened MC2000B device
        lock: pointer to the lock state
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetLocked(hdl,val)
    lock[0] = val.value
    return ret

def MC2000BGetCycleAdjust(hdl,cycle):
    """ Get the cycle adjustment.
    Args:
        hdl: the handle of opened MC2000B device
        cycle: pointer to the cycle adjustment
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetCycleAdjust(hdl,val)
    cycle[0] = val.value
    return ret

def MC2000BSetCycleAdjust(hdl,cycle):
    """  Set the cycle adjustment.
    Args:
        hdl: the handle of opened MC2000B device
        cycle: the desired cycle adjustment
    Returns: 
        0: Success; negative number: failed.
    """
    return SetCycleAdjust(hdl,cycle)

def MC2000BGetReferenceOutFrequency(hdl,freq):
    """ Get actual frequency of blade spinning
    Args:
        hdl: the handle of opened MC2000B device
        freq: pointer to the actual frequency
    Returns: 
        0: Success; negative number: failed.
    """
    val = c_int(0)
    ret = GetReferenceOutFrequency(hdl,val)
    freq[0] = val.value
    return ret

