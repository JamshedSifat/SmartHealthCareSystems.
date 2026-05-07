
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import DoctorReview, Doctor


@receiver(post_save, sender=DoctorReview)
def update_doctor_rating_on_save(sender, instance, created, **kwargs):
    """Update doctor rating when review is added"""
    doctor = instance.doctor
    
    # Calculate average rating
    avg_rating = doctor.reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Update doctor
    doctor.average_rating = avg_rating or 0
    doctor.total_reviews = doctor.reviews.count()
    doctor.save(update_fields=['average_rating', 'total_reviews'])
    
    print(f"✅ {doctor.name} rating updated: {avg_rating}")


@receiver(post_delete, sender=DoctorReview)
def update_doctor_rating_on_delete(sender, instance, **kwargs):
    """Update doctor rating when review is deleted"""
    doctor = instance.doctor
    
    # Calculate new average
    avg_rating = doctor.reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Update doctor
    doctor.average_rating = avg_rating or 0
    doctor.total_reviews = doctor.reviews.count()
    doctor.save(update_fields=['average_rating', 'total_reviews'])
    
    print(f"✅ {doctor.name} rating updated (deleted): {avg_rating}")
