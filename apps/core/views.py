from rest_framework.viewsets import ViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action

from apps.blogs.permissions.is_authenticated import IsAuthenticated
from apps.core.serializers import TrainingSerializer

from utils.core_utils import TrainingUtil
from utils.response_utils import ResponseManager


class TrainingViewSet(ViewSet):
    authentication_classes = (IsAuthenticated,)
    permission_classes = ()

    def list(self, request):
        user = request.user
        trainings = TrainingUtil.list_trainings(
            user, request.query_params
        )
        serializer = TrainingSerializer(trainings, many=True)
        return ResponseManager


class Dashboard(ViewSet):

    @action(methods=["get"], detail=False, url_path="dashboard")
    def get_dashboard_data(self, request):
        pass
