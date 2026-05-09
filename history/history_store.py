import time
import datetime

def get_analytics_summary():
    """
    Returns mock analytics data for the dashboard since the real history tracking 
    has not been implemented yet.
    """
    today = datetime.date.today()
    
    # Generate some dummy daily stats for the last 7 days
    daily_stats = []
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        daily_stats.append({
            "date": date.isoformat(),
            "count": 5 + (i * 2) # Fake trend
        })
        
    return {
        "total_commands": 42,
        "total_commits": 7,
        "total_file_changes": 15,
        "daily_stats": daily_stats,
        "recent_activity": [
            {
                "timestamp": time.time() * 1000,
                "type": "command_execution",
                "command": "ls -la"
            },
            {
                "timestamp": (time.time() - 3600) * 1000, # 1 hour ago
                "type": "git_commit",
                "command": "git commit -m 'Initial commit'"
            },
            {
                "timestamp": (time.time() - 7200) * 1000, # 2 hours ago
                "type": "command_execution",
                "command": "python test_redis.py"
            }
        ]
    }
