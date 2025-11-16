# client/overlay/ui.py
import sys
import threading
import asyncio
import json
import ctypes
from PySide6 import QtWidgets, QtCore, QtGui
from .config import WINDOW_WIDTH, WINDOW_HEIGHT, WEBSOCKET_URL, BACKEND_URL
from .state_manager import state
from .api import start_background_loop
import aiohttp
import websockets
from .auth import login_via_browser
from .api import fetch_contracts, fetch_contract_status, start_contract, join_contract, reserve_name

# Win32 helpers for click-through (Windows only)
try:
    user32 = ctypes.windll.user32
    gwl_exstyle = -20
    ws_ex_transparent = 0x20
    ws_ex_layered = 0x80000
    def set_window_clickthrough(hwnd, enable: bool):
        ex = user32.GetWindowLongW(hwnd, gwl_exstyle)
        if enable:
            user32.SetWindowLongW(hwnd, gwl_exstyle, ex | ws_ex_transparent | ws_ex_layered)
        else:
            user32.SetWindowLongW(hwnd, gwl_exstyle, ex & ~(ws_ex_transparent))
except Exception:
    def set_window_clickthrough(hwnd, enable: bool):
        pass  # no-op on non-Windows

class ContractRow(QtWidgets.QWidget):
    def __init__(self, contract: dict, parent=None):
        super().__init__(parent)
        self.contract = contract
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(54)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8,4,8,4)
        lbl = QtWidgets.QLabel(f"{self.contract.get('type_contract','?')} #{self.contract.get('id')}")
        lbl.setStyleSheet("color:white; font-weight:600;")
        layout.addWidget(lbl)
        layout.addStretch()
        status = QtWidgets.QLabel(self.contract.get('status','-'))
        status.setStyleSheet("color: #ddd;")
        layout.addWidget(status)

class OverlayWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self._moving = False

        main = QtWidgets.QVBoxLayout(self)
        main.setContentsMargins(6,6,6,6)

        # Title bar
        titlebar = QtWidgets.QFrame()
        titlebar.setFixedHeight(36)
        tb_layout = QtWidgets.QHBoxLayout(titlebar)
        tb_layout.setContentsMargins(8,0,8,0)
        self.title_lbl = QtWidgets.QLabel("Контракти")
        self.title_lbl.setStyleSheet("color:white; font-weight:700;")
        tb_layout.addWidget(self.title_lbl)
        tb_layout.addStretch()
        self.login_btn = QtWidgets.QPushButton("Login with Discord")
        self.login_btn.setFixedHeight(26)
        self.login_btn.clicked.connect(self.on_login)
        tb_layout.addWidget(self.login_btn)
        self.lock_btn = QtWidgets.QPushButton("🔒")
        self.lock_btn.setFixedSize(28,20)
        self.lock_btn.clicked.connect(self.toggle_click)
        tb_layout.addWidget(self.lock_btn)
        main.addWidget(titlebar)

        # Content
        self.content = QtWidgets.QFrame()
        self.content.setObjectName("content")
        self.content.setStyleSheet("""
            QFrame#content {
                background: rgba(10,10,10,0.45);
                border-radius: 10px;
            }
        """)
        content_layout = QtWidgets.QVBoxLayout(self.content)
        content_layout.setContentsMargins(8,8,8,8)

        # Scroll area for contracts
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea{ background: transparent; }")
        self.list_widget = QtWidgets.QWidget()
        self.list_layout = QtWidgets.QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0,0,0,0)
        self.list_layout.setSpacing(6)
        self.list_layout.addStretch()
        self.scroll.setWidget(self.list_widget)
        content_layout.addWidget(self.scroll)

        # Buttons
        self.refresh_btn = QtWidgets.QPushButton("Оновити")
        self.refresh_btn.clicked.connect(self.on_refresh)
        content_layout.addWidget(self.refresh_btn)

        main.addWidget(self.content)

        self.setStyleSheet("""
            QPushButton {
                background: rgba(30,30,30,0.6);
                color: white;
                border-radius: 8px;
                padding: 6px 10px;
                font-weight:600;
            }
            QPushButton:hover {
                background: rgba(60,60,60,0.8);
            }
        """)

        # Signals
        state.signals.contracts_updated.connect(self.on_contracts_updated)
        state.signals.contract_updated.connect(self.on_contract_updated)
        state.signals.token_changed.connect(self.on_token_changed)

        # Start background asyncio loop and WS listener
        self._bg_loop = asyncio.new_event_loop()
        self._bg_thread = threading.Thread(target=self._start_loop_forever, daemon=True)
        self._bg_thread.start()

        # create aiohttp session in background loop
        asyncio.run_coroutine_threadsafe(self._create_session_and_start_ws(), self._bg_loop)

    def _start_loop_forever(self):
        asyncio.set_event_loop(self._bg_loop)
        self._bg_loop.run_forever()

    async def _create_session_and_start_ws(self):
        self._session = aiohttp.ClientSession()
        start_background_loop(self._bg_loop, self._session)
        # initial fetch
        try:
            contracts = await fetch_contracts(self._session)
            state.set_contracts(contracts)
        except Exception as e:
            print("Fetch contracts failed:", e)
        # start websocket listener
        asyncio.create_task(self._ws_listener())

    async def _ws_listener(self):
        # connect to backend websocket
        url = WEBSOCKET_URL
        try:
            async with websockets.connect(url) as ws:
                print("WS connected")
                async for message in ws:
                    try:
                        data = json.loads(message)
                    except Exception:
                        data = {"raw": message}
                    # forward into state
                    state.signals.ws_message.emit(data)
        except Exception as e:
            print("WS error:", e)

    # UI callbacks
    def on_login(self):
        # open browser and start local callback server (auth.login_via_browser)
        t, loop, server = login_via_browser()
        self.title_lbl.setText("Waiting for login...")

    def on_token_changed(self, token):
        self.title_lbl.setText("Logged in")
        self.login_btn.setText("Logged")

    def on_refresh(self):
        # trigger fetch contracts
        asyncio.run_coroutine_threadsafe(self._fetch_and_update(), self._bg_loop)

    async def _fetch_and_update(self):
        try:
            contracts = await fetch_contracts(self._session)
            state.set_contracts(contracts)
        except Exception as e:
            print("Refresh error:", e)

    def on_contracts_updated(self, contracts):
        # clear existing non-stretch items
        for i in reversed(range(self.list_layout.count()-1)):
            item = self.list_layout.itemAt(i).widget()
            if item:
                item.setParent(None)
        for c in contracts:
            row = ContractRow(c)
            row.mousePressEvent = lambda e, cc=c: self.on_contract_clicked(cc)
            self.list_layout.insertWidget(self.list_layout.count()-1, row)

    def on_contract_updated(self, contract):
        # find updated row and update visually (simple: refresh all)
        self.on_refresh()

    def on_contract_clicked(self, contract):
        dlg = ContractDialog(contract, parent=self)
        dlg.exec_()

    def on_token_changed(self, token):
        self.login_btn.setText("Logged")

    def toggle_click(self):
        hwnd = int(self.winId())
        if self.lock_btn.text() == "🔒":
            set_window_clickthrough(hwnd, True)
            self.lock_btn.setText("🔓")
        else:
            set_window_clickthrough(hwnd, False)
            self.lock_btn.setText("🔒")

    # dragging
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._moving = True
            self._start_pos = event.globalPosition().toPoint()
            self._click_pos = self.pos()

    def mouseMoveEvent(self, event):
        if self._moving:
            delta = event.globalPosition().toPoint() - self._start_pos
            self.move(self._click_pos + delta)

    def mouseReleaseEvent(self, event):
        self._moving = False

class ContractDialog(QtWidgets.QDialog):
    def __init__(self, contract: dict, parent=None):
        super().__init__(parent)
        self.contract = contract
        self.setModal(True)
        self.setWindowTitle(f"Contract #{contract.get('id')}")
        self.setFixedSize(360, 240)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        lbl = QtWidgets.QLabel(f"Type: {self.contract.get('type_contract')}")
        layout.addWidget(lbl)
        lbl2 = QtWidgets.QLabel(f"Status: {self.contract.get('status')}")
        layout.addWidget(lbl2)
        self.join_btn = QtWidgets.QPushButton("Прийняти участь")
        self.join_btn.clicked.connect(self.on_join)
        layout.addWidget(self.join_btn)
        self.reserve_btn = QtWidgets.QPushButton("Зарезервувати нік")
        self.reserve_btn.clicked.connect(self.on_reserve)
        layout.addWidget(self.reserve_btn)
        self.list_btn = QtWidgets.QPushButton("Список")
        self.list_btn.clicked.connect(self.on_list)
        layout.addWidget(self.list_btn)

    def on_join(self):
        # ask nickname
        nick, ok = QtWidgets.QInputDialog.getText(self, "Нік персонажа", "Введіть ваш нік:")
        if not ok or not nick:
            return
        # call join via background
        asyncio.run_coroutine_threadsafe(self._join(nick), self.parent()._bg_loop)

    async def _join(self, nick):
        try:
            res = await join_contract(self.parent()._session, self.contract.get("id"), nick)
            print("join res:", res)
        except Exception as e:
            print("join error:", e)

    def on_reserve(self):
        nick, ok = QtWidgets.QInputDialog.getText(self, "Резерв нік", "Введіть нік для резерву:")
        if not ok or not nick:
            return
        asyncio.run_coroutine_threadsafe(self._reserve(nick), self.parent()._bg_loop)

    async def _reserve(self, nick):
        try:
            res = await reserve_name(self.parent()._session, self.contract.get("id"), nick)
            print("reserve res:", res)
        except Exception as e:
            print("reserve error:", e)

    def on_list(self):
        # fetch list and show results
        asyncio.run_coroutine_threadsafe(self._fetch_list_and_show(), self.parent()._bg_loop)

    async def _fetch_list_and_show(self):
        try:
            data = await fetch_contract_status(self.parent()._session, self.contract.get("id"))
            # show simple dialog
            participants = data.get("participants_count", 0)
            reserves = data.get("reservations_count", 0)
            QtWidgets.QMessageBox.information(self, "Список", f"Учасників: {participants}\nРезервів: {reserves}")
        except Exception as e:
            print("list error:", e)

def main():
    app = QtWidgets.QApplication(sys.argv)
    overlay = OverlayWindow()
    # position bottom-left like your screenshot, tweak as needed
    screen = app.primaryScreen().availableGeometry()
    overlay.move(60, 180)
    overlay.show()
    # by default allow clicks
    set_window_clickthrough(int(overlay.winId()), False)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
