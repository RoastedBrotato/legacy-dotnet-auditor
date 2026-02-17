using System;
using System.Collections.Generic;
using System.Linq;
using System.Web.Mvc;
using System.Threading.Tasks;

namespace DemoApp.Controllers
{
    // This is a large controller with multiple anti-patterns
    public class UserController : Controller
    {
        private readonly UserRepository _userRepository;
        private readonly EmailService _emailService;

        public UserController(UserRepository userRepository, EmailService emailService)
        {
            _userRepository = userRepository;
            _emailService = emailService;
        }

        // ISSUE: Synchronous blocking with .Result
        public ActionResult Index()
        {
            var users = GetUsersAsync().Result; // BAD: Blocking call
            return View(users);
        }

        // ISSUE: Database operation in loop - N+1 problem
        public ActionResult ProcessUsers()
        {
            var users = _userRepository.GetAll();

            foreach (var user in users)
            {
                // BAD: Database call inside loop
                var orders = _userRepository.GetUserOrders(user.Id).Result;
                user.OrderCount = orders.Count();
            }

            return View(users);
        }

        // ISSUE: Sequential HTTP calls
        public async Task<ActionResult> GetUserData(int userId)
        {
            var client = new HttpClient();

            // BAD: Sequential HTTP calls - could be parallelized
            var profile = await client.GetAsync($"/api/profile/{userId}");
            var settings = await client.GetAsync($"/api/settings/{userId}");
            var preferences = await client.GetAsync($"/api/preferences/{userId}");

            return View();
        }

        // ISSUE: Long-running operation in request thread
        public ActionResult SendBulkEmails(List<int> userIds)
        {
            foreach (var userId in userIds)
            {
                var user = _userRepository.GetById(userId).Wait(); // BAD: Should be queued
                _emailService.SendEmail(user.Email, "Subject", "Body");
            }

            return RedirectToAction("Index");
        }

        // Helper method
        private async Task<List<User>> GetUsersAsync()
        {
            return await _userRepository.GetAllAsync();
        }

        // More methods to make this file large...
        public ActionResult Details(int id) { return View(); }
        public ActionResult Create() { return View(); }
        public ActionResult Edit(int id) { return View(); }
        public ActionResult Delete(int id) { return View(); }
        public ActionResult Search(string query) { return View(); }
        public ActionResult Export() { return View(); }
        public ActionResult Import() { return View(); }
        public ActionResult Reports() { return View(); }
        public ActionResult Settings() { return View(); }
        public ActionResult Profile(int id) { return View(); }
        public ActionResult UpdateProfile(int id) { return View(); }
        public ActionResult ChangePassword(int id) { return View(); }
        public ActionResult Notifications(int id) { return View(); }
        public ActionResult Messages(int id) { return View(); }
        public ActionResult Friends(int id) { return View(); }
        public ActionResult Activity(int id) { return View(); }
        public ActionResult Photos(int id) { return View(); }
        public ActionResult Videos(int id) { return View(); }
        public ActionResult Documents(int id) { return View(); }
        public ActionResult Calendar(int id) { return View(); }
        public ActionResult Tasks(int id) { return View(); }
        public ActionResult Notes(int id) { return View(); }
        public ActionResult Tags(int id) { return View(); }
        public ActionResult Categories(int id) { return View(); }
        public ActionResult Statistics(int id) { return View(); }
        public ActionResult Analytics(int id) { return View(); }
        public ActionResult Dashboard(int id) { return View(); }
        public ActionResult Overview(int id) { return View(); }
        public ActionResult Summary(int id) { return View(); }
        public ActionResult History(int id) { return View(); }
        public ActionResult Logs(int id) { return View(); }
        public ActionResult Audit(int id) { return View(); }
        public ActionResult Security(int id) { return View(); }
        public ActionResult Privacy(int id) { return View(); }
        public ActionResult Terms(int id) { return View(); }
        public ActionResult Help(int id) { return View(); }
        public ActionResult Support(int id) { return View(); }
        public ActionResult Contact(int id) { return View(); }
        public ActionResult About(int id) { return View(); }
        public ActionResult FAQ(int id) { return View(); }
        public ActionResult Feedback(int id) { return View(); }
        public ActionResult Subscribe(int id) { return View(); }
        public ActionResult Unsubscribe(int id) { return View(); }
        public ActionResult Activate(int id) { return View(); }
        public ActionResult Deactivate(int id) { return View(); }
        public ActionResult Archive(int id) { return View(); }
        public ActionResult Restore(int id) { return View(); }
        public ActionResult Backup(int id) { return View(); }
        public ActionResult Download(int id) { return View(); }
        public ActionResult Upload(int id) { return View(); }
        public ActionResult Share(int id) { return View(); }
        public ActionResult Print(int id) { return View(); }
        public ActionResult Preview(int id) { return View(); }
        public ActionResult Validate(int id) { return View(); }
        public ActionResult Process(int id) { return View(); }
        public ActionResult Calculate(int id) { return View(); }
        public ActionResult Generate(int id) { return View(); }
        public ActionResult Transform(int id) { return View(); }
        public ActionResult Convert(int id) { return View(); }
        public ActionResult Merge(int id) { return View(); }
        public ActionResult Split(int id) { return View(); }
        public ActionResult Copy(int id) { return View(); }
        public ActionResult Move(int id) { return View(); }
        public ActionResult Rename(int id) { return View(); }
        public ActionResult Duplicate(int id) { return View(); }
        public ActionResult Clone(int id) { return View(); }
        public ActionResult Compare(int id) { return View(); }
        public ActionResult Verify(int id) { return View(); }
        public ActionResult Confirm(int id) { return View(); }
        public ActionResult Approve(int id) { return View(); }
        public ActionResult Reject(int id) { return View(); }
        public ActionResult Publish(int id) { return View(); }
        public ActionResult Unpublish(int id) { return View(); }
        public ActionResult Schedule(int id) { return View(); }
        public ActionResult Cancel(int id) { return View(); }
        public ActionResult Reschedule(int id) { return View(); }
        public ActionResult Postpone(int id) { return View(); }
        public ActionResult Complete(int id) { return View(); }
        public ActionResult Incomplete(int id) { return View(); }
        public ActionResult Start(int id) { return View(); }
        public ActionResult Stop(int id) { return View(); }
        public ActionResult Pause(int id) { return View(); }
        public ActionResult Resume(int id) { return View(); }
        public ActionResult Restart(int id) { return View(); }
        public ActionResult Reset(int id) { return View(); }
        public ActionResult Clear(int id) { return View(); }
        public ActionResult Refresh(int id) { return View(); }
        public ActionResult Reload(int id) { return View(); }
        public ActionResult Sync(int id) { return View(); }
        public ActionResult Update(int id) { return View(); }
        public ActionResult Upgrade(int id) { return View(); }
        public ActionResult Downgrade(int id) { return View(); }
        public ActionResult Migrate(int id) { return View(); }
        public ActionResult Rollback(int id) { return View(); }
        public ActionResult Commit(int id) { return View(); }
        public ActionResult Revert(int id) { return View(); }
        public ActionResult Undo(int id) { return View(); }
        public ActionResult Redo(int id) { return View(); }
        public ActionResult Save(int id) { return View(); }
        public ActionResult Discard(int id) { return View(); }
        public ActionResult Apply(int id) { return View(); }
        public ActionResult Close(int id) { return View(); }
        public ActionResult Open(int id) { return View(); }
        public ActionResult Lock(int id) { return View(); }
        public ActionResult Unlock(int id) { return View(); }
        public ActionResult Enable(int id) { return View(); }
        public ActionResult Disable(int id) { return View(); }
        public ActionResult Show(int id) { return View(); }
        public ActionResult Hide(int id) { return View(); }
        public ActionResult Expand(int id) { return View(); }
        public ActionResult Collapse(int id) { return View(); }
        public ActionResult Maximize(int id) { return View(); }
        public ActionResult Minimize(int id) { return View(); }
        public ActionResult Zoom(int id) { return View(); }
        public ActionResult Pan(int id) { return View(); }
        public ActionResult Rotate(int id) { return View(); }
        public ActionResult Flip(int id) { return View(); }
        public ActionResult Crop(int id) { return View(); }
        public ActionResult Resize(int id) { return View(); }
        public ActionResult Adjust(int id) { return View(); }
        public ActionResult Filter(int id) { return View(); }
        public ActionResult Sort(int id) { return View(); }
        public ActionResult Group(int id) { return View(); }
        public ActionResult Ungroup(int id) { return View(); }
        public ActionResult Align(int id) { return View(); }
        public ActionResult Distribute(int id) { return View(); }
        public ActionResult Arrange(int id) { return View(); }
        public ActionResult Order(int id) { return View(); }
        public ActionResult Select(int id) { return View(); }
        public ActionResult Deselect(int id) { return View(); }
        public ActionResult ToggleSelection(int id) { return View(); }
        public ActionResult SelectAll(int id) { return View(); }
        public ActionResult DeselectAll(int id) { return View(); }
        public ActionResult InvertSelection(int id) { return View(); }
        public ActionResult Find(int id) { return View(); }
        public ActionResult Replace(int id) { return View(); }
        public ActionResult Navigate(int id) { return View(); }
        public ActionResult Go(int id) { return View(); }
        public ActionResult Back(int id) { return View(); }
        public ActionResult Forward(int id) { return View(); }
        public ActionResult Home(int id) { return View(); }
        public ActionResult End(int id) { return View(); }
        public ActionResult First(int id) { return View(); }
        public ActionResult Last(int id) { return View(); }
        public ActionResult Next(int id) { return View(); }
        public ActionResult Previous(int id) { return View(); }
        public ActionResult Random(int id) { return View(); }
    }
}
