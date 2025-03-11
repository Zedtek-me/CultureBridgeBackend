from typing import Type, Optional, Union, List, Dict

from apps.core.models import Training

class TrainingUtil:
    """all things training utility"""

    @classmethod
    def create_training(cls, **kwargs) -> Type[Training]:
        training = Training.objects.create(**kwargs)
        return training

    @classmethod
    def list_trainings(self, user, filter_params):
        """
        """
