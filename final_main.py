#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yum

import locale

import curses
import time


# fce apply
# uninstall + install
# reload

# F1

FILTER = "" 
UPDATES = False
REPAIR = False

class MainApp():
  '''Main class of yum extension using curses.'''
  
  DOWN = 1
  UP = -1
  P_DOWN = 20
  P_UP = -20
  RIGHT = 1
  LEFT = -1
  SPACE_KEY = 32
  ESC_KEY =  27
  N_LINES = 21

  

  INSTALLED = 0
  AVAILABLE = 1
  
  def __init__(self, screen):
    '''Ctor of this class'''
    self.active_window = self.INSTALLED
    self.installed_data = list()
    self.available_data = list()
    self.installed_marked = list()
    self.available_marked = list()

    

    self.installed_top = 0
    self.available_top = 0
    self.active_category = 0
    self.active_installed = 0
    self.active_available = 0

    self.yum_base = yum.YumBase()
    self.yum_base.doConfigSetup()
    self.yum_base.doTsSetup()
 
    self.stdscr = screen
    curses.curs_set(0)
    self.init_colors()
    (self.window_max_y, self.window_max_x) = self.stdscr.getmaxyx()
    self.load_data()

    locale.setlocale(locale.LC_ALL, "")

    self.run()
    return None

   

#  def __enter__(self):
#    self.stdscr = curses.initscr()
#    curses.noecho()
#    curses.cbreak()
#    self.stdscr.keypad(1)
#    curses.start_color()
#    curses.curs_set(0)
#    self.init_colors()

    return self

  def init_colors(self):
    '''Prepaire required color combinations'''
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLUE)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLUE)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)

    self.DIM_RED = curses.color_pair(1)
    self.DIM_GREEN = curses.color_pair(2)
    self.DIM_MAGENTA = curses.color_pair(3)
    self.DIM_CYAN = curses.color_pair(4)
    self.DIM_YELLOW = curses.color_pair(5)
    self.DIM_WHITE = curses.color_pair(6)

    self.RED = curses.color_pair(1) | curses.A_BOLD
    self.GREEN = curses.color_pair(2) | curses.A_BOLD
    self.MAGENTA = curses.color_pair(3) | curses.A_BOLD
    self.CYAN = curses.color_pair(4) | curses.A_BOLD
    self.YELLOW = curses.color_pair(5) | curses.A_BOLD
    self.WHITE = curses.color_pair(6) | curses.A_BOLD

    self.COLOR_EXIT = curses.color_pair(7)
    self.REVERSE = curses.A_REVERSE | curses.A_DIM | curses.A_BOLD

  def display_screen(self):
    '''Method used for refreshing screen'''
    
    self.stdscr.refresh()
    self.installed_window()
    self.available_window()
    self.command_window()
    curses.doupdate()

  def run(self):
    '''Application main loop'''
    while True:
      self.display_screen()
      c = self.stdscr.getch()
      if c == curses.KEY_UP:
        self.up_down(self.UP)
      elif c == curses.KEY_DOWN:
        self.up_down(self.DOWN)
      elif c == curses.KEY_LEFT:
        self.left_right(self.LEFT)
      elif c == curses.KEY_RIGHT:
        self.left_right(self.RIGHT)
      elif c == curses.KEY_PPAGE:
        self.page_up_down(self.P_UP)
      elif c == curses.KEY_NPAGE:
        self.page_up_down(self.P_DOWN)
      elif c == self.SPACE_KEY:
        self.mark_line()
      elif c == curses.KEY_F6:
        self.help_window()
      elif c == curses.KEY_F2:
        self.remove_marked()
      elif c == curses.KEY_F3:
        self.install_marked()
      elif c == curses.KEY_F4:
        self.autoinstall_updates()
      elif c == curses.KEY_F5:
        self.load_data()
        self.Installed.refresh()
        self.Available.refresh()
        self.Command.refresh()
      elif c == curses.KEY_F7:
        self.sort_window()

      elif c == self.ESC_KEY:
        break
    pass

  def show_data_installed(self):
    '''Display loaded data to the installed subwindow'''
    data_width = 38
    (sub_win_y, sub_win_x) = self.Installed.getmaxyx()
    sub_win_y -= 2
    sub_win_x -= 2

    # size of inner 'panel'
    pad_y = max(sub_win_y, len(self.installed_data)+1)
    pad_x = max(sub_win_x, 300)
    top = self.installed_top
    bottom = self.installed_top + self.N_LINES
    for (index, line) in enumerate(self.installed_data[top:bottom]):
      line_num = self.installed_top + index
      if (line_num in self.installed_marked):
        if (index != self.active_installed):
          self.Installed.addstr(index + 1, 1, line[0][:data_width], self.RED)
        else:
          self.Installed.addstr(index + 1, 1, line[0][:data_width], self.WHITE)
      else: # not marked
        if (index != self.active_installed):
          self.Installed.addstr(index + 1, 1, line[0][:data_width], self.CYAN)
        else:
          self.Installed.addstr(index + 1, 1, line[0][:data_width], self.YELLOW)
    return

  def show_data_available(self):
    '''Display loaded data to the available subwindow'''
    data_width = 38
    (sub_win_y, sub_win_x) = self.Available.getmaxyx()
    sub_win_y -= 2
    sub_win_x -= 2

    # size of inner 'panel'
    pad_y = max(sub_win_y, len(self.available_data)+1)
    pad_x = max(sub_win_x, 300)
    top = self.available_top
    bottom = self.available_top + self.N_LINES
    for (index, line) in enumerate(self.available_data[top:bottom]):
      line_num = self.available_top + index
      if (line_num in self.available_marked):
        if (index != self.active_available):
          self.Available.addstr(index + 1, 1, line[0][:data_width], self.RED)
        else:
          self.Available.addstr(index + 1, 1, line[0][:data_width], self.WHITE)
      else: # not marked
        if (index != self.active_available):
          self.Available.addstr(index + 1, 1, line[0][:data_width], self.CYAN)
        else:
          self.Available.addstr(index + 1, 1, line[0][:data_width], self.YELLOW)
    return

  def show_summary(self):
    '''Display loaded data to the available subwindow'''
    data = ''
    if (self.active_window == self.INSTALLED):
      data = str(self.installed_data[self.active_installed][1].description)
    else:#if (self.active_window == self.AVAILABLE):
      data = str(self.available_data[self.active_available][1].description)
    self.stdscr.refresh()
    self.Summary.addstr(0, 0, 'data', self.WHITE)
    self.Summary.noutrefresh()
    self.Help.noutrefresh()

  def up_down(self, increment):
    ''''''
    if (self.active_window == self.AVAILABLE):
      next_line = self.active_available + increment
      # paging
      if (increment == self.UP and self.active_available == 0 and \
          self.available_top != 0):
        self.available_top += self.UP
        return
      elif (increment == self.DOWN and next_line == self.N_LINES and \
            (self.available_top + self.N_LINES) != self.available_count):
        self.available_top += self.DOWN
        return

      # scroll highlight line
      if (increment == self.UP and (self.available_top != 0 or self.active_available != 0)):
        self.active_available = next_line
      elif (increment == self.DOWN and (self.available_top+self.active_available+1) != \
            self.available_count and self.active_available != self.N_LINES):
        self.active_available = next_line
      return
    elif (self.active_window == self.INSTALLED):
      next_line = self.active_installed + increment
      # paging
      if (increment == self.UP and self.active_installed == 0 and \
          self.installed_top != 0):
        self.installed_top += self.UP
        return
      elif (increment == self.DOWN and next_line == self.N_LINES and \
            (self.installed_top + self.N_LINES) != self.installed_count):
        self.installed_top += self.DOWN
        return

      # scroll highlight line
      if (increment == self.UP and (self.installed_top != 0 or self.active_installed != 0)):
        self.active_installed = next_line
      elif (increment == self.DOWN and (self.installed_top+self.active_installed+1) != \
            self.installed_count and self.active_installed != self.N_LINES):
        self.active_installed = next_line
      return

  def page_up_down(self, increment):
    '''Shift data window after pressing page keys
      ...Under Construction...
    '''
    if (increment == self.P_UP):
      for index in xrange(abs(increment)):
        self.up_down(self.UP)
    elif (increment == self.P_DOWN):
      for index in xrange(abs(increment)):
        self.up_down(self.DOWN)

  def left_right(self, increment):
    if (increment == self.LEFT and self.active_window == self.INSTALLED):
      self.active_window = self.AVAILABLE
    elif (increment == self.LEFT):
      self.active_window += increment
    if (increment == self.RIGHT and self.active_window == self.AVAILABLE):
      self.active_window = self.INSTALLED
    elif (increment == self.RIGHT):
      self.active_window += increment
      

  def mark_line(self):
    '''...'''
    if (self.active_window == self.AVAILABLE):
      line_num = self.available_top + self.active_available
      if (line_num in self.available_marked):
        self.available_marked.remove(line_num)
      else:
        self.available_marked.append(line_num)
    elif (self.active_window == self.INSTALLED):
      line_num = self.installed_top + self.active_installed
      if (line_num in self.installed_marked):
        self.installed_marked.remove(line_num)
      else:
        self.installed_marked.append(line_num)
    else:
      pass


  def description_up_down(self, increment):
    ''''''
#    next_line = self.active_installed + increment
#    # paging
#    if (increment == self.UP and self.active_installed == 0 and \
#        self.installed_top != 0):
#      self.installed_top += self.UP
#      return
#    elif (increment == self.DOWN and next_line == self.N_LINES and \
#          (self.installed_top + self.N_LINES) != self.installed_count):
#      self.installed_top += self.DOWN
#      return
#
#    # scroll highlight line
#    if (increment == self.UP and (self.installed_top != 0 or self.active_installed != 0)):
#      self.active_installed = next_line
#    elif (increment == self.DOWN and (self.installed_top+self.active_installed+1) != \
#          self.installed_count and self.active_installed != self.N_LINES):
#      self.active_installed = next_line
#    return
    pass

  def install_marked(self):
    '''Method for installing previously marked (available) packages
      ...Under Construction...
    '''
    install_list = list()
    for index in sorted(self.available_marked):
      install_list.append(self.available_data[index][1])
    for po in install_list:
      self.yum_base.install(po)

    self.pop_up()

    self.yum_base.resolveDeps()
    self.yum_base.buildTransaction()
    self.yum_base.processTransaction()
    self.Installed.noutrefresh()
    self.Available.noutrefresh()
    self.Command.noutrefresh()
    self.stdscr.refresh()

  def autoinstall_updates(self):
    '''Method for automatic update install
      ...Under Construction...
    '''
    install_list = list()
    
    self.load_updates() #dle aktuálního filtru načte seznam aktualizací
    
    install_list = self.available_data
    for po in install_list:
      self.yum_base.install(po)

    self.pop_up()

    self.yum_base.resolveDeps()
    self.yum_base.buildTransaction()
    self.yum_base.processTransaction()
    self.Installed.noutrefresh()
    self.Available.noutrefresh()
    self.Command.noutrefresh()
    self.stdscr.refresh()

  def remove_marked(self):
    '''Method for removing previously marked (installed) packages
      ...Under Construction...
    '''
    remove_list = list()
    for index in sorted(self.installed_marked):
      remove_list.append(self.installed_data[index][1])
    for po in remove_list:
      self.yum_base.remove(po)

    self.pop_up()

    self.yum_base.resolveDeps()
    self.yum_base.buildTransaction()
    self.yum_base.processTransaction()
    self.Installed.noutrefresh()
    self.Available.noutrefresh()
    self.Command.noutrefresh()
    self.stdscr.refresh()

  def apply_marked(self):
    '''...'''
    self.install_marked()
    self.remove_marked()
    self.load_data()
    self.Installed.noutrefresh()
    self.Available.noutrefresh()
    self.Command.noutrefresh()

  
  def pop_up(self):
    '''...'''
    text = 'Yum is working...'
    self.Pop_up = curses.newwin(3, len(text)+2, (self.window_max_y/2)-2, \
                                ((self.window_max_x - (len(text)+2))/2))
    self.Pop_up.bkgd(self.WHITE)
    self.Pop_up.box()
    self.Pop_up.addstr(1, 1, text, self.WHITE)
    self.Pop_up.noutrefresh()
    self.stdscr.refresh()

  def installed_window(self):
    '''...'''
    global FILTER
    self.Installed = curses.newwin(self.window_max_y - 1, 40, 0, 0)
    if (self.active_window == self.INSTALLED):
      self.Installed.bkgd(self.RED)
    else:
      self.Installed.bkgd(self.WHITE)
    self.Installed.box()
    self.Installed.addstr(0, 1, "Installed:", self.CYAN)
    self.Installed.addstr(0, 12, "%d-%d/%d" % (self.installed_top, \
         self.active_installed ,self.installed_count), self.CYAN)
    self.Installed.addstr(0, 22, FILTER , self.CYAN)
    self.show_data_installed()
    self.Installed.noutrefresh()

  def available_window(self):
    '''...'''
    global FILTER
    self.Available = curses.newwin(self.window_max_y - 1, 40, 0, 40)
    if (self.active_window == self.AVAILABLE):
      self.Available.bkgd(self.RED)
    else:
      self.Available.bkgd(self.WHITE)
    self.Available.box()
    self.Available.addstr(0, 1, "Available:", self.CYAN)
    self.Available.addstr(0, 12, "%d-%d/%d" % (self.available_top, \
         self.active_available ,self.available_count), self.CYAN)
    if UPDATES:
      self.Available.addstr(0, 23, "UPDATES" , self.CYAN)
    elif REPAIR:
      self.Available.addstr(0, 30, "REPAIR" , self.CYAN)
    else:
      self.Available.addstr(0, 20, "", self.CYAN)

    self.show_data_available()
    self.Available.noutrefresh()

  def help_window(self):
    '''...Under Construction...'''
    self.Help = curses.newwin(self.window_max_y - 4, self.window_max_x - 4, 2, 2)
    self.Help.box()
    self.Help.bkgd(self.WHITE)
    self.Help.addstr(2, 2, 'YUM TextInstaller 0.5.5       Author: Nikola Culik', self.CYAN)
    if (self.active_window == self.INSTALLED):
      data = self.installed_data[self.installed_top + self.active_installed][1]
      name = str(data.name)
      ver = str(data.ver)
      group = str(data.group)
      description = str(data.description)
    else:#if (self.active_window == self.AVAILABLE):
      data = self.available_data[self.available_top + self.active_available][1]
      name = str(data.name)
      ver = str(data.ver)
      group = str(data.group)
      description = str(data.description)
    self.Help.addstr(4, 2, 'Name:   ', self.WHITE)
    self.Help.addstr(4, 11, name, self.WHITE)
    self.Help.addstr(5, 2, 'Version:', self.WHITE)
    self.Help.addstr(5, 11, ver, self.WHITE)
    self.Help.addstr(6, 2, 'Group:', self.WHITE)
    self.Help.addstr(6, 11, group, self.WHITE)
    self.Help.addstr(7, 2, 'Description:', self.WHITE)
    

    self.Summary = curses.newwin(self.window_max_y - 15, self.window_max_x - 12, 10, 5)
    self.Summary.bkgd(self.WHITE)
    self.Summary.addstr(0, 0, description, self.WHITE)
    

    
################################################################################
#    self.show_summary()
################################################################################
    self.Help.noutrefresh()
    self.Summary.noutrefresh()
    self.stdscr.refresh()
   # c = self.stdscr.getch()
    while True:
      c = self.stdscr.getch()
      if c == curses.KEY_UP:
        self.description_up_down(self.UP)
      elif c == curses.KEY_DOWN:
        self.description_up_down(self.DOWN)
      elif c == curses.KEY_F6:
        break
      elif c == self.ESC_KEY:
        break
    self.Installed.noutrefresh()
    self.Available.noutrefresh()
    self.stdscr.refresh()

  def sort_window(self):
    '''.Okno výběru klíče třídění'''
    global FILTER
    global UPDATES
    global REPAIR

    self.Sort = curses.newwin(self.window_max_y - 5, self.window_max_x - 4, 2, 2)
    self.Sort.box()
    self.Sort.bkgd(self.WHITE)

    self.Sort.addstr(4, 2, 'A', self.WHITE)
    self.Sort.addstr(4, 3, 'm', self.YELLOW)
    self.Sort.addstr(4, 4, 'usements', self.WHITE)
    self.Sort.addstr(5, 2, 'A', self.YELLOW)
    self.Sort.addstr(5, 3, 'pplications', self.WHITE)
    self.Sort.addstr(6, 2, 'Developmen', self.WHITE)
    self.Sort.addstr(6, 11, 't', self.YELLOW)
    self.Sort.addstr(7, 2, 'D', self.YELLOW)
    self.Sort.addstr(7, 3, 'ocumentation', self.WHITE)
    self.Sort.addstr(8, 2, 'S', self.YELLOW)
    self.Sort.addstr(8, 3, 'ystem Environment', self.WHITE)
    self.Sort.addstr(9, 2, 'User', self.WHITE)
    self.Sort.addstr(9, 7, 'I', self.YELLOW)
    self.Sort.addstr(9, 8, 'nterface', self.WHITE)
    self.Sort.addstr(10, 2, 'All', self.WHITE)
    self.Sort.addstr(10, 3, 'l', self.YELLOW)

    self.Sort.addstr(12, 2, '[ ] Show ', self.WHITE)
    self.Sort.addstr(12, 11, 'U', self.YELLOW)
    self.Sort.addstr(12, 12, 'pdates only', self.WHITE)
    if UPDATES:
      self.Sort.addstr(12, 3, 'X', self.WHITE)

    self.Sort.addstr(13, 2, '[ ] Show ', self.WHITE)
    self.Sort.addstr(13, 11, 'R', self.YELLOW)
    self.Sort.addstr(13, 12, 'epair packages', self.WHITE)
    if REPAIR:
      self.Sort.addstr(12, 3, 'X', self.WHITE)

    self.Sort.noutrefresh()
    self.stdscr.refresh()
    #c = self.stdscr.getch()
    while True:
      c = self.stdscr.getch()
      if c == ord('m'):
        FILTER = str("Amusements")
        self.Sort.addstr(4, 2, 'Amusements', self.YELLOW)
        break
      elif c == ord('a'):
        FILTER = str("Applications")
        self.Sort.addstr(5, 2, 'Applications', self.YELLOW)
        break
      elif c == ord('t'):
        FILTER = str("Development")
        self.Sort.addstr(6, 2, 'Development', self.YELLOW)
        break
      elif c == ord('d'):
        FILTER = str("Documentation")
        self.Sort.addstr(7, 2, 'Documentation', self.YELLOW)
        break
      elif c == ord('s'):
        FILTER = str("System")
        self.Sort.addstr(8, 2, 'System Environment', self.YELLOW)
        break
      elif c == ord('i'):
        FILTER = str("User")
        self.Sort.addstr(9, 2, 'User Interface', self.YELLOW)
        break
      elif c == ord('l'):
        FILTER = str("")
        self.Sort.addstr(10, 2, 'All', self.YELLOW)
        break
      elif c == ord('u'):
        if UPDATES:
          UPDATES = False
          self.Sort.addstr(12, 3, ' ', self.WHITE)
          self.Sort.refresh()
        else:
          UPDATES = True
          REPAIR = False
          self.Sort.addstr(12, 3, 'X', self.WHITE)
          self.Sort.addstr(13, 3, ' ', self.WHITE)
          self.Sort.refresh()
      elif c == ord('r'):
        if REPAIR:
          REPAIR = False
          self.Sort.addstr(13, 3, ' ', self.WHITE)
          self.Sort.refresh()
        else:
          REPAIR = True
          UPDATES = False
          self.Sort.addstr(12, 3, ' ', self.WHITE)
          self.Sort.addstr(13, 3, 'X', self.WHITE)
          self.Sort.refresh()
      elif c == curses.KEY_F7:
        break
      elif c == self.ESC_KEY:
        break

    self.load_data()
    self.Installed.noutrefresh()
    self.Available.noutrefresh()
    self.stdscr.refresh()

  def command_window(self):
    '''...'''
    self.Command = curses.newwin(1, self.window_max_x, \
                              self.window_max_y - 1, 0)
    self.Command.bkgd(self.DIM_WHITE)
    self.command_1 = 'F2 Uninstall'
    self.command_1_offset = 0
    self.command_2 = 'F3 Install'
    self.command_2_offset = self.command_1_offset + len(self.command_1) + 1
    self.command_3 = 'F4 Autoupdate'
    self.command_3_offset = self.command_2_offset + len(self.command_2) + 1
    self.command_4 = 'F5 Reload'
    self.command_4_offset = self.command_3_offset + len(self.command_3) + 1
    self.command_5 = 'F6 Info'
    self.command_5_offset = self.command_4_offset + len(self.command_4) + 1
    self.command_6 = 'F7 Filter'
    self.command_6_offset = self.command_5_offset + len(self.command_5) + 1
    self.command_0 = 'ESC Exit'
    self.command_0_offset = self.command_6_offset + len(self.command_6) + 1
    
    self.Command.addstr(0, self.command_1_offset, self.command_1, self.REVERSE)
    self.Command.addstr(0, self.command_2_offset, self.command_2, self.REVERSE)
    self.Command.addstr(0, self.command_3_offset, self.command_3, self.REVERSE)
    self.Command.addstr(0, self.command_4_offset, self.command_4, self.REVERSE)
    self.Command.addstr(0, self.command_5_offset, self.command_5, self.REVERSE)
    self.Command.addstr(0, self.command_6_offset, self.command_6, self.REVERSE)
    self.Command.addstr(0, self.command_0_offset, self.command_0, self.REVERSE)
    self.Command.noutrefresh()

  def load_data(self):
    '''...'''
    global UPDATES
    global REPAIR
    self.load_installed()
    if UPDATES:
      self.load_updates()
    elif REPAIR:
      self.load_repair()
    else:
      self.load_available()
    
    

  def load_installed(self):
    '''...'''
    global FILTER
    list_installed = list()
    #
    pass
    lst = self.yum_base.doPackageLists()
    if lst.installed:
      for pkg in sorted(lst.installed):
        lst = [pkg.name, pkg]
        grp = str(pkg.group)
        if FILTER in grp:           
          list_installed.append(lst)
    list_installed.sort(key=lambda s: s[0].lower())
    self.installed_data = list_installed
    self.installed_count = len(self.installed_data)

  def load_repair(self):
    '''...'''
    global FILTER
    list_repair = list()
    #
    pass
    lst = self.yum_base.doPackageLists()
    if lst.reinstall_available:
      for pkg in sorted(lst.reinstall_available):
        lst = [pkg.name, pkg]
        grp = str(pkg.group)
        if FILTER in grp:           
          list_repair.append(lst)
    list_repair.sort(key=lambda s: s[0].lower())
    self.available_data = list_repair
    self.available_count = len(self.available_data)

  def load_updates(self):
    '''...'''
    global FILTER
    list_updates = list()
    list_available = list()
    pass

    lst = self.yum_base.doPackageLists()
    
    if lst.available:
      for pkg in sorted(lst.available):
        lst = [pkg.name, pkg]
        grp = str(pkg.group)
        if FILTER in grp:
          list_available.append(lst)
    list_updates.sort(key=lambda s: s[0].lower())
####################################
    for i in range(len(list_available)):
      for j in range(len(self.installed_data)):
        data2 = list_available[i][1]
        name2 = str(data2.name)
        data1 = self.installed_data[j][1]
        name1 = str(data1.name) 
        
        if name1 == name2:
          list_updates.append(list_available[i])  
#######################################
    self.available_data = sorted(list_updates)###
    self.available_count = len(self.available_data)

  def load_available(self):
    '''...'''
    global FILTER
    list_available = list()
    pass

    lst = self.yum_base.doPackageLists()
    if lst.available:
      for pkg in sorted(lst.available):
        lst = [pkg.name, pkg]
        grp = str(pkg.group)
        if FILTER in grp:
          list_available.append(lst)
    list_available.sort(key=lambda s: s[0].lower())
    self.available_data = list_available
    self.available_count = len(self.available_data)

#  def __exit__(self, type, value, traceback):
#    curses.curs_set(1)
#    curses.nocbreak()
#    self.stdscr.keypad(0)
#    curses.echo()
#    curses.endwin()


def main(screen):
  #
  MainApp(screen)

if __name__ == '__main__':
  try:
    curses.wrapper(main)
  except KeyboardInterrupt:
    print "Got KeyboardInterrupt exception. Exiting..."
    exit()
