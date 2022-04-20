# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import os
from logging import DEBUG, ERROR, INFO, WARNING, basicConfig, getLogger
from string import Template
from typing import Any, Optional, Dict, List

from bugsy import Bugsy
from github import Github
from prefpicker import PrefPicker

LOG = getLogger(__name__)

REPO_NAME = "MozillaSecurity/prefpicker"

ISSUE_TITLE = Template('[prefmonitor] - Template pref "$pref" can be removed')
ISSUE_BODY = Template(
    'All entries in the `review_on_close` field for pref "$pref" have been resolved.  '
    "This pref entry can be safely removed."
)


def parse_args(argv: Any = None) -> argparse.Namespace:
    """Arg parser

    :param argv: Command line to use instead of sys.argv (optional)
    """
    log_level_map = {"ERROR": ERROR, "WARN": WARNING, "INFO": INFO, "DEBUG": DEBUG}

    parser = argparse.ArgumentParser("PrefMonitor - Prefpicker bug dependency monitor")
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="Github personal access token",
    )
    parser.add_argument(
        "--log-level",
        choices=sorted(log_level_map),
        default="INFO",
        help="Configure console logging (default: %(default)s)",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Perform dry run",
    )

    args = parser.parse_args(argv)
    if not args.token:
        parser.error("You must supply a Github access token!")

    return args


def get_closed_prefs() -> List[str]:
    """Identify which prefs can be safely removed"""
    bugsy = Bugsy()

    is_closed = []
    for template in PrefPicker.templates():
        picker = PrefPicker.load_template(template)
        for pref, entry in picker.prefs.items():
            if "review_on_close" in entry:
                bugs = bugsy.request("bug", params={"id": entry["review_on_close"]})
                if all(bug["status"] == "RESOLVED" for bug in bugs["bugs"]):
                    is_closed.append(pref)
                    LOG.info(
                        f'All dependent bugs for pref "{pref}" have been resolved.'
                    )
                else:
                    LOG.info(f'The pref "{pref}" has open dependencies.')

    return is_closed


def create_issues(prefs: List[str], token: str, dry_run: bool) -> None:
    """Create issues for closed prefs"""
    github = Github(token)
    repo = github.get_repo(REPO_NAME)

    for pref in prefs:
        title = ISSUE_TITLE.substitute({"pref": pref})
        body = ISSUE_BODY.substitute({"pref": pref})
        has_issue = False
        for issue in repo.get_issues(state="open"):
            if issue.title == title:
                LOG.warning(f'An issue for "{pref}" already exists!')
                has_issue = True

        if not has_issue:
            LOG.info(f"Creating issue: {title}")
            if not dry_run:
                repo.create_issue(title=title, body=body)


def main(argv: Optional[Dict[str, Any]] = None) -> None:
    """PrefMonitor CLI entry-point"""
    args = parse_args(argv)
    # set output verbosity
    if args.log_level == DEBUG:
        date_fmt = None
        log_fmt = "%(asctime)s %(levelname).1s %(name)s | %(message)s"
    else:
        date_fmt = "%Y-%m-%d %H:%M:%S"
        log_fmt = "[%(asctime)s] %(message)s"
    basicConfig(format=log_fmt, datefmt=date_fmt, level=args.log_level)

    prefs = get_closed_prefs()
    if len(prefs) != 0:
        create_issues(prefs, args.token, args.dry_run)
