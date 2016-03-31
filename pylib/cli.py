# vim:fileencoding=utf-8
# This file is in the Public Domain

'''
Convenient functions for command-line use.

Python 2 & 3
'''

import os
import re
import sys

def repl(local, histfile=None, banner=None):
  import readline
  import rlcompleter
  if 'libedit' in readline.__doc__:
    readline.parse_and_bind('bind ^I rl_complete')
  else:
    readline.parse_and_bind('tab: complete')
  if histfile is not None and os.path.exists(histfile):
    # avoid duplicate reading
    if readline.get_current_history_length() <= 0:
      readline.set_history_length(10000)
      readline.read_history_file(histfile)
  import code
  readline.set_completer(rlcompleter.Completer(local).complete)
  code.interact(local=local, banner=banner)
  if histfile is not None:
    readline.write_history_file(histfile)

def repl_reset_stdin(*args, **kwargs):
  fd = os.open('/dev/tty', os.O_RDONLY)
  os.dup2(fd, 0)
  os.close(fd)
  repl(*args, **kwargs)

if sys.version_info[0] == 2:
  def _translate(m):
    s = m.group(0)
    type, code = s[1], int(s[2:], 16)
    if type == 'x':
      return chr(code)
    else:
      return unichr(code).encode('utf-8')
else:
  def _translate(m):
    s = m.group(0)
    type, code = s[1], int(s[2:], 16)
    return chr(code)

def unescape_py2(s):
  '''unescape string displays for Python 2, works in Python 2'''
  return re.sub(r'\\x[0-9A-Fa-f]{2}|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8}',
                _translate, s)

def repl_py27(local, *args, **kwargs):
  '''Fix unicode display in Python 2.x; Console encoding must be UTF-8'''
  import re, sys

  def displayfunc(value):
    if value is None:
      local['_'] = None
      return

    r = repr(value)
    r = unescape_py2(r)
    print(r)
    local['_'] = value

  old_displayhook = sys.displayhook
  sys.displayhook = displayfunc
  try:
    repl(local, *args, **kwargs)
  finally:
    sys.displayhook = old_displayhook

def install_exc_hook(func=repl):
  old_hook = sys.excepthook

  def handle_exception(type, value, tb):
    import traceback
    traceback.print_exception(type, value, tb)
    frame = tb.tb_next.tb_frame
    sys.excepthook = old_hook
    func(frame.f_locals, banner='>>> Welcome to the debugging console <<<')
    sys.excepthook = handle_exception

  sys.excepthook = handle_exception

if __name__ == '__main__':
  if sys.version_info[0] == 3:
    repl_func = repl
  else:
    repl_func = repl_py27
  repl_func(vars(), os.path.expanduser('~/.pyhistory'))
