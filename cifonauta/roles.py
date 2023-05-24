from rolepermissions.roles import AbstractUserRole

class Author(AbstractUserRole):
    available_permissions = {
        'upload_media': True
    }

class Specialist(AbstractUserRole):
    available_permissions = {
        'metadata_edit_content': True
    }