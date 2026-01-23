import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import LoyaltyAccount, LoyaltyTransaction, SagaMilesAward

class LoyaltyServiceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.award_miles_url = reverse('award_miles')
        self.reverse_miles_url = reverse('reverse_miles')
        self.user_id = "test_user"
        self.correlation_id = "test_correlation"
        self.flight_fare = 200

        # Create a loyalty account
        self.account = LoyaltyAccount.objects.create(user_id=self.user_id, points_balance=100)

    def test_award_miles(self):
        """Test awarding miles for a booking"""
        data = {
            "correlation_id": self.correlation_id,
            "booking_data": {
                "user_id": self.user_id,
                "flight_fare": self.flight_fare
            }
        }
        response = self.client.post(self.award_miles_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))
        self.assertEqual(LoyaltyTransaction.objects.count(), 1)
        self.assertEqual(SagaMilesAward.objects.count(), 1)
        self.assertEqual(LoyaltyAccount.objects.get(user_id=self.user_id).points_balance, 300)

    def test_reverse_miles(self):
        """Test reversing awarded miles"""
        # Award miles first
        SagaMilesAward.objects.create(
            correlation_id=self.correlation_id,
            account=self.account,
            miles_awarded=self.flight_fare,
            original_balance=self.account.points_balance,
            new_balance=self.account.points_balance + self.flight_fare,
            status="AWARDED"
        )
        self.account.points_balance += self.flight_fare
        self.account.save()

        # Reverse miles
        data = {
            "correlation_id": self.correlation_id
        }
        response = self.client.post(self.reverse_miles_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))
        self.assertEqual(LoyaltyTransaction.objects.count(), 1)
        self.assertEqual(SagaMilesAward.objects.get(correlation_id=self.correlation_id).status, "REVERSED")
        self.assertEqual(LoyaltyAccount.objects.get(user_id=self.user_id).points_balance, 100)