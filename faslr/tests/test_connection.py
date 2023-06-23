import os

from faslr.connection import (
    ConnectionDialog,
    FaslrConnection,
    connect_db,
    get_startup_db_path
)

from faslr.constants import DEFAULT_DIALOG_PATH

from faslr.__main__ import MainWindow

from sqlalchemy.engine import Engine
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.session import Session


from pathlib import Path

from pynput.keyboard import (
    Key,
    Controller
)

from PyQt6.QtCore import QTimer, Qt

from PyQt6.QtWidgets import QApplication

from pytestqt.qtbot import QtBot


def test_connection_dialog_existing(qtbot: QtBot) -> None:
    """
    Test whether the connection dialog can initiate a connection to an existing database. In this case,
    the sample database.

    :param qtbot: The QtBot fixture.
    :return: None
    """

    def handle_dialog() -> None:
        """
        Simulate keystrokes to type in the database name and press enter.
        :return: None
        """
        keyboard = Controller()

        dialog = QApplication.activeModalWidget()
        qtbot.addWidget(dialog)

        qtbot.waitUntil(
            callback=dialog.isVisible,
            timeout=5000
        )
        keyboard.type('sample.db')
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

    main_window = MainWindow()

    connection_dialog = ConnectionDialog(parent=main_window.menu_bar)

    # Set the radio button to indicate we want to connect to an existing database.
    connection_dialog.existing_connection.setChecked(True)

    QTimer.singleShot(
        500,
        handle_dialog
    )

    qtbot.mouseClick(
        connection_dialog.button_box.button(connection_dialog.ok_button),
        Qt.MouseButton.LeftButton,
        delay=1
    )

    main_window.close()


def test_connection_dialog_new(qtbot: QtBot) -> None:
    """
    Test whether the connection dialog can create a new database and connect to it.

    :param qtbot: The QtBot fixture.
    :return: None
    """

    db_name = 'unittest.db'

    def handle_dialog():
        keyboard = Controller()

        dialog = QApplication.activeModalWidget()
        qtbot.addWidget(dialog)

        qtbot.waitUntil(
            callback=dialog.isVisible,
            timeout=5000
        )
        keyboard.type(db_name)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

    main_window = MainWindow()
    connection_dialog = ConnectionDialog(parent=main_window.menu_bar)

    connection_dialog.new_connection.setChecked(True)

    QTimer.singleShot(
        500,
        handle_dialog
    )

    qtbot.mouseClick(
        connection_dialog.button_box.button(connection_dialog.ok_button),
        Qt.MouseButton.LeftButton,
        delay=1
    )

    main_window.close()

    db_path = DEFAULT_DIALOG_PATH + '/' + db_name

    if os.path.isfile(db_path):
        os.remove(db_path)


def test_connection_dialog_replace(qtbot: QtBot) -> None:
    """
    Test the scenario when you decide to create a new database, but when replacing a file that already exists.

    :param qtbot: The QtBot fixture.
    :return: None
    """

    db_name = 'unittest.db'
    db_path = DEFAULT_DIALOG_PATH + '/' + db_name

    Path(db_path).touch()

    def handle_override() -> None:
        """
        This simulates the keystrokes needed to handle the popup asking if you want to replace an
        existing file.
        :return: None
        """
        keyboard = Controller()

        dialog_override = QApplication.activeModalWidget()
        qtbot.addWidget(dialog_override)

        qtbot.waitUntil(
            callback=dialog_override.isVisible,
            timeout=5000
        )

        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

    def handle_dialog():
        keyboard = Controller()

        dialog = QApplication.activeModalWidget()
        qtbot.addWidget(dialog)

        qtbot.waitUntil(
            callback=dialog.isVisible,
            timeout=5000
        )
        keyboard.type(db_name)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

        QTimer.singleShot(500, handle_override)

    main_window = MainWindow()
    connection_dialog = ConnectionDialog(parent=main_window.menu_bar)

    connection_dialog.new_connection.setChecked(True)

    QTimer.singleShot(500, handle_dialog)

    qtbot.mouseClick(
        connection_dialog.button_box.button(connection_dialog.ok_button),
        Qt.MouseButton.LeftButton,
        delay=1
    )

    main_window.close()

    if os.path.isfile(db_path):
        os.remove(db_path)


def test_connection_dialog_cancel(qtbot: QtBot) -> None:
    """
    Test whether pressing cancel on the connection dialog exits it.

    :param qtbot: The QtBot fixture.
    :return: None
    """

    main_window = MainWindow()
    connection_dialog = ConnectionDialog(parent=main_window.menu_bar)

    connection_dialog.reject()


def test_faslr_connection(qtbot: QtBot) -> None:
    """
    Test the initialization of the FaslrConnection class and its attributes.

    :param qtbot: The QtBot fixture.
    :return: None
    """

    faslr_connection = FaslrConnection(
        db_path='sample.db'
    )

    assert isinstance(faslr_connection.engine, Engine)
    assert isinstance(faslr_connection.session, Session)
    assert isinstance(faslr_connection.connection, Connection)

    faslr_connection.session.close()


def test_connect_db() -> None:
    """
    Test function to connect to a database.

    :return: None
    """

    session_test, connection_test = connect_db('sample.db')

    assert isinstance(session_test, Session)
    assert isinstance(connection_test, Connection)

    session_test.close()


def test_get_startup_db_path() -> None:

    startup_db = get_startup_db_path()

    assert startup_db == 'None'
