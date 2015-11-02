#!/usr/bin/env python3
import sys
import time as time_io
import gi
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, AppIndicator3, GLib

class Timer:
    def __init__(self, name, total_time):
        self.name = name
        self.time_remaining = total_time # In seconds
        self.start_time = None

    def get_time(self):
        time = self.time_remaining
        if self.start_time is not None:
            time -= (time_io.time() - self.start_time)
        return time if time > 0 else 0

    def start(self):
        self.start_time = time_io.time()

    def pause(self):
        self.time_remaining = self.get_time()
        self.start_time = None

    def is_running(self):
        return self.start_time is not None

class PomodoroIndicator:
    def __init__(self):
        # Create Menu
        self.menu = Gtk.Menu()

        self.toogle_timer_item = Gtk.MenuItem("")
        self.toogle_timer_item.connect("activate", self.toogle_timer)
        self.menu.append(self.toogle_timer_item)

        self.delete_timer_item = Gtk.MenuItem("Remove")
        self.delete_timer_item.connect("activate", self.delete_timer)
        self.menu.append(self.delete_timer_item)

        self.toogle_separator = Gtk.SeparatorMenuItem()
        self.menu.append(self.toogle_separator)

        pomodoro_item = Gtk.MenuItem("Pomodoro")
        pomodoro_item.connect("activate", self.start_pomodoro)
        self.menu.append(pomodoro_item)

        short_break_item = Gtk.MenuItem("Short Break")
        short_break_item.connect("activate", self.start_short_break)
        self.menu.append(short_break_item)

        long_break_item = Gtk.MenuItem("Long Break")
        long_break_item.connect("activate", self.start_long_break)
        self.menu.append(long_break_item)

        separator = Gtk.SeparatorMenuItem()
        self.menu.append(separator)

        quit = Gtk.MenuItem("Quit")
        quit.connect("activate", self.quit)
        self.menu.append(quit)

        self.menu.show_all()

        # Create Indicator
        self.indicator = AppIndicator3.Indicator.new("indicator-pomodoro", "", AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status (AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.menu)

        self.timer = None
        self.update_time()
        self.update_interface()

    def start_pomodoro(self, widget): self.create_timer("Pomodoro", 25*60)
    def start_short_break(self, widget): self.create_timer("Short break", 5*60)
    def start_long_break(self, widget): self.create_timer("Long break", 15*60)

    def create_timer(self, name, time):
        notify(name + " started")
        self.timer = Timer(name, time)
        self.timer.start()
        self.update_interface()

    def toogle_timer(self, widget):
        if self.timer is None:
            pass
        elif self.timer.is_running():
            self.timer.pause()
        else:
            self.timer.start()

        self.update_interface()

    def delete_timer(self, widget):
        self.timer = None
        self.update_interface()

    def update_interface(self):
        if self.timer is None:
            self.indicator.set_icon("alarm-clock-panel")
            self.toogle_timer_item.hide()
            self.toogle_separator.hide()
            self.delete_timer_item.hide()
            return

        self.delete_timer_item.show()
        self.toogle_timer_item.show()
        self.toogle_separator.show()

        if self.timer.is_running():
            self.indicator.set_icon("alarm-clock-triggered")
            self.toogle_timer_item.set_label("Pause")
        else:
            self.indicator.set_icon("alarm-clock-panel")
            self.toogle_timer_item.set_label("Resume")

    def update_time(self):
        GLib.timeout_add(1000, self.update_time) # Every second
        if self.timer is None:
            self.indicator.set_label("", "")
            return

        time = self.timer.get_time()

        if time == 0:
            notify(self.timer.name + " ended!", True)
            self.delete_timer(None)

        self.indicator.set_label("%d:%02d" % (time/60, time%60), "")

    def create_menu(self):
        menu = Gtk.Menu()

        # Quit
        quit = Gtk.MenuItem("Quit")
        quit.connect("activate", self.quit)
        quit.show()
        menu.append(quit)

        return menu

    def quit(self, widget):
        sys.exit(0)

def notify(message, is_critical = False):
    subprocess.Popen(['notify-send', '-u', 'critical' if is_critical else 'low', message])
    return


if __name__ == "__main__":
    indicator = PomodoroIndicator()
    Gtk.main()
