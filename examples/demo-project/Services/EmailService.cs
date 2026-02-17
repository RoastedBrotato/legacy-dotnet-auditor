using System;
using System.Net.Mail;
using System.Threading;

namespace DemoApp.Services
{
    public class EmailService
    {
        // Synchronous email sending - should be queued
        public void SendEmail(string to, string subject, string body)
        {
            // Simulate long-running operation
            Thread.Sleep(2000);

            using (var client = new SmtpClient())
            {
                var message = new MailMessage("from@example.com", to, subject, body);
                client.Send(message);
            }
        }

        // Polling for status - should use SignalR
        public string CheckEmailStatus(string emailId)
        {
            while (true)
            {
                Thread.Sleep(5000);
                // Check status
                var status = GetStatus(emailId);
                if (status == "Sent")
                    return status;
            }
        }

        private string GetStatus(string emailId)
        {
            return "Pending";
        }
    }
}
