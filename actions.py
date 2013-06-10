# taken from: http://stackoverflow.com/questions/11906925/python-simulate-keydown
import ctypes, codes

LONG = ctypes.c_long
DWORD = ctypes.c_ulong
ULONG_PTR = ctypes.POINTER(DWORD)
WORD = ctypes.c_ushort

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (('dx', LONG),
                ('dy', LONG),
                ('mouseData', DWORD),
                ('dwFlags', DWORD),
                ('time', DWORD),
                ('dwExtraInfo', ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (('wVk', WORD),
                ('wScan', WORD),
                ('dwFlags', DWORD),
                ('time', DWORD),
                ('dwExtraInfo', ULONG_PTR))

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (('uMsg', DWORD),
                ('wParamL', WORD),
                ('wParamH', WORD))

class _INPUTunion(ctypes.Union):
    _fields_ = (('mi', MOUSEINPUT),
                ('ki', KEYBDINPUT),
                ('hi', HARDWAREINPUT))

class INPUT(ctypes.Structure):
    _fields_ = (('type', DWORD),
                ('union', _INPUTunion))

def SendInput(*inputs):
    nInputs = len(inputs)
    LPINPUT = INPUT * nInputs
    pInputs = LPINPUT(*inputs)
    cbSize = ctypes.c_int(ctypes.sizeof(INPUT))
    return ctypes.windll.user32.SendInput(nInputs, pInputs, cbSize)

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

def Input(structure):
    if isinstance(structure, MOUSEINPUT):
        SendInput(INPUT(INPUT_MOUSE, _INPUTunion(mi=structure)))
    elif isinstance(structure, KEYBDINPUT):
        SendInput(INPUT(INPUT_KEYBOARD, _INPUTunion(ki=structure)))
    else:
        raise TypeError('Cannot create INPUT structure!')

#Mouse inputs don't work as I haven't wanted to use them!!!
def Mouse(flags, x=0, y=0, data=0):
    minput = MOUSEINPUT(x, y, data, flags, 0, None)
    Input(minput)

def Keyboard(code, flags=0):
    kinput = KEYBDINPUT(code, code, flags, 0, None)
    Input(kinput)

def press_button(key_name):
    if not hasattr(codes, key_name):
        print 'key %s not found!' % key_name
        return
    key = getattr(codes, key_name)
    Keyboard(key)
    
    
    
    