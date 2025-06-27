from rest_framework import viewsets

from rest_framework import generics, permissions, status
from .models import Subject
from .serializers import SubjectSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = (permissions.AllowAny,)
