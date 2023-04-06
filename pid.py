class PID:
    """Simple PID controller with clamping of the signal and individual components."""

    kp: int = 1
    ki: int = 0
    kd: int = 0
    target: float

    _sig_max: int
    _sig_min: int

    _err: float = 0
    _current: float = 0

    _signal: int
    _p: int = 0
    _i: int = 0
    _d: int = 0

    _read_value: function

    def p(self) -> int:
        return self._p

    def i(self) -> int:
        return self._i

    def d(self) -> int:
        return self._d

    def current(self) -> float:
        return self._current

    def signal(self) -> int:
        return self._signal

    def _prevent_windup(self, value: int) -> int:
      ''' Limit the signal to ±sig_max. '''
      if value < -self._sig_max:
          return -self._sig_min
      if value > self._sig_max:
          return self._sig_max
      return int(value)

    def _clamp_signal(self, value: int) -> int:
      ''' Limit the signal to the interval min ≤ sig ≤ max. '''
      if value < self._sig_min:
          return self._sig_min
      if value > self._sig_max:
          return self._sig_max
      return value

    def __init__(self, target: float, sampler, sig_min: int, sig_max: int, inverse=False):
        """
        Construct a new PID for a given target value using a sample function to read current values.

        :param int target: The target value that the regulator shouid reach.
        :param def function: Function called to get the current value.
        """
        self.target = target
        self._sig_min = sig_min
        self._sig_max = sig_max
        self._read_value = sampler
        self._inverse = inverse

    def sample(self) -> tuple[int, int]:
        """
        Sample a value and update the state of the PID controller.
        :return: Return the sampled value and current signal as a tuple.
        :rtype: tuple[int, int]
        """

        self._current = self._read_value()
        # positive error if sample is bigger than target else positive error if sample is smaller than target
        old_err = self._err
        self._err = (self._current - self.target) if self._inverse else (self.target - self._current)

        self._p = self.kp * self._err
        # interval assumed to be one unit of time
        self._i = self._prevent_windup(self.ki * self._err + self._i)
        self._d = self.kd * (self._err - old_err)

        self._signal = self._clamp_signal(self._p + self._i + self._d)

        return self._current, self._signal
