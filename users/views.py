from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from .models import UserProfile
from .forms import UserCreateForm, UserUpdateForm, UserProfileUpdateForm
import logging

logger = logging.getLogger(__name__)


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_superuser or hasattr(user, 'profile') and user.profile.role == 'ADMIN')


@login_required
@user_passes_test(is_admin)
def user_list(request):
    """List all users"""
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'users/user_list.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def user_create(request):
    """Create a new user"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                logger.info(f"User {user.username} created by {request.user.username}")
                messages.success(request, f'User "{user.username}" created successfully!')
                return redirect('users:user_list')
            except Exception as e:
                logger.error(f"Error creating user: {e}")
                messages.error(request, 'An error occurred while creating the user.')
        else:
            logger.warning(f"Invalid user creation form: {form.errors}")
    else:
        form = UserCreateForm()
    
    return render(request, 'users/user_form.html', {
        'form': form,
        'action': 'Create'
    })


@login_required
@user_passes_test(is_admin)
def user_detail(request, pk):
    """View user details"""
    user = get_object_or_404(User.objects.select_related('profile'), pk=pk)
    return render(request, 'users/user_detail.html', {'view_user': user})


@login_required
@user_passes_test(is_admin)
@transaction.atomic
def user_update(request, pk):
    """Update user information"""
    user = get_object_or_404(User, pk=pk)
    
    # Ensure profile exists
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileUpdateForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                user_form.save()
                profile_form.save()
                logger.info(f"User {user.username} updated by {request.user.username}")
                messages.success(request, f'User "{user.username}" updated successfully!')
                return redirect('users:user_detail', pk=user.pk)
            except Exception as e:
                logger.error(f"Error updating user {user.username}: {e}")
                messages.error(request, 'An error occurred while updating the user.')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileUpdateForm(instance=profile)
    
    return render(request, 'users/user_update.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'view_user': user
    })


@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    """Delete a user"""
    user = get_object_or_404(User, pk=pk)
    
    # Prevent deleting yourself
    if user == request.user:
        messages.error(request, 'You cannot delete your own account!')
        return redirect('users:user_list')
    
    if request.method == 'POST':
        username = user.username
        try:
            user.delete()
            logger.info(f"User {username} deleted by {request.user.username}")
            messages.success(request, f'User "{username}" deleted successfully!')
            return redirect('users:user_list')
        except Exception as e:
            logger.error(f"Error deleting user {username}: {e}")
            messages.error(request, 'An error occurred while deleting the user.')
    
    return render(request, 'users/user_confirm_delete.html', {'view_user': user})


@login_required
def user_profile(request):
    """View and edit own profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileUpdateForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                user_form.save()
                profile_form.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('users:user_profile')
            except Exception as e:
                logger.error(f"Error updating profile for {request.user.username}: {e}")
                messages.error(request, 'An error occurred while updating your profile.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileUpdateForm(instance=profile)
    
    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })