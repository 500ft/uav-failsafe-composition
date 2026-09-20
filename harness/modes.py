"""PX4 custom-mode decoding, transcribed from src/modules/commander/px4_custom_mode.h at v1.17.0 [B1 commit]."""
MAIN = {1: "MANUAL", 2: "ALTCTL", 3: "POSCTL", 4: "AUTO", 5: "ACRO", 6: "OFFBOARD", 7: "STABILIZED", 8: "RATTITUDE_LEGACY", 9: "SIMPLE", 10: "TERMINATION", 11: "ALTITUDE_CRUISE"}
AUTO_SUB = {1: "READY", 2: "TAKEOFF", 3: "LOITER", 4: "MISSION", 5: "RTL", 6: "LAND", 7: "RESERVED", 8: "FOLLOW_TARGET", 9: "PRECLAND", 10: "VTOL_TAKEOFF"}
# VehicleStatus.msg nav_state values (used when reading the uLog)
NAV_STATE = {0: "MANUAL", 1: "ALTCTL", 2: "POSCTL", 3: "AUTO_MISSION", 4: "AUTO_LOITER", 5: "AUTO_RTL", 6: "POSITION_SLOW", 8: "ALTITUDE_CRUISE", 10: "ACRO", 12: "DESCEND", 13: "TERMINATION", 14: "OFFBOARD", 15: "STAB", 17: "AUTO_TAKEOFF", 18: "AUTO_LAND", 19: "AUTO_FOLLOW_TARGET", 20: "AUTO_PRECLAND", 21: "ORBIT", 22: "AUTO_VTOL_TAKEOFF"}


def decode_custom_mode(custom_mode: int) -> str:
    main = (custom_mode >> 16) & 0xFF
    sub = (custom_mode >> 24) & 0xFF
    name = MAIN.get(main, f"MAIN{main}")
    if name == "AUTO":
        return "AUTO_" + AUTO_SUB.get(sub, f"SUB{sub}")
    return name


def encode_custom_mode(main: int, sub: int = 0) -> int:
    return (main << 16) | (sub << 24)


# The failsafe framework's action → the nav state it produces (framework.cpp modeFromAction L670-697)
ACTION_TO_NAV = {"Hold": "AUTO_LOITER", "RTL": "AUTO_RTL", "Land": "AUTO_LAND", "Descend": "DESCEND", "FallbackPosCtrl": "POSCTL", "FallbackAltCtrl": "ALTCTL", "FallbackStab": "STAB", "Terminate": "TERMINATION"}
