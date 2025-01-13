#!/usr/bin/env python3
from typing import Dict, List, Optional
import fire
import urllib.request
import urllib.error
import json
import os
import base64
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()

def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers using environment variables.
    
    Returns:
        Dictionary of headers including authentication
        
    Raises:
        ValueError: If required environment variables are not set
    """
    username = os.getenv('GITHUB_USERNAME')
    token = os.getenv('GITHUB_TOKEN')
    
    if not username or not token:
        raise ValueError(
            "Missing required environment variables.\n"
            "Please set USERNAME and GITHUB_TOKEN environment variables."
        )
    
    # Create basic auth header
    auth = base64.b64encode(f"{username}:{token}".encode()).decode()
    
    return {
        'User-Agent': 'GitHub-Activity-CLI/1.0',
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'Basic {auth}'
    }

def fetch_github_events(username: str) -> List[Dict]:
    """Fetch recent GitHub events for a given username.
    
    Args:
        username: GitHub username to fetch events for
        
    Returns:
        List of event dictionaries from GitHub API
        
    Raises:
        urllib.error.HTTPError: If API request fails
        ValueError: If username is invalid or env variables not set
    """
    if not username or not isinstance(username, str):
        raise ValueError("Username must be a non-empty string")
    
    try:
        headers = get_auth_headers()
    except ValueError as e:
        rprint(f"[yellow]Warning: Running unauthenticated. {str(e)}[/yellow]")
        headers = {
            'User-Agent': 'GitHub-Activity-CLI/1.0',
            'Accept': 'application/vnd.github.v3+json'
        }
        
    url = f"https://api.github.com/users/{username}/events"
    
    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError(f"User '{username}' not found")
        elif e.code == 401:
            raise ValueError("Invalid GitHub credentials")
        elif e.code == 403:
            raise ValueError("API rate limit exceeded. Try authenticating with GitHub credentials.")
        raise

def format_event(event: Dict) -> Optional[str]:
    """Format a GitHub event into a human-readable string.
    
    Args:
        event: GitHub event dictionary
        
    Returns:
        Formatted string describing the event, or None if event type not supported
    """
    event_type = event['type']
    repo = event['repo']['name']
    created_at = datetime.fromisoformat(event['created_at'].replace('Z', '+00:00'))
    
    if event_type == 'PushEvent':
        commits = event['payload'].get('commits', [])
        return f"Pushed {len(commits)} commit(s) to {repo}"
    elif event_type == 'IssuesEvent':
        action = event['payload']['action']
        issue_number = event['payload']['issue']['number']
        return f"{action.capitalize()} issue #{issue_number} in {repo}"
    elif event_type == 'WatchEvent':
        return f"Starred {repo}"
    elif event_type == 'CreateEvent':
        ref_type = event['payload']['ref_type']
        return f"Created {ref_type} in {repo}"
    elif event_type == 'PullRequestEvent':
        action = event['payload']['action']
        pr_number = event['payload']['pull_request']['number']
        return f"{action.capitalize()} pull request #{pr_number} in {repo}"
    
    return None

class GitHubActivity:
    """CLI tool to display GitHub user activity."""
    
    def show(self, username: str) -> None:
        """Display recent GitHub activity for a user.
        
        Args:
            username: GitHub username to fetch activity for
        """
        try:
            with console.status(f"Fetching activity for {username}...", spinner="dots"):
                events = fetch_github_events(username)
            
            if not events:
                rprint(f"[yellow]No recent activity found for user '{username}'[/yellow]")
                return
                
            table = Table(title=f"Recent GitHub Activity for {username}")
            table.add_column("Event", style="cyan")
            table.add_column("Date", style="green")
            
            for event in events[:10]:  # Show last 10 events
                formatted_event = format_event(event)
                if formatted_event:
                    created_at = datetime.fromisoformat(event['created_at'].replace('Z', '+00:00'))
                    table.add_row(
                        formatted_event,
                        created_at.strftime("%Y-%m-%d %H:%M:%S")
                    )
            
            console.print(table)
            
        except ValueError as e:
            rprint(f"[red]Error:[/red] {str(e)}")
        except urllib.error.HTTPError as e:
            rprint(f"[red]API Error:[/red] {str(e)}")
        except Exception as e:
            rprint(f"[red]Unexpected error:[/red] {str(e)}")

def main():
    """Entry point for the CLI."""
    fire.Fire(GitHubActivity)

if __name__ == '__main__':
    main() 