from django import forms
from .models import Dossier, Client, Commentaire, PiecesJointes


class DossierForm(forms.ModelForm):
    class Meta:
        model = Dossier
        fields = ('titre', 'description', 'client', 'categorie',
                  'statut', 'priorite', 'responsable', 'date_echeance')
        widgets = {
            'date_echeance': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        # Les agents ne peuvent pas changer le responsable
        if user and user.is_agent:
            self.fields.pop('responsable', None)
            self.fields.pop('statut', None)


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('nom', 'email', 'telephone', 'adresse', 'notes')
        widgets = {'adresse': forms.Textarea(attrs={'rows': 3}),
                   'notes': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ('contenu',)
        widgets = {'contenu': forms.Textarea(attrs={'rows': 3, 'class': 'form-control',
                                                     'placeholder': 'Ajouter un commentaire...'})}


class PieceJointeForm(forms.ModelForm):
    class Meta:
        model = PiecesJointes
        fields = ('fichier', 'nom')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
