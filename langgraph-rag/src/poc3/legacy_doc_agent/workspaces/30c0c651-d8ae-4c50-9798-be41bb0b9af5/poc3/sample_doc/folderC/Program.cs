using System;
using SampleRepo.FolderA;
using SampleRepo.FolderB;

namespace SampleRepo.FolderC
{
    class Program
    {
        static void Main(string[] args)
        {
            var calc = new Calculator();
            var logger = new Logger();
            int result = calc.Add(5, 7);
            logger.Log($"Addition result: {result}");
        }
    }
}
