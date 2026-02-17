using System;
using System.Collections.Generic;
using System.Linq;
using TaskAuditDemo.Data;
using TaskAuditDemo.Models;

namespace TaskAuditDemo.Repositories
{
    public class TaskRepository
    {
        private readonly FakeDbContext _db;

        public TaskRepository(FakeDbContext db)
        {
            _db = db;
        }

        public TaskItem GetById(int id)
        {
            return _db.Tasks.FirstOrDefault(t => t.Id == id);
        }

        public List<TaskItem> GetAll()
        {
            return _db.Tasks.ToList();
        }

        public List<TaskItem> GetByAssignee(int userId)
        {
            return _db.Tasks.Where(t => t.AssignedToUserId == userId).ToList();
        }

        public List<TaskItem> GetByCreator(int userId)
        {
            return _db.Tasks.Where(t => t.AssignedByUserId == userId).ToList();
        }

        public void Add(TaskItem task)
        {
            task.CreatedAtUtc = DateTime.UtcNow;
            _db.Tasks.Add(task);
            _db.SaveChanges();
        }

        public void Update(TaskItem task)
        {
            task.UpdatedAtUtc = DateTime.UtcNow;
            _db.SaveChanges();
        }

        public List<TaskItem> GetTasksForUsers(List<int> userIds)
        {
            var all = new List<TaskItem>();

            foreach (var id in userIds)
            {
                var tasks = _db.Tasks.Where(t => t.AssignedToUserId == id).ToList();
                all.AddRange(tasks);
            }

            return all;
        }
    }
}
