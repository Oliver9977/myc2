using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Management.Automation;
using System.Management.Automation.Runspaces;
using System.Collections.ObjectModel;

namespace myclient
{
    class PsRun
    {
        private Runspace rs = RunspaceFactory.CreateRunspace();

        private Runspace remoteRunspace;


        public Runspace cleanPsRun
        {
            set
            {
                rs = value;
            }
        }

        public void init()
        {
            rs.ApartmentState = System.Threading.ApartmentState.MTA;
            rs.ThreadOptions = PSThreadOptions.UseCurrentThread;
            rs.Open();
        }
        public void remoteInit(string connect)
        {
            Uri RemoteComputerUri = new Uri(connect);
            WSManConnectionInfo connectionInfo = new WSManConnectionInfo(RemoteComputerUri);
            remoteRunspace = RunspaceFactory.CreateRunspace(connectionInfo);
            remoteRunspace.ApartmentState = System.Threading.ApartmentState.MTA;
            remoteRunspace.ThreadOptions = PSThreadOptions.UseCurrentThread;
            remoteRunspace.Open();

            rs = remoteRunspace; //override

        }

        public string doPsRun(string testInput)
        {

            

            Pipeline ps = rs.CreatePipeline();
            ps.Commands.AddScript(testInput);

            Collection<PSObject> results = ps.Invoke();
            StringBuilder stringBuilder = new StringBuilder();
            foreach (PSObject obj in results)
            {
                stringBuilder.AppendLine(obj.ToString());
            }

            var response = stringBuilder.ToString();
            return response;
        }
    }
}

