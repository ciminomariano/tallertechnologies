# models.py
from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid

class CreditCard(models.Model):
    card_number = models.CharField(max_length=16)
    expiration_date = models.DateField()
    security_code = models.CharField(max_length=3)
    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='credit_cards')
    
    def __str__(self):
        return f"**** **** **** {self.card_number[-4:]}"

class User(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    default_credit_card = models.OneToOneField(
        CreditCard, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='default_for_user'
    )
    friends = models.ManyToManyField('self', blank=True, symmetrical=True)
    
    def __str__(self):
        return self.username
    
    def add_credit_card(self, card_number, expiration_date, security_code):
        credit_card = CreditCard.objects.create(
            card_number=card_number,
            expiration_date=expiration_date,
            security_code=security_code,
            owner=self
        )
        if not self.default_credit_card:
            self.default_credit_card = credit_card
            self.save()
        return credit_card
    
    def add_friend(self, friend):
        """Add another user as a friend."""
        if friend != self:  # Prevent adding self as friend
            self.friends.add(friend)
            # Create an activity record for adding a friend
            Activity.objects.create(
                actor=self,
                target=friend,
                action_type='friend',
                amount=None,
                description=None
            )
            return True
        return False
    
    def pay(self, target_user, amount, description):
        """Pay another user."""
        # Ensure amount is a Decimal
        amount = Decimal(str(amount))  # Convert to string first to avoid float precision issues
        
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        if not isinstance(target_user, User):
            raise ValueError("Target must be a valid user")
        
        # Check if user has enough balance
        if self.balance >= amount:
            # Use balance
            self.balance = Decimal(str(self.balance)) - amount
            target_user.balance = Decimal(str(target_user.balance)) + amount
            self.save()
            target_user.save()
            
            payment_method = "balance"
        else:
            # Use credit card
            if not self.default_credit_card:
                raise ValueError("No credit card available for payment")
                
            # Charge credit card (in a real app, this would involve payment processor integration)
            # For this example, we'll just simulate a credit card charge
            payment_method = "credit card"
            
            # Update target user's balance
            target_user.balance = Decimal(str(target_user.balance)) + amount
            target_user.save()
        
        # Create activity record
        activity = Activity.objects.create(
            actor=self,
            target=target_user,
            action_type='payment',
            amount=amount,
            description=description
        )
        
        return activity
    
    def retrieve_activity(self, limit=10):
        """Retrieve user's activity including payments and friend additions."""
        # Get activities where user is actor or target
        activities = Activity.objects.filter(
            models.Q(actor=self) | models.Q(target=self)
        ).order_by('-created_at')[:limit]
        
        return activities

class Activity(models.Model):
    ACTION_TYPES = [
        ('payment', 'Payment'),
        ('friend', 'Friend Addition'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities_as_actor')
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities_as_target')
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        if self.action_type == 'payment':
            return f"{self.actor} paid {self.target} ${self.amount} for {self.description}"
        elif self.action_type == 'friend':
            return f"{self.actor} added {self.target} as a friend"
        return f"Activity {self.id}"