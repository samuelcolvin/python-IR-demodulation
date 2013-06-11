import sys
import decode, monitor, settings, actions

def setup_reference():
    seconds = 2
    print 'Recording reference signals to help detect button press'
    ref = decode.Reference()
    for i in range(8):
        print 'Recording %d, press button now...' % i
        ref.add_example(monitor.record_for_time(seconds))
    print 'Finished recording reference signals'
        
    ref.save_reference()
    pylab.figure(1)
    colors = matplotlib.cm.rainbow(numpy.linspace(0, 1, len(ref.example_ys)))
    for y, c in zip(ref.example_ys, colors):
        pylab.plot(ref.x2, y, color=c, linewidth=0.5)

    pylab.title('Recorded Reference Signals')
    pylab.xlabel('Time (s)')
    pylab.ylabel('Amplitude')
    pylab.show()
    
def learn_actions():
    seconds = 3
    det = decode.Detect()
    ref = decode.Reference()
    current_settings = {}
    while True:
        for i, a in enumerate(settings.ACTIONS):
            if not current_settings.has_key(i):
                current_settings[i] = []
            print '%d: %s (%s)' % (i, a['name'], ', '.join(current_settings[i]))
        print '%d: finish' % (i + 1)
        choice = input('Enter number of button to set: ')
        if choice == i + 1:
            break
        action = settings.ACTIONS[choice]
        print 'press %s...' % action['name']
        data = monitor.record_for_time(seconds)
        print 'stop'
        detected = ref.test_data(data)
        print 'error in signal compared to reference: %0.3f %% (%0.3f%% max)' % (ref.ref_error, settings.REFERENCE_THRESHOLD)
        if detected == 1:
            data = data[ref.start:]
            msg = det.learn_action(action, data)
            current_settings[choice].append(bin(msg))
        else:
            print 'error compared to reference signal was too high.'
    det.save_actions()
    
def plot_signal():
    seconds = 4
    ref = decode.Reference(True)
    det = decode.Detect()
    print 'Recording, press button now...'
    data = monitor.record_for_time(seconds)
    print 'stop'
    print 'Message detected: %r' % (ref.test_data(data) == 1)
    if ref.start is not None:
        secs = ref.start/float(settings.RATE)
        print 'Start of message detected by reference: %d samples - %0.4f secs' % (ref.start, secs)
    pylab.figure(1)
    t =  numpy.linspace(0, seconds, len(data)) 
    pylab.plot(t, data, linewidth=0.5)
    pylab.title('Recorded Data')
    pylab.xlabel('Time (s)')
    pylab.ylabel('Amplitude')
    if ref.start is not None:
        pylab.figure(2)
        pylab.plot(ref.reference['x'], ref.reference['y'], 'k', linewidth=0.5)
        pylab.hold = True
        ref_data =  data[ref.start:ref.start + ref.test_samples]
        pylab.plot(ref.x1, ref_data, 'r', linewidth=0.5)
        pylab.title('Reference Signal Comparison')
        pylab.legend(['Reference Signal', 'Recorded Data'])
        pylab.xlabel('Time (s)')
        pylab.ylabel('Amplitude')
        data = data[ref.start:]
        dec = decode.Decode(data, True)
        print 'message received: %s' % bin(dec.message)
        secs = dec.start/float(settings.RATE)
        print 'length of header cut off: %d samples - %0.4f secs' % (dec.start, secs)
        secs = (dec.finish - dec.start)/float(settings.RATE)
        print 'length of message: %d samples - %0.4f secs' % (dec.finish - dec.start, secs)
        code = det.detect_action(dec.message)
        if code is not None:
            print 'message decodes as %s' % code['name']
        pylab.figure(3)
        pylab.subplot(211)
        data = data[dec.start:dec.finish]
        pylab.plot(range(len(data)), data, 'r')
        pylab.title('Signal Processing')
        pylab.xlabel('Samples')
        pylab.ylabel('Amplitude')
        pylab.subplot(212)
        pylab.plot(range(len(data)), dec.onoff*0.9, 'b')
        pylab.hold = True
        y= numpy.ones(len(data))*0.5
        for i, r in enumerate(dec.bit_ranges):
            y[r[0]:r[1]] = dec.bits[i]
            y[r[0]] = 0.5
            if r[1] < len(y):
                y[r[1]] = 0.5
        pylab.plot(range(len(data)), y, 'k', linewidth=2)
        pylab.legend(['on off', 'bits'])
        pylab.xlabel('Samples')
        pylab.ylabel('0/1')
        pylab.ylim([-0.05, 1.05])
        pylab.grid(True)
    pylab.show()
    
def print_button(action):
    print '    pressed: %s' % action['name']
    
def verbose_test():
    ir = decode.IRDeamon(print_button, True)
    monitor.continuous(ir.process_signal, 20)
    
def do_action(action):
    print action['name']
    actions.press_button(action['action'])
    
def run():
    ir = decode.IRDeamon(do_action)
    print 'Monitor Running...'
    monitor.continuous(ir.process_signal)
    
def print_usage():
    try:
        readme = open('README.md', 'r').read()
        usage = readme[readme.index('<!--usage-->')+12:readme.index('<!--/usage-->')]
        usage = usage.strip()
        usage = usage.replace('\t', '')
    except:
        usage = 'python-IR-demodulation see README.md for details.' 
    print usage

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print_usage()
    elif sys.argv[1] in ['setup_refs', 'plot_signal']:
        import pylab
        import matplotlib.cm
        import numpy
        if sys.argv[1] == 'setup_refs':
            setup_reference()
        elif sys.argv[1] == 'plot_signal':
            plot_signal()
    elif sys.argv[1] == 'learn_actions':
        learn_actions()
    elif sys.argv[1] == 'verbose_test':
        verbose_test()
    elif sys.argv[1] == 'run_active':
        run()
    else:
        print_usage()
