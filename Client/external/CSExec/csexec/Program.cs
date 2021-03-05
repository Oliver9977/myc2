using Microsoft.Win32;
using System;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Threading;

namespace csexec
{
    public class Program
    {
        public static void Main(string[] args)
        {
            if (args.Length < 1)
            {
                PrintUsage();
                return;
            }
            var hostname = args[1];
            var execmode = args[0];

            var initialCommand = string.Empty;
            var stopAfterInitialCommand = false;

            if (args.Length > 2)
            {
                if (args[2] == "cmd")
                {
                    int initialCommandArgsSkip = 2;

                    if (args.Length > 3)
                    {
                        var cParameter = "/c";
                        if (args[3] == cParameter)
                        {
                            stopAfterInitialCommand = true;
                            ++initialCommandArgsSkip;
                        }
                    }

                    initialCommand = string.Join(" ",
                        args.Skip(initialCommandArgsSkip)
                            .Select(arg =>
                            {
                                if (arg.Contains(" "))
                                {
                                    if (arg.EndsWith(@"\"))
                                    {
                                        arg += @"\"; // add backslash to ensure existing backslash is not evaluated as escape char for trailing quote char
                                    }

                                    arg = $"\"{arg}\"";
                                }

                                return arg;
                            })
                            .ToArray());
                }
            }

#if DEBUG
            Console.WriteLine("[*] hostname: {0}", hostname);
#endif
            var version = GetDotNetVersion(hostname);
            if (execmode == "start")
            {
                CopyServiceExe(version, hostname);
                CopyPayloadExe(version, hostname);
                InstallService(hostname, version);
            }
            else if (execmode == "stop")
            {
                StopServiceExe(hostname);
                UninstallService(hostname);
                DeleteServiceExe(hostname);
                DeletePayloadExe(hostname);
            }
            else
            {
                Console.WriteLine("[*] Unknown Execute Mode ...");
            }


            //try
            //{
            //    CSExecClient.Connect(hostname, initialCommand, stopAfterInitialCommand);
            //}
            //catch (TimeoutException te)
            //{
            //    Console.WriteLine(te.Message);
            //}

        }

        private static void StopServiceExe(string hostname)
        {
            ServiceControlHandle con = NativeMethods.OpenSCManager(hostname, null, NativeMethods.SCM_ACCESS.SC_MANAGER_ALL_ACCESS);
            ServiceControlHandle m_serv = NativeMethods.OpenService(con, GlobalVars.ServiceName, NativeMethods.SERVICE_ACCESS.SERVICE_ALL_ACCESS);
            NativeMethods.SERVICE_STATUS stat = new NativeMethods.SERVICE_STATUS();
            bool res = NativeMethods.ControlService(m_serv, NativeMethods.SERVICE_CONTROL.STOP, ref stat);
            Console.WriteLine("[*] Stop service result: " + res);
            // TODO: Code to halt execution until the service has finally stopped, to continue another task afterwards.
            while (!res)
            {
                res = NativeMethods.QueryServiceStatus(m_serv, ref stat);
                if (stat.dwCurrentState == NativeMethods.SERVICE_STATE.SERVICE_STOPPED)
                {
                    break;
                }
                if (!res)
                {
                    int error = Marshal.GetLastWin32Error();
                    if (error == 0x6)
                    {
                        Console.WriteLine("[*] StopServiceExe ERROR_INVALID_HANDLE");
                        break;
                    }
                    if (error == 0x5)
                    {
                        Console.WriteLine("[*] StopServiceExe ERROR_ACCESS_DENIED");
                        break;
                    }

                }
                Console.WriteLine("[*] Waiting for it to stop ...");
                Thread.Sleep(5);
            }

        }

        static void PrintUsage()
        {
            Console.WriteLine("This is similar to psexec -s \\\\hostname cmd.exe");
            Console.WriteLine("Syntax: ");
            Console.WriteLine("csexec.exe \\\\{hostname} [cmd [/c] [<string>]]");
        }

        private static void CopyServiceExe(DotNetVersion version, string hostname)
        {
            byte[] svcexe = new byte[0];
            if (version == DotNetVersion.net35)
            {
                svcexe = Properties.Resources.WindowsService1;
            }
            if (version == DotNetVersion.net40)
            {
                svcexe = Properties.Resources.WindowsService1;
            }
            if (version == DotNetVersion.net45)
            {
                svcexe = Properties.Resources.WindowsService1;
            }
            var path = hostname + @"\admin$\system32\csexecsvc.exe";
            try
            {
                File.WriteAllBytes(path, svcexe);
#if DEBUG
                Console.WriteLine("[*] Copied {0} service executable to {1}", version, hostname);
#endif
            }
            catch (UnauthorizedAccessException uae)
            {
                Console.WriteLine(uae.Message);
                return;
            }
        }

        private static void CopyPayloadExe(DotNetVersion version, string hostname)
        {
            byte[] svcexe = new byte[0];
            if (version == DotNetVersion.net35)
            {
                svcexe = Properties.Resources.test;
            }
            if (version == DotNetVersion.net40)
            {
                svcexe = Properties.Resources.test;
            }
            if (version == DotNetVersion.net45)
            {
                svcexe = Properties.Resources.test;
            }
            var path = hostname + @"\c$\windows\temp\test.exe";
            try
            {
                File.WriteAllBytes(path, svcexe);
#if DEBUG
                Console.WriteLine("[*] Copied {0} payload executable to {1}", version, hostname);
#endif
            }
            catch (UnauthorizedAccessException uae)
            {
                Console.WriteLine(uae.Message);
                return;
            }
        }

        private static void DeletePayloadExe(string hostname)
        {
            var path = hostname + @"\c$\windows\temp\test.exe";

            while (File.Exists(path))
            {
                try
                {
                    Thread.Sleep(1000);
                    File.Delete(path);
#if DEBUG
                    Console.WriteLine("[*] Delating payload executable from {0}", hostname);
#endif
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    return;
                }
            }

#if DEBUG
            Console.WriteLine("[*] Delated payload executable from {0}", hostname);
#endif

        }


        private static void DeleteServiceExe(string hostname)
        {
            var path = hostname + @"\admin$\system32\csexecsvc.exe";
            
            while (File.Exists(path))
            {
                try
                {
                    Thread.Sleep(1000);
                    File.Delete(path);
#if DEBUG
                    Console.WriteLine("[*] Delating service executable from {0}", hostname);
#endif
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    return;
                }
            }

#if DEBUG
            Console.WriteLine("[*] Delated service executable from {0}", hostname);
#endif

        }

        static void InstallService(string hostname, DotNetVersion version)
        {
            //try
            //{
            //    UninstallService(hostname);
            //}
            //catch (Exception) { }

            using (var scmHandle = NativeMethods.OpenSCManager(hostname, null, NativeMethods.SCM_ACCESS.SC_MANAGER_CREATE_SERVICE))
            {
                if (scmHandle.IsInvalid)
                {
                    throw new Win32Exception();
                }

                using (
                    var serviceHandle = NativeMethods.CreateService(
                        scmHandle,
                        GlobalVars.ServiceName,
                        GlobalVars.ServiceDisplayName,
                        NativeMethods.SERVICE_ACCESS.SERVICE_ALL_ACCESS,
                        NativeMethods.SERVICE_TYPES.SERVICE_WIN32_OWN_PROCESS,
                        NativeMethods.SERVICE_START_TYPES.SERVICE_AUTO_START,
                        NativeMethods.SERVICE_ERROR_CONTROL.SERVICE_ERROR_NORMAL,
                        GlobalVars.ServiceEXE,
                        null,
                        IntPtr.Zero,
                        null,
                        null,
                        null))
                {
                    if (serviceHandle.IsInvalid)
                    {
                        throw new Win32Exception();
                    }
#if DEBUG
                    Console.WriteLine("[*] Installed {0} Service on {1}", version, hostname);
#endif
                    NativeMethods.StartService(serviceHandle, 0, null);
#if DEBUG
                    Console.WriteLine("[*] Service Started on {0}", hostname);
#endif
                }
            }
        }
        static void UninstallService(string hostname)
        {
            try
            {
                using (var scmHandle = NativeMethods.OpenSCManager(hostname, null, NativeMethods.SCM_ACCESS.SC_MANAGER_CREATE_SERVICE))
                {
                    if (scmHandle.IsInvalid)
                    {
                        throw new Win32Exception();
                    }

                    using (var serviceHandle = NativeMethods.OpenService(scmHandle, GlobalVars.ServiceName, NativeMethods.SERVICE_ACCESS.SERVICE_ALL_ACCESS))
                    {
                        if (serviceHandle.IsInvalid)
                        {
                            throw new Win32Exception();
                        }

                        NativeMethods.DeleteService(serviceHandle);
#if DEBUG
                        Console.WriteLine("[*] Service Uninstalled from {0}", hostname);
#endif
                    }
                }
            }catch (Exception e)
            {
                Console.WriteLine("[*] UninstallService Exception" + e.ToString());
            }
            
        }
        public static DotNetVersion GetDotNetVersion(string hostname)
        {
            var version = DotNetVersion.net20;
            var path1 = string.Format("{0}\\admin$\\Microsoft.NET\\Framework64", hostname);
            var path2 = string.Format("{0}\\admin$\\Microsoft.NET\\Framework", hostname);
            DirectoryInfo[] directories;
            try
            {
                var directory = new DirectoryInfo(path1);
                directories = directory.GetDirectories();
            }
            catch (IOException)
            {
                var directory = new DirectoryInfo(path2);
                directories = directory.GetDirectories();
            }
            foreach (var dir in directories)
            {
                var name = dir.Name.Substring(0, 4);
#if DEBUG
                Console.WriteLine("[*] Found .NET version: {0}", name);
#endif
                switch (name)
                {
                    case "v4.5":
                        version = DotNetVersion.net45;
                        break;
                    case "v4.0":
                        version = DotNetVersion.net40;
                        break;
                    case "v3.5":
                        version = DotNetVersion.net35;
                        break;
                    default:
                        continue;
                }
            }
#if DEBUG
            Console.WriteLine("[*] Choosing {0}", version);
#endif
            return version;
        }
        public enum DotNetVersion
        {
            net20,
            net35,
            net40,
            net45
        }
    }
}
