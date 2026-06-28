import numpy as np

import control as c


def _hand(center, lm=None):
    if lm is None:
        lm = np.zeros((21, 3), np.float32)
    return {"center": center, "lm": lm}


def test_wasd_up_is_w():
    assert c.wasd_from_center(0.5, 0.2) == {"w"}


def test_wasd_down_is_s():
    assert c.wasd_from_center(0.5, 0.8) == {"s"}


def test_wasd_left_is_a():
    assert c.wasd_from_center(0.2, 0.5) == {"a"}


def test_wasd_right_is_d():
    assert c.wasd_from_center(0.8, 0.5) == {"d"}


def test_wasd_center_is_deadzone():
    assert c.wasd_from_center(0.5, 0.5) == set()


def test_wasd_diagonal_up_right():
    assert c.wasd_from_center(0.85, 0.15) == {"w", "d"}


def test_cursor_center_maps_to_screen_center():
    x, y = c.cursor_target(0.5, 0.5, 1920, 1080)
    assert abs(x - 960) <= 1 and abs(y - 540) <= 1


def test_cursor_clamps_to_screen():
    assert c.cursor_target(-1.0, -1.0, 1920, 1080) == (0, 0)
    assert c.cursor_target(2.0, 2.0, 1920, 1080) == (1920, 1080)


def test_pinch_scale_invariant():
    lm = np.zeros((21, 3), np.float32)
    lm[c.INDEX_MCP, :2] = [0.4, 0.5]
    lm[c.PINKY_MCP, :2] = [0.6, 0.5]
    lm[c.THUMB_TIP, :2] = [0.50, 0.5]
    lm[c.INDEX_TIP, :2] = [0.51, 0.5]
    assert c.pinch(lm, c.THUMB_TIP, c.INDEX_TIP)
    lm[c.INDEX_TIP, :2] = [0.72, 0.5]
    assert not c.pinch(lm, c.THUMB_TIP, c.INDEX_TIP)


def test_assign_roles_orders_by_side():
    left, right = _hand((0.3, 0.5)), _hand((0.7, 0.5))
    l, r = c.assign_roles([right, left])
    assert l is left and r is right


def test_assign_roles_handles_empty():
    assert c.assign_roles([]) == (None, None)


def test_controller_no_inject_holds_wasd():
    ctrl = c.Controller(inject=False, screen=(1920, 1080))
    assert ctrl.update_wasd(_hand((0.5, 0.2))) == {"w"}
    assert ctrl.held == {"w"}
    ctrl.update_wasd(None)
    assert ctrl.held == set()


def test_controller_no_inject_left_click_event():
    ctrl = c.Controller(inject=False, screen=(1920, 1080))
    lm = np.zeros((21, 3), np.float32)
    lm[c.INDEX_MCP, :2] = [0.4, 0.5]
    lm[c.PINKY_MCP, :2] = [0.6, 0.5]
    lm[c.INDEX_TIP, :2] = [0.50, 0.5]
    lm[c.THUMB_TIP, :2] = [0.505, 0.5]
    cursor, events = ctrl.update_mouse({"center": (0.5, 0.5), "lm": lm})
    assert cursor is not None and "left-down" in events
