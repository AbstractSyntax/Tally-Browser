import webview
import ctypes
import time
import os
from ctypes import windll, byref, c_ulong, c_int

# --- CONFIGURATION ---
INPUT = 'hdmi_5'
USER = 'user'
PASS = '0000'
URL = f"http://{USER}:{PASS}@192.168.8.212/tally/{INPUT}"
# URL = "https://google.com" # Debug URL if you need to test

TITLE = "HDMI 5"
WIDTH = 700
HEIGHT = 300   # The sliver height
OPACITY = 180 # 0-255 (128 = ~50% transparent)

# --- Windows API Constants ---
GWL_STYLE = -16
GWL_EXSTYLE = -20

WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_POPUP = 0x80000000  # <--- Essential for <50px height

WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20 # Mouse Click-Through
LWA_ALPHA = 0x2
SWP_FRAMECHANGED = 0x0020

def get_my_hwnd():
    """ 
    Finds the window handle belonging to THIS python process. 
    Matches by PID, so it works even if the website changes the Title.
    """
    my_pid = os.getpid()
    result_hwnd = None

    def callback(hwnd, _):
        nonlocal result_hwnd
        # Get the PID of the window handle
        tid, pid = c_ulong(), c_ulong()
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        
        # If the window belongs to us and is visible, grab it
        if pid.value == my_pid and windll.user32.IsWindowVisible(hwnd):
            result_hwnd = hwnd
            return False # Stop enumerating
        return True # Keep looking

    # Define the C-compatible callback type
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
    windll.user32.EnumWindows(WNDENUMPROC(callback), 0)
    
    return result_hwnd

def setup_window(window):
    # Wait for webview to settle
    time.sleep(1.0)
    
    window.load_css('body { overflow: hidden !important; background: transparent !important; }')

    # 1. FIND WINDOW BY PROCESS ID (Robust Method)
    hwnd = get_my_hwnd()

    if hwnd:
        print(f"Window found! Handle: {hwnd}")
        
        # 2. STRIP STYLES (Allow small size)
        old_style = windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        # Remove borders/caption, Add POPUP (removes min-height limits)
        new_style = (old_style & ~WS_CAPTION & ~WS_THICKFRAME) | WS_POPUP
        windll.user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)

        # 3. ADD TRANSPARENCY
        ex_style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        # Add Layered (for opacity) + Transparent (Click-through)
        # NOTE: Remove ' | WS_EX_TRANSPARENT' if you need to click/drag the window
        windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
        windll.user32.SetLayeredWindowAttributes(hwnd, 0, OPACITY, LWA_ALPHA)

        # 4. FORCE GEOMETRY
        if len(webview.screens) > 0:
            active_screen = webview.screens[0]
            x_pos = int((active_screen.width - WIDTH) / 2)
        else:
            x_pos = 0

        # Force the OS to repaint it at the specific sliver size
        windll.user32.SetWindowPos(hwnd, 0, x_pos, 0, WIDTH, HEIGHT, SWP_FRAMECHANGED)
        print("Styles applied successfully.")
    else:
        print("ERROR: Could not find window handle.")

def run_tally():
    window = webview.create_window(
        title=TITLE,
        url=URL,
        width=WIDTH,
        height=200, # Start larger to ensure it loads, we shrink it later
        on_top=True,
        frameless=True,
        easy_drag=False, # Must be False for click-through to work
        focus=False,
        text_select=False
    )
    
    webview.start(func=setup_window, args=(window,))
    
if __name__ == '__main__':
    run_tally()