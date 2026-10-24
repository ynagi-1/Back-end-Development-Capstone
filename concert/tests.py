from unittest.mock import Mock, patch
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Concert, ConcertAttending


class ConcertFlowTests(TestCase):
    def setUp(self):
        self.concert = Concert.objects.create(
            concert_name="Djirection Live", duration=3,
            city="Astana", date="2027-04-14")
        self.user = User.objects.create_user("listener", password="test-pass-123")

    def test_anonymous_users_cannot_rsvp(self):
        response = self.client.post(reverse("concert_attendee"), {
            "concert_id": self.concert.pk, "attendee_choice": "Attending"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        self.assertEqual(ConcertAttending.objects.count(), 0)

    def test_rsvp_updates_one_record_and_is_scoped_to_user(self):
        self.client.force_login(self.user)
        payload = {"concert_id": self.concert.pk, "attendee_choice": "Attending"}
        self.client.post(reverse("concert_attendee"), payload)
        payload["attendee_choice"] = "Not Attending"
        self.client.post(reverse("concert_attendee"), payload)
        self.assertEqual(ConcertAttending.objects.count(), 1)
        self.assertEqual(ConcertAttending.objects.get().attending, "Not Attending")
        other = User.objects.create_user("another-listener")
        self.client.force_login(other)
        self.assertContains(self.client.get(reverse("concerts")), "Djirection Live")
        self.assertEqual(self.client.get(reverse("concerts")).context["concerts"][0]["status"], "-")

    def test_invalid_rsvp_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("concert_attendee"), {
            "concert_id": self.concert.pk, "attendee_choice": "invalid"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ConcertAttending.objects.count(), 0)

    def test_signup_hashes_password_and_rejects_duplicate_username(self):
        data = {"username": "new-listener", "password1": "course-test-123", "password2": "course-test-123"}
        self.assertRedirects(self.client.post(reverse("signup"), data), reverse("index"))
        user = User.objects.get(username="new-listener")
        self.assertTrue(user.check_password(data["password1"]))
        self.assertNotEqual(user.password, data["password1"])
        self.client.post(reverse("signup"), data)
        self.assertEqual(User.objects.filter(username="new-listener").count(), 1)

    def test_login_and_post_logout(self):
        self.assertRedirects(self.client.post(reverse("login"), {
            "username": "listener", "password": "test-pass-123"}), reverse("index"))
        self.assertEqual(self.client.get(reverse("concerts")).status_code, 200)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.client.post(reverse("logout"))
        self.assertEqual(self.client.get(reverse("concerts")).status_code, 302)

    @patch("concert.views.requests.get")
    def test_songs_accept_service_envelope_and_display_lyrics(self, get):
        get.return_value = Mock(json=lambda: {"songs": [{"id": 1, "title": "Live Song", "lyrics": "A test verse"}]})
        response = self.client.get(reverse("songs"))
        self.assertContains(response, "Live Song")
        self.assertContains(response, "A test verse")

    @patch("concert.views.requests.get")
    def test_photos_accept_picture_array(self, get):
        get.return_value = Mock(json=lambda: [{"id": 1, "pic_url": "https://example.com/show.jpg", "event_city": "Astana"}])
        self.assertContains(self.client.get(reverse("photos")), "https://example.com/show.jpg")
