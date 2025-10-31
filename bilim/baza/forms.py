from django import forms
from .models import Savol

class TestForm(forms.Form):
    def init(self, *args, **kwargs):
        super(TestForm, self).init(*args, **kwargs)
        savollar = Savol.objects.prefetch_related("javoblar").all()
        for savol in savollar:
            self.fields[f"savol_{savol.id}"] = forms.ChoiceField(
                label=savol.matn,
                choices=[(j.id, j.matn) for j in savol.javoblar.all()],
                widget=forms.RadioSelect
            )