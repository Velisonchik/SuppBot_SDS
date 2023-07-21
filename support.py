from reqs import SUPPORT_SITE, SUPPORT_API_KEY, SUPPORT_VERSION, PROJECT_ID_FOR_NEW_ISSUE
from redminelib import Redmine

tracker_ids = {'i': 2, 'c': 3, 'e': 1}


def create_new_issue(subject: str, description: str, username: str, tracker_id_in_str: str, elapsed_time: float,
                     author_issue='', comment=''):
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
    issue = redmine_for_author_issue.issue.create(
        project_id=PROJECT_ID_FOR_NEW_ISSUE,
        subject=subject,
        tracker_id=tracker_ids[tracker_id_in_str],
        description=description,
        status_id=5,
        priority_id=4,
        category_id=186,
        fixed_version_id=4,
        assigned_to_id=assigned_to_id,
        done_ratio=40,
    )
    redmine_for_current_user = Redmine(SUPPORT_SITE, key=redmine_adm.user.get(assigned_to_id).api_key,
                                       version=SUPPORT_VERSION)

    redmine_for_current_user.time_entry.create(
        issue_id=issue.id,
        hours=elapsed_time,
        user_id=assigned_to_id,
        comments=comment
    )
    print(issue.url)
    return issue.url


if __name__ == '__main__':
    print(create_new_issue(subject='Test SuppBot', description='Description', username='', tracker_id_in_str='c',
                           elapsed_time=0.8))
