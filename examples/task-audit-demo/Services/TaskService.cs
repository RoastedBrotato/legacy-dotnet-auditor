using System;
using System.Collections.Generic;
using TaskAuditDemo.Models;
using TaskAuditDemo.Repositories;

namespace TaskAuditDemo.Services
{
    public class TaskService
    {
        private readonly TaskRepository _tasks;

        public TaskService(TaskRepository tasks)
        {
            _tasks = tasks;
        }

        public List<TaskItem> GetAllTasks()
        {
            return _tasks.GetAll();
        }

        public TaskItem AssignTask(int assignedByUserId, int assignedToUserId, string title, string description)
        {
            var task = new TaskItem
            {
                Id = new Random().Next(1000, 9999),
                AssignedByUserId = assignedByUserId,
                AssignedToUserId = assignedToUserId,
                Title = title,
                Description = description,
                Status = TaskStatus.Assigned
            };

            _tasks.Add(task);
            return task;
        }

        public bool UpdateTaskStatus(int taskId, int updatedByUserId, TaskStatus newStatus)
        {
            var task = _tasks.GetById(taskId);
            if (task == null)
            {
                return false;
            }

            if (task.AssignedToUserId != updatedByUserId)
            {
                return false;
            }

            task.Status = newStatus;
            _tasks.Update(task);
            return true;
        }

        public bool ApproveTask(int taskId, int approverUserId, bool approved)
        {
            var task = _tasks.GetById(taskId);
            if (task == null)
            {
                return false;
            }

            task.ApprovedByUserId = approverUserId;
            task.ApprovedAtUtc = DateTime.UtcNow;
            task.Status = approved ? TaskStatus.Approved : TaskStatus.Rejected;
            _tasks.Update(task);
            return true;
        }
    }
}
