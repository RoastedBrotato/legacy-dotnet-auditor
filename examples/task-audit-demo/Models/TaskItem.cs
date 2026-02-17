using System;

namespace TaskAuditDemo.Models
{
    public enum TaskStatus
    {
        Created,
        Assigned,
        InProgress,
        Done,
        Approved,
        Rejected
    }

    public class TaskItem
    {
        public int Id { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public int AssignedByUserId { get; set; }
        public int AssignedToUserId { get; set; }
        public int? ApprovedByUserId { get; set; }
        public TaskStatus Status { get; set; }
        public DateTime CreatedAtUtc { get; set; }
        public DateTime? UpdatedAtUtc { get; set; }
        public DateTime? ApprovedAtUtc { get; set; }
    }
}
