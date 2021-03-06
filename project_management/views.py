from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from project_management.permissions import (IsProjectContributor,
                                            IsProjectCreator,
                                            IsAuthor,
                                            IsIssueInProject)

from project_management.models import (Project,
                                        User,
                                        Contributor,
                                        Issue,
                                        Comment)
from project_management.serializer import (ProjectSerializer,
                                            ProjectSimpleSerializer,
                                            ProjectDetailsSerializer,
                                            ContributorSerializer,
                                            ContributorCreateSerializer,
                                            IssueSerializer,
                                            IssueCreateSerializer,
                                            CommentSerializer,
                                            CommentDetailsSerializer,
                                            CommentCreateSerializer)


class ProjectViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """ /projects/ """

    def get_permissions(self):
        permission_classes = [IsAuthenticated]

        if self.action == 'retrieve':
            permission_classes.append(IsProjectContributor)
        elif self.action == 'update' or self.action == 'destroy':
            permission_classes.append(IsProjectContributor)
            permission_classes.append(IsProjectCreator)

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        contribs = Contributor.objects.filter(user=self.request.user)
        return Project.objects.filter(contributor__in=contribs)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectSimpleSerializer

        elif self.action == 'retrieve':
            return ProjectDetailsSerializer

        else:
            return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save()

        # Creator's creation
        new_contributor = Contributor(user=self.request.user,
                                      project=Project.objects.last(),
                                      permission=Contributor.Permission.CREATOR)
        new_contributor.save()

    def perform_destroy(self, instance):
        # Also delete all project's contributors
        contributors = Contributor.objects.filter(project=instance)
        for c in contributors:
            c.delete()

        # Issues and comments are deleted in cascade
        instance.delete()


class ProjectUserViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """ /projects/<id>/users/ """

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsProjectContributor]
        if self.action == 'create' or self.action == 'destroy':
            permission_classes.append(IsProjectCreator)

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Contributor.objects.filter(project=self.kwargs['project_pk'])

    def get_serializer_class(self):
        if self.action == 'list':
            return ContributorSerializer
        else:
            return ContributorCreateSerializer

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['project'] = kwargs['project_pk']
        request.data['permission'] = Contributor.Permission.CONTRIBUTOR

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['project_pk'])
        user_to_delete = get_object_or_404(User, pk=kwargs['pk'])
        contributor = get_object_or_404(Contributor, user=user_to_delete, project=project)

        # Prevent creator deletion
        if contributor.permission == Contributor.Permission.CREATOR:
            return Response(data="Project's creator can't be delete", status=status.HTTP_403_FORBIDDEN)
        else:
            # Delete all user's comments and issues
            for comment in Comment.objects.filter(issue__project=project, author=user_to_delete):
                comment.delete()

            for issue in Issue.objects.filter(project=project, author=user_to_delete):
                issue.delete()

            contributor.delete()
            return Response(data='Contributor removed', status=status.HTTP_204_NO_CONTENT)


class IssueViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """ /projects/<id>/issues/ """

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsProjectContributor]
        if self.action == 'update' or self.action == 'destroy':
            permission_classes.append(IsAuthor)

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Issue.objects.filter(project=self.kwargs['project_pk'])

    def get_serializer_class(self):
        if self.action == 'list':
            return IssueSerializer
        else:
            return IssueCreateSerializer

    def perform_create(self, serializer):
        # 'Assigned user' has to be a contributor
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        if Contributor.objects.filter(project=project, user=serializer.validated_data['assigned']):
            serializer.save(project=project, author=self.request.user)
        else:
            raise ValidationError("Assigned user has to be a project's contributor")


class CommentViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """ /projects/<id>/issues/<id>/comments/ """

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsIssueInProject, IsProjectContributor]
        if self.action == 'update' or self.action == 'destroy':
            permission_classes.append(IsAuthor)

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Comment.objects.filter(issue=self.kwargs['issue_pk'])

    def get_serializer_class(self):
        if self.action == 'list':
            return CommentSerializer
        elif self.action == 'retrieve':
            return CommentDetailsSerializer
        else:
            return CommentCreateSerializer

    def perform_create(self, serializer):
        issue = get_object_or_404(Issue, pk=self.kwargs['issue_pk'])
        serializer.save(issue=issue, author=self.request.user)
