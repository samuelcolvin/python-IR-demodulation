import pylab, pdb
import matplotlib.cm as cm
from numpy import *
import decode, record, press_key
from scipy.interpolate import interp1d
import pickle

def setup_reference():
    RECORD_SECONDS = 2
    print 'Recording reference signals to help detect button press'
    ref = decode.Reference(record.RATE, 0)
    for i in range(8):
        print 'Recording %d, press button now...' % i
        ref.add_example(record.record_for_time(RECORD_SECONDS))

    print 'Finished recording reference signals'
        
    ref.save_reference()
    pylab.figure(1)
    colors = cm.rainbow(linspace(0, 1, len(ref.example_ys)))
    for y, c in zip(ref.example_ys, colors):
        pylab.plot(ref.x2, y, color=c, linewidth=0.5)

    pylab.title('Recorded Reference Signals')
    pylab.xlabel('Time (s)')
    pylab.ylabel('Amplitude')
    pylab.show()
    
def learn_buttons():
    RECORD_SECONDS = 3
    det = decode.Detect(record.RATE)
    ref = decode.Reference(record.RATE, 8)
    while True:
        for i, b in enumerate(det.buttons):
            print '%d: %s (%s)' % (i, b, det.current_settings[i])
        print '%d: finish' % (i + 1)
        choice = input('Enter number of button to set: ')
        if choice == i + 1:
            break
        button = det.buttons[choice]
        print 'press %s...' % button
        data = record.record_for_time(RECORD_SECONDS)
        print 'stop' 
        if ref.test_data(data) == 1:
            data = data[ref.start:]
            det.learn_button(button, data)
    det.save_buttons()
    
def print_button(button):
    print '    pressed: %s' % button
    
def test_buttons():
    RECORD_SECONDS = 4
    ir = decode.IRDeamon(record.RATE, print_button)
    for i in range(5):
        print 'Testing, press button now...'
        data = record.record_for_time(RECORD_SECONDS)
        ir.process_signal(data)
    
def do_press(button):
    if not hasattr(press_key.Buttons, button):
        print 'no such function in buttons class: %s' % button
    else:
        print 'pressing %s' % button
        getattr(press_key.Buttons, button)()
    
def run_deamon():
    RECORD_SECONDS = 4
    ir = decode.IRDeamon(record.RATE, do_press)
    record.continuous(ir.process_signal)
 
# setup_reference()
# learn_buttons()
run_deamon()


# def add_to_data(data_in):
    # global data
    # print 'adding to data'
    # data.extend(data_in)

# data=[]
# record.continuous(add_to_data)
# pylab.figure(1)
# t = linspace(0, 2, len(data))
# pylab.plot(t, data, linewidth=0.5)
# pylab.xlabel('Time (s)')
# pylab.ylabel('Amplitude')
# pylab.show()