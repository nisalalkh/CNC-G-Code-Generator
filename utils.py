# utils.py
from config import *

def add_tool_change(gcode, tool_number):
    gcode.append(f"{TOOL_CHANGE_COMMAND} T{tool_number} ; Change to tool {tool_number}")

def add_safe_movement(gcode):
    gcode.append(f"G0 Z{SAFE_HEIGHT} ; Move to safe height")
