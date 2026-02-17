namespace TaskAuditDemo.Models
{
    public enum UserRole
    {
        Manager,
        Contributor,
        Approver
    }

    public class User
    {
        public int Id { get; set; }
        public string FullName { get; set; }
        public string Email { get; set; }
        public UserRole Role { get; set; }
    }
}
