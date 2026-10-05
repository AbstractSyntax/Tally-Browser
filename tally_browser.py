import webview

INPUT = 'hdmi_5'
USER = 'user'
PASS = '0000'
URL = f"http://{USER}:{PASS}@192.168.8.212/tally/{INPUT}"
TITLE = "HDMI 5"
WIDTH = 700
HEIGHT = 1

def setup_window(window):
    window.load_css('body { overflow: hidden !important; }')

    active_screen = webview.screens[0]
    x_pos = int((active_screen.width - WIDTH) / 2)
    window.move(x_pos, 0)

def run_tally():
    window = webview.create_window(
        title=TITLE,
        url=URL,
        width=WIDTH,
        height=HEIGHT,
        on_top=True,
        frameless=True,
        easy_drag=True,
        focus=False,
        min_size=(1, 1)
    )
    
    webview.start(func=setup_window, args=(window,))
    
if __name__ == '__main__':
    run_tally()