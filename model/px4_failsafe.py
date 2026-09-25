"""Executable model of the PX4 v1.17.0 failsafe framework — the discrete part of Study A.

Every table and rule here is transcribed from the pinned source [B1] (commit d6f12ad1c4f70ad3230afd7d86e971421e02fef4,
src/modules/commander/failsafe/{framework.h,framework.cpp,failsafe.h,failsafe.cpp}); line numbers are given per rule so a
reviewer can diff the model against the code. Continuous inputs (battery warning level, position validity, geofence
breach) enter as boolean/enum flags: this model decides *which action* the framework selects and *when*, not the physics.

No dependency beyond the standard library. `python model/px4_failsafe.py` runs the self-check.
"""
from __future__ import annotations
from dataclasses import dataclass, field

# framework.h L52-70: "Actions further down take precedence"
ACTIONS = ("None", "Warn", "FallbackPosCtrl", "FallbackAltCtrl", "FallbackStab", "Hold", "RTL", "Land", "Descend", "Disarm", "Terminate")
PRECEDENCE = {a: i for i, a in enumerate(ACTIONS)}

# failsafe.cpp L43-84 (NAV_DLL_ACT and NAV_RCL_ACT share fromNavDllOrRclActParam); failsafe.h L113-120
LINK_LOSS_ACTION = {0: "None", 1: "Hold", 2: "RTL", 3: "Land", 5: "Terminate", 6: "Disarm"}
# failsafe.cpp L86-127; failsafe.h L104-111
GF_ACTION = {0: "None", 1: "Warn", 2: "Hold", 3: "RTL", 4: "Terminate", 5: "Land"}
# failsafe.cpp L280-327; failsafe.h L78-87 (COM_OBL_RC_ACT)
OFFBOARD_LOSS_ACTION = {0: "FallbackPosCtrl", 1: "FallbackAltCtrl", 2: "FallbackStab", 3: "RTL", 4: "Land", 5: "Hold", 6: "Terminate", 7: "Disarm"}
# failsafe.cpp L372-413; failsafe.h L151-158 (COM_POS_LOW_ACT)
POS_LOW_ACTION = {0: "None", 1: "Warn", 2: "Hold", 3: "RTL", 4: "Terminate", 5: "Land"}
# failsafe.cpp L190-249 (COM_LOW_BAT_ACT by warning level); failsafe.h L70-76
def battery_action(com_low_bat_act: int, warning: str) -> str:
    if warning == "low":
        return "Warn"
    if warning == "critical":
        return {0: "Warn", 1: "RTL", 2: "Land", 3: "RTL"}[com_low_bat_act]
    if warning == "emergency":
        return {0: "Warn", 1: "RTL", 2: "Land", 3: "Land"}[com_low_bat_act]
    return "None"

# framework.cpp L490-493: actions that can be delayed behind Hold
def can_be_delayed(action: str) -> bool:
    return action not in ("None", "Disarm", "Terminate", "Hold")

# failsafe.cpp L562, L542-544: geofence / wind / flight-time cannot be deferred (irrelevant to delay); the delay applies when
# COM_FAIL_ACT_T > 0.1 s and takeover is Auto (framework.cpp L351-362). Geofence Hold and PosLow use AlwaysModeSwitchOnly.

HAZARD_PARAM = {  # hazard class -> (parameter, map)
    "datalink_loss": ("NAV_DLL_ACT", LINK_LOSS_ACTION),
    "rc_loss": ("NAV_RCL_ACT", LINK_LOSS_ACTION),
    "geofence_breach": ("GF_ACTION", GF_ACTION),
    "offboard_loss": ("COM_OBL_RC_ACT", OFFBOARD_LOSS_ACTION),
    "position_low": ("COM_POS_LOW_ACT", POS_LOW_ACTION),
}


def configured_action(hazard: str, params: dict, battery_warning: str = "critical") -> str:
    """Action the framework will register for `hazard` under `params` (failsafe.cpp checkStateAndMode)."""
    if hazard.startswith("battery"):
        return battery_action(int(params.get("COM_LOW_BAT_ACT", 0)), hazard.split("_", 1)[1] if "_" in hazard else battery_warning)
    p, table = HAZARD_PARAM[hazard]
    return table[int(params.get(p, DEFAULTS[p]))]


DEFAULTS = {"NAV_DLL_ACT": 0, "NAV_RCL_ACT": 2, "GF_ACTION": 2, "COM_OBL_RC_ACT": 0, "COM_POS_LOW_ACT": 3, "COM_LOW_BAT_ACT": 0,
            "COM_FAIL_ACT_T": 5.0, "COM_DL_LOSS_T": 10, "COM_RC_LOSS_T": 0.5, "COM_OF_LOSS_T": 1.0}  # [B10]


@dataclass
class Selector:
    """framework.cpp getSelectedAction (L438-645) restricted to: max over active actions, delayed Hold, terminate latch.
    User takeover and mode-requirement fallbacks are modelled as inputs (`takeover`, `mode_can_run`)."""
    params: dict
    active: dict = field(default_factory=dict)  # hazard -> action
    delay_left_s: float = 0.0            # _current_delay: what is left of the delay now running
    start_delay_s: float | None = None   # _current_start_delay: the pot the NEXT delay is filled from
    selected: str = "None"
    delayed: str = "None"
    terminated: bool = False

    def __post_init__(self) -> None:
        # framework.cpp L50 and L146: both the constructor and updateParams seed the pot from COM_FAIL_ACT_T.
        if self.start_delay_s is None:
            self.start_delay_s = float(self.params.get("COM_FAIL_ACT_T", 5.0))

    def _update_start_delay(self, dt_s: float, delay_active: bool) -> None:
        """framework.cpp updateStartDelay L121-141. The pot drains while a delayed action is pending and refills
        at a QUARTER of real time when none is. Its own comment says why: "Ensure that even with a toggling
        state the delayed action is executed at some point. This is done by increasing the delay slower than
        reducing it." So a hazard that clears and re-raises does not get its full delay back, and the second
        episode acts sooner than the first. This is state shared across episodes, and it was the omission the
        earlier model carried as a marker (critique 2026-09-24, F6).
        """
        configured = float(self.params.get("COM_FAIL_ACT_T", 5.0))
        if delay_active:
            self.start_delay_s = max(0.0, self.start_delay_s - dt_s)
        else:
            self.start_delay_s = min(configured, self.start_delay_s + dt_s / 4.0)

    def raise_hazard(self, hazard: str, warning: str = "critical") -> None:
        act = configured_action(hazard, self.params, warning)
        newly = hazard not in self.active
        self.active[hazard] = act
        # framework.cpp L351-356: a new delayable action with no delay already running fills _current_delay from
        # _current_start_delay -- NOT from COM_FAIL_ACT_T. On a first hazard they are equal; after a previous
        # delayed episode the pot is lower, which is the whole point of the recharge rule.
        if newly and float(self.params.get("COM_FAIL_ACT_T", 5.0)) > 0.1 and act != "Warn" and self.delay_left_s == 0.0 and can_be_delayed(act):
            self.delay_left_s = self.start_delay_s

    def clear_hazard(self, hazard: str, mode_changed_or_disarmed: bool = False) -> None:
        # ClearCondition: link-loss/geofence/offboard actions clear OnModeChangeOrDisarm (failsafe.cpp L54, L102, L108...), position-low clears WhenConditionClears (L388-404)
        if hazard == "position_low" or mode_changed_or_disarmed:
            self.active.pop(hazard, None)

    def step(self, dt_s: float, armed: bool = True, takeover: bool = False, hold_can_run: bool = True) -> str:
        if self.terminated:  # framework.cpp L446-450: Terminate never clears
            self.selected = "Terminate"; return self.selected
        if not armed:
            self.selected = "None"; return self.selected
        self.delay_left_s = max(0.0, self.delay_left_s - dt_s)  # framework.cpp updateDelay L149-157
        # framework.cpp L89: updateStartDelay runs every update, keyed on whether a delayed action is pending.
        self._update_start_delay(dt_s, self.delayed != "None")
        # framework.cpp clearDelayIfNeeded L653-668: no Hold-first delay when already in a failsafe (selected > Hold),
        # when Hold cannot run, or when the user has taken over
        if PRECEDENCE[self.selected] > PRECEDENCE["Hold"] or not hold_can_run or takeover:
            self.delay_left_s = 0.0
        best = "None"
        for act in self.active.values():  # L462-481: worst (highest precedence) action wins
            if PRECEDENCE[act] > PRECEDENCE[best]:
                best = act
        self.delayed = "None"
        if self.delay_left_s > 0 and not takeover and can_be_delayed(best) and hold_can_run:  # L489-500, clearDelayIfNeeded L653-668
            self.delayed = best; best = "Hold"
        if takeover and best in ("Hold", "RTL", "Land", "Descend"):  # L502-535, actionAllowsUserTakeover L647-651
            best = "Warn"
        if best == "Terminate":
            self.terminated = True
        self.selected = best
        return best


def demo() -> None:
    """Self-check: the smallest assertions that fail if a table or rule is transcribed wrongly."""
    assert PRECEDENCE["Terminate"] > PRECEDENCE["Disarm"] > PRECEDENCE["Land"] > PRECEDENCE["RTL"] > PRECEDENCE["Hold"] > PRECEDENCE["Warn"]
    assert configured_action("datalink_loss", DEFAULTS) == "None"          # vendor default disables the datalink failsafe [B10]
    assert configured_action("rc_loss", DEFAULTS) == "RTL"
    assert configured_action("geofence_breach", DEFAULTS) == "Hold"
    assert configured_action("offboard_loss", DEFAULTS) == "FallbackPosCtrl"
    assert battery_action(3, "critical") == "RTL" and battery_action(3, "emergency") == "Land" and battery_action(0, "critical") == "Warn"
    s = Selector(dict(DEFAULTS, NAV_DLL_ACT=2))
    s.raise_hazard("datalink_loss"); assert s.step(0.0) == "Hold" and s.delayed == "RTL"     # Hold first for COM_FAIL_ACT_T [B2]
    assert s.step(4.9) == "Hold" and s.step(0.2) == "RTL"                                    # then the delayed action
    s.raise_hazard("geofence_breach"); assert s.step(0.1) == "RTL"                           # Hold (geofence) < RTL: RTL stays selected
    s2 = Selector(dict(DEFAULTS, NAV_DLL_ACT=2, GF_ACTION=5)); s2.raise_hazard("datalink_loss"); s2.step(6.0); s2.raise_hazard("geofence_breach")
    assert s2.step(0.1) == "Land"                                                            # Land > RTL takes precedence
    s3 = Selector(dict(DEFAULTS, NAV_DLL_ACT=2, COM_FAIL_ACT_T=0.0)); s3.raise_hazard("datalink_loss"); assert s3.step(0.0) == "RTL"  # no delay when COM_FAIL_ACT_T <= 0.1
    s4 = Selector(dict(DEFAULTS, NAV_DLL_ACT=2)); s4.raise_hazard("datalink_loss"); assert s4.step(0.0, takeover=True) == "Warn"       # stick takeover interrupts
    s5 = Selector(dict(DEFAULTS, NAV_DLL_ACT=5)); s5.raise_hazard("datalink_loss"); s5.step(0.0); s5.clear_hazard("datalink_loss", True); assert s5.step(1.0) == "Terminate"  # latch
    print("px4_failsafe model self-check OK")


if __name__ == "__main__":
    demo()
