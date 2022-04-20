# prefpicker-monitor

[![Task Status](https://community-tc.services.mozilla.com/api/github/v1/repository/MozillaSecurity/prefpicker-monitor/master/badge.svg)](https://community-tc.services.mozilla.com/api/github/v1/repository/MozillaSecurity/prefpicker-monitor/master/latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/MozillaSecurity/prefpicker-monitor/branch/master/graph/badge.svg)](https://codecov.io/gh/MozillaSecurity/prefpicker-monitor)

Prefpicker bug dependency monitor

## Overview
Prefpicker-monitor is a tool for monitoring bugs associated with individual prefs in prefpicker templates.  When a dependent bug has been resolved, prefpicker-monitor will open an issue indicating that the pref entry should be removed.'

## Installation
```shell script
git clone https://github.com/MozillaSecurity/prefpicker-monitor
cd prefpicker-monitor
poetry install
```
## Basic Usage
```shell script
> export GITHUB_TOKEN="ghp_988881adc9fc3655077dc2d4d757d480b5ea0e11"
> poetry run prefmonitor
[2022-04-20 09:17:50] The pref "dom.imagecapture.enabled" has open dependencies.
[2022-04-20 09:17:50] The pref "dom.paintWorklet.enabled" has open dependencies.
[2022-04-20 09:17:51] The pref "dom.security.sanitizer.enabled" has open dependencies.
[2022-04-20 09:17:51] The pref "dom.vr.puppet.enabled" has open dependencies.
[2022-04-20 09:17:52] The pref "media.getusermedia.audiocapture.enabled" has open dependencies.
[2022-04-20 09:17:52] The pref "media.getusermedia.browser.enabled" has open dependencies.
[2022-04-20 09:17:53] The pref "media.track.enabled" has open dependencies.
[2022-04-20 09:17:53] The pref "media.webspeech.recognition.enable" has open dependencies.
[2022-04-20 09:17:53] All dependent bugs for pref "foo.bar.pref" have been resolved.
[2022-04-20 09:17:53] Creating issue: [prefmonitor] - Template pref "foo.bar.pref" can be removed
```

## Contributing
Before submitting commits, make sure that you install both the pre-commit and pre-commit commit-message hooks:
```shell script
> pre-commit install
> pre-commit install --hook-type commit-msg
```
