# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
from json import dumps
from pathlib import Path

import pytest

from github.Issue import Issue

from prefmonitor.main import get_closed_prefs, create_issues, ISSUE_TITLE, ISSUE_BODY

BUG_ID = 123456
TEMPLATE = {
    "pref": {
        "dom.imagecapture.enabled": {
            "review_on_close": [BUG_ID],
            "variants": {"default": [None]},
        }
    }
}


@pytest.mark.parametrize("status, count", [("RESOLVED", 1), ("NEW", 0)])
def test_get_closed_prefs(mocker, status, count):
    """Verify that prefs with resolved dependencies are identified"""
    mocker.patch(
        "prefmonitor.main.PrefPicker.templates", return_value=[Path("/foo/bar.yml")]
    )
    mocker.patch(
        "pathlib.Path.read_bytes", return_value=dumps(TEMPLATE).encode("utf-8")
    )
    mocker.patch(
        "prefmonitor.main.Bugsy.request",
        return_value={"bugs": [{"id": BUG_ID, "status": status}]},
    )
    assert len(get_closed_prefs()) == count


@pytest.mark.parametrize("dry_run", [True, False])
def test_create_issues_success(mocker, dry_run):
    """Verify that issues are created"""
    mock_github_class = mocker.patch("prefmonitor.main.Github")
    mock_github_instance = mock_github_class.return_value
    mock_repo = mock_github_instance.get_repo.return_value

    create_issues(["dom.imagecapture.enabled"], "", dry_run)

    title = ISSUE_TITLE.substitute({"pref": "dom.imagecapture.enabled"})
    body = ISSUE_BODY.substitute({"pref": "dom.imagecapture.enabled"})
    if dry_run:
        mock_repo.create_issue.assert_not_called()
    else:
        mock_repo.create_issue.assert_called_once_with(title=title, body=body)


def test_create_issues_duplicate(mocker):
    """Verify that no duplicate issues are created"""
    pref = "dom.imagecapture.enabled"
    title = ISSUE_TITLE.substitute({"pref": pref})

    mock_github_class = mocker.patch("prefmonitor.main.Github")
    mock_github_instance = mock_github_class.return_value
    mock_repo = mock_github_instance.get_repo.return_value

    issue = mocker.MagicMock(Issue)
    issue.title = title
    mock_repo.get_issues = mocker.MagicMock(return_value=[issue])

    create_issues([pref], "", False)
    mock_repo.create_issue.assert_not_called()
