import json
from jira import JIRA
import requests
import itop
from datetime import datetime

user = 'jira-admin@example.com'
apikey = 'jira-api-secret'
server = 'https://customername.atlassian.net'

options = {
 'server': server
}

jira = JIRA(options, basic_auth=(user,apikey))

projects = [
   {
        "jira": "DEVEL",
        "itop": 13,
        "start": 0
   },
   {
        "jira": "QA",
        "itop": 14,
        "start": 0
   },
]

print("Starting process...")

# we process Jira projects one after the other
for project in projects:

    # Jira sends us only 50 results at a time, so we must implement a paging process.
    # The While loop is used to gather all Jira issues, incrementing by 50 each time.
    maxResults = 50
    startAt = project["start"]
    while True:
        # we gather the issues in the current project, sorted oldest first.
        project_issues = jira.search_issues("project=" + project["jira"] + " order by issuekey asc", maxResults=maxResults, startAt=startAt)

        # we do not get every attributes needed (comments, attachments)..
        # so we loop into the results and ask for a specfic issue.
        for project_issue in project_issues:
            print(project_issue.key + " / " + str(project_issues.total))
            issue = jira.issue(project_issue.key)
            print("  --> Retrieved from Jira Cloud ✓")

            # custom attribute, set to empty string if Null or missing.
            if hasattr(issue.fields, 'customfield_10100') and issue.fields.customfield_10100 is not None:
                issue.fields.customfield_10100 = "CLIENT : " + issue.fields.customfield_10100 + "\r\n"
            else:
                issue.fields.customfield_10100 = ""

            # if an issue has no description, we set it to empry string.
            if issue.fields.description is None:
                issue.fields.description = ""

            datetime_creation = (datetime.strptime(issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z")).strftime("%Y-%m-%d %H:%M:%S")

            # we create the ticket on Itop ITSM
            itop_ticket = itop.create(project["itop"], issue.key + " : " + issue.fields.summary, issue.fields.customfield_10100 + issue.fields.description, datetime_creation)
            print("  --> Ticket created on Itop ✓")
            for obj in json.loads(itop_ticket.text)["objects"]:
                ticket_id = obj.split("::")[1]

                # we add the original comments under the newly created ticket.
                for comment in issue.fields.comment.comments:
                    itop.update(ticket_id,{"public_log": comment.body})
                print("  --> Comments added on Itop ✓")

                # we add the original attachments under the newly created ticket.
                for attachment in issue.fields.attachment:
                    itop_attachment = itop.attachment(ticket_id, attachment.filename, attachment.mimeType, attachment.get())
                print("  --> Attachments added on Itop ✓")

                # we close the newly created ticket if it was closed on Jira.
                if issue.fields.resolution is not None:
                    datetime_closing = (datetime.strptime(issue.fields.resolutiondate, "%Y-%m-%dT%H:%M:%S.%f%z")).strftime("%Y-%m-%d %H:%M:%S")
                    itop.update(ticket_id,{"status": "resolved", "resolution_date": datetime_closing})
                    print("  --> Ticket closed on Itop ✓")

        # imcrementing the paging value
        startAt += maxResults
        if project_issues.startAt + maxResults > project_issues.total:
            break