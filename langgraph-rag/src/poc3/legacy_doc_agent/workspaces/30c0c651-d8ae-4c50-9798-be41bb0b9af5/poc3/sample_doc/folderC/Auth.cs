using System;

namespace SampleRepo.FolderC
{
    public class Auth
    {
        public bool Login(string username, string password)
        {
            // Dummy authentication logic
            return username == "admin" && password == "password";
        }

        public void Logout()
        {
            Console.WriteLine("User logged out");
        }
    }
}
