from django.db.models.manager import Manager


class VlogManager(Manager):
    """custom manager for Vlog model"""

    def all_vlogs(self, owner = None):
        all_vlogs = self.get_queryset()
        if owner:
            all_vlogs = all_vlogs.filter(uploaded_by=owner)
        return all_vlogs
