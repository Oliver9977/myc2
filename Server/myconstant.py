"""
build in constants ...
"""


class myconstant():
    def __init__(self):

        self.SOCKET_TIMEOUT = 5
        self.PFW_ACK_SPEED = 2

        self.TAG_MYCS = "[MYCS]"
        self.TAG_LISTENER = "[Listener]"
        self.TAG_INTE_STAGER = "[Interact]"
        self.TAG_PIPE_LISTENER = "[Pipe Listener]"
        self.TAG_PIPE_INTE_STAGER = "[Pipe Interact]"
        self.TAG_PAYLOAD = "[Payload]"
        self.TAG_STAGER_TOOLS = "[Tools]"


        self.CMD_USELISTENER = "uselistener"
        self.CMD_INTERACTSTAGER = "stager"
        self.CMD_PIPE_INTERACTSTAGER = "pstager"
        self.CMD_USEPIPELISTENER = "usepipelistener"
        self.CMD_PAYLOAD = "payload"
        self.CND_LOCALSERVER = "localserver"
        self.CMD_HELP = "help"
        self.CMD_EXIT = "exit"
        self.CMD_AUTOLIST = [self.CMD_USEPIPELISTENER,self.CMD_USELISTENER,self.CMD_INTERACTSTAGER,self.CMD_HELP,self.CMD_EXIT,self.CMD_PIPE_INTERACTSTAGER,self.CMD_PAYLOAD,self.CND_LOCALSERVER]

        self.CMD_BACK = "back"
        self.CMD_LOCALSERVER_GETINTO = "info"
        self.CMD_LOCALSERVER_SETCONFIG = "set"
        self.CMD_LOCALSERVER_START = "start"
        self.CMD_LOCALSERVER_STOP = "stop"
        self.CMD_LOCALSERVER_LIST = "list"
        self.CMD_LOCALSERVER_AUTOLIST = [self.CMD_LOCALSERVER_GETINTO,self.CMD_LOCALSERVER_SETCONFIG,self.CMD_LOCALSERVER_START,self.CMD_LOCALSERVER_STOP,self.CMD_LOCALSERVER_LIST,self.CMD_BACK]

        
        self.CMD_LISTENER_GETINFO = "info"
        self.CMD_LISTENER_SETHOSTNAME = "sethost"
        self.CMD_LISTENER_SETPORT = "setport"
        self.CMD_LISTENER_START = "start"
        self.CMD_LISTENER_LIST = "list"
        self.CMD_LISTENER_STOP = "stop"
        self.CMD_LISTENER_AUTOLIST = [self.CMD_BACK,self.CMD_LISTENER_GETINFO,self.CMD_LISTENER_SETHOSTNAME,
                                    self.CMD_LISTENER_SETPORT,self.CMD_LISTENER_START,self.CMD_LISTENER_LIST,self.CMD_LISTENER_STOP,self.CMD_HELP]

        self.CMD_STAGER_GET_LIST = "list"
        self.CMD_STAGER_GET_RUNNING_LIST = "rlist"
        self.CMD_STAGER_GET_INTO = "into"
        self.CMD_STAGER_GET_HISTORY = "history"
        self.CMD_STAGER_LOAD_PS = "psload"
        self.CMD_STAGER_CON = "connect"
        self.CMD_STAGER_PFW = "pfw"
        self.CMD_STAGER_BUILDIN = "tools"
        #self.CMD_STAGER_GET_UNSEEN_HISTORY = "uhistory"
        self.CMD_STAGER_AUTOLIST = [self.CMD_BACK,self.CMD_STAGER_GET_LIST,self.CMD_STAGER_GET_RUNNING_LIST,self.CMD_STAGER_GET_INTO,
                                        self.CMD_STAGER_GET_HISTORY,self.CMD_HELP,self.CMD_STAGER_LOAD_PS,self.CMD_STAGER_CON,self.CMD_STAGER_PFW,self.CMD_STAGER_BUILDIN]

        self.CMD_STAGER_TOOLS_PSEXEC = "psexec"
        self.CMD_STAGER_TOOLS_IF64BIT = "if64"
        self.CMD_STAGER_TOOLS_GETNETVERSION = "getnet"
        self.CMD_STAGER_TOOLS_GETAV = "getav"
        self.CMD_STAGER_TOOLS_GETAL = "getal"
        self.CMD_STAGER_TOOLS_GETCLM = "getclm"
        self.CMD_STAGER_TOOLS_MAKETOKEN = "maketoken"
        self.CMD_STAGER_TOOLS_PSRESET = "psreset"
        self.CMD_STAGER_TOOLS_INJECT = "inject"
        
        self.CMD_STAGER_TOOLS_AUTOLIST = [self.CMD_BACK,self.CMD_STAGER_TOOLS_PSEXEC,self.CMD_STAGER_TOOLS_IF64BIT,
                                            self.CMD_STAGER_TOOLS_GETNETVERSION,self.CMD_STAGER_TOOLS_GETAV,self.CMD_STAGER_TOOLS_GETAL,
                                            self.CMD_STAGER_TOOLS_GETCLM,self.CMD_STAGER_TOOLS_MAKETOKEN,self.CMD_STAGER_TOOLS_PSRESET,self.CMD_STAGER_TOOLS_INJECT]

        self.CMD_PIPE_LISTENER_GETINFO = "info"
        self.CMD_PIPE_LISTENER_SETPIPENAME = "setpipename"
        self.CMD_PIPE_LISTENER_START = "start"
        self.CMD_PIPE_LISTENER_LIST = "list"
        self.CMD_PIPE_LISTENER_STOP = "stop"
        self.CMD_PIPE_LISTENER_AUTOLIST = [self.CMD_PIPE_LISTENER_GETINFO,self.CMD_PIPE_LISTENER_SETPIPENAME,self.CMD_PIPE_LISTENER_START,
                                            self.CMD_PIPE_LISTENER_LIST,self.CMD_PIPE_LISTENER_STOP,self.CMD_BACK]
        
        self.CMD_PIPE_STAGER_GET_LIST = "list"
        self.CMD_PIPE_STAGER_GET_RUNNING_LIST = "rlist"
        self.CMD_PIPE_STAGER_GET_INTO = "into"
        self.CMD_PIPE_STAGER_GET_HISTORY = "history"
        self.CMD_PIPE_STAGER_CON = "connect"
        self.CMD_PIPE_SAGER_AUTOLIST = [self.CMD_PIPE_STAGER_GET_LIST,self.CMD_PIPE_STAGER_GET_INTO,self.CMD_PIPE_STAGER_GET_HISTORY,
                                            self.CMD_BACK,self.CMD_PIPE_STAGER_GET_RUNNING_LIST,self.CMD_PIPE_STAGER_CON]
        #self.CMD_PIPE_STAGER_LOAD_PS = "psload"
        #self.CMD_PIPE_STAGER_CON = "connect" 

        self.CMD_PAYLOAD_SETCONFIG = "set"
        self.CMD_PAYLOAD_GEN = "start"
        self.CMD_PAYLOAD_INFO = "info"
        self.CMD_PAYLOAD_AUTOLIST = [self.CMD_PAYLOAD_SETCONFIG,self.CMD_PAYLOAD_GEN,self.CMD_PAYLOAD_INFO,self.CMD_BACK]




class myconstant_networking(): #applicaiton layer tag
    def __init__(self):
        self.PSRUN_SUCCESS = "PSRUN_SUCCESS"
        self.PSRESET = "PSRESET_SUCCESS"
        self.PIPE_CONNECTED = "PIPE_CONNECTED"
        self.FW_NOTREADY = "FW_NOTREADY"
        self.FW_SUCCESS = "FW_SUCCESS" #for remote startup
        self.FW_LOCAL_SUCCESS = "FW_LOCAL_SUCCESS" #for local startup
        self.FW_LOCAL_ERROR = "FW_LOCAL_ERROR" #for local startup


class mybuildin_cmd():
    def __init__(self):
        self.IF64BIT = "[Environment]::Is64BitProcess"
        self.GETNETVERSION = "get-childitem -path \"HKLM:\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP\""
        self.GETDEFENDER = "Get-MpComputerStatus"
        self.GETAPPLOCKER = "Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections"
        self.GETLANGMODE = "$ExecutionContext.SessionState.LanguageMode"

        #overpassthehash
        self.OPH_INIT = "$token = [SharPsplOit.Credentials.Tokens]::new()"
        self.OPH_NEWTOKEN = "$token.MakeToken(\"{}\",\"{}\",\"{}\")"

