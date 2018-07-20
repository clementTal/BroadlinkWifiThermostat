import broadlink

class BroadlinkWifiThermostat:
    def __init__(self, mac, ip, name, advanced_config,
                 schedule_wd, schedule_we, min_temp, max_temp):
        self.host = ip
        self.port = 80
        self.mac = bytes.fromhex(''.join(reversed(mac.split(':'))))
        self.current_temp = None
        self.current_operation = None
        self.power = None
        self.target_temperature = None
        self.name = name
        self.loop_mode = json.loads(advanced_config)["loop_mode"]
        self.operation_list = [STATE_AUTO, STATE_IDLE, STATE_MANUAL]
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.state = 0
        self.freeze = 0
        self.advanced_config = json.loads(advanced_config)
        self.schedule = {CONF_WEEKDAY: json.loads(schedule_wd),
                         CONF_WEEKEND: json.loads(schedule_we)}
        self.set_advanced_config(self.advanced_config)
        self.set_schedule(self.schedule)

    def set_advanced_config(self, advanced_config):
        """Set the thermostat advanced config"""
        try:
            device = self.connect()
            if device.auth():
                device.set_advanced(advanced_config["loop_mode"],
                                    advanced_config["sen"],
                                    advanced_config["osv"],
                                    advanced_config["dif"],
                                    advanced_config["svh"],
                                    advanced_config["svl"],
                                    advanced_config["adj"],
                                    advanced_config["fre"],
                                    advanced_config["pon"])
        except timeout:
            _LOGGER.error("set_advanced_config timeout")

    def set_schedule(self, schedule):
        """Set the thermostat schedule"""
        try:
            device = self.connect()
            if device.auth():
                device.set_schedule(schedule[CONF_WEEKDAY],
                                    schedule[CONF_WEEKEND])
        except timeout:
            _LOGGER.error("set_schedule timeout")

    def power_on_off(self, power):
        """power on/off thermostat"""
        try:
            device = self.connect()
            if device.auth():
                if str(power) == STATE_IDLE:
                    device.set_power(POWER_OFF)
                else:
                    device.set_power(POWER_ON)
        except timeout:
            _LOGGER.error("power_on_off timeout")

    def set_temperature(self, temperature):
        """Set the thermostat target temperature"""
        try:
            device = self.connect()
            if device.auth():
                device.set_temp(float(temperature))
        except timeout:
            _LOGGER.error("set_temperature timeout")

    def set_operation_mode(self, mode):
        """Set the thermostat operation mode: [on, off, auto]"""
        try:
            device = self.connect()
            if device.auth():
                if mode == STATE_AUTO:
                    device.set_power(POWER_ON)
                    device.set_mode(AUTO, self.loop_mode)
                elif mode == STATE_MANUAL:
                    device.set_power(POWER_ON)
                    device.set_mode(MANUAL, self.loop_mode)
                elif mode == STATE_IDLE:
                    device.set_mode(MANUAL, self.loop_mode)
                    if self.freeze == 1:
                        device.set_temp(float(12))
                    else :
                        device.set_temp(float(0))
                    device.set_power(POWER_OFF)
        except timeout:
            _LOGGER.error("set_operation_mode timeout")

    def read_status(self):
        """Read thermostat data"""
        _LOGGER.debug("read_status")
        try:
            device = self.connect()
            if device.auth():
                data = device.get_full_status()
                self.current_temp = data['room_temp']
                self.target_temperature = data['thermostat_temp']
                self.current_operation = STATE_IDLE \
                    if \
                    data["power"] == 0 \
                    else \
                    (STATE_AUTO
                     if
                     data["auto_mode"] == 1
                     else
                     STATE_MANUAL)
                self.state = STATE_MANUAL if data["active"] == 0 \
                    else STATE_IDLE
                self.freeze = data['fre']
        except timeout:
            _LOGGER.error("read_status timeout")

    def connect(self):
        """Open a connexion"""
        return broadlink.gendevice(0x4EAD,
                                   (self.host,
                                    self.port),
                                   self.mac)
