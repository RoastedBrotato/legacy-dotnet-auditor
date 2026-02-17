using System.Collections.Generic;
using TaskAuditDemo.Models;

namespace TaskAuditDemo.Data
{
    public class FakeDbContext
    {
        public List<User> Users { get; set; }
        public List<TaskItem> Tasks { get; set; }

        public FakeDbContext()
        {
            Users = new List<User>
            {
                new User { Id = 1, FullName = "Maya Manager", Email = "maya@demo.local", Role = UserRole.Manager },
                new User { Id = 2, FullName = "Ali Contributor", Email = "ali@demo.local", Role = UserRole.Contributor },
                new User { Id = 3, FullName = "Rina Contributor", Email = "rina@demo.local", Role = UserRole.Contributor },
                new User { Id = 4, FullName = "Arun Approver", Email = "arun@demo.local", Role = UserRole.Approver }
            };

            Tasks = new List<TaskItem>
            {
                new TaskItem { Id = 101, Title = "Prepare sprint plan", Description = "Draft sprint goals", AssignedByUserId = 1, AssignedToUserId = 2, Status = TaskStatus.InProgress },
                new TaskItem { Id = 102, Title = "Build dashboard widgets", Description = "Implement KPI tiles", AssignedByUserId = 1, AssignedToUserId = 3, Status = TaskStatus.Assigned },
                new TaskItem { Id = 103, Title = "Security review", Description = "Verify auth policies", AssignedByUserId = 1, AssignedToUserId = 2, Status = TaskStatus.Done }
            };
        }

        public void SaveChanges()
        {
            // No-op in demo. Included to resemble EF usage patterns.
        }
    }
}
