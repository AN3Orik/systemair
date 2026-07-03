"""Legacy Residential / D24810 device profile."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorStateClass
from homeassistant.const import PERCENTAGE, REVOLUTIONS_PER_MINUTE, EntityCategory, Platform, UnitOfTime

from custom_components.systemair.const import API_TYPE_MODBUS_SERIAL, API_TYPE_MODBUS_TCP
from custom_components.systemair.modbus import IntegerType, ModbusParameter, RegisterType
from custom_components.systemair.profiles.base import DeviceProfile, ProfileEntityDescriptions
from custom_components.systemair.profiles.entities import (
    BinarySensorProfileEntity,
    NumberProfileEntity,
    SelectProfileEntity,
    SensorProfileEntity,
    SwitchProfileEntity,
)


def _uint(  # noqa: PLR0913 - local builder mirrors ModbusParameter fields.
    register: int,
    short: str,
    description: str,
    *,
    scale_factor: int | None = None,
    min_value: int | None = None,
    max_value: int | None = None,
) -> ModbusParameter:
    return ModbusParameter(
        register=register,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short=short,
        description=description,
        scale_factor=scale_factor,
        min_value=min_value,
        max_value=max_value,
    )


def _int(  # noqa: PLR0913 - local builder mirrors ModbusParameter fields.
    register: int,
    short: str,
    description: str,
    *,
    scale_factor: int | None = None,
    min_value: int | None = None,
    max_value: int | None = None,
) -> ModbusParameter:
    return ModbusParameter(
        register=register,
        sig=IntegerType.INT,
        reg_type=RegisterType.Holding,
        short=short,
        description=description,
        scale_factor=scale_factor,
        min_value=min_value,
        max_value=max_value,
    )


def _bool(register: int, short: str, description: str) -> ModbusParameter:
    return ModbusParameter(
        register=register,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short=short,
        description=description,
        boolean=True,
        min_value=0,
        max_value=1,
    )


def _week_program_parameters() -> list[ModbusParameter]:
    parameters = [
        _bool(401, "REG_WP_ACTIVE", "Week program active. Coil 6401."),
        _uint(402, "REG_WP_ON_LVL", "Week program active speed level.", min_value=0, max_value=4),
        _uint(403, "REG_WP_OFF_LVL", "Week program inactive speed level.", min_value=0, max_value=4),
    ]

    register = 404
    for day in range(1, 8):
        for period in range(1, 3):
            parameters.extend(
                [
                    _uint(
                        register,
                        f"REG_WP_WD{day}_PRD{period}_START_H",
                        f"Week program day {day}, period {period}, start hour.",
                        min_value=0,
                        max_value=23,
                    ),
                    _uint(
                        register + 1,
                        f"REG_WP_WD{day}_PRD{period}_START_M",
                        f"Week program day {day}, period {period}, start minute.",
                        min_value=0,
                        max_value=59,
                    ),
                    _uint(
                        register + 2,
                        f"REG_WP_WD{day}_PRD{period}_END_H",
                        f"Week program day {day}, period {period}, end hour.",
                        min_value=0,
                        max_value=23,
                    ),
                    _uint(
                        register + 3,
                        f"REG_WP_WD{day}_PRD{period}_END_M",
                        f"Week program day {day}, period {period}, end minute.",
                        min_value=0,
                        max_value=59,
                    ),
                ]
            )
            register += 4
    return parameters


def _wireless_node_parameters() -> list[ModbusParameter]:
    parameters: list[ModbusParameter] = []
    for node in range(1, 11):
        base = 901 + ((node - 1) * 10)
        parameters.extend(
            [
                _uint(
                    base,
                    f"REG_WL_NODE_{node}_TYPE",
                    f"Wireless node {node} type. 0: none, 1: CO2, 2: RH, 3: DI module, 4: user interface.",
                    min_value=0,
                    max_value=4,
                ),
                _uint(base + 1, f"REG_WL_NODE_{node}_VALUE_T", f"Wireless node {node} value depending on node type."),
                _uint(
                    base + 2,
                    f"REG_WL_NODE_{node}_STATUS",
                    f"Wireless node {node} status. 0: not bound, 1: OK, 2: battery failure, "
                    "3: communication failure, 4: no network, 5: sensor failure.",
                    min_value=0,
                    max_value=5,
                ),
            ]
        )
        parameters.extend(
            _uint(
                base + offset,
                f"REG_WL_NODE_{node}_RESERVED_{offset}",
                f"Wireless node {node} reserved register {offset}.",
            )
            for offset in range(3, 10)
        )
    return parameters


def _wireless_di_connection_parameters() -> list[ModbusParameter]:
    return [
        _uint(
            1000 + connection,
            f"REG_WL_DI_CONNECTION_{connection}",
            f"Wireless DI connection {connection}. 0: not connected, 1: DI1, 2: DI2, 3: DI3, 4: DI4, 5: DI5, 7: DI7.",
            min_value=0,
            max_value=7,
        )
        for connection in range(1, 21)
    ]


def _compact_read_blocks(parameters: list[ModbusParameter], *, max_gap: int = 3, max_count: int = 100) -> tuple[tuple[int, int], ...]:
    addresses = sorted({param.register for param in parameters})
    if not addresses:
        return ()

    blocks: list[tuple[int, int]] = []
    start = previous = addresses[0]

    for address in addresses[1:]:
        current_count = previous - start + 1
        gap = address - previous
        if gap <= max_gap and current_count + gap <= max_count:
            previous = address
            continue

        blocks.append((start, previous - start + 1))
        start = previous = address

    blocks.append((start, previous - start + 1))
    return tuple(blocks)


D24810_PARAMETERS = [
    _uint(101, "REG_FAN_SPEED_LEVEL", "Fan speed level. 0: off, 1: low, 2: normal, 3: high, 4: auto.", min_value=0, max_value=4),
    _uint(102, "REG_FAN_SF_FLOW_LOW", "Supply fan speed for low speed."),
    _uint(103, "REG_FAN_EF_FLOW_LOW", "Extract fan speed for low speed."),
    _uint(104, "REG_FAN_SF_FLOW_NOM", "Supply fan speed for nominal speed."),
    _uint(105, "REG_FAN_EF_FLOW_NOM", "Extract fan speed for nominal speed."),
    _uint(106, "REG_FAN_SF_FLOW_HIGH", "Supply fan speed for high speed."),
    _uint(107, "REG_FAN_EF_FLOW_HIGH", "Extract fan speed for high speed."),
    _uint(108, "REG_FAN_FLOW_UNITS", "Fan airflow units. 0: l/s, 1: m3/h.", min_value=0, max_value=1),
    _uint(109, "REG_FAN_SF_PWM", "Supply fan PWM output, 0..100 percent.", min_value=0, max_value=100),
    _uint(110, "REG_FAN_EF_PWM", "Extract fan PWM output, 0..100 percent.", min_value=0, max_value=100),
    _uint(111, "REG_FAN_SF_RPM", "Supply fan RPM indication."),
    _uint(112, "REG_FAN_EF_RPM", "Extract fan RPM indication."),
    _bool(114, "REG_FAN_ALLOW_MANUAL_STOP", "Manual fan stop allowed. Coil 1809."),
    _uint(115, "REG_FAN_SPEED_LOG_RESET", "Write 90 to clear resettable fan speed log values.", min_value=90, max_value=90),
    _uint(116, "REG_FAN_SPEED_LOG_SF_LVL1", "Supply fan speed log value for speed level 1."),
    _uint(117, "REG_FAN_SPEED_LOG_SF_LVL2", "Supply fan speed log value for speed level 2."),
    _uint(118, "REG_FAN_SPEED_LOG_SF_LVL3", "Supply fan speed log value for speed level 3."),
    _uint(119, "REG_FAN_SPEED_LOG_SF_LVL4", "Supply fan speed log value for speed level 4."),
    _uint(120, "REG_FAN_SPEED_LOG_SF_LVL5", "Supply fan speed log value for speed level 5."),
    _uint(121, "REG_FAN_SPEED_LOG_EF_LVL1", "Extract fan speed log value for speed level 1."),
    _uint(122, "REG_FAN_SPEED_LOG_EF_LVL2", "Extract fan speed log value for speed level 2."),
    _uint(123, "REG_FAN_SPEED_LOG_EF_LVL3", "Extract fan speed log value for speed level 3."),
    _uint(124, "REG_FAN_SPEED_LOG_EF_LVL4", "Extract fan speed log value for speed level 4."),
    _uint(125, "REG_FAN_SPEED_LOG_EF_LVL5", "Extract fan speed log value for speed level 5."),
    _uint(126, "REG_FAN_SPEED_LOG_SF_NR_LVL1", "Non-resettable supply fan speed log value for speed level 1."),
    _uint(127, "REG_FAN_SPEED_LOG_SF_NR_LVL2", "Non-resettable supply fan speed log value for speed level 2."),
    _uint(128, "REG_FAN_SPEED_LOG_SF_NR_LVL3", "Non-resettable supply fan speed log value for speed level 3."),
    _uint(129, "REG_FAN_SPEED_LOG_SF_NR_LVL4", "Non-resettable supply fan speed log value for speed level 4."),
    _uint(130, "REG_FAN_SPEED_LOG_SF_NR_LVL5", "Non-resettable supply fan speed log value for speed level 5."),
    _uint(131, "REG_FAN_SPEED_LOG_EF_NR_LVL1", "Non-resettable extract fan speed log value for speed level 1."),
    _uint(132, "REG_FAN_SPEED_LOG_EF_NR_LVL2", "Non-resettable extract fan speed log value for speed level 2."),
    _uint(133, "REG_FAN_SPEED_LOG_EF_NR_LVL3", "Non-resettable extract fan speed log value for speed level 3."),
    _uint(134, "REG_FAN_SPEED_LOG_EF_NR_LVL4", "Non-resettable extract fan speed log value for speed level 4."),
    _uint(135, "REG_FAN_SPEED_LOG_EF_NR_LVL5", "Non-resettable extract fan speed log value for speed level 5."),
    _uint(136, "REG_FAN_SYSTEM_CURVE_SF", "Supply fan system curve. Range 1..20.", min_value=1, max_value=20),
    _uint(137, "REG_FAN_SYSTEM_CURVE_EF", "Extract fan system curve. Range 1..10.", min_value=1, max_value=10),
    _uint(138, "REG_FAN_CONTROL_TYPE", "Fan control type. 0: airflow, 1: speed.", min_value=0, max_value=1),
    _bool(139, "REG_FAN_INTERLOCK", "Interlock normally-open relay state."),
    _uint(201, "REG_HC_HEATER_TYPE", "Heater type. 0: none, 1: water heater, 2: electrical heater, 3: other.", min_value=0, max_value=3),
    _uint(202, "REG_HC_COOLER_TYPE", "Cooler type. 0: none, 1: water cooler.", min_value=0, max_value=1),
    _uint(204, "REG_HC_WC_SIGNAL", "Cooler output signal in percent.", min_value=0, max_value=100),
    _uint(205, "REG_HC_WH_SIGNAL", "Analog heater output signal in percent.", min_value=0, max_value=100),
    _int(206, "REG_HC_FPS_LEVEL", "Frost protection level in degrees C.", min_value=70, max_value=120),
    _uint(
        207,
        "REG_HC_TEMP_LVL",
        "Temperature set point level. 0: manual summer mode, 1..5: configured levels, 6..29: extension levels.",
        min_value=0,
        max_value=29,
    ),
    _int(208, "REG_HC_TEMP_SP", "Temperature set point."),
    _int(209, "REG_HC_TEMP_LVL1", "Temperature level 1, scaled by 10.", scale_factor=10),
    _int(210, "REG_HC_TEMP_LVL2", "Temperature level 2, scaled by 10.", scale_factor=10),
    _int(211, "REG_HC_TEMP_LVL3", "Temperature level 3, scaled by 10.", scale_factor=10),
    _int(212, "REG_HC_TEMP_LVL4", "Temperature level 4, scaled by 10.", scale_factor=10),
    _int(213, "REG_HC_TEMP_LVL5", "Temperature level 5, scaled by 10.", scale_factor=10),
    _int(214, "REG_HC_TEMP_IN1", "Temperature on sensor 1, supply air, scaled by 10.", scale_factor=10),
    _int(215, "REG_HC_TEMP_IN2", "Temperature on sensor 2, extract air, scaled by 10.", scale_factor=10),
    _int(216, "REG_HC_TEMP_IN3", "Temperature on sensor 3, exhaust air/preheater, scaled by 10.", scale_factor=10),
    _int(217, "REG_HC_TEMP_IN4", "Temperature on sensor 4, overheating/frost protection, scaled by 10.", scale_factor=10),
    _int(218, "REG_HC_TEMP_IN5", "Temperature on sensor 5, outdoor air, scaled by 10.", scale_factor=10),
    _uint(219, "REG_HC_TEMP_STATE", "Temperature sensor state bitfield. Coils 3489..3493."),
    _uint(220, "REG_HC_PREHEATER_TYPE", "Preheater type. 0: no preheater, 1: electrical preheater.", min_value=0, max_value=1),
    _int(221, "REG_HC_HEATER_TEMP_SP_HOME_LEAVE", "Home/Leave support control heater set point."),
    _int(222, "REG_HC_TEMP_SP_DEG", "Setpoint for temperature regulation, scaled by 10.", scale_factor=10),
    _uint(223, "REG_HC_INTERVAL_COOLING_LOW", "Combined controller output where cooling is at maximum."),
    _uint(224, "REG_HC_INTERVAL_COOLING_HIGH", "Combined controller output where cooling is at minimum."),
    _uint(225, "REG_HC_INTERVAL_EXCHANGING_LOW", "Lower heat exchanging range limit for combined temperature regulator."),
    _uint(226, "REG_HC_INTERVAL_EXCHANGING_HIGH", "Upper heat exchanging range limit for combined temperature regulator."),
    _uint(227, "REG_HC_INTERVAL_HEATING_LOW", "Lower heating range limit for combined temperature regulator."),
    _uint(228, "REG_HC_INTERVAL_HEATING_HIGH", "Upper heating range limit for combined temperature regulator."),
    _uint(229, "REG_HC_P_BAND", "Combined temperature regulator P-band, scaled by 10.", scale_factor=10, min_value=10, max_value=600),
    _uint(230, "REG_HC_I_TIME", "Combined temperature regulator I-time. 0: no integration.", min_value=0, max_value=240),
    _int(231, "REG_PREHEATER_SETPOINT", "Preheater set point. Range -300..0.", min_value=-300, max_value=0),
    _uint(232, "REG_PREHEATER_P_BAND", "Preheater P-band, scaled by 10.", scale_factor=10, min_value=10, max_value=600),
    _uint(233, "REG_PREHEATER_I_TIME", "Preheater I-time. 0: no integration.", min_value=0, max_value=240),
    _uint(234, "REG_HC_OUT", "Split-level temperature controller output, 0..100 percent.", min_value=0, max_value=100),
    _uint(235, "REG_PREHEATER_OUT", "Electrical preheater PI controller output, 0..100 percent.", min_value=0, max_value=100),
    _uint(236, "REG_HC_TEMP_SP_DEG_STEP", "Temperature setting step, scaled by 10.", scale_factor=10),
    _uint(301, "REG_DAMPER_PWM", "Damper output value, 0..100 corresponding to 0..10 V.", min_value=0, max_value=100),
    _uint(351, "REG_ROTOR_STATE", "Rotor control state machine state."),
    _bool(352, "REG_ROTOR_RELAY_ACTIVE", "Rotor relay active. Coil 5617."),
    _uint(353, "REG_SYSTEM_ROTOR_TYPE", "Rotor control type. 0: on/off control, 1: variable control.", min_value=0, max_value=1),
    _bool(354, "REG_SYSTEM_PASSIVE_HOUSE", "Passive house mode active."),
    _uint(381, "REG_RH_SENSOR_VALUE", "RH sensor value in percent.", min_value=0, max_value=100),
    _bool(383, "REG_RH_SENSOR_DATA_VALID", "Valid data is available from the RH sensor."),
    *_week_program_parameters(),
    _uint(
        501,
        "REG_SYSTEM_TYPE",
        "System type. 0: VR400, 1: VR700, 2: VR700DK, 3: VR400DE, 4: VTC300, 5: VTC700, 12..21 listed residential units.",
        min_value=0,
        max_value=21,
    ),
    _uint(502, "REG_SYSTEM_PROG_V_HIGH", "PCU-ECx main program version, high number."),
    _uint(503, "REG_SYSTEM_PROG_V_MID", "PCU-ECx main program version, middle number."),
    _uint(504, "REG_SYSTEM_PROG_V_LOW", "PCU-ECx main program version, low number."),
    _uint(505, "REG_SYSTEM_BOOT_PROG_V_HIGH", "PCU-ECx boot program version, high number."),
    _uint(506, "REG_SYSTEM_BOOT_PROG_V_MID", "PCU-ECx boot program version, middle number."),
    _uint(507, "REG_SYSTEM_BOOT_PROG_V_LOW", "PCU-ECx boot program version, low number."),
    _uint(508, "REG_SYSTEM_PROG_STATE", "Program state. 1: main program, 2: boot loader, 3: boot loading accepted."),
    _uint(509, "REG_SYSTEM_START_BOOTLOADER", "Write non-zero value to activate boot loader.", min_value=1),
    _uint(510, "REG_SYSTEM_BOOTLOADER_FLAGS", "Boot loader flags."),
    _uint(518, "REG_SYSTEM_BRIDGE_CD3_FIRMWARE_H", "Program version for CD2/3 available in Z-wave bridge, high number."),
    _uint(519, "REG_SYSTEM_BRIDGE_CD3_FIRMWARE_M", "Program version for CD2/3 available in Z-wave bridge, middle number."),
    _uint(520, "REG_SYSTEM_BRIDGE_CD3_FIRMWARE_L", "Program version for CD2/3 available in Z-wave bridge, low number."),
    _uint(521, "REG_SYSTEM_BRIDGE_PCU_EC3_FIRMWARE_H", "Program version for PCU-ECx available in Z-wave bridge, high number."),
    _uint(522, "REG_SYSTEM_BRIDGE_PCU_EC3_FIRMWARE_M", "Program version for PCU-ECx available in Z-wave bridge, middle number."),
    _uint(523, "REG_SYSTEM_BRIDGE_PCU_EC3_FIRMWARE_L", "Program version for PCU-ECx available in Z-wave bridge, low number."),
    _uint(524, "REG_SYSTEM_CDX_PROG_V_H", "CDx program version, high number."),
    _uint(525, "REG_SYSTEM_CDX_PROG_V_M", "CDx program version, middle number."),
    _uint(526, "REG_SYSTEM_CDX_PROG_V_L", "CDx program version, low number."),
    _uint(549, "REG_STORE_NVM", "Write 165 to store selected NVM parameters.", min_value=165, max_value=165),
    _uint(551, "REG_CLK_S", "Clock seconds.", min_value=0, max_value=59),
    _uint(552, "REG_CLK_M", "Clock minutes.", min_value=0, max_value=59),
    _uint(553, "REG_CLK_H", "Clock hours.", min_value=0, max_value=23),
    _uint(554, "REG_CLK_D", "Clock day of month.", min_value=1, max_value=31),
    _uint(555, "REG_CLK_MNTH", "Clock month.", min_value=1, max_value=12),
    _uint(556, "REG_CLK_Y", "Clock year offset from 2000.", min_value=0),
    _uint(557, "REG_CLK_WD", "Clock day of week. 0: Monday through 6: Sunday.", min_value=0, max_value=6),
    _uint(601, "REG_FILTER_PER", "Filter replacement time in months.", min_value=1, max_value=24),
    _uint(602, "REG_FILTER_DAYS", "Elapsed days since last filter replacement.", min_value=0, max_value=3650),
    _uint(651, "REG_DEFR_STATE_VTC", "VTC defrosting state machine state."),
    _uint(652, "REG_DEFR_CONFIGURATION", "Defrosting configuration. 0: A, 1: B, 2: C, 3: D.", min_value=0, max_value=3),
    _bool(653, "REG_DEFR_UNBAL_ALLOWED", "Defrosting unbalance allowed. Coil 10433."),
    _uint(654, "REG_DEFR_MODE_VTC", "VTC defrosting mode.", min_value=1, max_value=5),
    _bool(655, "REG_RH_SENSOR_PRESENT", "RH sensor is connected and shall be used."),
    _uint(671, "REG_DEFR_STATE_VR", "VR/VTR defrosting state machine state."),
    _uint(672, "REG_DEFR_MODE_VR", "VR/VTR defrosting mode.", min_value=0, max_value=5),
    _uint(701, "REG_DI_ALL", "Digital input bitfield. Coils 11201..11207."),
    _uint(702, "REG_DI_EXT_RUNNING_M", "Extended running time in minutes."),
    _uint(703, "REG_DI_EXT_RUNNING_SPEED_LVL", "Fan speed level during extended running.", min_value=0, max_value=3),
    _uint(704, "REG_DI1_SF_LVL", "Supply fan speed level at activated digital input 1.", min_value=0, max_value=4),
    _uint(705, "REG_DI1_EF_LVL", "Extract fan speed level at activated digital input 1.", min_value=0, max_value=4),
    _uint(706, "REG_DI2_SF_LVL", "Supply fan speed level at activated digital input 2.", min_value=0, max_value=4),
    _uint(707, "REG_DI2_EF_LVL", "Extract fan speed level at activated digital input 2.", min_value=0, max_value=4),
    _uint(708, "REG_DI3_SF_LVL", "Supply fan speed level at activated digital input 3.", min_value=0, max_value=4),
    _uint(709, "REG_DI3_EF_LVL", "Extract fan speed level at activated digital input 3.", min_value=0, max_value=4),
    _uint(710, "REG_DI_FUNCTIONS", "Functions active due to activated digital inputs."),
    _uint(711, "REG_DI_MODBUS", "Latest value written to REG_DI_ALL."),
    _uint(712, "REG_DI_WIRELESS", "OR-ed value of all wireless inputs."),
    _uint(713, "REG_DI_REMAINING_TIME_1", "Remaining delay time for DI1 in seconds."),
    _uint(714, "REG_DI_REMAINING_TIME_2", "Remaining delay time for DI2 in seconds."),
    _uint(715, "REG_DI_REMAINING_TIME_3", "Remaining delay time for DI3 in seconds."),
    _uint(716, "REG_DI_REMAINING_TIME_EXT_RUNNING", "Remaining delay time for extended running in seconds."),
    _uint(751, "REG_PCU_PB_RELAYS", "PCU-PB relay bitfield. Coils 12001..12003."),
    _uint(801, "REG_ALARMS_ALL", "All alarm flags. Coils 12801..12812."),
    _bool(802, "REG_ALARMS_RELAY_ACTIVE", "Alarm relay active. Coil 12817."),
    _uint(803, "REG_ALARMS_ALL_DETAILED", "All alarm flags including temperature sensor status flags."),
    _uint(851, "REG_DEMC_CO2_SP", "Demand control CO2 set point. 0: off, range 0..2000 ppm.", min_value=0, max_value=2000),
    _uint(852, "REG_DEMC_CO2_P_BAND", "Demand control CO2 P-band. Range 1..2000.", min_value=1, max_value=2000),
    _uint(853, "REG_DEMC_CO2_I_TIME", "Demand control CO2 I-time. 0: no integration.", min_value=0, max_value=120),
    _uint(854, "REG_DEMC_RH_SP_SUMMER", "Demand control RH summer set point. 0: off, range 0..100%.", min_value=0, max_value=100),
    _uint(855, "REG_DEMC_RH_P_BAND", "Demand control RH P-band. Range 1..100.", min_value=1, max_value=100),
    _uint(856, "REG_DEMC_RH_I_TIME", "Demand control RH I-time. 0: no integration.", min_value=0, max_value=120),
    _uint(
        857,
        "REG_DEMC_STATE",
        "Demand control state. 0: startup, 1: waiting network, 2: waiting data, 3: auto, 4: normal.",
        min_value=0,
        max_value=4,
    ),
    _uint(858, "REG_DEMC_MODBUS_CO2_VALUE", "Demand control Modbus CO2 value in ppm. Range 0..2000.", min_value=0, max_value=2000),
    _uint(859, "REG_DEMC_MODBUS_RH_VALUE", "Demand control Modbus RH value in percent. Range 0..100.", min_value=0, max_value=100),
    _uint(860, "REG_DEMC_MODBUS_CO2_OUT", "Demand control CO2 PI controller output."),
    _uint(861, "REG_DEMC_MODBUS_RH_OUT", "Demand control RH PI controller output."),
    _uint(862, "REG_DEMC_ALLOWED", "Demand control allowed bitfield."),
    _uint(863, "REG_DEMC_RH_SP_WINTER", "Demand control RH winter set point. Range 0..100%.", min_value=0, max_value=100),
    _uint(864, "REG_DEMC_SUMMER_WINTER_MODE", "Demand control summer/winter mode. 0: summer, 1: winter.", min_value=0, max_value=1),
    _uint(865, "REG_DEMC_SUMMER_WINTER_CNTR_H", "Highest 16 bits of remaining time until summer mode."),
    _uint(866, "REG_DEMC_SUMMER_WINTER_CNTR_L", "Lowest 16 bits of remaining time until summer mode."),
    *_wireless_node_parameters(),
    *_wireless_di_connection_parameters(),
]

D24810_SENSOR_ENTITIES = (
    SensorProfileEntity(
        key="d24810_system_type",
        register_key="REG_SYSTEM_TYPE",
        translation_key="d24810_system_type",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorProfileEntity(
        key="meter_sf_rpm",
        register_key="REG_FAN_SF_RPM",
        translation_key="meter_saf_rpm",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
    ),
    SensorProfileEntity(
        key="meter_ef_rpm",
        register_key="REG_FAN_EF_RPM",
        translation_key="meter_eaf_rpm",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
    ),
    SensorProfileEntity(
        key="meter_sf_reg_speed",
        register_key="REG_FAN_SF_PWM",
        translation_key="meter_saf_reg_speed",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorProfileEntity(
        key="meter_ef_reg_speed",
        register_key="REG_FAN_EF_PWM",
        translation_key="meter_eaf_reg_speed",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorProfileEntity(
        key="filter_days",
        register_key="REG_FILTER_DAYS",
        translation_key="filter_days",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.DAYS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

D24810_BINARY_SENSOR_ENTITIES = (
    BinarySensorProfileEntity(
        key="manual_fan_stop_allowed",
        register_key="REG_FAN_ALLOW_MANUAL_STOP",
        translation_key="manual_fan_stop_allowed",
        device_class=BinarySensorDeviceClass.RUNNING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

D24810_SELECT_ENTITIES = (
    SelectProfileEntity(
        key="fan_speed_level",
        register_key="REG_FAN_SPEED_LEVEL",
        translation_key="fan_speed_level",
        icon="mdi:fan",
        options_map={0: "off", 1: "low", 2: "normal", 3: "high", 4: "auto"},
    ),
)

D24810_SWITCH_ENTITIES: tuple[SwitchProfileEntity, ...] = ()

D24810_NUMBER_ENTITIES = (
    NumberProfileEntity(
        key="filter_period",
        register_key="REG_FILTER_PER",
        translation_key="filter_period",
        native_unit_of_measurement=UnitOfTime.MONTHS,
        entity_category=EntityCategory.CONFIG,
    ),
)

d24810_parameter_map = {param.short: param for param in D24810_PARAMETERS}

D24810_PROFILE = DeviceProfile(
    profile_id="legacy_d24810",
    name="Legacy Residential / D24810",
    supported_api_types=(API_TYPE_MODBUS_TCP, API_TYPE_MODBUS_SERIAL),
    supported_platforms=(
        Platform.CLIMATE,
        Platform.SENSOR,
        Platform.BINARY_SENSOR,
        Platform.SWITCH,
        Platform.NUMBER,
        Platform.SELECT,
    ),
    registry=d24810_parameter_map,
    read_blocks=_compact_read_blocks(D24810_PARAMETERS),
    test_register=501,
    model_options=(
        "VR400",
        "VR700",
        "VR700DK",
        "VR400DE",
        "VTC300",
        "VTC700",
        "VTR150K",
        "VTR200B",
        "VSR300",
        "VSR500",
        "VSR150",
        "VTR300",
        "VTR500",
        "VSR300DE",
        "VTC200",
        "VTC100",
    ),
    entities=ProfileEntityDescriptions(
        sensors=D24810_SENSOR_ENTITIES,
        binary_sensors=D24810_BINARY_SENSOR_ENTITIES,
        switches=D24810_SWITCH_ENTITIES,
        selects=D24810_SELECT_ENTITIES,
        numbers=D24810_NUMBER_ENTITIES,
    ),
    climate_registers={
        "fan_mode": "REG_FAN_SPEED_LEVEL",
        "current_temperature": "REG_HC_TEMP_IN1",
        "target_temperature": "REG_HC_TEMP_SP",
    },
)
