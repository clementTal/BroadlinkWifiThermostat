import broadlink
import logging
from datetime import datetime
from socket import timeout

POWER_ON = 1
POWER_OFF = 0
AUTO = 1
MANUAL = 0
CONF_WEEKDAY = "weekday"
CONF_WEEKEND = "weekend"

STATE_HEAT = 'heat'
STATE_IDLE = 'idle'
STATE_OFF = 'off'
STATE_AUTO = 'auto'

_LOGGER = logging.getLogger(__name__)


class Thermostat:
    def __init__(self, mac, ip, name, use_external_temp=False, awayTemp=12):
        self.host = ip
        self.port = 80
        self.mac = bytes.fromhex(''.join(reversed(mac.split(':'))))
        self.current_temp = None
        self.external_temp = None
        self.current_operation = None
        self.power = None
        self.target_temperature = None
        self.name = name
        self.entity_id = "climate." + name
        self.state = 0
        self.use_external_temp = use_external_temp
        self.active = None
        self.away = False
        self.awayTemp = awayTemp
        self.loop_mode = 0

    def set_time(self):
        try:
            device = self.connect()
            if device.auth():
                now = datetime.now()
                device.set_time(now.hour, now.minute, now.second, now.weekday())
        except timeout:
            _LOGGER.error("set_schedule timeout")

    def set_advanced_config(self, loop_mode, sen, osv, dif, svh, svl, adj, fre, pon):
        """Set the thermostat advanced config"""
        try:
            device = self.connect()
            if device.auth():
                device.set_advanced(loop_mode, sen, osv, dif, svh,
                                    svl, adj, fre, pon)
                self.loop_mode = loop_mode
        except timeout:
            _LOGGER.error("set_advanced_config timeout")

    def set_schedule(self, week_start_1, week_stop_1,
                     week_start_2, week_stop_2,
                     week_start_3, week_stop_3,
                     weekend_start, weekend_stop,
                     away_temp, home_temp):
        """Set the thermostat schedule"""
        try:
            device = self.connect()
            if device.auth():
                weekday_conf_1_in = {}
                weekday_conf_2_in = {}
                weekday_conf_3_in = {}
                weekday_conf_1_out = {}
                weekday_conf_2_out = {}
                weekday_conf_3_out = {}
                weekend_conf_in = {}
                weekend_conf_out = {}

                weekday_conf_1_in["start_hour"] = int(week_start_1.strftime('%H'))
                weekday_conf_1_in["start_minute"] = int(week_start_1.strftime('%M'))
                weekday_conf_1_in["temp"] = float(home_temp)

                weekday_conf_1_out["start_hour"] = int(week_stop_1.strftime('%H'))
                weekday_conf_1_out["start_minute"] = int(week_stop_1.strftime('%M'))
                weekday_conf_1_out["temp"] = float(away_temp)

                weekday_conf_2_in["start_hour"] = int(week_start_2.strftime('%H'))
                weekday_conf_2_in["start_minute"] = int(week_start_2.strftime('%M'))
                weekday_conf_2_in["temp"] = float(home_temp)

                weekday_conf_2_out["start_hour"] = int(week_stop_2.strftime('%H'))
                weekday_conf_2_out["start_minute"] = int(week_stop_2.strftime('%M'))
                weekday_conf_2_out["temp"] = float(away_temp)

                weekday_conf_3_in["start_hour"] = int(week_start_3.strftime('%H'))
                weekday_conf_3_in["start_minute"] = int(week_start_3.strftime('%M'))
                weekday_conf_3_in["temp"] = float(home_temp)

                weekday_conf_3_out["start_hour"] = int(week_stop_3.strftime('%H'))
                weekday_conf_3_out["start_minute"] = int(week_stop_3.strftime('%M'))
                weekday_conf_3_out["temp"] = float(away_temp)

                weekend_conf_in["start_hour"] = int(weekend_start.strftime('%H'))
                weekend_conf_in["start_minute"] = int(weekend_start.strftime('%M'))
                weekend_conf_in["temp"] = float(home_temp)

                weekend_conf_out["start_hour"] = int(weekend_stop.strftime('%H'))
                weekend_conf_out["start_minute"] = int(weekend_stop.strftime('%M'))
                weekend_conf_out["temp"] = float(away_temp)

                weekday_conf = [weekday_conf_1_in, weekday_conf_1_out,
                                weekday_conf_2_in, weekday_conf_2_out,
                                weekday_conf_3_in, weekday_conf_3_out]
                weekend_conf = [weekend_conf_in, weekend_conf_out]

                device.set_schedule(weekday_conf,weekend_conf)
        except timeout:
            _LOGGER.error("set_schedule timeout")

    def power_on_off(self, power):
        """power on/off thermostat"""
        try:
            device = self.connect()
            if device.auth():
                if str(power) == STATE_OFF:
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
                elif mode == STATE_HEAT:
                    device.set_power(POWER_ON)
                    device.set_mode(MANUAL, self.loop_mode)
                elif mode == STATE_OFF:
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
                if self.use_external_temp:
                    self.current_temp = data['external_temp']
                else:
                    self.current_temp = data['room_temp']
                self.target_temperature = data['thermostat_temp']
                self.external_temp = data['external_temp']
                self.active = data['active']
                self.current_operation = STATE_OFF \
                    if \
                    data["power"] == 0 \
                    else \
                    (STATE_AUTO
                     if
                     data["auto_mode"] == 1
                     else
                     STATE_HEAT)
                self.state = STATE_HEAT if data["active"] == 1 \
                    else STATE_IDLE

        except timeout:
            _LOGGER.warning("read_status timeout")

    def set_away(self, is_away):
        try:
            device = self.connect()
            if device.auth():
                device.set_power(POWER_ON)
                if is_away:
                    device.set_mode(MANUAL, self.loop_mode)
                    device.set_temp(float(self.awayTemp))
                else:
                    device.set_mode(AUTO, self.loop_mode)
                self.away = is_away
        except timeout:
            _LOGGER.warning("setAway timeout")

    def connect(self):
        """Open a connexion"""
        return broadlink.gendevice(0x4EAD,
                                   (self.host,
                                    self.port),
                                   self.mac)
