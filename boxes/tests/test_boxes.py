import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from boxes.models import Box

User = get_user_model()


@pytest.mark.django_db
class TestPastBoxesView:

    def setup_method(self):
        """
        Sets up test data for each test.
        """
        self.client = Client()
        self.user = User.objects.create(
            username="testuser",
            email="testuser@example.com"
        )
        self.client.force_login(self.user)
        # Create archived and non-archived boxes
        self.archived_box_1 = Box.objects.create(
            name="Archived Box 1",
            description="First archived box.",
            shipping_date=timezone.now().date(),
            is_archived=True
        )
        self.archived_box_2 = Box.objects.create(
            name="Archived Box 2",
            description="Second archived box.",
            shipping_date=timezone.now().date(),
            is_archived=True
        )
        self.active_box = Box.objects.create(
            name="Active Box",
            description="This one is still active.",
            shipping_date=timezone.now().date(),
            is_archived=False
        )

    def test_past_boxes_view_success(self):
        """
        Test the past boxes view renders correctly and shows only archived
        boxes.
        """
        response = self.client.get(reverse('past_boxes'))
        assert response.status_code == 200
        assert "Archived Box 1" in response.content.decode()
        assert "Archived Box 2" in response.content.decode()
        assert "Active Box" not in response.content.decode()
        assert "boxes/past_boxes.html" in [t.name for t in response.templates]

    def test_past_boxes_view_no_archived_boxes(self):
        """
        Test that the past boxes view handles no archived boxes gracefully.
        """
        Box.objects.filter(is_archived=True).delete()
        response = self.client.get(reverse('past_boxes'))
        assert response.status_code == 200
        assert (
            "No past boxes available yet — check back soon!"
            in response.content.decode()
        )


@pytest.mark.django_db
class TestBoxDetailView:

    def setup_method(self):
        """
        Sets up test data for each test.
        """
        self.client = Client()
        self.user = User.objects.create(
            username="testuser",
            email="testuser@example.com"
        )
        self.client.force_login(self.user)
        self.box = Box.objects.create(
            name="Detail Box",
            description="This is a box for detail view.",
            shipping_date=timezone.now().date(),
            is_archived=True
        )

    def test_box_detail_view_success(self):
        """
        Test that the box detail view displays correctly.
        """
        response = self.client.get(reverse('box_detail', args=[self.box.slug]))
        assert response.status_code == 200
        assert "Detail Box" in response.content.decode()
        assert "This is a box for detail view." in response.content.decode()
        assert "boxes/box_detail.html" in [t.name for t in response.templates]

    def test_box_detail_view_not_found(self):
        """
        Test that the box detail view returns 404 for a non-existing slug.
        """
        response = self.client.get(
            reverse('box_detail', args=['non-existent-slug'])
        )
        assert response.status_code == 404
