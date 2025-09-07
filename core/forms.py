from django import forms

class ProductAddForm(forms.Form):
    name = forms.CharField(label="Product name", max_length=255)
    pid  = forms.CharField(label="Flipkart PID", max_length=64, help_text="e.g. PSLERGUYC4UNKHKG")
    # If you later want URL-based scraping, add:
    # url = forms.URLField(label="Flipkart Product Reviews URL", required=False)
