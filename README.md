# GitHub Activity CLI

Developed as per the requirements provided as part of https://roadmap.sh/projects/github-user-activity

## Introduction
GitHub Activity CLI is a command-line tool that displays recent GitHub activity for any user. It shows various activities including:
- Push events
- Issue events
- Pull request events
- Repository creation events
- Watch (star) events

The tool provides a clean, formatted output with timestamps and color-coding for better readability.

## Prerequisites

### Python
- Python 3.8 or higher
- pip (Python package installer)

### GitHub Authentication (Optional but Recommended)
To avoid API rate limits, you'll need:
- GitHub username
- GitHub Personal Access Token

To create a Personal Access Token:
1. Go to GitHub Settings
2. Navigate to Developer Settings > Personal access tokens > Tokens (classic)
3. Click "Generate new token"
4. Select at least these scopes:
   - `read:user`
   - `repo`
5. Copy the generated token (you won't see it again!)

## Installation

1. Clone the repository:
2. Install the dependencies:
3. Run the tool:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py install
git clone https://github.com/officialsuhassuresh/github-activity.git
cd github-activity
```

## Usage

```bash
export GITHUB_TOKEN=<your_token>
export GITHUB_USERNAME=<your_username>
github-activity --username <username>
```

## Tests

```bash
pytest
```

## Coverage

```bash
pytest --cov=github_activity
```

## License

This project is open-sourced under the MIT License - see the LICENSE file for details.
