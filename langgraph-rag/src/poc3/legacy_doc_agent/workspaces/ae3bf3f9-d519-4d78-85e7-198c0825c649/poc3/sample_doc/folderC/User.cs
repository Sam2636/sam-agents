namespace SampleRepo.FolderC
{
    public class User
    {
        public string Name { get; set; }
        public string Email { get; set; }

        public bool IsValid()
        {
            return !string.IsNullOrEmpty(Name) && !string.IsNullOrEmpty(Email);
        }
    }
}
