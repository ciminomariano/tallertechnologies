# tests.py
from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from .models import User, CreditCard, Activity
from .mini_venmo import MiniVenmo

class MiniVenmoTests(TestCase):
    def setUp(self):
        # Create test users
        self.user_alice = MiniVenmo.create_user("Alice", "alice123")
        self.user_bob = MiniVenmo.create_user("Bob", "bob456")
        self.user_carol = MiniVenmo.create_user("Carol", "carol789")
        
        # Add credit cards
        self.alice_cc = self.user_alice.add_credit_card(
            "1234567890123456", 
            timezone.now().date() + timedelta(days=365), 
            "123"
        )
        self.bob_cc = self.user_bob.add_credit_card(
            "9876543210987654", 
            timezone.now().date() + timedelta(days=365), 
            "456"
        )
        
        # Add initial balance to Alice
        self.user_alice.balance = Decimal('100.00')
        self.user_alice.save()

    def test_create_user(self):
        """Test user creation"""
        self.assertEqual(self.user_alice.name, "Alice")
        self.assertEqual(self.user_alice.username, "alice123")
        self.assertEqual(self.user_alice.balance, Decimal('100.00'))
        
        # Test duplicate username
        with self.assertRaises(ValueError):
            MiniVenmo.create_user("Another Alice", "alice123")

    def test_add_credit_card(self):
        """Test adding a credit card"""
        self.assertEqual(self.user_alice.default_credit_card, self.alice_cc)
        self.assertEqual(str(self.alice_cc), "**** **** **** 3456")

    def test_payment_using_balance(self):
        """Test payment using user's balance"""
        # Alice pays Bob $50 (should use balance)
        activity = self.user_alice.pay(self.user_bob, 50, "Dinner")
        
        # Check balances
        self.user_alice.refresh_from_db()
        self.user_bob.refresh_from_db()
        self.assertEqual(self.user_alice.balance, Decimal('50.00'))
        self.assertEqual(self.user_bob.balance, Decimal('50.00'))
        
        # Check activity record
        self.assertEqual(activity.actor, self.user_alice)
        self.assertEqual(activity.target, self.user_bob)
        self.assertEqual(activity.amount, Decimal('50.00'))
        self.assertEqual(activity.description, "Dinner")

    def test_payment_using_credit_card(self):
        """Test payment using user's credit card when balance is insufficient"""
        # Bob pays Alice $200 (should use credit card)
        activity = self.user_bob.pay(self.user_alice, 200, "Rent")
        
        # Check balances
        self.user_alice.refresh_from_db()
        self.user_bob.refresh_from_db()
        self.assertEqual(self.user_bob.balance, Decimal('0.00'))  # Balance unchanged
        self.assertEqual(self.user_alice.balance, Decimal('300.00'))  # Alice received payment
        
        # Check activity record
        self.assertEqual(activity.actor, self.user_bob)
        self.assertEqual(activity.target, self.user_alice)
        self.assertEqual(activity.amount, Decimal('200.00'))
        self.assertEqual(activity.description, "Rent")

    def test_payment_without_balance_or_card(self):
        """Test payment fails when no balance and no credit card"""
        # Remove Bob's credit card
        self.user_bob.default_credit_card = None
        self.user_bob.save()
        
        # Bob attempts to pay without enough balance and no card
        with self.assertRaises(ValueError):
            self.user_bob.pay(self.user_alice, 50, "Failed payment")

    def test_add_friend(self):
        """Test adding a friend"""
        result = self.user_alice.add_friend(self.user_bob)
        self.assertTrue(result)
        
        # Check friendship is established
        self.assertIn(self.user_bob, self.user_alice.friends.all())
        self.assertIn(self.user_alice, self.user_bob.friends.all())
        
        # Check activity was created
        activity = Activity.objects.filter(
            actor=self.user_alice, 
            target=self.user_bob,
            action_type='friend'
        ).first()
        self.assertIsNotNone(activity)

    def test_cannot_add_self_as_friend(self):
        """Test that a user cannot add themselves as a friend"""
        result = self.user_alice.add_friend(self.user_alice)
        self.assertFalse(result)
        
        # Check no friendship was established
        self.assertNotIn(self.user_alice, self.user_alice.friends.all())

    def test_retrieve_activity(self):
        """Test retrieving a user's activity"""
        # Create some activities
        self.user_alice.pay(self.user_bob, 25, "Coffee")
        self.user_bob.pay(self.user_alice, 75, "Lunch")
        self.user_alice.add_friend(self.user_carol)
        
        # Retrieve Alice's activity
        activities = self.user_alice.retrieve_activity()
        
        # Should have 3 activities
        self.assertEqual(activities.count(), 3)
        
        # First activity should be the friend addition (most recent)
        self.assertEqual(activities[0].action_type, 'friend')

    def test_render_feed(self):
        """Test rendering the activity feed"""
        # Add a credit card for Carol first
        self.carol_cc = self.user_carol.add_credit_card(
            "1234123412341234", 
            timezone.now().date() + timedelta(days=365), 
            "789"
        )
        
        # Create some activities
        self.user_alice.pay(self.user_bob, 5, "Coffee")
        self.user_carol.pay(self.user_bob, 15, "Lunch")
        self.user_bob.add_friend(self.user_carol)
        
        # Render feed
        feed = MiniVenmo.render_feed()
        
        # Check feed contents
        self.assertEqual(len(feed), 3)
        self.assertEqual(feed[2], "Alice paid Bob $5.00 for Coffee")
        self.assertEqual(feed[1], "Carol paid Bob $15.00 for Lunch")
        self.assertEqual(feed[0], "Bob added Carol as a friend")