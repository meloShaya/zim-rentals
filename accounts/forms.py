from django import forms
from django.contrib.auth import get_user_model, authenticate
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, ButtonHolder, Div, HTML
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from allauth.account.forms import LoginForm, SignupForm
from django.utils.translation import gettext_lazy as _
from .models import LandlordVerification

User = get_user_model()

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = 'Email or Username'
        self.fields['login'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your email or username'
        })
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'login',
            'password',
            ButtonHolder(
                Submit('submit', 'Login', css_class='btn-primary btn-block')
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        login = cleaned_data.get('login')
        password = cleaned_data.get('password')
        
        if login and password:
            # Try to authenticate with username
            self.user_cache = authenticate(self.request, username=login, password=password)
            
            # If authentication with username fails, try with email
            if self.user_cache is None:
                try:
                    user = User.objects.get(email=login)
                    self.user_cache = authenticate(self.request, username=user.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if self.user_cache is None:
                raise ValidationError(
                    "Please enter a correct email/username and password. Note that both fields may be case-sensitive."
                )
            
            if not self.user_cache.is_active:
                raise ValidationError("This account is inactive.")
        
        return cleaned_data

class CustomSignupForm(SignupForm):
    user_type = forms.ChoiceField(
        choices=User.USER_TYPES,
        widget=forms.RadioSelect,
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        # The request is passed as a separate parameter, not an attribute
        self.request = kwargs.get('request')
        super().__init__(*args, **kwargs)
        
        # Check if user_type is provided in the request's GET parameters
        if self.request and hasattr(self.request, 'GET') and 'user_type' in self.request.GET:
            requested_type = self.request.GET.get('user_type')
            # Validate that the requested type is a valid choice
            valid_types = [choice[0] for choice in User.USER_TYPES]
            if requested_type in valid_types:
                self.initial['user_type'] = requested_type
        
        # Add better help text for email field
        self.fields['email'].help_text = "A valid email address. This will be used for account verification."
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Account Information',
                'username',
                'email',
                'password1',
                'password2',
            ),
            Fieldset(
                'User Type',
                'user_type',
            ),
            ButtonHolder(
                Submit('submit', 'Sign Up', css_class='btn-primary btn-block')
            )
        )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if len(username) < 3:
                raise ValidationError(
                    _('Username must be at least 3 characters long.'),
                    code='username_too_short'
                )
            if not username.isalnum():
                raise ValidationError(
                    _('Username can only contain letters and numbers.'),
                    code='username_invalid'
                )
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if a user with this email already exists
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError(
                    _('An account with this email address already exists. Please use a different email or log in.'),
                    code='email_exists'
                )
        return email
    
    def save(self, request):
        user = super().save(request)
        user.user_type = self.cleaned_data['user_type']
        user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'profile_picture', 'bio']
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': '+263...'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Personal Information',
                Row(
                    Column('first_name', css_class='form-group col-md-6 mb-0'),
                    Column('last_name', css_class='form-group col-md-6 mb-0'),
                ),
                'phone_number',
                'profile_picture',
                'bio',
            ),
            ButtonHolder(
                Submit('submit', 'Update Profile', css_class='btn-primary')
            )
        )

class LandlordVerificationForm(forms.ModelForm):
    class Meta:
        model = LandlordVerification
        fields = ['document', 'document_type', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any additional information that might help with verification'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add help text and validation messages
        self.fields['document'].help_text = 'Upload a clear copy of your ID or property ownership documents (PDF, JPG, PNG formats only, max 5MB)'
        self.fields['document'].widget.attrs.update({'accept': '.pdf,.jpg,.jpeg,.png'})
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML("""
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>Landlord Verification:</strong> Upload your ID or proof of property ownership. 
                    Our team will review your documents and verify your account within 2-3 business days.
                </div>
            """),
            Fieldset(
                'Verification Documents',
                'document_type',
                'document',
                'notes',
            ),
            ButtonHolder(
                Submit('submit', 'Submit for Verification', css_class='btn-primary')
            )
        )
    
    def clean_document(self):
        document = self.cleaned_data.get('document')
        if document:
            # Get file extension
            ext = document.name.split('.')[-1].lower()
            
            # Validate file type
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise ValidationError('Only PDF, JPG, and PNG files are allowed.')
            
            # Validate file size (5MB max)
            if document.size > 5 * 1024 * 1024:
                raise ValidationError('File size must be no more than 5MB.')
        
        return document
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        
        if commit:
            instance.save()
        
        return instance
 