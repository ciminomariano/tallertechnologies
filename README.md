MiniVenmo
A Django-based payment application that simulates basic Venmo functionality. MiniVenmo allows users to send payments to each other, add friends, and view a social feed of payment and friend activities.
Features

User Management: Create user accounts with individual balances
Payment Processing: Users can pay each other using their balance or credit card
Credit Card Management: Users can add credit cards for payment processing
Friend System: Users can add other users as friends
Activity Feed: View a social feed of payments and friend additions

System Architecture
Models

User

Stores user information (name, username)
Tracks user balance
Maintains relationships with other users (friends)
Links to credit cards


CreditCard

Stores credit card details
Links to user account


Activity

Records all user activities (payments, friend additions)
Maintains relationship between actors and targets
Contains metadata (amount, description, timestamp)



Core Components

MiniVenmo: Main application class with methods for user creation and feed rendering
User: Contains methods for payments and friend management

Installation

Clone the repository:
Copygit clone [https://github.com/yourusername/mini-venmo.git](https://github.com/ciminomariano/tallertechnologies/tree/main)
cd mini-venmo

Create a virtual environment and activate it:
Copypython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:
Copypip install -r requirements.txt

Run migrations:
Copypython manage.py makemigrations
python manage.py migrate

Run the development server:
Copypython manage.py runserver


Usage
Creating Users
pythonCopyfrom mini_venmo import MiniVenmo

# Create new users
alice = MiniVenmo.create_user("Alice", "alice123")
bob = MiniVenmo.create_user("Bob", "bob456")
Adding Credit Cards
pythonCopyfrom django.utils import timezone
from datetime import timedelta

# Add a credit card for Alice
expiration_date = timezone.now().date() + timedelta(days=365)
alice.add_credit_card("1234567890123456", expiration_date, "123")
Making Payments
pythonCopy# Alice pays Bob $25 for lunch
alice.pay(bob, 25, "Lunch")
Adding Friends
pythonCopy# Alice adds Bob as a friend
alice.add_friend(bob)
Viewing Activities
pythonCopy# Get Alice's activities
activities = alice.retrieve_activity()

# Render feed of all activities
feed = MiniVenmo.render_feed()
for item in feed:
    print(item)
Testing
Run the unit tests:
Copypython manage.py test
The test suite covers:

User creation
Credit card management
Payment processing (using balance and credit card)
Friend addition
Activity feed rendering

Implementation Details
Payment Processing
When a user makes a payment:

The system first checks if the user has sufficient balance
If balance is sufficient, it's used for the payment
If balance is insufficient, the system charges the user's credit card
The recipient's balance is increased by the payment amount
An activity record is created

Activity Feed
The feed displays:

Payment transactions: "{payer} paid {recipient} ${amount} for {description}"
Friend additions: "{user} added {friend} as a friend"
