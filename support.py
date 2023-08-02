import os

from reqs import SUPPORT_SITE, SUPPORT_API_KEY, SUPPORT_VERSION, PROJECT_ID_FOR_NEW_ISSUE
from redminelib import Redmine

tracker_ids = {'i': 2, 'c': 3, 'e': 1}


def create_new_issue(subject: str, description: str, username: str, tracker_id_in_str: str, elapsed_time: float,
                     author_issue='', comment='', file_path=''):
    print('Result of create_new_issue: ')
    if not author_issue:
        author_issue = username
    redmine_adm = Redmine(SUPPORT_SITE, key=SUPPORT_API_KEY, version=SUPPORT_VERSION)
    assigned_to_id = int(list(redmine_adm.user.filter(name=username).values('id'))[0]['id'])
    try:
        author_issue_id = int(list(redmine_adm.user.filter(name=author_issue).values('id'))[0]['id'])
    except IndexError:
        return f'Такого пользователя {author_issue} не нашел в саппорте'
    redmine_for_author_issue = Redmine(SUPPORT_SITE, key=redmine_adm.user.get(author_issue_id).api_key,
                                       version=SUPPORT_VERSION)

    issue = redmine_for_author_issue.issue.new()
    issue.project_id = PROJECT_ID_FOR_NEW_ISSUE
    issue.subject = subject
    issue.tracker_id = tracker_ids[tracker_id_in_str]
    issue.description = description
    issue.status_id = 5
    issue.priority_id = 4
    issue.category_id = 186
    issue.fixed_version_id = 4
    issue.assigned_to_id = assigned_to_id
    issue.done_ratio = 40
    if file_path != '':
        issue.uploads = [{'path': f'{file_path}', 'filename': f'{file_path}'}]
    issue.save()
    os.remove(file_path)

    redmine_for_current_user = Redmine(SUPPORT_SITE, key=redmine_adm.user.get(assigned_to_id).api_key,
                                       version=SUPPORT_VERSION)

    redmine_for_current_user.time_entry.create(
        issue_id=issue.id,
        hours=elapsed_time,
        user_id=assigned_to_id,
        # comments=comment
    )
    if comment != '':
        redmine_for_current_user.issue.update(resource_id=issue.id, notes=comment)

    print(issue.url)
    return issue.url


if __name__ == '__main__':
    print(create_new_issue(subject='Test SuppBot', description='Description', username='kashanyan.v',
                           tracker_id_in_str='c',
                           elapsed_time=0.8, comment='Тестовый коммент'))
