using System.Collections.Generic;
using System.Linq;
using TaskAuditDemo.Data;
using TaskAuditDemo.Models;

namespace TaskAuditDemo.Repositories
{
    public class UserRepository
    {
        private readonly FakeDbContext _db;

        public UserRepository(FakeDbContext db)
        {
            _db = db;
        }

        public User GetById(int id)
        {
            return _db.Users.FirstOrDefault(u => u.Id == id);
        }

        public List<User> GetAll()
        {
            return _db.Users.ToList();
        }
    }
}
