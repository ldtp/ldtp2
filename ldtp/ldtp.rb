
"""
LDTP v2 ruby client.

@author: Nagappan Alagappan <nagappan@gmail.com>
@copyright: Copyright (c) 2009-12 Nagappan Alagappan
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU Lesser General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See 'COPYING' in the source distribution for more information.

Headers in this file shall remain intact.
"""

require "base64"
require "rbconfig"
require "tempfile"
require "xmlrpc/client"

class LdtpExecutionError < RuntimeError
  attr_reader :message

  def initialize(message)
    @message = message
  end
end

class Ldtp
  @@child_pid = 0
  @@ldtp_windows_env = false

  def initialize(window_name, server_addr="localhost", server_port=4118)
    @poll_events = {}
    @@is_windows = (RbConfig::CONFIG['host_os'] =~ /mswin|mingw|cygwin/)
    if ENV['LDTP_WINDOWS']
      @@ldtp_windows_env = true
    elsif ENV['LDTP_LINUX']
      @@ldtp_windows = false
    elsif @@is_windows
      @@ldtp_windows_env = true
    end
    if ENV['LDTP_SERVER_ADDR']
      @@ldtp_server_addr = ENV['LDTP_SERVER_ADDR']
    end
    if ENV['LDTP_SERVER_PORT']
      @@ldtp_server_port = Integer(ENV['LDTP_SERVER_PORT'])
    end
    if window_name == nil || window_name == "" then
      raise LdtpExecutionError.new("Invalid argument passed to window_name")
    end
    @window_name = window_name
    @client = XMLRPC::Client.new( server_addr, "/RPC2", server_port )
    begin
      ok, param = @client.call2("isalive")
    rescue => detail
      start_ldtp
      begin
        ok, param = @client.call2("isalive")
      rescue => detail
        raise LdtpExecutionError.new("Unable to connect to server %s" % [server_addr])
      end
    end
  end

  private

  def start_ldtp
    if @@ldtp_windows_env
      io = IO.popen("CobraWinLDTP.exe")
    else
      io = IO.popen("ldtp")
    end
    @@child_pid = io.pid
    sleep 5
  end

  def try_call(*args)
    ok, param = @client.call2(*args)
    if ok
      param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end

  public

  def Ldtp.childpid
    @@child_pid
  end

  def Ldtp.windowsenv
    @@ldtp_windows_env
  end

  def wait(timeout=5)
    try_call("wait", timeout)
  end

  def waittillguiexist(object_name = "", guiTimeOut = 30, state = "")
    try_call("waittillguiexist", @window_name, object_name, guiTimeOut, state)
  end

  def waittillguinotexist(object_name = "", guiTimeOut = 30, state = "")
    try_call("waittillguinotexist", @window_name, object_name,
             guiTimeOut, state)
  end

  def guiexist(object_name = "")
    try_call("guiexist", @window_name, object_name)
  end

  def generatemouseevent(x, y, eventType = "b1c")
    try_call("generatemouseevent", x, y, eventType)
  end

  def getapplist()
    try_call("getapplist")
  end

  def getwindowlist()
    try_call("getwindowlist")
  end

  def registerevent(event_name, fnname, *args)
    @poll_events[event_name] = [fnname, args]
    try_call("registerevent", event_name)
  end

  def deregisterevent(event_name)
    if @poll_events.has_key?(event_name)
      @poll_events.delete(event_name)
    end
    try_call("deregisterevent", event_name)
  end

  def registerkbevent(keys, modifiers, fnname, *args)
    event_name = "kbevent%s%s" % [keys, modifiers]
    @poll_events[event_name] = [fnname, args]
    try_call("registerkbevent", event_name)
  end

  def deregisterkbevent(keys, modifiers)
    event_name = "kbevent%s%s" % [keys, modifiers]
    if @poll_events.has_key?(event_name)
      @poll_events.delete(event_name)
    end
    try_call("deregisterkbevent", event_name)
  end

  def launchapp(cmd, args = [], delay = 0, env = 1, lang = "C")
    try_call("launchapp", cmd, args, delay, env, lang)
  end

  def hasstate(object_name, state, guiTimeOut = 0)
    try_call("hasstate", @window_name, object_name, state, guiTimeOut)
  end

  def selectrow(object_name, row_text)
    try_call("selectrow", @window_name, object_name, row_text, false)
  end

  def getchild(child_name = "", role = "", parent = "")
    try_call("getchild", @window_name, object_name, role, parent)
  end

  def getcpustat(process_name)
    try_call("getcpustat", process_name)
  end

  def getmemorystat(process_name)
    try_call("getmemorystat", process_name)
  end

  def getlastlog()
    try_call("getlastlog")
  end

  def getobjectnameatcoords(wait_time = 0)
    try_call("getobjectnameatcoords", wait_time)
  end

  def enterstring(param1, param2 = "")
    if param2 == ""
      try_call("enterstring", param1, "", "")
    else
      try_call("enterstring", @window_name, param1, param2)
    end
  end

  def setvalue(object_name, data)
    try_call("setvalue", @window_name, object_name, data)
  end

  def grabfocus(object_name = "")
    # On Linux just with window name, grab focus doesn't work
    # So, we can't make this call generic
    try_call("grabfocus", @window_name, object_name)
  end

  def copytext(object_name, start, end_index = -1)
    try_call("copytext", @window_name, object_name, start, end_index)
  end

  def cuttext(object_name, start, end_index = -1)
    try_call("cuttext", @window_name, object_name, start, end_index)
  end

  def deletetext(object_name, start, end_index = -1)
    try_call("deletetext", @window_name, object_name, start, end_index)
  end

  def startprocessmonitor(process_name, interval = 2)
    try_call("startprocessmonitor", process_name, interval)
  end

  def stopprocessmonitor(process_name)
    try_call("stopprocessmonitor", process_name)
  end

  def keypress(data)
    try_call("keypress", data)
  end

  def keyrelease(data)
    try_call("keyrelease", data)
  end

  def gettextvalue(object_name, startPosition = 0, endPosition = 0)
    try_call("gettextvalue", @window_name, object_name,
             startPosition, endPosition)
  end

  def getcellvalue(object_name, row, column = 0)
    try_call("getcellvalue", @window_name, object_name, row, column)
  end

  def getcellsize(object_name, row, column = 0)
    try_call("getcellsize", @window_name, object_name, row, column)
  end

  def closewindow(window_name = "")
    if window_name == nil || window_name == "" then
       window_name = @window_name
    end

    try_call("closewindow", window_name)
  end

  def maximizewindow(window_name = "")
    if window_name == nil || window_name == "" then
       window_name = @window_name
    end

    try_call("maximizewindow", window_name)
  end

  def minimizewindow(window_name = "")
    if window_name == nil || window_name == "" then
      window_name = @window_name
    end

    try_call("minimizewindow", window_name)
  end

  def simulatemousemove(source_x, source_y, dest_x, dest_y, delay = 0.0)
    try_call("simulatemousemove", source_x, source_y, dest_x, dest_y, delay)
  end

  def delaycmdexec(delay)
    try_call("delaycmdexec", delay)
  end

  def imagecapture(params = {})
    opts = {
      :window_name => "",
      :out_file => "",
      :x => 0,
      :y => 0,
      :width => -1,
      :height => -1
    }.merge params
    ok, param = @client.call2("imagecapture", opts[:window_name],
                              opts[:x], opts[:y], opts[:width], opts[:height])
    if ok
      if opts[:out_file] != ""
        filename = opts[:out_file]
      else
        file = Tempfile.new(['ldtp_', '.png'])
        filename = file.path
        file.close(true)
      end
      File.open(filename, 'wb') {|f| f.write(Base64.decode64(param))}
      return filename
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end

  def onwindowcreate(fn_name, *args)
    @poll_events[window_name] = [fnname, args]
    # FIXME: Implement the method
  end

  def removecallback(fn_name)
    if @poll_events.has_key?(window_name)
      @poll_events.delete(window_name)
    end
    # FIXME: Implement the method
  end

  def method_missing(sym, *args, &block)
    ok, param = @client.call2 sym, @window_name, *args, &block
    if ok
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
end

at_exit do
  childpid = Ldtp.childpid
  if childpid != 0
    # Kill LDTP process
    begin
      if Ldtp.windowsenv
        io = IO.popen("taskkill /F /IM CobraWinLDTP.exe")
      else
        Process.kill('KILL', childpid)
      end
    rescue => detail
    end
  end
end
