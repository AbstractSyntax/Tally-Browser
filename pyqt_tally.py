import sys
import os
import urllib.request
import urllib.error
import base64 

from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QFormLayout, 
                             QLineEdit, QDialogButtonBox, QDoubleSpinBox, QSpinBox,
                             QSystemTrayIcon, QMenu, QStyle, QMessageBox, QComboBox, QWidgetAction, QSlider, QWidget, QLabel)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QIcon # Ensure QIcon is imported
from PyQt6.QtWebEngineCore import QWebEngineScript

# --- Defaults ---
DEFAULT_IP = '192.168.8.140'
DEFAULT_INPUT = 'hdmi_1'
DEFAULT_USER = 'user'
DEFAULT_PASS = '0000'
DEFAULT_WIDTH = 700
DEFAULT_HEIGHT = 20
DEFAULT_OPACITY = 0.5
DEFAULT_POSITION = "Top"

# --- HELPER: Get File Path inside EXE ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tally Configuration")
        
        # Set the Window Icon for the Dialog too
        self.setWindowIcon(QIcon(resource_path("fixed_icon.ico")))
        
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.resize(300, 300)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Inputs
        self.ip_input = QLineEdit(DEFAULT_IP)
        self.ip_input.setPlaceholderText("e.g. 192.168.1.50")
        
        self.input_name = QLineEdit(DEFAULT_INPUT)
        self.user_input = QLineEdit(DEFAULT_USER)
        self.pass_input = QLineEdit(DEFAULT_PASS)
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password) 

        self.width_input = QSpinBox()
        self.width_input.setRange(10, 4000)
        self.width_input.setValue(DEFAULT_WIDTH)

        self.height_input = QSpinBox()
        self.height_input.setRange(10, 2000)
        self.height_input.setValue(DEFAULT_HEIGHT)

        self.position_input = QComboBox()
        self.position_input.addItems(["Top", "Bottom", "Left", "Right"])
        self.position_input.setCurrentText(DEFAULT_POSITION)

        self.opacity_input = QDoubleSpinBox()
        self.opacity_input.setRange(0.1, 1.0)
        self.opacity_input.setSingleStep(0.1)
        self.opacity_input.setValue(DEFAULT_OPACITY)

        form_layout.addRow("Tally IP:", self.ip_input)
        form_layout.addRow("Input ID:", self.input_name)
        form_layout.addRow("Username:", self.user_input)
        form_layout.addRow("Password:", self.pass_input)
        form_layout.addRow("Position:", self.position_input)
        form_layout.addRow("Width (px):", self.width_input)
        form_layout.addRow("Height (px):", self.height_input)
        form_layout.addRow("Opacity (0-1):", self.opacity_input)

        layout.addLayout(form_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

        self.buttons.rejected.connect(self.reject)
        self.ok_button = self.buttons.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.clicked.connect(self.check_connection)

    def check_connection(self):
        original_text = self.ok_button.text()
        self.ok_button.setText("Testing...")
        self.ok_button.setEnabled(False)
        QApplication.processEvents() 

        data = self.get_data()
        ip = data['ip'].replace("http://", "").replace("https://", "").rstrip("/")
        test_url = f"http://{ip}/tally/{data['input']}"
        
        try:
            req = urllib.request.Request(test_url)
            auth_str = f"{data['user']}:{data['pass']}"
            auth_bytes = auth_str.encode("utf-8")
            auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
            req.add_header("Authorization", f"Basic {auth_base64}")

            with urllib.request.urlopen(req, timeout=3) as response:
                if response.getcode() == 200:
                    self.accept()
                else:
                    self.show_error(f"Connected, but received status: {response.getcode()}")

        except urllib.error.HTTPError as e:
            if e.code == 401:
                self.show_error("Authentication Failed.\nThe device rejected the password.")
            elif e.code == 404:
                self.show_error(f"Input '{data['input']}' not found.\nCheck Input ID.")
            else:
                self.show_error(f"HTTP Error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            self.show_error(f"Connection Failed to {ip}.\nReason: {e.reason}")
        except Exception as e:
            self.show_error(f"Error:\n{str(e)}")
        finally:
            self.ok_button.setText(original_text)
            self.ok_button.setEnabled(True)

    def show_error(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Connection Failed")
        msg.setText("Settings Incorrect")
        msg.setInformativeText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def get_data(self):
        return {
            'ip': self.ip_input.text().strip(),
            'input': self.input_name.text().strip(),
            'user': self.user_input.text().strip(),
            'pass': self.pass_input.text().strip(),
            'position': self.position_input.currentText(),
            'width': self.width_input.value(),
            'height': self.height_input.value(),
            'opacity': self.opacity_input.value()
        }
        
def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Set the default icon for the whole app
    app_icon = QIcon(resource_path("fixed_icon.ico"))
    app.setWindowIcon(app_icon)

    dialog = SettingsDialog()
    if dialog.exec() != QDialog.DialogCode.Accepted:
        sys.exit()

    settings = dialog.get_data()
    final_url = f"http://{settings['user']}:{settings['pass']}@{settings['ip']}/tally/{settings['input']}"
    
    
    def update_opacity(value):
        new_opacity = value / 100.0
        view.setWindowOpacity(new_opacity)


    tray_icon = QSystemTrayIcon()
    
    # --- FIX: Use the custom icon from the resource path ---
    tray_icon.setIcon(app_icon)
    # -------------------------------------------------------
    
    tray_icon.setVisible(True)

    tray_menu = QMenu()
    quit_action = QAction("Exit Tally", app)
    quit_action.triggered.connect(app.quit)
    tray_menu.addAction(quit_action)
    tray_icon.setContextMenu(tray_menu)

    view = QWebEngineView()
    view.setWindowFlags(
        Qt.WindowType.FramelessWindowHint | 
        Qt.WindowType.WindowStaysOnTopHint |
        Qt.WindowType.Tool 
    )

    view.setWindowOpacity(settings['opacity'])
    view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    view.page().setBackgroundColor(Qt.GlobalColor.transparent)
    view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    script_source = """
    var css = 'body { overflow: hidden !important; margin: 0; background-color: transparent; }';
    var head = document.head || document.getElementsByTagName('head')[0];
    var style = document.createElement('style');
    style.type = 'text/css';
    style.appendChild(document.createTextNode(css));
    head.appendChild(style);
    """
    
    web_script = QWebEngineScript()
    web_script.setSourceCode(script_source)
    web_script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
    web_script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
    view.page().scripts().insert(web_script)
    
    
    #Add opacity slider
    opacity_widget = QWidget()
    opacity_layout = QVBoxLayout(opacity_widget)
    opacity_layout.setContentsMargins(10, 10, 10, 10)
    opacity_label = QLabel("Opacity")
    opacity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    opacity_layout.addWidget(opacity_label)
    
    opacity_slider = QSlider(Qt.Orientation.Horizontal)
    opacity_slider.setRange(0, 100)
    opacity_slider.setValue(int(settings['opacity'] * 100))
    
    opacity_slider.valueChanged.connect(update_opacity)
    
    opacity_layout.addWidget(opacity_slider)
    opacity_action = QWidgetAction(tray_menu)
    opacity_action.setDefaultWidget(opacity_widget)
    tray_menu.addAction(opacity_action)
    

    screen_rect = app.primaryScreen().availableGeometry()
    
    width = settings['width']
    height = settings['height']
    position = settings['position']

    x_pos = screen_rect.x()
    y_pos = screen_rect.y()

    if position == "Top":
        x_pos += int((screen_rect.width() - width) / 2)
    elif position == "Bottom":
        x_pos += int((screen_rect.width() - width) / 2)
        y_pos += (screen_rect.height() - height)
    elif position == "Left":
        y_pos += int((screen_rect.height() - height) / 2)
    elif position == "Right":
        x_pos += (screen_rect.width() - width)
        y_pos += int((screen_rect.height() - height) / 2)
    
    view.setGeometry(x_pos, y_pos, width, height)

    print(f"Loading Tally at {position}: {x_pos},{y_pos} ({width}x{height})")
    view.load(QUrl(final_url))
    view.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()