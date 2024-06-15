# SPDX-FileCopyrightText: 2022 lbuque
#
# SPDX-License-Identifier: MIT

import time
import struct


_DEV_MODE_REG = const(0x00)
_GEST_ID_REG = const(0x01)
_TD_STATUS_REG = const(0x02)
_P1_XH_REG = const(0x03)
_P1_XL_REG = const(0x04)
_P1_YH_REG = const(0x05)
_P1_YL_REG = const(0x06)
_P1_WEIGHT_REG = const(0x07)
_P1_MISC_REG = const(0x08)
_P2_XH_REG = const(0x09)
_P2_XL_REG = const(0x0A)
_P2_YH_REG = const(0x0B)
_P2_YL_REG = const(0x0C)
_P2_WEIGHT_REG = const(0x0D)
_P2_MISC_REG = const(0x0E)
_TH_GROUP_REG = const(0x80)
_TH_DIFF_REG = const(0x85)
_CTRL_REG = const(0x86)
_TIMEENTERMONITOR_REG = const(0x87)
_PERIODACTIVE_REG = const(0x88)
_PERIODMONITOR_REG = const(0x89)
_RADIAN_VALUE_REG = const(0x91)
_OFFSET_LEFT_RIGHT_REG = const(0x92)
_OFFSET_UP_DOWN_REG = const(0x93)
_DISTANCE_LEFT_RIGHT_REG = const(0x94)
_DISTANCE_UP_DOWN_REG = const(0x95)
_DISTANCE_ZOOM_REG = const(0x96)
_LIB_VER_H_REG = const(0xA1)
_LIB_VER_L_REG = const(0xA2)
_CIPHER_REG = const(0xA3)
_G_MODE_REG = const(0xA4)
_PWR_MODE_REG = const(0xA5)
_FIRMID_REG = const(0xA6)
_FOCALTECH_ID_REG = const(0xA8)
_RELEASE_CODE_ID_REG = const(0xAF)
_STATE_REG = const(0xBC)


class FT6x36:
    PORTRAIT = const(0)
    LANDSCAPE = const(1)
    PORTRAIT_INVERTED = const(2)
    LANDSCAPE_INVERTED = const(3)

    GESTURE_NO_GESTRUE = const(0)
    GESTURE_MOVE_UP = const(1)
    GESTURE_MOVE_LEFT = const(2)
    GESTURE_MOVE_DOWN = const(3)
    GESTURE_MOVE_RIGHT = const(4)
    GESTURE_ZOOM_IN = const(5)
    GESTURE_ZOOM_OUT = const(6)

    POLLING_MODE = const(0x00)
    TRIGGER_MODE = const(0x01)

    """
    FocalTech Self-Capacitive Touch Panel Controller module

    :param I2C i2c: The board I2C object
    :param int address: The I2C address
    :param Pin rst: The reset Pin object
    :param int rotation: The rotation of the touch screen
    :param int width: The width of the touch screen
    :param int height: The height of the touch screen
    """

    def __init__(
        self,
        i2c: I2C,
        address: int = 0x38,
        rst: Pin = None,
        rotation=PORTRAIT,
        width=320,
        height=240,
    ) -> None:
        self._i2c = i2c
        self._address = address
        self._rst = rst
        self._rotation = rotation
        self._width = width
        self._height = height
        self._buffer12 = bytearray(12)
        self._buffer2 = bytearray(2)
        self._buffer1 = bytearray(1)

    def get_gesture(self) -> int:
        """
        Get Gesture events. Should be a value of:

        * ``GESTURE_NO_GESTRUE``: No Gesture
        * ``GESTURE_MOVE_UP``: Move Up
        * ``GESTURE_MOVE_RIGHT``: Move Right
        * ``GESTURE_MOVE_DOWN``: Move Down
        * ``GESTURE_MOVE_LEFT``: Move Left
        * ``GESTURE_ZOOM_IN``: Zoom In
        * ``GESTURE_ZOOM_OUT``: Zoom Out
        """
        gesture = self._i2c.readfrom_mem(self._address, _GEST_ID_REG, 1)[0]
        if 0x10 == gesture:
            return self.GESTURE_MOVE_UP
        elif 0x14 == gesture:
            return self.GESTURE_MOVE_RIGHT
        elif 0x18 == gesture:
            return self.GESTURE_MOVE_DOWN
        elif 0x1C == gesture:
            return self.GESTURE_MOVE_LEFT
        elif 0x48 == gesture:
            return self.GESTURE_ZOOM_IN
        elif 0x49 == gesture:
            return self.GESTURE_ZOOM_OUT
        else:
            return self.GESTURE_NO_GESTRUE

    def set_rotation(self, rotation: int) -> None:
        """
        Set the rotation of the touch screen. Should be a value of:

        * ``PORTRAIT``: Portrait
        * ``LANDSCAPE``: Landscape
        * ``PORTRAIT_INVERTED``: Portrait Inverted
        * ``LANDSCAPE_INVERTED``: Landscape Inverted
        """
        self._rotation = rotation

    def _rotation_swap(self, x: int, y: int) -> tuple:
        if self._rotation == self.PORTRAIT:
            return (x, y)
        elif self._rotation == self.LANDSCAPE:
            return (y, self._width - x)
        elif self._rotation == self.PORTRAIT_INVERTED:
            return (self._width - x, self._height - y)
        elif self._rotation == self.LANDSCAPE_INVERTED:
            return (self._height - y, x)

    def get_positions(self) -> list:
        positions = []
        num_points = self._i2c.readfrom_mem(self._address, _TD_STATUS_REG, 1)[0] & 0x0F
        self._i2c.readfrom_mem_into(self._address, _P1_XH_REG, self._buffer12)
        (
            x1,
            y1,
            weight1,
            area1,
        ) = struct.unpack_from(">HHBB", self._buffer12, 0)
        (
            x2,
            y2,
            weight2,
            area2,
        ) = struct.unpack_from(">HHBB", self._buffer12, 6)
        (x1, y1) = self._rotation_swap(x1 & 0x0FFF, y1 & 0x0FFF)
        (x2, y2) = self._rotation_swap(x2 & 0x0FFF, y2 & 0x0FFF)
        if num_points > 0:
            positions.append((x1, y1, weight1, area1 & 0x0F))
        if num_points > 1:
            positions.append((x2, y2, weight2, area2 & 0x0F))
        return positions

    @property
    def theshold(self) -> int:
        """
        Threshold for touch detection.
        """
        return self._i2c.readfrom_mem(self._address, _TH_GROUP_REG, 1)[0]

    @theshold.setter
    def theshold(self, val: int) -> None:
        self._buffer1[0] = val
        self._i2c.writeto_mem(self._address, _TH_GROUP_REG, self._buffer1)

    @property
    def monitor_time(self) -> int:
        """
        The time period of switching from Active mode to Monitor mode when there is no touching.
        """
        return self._i2c.readfrom_mem(self._address, _TIMEENTERMONITOR_REG, 1)[0]

    @monitor_time.setter
    def monitor_time(self, val: int) -> None:
        self._buffer1[0] = val
        self._i2c.writeto_mem(self._address, _TIMEENTERMONITOR_REG, self._buffer1)

    @property
    def active_period(self) -> int:
        """
        Report rate in Active mode.
        """
        return self._i2c.readfrom_mem(self._address, _PERIODACTIVE_REG, 1)[0]

    @active_period.setter
    def active_period(self, val: int) -> None:
        self._buffer1[0] = val
        self._i2c.writeto_mem(self._address, _PERIODACTIVE_REG, self._buffer1)

    @property
    def monitor_period(self) -> int:
        """
        Report rate in Monitor mode.
        """
        return self._i2c.readfrom_mem(self._address, _PERIODMONITOR_REG, 1)[0]

    @monitor_period.setter
    def monitor_period(self, val: int) -> None:
        self._buffer1[0] = val
        self._i2c.writeto_mem(self._address, _PERIODMONITOR_REG, self._buffer1)

    @property
    def library_version(self) -> int:
        """
        Library Version info.
        """
        self._i2c.readfrom_mem_into(self._address, _LIB_VER_H_REG, self._buffer2)
        return struct.unpack_from(">H", self._buffer2, 0)[0]

    @property
    def firmware_version(self) -> int:
        """
        Firmware Version.
        """
        return self._i2c.readfrom_mem(self._address, _FIRMID_REG, 1)[0]

    @property
    def interrupt_mode(self) -> int:
        """
        Interrupt mode for valid data. Should be a value of:

        * ``POLLING_MODE``: Interrupt Polling mode
        * ``TRIGGER_MODE``:  Interrupt Trigger mode
        """
        return self._i2c.readfrom_mem(self._address, _G_MODE_REG, 1)[0]

    @interrupt_mode.setter
    def interrupt_mode(self, val: int) -> None:
        self._buffer1[0] = val
        self._i2c.writeto_mem(self._address, _G_MODE_REG, self._buffer1)

    @property
    def power_mode(self) -> int:
        """
        Current power mode which system is in.
        """
        return self._i2c.readfrom_mem(self._address, _PWR_MODE_REG, 1)[0]

    @power_mode.setter
    def power_mode(self, val: int) -> None:
        self._buffer1[0] = val
        self._i2c.writeto_mem(self._address, _PWR_MODE_REG, self._buffer1)

    @property
    def vendor_id(self) -> int:
        """
        Chip Selecting.
        """
        return self._i2c.readfrom_mem(self._address, _CIPHER_REG, 1)[0]

    @property
    def panel_id(self) -> int:
        """
        FocalTech’s Panel ID.
        """
        return self._i2c.readfrom_mem(self._address, _FOCALTECH_ID_REG, 1)[0]

    def reset(self) -> None:
        """
        Hardware reset touch screen.
        """
        if self._rst is None:
            return
        self._rst.off()
        time.sleep_ms(1)
        self._rst.on()
