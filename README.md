# MiniVenmo

MiniVenmo is a Django-based payment application that simulates basic Venmo functionality. Users can send payments to each other, add friends, and view a social feed of payment and friend activities.

## Features

- **User Management**: Create user accounts with individual balances.
- **Payment Processing**: Users can pay each other using their balance or credit card.
- **Credit Card Management**: Users can add credit cards for payment processing.
- **Friend System**: Users can add other users as friends.
- **Activity Feed**: View a social feed of payments and friend additions.

## System Architecture

### Models

#### User
- Stores user information (name, username).
- Tracks user balance.
- Maintains relationships with other users (friends).
- Links to credit cards.

#### CreditCard
- Stores credit card details.
- Links to the user account.

#### Activity
- Records all user activities (payments, friend additions).
- Maintains relationships between actors and targets.
- Contains metadata (amount, description, timestamp).

### Core Components

- **MiniVenmo**: Main application class with methods for user creation and feed rendering.
- **User**: Contains methods for payments and friend management.

## Installation

### Clone the Repository

git clone https://github.com/ciminomariano/tallertechnologies

### Create virtual enviroment and activate
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd mini-venmo

### Run migrations

python manage.py makemigrations
python manage.py migrate

### Run development server

python manage.py runserver





