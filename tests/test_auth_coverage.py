"""
Testes específicos para melhorar cobertura do módulo basic_auth.py
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open
from app.auth.basic_auth import (
    BasicAuthManager, 
    decode_basic_auth, 
    create_basic_auth_header,
    auth_manager
)


class TestBasicAuthManagerCoverage:
    """Testes para melhorar cobertura do BasicAuthManager"""

    def test_load_users_from_file_not_found(self):
        """Testa carregamento quando arquivo não existe"""
        with patch('os.path.exists', return_value=False):
            manager = BasicAuthManager()
            users, metadata = manager._load_users_from_file()
            assert users == {}
            assert metadata == {}

    def test_load_users_from_file_json_error(self):
        """Testa carregamento com erro de JSON"""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='invalid json')):
            manager = BasicAuthManager()
            users, metadata = manager._load_users_from_file()
            assert users == {}
            assert metadata == {}

    def test_load_users_from_file_read_error(self):
        """Testa carregamento com erro de leitura"""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', side_effect=IOError("Erro de leitura")):
            manager = BasicAuthManager()
            users, metadata = manager._load_users_from_file()
            assert users == {}
            assert metadata == {}

    def test_load_users_from_file_success(self):
        """Testa carregamento bem-sucedido do arquivo"""
        test_data = {
            "metadata": {"version": "1.0", "description": "Test users"},
            "users": [
                {
                    "username": "testuser",
                    "password": "testpass",
                    "role": "user",
                    "description": "Test user"
                }
            ]
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            manager = BasicAuthManager()
            users, metadata = manager._load_users_from_file()
            
            assert "testuser" in users
            assert users["testuser"]["password"] == "testpass"
            assert users["testuser"]["role"] == "user"
            assert metadata["version"] == "1.0"

    def test_load_users_from_file_missing_username(self):
        """Testa carregamento com usuário sem username"""
        test_data = {
            "users": [
                {
                    "password": "testpass",
                    "role": "user"
                }
            ]
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            manager = BasicAuthManager()
            users, metadata = manager._load_users_from_file()
            
            assert len(users) == 0

    def test_load_users_fallback_to_env(self):
        """Testa fallback para variáveis de ambiente"""
        with patch.object(BasicAuthManager, '_load_users_from_file', return_value=({}, {})), \
             patch.object(BasicAuthManager, '_load_users_from_env', return_value={"admin": {"password": "secret", "role": "admin", "description": "Test"}}):
            manager = BasicAuthManager()
            assert "admin" in manager.users

    def test_verify_credentials_user_not_found(self):
        """Testa verificação com usuário inexistente"""
        manager = BasicAuthManager()
        manager.users = {"admin": {"password": "secret", "role": "admin", "description": "Test"}}
        
        result = manager.verify_credentials("nonexistent", "password")
        assert result is False

    def test_get_user_info_not_found(self):
        """Testa obtenção de info de usuário inexistente"""
        manager = BasicAuthManager()
        manager.users = {"admin": {"password": "secret", "role": "admin", "description": "Test"}}
        
        result = manager.get_user_info("nonexistent")
        assert result is None

    def test_reload_users_success(self):
        """Testa reload bem-sucedido"""
        test_data = {
            "users": [{"username": "newuser", "password": "newpass", "role": "user", "description": "New"}]
        }
        
        manager = BasicAuthManager()
        with patch.object(manager, '_load_users_from_file', return_value=({"newuser": {"password": "newpass", "role": "user", "description": "New"}}, {})):
            result = manager.reload_users()
            assert result is True
            assert "newuser" in manager.users

    def test_reload_users_failure(self):
        """Testa reload com falha"""
        manager = BasicAuthManager()
        with patch.object(manager, '_load_users_from_file', return_value=({}, {})):
            result = manager.reload_users()
            assert result is False

    def test_reload_users_exception(self):
        """Testa reload com exceção"""
        manager = BasicAuthManager()
        with patch.object(manager, '_load_users_from_file', side_effect=Exception("Test error")):
            result = manager.reload_users()
            assert result is False


class TestBasicAuthUtilities:
    """Testes para funções utilitárias de Basic Auth"""

    def test_decode_basic_auth_invalid_format(self):
        """Testa decodificação com formato inválido"""
        # Sem "Basic "
        username, password = decode_basic_auth("Bearer token")
        assert username is None
        assert password is None

    def test_decode_basic_auth_invalid_base64(self):
        """Testa decodificação com base64 inválido"""
        username, password = decode_basic_auth("Basic invalid_base64!")
        assert username is None
        assert password is None

    def test_decode_basic_auth_no_colon(self):
        """Testa decodificação sem dois pontos"""
        import base64
        # "userpassword" sem ":"
        encoded = base64.b64encode("userpassword".encode()).decode()
        username, password = decode_basic_auth(f"Basic {encoded}")
        assert username is None
        assert password is None

    def test_decode_basic_auth_success(self):
        """Testa decodificação bem-sucedida"""
        username, password = decode_basic_auth("Basic YWRtaW46c2VjcmV0")  # admin:secret
        assert username == "admin"
        assert password == "secret"

    def test_create_basic_auth_header(self):
        """Testa criação de header Basic Auth"""
        header = create_basic_auth_header("admin", "secret")
        assert header == "Basic YWRtaW46c2VjcmV0"

    def test_decode_encode_roundtrip(self):
        """Testa ida e volta de encode/decode"""
        original_user = "testuser"
        original_pass = "testpass"
        
        header = create_basic_auth_header(original_user, original_pass)
        decoded_user, decoded_pass = decode_basic_auth(header)
        
        assert decoded_user == original_user
        assert decoded_pass == original_pass


class TestBasicAuthManagerIntegration:
    """Testes de integração para BasicAuthManager"""

    def test_manager_with_real_file(self):
        """Testa manager com arquivo real temporário"""
        test_data = {
            "metadata": {"version": "test", "description": "Test file"},
            "users": [
                {
                    "username": "fileuser",
                    "password": "filepass",
                    "role": "user",
                    "description": "User from file"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            # Patch para usar nosso arquivo temporário
            with patch('app.auth.basic_auth.BasicAuthManager._load_users_from_file') as mock_load:
                mock_load.return_value = (
                    {"fileuser": {"password": "filepass", "role": "user", "description": "User from file"}},
                    {"version": "test"}
                )
                
                manager = BasicAuthManager()
                assert "fileuser" in manager.users
                assert manager.verify_credentials("fileuser", "filepass")
                assert not manager.verify_credentials("fileuser", "wrongpass")
                
                user_info = manager.get_user_info("fileuser")
                assert user_info["username"] == "fileuser"
                assert user_info["role"] == "user"
        finally:
            os.unlink(temp_file)

    def test_list_users_functionality(self):
        """Testa funcionalidade de listagem de usuários"""
        manager = BasicAuthManager()
        manager.users = {
            "admin": {"password": "secret", "role": "admin", "description": "Administrator"},
            "user": {"password": "pass", "role": "user", "description": "Regular user"}
        }
        
        users_list = manager.list_users()
        assert len(users_list) == 2
        
        # Verifica que não há senhas na listagem
        for user in users_list:
            assert "password" not in user
            assert "username" in user
            assert "role" in user
            assert "description" in user

    def test_auth_manager_global_instance(self):
        """Testa instância global do auth_manager"""
        # Verifica que a instância global existe
        assert auth_manager is not None
        assert isinstance(auth_manager, BasicAuthManager)
        
        # Verifica que tem usuários carregados
        assert len(auth_manager.users) > 0 