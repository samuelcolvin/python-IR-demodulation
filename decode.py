from numpy import *
# import pylab
import pickle
from scipy.interpolate import interp1d
THRESHOLD = -10000
MESSAGE_LENGTH = 0.09
ENTIRE_MESSAGE_LENGTH = 0.15

class IRDeamon(object):
    def __init__(self, rate, processor, verbose = False):
        self._verbose = verbose
        self.det = Detect(rate, verbose)
        self.ref = Reference(rate, 15, verbose)
        self.processor = processor
        self.min_length = int((ENTIRE_MESSAGE_LENGTH)*rate)
        self.message_length = int(MESSAGE_LENGTH*rate)
        self.data=[]
      
    def process_signal(self, data):
        self.data.extend(data)
        while len(self.data) > self.min_length:
            test_result = self.ref.test_data(self.data)
            if test_result == 1 and len(self.data) - self.ref.start < self.min_length:
                break
            if test_result == 1:
                button = self.det.detect_button(self.data[self.ref.start:])
                if button is not None:
                    self.processor(button)
                self.data = self.data[self.ref.start + self.message_length:]
            elif test_result == 0:
                self.data = self.data[self.ref.start + self.message_length:]
            else:
                self.data = self.data[-self.min_length*2:]
                break
        if self._verbose:
            print 'number of data points carried over: %d' % len(self.data)
            
    # def plot_comparison(self, data):
        # x = linspace(0, len(data)/float(self.ref.rate), len(data))
        # pylab.plot(x, data, 'k', linewidth=0.5)
        # pylab.title('Recorded Reference Signals')
        # pylab.xlabel('Time (s)')
        # pylab.ylabel('Amplitude')
        # pylab.show()

class Reference(object):
    def __init__(self, rate, error_threshold, verbose = False):
        self._verbose = verbose
        self.t= 0.015
        self.error_threshold = error_threshold
        self.rate = rate
        self.test_samples = int(self.t*rate)
        record_samples = 400
        self.x2 = linspace(0, self.t, record_samples)
        self.x1 = linspace(0, self.t, self.test_samples) 
        self.example_ys = []
        self.fname = 'reference_signal.pkl'
        self.reference = None
        self.start = None
        self._load_reference()
        
    def add_example(self, data):
        if not self._interpolate(data):
            print 'No apparent signal, ignoring'
            return
        self.example_ys.append(self.interp_func(self.x2))
        
    def save_reference(self):
        if self.example_ys == []:
            print 'Nothing to save!'
            return
        self.reference = {'x': self.x2, 'y': mean(self.example_ys, axis=0)}
        for i, example in enumerate(self.example_ys):
            print 'Error from dataset %d: %0.3f%%' % (i, self._error(example))
        pickle.dump(self.reference, open(self.fname, 'wb'))
        
    def test_data(self, data):
        if not self._interpolate(data):
            return -1
        error = self._error(self.interp_func(self.x2))
        if error < self.error_threshold:
            return 1
        else:
            return 0
        if self._verbose:
            print 'error in signal compared to reference: %0.3f' % error
        
    def _error(self, y_vals):
        return mean(abs(y_vals - self.reference['y']))/mean(abs(self.reference['y']))*100
        
    def _interpolate(self, data):
        onoff = less(data, THRESHOLD)*1
        ion = flatnonzero(onoff)
        if len(ion) == 0:
            return False
        self.start = ion[0]
        finish = self.start + self.test_samples
        data = data[self.start:finish]
        if len(self.x1) != len(data):
            if self._verbose:
                print 'len(self.x1): %d, len(data): %s' % (len(self.x1), len(data))
            return False
        self.interp_func = interp1d(self.x1, data)
        return True
    
    def _load_reference(self):
        self.reference = pickle.load(open(self.fname, 'rb'))

class Detect(object):
    def __init__(self, rate, verbose = False):
        self._verbose = verbose
        self.rate = rate
        self.buttons = ['PLAYPAUSE', 'BACK', 'FORWARD', 'STOP', 'EJECT', 'PAUSE']
        self.current_settings = ['','','','','','']
        self.codes = {}
        self.fname = 'button_definitions.pkl'
        self._load_codes()
        
    def learn_button(self, button, data):
        message = decode(data, self.rate)
        print 'setting %s == %s' %(button, bin(message))
        self.codes[message]= button
        self.current_settings[self.buttons.index(button)] += '%s, ' % bin(message)
    
    def save_buttons(self):
        if self.codes == {}:
            print 'Nothing to save!'
            return
        pickle.dump(self.codes, open(self.fname, 'wb'))
        print '%d buttons saved' % len(self.codes)
        
    def detect_button(self, data):
        message = decode(data, self.rate)
        if message not in self.codes.keys():
            if self._verbose:
                print 'unknown button: %s' % bin(message)
            return None
        else:
            return self.codes[message]
    
    def _load_codes(self):
        self.codes = pickle.load(open(self.fname, 'rb'))

def decode(data, rate):
    delay = 0.007
    delay_s = int(delay * rate)
    msg_l_s = int(MESSAGE_LENGTH * rate)
    onoff = less(data, THRESHOLD)*1
    ilow = flatnonzero(onoff[delay_s:])
    start = delay_s + ilow[0] - 1
    ilow = flatnonzero(onoff[:start+msg_l_s])
    finish = ilow[-1]
    onoff = onoff[start:finish]
    data_length = len(onoff)
    steps = diff(onoff)
    step_size = 51 #[]
    high_size = 26 # []
    
    # stepi = flatnonzero(greater(steps[:delay_s], 0.5))
    # for i in range(1,len(stepi)):
        # step_size.append(stepi[i] - stepi[i-1])
    # step_size = int(round(mean(step_size)))
    # print 'step_size: %d' % step_size
    # stepi = flatnonzero(greater(abs(steps[:delay_s]), 0.5))
    # for i in range(1,len(stepi), 2):
        # high_size.append(stepi[i] - stepi[i-1])
    # high_size = int(round(mean(high_size)))
    # print 'high size: %d' % high_size

    bits = []
    i=0
    search_area = 40
    while True:
        this_size = step_size
        if data_length - i < step_size:
            this_size = data_length - i
        yes = zeros(this_size)
        yes[:high_size]=1
        yes_error = mean(abs(onoff[i:i+step_size] - yes))
        no_error = mean(abs(onoff[i:i+step_size]))
        bit = 1
        if no_error < yes_error:
            bit = 0
        bits.append(bit)
        i += step_size
        if i > data_length:
            break
        steps = diff(onoff[i-search_area:i+search_area])
        stepi = flatnonzero(greater(steps,0.5))
        if len(stepi) > 1:
            print 'Warning %d steps found!!!' % len(stepi)
        elif len(stepi) == 1:
            i = i - search_area + stepi[0]

    bits = bits[5:]
    if len(bits) < 5:
        return 0
    if len(bits) % 2 != 0:
        bits.append(0)
    message=[]
    for i in range(0, len(bits),2):
        message.append(bits[i]*bits[i+1])
    msg_str = ''.join([str(b) for b in message])
    return int(msg_str, 2)