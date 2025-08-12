from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    DeliveryPartner, DeliveryJob, JobAssignment, 
    DeliveryTracking, PartnerEarnings
)
from .serializers import (
    DeliveryPartnerSerializer, DeliveryJobSerializer, JobAssignmentSerializer,
    DeliveryTrackingSerializer, PartnerEarningsSerializer
)
from user.models import UserRole

User = get_user_model()


class DeliveryPartnerModelTest(TestCase):
    """Test cases for DeliveryPartner model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='partner@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role=UserRole.DELIVERY_PARTNER
        )
        
        self.partner = DeliveryPartner.objects.create(
            user=self.user,
            partner_type='individual',
            status='active',
            phone_number='9876543210',
            address_line1='123 Test Street',
            city='Mumbai',
            state='Maharashtra',
            postal_code='400001',
            vehicle_type='bike',
            vehicle_number='MH01AB1234',
            service_areas=['400001', '400002', '400003'],
            max_delivery_distance=10.0,
            is_available=True,
            working_days=[0, 1, 2, 3, 4, 5],  # Monday to Saturday
            commission_rate=10.0
        )
    
    def test_delivery_partner_creation(self):
        """Test delivery partner creation."""
        self.assertEqual(self.partner.partner_code[:2], 'DP')
        self.assertEqual(self.partner.user, self.user)
        self.assertEqual(self.partner.status, 'active')
        self.assertEqual(self.partner.is_available, True)
    
    def test_get_success_rate(self):
        """Test success rate calculation."""
        self.partner.total_deliveries = 10
        self.partner.successful_deliveries = 8
        self.partner.save()
        
        self.assertEqual(self.partner.get_success_rate(), 80.0)
    
    def test_get_success_rate_zero_deliveries(self):
        """Test success rate when no deliveries."""
        self.assertEqual(self.partner.get_success_rate(), 0.0)
    
    def test_is_working_now(self):
        """Test working status check."""
        # Set working hours
        self.partner.available_from = datetime.strptime('09:00', '%H:%M').time()
        self.partner.available_to = datetime.strptime('18:00', '%H:%M').time()
        self.partner.save()
        
        # Should return True during working hours
        self.assertTrue(self.partner.is_working_now())
    
    def test_update_location(self):
        """Test location update."""
        latitude = Decimal('19.0760')
        longitude = Decimal('72.8777')
        
        self.partner.update_location(latitude, longitude)
        
        self.assertEqual(self.partner.current_latitude, latitude)
        self.assertEqual(self.partner.current_longitude, longitude)
        self.assertIsNotNone(self.partner.last_location_update)
    
    def test_can_accept_job(self):
        """Test job acceptance capability."""
        # Create a test job
        customer = User.objects.create_user(
            email='customer@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            role=UserRole.CUSTOMER
        )
        
        job = DeliveryJob.objects.create(
            customer=customer,
            customer_name='Jane Smith',
            customer_phone='9876543211',
            customer_email='customer@test.com',
            pickup_address='123 Pickup Street',
            pickup_pincode='400001',
            pickup_city='Mumbai',
            pickup_state='Maharashtra',
            delivery_address='456 Delivery Street',
            delivery_pincode='400002',
            delivery_city='Mumbai',
            delivery_state='Maharashtra',
            package_description='Test Package',
            package_weight=Decimal('1.5'),
            package_value=Decimal('100.00'),
            pickup_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=1),
            base_fare=Decimal('50.00')
        )
        
        self.assertTrue(self.partner.can_accept_job(job))
    
    def test_cannot_accept_job_outside_service_area(self):
        """Test job rejection when outside service area."""
        customer = User.objects.create_user(
            email='customer2@test.com',
            password='testpass123',
            first_name='Bob',
            last_name='Johnson',
            role=UserRole.CUSTOMER
        )
        
        job = DeliveryJob.objects.create(
            customer=customer,
            customer_name='Bob Johnson',
            customer_phone='9876543212',
            customer_email='customer2@test.com',
            pickup_address='123 Pickup Street',
            pickup_pincode='500001',  # Outside service area
            pickup_city='Hyderabad',
            pickup_state='Telangana',
            delivery_address='456 Delivery Street',
            delivery_pincode='500002',
            delivery_city='Hyderabad',
            delivery_state='Telangana',
            package_description='Test Package',
            package_weight=Decimal('1.5'),
            package_value=Decimal('100.00'),
            pickup_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=1),
            base_fare=Decimal('50.00')
        )
        
        self.assertFalse(self.partner.can_accept_job(job))


class DeliveryJobModelTest(TestCase):
    """Test cases for DeliveryJob model."""
    
    def setUp(self):
        """Set up test data."""
        self.customer = User.objects.create_user(
            email='customer@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            role=UserRole.CUSTOMER
        )
        
        self.partner = DeliveryPartner.objects.create(
            user=User.objects.create_user(
                email='partner@test.com',
                password='testpass123',
                first_name='John',
                last_name='Doe',
                role=UserRole.DELIVERY_PARTNER
            ),
            partner_type='individual',
            status='active',
            phone_number='9876543210',
            address_line1='123 Test Street',
            city='Mumbai',
            state='Maharashtra',
            postal_code='400001',
            vehicle_type='bike',
            vehicle_number='MH01AB1234',
            service_areas=['400001', '400002'],
            max_delivery_distance=10.0,
            is_available=True,
            commission_rate=10.0
        )
        
        self.job = DeliveryJob.objects.create(
            customer=self.customer,
            customer_name='Jane Smith',
            customer_phone='9876543211',
            customer_email='customer@test.com',
            job_type='pickup_and_delivery',
            status='pending',
            priority='normal',
            pickup_address='123 Pickup Street',
            pickup_pincode='400001',
            pickup_city='Mumbai',
            pickup_state='Maharashtra',
            delivery_address='456 Delivery Street',
            delivery_pincode='400002',
            delivery_city='Mumbai',
            delivery_state='Maharashtra',
            package_description='Test Package',
            package_weight=Decimal('1.5'),
            package_value=Decimal('100.00'),
            pickup_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=1),
            base_fare=Decimal('50.00'),
            distance_fare=Decimal('10.00'),
            priority_fare=Decimal('5.00')
        )
    
    def test_delivery_job_creation(self):
        """Test delivery job creation."""
        self.assertEqual(self.job.job_id[:2], 'DJ')
        self.assertEqual(self.job.tracking_number[:3], 'TRK')
        self.assertEqual(self.job.status, 'pending')
        self.assertEqual(self.job.total_fare, Decimal('65.00'))  # 50 + 10 + 5
    
    def test_assign_to_partner(self):
        """Test job assignment to partner."""
        self.job.assign_to_partner(self.partner)
        
        self.assertEqual(self.job.assigned_partner, self.partner)
        self.assertEqual(self.job.status, 'assigned')
        self.assertIsNotNone(self.job.assigned_at)
    
    def test_accept_by_partner(self):
        """Test job acceptance by partner."""
        self.job.assign_to_partner(self.partner)
        self.job.accept_by_partner()
        
        self.assertEqual(self.job.status, 'accepted')
        self.assertIsNotNone(self.job.accepted_at)
    
    def test_reject_by_partner(self):
        """Test job rejection by partner."""
        self.job.assign_to_partner(self.partner)
        self.job.reject_by_partner('Too far from current location')
        
        self.assertEqual(self.job.status, 'rejected')
        self.assertIsNotNone(self.job.rejected_at)
        self.assertEqual(self.job.rejection_reason, 'Too far from current location')
        self.assertIsNone(self.job.assigned_partner)
    
    def test_mark_as_picked_up(self):
        """Test marking job as picked up."""
        self.job.mark_as_picked_up()
        
        self.assertEqual(self.job.status, 'picked_up')
        self.assertIsNotNone(self.job.actual_pickup_time)
    
    def test_mark_as_delivered(self):
        """Test marking job as delivered."""
        self.job.assign_to_partner(self.partner)
        self.job.mark_as_delivered()
        
        self.assertEqual(self.job.status, 'delivered')
        self.assertIsNotNone(self.job.actual_delivery_time)
        self.assertEqual(self.partner.successful_deliveries, 1)
        self.assertEqual(self.partner.total_deliveries, 1)
    
    def test_mark_as_failed(self):
        """Test marking job as failed."""
        self.job.assign_to_partner(self.partner)
        self.job.mark_as_failed('Customer not available')
        
        self.assertEqual(self.job.status, 'failed')
        self.assertEqual(self.partner.failed_deliveries, 1)
        self.assertEqual(self.partner.total_deliveries, 1)
    
    def test_get_distance(self):
        """Test distance calculation."""
        self.job.pickup_latitude = Decimal('19.0760')
        self.job.pickup_longitude = Decimal('72.8777')
        self.job.delivery_latitude = Decimal('19.2183')
        self.job.delivery_longitude = Decimal('72.9781')
        self.job.save()
        
        distance = self.job.get_distance()
        self.assertGreater(distance, 0)
        self.assertIsInstance(distance, float)


class JobAssignmentModelTest(TestCase):
    """Test cases for JobAssignment model."""
    
    def setUp(self):
        """Set up test data."""
        self.customer = User.objects.create_user(
            email='customer@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            role=UserRole.CUSTOMER
        )
        
        self.partner = DeliveryPartner.objects.create(
            user=User.objects.create_user(
                email='partner@test.com',
                password='testpass123',
                first_name='John',
                last_name='Doe',
                role=UserRole.DELIVERY_PARTNER
            ),
            partner_type='individual',
            status='active',
            phone_number='9876543210',
            address_line1='123 Test Street',
            city='Mumbai',
            state='Maharashtra',
            postal_code='400001',
            vehicle_type='bike',
            vehicle_number='MH01AB1234',
            service_areas=['400001', '400002'],
            max_delivery_distance=10.0,
            is_available=True,
            commission_rate=10.0
        )
        
        self.job = DeliveryJob.objects.create(
            customer=self.customer,
            customer_name='Jane Smith',
            customer_phone='9876543211',
            customer_email='customer@test.com',
            pickup_address='123 Pickup Street',
            pickup_pincode='400001',
            pickup_city='Mumbai',
            pickup_state='Maharashtra',
            delivery_address='456 Delivery Street',
            delivery_pincode='400002',
            delivery_city='Mumbai',
            delivery_state='Maharashtra',
            package_description='Test Package',
            package_weight=Decimal('1.5'),
            package_value=Decimal('100.00'),
            pickup_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=1),
            base_fare=Decimal('50.00')
        )
        
        self.assignment = JobAssignment.objects.create(
            job=self.job,
            partner=self.partner,
            status='pending'
        )
    
    def test_job_assignment_creation(self):
        """Test job assignment creation."""
        self.assertEqual(self.assignment.job, self.job)
        self.assertEqual(self.assignment.partner, self.partner)
        self.assertEqual(self.assignment.status, 'pending')
        self.assertIsNotNone(self.assignment.expires_at)
    
    def test_is_expired(self):
        """Test expiration check."""
        # Set expiry to past
        self.assignment.expires_at = timezone.now() - timedelta(minutes=1)
        self.assignment.save()
        
        self.assertTrue(self.assignment.is_expired())
    
    def test_accept_assignment(self):
        """Test assignment acceptance."""
        estimated_pickup_time = timezone.now() + timedelta(hours=1)
        estimated_delivery_time = timezone.now() + timedelta(hours=3)
        
        success = self.assignment.accept_assignment(
            estimated_pickup_time=estimated_pickup_time,
            estimated_delivery_time=estimated_delivery_time,
            partner_notes='Will pickup on time'
        )
        
        self.assertTrue(success)
        self.assertEqual(self.assignment.status, 'accepted')
        self.assertIsNotNone(self.assignment.responded_at)
        self.assertEqual(self.job.status, 'accepted')
    
    def test_reject_assignment(self):
        """Test assignment rejection."""
        success = self.assignment.reject_assignment('Too far from current location')
        
        self.assertTrue(success)
        self.assertEqual(self.assignment.status, 'rejected')
        self.assertIsNotNone(self.assignment.responded_at)
        self.assertEqual(self.job.status, 'rejected')


class DeliveryPartnerSerializerTest(TestCase):
    """Test cases for DeliveryPartner serializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='partner@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role=UserRole.DELIVERY_PARTNER
        )
        
        self.partner = DeliveryPartner.objects.create(
            user=self.user,
            partner_type='individual',
            status='active',
            phone_number='9876543210',
            address_line1='123 Test Street',
            city='Mumbai',
            state='Maharashtra',
            postal_code='400001',
            vehicle_type='bike',
            vehicle_number='MH01AB1234',
            service_areas=['400001', '400002'],
            max_delivery_distance=10.0,
            is_available=True,
            commission_rate=10.0
        )
    
    def test_delivery_partner_serializer(self):
        """Test delivery partner serializer."""
        serializer = DeliveryPartnerSerializer(self.partner)
        data = serializer.data
        
        self.assertEqual(data['partner_code'], self.partner.partner_code)
        self.assertEqual(data['status'], 'active')
        self.assertEqual(data['phone_number'], '9876543210')
        self.assertEqual(data['vehicle_number'], 'MH01AB1234')
        self.assertIn('user', data)
        self.assertIn('success_rate', data)
        self.assertIn('is_working_now', data)
    
    def test_delivery_partner_validation(self):
        """Test delivery partner validation."""
        invalid_data = {
            'phone_number': '123',  # Too short
            'vehicle_number': 'AB',  # Too short
            'service_areas': 'not_a_list',  # Not a list
            'working_days': [8, 9]  # Invalid days
        }
        
        serializer = DeliveryPartnerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)
        self.assertIn('vehicle_number', serializer.errors)
        self.assertIn('service_areas', serializer.errors)
        self.assertIn('working_days', serializer.errors)


class DeliveryPartnerAPITest(APITestCase):
    """Test cases for DeliveryPartner API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role=UserRole.ADMIN,
            is_staff=True
        )
        
        # Create delivery partner user
        self.partner_user = User.objects.create_user(
            email='partner@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role=UserRole.DELIVERY_PARTNER
        )
        
        # Create customer user
        self.customer_user = User.objects.create_user(
            email='customer@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            role=UserRole.CUSTOMER
        )
        
        # Create delivery partner
        self.partner = DeliveryPartner.objects.create(
            user=self.partner_user,
            partner_type='individual',
            status='active',
            phone_number='9876543210',
            address_line1='123 Test Street',
            city='Mumbai',
            state='Maharashtra',
            postal_code='400001',
            vehicle_type='bike',
            vehicle_number='MH01AB1234',
            service_areas=['400001', '400002'],
            max_delivery_distance=10.0,
            is_available=True,
            commission_rate=10.0
        )
    
    def test_list_delivery_partners_authenticated(self):
        """Test listing delivery partners when authenticated."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('delivery_partners:delivery-partner-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_list_delivery_partners_unauthenticated(self):
        """Test listing delivery partners when unauthenticated."""
        url = reverse('delivery_partners:delivery-partner-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_delivery_partner(self):
        """Test retrieving a specific delivery partner."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('delivery_partners:delivery-partner-detail', args=[self.partner.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['partner_code'], self.partner.partner_code)
    
    def test_create_delivery_partner(self):
        """Test creating a new delivery partner."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('delivery_partners:delivery-partner-list')
        
        data = {
            'user_id': str(self.partner_user.id),
            'partner_type': 'individual',
            'phone_number': '9876543211',
            'address_line1': '456 New Street',
            'city': 'Delhi',
            'state': 'Delhi',
            'postal_code': '110001',
            'vehicle_type': 'scooter',
            'vehicle_number': 'DL01CD5678',
            'service_areas': ['110001', '110002'],
            'max_delivery_distance': 15.0,
            'commission_rate': 12.0
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('data', response.data)
    
    def test_update_delivery_partner(self):
        """Test updating a delivery partner."""
        self.client.force_authenticate(user=self.partner_user)
        url = reverse('delivery_partners:delivery-partner-detail', args=[self.partner.id])
        
        data = {
            'phone_number': '9876543212',
            'city': 'Pune'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.partner.refresh_from_db()
        self.assertEqual(self.partner.phone_number, '9876543212')
        self.assertEqual(self.partner.city, 'Pune')
    
    def test_update_location(self):
        """Test updating delivery partner location."""
        self.client.force_authenticate(user=self.partner_user)
        url = reverse('delivery_partners:delivery-partner-update-location', args=[self.partner.id])
        
        data = {
            'latitude': '19.0760',
            'longitude': '72.8777'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.partner.refresh_from_db()
        self.assertEqual(str(self.partner.current_latitude), '19.0760')
        self.assertEqual(str(self.partner.current_longitude), '72.8777')
    
    def test_update_availability(self):
        """Test updating delivery partner availability."""
        self.client.force_authenticate(user=self.partner_user)
        url = reverse('delivery_partners:delivery-partner-update-availability', args=[self.partner.id])
        
        data = {
            'is_available': False,
            'available_from': '09:00:00',
            'available_to': '18:00:00',
            'working_days': [0, 1, 2, 3, 4]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.partner.refresh_from_db()
        self.assertFalse(self.partner.is_available)
    
    def test_dashboard(self):
        """Test delivery partner dashboard."""
        self.client.force_authenticate(user=self.partner_user)
        url = reverse('delivery_partners:delivery-partner-dashboard', args=[self.partner.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertIn('partner', response.data['data'])
        self.assertIn('active_jobs', response.data['data'])
        self.assertIn('pending_assignments', response.data['data'])
        self.assertIn('recent_earnings', response.data['data'])


class DeliveryJobAPITest(APITestCase):
    """Test cases for DeliveryJob API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create users
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role=UserRole.ADMIN,
            is_staff=True
        )
        
        self.customer_user = User.objects.create_user(
            email='customer@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            role=UserRole.CUSTOMER
        )
        
        self.partner_user = User.objects.create_user(
            email='partner@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role=UserRole.DELIVERY_PARTNER
        )
        
        # Create delivery partner
        self.partner = DeliveryPartner.objects.create(
            user=self.partner_user,
            partner_type='individual',
            status='active',
            phone_number='9876543210',
            address_line1='123 Test Street',
            city='Mumbai',
            state='Maharashtra',
            postal_code='400001',
            vehicle_type='bike',
            vehicle_number='MH01AB1234',
            service_areas=['400001', '400002'],
            max_delivery_distance=10.0,
            is_available=True,
            commission_rate=10.0
        )
        
        # Create delivery job
        self.job = DeliveryJob.objects.create(
            customer=self.customer_user,
            customer_name='Jane Smith',
            customer_phone='9876543211',
            customer_email='customer@test.com',
            job_type='pickup_and_delivery',
            status='pending',
            priority='normal',
            pickup_address='123 Pickup Street',
            pickup_pincode='400001',
            pickup_city='Mumbai',
            pickup_state='Maharashtra',
            delivery_address='456 Delivery Street',
            delivery_pincode='400002',
            delivery_city='Mumbai',
            delivery_state='Maharashtra',
            package_description='Test Package',
            package_weight=Decimal('1.5'),
            package_value=Decimal('100.00'),
            pickup_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=1),
            base_fare=Decimal('50.00')
        )
    
    def test_list_delivery_jobs_customer(self):
        """Test listing delivery jobs as customer."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('delivery_partners:delivery-job-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_list_delivery_jobs_partner(self):
        """Test listing delivery jobs as partner."""
        self.client.force_authenticate(user=self.partner_user)
        url = reverse('delivery_partners:delivery-job-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_create_delivery_job(self):
        """Test creating a new delivery job."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('delivery_partners:delivery-job-list')
        
        data = {
            'customer_id': str(self.customer_user.id),
            'job_type': 'pickup_and_delivery',
            'priority': 'normal',
            'customer_name': 'Jane Smith',
            'customer_phone': '9876543211',
            'customer_email': 'customer@test.com',
            'pickup_address': '789 Pickup Street',
            'pickup_pincode': '400003',
            'pickup_city': 'Mumbai',
            'pickup_state': 'Maharashtra',
            'delivery_address': '012 Delivery Street',
            'delivery_pincode': '400004',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'package_description': 'New Package',
            'package_weight': '2.0',
            'package_value': '150.00',
            'pickup_date': (timezone.now().date() + timedelta(days=1)).isoformat(),
            'delivery_date': (timezone.now().date() + timedelta(days=2)).isoformat(),
            'base_fare': '60.00'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('data', response.data)
    
    def test_update_job_status(self):
        """Test updating job status."""
        self.job.assign_to_partner(self.partner)
        self.client.force_authenticate(user=self.partner_user)
        url = reverse('delivery_partners:delivery-job-update-status', args=[self.job.id])
        
        data = {
            'status': 'picked_up',
            'latitude': '19.0760',
            'longitude': '72.8777',
            'location_address': '123 Pickup Street, Mumbai',
            'notes': 'Package picked up successfully'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'picked_up')
    
    def test_assign_partner_to_job(self):
        """Test assigning partner to job."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('delivery_partners:delivery-job-assign-partner', args=[self.job.id])
        
        data = {
            'partner_id': str(self.partner.id)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.assigned_partner, self.partner)
        self.assertEqual(self.job.status, 'assigned')


class JobAssignmentAPITest(APITestCase):
    """Test cases for JobAssignment API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create users
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role=UserRole.ADMIN,
            is_staff=True
        )
        
        self.partner_user = User.objects.create_user(
            email='partner@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role=UserRole.DELIVERY_PARTNER
        )
        
        self.customer_user = User.objects.create_user(
            email='customer@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            role=UserRole.CUSTOMER
        )
        
        # Create delivery partner
        self.partner = DeliveryPartner.objects.create(
            user=self.partner_user,
            partner_type='individual',
            status='active',
            phone_number='9876543210',
            address_line1='123 Test Street',
            city='Mumbai',
            state='Maharashtra',
            postal_code='400001',
            vehicle_type='bike',
            vehicle_number='MH01AB1234',
            service_areas=['400001', '400002'],
            max_delivery_distance=10.0,
            is_available=True,
            commission_rate=10.0
        )
        
        # Create delivery job
        self.job = DeliveryJob.objects.create(
            customer=self.customer_user,
            customer_name='Jane Smith',
            customer_phone='9876543211',
            customer_email='customer@test.com',
            pickup_address='123 Pickup Street',
            pickup_pincode='400001',
            pickup_city='Mumbai',
            pickup_state='Maharashtra',
            delivery_address='456 Delivery Street',
            delivery_pincode='400002',
            delivery_city='Mumbai',
            delivery_state='Maharashtra',
            package_description='Test Package',
            package_weight=Decimal('1.5'),
            package_value=Decimal('100.00'),
            pickup_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=1),
            base_fare=Decimal('50.00')
        )
        
        # Create job assignment
        self.assignment = JobAssignment.objects.create(
            job=self.job,
            partner=self.partner,
            status='pending'
        )
    
    def test_list_job_assignments_partner(self):
        """Test listing job assignments as partner."""
        self.client.force_authenticate(user=self.partner_user)
        url = reverse('delivery_partners:job-assignment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_respond_to_assignment_accept(self):
        """Test accepting job assignment."""
        self.client.force_authenticate(user=self.partner_user)
        url = reverse('delivery_partners:job-assignment-respond', args=[self.assignment.id])
        
        data = {
            'action': 'accept',
            'estimated_pickup_time': (timezone.now() + timedelta(hours=1)).isoformat(),
            'estimated_delivery_time': (timezone.now() + timedelta(hours=3)).isoformat(),
            'partner_notes': 'Will pickup on time'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, 'accepted')
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'accepted')
    
    def test_respond_to_assignment_reject(self):
        """Test rejecting job assignment."""
        self.client.force_authenticate(user=self.partner_user)
        url = reverse('delivery_partners:job-assignment-respond', args=[self.assignment.id])
        
        data = {
            'action': 'reject',
            'rejection_reason': 'Too far from current location'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, 'rejected')
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'rejected')
    
    def test_pending_assignments(self):
        """Test getting pending assignments."""
        self.client.force_authenticate(user=self.partner_user)
        url = reverse('delivery_partners:job-assignment-pending')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
