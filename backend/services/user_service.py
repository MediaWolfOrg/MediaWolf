from db.user_db_handler import UserDBHandler
from logger import logger
from dataclasses import asdict
import bcrypt

class UserService:
    def __init__(self):
        self.user_db_handler = UserDBHandler() 

    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def get_all_users(self):
        """Fetch all users from the database."""
        users = self.user_db_handler.get_existing_user()
        return users
    
    def get_user_by_id(self, id):
        """Get user by ID"""
        user = self.user_db_handler.get_user_by_id(id)
        
        return user

    def update_user(self, data):
        """Update user from form on User Page"""
        user_id = data.get("id")
        old_user_data = self.user_db_handler.get_user_by_id(user_id)
    
        if not old_user_data:
            pass
    
        updates = {}
    
        for key, new_value in data.items():
            old_value = getattr(old_user_data, key, None)

            if key == "password":
                if not new_value:  # Skip password update if it's empty
                    continue
                new_value = self._hash_password(new_value)

            if new_value != old_value:  # Only update changed values
                updates[key] = new_value
    
        if updates:
            
            self.user_db_handler.update_user(user_id, updates)  # Apply changes
            return

    def create_user(self, data):
        username = data.get("name")
        password = data.get("password")
        role = data.get("role")

        hashed_password = self._hash_password(password)

        new_user = {
            "name": username,
            "password": hashed_password,
            "role": role
        }

        self.user_db_handler.create_user(new_user)


    def delete_user(self, user):
        self.user_db_handler.delete_user(user)