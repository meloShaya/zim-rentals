from django import forms
from .models import Listing, ListingImage, RoommateProfile, SavedSearch
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, ButtonHolder, Div

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ListingForm(forms.ModelForm):
    images = MultipleFileField(
        required=False,
        help_text="Upload up to 4 images (optional)"
    )

    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'price', 'city', 'suburb', 'address',
            'property_type', 'bedrooms', 'bathrooms', 'is_furnished',
            'has_water', 'has_electricity', 'has_wifi', 'phone_number',
            'whatsapp_number', 'featured_image', 'latitude', 'longitude'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g +263XXXXXXXXX'}),
            'whatsapp_number': forms.TextInput(attrs={'placeholder': 'e.g +263XXXXXXXXX'}),
            'latitude': forms.TextInput(attrs={'placeholder': 'e.g -17.821239 (optional, but recommended for map view)'}),
            'longitude': forms.TextInput(attrs={'placeholder': 'e.g 31.046922 (optional, but recommended for map view)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Basic Information',
                Row(
                    Column('title', css_class='form-group col-md-6 mb-0'),
                    Column('property_type', css_class='form-group col-md-6 mb-0'),
                ),
                'description',
            ),
            Fieldset(
                'Location Details',
                Row(
                    Column('city', css_class='form-group col-md-6 mb-0'),
                    Column('suburb', css_class='form-group col-md-6 mb-0'),
                ),
                'address',
                Row(
                    Column('latitude', css_class='form-group col-md-6 mb-0'),
                    Column('longitude', css_class='form-group col-md-6 mb-0'),
                ),
            ),
            Fieldset(
                'Property Details',
                Row(
                    Column('bedrooms', css_class='form-group col-md-4 mb-0'),
                    Column('bathrooms', css_class='form-group col-md-4 mb-0'),
                    Column('is_furnished', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('has_water', css_class='form-group col-md-4 mb-0'),
                    Column('has_electricity', css_class='form-group col-md-4 mb-0'),
                    Column('has_wifi', css_class='form-group col-md-4 mb-0'),
                ),
            ),
            Fieldset(
                'Contact Information',
                Row(
                    Column('phone_number', css_class='form-group col-md-6 mb-0'),
                    Column('whatsapp_number', css_class='form-group col-md-6 mb-0'),
                ),
            ),
            Fieldset(
                'Images',
                'featured_image',
                'images',
            ),
            ButtonHolder(
                Submit('submit', 'Save Listing', css_class='btn-primary')
            )
        )

    def clean_images(self):
        images = self.files.getlist('images')
        if len(images) > 4:
            raise forms.ValidationError("You can upload a maximum of 4 images.")
        return images

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            # Delete existing images if any
            instance.images.all().delete()
            # Save new images
            for image in self.cleaned_data.get('images', []):
                ListingImage.objects.create(listing=instance, image=image)
        return instance

class RoommateProfileForm(forms.ModelForm):
    class Meta:
        model = RoommateProfile
        exclude = ['user', 'created_at', 'updated_at', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'suburb': forms.TextInput(attrs={'class': 'form-control'}),
            'min_budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'move_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lifestyle': forms.Select(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'preferences': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_smoker': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_pets': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SavedSearchForm(forms.ModelForm):
    class Meta:
        model = SavedSearch
        exclude = ['user', 'created_at', 'last_sent_at', 'is_active']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Search Criteria',
                'name',
                Row(
                    Column('city', css_class='form-group col-md-6 mb-0'),
                    Column('suburb', css_class='form-group col-md-6 mb-0'),
                ),
                Row(
                    Column('property_type', css_class='form-group col-md-4 mb-0'),
                    Column('min_price', css_class='form-group col-md-4 mb-0'),
                    Column('max_price', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('bedrooms', css_class='form-group col-md-6 mb-0'),
                    Column('bathrooms', css_class='form-group col-md-6 mb-0'),
                ),
                'is_furnished',
            ),
            ButtonHolder(
                Submit('submit', 'Save Search Alert', css_class='btn-primary')
            )
        )
        
        # Add help texts
        self.fields['name'].help_text = "Give your search a name to easily identify it"
        self.fields['min_price'].help_text = "Minimum price (optional)"
        self.fields['max_price'].help_text = "Maximum price (optional)"
        self.fields['suburb'].help_text = "Enter a suburb name (optional)"
        
        # Make fields optional
        for field in self.fields:
            if field != 'name':  # Name is required
                self.fields[field].required = False 

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-control mb-2'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Your Email', 'class': 'form-control mb-2'})
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Subject', 'class': 'form-control mb-2'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Your Message', 'rows': 5, 'class': 'form-control mb-3'})
    ) 