﻿using System;
using System.Diagnostics;
using System.IO;
using System.IO.Pipes;
using System.ServiceProcess;
using System.Text;
using System.Threading;

namespace csexecsvc
{
    class csexecsvc : ServiceBase
    {
        public const string _ServiceName = "csexecsvc";

        static void Main(string[] args)
        {
            Run(new csexecsvc());
        }

        public csexecsvc()
        {
            ServiceName = _ServiceName;
        }

        protected override void OnStart(string[] args)
        {
#if DEBUG
            Console.WriteLine("Service Started.");
#endif
            new Thread(workerthread) { IsBackground = true, Name = _ServiceName }.Start();
        }

        protected override void OnStop()
        {
            base.OnStop();
        }

        void workerthread()
        {
            using (var pipe = new NamedPipeServerStream(
                _ServiceName,
                PipeDirection.InOut,
                NamedPipeServerStream.MaxAllowedServerInstances,
                PipeTransmissionMode.Message))
            {
#if DEBUG
                Console.WriteLine("[*] Waiting for client connection...");
#endif
                pipe.WaitForConnection();
#if DEBUG
                Console.WriteLine("[*] Client connected.");
#endif
                while (true)
                {
                    var messageBytes = ReadMessage(pipe);
                    var line = Encoding.UTF8.GetString(messageBytes);
#if DEBUG
                    Console.WriteLine("[*] Received: {0}", line);
#endif
                    if (line.ToLower().Trim() == "exit")
                    {
                        Process.GetCurrentProcess().Kill();
                        return;
                    }

                    var processStartInfo = new ProcessStartInfo
                    {
                        FileName = "cmd.exe",
                        Arguments = "/c " + line,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        UseShellExecute = false
                    };
                    try
                    {
                        var process = Process.Start(processStartInfo);
                        var output = process.StandardOutput.ReadToEnd();
                        output += process.StandardError.ReadToEnd();
                        process.WaitForExit();
                        if (string.IsNullOrEmpty(output))
                        {
                            output = "\n";
                        }
                        var response = Encoding.UTF8.GetBytes(output);
                        pipe.Write(response, 0, response.Length);
                    }
                    catch (Exception ex)
                    {
#if DEBUG
                        Console.WriteLine(ex);
#endif
                        var response = Encoding.UTF8.GetBytes(ex.Message);
                        pipe.Write(response, 0, response.Length);
                    }
                }
            }
        }

        private static byte[] ReadMessage(PipeStream pipe)
        {
            byte[] buffer = new byte[1024];
            using (var ms = new MemoryStream())
            {
                do
                {
                    var readBytes = pipe.Read(buffer, 0, buffer.Length);
                    ms.Write(buffer, 0, readBytes);
                }
                while (!pipe.IsMessageComplete);

                return ms.ToArray();
            }
        }
    }
}
