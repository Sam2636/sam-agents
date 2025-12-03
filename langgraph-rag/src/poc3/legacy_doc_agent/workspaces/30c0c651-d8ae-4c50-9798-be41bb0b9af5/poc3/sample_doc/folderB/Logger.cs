using System;

namespace SampleRepo.FolderB
{
    public class Logger
    {
        public void Log(string message)
        {
            Console.WriteLine($"[LOG] {message}");
        }
    }
}
