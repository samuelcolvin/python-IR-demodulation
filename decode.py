from numpy import *
# import pylab
import json, pickle
from scipy.interpolate import interp1d
import settings

class IRDeamon(object):
    def __init__(self, processor, verbose = False):
        self._verbose = verbose
        self.det = Detect(verbose)
        self.ref = Reference(verbose)
        self.processor = processor
        self.min_length = int(settings.ENTIRE_MESSAGE_LENGTH*settings.RATE)
        self.message_length = int(settings.MESSAGE_LENGTH*settings.RATE)
        self.data=[]
      
    def process_signal(self, data):
#         if self._verbose:
#             print 'number of data points carried over: %d' % len(self.data)
        self.data.extend(data)
        while len(self.data) > self.min_length:
            test_result = self.ref.test_data(self.data)
            if test_result == 1 and len(self.data) - self.ref.start < self.min_length:
                self.data = self.data[self.ref.start:]
                return
            if test_result == 1:
                self.decode_message()
                self.data = self.data[self.ref.start + self.message_length:]
            elif test_result == 0:
                self.data = self.data[self.ref.start + self.message_length:]
            else:
                self.data = self.data[-self.min_length*2:]
                return
    
    def decode_message(self):
        if self._verbose:
            print 'index of detected message: %d' % self.ref.start
        action = self.det.detect_button(self.data[self.ref.start:])
        if action is not None:
            self.processor(action)

class Reference(object):
    def __init__(self, verbose = False):
        self._verbose = verbose
        self.error_threshold = settings.REFERENCE_THRESHOLD
        t = settings.REFERENCE_SINGAL_TIME
        self.test_samples = int(t*settings.RATE)
        self.x1 = linspace(0, t, self.test_samples) 
        self.x2 = linspace(0, t, settings.REFERENCE_INTERP_SAMPLES)
        self.example_ys = []
        self.fname = settings.REFERENCE_SIGNAL_FILENAME
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
        print 'reference signals saved to %s' % self.fname
        
    def test_data(self, data):
        if not self._interpolate(data):
            return -1
        self.ref_error = self._error(self.interp_func(self.x2))
        if self._verbose:
            print 'error in signal compared to reference: %0.3f%%' % self.ref_error
        if self.ref_error < self.error_threshold:
            return 1
        else:
            return 0
        
    def _error(self, y_vals):
        return mean(abs(y_vals - self.reference['y']))/mean(abs(self.reference['y']))*100
        
    def _interpolate(self, data):
        onoff = less(data, settings.THRESHOLD)*1
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
        try:
            self.reference = pickle.load(open(self.fname, 'rb'))
        except IOError:
            print '%s not found, loading blank reference' % self.fname
            self.reference = {'x': self.x2, 'y': zeros(len(self.x2))}
            

class Detect(object):
    def __init__(self, verbose = False):
        self._verbose = verbose
        self.codes = {}
        self.fname = settings.ACTIONS_FILENAME
        self._load_codes()
        
    def learn_action(self, action, data):
        message = Decode(data, self._verbose).message
        print 'setting %s == %s' %(action['name'], bin(message))
        self.codes[message]= action
        return message
        
    def save_actions(self):
        if self.codes == {}:
            print 'Nothing to save!'
            return
        dump_json_pretty(self.codes, self.fname)
        print '%d buttons saved' % len(self.codes)
        
    def detect_button(self, data):
        message = Decode(data, self._verbose).message
        if message not in self.codes.keys():
            if self._verbose:
                print 'unknown action: %s' % bin(message)
            return None
        else:
            return self.codes[message]
    
    def _load_codes(self):
        try:
            codes_str = json.load(open(self.fname, 'r'))
        except IOError:
            print '%s not found, unable to load actions definitions' % self.fname
        else:
            for code in codes_str:
                self.codes[int(code)] = codes_str[code]
            if self._verbose:
                for a in self.codes:
                    print '%s: %s >> %s' % (self.codes[a]['name'], bin(a), self.codes[a]['action'])

class Decode(object):
    def __init__(self, data, verbose = False):
        self._verbose = verbose
        delay = 0.007
        self._delay_s = int(delay * settings.RATE)
        self._msg_l_s = int(settings.MESSAGE_LENGTH * settings.RATE)
        all_onoff = less(data, settings.THRESHOLD)*1
        ilow = flatnonzero(all_onoff[self._delay_s:])
        self.start = self._delay_s + ilow[0] - 1
        ilow = flatnonzero(all_onoff[:self.start+self._msg_l_s])
        self.finish = ilow[-1]
        self.onoff = all_onoff[self.start:self.finish]
        self._data_length = len(self.onoff)
        self._calc_wave_length()
        self.bits = []
        self.bit_ranges=[]
        i=0
        while i != -1:
            i = self._generate_bit(i)    
        self._convert_bits(self.bits)
        
    def _calc_wave_length(self):
        self._step_size = []
        self._high_size = []
        steps = diff(self.onoff)
        stepi = flatnonzero(greater(steps[:self._delay_s], 0.5))
        for i in range(1,len(stepi)):
            self._step_size.append(stepi[i] - stepi[i-1])
        self._step_size = int(round(mean(self._step_size)))
        stepi = flatnonzero(greater(abs(steps[:self._delay_s]), 0.5))
        for i in range(1,len(stepi), 2):
            self._high_size.append(stepi[i] - stepi[i-1])
        self._high_size = int(round(mean(self._high_size)))
        if self._verbose:
            print 'step size: %d' % self._step_size
            print 'high size: %d' % self._high_size
    
    def _generate_bit(self, i):
        search_area = settings.DECODE_SEARCH_AREA
        this_size = self._step_size
        if self._data_length - i < self._step_size:
            this_size = self._data_length - i
        yes = zeros(this_size)
        yes[:self._high_size]=1
        yes_error = mean(abs(self.onoff[i:i+self._step_size] - yes))
        no_error = mean(abs(self.onoff[i:i+self._step_size]))
        bit = 1
        if no_error < yes_error:
            bit = 0
        self.bits.append(bit)
        self.bit_ranges.append([i, i+self._step_size])
        i += self._step_size
        if i > self._data_length:
            return -1
        steps = diff(self.onoff[i-search_area:i+search_area])
        stepi = flatnonzero(greater(steps,0.5))
        if len(stepi) > 1:
            if self._verbose:
                print 'Warning %d steps found!!!' % len(stepi)
        elif len(stepi) == 1:
            i = i - search_area + stepi[0]
        return i
    
    def _convert_bits(self, bits_old):    
        self.bits = bits_old[settings.BIT_HEADER:]
        self.bit_ranges = self.bit_ranges[settings.BIT_HEADER:]
        if len(self.bits) < 5:
            self.bits = []
            self.bit_ranges = []
            return
        msg_str = ''.join([str(b) for b in self.bits])
        self.message = int(msg_str, 2)

def dump_json_pretty(data, fname):
    json.dump(data, open(fname,'w'),
              sort_keys=True, indent=4, separators=(',', ': '))