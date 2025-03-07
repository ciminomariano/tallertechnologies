
from mini_venmo.models import User, Activity 

class MiniVenmo:
    @staticmethod
    def create_user(name, username):
        """Create a new user for the app."""
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            raise ValueError(f"Username '{username}' is already taken")
            
        # Create and return new user
        user = User.objects.create(
            name=name,
            username=username,
            balance=0.00
        )
        return user
    
    @staticmethod
    def render_feed(limit=20):
        """Render the activity feed."""
        activities = Activity.objects.all().order_by('-created_at')[:limit]
        feed_items = []
        
        for activity in activities:
            if activity.action_type == 'payment':
                feed_items.append(
                    f"{activity.actor.name} paid {activity.target.name} ${activity.amount:.2f} for {activity.description}"
                )
            elif activity.action_type == 'friend':
                feed_items.append(
                    f"{activity.actor.name} added {activity.target.name} as a friend"
                )
                
        return feed_items