from rolepermissions.roles import AbstractUserRole

class Author(AbstractUserRole):
    available_permissions = {
        'upload_media': True
    }