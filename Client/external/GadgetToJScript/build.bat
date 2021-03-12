@echo off
GadgetToJScript.NET4.x.exe -c GadgetToJScript.cs -w hta -o test -d System.Linq.dll,System.dll --bypass
GadgetToJScript.NET4.x.exe -c GadgetToJScript.cs -w js -o test -d System.Linq.dll,System.dll --bypass
GadgetToJScript.NET4.x.exe -c GadgetToJScript.cs -w vba -o test -d System.Linq.dll,System.dll --bypass
GadgetToJScript.NET4.x.exe -c GadgetToJScript.cs -w vbs -o test -d System.Linq.dll,System.dll --bypass