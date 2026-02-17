using System.Linq;
using System.Threading.Tasks;
using TaskAuditDemo.Models;
using TaskAuditDemo.Services;

namespace TaskAuditDemo.Controllers
{
    public class DashboardController
    {
        private readonly TaskService _taskService;
        private readonly UserService _userService;

        public DashboardController(TaskService taskService, UserService userService)
        {
            _taskService = taskService;
            _userService = userService;
        }

        public DashboardViewModel Index(int currentUserId)
        {
            var allTasks = _taskService.GetAllTasks();
            var health = _userService.GetUserHealthSummaryAsync().Result;

            return new DashboardViewModel
            {
                TotalTasks = allTasks.Count,
                PendingApproval = allTasks.Count(t => t.Status == TaskStatus.Done),
                InProgress = allTasks.Count(t => t.Status == TaskStatus.InProgress),
                Approved = allTasks.Count(t => t.Status == TaskStatus.Approved),
                MyAssignedTasks = allTasks.Where(t => t.AssignedToUserId == currentUserId).ToList(),
                MyCreatedTasks = allTasks.Where(t => t.AssignedByUserId == currentUserId).ToList()
            };
        }

        public async Task<string> Ping()
        {
            return await _userService.GetUserHealthSummaryAsync();
        }
    }
}
