using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Linq;
using System.ServiceProcess;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace WindowsService1
{
    public partial class Service1 : ServiceBase
    {
        public Service1()
        {
            InitializeComponent();
        }

        protected override void OnStart(string[] args)
        {
            var si = new ProcessStartInfo
            {
                FileName = @"C:\windows\temp\test.exe",
                Arguments = @"dummy"
            };

            var proc = new Process
            {
                StartInfo = si
            };

            var t = new Thread(() =>
            {
                proc.Start();
                proc.WaitForExit();
                proc.Dispose();
            });

            t.Start();
        }

        protected override void OnStop()
        {
            base.OnStop();
        }
    }
}
