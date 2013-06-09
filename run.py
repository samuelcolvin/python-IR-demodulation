import pylab, sys
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
    
def test_demod():
    ir = decode.IRDeamon(record.RATE, print_button, True)
    record.continuous(ir.process_signal, 20)
    
def do_press(button):
    if not hasattr(press_key.Buttons, button):
        print 'no such function in buttons class: %s' % button
    else:
        print button
        getattr(press_key.Buttons, button)()
    
def run():
    ir = decode.IRDeamon(record.RATE, do_press)
    record.continuous(ir.process_signal)

if __name__ == '__main__':
    usage = 'python-IR-demodulation, Samuel Colvin June 2013 Usage:\n run.py setup_refs || learn_buttons || test_demod || run_active'
    if len(sys.argv) != 2:
        print usage
    elif sys.argv[1] == 'setup_refs':
        setup_reference()
    elif sys.argv[1] == 'learn_buttons':
        learn_buttons()
    elif sys.argv[1] == 'test_demod':
        test_demod()
    elif sys.argv[1] == 'run_active':
        run()
    else:
        print usage
