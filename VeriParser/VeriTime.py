# VeriTime.py
#
# Classes and functions used for simulation time.

class TimeScale(object):
    ''' Has a scale and a precision amount. '''

    def __init__(self, scale=1, prec=1):
        self.scale = scale  # scale (what to multiple current delays by to convert them into fs)
        self.prec  = prec   # precision (fs)


    def _scale_to_fs(self, scaleL):
        ''' convert 2 item list of text such as [ '1', 'ns' ] to a
            scale value relative to fs.
            so 1 fs => 1
               10 fs => 10
               100 ps => 100000
        '''
        fs_in = { 'fs':1L, 'ps':1000L, 'ns':1000000L,
                  'us':1000000000L, 'ms':1000000000000L, 's':1000000000000000L
                }
        assert len(scaleL) == 2
        return int(scaleL[0]) * fs_in[scaleL[1]]


    def process_timescale_spec(self, scaleL, precL):
        ''' e.g. scaleL = [ '1', 'ns' ] 
                 precL  = [ '100', 'fs' ]
        '''
        self.scale = self._scale_to_fs(scaleL)
        self.prec  = self._scale_to_fs(precL )


    def __str__(self):
        return "scale=%d  prec=%d" % (self.scale, self.prec)
