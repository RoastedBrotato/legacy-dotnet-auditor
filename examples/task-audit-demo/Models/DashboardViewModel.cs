using System.Collections.Generic;

namespace TaskAuditDemo.Models
{
    public class DashboardViewModel
    {
        public int TotalTasks { get; set; }
        public int PendingApproval { get; set; }
        public int InProgress { get; set; }
        public int Approved { get; set; }
        public List<TaskItem> MyAssignedTasks { get; set; }
        public List<TaskItem> MyCreatedTasks { get; set; }
    }
}
