from .contracts import CryoProfile


def thermal_margin_w(cryo: CryoProfile) -> float:
    return cryo.cooling_capacity_w - cryo.heat_load_w


def omega_thermal(cryo: CryoProfile) -> float:
    if cryo.cooling_capacity_w <= 0.0:
        return 0.0
    margin = thermal_margin_w(cryo)
    return max(0.0, min(1.0, (margin / cryo.cooling_capacity_w + 1.0) / 2.0))

