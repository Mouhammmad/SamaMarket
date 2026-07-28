from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
import logging

from boutiques.models import Boutique
from commandes.models import Commande
from produits.models import Produit

from .serializers import SerializerVendeursEnAttente, SerializerUtilisateursRecents
import csv
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)
User = get_user_model()


def has_admin_access(user):
    if not getattr(user, 'is_authenticated', False):
        return False
    if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
        return True
    return str(getattr(user, 'role', '')).upper() == 'ADMIN'


class AllowOptionsPermission(BasePermission):
    """
    Allow OPTIONS requests without authentication for CORS preflight.
    """
    def has_permission(self, request, view):
        logger.debug(f"AllowOptionsPermission check: method={request.method}, user={request.user}, is_auth={request.user.is_authenticated if request.user else 'NO USER'}")
        return request.method == 'OPTIONS' or bool(request.user and request.user.is_authenticated)


class VueStatistiquesAdmin(APIView):

    permission_classes = [AllowOptionsPermission]

    def get(self, request):
        logger.debug(f"GET /stats called: user={request.user}, is_staff={request.user.is_staff}, is_auth={request.user.is_authenticated}")
        if not has_admin_access(request.user):
            return Response({'detail': 'Accès refusé.'}, status=403)
        today = timezone.now().date()
        start_month = today.replace(day=1)
        prev_month_end = start_month - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)

        utilisateurs_total = User.objects.count()
        nouveaux_utilisateurs_mois = User.objects.filter(date_joined__date__gte=start_month).count()
        vendeurs_actifs = Boutique.objects.filter(apprové=True).count()
        vendeurs_en_attente = Boutique.objects.filter(apprové=False).count()
        produits_total = Produit.objects.count()
        commandes_total = Commande.objects.count()
        commandes_du_jour = Commande.objects.filter(date_creation__date=today).count()
        commandes_ce_mois = Commande.objects.filter(date_creation__date__gte=start_month).count()
        commandes_mois_precedent = Commande.objects.filter(date_creation__date__gte=prev_month_start, date_creation__date__lte=prev_month_end).count()

        def pct_change(curr, prev):
            if prev == 0:
                return None
            return round((curr - prev) / prev * 100, 1)

        commandes_change_pct = pct_change(commandes_ce_mois, commandes_mois_precedent)

        donnees = {
            'utilisateurs_total': utilisateurs_total,
            'nouveaux_utilisateurs_ce_mois': nouveaux_utilisateurs_mois,
            'vendeurs_actifs': vendeurs_actifs,
            'vendeurs_en_attente': vendeurs_en_attente,
            'produits_total': produits_total,
            'commandes_total': commandes_total,
            'commandes_du_jour': commandes_du_jour,
            'commandes_ce_mois': commandes_ce_mois,
            'commandes_mois_precedent': commandes_mois_precedent,
            'commandes_change_pct': commandes_change_pct,
        }

        return Response(donnees)


class VueVendeursEnAttente(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not has_admin_access(request.user):
            return Response({'detail': 'Accès refusé.'}, status=403)
        vendeurs = Boutique.objects.filter(apprové=False)
        serializer = SerializerVendeursEnAttente(vendeurs, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not has_admin_access(request.user):
            return Response({'detail': 'Accès refusé.'}, status=403)

        boutique_id = request.data.get('boutique_id')
        approve = request.data.get('approve', True)
        boutique = Boutique.objects.filter(id=boutique_id).first()
        if boutique is None:
            return Response({'detail': 'Boutique introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        boutique.apprové = bool(approve)
        boutique.save(update_fields=['apprové'])
        return Response({'detail': 'Décision enregistrée.', 'approved': boutique.approuvé})


class VueUtilisateursRecents(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not has_admin_access(request.user):
            return Response({'detail': 'Accès refusé.'}, status=403)
        utilisateurs = User.objects.order_by('-date_joined')[:10]
        serializer = SerializerUtilisateursRecents(utilisateurs, many=True)
        return Response(serializer.data)


class VueExportCommandesAdmin(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only allow staff/admin users to export
        if not has_admin_access(request.user):
            return Response({'detail': 'Accès refusé.'}, status=403)

        commandes = Commande.objects.all().order_by('-date_creation')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="commandes_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['id', 'customer_username', 'customer_email', 'total_price', 'status', 'created_at', 'items'])

        for o in commandes:
            items = o.lignes.select_related('produit').all()
            items_summary = '; '.join([f"{it.produit.nom} x{it.quantite}" for it in items])
            writer.writerow([o.id, o.utilisateur.username, getattr(o.utilisateur, 'email', ''), str(o.montant_total), o.statut, o.date_creation.isoformat(), items_summary])

        return response