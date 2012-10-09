
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

  def initialize message
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
public
  def Ldtp.childpid
    @@child_pid
  end
  def Ldtp.windowsenv
    @@ldtp_windows_env
  end
  def wait(timeout=5)
    ok, param = @client.call2("wait", timeout)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def waittillguiexist(object_name = "", guiTimeOut = 30, state = "")
    ok, param = @client.call2("waittillguiexist", @window_name, object_name,
                              guiTimeOut, state)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def waittillguinotexist(object_name = "", guiTimeOut = 30, state = "")
    ok, param = @client.call2("waittillguinotexist", @window_name, object_name,
                              guiTimeOut, state)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def guiexist(object_name = "")
    ok, param = @client.call2("guiexist", @window_name, object_name)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def generatemouseevent(x, y, eventType = "b1c")
    ok, param = @client.call2("generatemouseevent", x, y, eventType)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def getapplist()
    ok, param = @client.call2("getapplist")
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def getwindowlist()
    ok, param = @client.call2("getwindowlist")
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def registerevent(event_name, fnname, *args)
    @poll_events[event_name] = [fnname, args]
    ok, param = @client.call2("registerevent", event_name)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def deregisterevent(event_name)
    if @poll_events.has_key?(event_name)
      @poll_events.delete(event_name)
    end
    ok, param = @client.call2("deregisterevent", event_name)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def registerkbevent(keys, modifiers, fnname, *args)
    event_name = "kbevent%s%s" % [keys, modifiers]
    @poll_events[event_name] = [fnname, args]
    ok, param = @client.call2("registerkbevent", event_name)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def deregisterkbevent(keys, modifiers)
    event_name = "kbevent%s%s" % [keys, modifiers]
    if @poll_events.has_key?(event_name)
      @poll_events.delete(event_name)
    end
    ok, param = @client.call2("deregisterkbevent", event_name)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def launchapp(cmd, args = [], delay = 0, env = 1, lang = "C")
    ok, param = @client.call2("launchapp", cmd, args, delay, env, lang)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def hasstate(object_name, state, guiTimeOut = 0)
    ok, param = @client.call2("hasstate", @window_name, object_name,
                              state, guiTimeOut)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def selectrow(object_name, row_text)
    ok, param = @client.call2("selectrow", @window_name, object_name,
                              row_text, false)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def getchild(child_name = "", role = "", parent = "")
    ok, param = @client.call2("getchild", @window_name, object_name,
                              role, parent)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def getcpustat(process_name)
    ok, param = @client.call2("getcpustat", process_name)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def getmemorystat(process_name)
    ok, param = @client.call2("getmemorystat", process_name)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def getlastlog()
    ok, param = @client.call2("getlastlog")
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def getobjectnameatcoords(wait_time = 0)
    ok, param = @client.call2("getobjectnameatcoords", wait_time)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def enterstring(param1, param2 = "")
    if param2 == "" then
        ok, param = @client.call2("enterstring", param1, "", "")
    else
        ok, param = @client.call2("enterstring", @window_name, param1, param2)
    end
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def setvalue(object_name, data)
    ok, param = @client.call2("setvalue", @window_name, object_name, data)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def grabfocus(object_name = "")
      # On Linux just with window name, grab focus doesn't work
      # So, we can't make this call generic
    ok, param = @client.call2("grabfocus", @window_name, object_name)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def copytext(object_name, start, end_index = -1)
    ok, param = @client.call2("copytext", @window_name, object_name,
                              start, end_index)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def cuttext(object_name, start, end_index = -1)
    ok, param = @client.call2("cuttext", @window_name, object_name,
                              start, end_index)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def deletetext(object_name, start, end_index = -1)
    ok, param = @client.call2("deletetext", @window_name, object_name,
                              start, end_index)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def startprocessmonitor(process_name, interval = 2)
    ok, param = @client.call2("startprocessmonitor", process_name, interval)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def stopprocessmonitor(process_name)
    ok, param = @client.call2("stopprocessmonitor", process_name)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def keypress(data)
    ok, param = @client.call2("keypress", data)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def keyrelease(data)
    ok, param = @client.call2("keyrelease", data)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def gettextvalue(object_name, startPosition = 0, endPosition = 0)
    ok, param = @client.call2("gettextvalue", @window_name, object_name,
                              startPosition, endPosition)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def closewindow(window_name = "")
    if window_name == nil || window_name == "" then
       window_name = @window_name
    end
    ok, param = @client.call2("closewindow", window_name)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def maximizewindow(window_name = "")
    if window_name == nil || window_name == "" then
       window_name = @window_name
    end
    ok, param = @client.call2("maximizewindow", window_name)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def minimizewindow(window_name = "")
    if window_name == nil || window_name == "" then
       window_name = @window_name
    end
    ok, param = @client.call2("minimizewindow", window_name)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def simulatemousemove(source_x, source_y, dest_x, dest_y, delay = 0.0)
    ok, param = @server.call2("simulatemousemove", source_x, source_y, dest_x, dest_y, delay)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def delaycmdexec(delay)
    ok, param = @client.call2("delaycmdexec", delay)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
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
    if ok then
      if opts[:out_file] != "" then
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
    if ok then
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
