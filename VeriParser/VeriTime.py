# VeriTime.py
#
# Classes and functions used for simulation time.

class TimeScale(object):
    ''' Has a scale and a precision amount. '''

    def __init__(self, scale=1, prec=1):
        self.scale = scale  # scale (what to multiple current delays by to convert them into fs)
        self.prec  = prec   # precision (fs)


    def process_timescale_spec(self, scaleL, precL):
        ''' e.g. scaleL = [ '1', 'ns' ] 
                 precL  = [ '100', 'fs' ]
        '''
        print scaleL, precL
