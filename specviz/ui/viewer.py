
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..third_party.qtpy.QtCore import *
from ..third_party.qtpy.QtWidgets import *
from ..third_party.qtpy.QtGui import *

from ..core.comms import Dispatch
from .widgets.windows import MainWindow


class Viewer(object):
    """
    The `Viewer` is the main construction area for all GUI widgets. This
    object does **not** control the interactions between the widgets,
    but only their creation and placement.
    """
    def __init__(self):
        # Instantiate main window object
        self._all_tool_bars = {}

        self.main_window = MainWindow()
        self.menu_docks = QMenu("Plugins")
        self.main_window.menu_bar.addMenu(self.menu_docks)

        self.menu_docks.addSeparator()

        # self.main_window.setDockNestingEnabled(True)

        # Load system and user plugins
        self.load_plugins()
        from ..interfaces.registries import loader_registry

        # Setup up top-level connections
        self._setup_connections()

    def load_plugins(self):
        from ..interfaces.registries import plugin_registry

        instance_plugins = plugin_registry.members

        for instance_plugin in sorted(instance_plugins,
                                      key=lambda x: x.priority):
            if instance_plugin.location != 'hidden':
                if instance_plugin.location == 'right':
                    location = Qt.RightDockWidgetArea
                elif instance_plugin.location == 'top':
                    location = Qt.TopDockWidgetArea
                else:
                    location = Qt.LeftDockWidgetArea

                self.main_window.addDockWidget(location, instance_plugin)
                # instance_plugin.show()

                # Add this dock's visibility action to the menu bar
                self.menu_docks.addAction(
                    instance_plugin.toggleViewAction())

        # Sort actions based on priority
        all_actions = [y for x in instance_plugins for y in x._actions]

        for cat in sorted([x['category'] for x in all_actions],
                          key=lambda x: x[0]):
            tool_bar = self._get_tool_bar(*cat)

            for act in sorted([x for x in all_actions
                               if x['category'][0] == cat[0]],
                              key=lambda x: x['priority'],
                              reverse=True):
                tool_bar.addAction(act['action'])

        # Sort tool bars based on priorty
        all_tool_bars = self._all_tool_bars.values()

        for tb in sorted(all_tool_bars, key=lambda x: x['priority'],
                         reverse=True):
            self.main_window.addToolBar(tb['widget'])

    def _get_tool_bar(self, name, priority):
        if name is None:
            name = "User Plugins"
            priority = -1

        if name not in self._all_tool_bars:
            tool_bar = QToolBar(name)
            tool_bar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            tool_bar.show()

            self._all_tool_bars[name] = dict(widget=tool_bar,
                                             priority=int(priority),
                                             name=name)
        else:
            if self._all_tool_bars[name]['priority'] == 0:
                self._all_tool_bars[name]['priority'] = priority

        return self._all_tool_bars[name]['widget']

    def _setup_connections(self):
        # Listen for subwindow selection events, update layer list on selection
        self.main_window.mdi_area.subWindowActivated.connect(
            lambda wi: Dispatch.on_selected_window.emit(
            window=wi.widget() if wi is not None else None))



