from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from repositories.user_repository import UserRepository
from services.base import BaseService


def hash_password(password: str) -> str:
    # TODO: remplace par passlib / bcrypt
    return password


class UserService(BaseService):
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
        self.repository = repository

    def create_user(self, db: Session, data: dict):
        if self.repository.get_by_email(db, data['email']):
            raise HTTPException(status_code=400, detail='Email already exists')
        if self.repository.get_by_username(db, data['username']):
            raise HTTPException(status_code=400, detail='Username already exists')

        password = data.pop('password')
        data['password_hash'] = hash_password(password)
        return self.repository.create(db, data)

    def list_users(self, db: Session, skip: int = 0, limit: int = 100):
        return self.repository.get_all(db, skip=skip, limit=limit)

    def get_user(self, db: Session, user_id: UUID):
        return self.get_or_404(db, user_id, 'User not found')

    def update_user(self, db: Session, user_id: UUID, data: dict):
        db_obj = self.get_user(db, user_id)
        if 'email' in data:
            existing = self.repository.get_by_email(db, data['email'])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=400, detail='Email already exists')
        if 'username' in data:
            existing = self.repository.get_by_username(db, data['username'])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=400, detail='Username already exists')
        if 'password' in data:
            data['password_hash'] = hash_password(data.pop('password'))
        return self.repository.update(db, db_obj, data)

    def delete_user(self, db: Session, user_id: UUID) -> None:
        self.delete(db, user_id, 'User not found')
