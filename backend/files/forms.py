from django import forms
from .models import Document, Category


class StyledFormMixin:
    """أضف form-control/form-select لكل الحقول تلقائيًا."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget
            # select
            if getattr(w, 'input_type', None) is None and w.__class__.__name__.lower().startswith('select'):
                css = w.attrs.get('class', '')
                if 'form-select' not in css:
                    w.attrs['class'] = (css + ' form-select').strip()
            # checkbox
            elif w.__class__.__name__.lower().startswith('checkbox'):
                css = w.attrs.get('class', '')
                if 'form-check-input' not in css:
                    w.attrs['class'] = (css + ' form-check-input').strip()
            else:
                css = w.attrs.get('class', '')
                if 'form-control' not in css:
                    w.attrs['class'] = (css + ' form-control').strip()


class DocumentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'category', 'owner_email',
                  'expires_on', 'alert_window_days', 'notes']
        widgets = {
            'expires_on': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class CategoryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']


class BulkImportForm(StyledFormMixin, forms.Form):
    file = forms.FileField(
        label='Excel/CSV file',
        help_text='Upload the unified template (.xlsx or .csv).',
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx,.csv'})
    )
    default_category = forms.ModelChoiceField(
        queryset=Category.objects.all(), required=False, empty_label='— No default —'
    )
    default_alert_window_days = forms.IntegerField(
        required=False, min_value=0, initial=7, help_text='Used if the sheet cell is empty.'
    )
    default_owner_email = forms.EmailField(
        required=False, help_text='Used if the sheet cell is empty.')
