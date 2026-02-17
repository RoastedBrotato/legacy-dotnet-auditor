using System.Net.Http;
using System.Threading.Tasks;
using TaskAuditDemo.Repositories;

namespace TaskAuditDemo.Services
{
    public class UserService
    {
        private readonly UserRepository _users;
        private readonly HttpClient _httpClient;

        public UserService(UserRepository users)
        {
            _users = users;
            _httpClient = new HttpClient();
        }

        public string GetDisplayName(int userId)
        {
            var user = _users.GetById(userId);
            return user == null ? "Unknown User" : user.FullName;
        }

        public async Task<string> GetUserHealthSummaryAsync()
        {
            var statusOne = await _httpClient.GetAsync("https://example.com/health/users");
            var statusTwo = await _httpClient.GetAsync("https://example.com/health/tasks");
            return statusOne.StatusCode + " / " + statusTwo.StatusCode;
        }
    }
}
