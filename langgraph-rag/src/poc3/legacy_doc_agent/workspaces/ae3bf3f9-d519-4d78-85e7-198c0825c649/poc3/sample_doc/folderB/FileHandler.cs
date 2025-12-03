using System.IO;

namespace SampleRepo.FolderB
{
    public class FileHandler
    {
        public void WriteToFile(string path, string content)
        {
            File.WriteAllText(path, content);
        }

        public string ReadFromFile(string path)
        {
            return File.ReadAllText(path);
        }
    }
}
