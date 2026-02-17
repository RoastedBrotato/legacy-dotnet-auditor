using TaskAuditDemo.Models;
using TaskAuditDemo.Services;

namespace TaskAuditDemo.Controllers
{
    public class TaskController
    {
        private readonly TaskService _taskService;

        public TaskController(TaskService taskService)
        {
            _taskService = taskService;
        }

        public TaskItem Assign(int assignedByUserId, int assignedToUserId, string title, string description)
        {
            return _taskService.AssignTask(assignedByUserId, assignedToUserId, title, description);
        }

        public bool UpdateStatus(int taskId, int updatedByUserId, TaskStatus newStatus)
        {
            return _taskService.UpdateTaskStatus(taskId, updatedByUserId, newStatus);
        }
    }
}
