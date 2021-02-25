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
        
        public Runspace cleanPsRun
        {
            set
            {
                rs = value;
            }
        }

        public string doPsRun(string testInput)
        {

            rs.ApartmentState = System.Threading.ApartmentState.STA;
            rs.Open();

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

