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
  def window_name=(new_window_name)
    @window_name = new_window_name
  end
private
  def call_ldtp(fnname, arg, *varargs)
    if @window_name == ""
      raise LdtpExecutionError.new("window_name is empty")
    end
    if varargs.length > 0
      # If "" args are passed, then join trims
      ok, param = @server.call2(fnname, @window_name, arg, varargs.join(', '))
    else
      # Due to above issue, having two calls
      # FIXME: Find better alternative
      ok, param = @server.call2(fnname, @window_name, arg)
    end
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def call_ldtp_noargs(fnname)
    ok, param = @server.call2(fnname)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def call_ldtp_arg(fnname, arg)
    ok, param = @server.call2(fnname, arg)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def call_ldtp_int(fnname, arg, time)
    # Takes integer argument at end
    # The above join converts it to string on join
    if @window_name == ""
      raise LdtpExecutionError.new("window_name is empty")
    end
    ok, param = @server.call2(fnname, @window_name, arg, time)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def start_ldtp
    io = IO.popen("python -c 'import ldtpd; ldtpd.main()'")
    @@child_pid = io.pid
    sleep 5
  end
public
  @@child_pid = 0
  if ENV['LDTP_SERVER_ADDR']
    @@ldtp_server_addr = ENV['LDTP_SERVER_ADDR']
  else
    @@ldtp_server_addr = 'localhost'
  end
  if ENV['LDTP_SERVER_PORT']
    @@ldtp_server_port = Integer(ENV['LDTP_SERVER_PORT'])
  else
    @@ldtp_server_port = 4118
  end
  @@is_windows = (RbConfig::CONFIG['host_os'] =~ /mswin|mingw|cygwin/)
  if ENV['LDTP_WINDOWS']
    @@ldtp_windows_env = true
  elsif ENV['LDTP_LINUX']
    @@ldtp_windows = false
  elsif @@is_windows
    @@ldtp_windows_env = true
  end
  def initialize(window_name = "")
    @poll_events = {}
    @window_name = window_name
    @server = XMLRPC::Client.new(@@ldtp_server_addr, "/RPC2", @@ldtp_server_port)
    begin
      call_ldtp_noargs("isalive")
    rescue => detail
      start_ldtp
    end
  end
  def Ldtp.childpid
    @@child_pid
  end
  # Launch
  def launchapp(cmd, args = [], delay = 0, env = 1, lang = "C")
    ok, param = @server.call2("launchapp", cmd, args, delay, env, lang)
    if ok then
      return param
    else
      # puts param.faultCode
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def delaycmdexec(delay)
    return call_ldtp("delaycmdexec", delay)
  end
  # Wait / State
  def getallstates(obj_name)
    return call_ldtp("getallstates", obj_name)
  end
  def stateenabled(obj_name)
    return call_ldtp("stateenabled", obj_name)
  end
  def hasstate(obj_name, state, guiTimeOut = 0)
    if @window_name == ""
      raise LdtpExecutionError.new("window_name is empty")
    end
    ok, param = @server.call2("hasstate", @window_name, obj_name, state, guiTimeOut)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def wait(timeout = 5)
    ok, param = @server.call2("wait", timeout)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def guiexist params = {}
    opts = {
      :obj_name => "",
    }.merge params
    status = call_ldtp("guiexist", opts[:obj_name])
    return status
  end
  def waittillguiexist params = {}
    opts = {
      :obj_name => "",
      :guiTimeOut => 30
    }.merge params
    # Increase the timeout as the default ruby xmlrpc
    # timeout is 30 seconds
    @server.timeout = opts[:guiTimeOut] + 10
    begin
      status = call_ldtp_int("waittillguiexist", opts[:obj_name], opts[:guiTimeOut])
    ensure
      # Set back to default timeout
      @server.timeout = 30
    end
    return status
  end
  def waittillguinotexist params = {}
    opts = {
      :obj_name => "",
      :guiTimeOut => 30
    }.merge params
    # Increase the timeout as the default ruby xmlrpc
    # timeout is 30 seconds
    @server.timeout = opts[:guiTimeOut] + 10
    begin
      status = call_ldtp_int("waittillguinotexist", opts[:obj_name], opts[:guiTimeOut])
    ensure
      # Set back to default timeout
      @server.timeout = 30
    end
    return status
  end
  # Image
  def imagecapture params = {}
    opts = {
      :window_name => "",
      :x => 0,
      :y => 0,
      :width => 0,
      :height => 0
    }.merge params
    ok, param = @server.call2("imagecapture", opts[:window_name],
                              opts[:x], opts[:y], opts[:width], opts[:height])
    if ok then
      file = Tempfile.new(['ldtp_', '.png'])
      filename = file.path
      file.close(true)
      File.open(filename, 'wb') {|f| f.write(Base64.decode64(param))}
      return filename
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  # Keyboard / Mouse
  def generatekeyevent(data)
    return call_ldtp_arg("generatekeyevent", data)
  end
  def enterstring(window_name = "", obj_name = "", data = "")
    if obj_name == "" and data =="":
        return call_ldtp_arg("enterstring", window_name)
    end
    if window_name == ""
      window_name = @window_name
    end
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    ok, param = @server.call2("enterstring", window_name, obj_name, data)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def keypress(data)
    return call_ldtp_arg("keypress", data)
  end
  def keyrelease(data)
    return call_ldtp_arg("keyrelease", data)
  end
  def generatemouseevent(x, y, eventType = 'b1p')
    ok, param = @server.call2("generatemouseevent", x, y, eventType)
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
  def mouseleftclick(obj_name)
    return call_ldtp("mouseleftclick", obj_name)
  end
  def mousemove(obj_name)
    return call_ldtp("mousemove", obj_name)
  end
  def mouserightclick(obj_name)
    return call_ldtp("mouserightclick", obj_name)
  end
  def doubleclick(obj_name)
    return call_ldtp("doubleclick", obj_name)
  end
  # Menu
  def selectmenuitem(obj_name)
    return call_ldtp("selectmenuitem", obj_name)
  end
  def doesmenuitemexist(obj_name)
    return call_ldtp("doesmenuitemexist", obj_name)
  end
  def menuitemenabled(obj_name)
    return call_ldtp("menuitemenabled", obj_name)
  end
  def listsubmenus(obj_name)
    return call_ldtp("listsubmenus", obj_name)
  end
  def menucheck(obj_name)
    return call_ldtp("menucheck", obj_name)
  end
  def menuuncheck(obj_name)
    return call_ldtp("menuuncheck", obj_name)
  end
  def verifymenucheck(obj_name)
    return call_ldtp("verifymenucheck", obj_name)
  end
  def verifymenuuncheck(obj_name)
    return call_ldtp("verifymenuuncheck", obj_name)
  end
  def invokemenu(obj_name)
    return call_ldtp("invokemenu", obj_name)
  end
  # Check box / Radio button / Toogle
  def check(obj_name)
    return call_ldtp("check", obj_name)
  end
  def uncheck(obj_name)
    return call_ldtp("uncheck", obj_name)
  end
  def verifytoggled(obj_name)
    return call_ldtp("verifytoggled", obj_name)
  end
  def verifypushbutton(obj_name)
    return call_ldtp("verifypushbutton", obj_name)
  end
  def verifycheck(obj_name)
    return call_ldtp("verifycheck", obj_name)
  end
  def verifyuncheck(obj_name)
    return call_ldtp("verifyuncheck", obj_name)
  end
  # Panel
  def getpanelchildcount(obj_name)
    return call_ldtp("getpanelchildcount", obj_name)
  end
  # General
  def click(obj_name)
    return call_ldtp("click", obj_name)
  end
  def getapplist
    return call_ldtp_noargs("getapplist")
  end
  def getwindowlist
    return call_ldtp_noargs("getwindowlist")
  end
  def press(obj_name)
    return call_ldtp("press", obj_name)
  end
  def objectexist(obj_name)
    return call_ldtp("objectexist", obj_name)
  end
  def grabfocus(obj_name)
    return call_ldtp("grabfocus", obj_name)
  end
  def getobjectsize(obj_name)
    return call_ldtp("getobjectsize", obj_name)
  end
  # Table
  def handletablecell
    return call_ldtp_noargs("handletablecell")
  end
  def unhandletablecell
    return call_ldtp_noargs("unhandletablecell")
  end
  # Log
  def getlastlog()
    return call_ldtp_noargs("getlastlog")
  end
  # Process monitor
  def startprocessmonitor(process_name, interval = 2)
    ok, param = @server.call2("startprocessmonitor", process_name, interval)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def stopprocessmonitor(process_name)
    return call_ldtp_arg("stopprocessmonitor", process_name)
  end
  def getcpustat(process_name)
    return call_ldtp_arg("getcpustat", process_name)
  end
  def getmemorystat(process_name)
    return call_ldtp_arg("getmemorystat", process_name)
  end
  # Window management
  def windowuptime(window_name = "")
    if window_name == ""
      window_name = @window_name
    end
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    return call_ldtp_arg("windowuptime", window_name)
  end
  def getobjectlist(window_name = "")
    if window_name == ""
      window_name = @window_name
    end
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    return call_ldtp_arg("getobjectlist", window_name)
  end
  def getobjectinfo(obj_name)
    return call_ldtp("getobjectinfo", obj_name)
  end
  def getobjectproperty(obj_name, property)
    return call_ldtp("getobjectproperty", obj_name, property)
  end
  def getchild(window_name = "", child_name = '', role = '', parent = '')
    if window_name == ""
      window_name = @window_name
    end
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    ok, param = @server.call2("getchild", @window_name, child_name, role, parent)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def remap(window_name = "")
    if window_name == ""
      window_name = @window_name
    end
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    return call_ldtp_arg("remap", window_name)
  end
  def getwindowsize(window_name = "")
    if window_name == ""
      window_name = @window_name
    end
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    return call_ldtp_arg("getwindowsize", window_name)
  end
  def getobjectnameatcoords(wait_time = 0)
    return call_ldtp_arg("getobjectnameatcoords", wait_time)
  end
  def onwindowcreate(window_name, fnname, *args)
    @poll_events[window_name] = [fnname, args]
    return call_ldtp_arg("onwindowcreate", window_name)
  end
  def removecallback(window_name)
    if @poll_events.has_key?(window_name)
      @poll_events.delete(window_name)
    end
    return call_ldtp_arg("removecallback", window_name)
  end
  def registerevent(window_name, fnname, *args)
    @poll_events[window_name] = [fnname, args]
    return call_ldtp_arg("registerevent", window_name)
  end
  def deregisterevent(window_name)
    if @poll_events.has_key?(window_name)
      @poll_events.delete(window_name)
    end
    return call_ldtp_arg("deregisterevent", window_name)
  end
  def registerkbevent(window_name, fnname, *args)
    @poll_events[window_name] = [fnname, args]
    return call_ldtp_arg("registerkbevent", window_name)
  end
  def deregisterkbevent(window_name)
    if @poll_events.has_key?(window_name)
      @poll_events.delete(window_name)
    end
    return call_ldtp_arg("deregisterkbevent", window_name)
  end
  def maximizewindow(window_name = "")
    return call_ldtp_arg("maximizewindow", window_name)
  end
  def minimizewindow(window_name = "")
    return call_ldtp_arg("minimizewindow", window_name)
  end
  def unmaximizewindow(window_name = "")
    return call_ldtp_arg("unmaximizewindow", window_name)
  end
  def unminimizewindow(window_name = "")
    return call_ldtp_arg("unminimizewindow", window_name)
  end
  def activatewindow(window_name = "")
    return call_ldtp_arg("activatewindow", window_name)
  end
  def closewindow(window_name = "")
    return call_ldtp_arg("closewindow", window_name)
  end
  # Status bar
  def getstatusbartext(obj_name)
    return call_ldtp("getstatusbartext", obj_name)
  end
  # Text
  def settextvalue(obj_name, data)
    return call_ldtp("settextvalue", obj_name, data)
  end
  def gettextvalue(obj_name)
    return call_ldtp("gettextvalue", obj_name)
  end
  def verifypartialmatch(obj_name, partial_text)
    return call_ldtp("verifypartialmatch", obj_name, partial_text)
  end
  def verifysettext(obj_name, text)
    return call_ldtp("verifysettext", obj_name, text)
  end
  def activatetext(obj_name)
    return call_ldtp("activatetext", obj_name)
  end
  def appendtext(obj_name, text)
    return call_ldtp("appendtext", obj_name, text)
  end
  def istextstateenabled(obj_name)
    return call_ldtp("istextstateenabled", obj_name)
  end
  def getcharcount(obj_name)
    return call_ldtp("getcharcount", obj_name)
  end
  def getcursorposition(obj_name)
    return call_ldtp("getcursorposition", obj_name)
  end
  def setcursorposition(obj_name, cursor_position)
    return call_ldtp_int("setcursorposition", obj_name, cursor_position)
  end
  def cuttext(obj_name, start_position, end_position = -1)
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    ok, param = @server.call2("cuttext", @window_name, obj_name, start_position, end_position)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def copytext(obj_name, start_position, end_position = -1)
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    ok, param = @server.call2("copytext", @window_name, obj_name, start_position, end_position)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def deletetext(obj_name, start_position, end_position = -1)
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    ok, param = @server.call2("deletetext", @window_name, obj_name, start_position, end_position)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def pastetext(obj_name, position = 0)
    return call_ldtp_int("pastetext", obj_name, position)
  end
  # Combo box
  def unselectitem(obj_name, item_name)
    return call_ldtp("unselectitem", obj_name, item_name)
  end
  def unselectindex(obj_name, item_index)
    return call_ldtp_int("unselectindex", obj_name, item_index)
  end
  def ischildselected(obj_name, item_name)
    return call_ldtp("ischildselected", obj_name, item_name)
  end
  def ischildindexselected(obj_name, item_index)
    return call_ldtp_int("ischildindexselected", obj_name, item_index)
  end
  def selecteditemcount(obj_name)
    return call_ldtp("selecteditemcount", obj_name)
  end
  def selectall(obj_name)
    return call_ldtp("selectall", obj_name)
  end
  def unselectall(obj_name)
    return call_ldtp("unselectall", obj_name)
  end
  def selectitem(obj_name, item_name)
    return call_ldtp("selectitem", obj_name, item_name)
  end
  def selectindex(obj_name, item_index)
    return call_ldtp_int("selectindex", obj_name, item_index)
  end
  def getallitem(obj_name)
    return call_ldtp("getallitem", obj_name)
  end
  def showlist(obj_name)
    return call_ldtp("showlist", obj_name)
  end
  def hidelist(obj_name)
    return call_ldtp("hidelist", obj_name)
  end
  def verifydropdown(obj_name)
    return call_ldtp("verifydropdown", obj_name)
  end
  def verifyshowlist(obj_name)
    return call_ldtp("verifyshowlist", obj_name)
  end
  def verifyhidelist(obj_name)
    return call_ldtp("verifyhidelist", obj_name)
  end
  def verifyselect(obj_name, item_name)
    return call_ldtp("verifyselect", obj_name, item_name)
  end
  # Table
  def getrowcount(obj_name)
    return call_ldtp("getrowcount", obj_name)
  end
  def selectrow(obj_name, row_text)
    return call_ldtp("selectrow", obj_name, row_text)
  end
  def selectrowpartialmatch(obj_name, row_text)
    return call_ldtp("selectrowpartialmatch", obj_name, row_text)
  end
  def selectrowindex(obj_name, row_index)
    return call_ldtp_int("selectrowindex", obj_name, row_index)
  end
  def selectlastrow(obj_name)
    return call_ldtp("selectlastrow", obj_name)
  end
  def setcellvalue(obj_name, row_index, column = 0, data = "")
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    ok, param = @server.call2("setcellvalue", @window_name, obj_name, row_index, column, data)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def getcellvalue(obj_name, row_index, column = 0)
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    ok, param = @server.call2("getcellvalue", @window_name, obj_name, row_index, column)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def rightclick(obj_name, row_text)
    return call_ldtp("rightclick", obj_name, row_text)
  end
  def singleclickrow(obj_name, row_text)
    return call_ldtp("singleclickrow", obj_name, row_text)
  end
  def doubleclickrow(obj_name, row_text)
    return call_ldtp("doubleclickrow", obj_name, row_text)
  end
  def gettablerowindex(obj_name, row_text)
    return call_ldtp("gettablerowindex", obj_name, row_text)
  end
  def checkrow(obj_name, row_index, column = 0)
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    ok, param = @server.call2("checkrow", @window_name, obj_name, row_index, column)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def uncheckrow(obj_name, row_index, column = 0)
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    ok, param = @server.call2("uncheckrow", @window_name, obj_name, row_index, column)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def expandtablecell(obj_name, row_index, column = 0)
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    ok, param = @server.call2("expandtablecell", @window_name, obj_name, row_index, column)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def verifytablecell(obj_name, row_index, column, row_text = "")
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    ok, param = @server.call2("verifytablecell", @window_name, obj_name, row_index, column, row_text)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def verifypartialtablecell(obj_name, row_index, column, row_text)
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    ok, param = @server.call2("verifypartialtablecell", @window_name, obj_name, row_index, column, row_text)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  def doesrowexist(obj_name, row_text, partial_match = false)
    if @window_name == ""
      raise LdtpExecutionError.new("@window_name is empty")
    end
    ok, param = @server.call2("doesrowexist", @window_name, obj_name, row_text, partial_match)
    if ok then
      return param
    else
      raise LdtpExecutionError.new(param.faultString)
    end
  end
  # Page tab
  def selecttab(obj_name, tab_name)
    return call_ldtp("selecttab", obj_name, tab_name)
  end
  def selecttabindex(obj_name, tab_index)
    return call_ldtp_int("selecttabindex", obj_name, tab_index)
  end
  def verifytabname(obj_name, tab_name)
    return call_ldtp("verifytabname", obj_name, tab_name)
  end
  def gettabcount(obj_name)
    return call_ldtp("gettabcount", obj_name)
  end
  def gettabname(obj_name, tab_index)
    return call_ldtp_int("gettabname", obj_name, tab_index)
  end
  # Value
  def setvalue(obj_name, data)
    return call_ldtp("setvalue", obj_name, data)
  end
  def getvalue(obj_name)
    return call_ldtp("getvalue", obj_name)
  end
  def getslidervalue(obj_name)
    return call_ldtp("getslidervalue", obj_name)
  end
  def verifysetvalue(obj_name, data)
    return call_ldtp("verifysetvalue", obj_name, data)
  end
  def getminvalue(obj_name)
    return call_ldtp("getminvalue", obj_name)
  end
  def getmaxvalue(obj_name)
    return call_ldtp("getmaxvalue", obj_name)
  end
  def getminincrement(obj_name)
    return call_ldtp("getminincrement", obj_name)
  end
  def getmin(obj_name)
    return call_ldtp("getmin", obj_name)
  end
  def getmax(obj_name)
    return call_ldtp("getmax", obj_name)
  end
  def verifyslidervertical(obj_name)
    return call_ldtp("verifyslidervertical", obj_name)
  end
  def verifysliderhorizontal(obj_name)
    return call_ldtp("verifysliderhorizontal", obj_name)
  end
  def verifyscrollbarvertical(obj_name)
    return call_ldtp("verifyscrollbarvertical", obj_name)
  end
  def verifyscrollbarhorizontal(obj_name)
    return call_ldtp("verifyscrollbarhorizontal", obj_name)
  end
  def scrollup(obj_name)
    return call_ldtp("scrollup", obj_name)
  end
  def scrolldown(obj_name)
    return call_ldtp("scrolldown", obj_name)
  end
  def scrollleft(obj_name)
    return call_ldtp("scrollleft", obj_name)
  end
  def scrollright(obj_name)
    return call_ldtp("scrollright", obj_name)
  end
  def setmin(obj_name)
    return call_ldtp("setmin", obj_name)
  end
  def setmax(obj_name)
    return call_ldtp("setmax", obj_name)
  end
  def increase(obj_name, iterations)
    return call_ldtp_int("increase", obj_name, iterations)
  end
  def decrease(obj_name, iterations)
    return call_ldtp_int("decrease", obj_name, iterations)
  end
  def onedown(obj_name, iterations)
    return call_ldtp_int("onedown", obj_name, iterations)
  end
  def oneup(obj_name, iterations)
    return call_ldtp_int("oneup", obj_name, iterations)
  end
  def oneright(obj_name, iterations)
    return call_ldtp_int("oneright", obj_name, iterations)
  end
  def oneleft(obj_name, iterations)
    return call_ldtp_int("oneleft", obj_name, iterations)
  end
end
at_exit do
  childpid = Ldtp.childpid
  if childpid != 0
    # LDTP launched in subprocess, kill that first
    Process.kill('KILL', childpid)
    # Kill LDTP process
    # FIXME: Is this correct way to do ?
    Process.kill('KILL', childpid + 1)
  end
end
