from rolepermissions.roles import AbstractUserRole

class Author(AbstractUserRole):
    available_permissions = {
        'upload_media': True
    }

class Specialist(AbstractUserRole):
    available_permissions = {
        'metadata_edit_content': True
    }

class Curator(AbstractUserRole):
    available_permissions = {
        'enable_author_profile': True,
        'enable_specialist_profile': True,
        'disable_author_profile': True,
        'disable_specialist_profile': True,
        'review_content': True,
        'publish_content': True,
        'create_tours': True
    }