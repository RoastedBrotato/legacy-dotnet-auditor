using TaskAuditDemo.Services;

namespace TaskAuditDemo.Controllers
{
    public class ApprovalController
    {
        private readonly TaskService _taskService;

        public ApprovalController(TaskService taskService)
        {
            _taskService = taskService;
        }

        public bool Approve(int taskId, int approverUserId)
        {
            return _taskService.ApproveTask(taskId, approverUserId, true);
        }

        public bool Reject(int taskId, int approverUserId)
        {
            return _taskService.ApproveTask(taskId, approverUserId, false);
        }
    }
}
