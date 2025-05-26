"""
Testes específicos para melhorar cobertura do serviço age_groups.py
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from bson import ObjectId
from app.services.age_groups import (
    create_age_group,
    get_age_group,
    get_all_age_groups,
    update_age_group,
    delete_age_group
)
from app.models.age_group import AgeGroupCreate, AgeGroupUpdate


class TestAgeGroupsServiceCoverage:
    """Testes para melhorar cobertura do serviço age_groups"""

    @pytest.mark.asyncio
    async def test_create_age_group_success(self):
        """Testa criação bem-sucedida de age group"""
        # Mock do MongoDB
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439011")
        mock_collection.insert_one.return_value = mock_result
        
        # Mock do documento criado
        created_doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "min_age": 18,
            "max_age": 25
        }
        mock_collection.find_one.return_value = created_doc
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            age_group_data = AgeGroupCreate(min_age=18, max_age=25)
            result = await create_age_group(age_group_data)
            
            # Verificações
            mock_collection.insert_one.assert_called_once_with({"min_age": 18, "max_age": 25})
            mock_collection.find_one.assert_called_once_with({"_id": mock_result.inserted_id})
            
            assert result["id"] == "507f1f77bcf86cd799439011"
            assert result["min_age"] == 18
            assert result["max_age"] == 25
            assert "_id" not in result

    @pytest.mark.asyncio
    async def test_get_age_group_found(self):
        """Testa busca de age group existente"""
        mock_collection = MagicMock()
        found_doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "min_age": 18,
            "max_age": 25
        }
        mock_collection.find_one.return_value = found_doc
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            result = await get_age_group("507f1f77bcf86cd799439011")
            
            # Verificações
            mock_collection.find_one.assert_called_once_with({"_id": ObjectId("507f1f77bcf86cd799439011")})
            
            assert result["id"] == "507f1f77bcf86cd799439011"
            assert result["min_age"] == 18
            assert result["max_age"] == 25
            assert "_id" not in result

    @pytest.mark.asyncio
    async def test_get_age_group_not_found(self):
        """Testa busca de age group inexistente"""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            result = await get_age_group("507f1f77bcf86cd799439011")
            
            # Verificações
            mock_collection.find_one.assert_called_once_with({"_id": ObjectId("507f1f77bcf86cd799439011")})
            assert result is None

    @pytest.mark.asyncio
    async def test_get_age_group_invalid_object_id(self):
        """Testa busca com ObjectId inválido"""
        mock_collection = MagicMock()
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            # ObjectId inválido deve gerar exceção
            with pytest.raises(Exception):  # bson.errors.InvalidId
                await get_age_group("invalid_id")

    @pytest.mark.asyncio
    async def test_get_all_age_groups_with_data(self):
        """Testa busca de todos os age groups com dados"""
        mock_collection = MagicMock()
        
        # Mock do cursor com múltiplos documentos
        mock_docs = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "min_age": 18, "max_age": 25},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "min_age": 26, "max_age": 35},
            {"_id": ObjectId("507f1f77bcf86cd799439013"), "min_age": 36, "max_age": 45}
        ]
        mock_collection.find.return_value = iter(mock_docs)
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            result = await get_all_age_groups()
            
            # Verificações
            mock_collection.find.assert_called_once()
            
            assert len(result) == 3
            
            # Verifica primeiro documento
            assert result[0]["id"] == "507f1f77bcf86cd799439011"
            assert result[0]["min_age"] == 18
            assert result[0]["max_age"] == 25
            assert "_id" not in result[0]
            
            # Verifica segundo documento
            assert result[1]["id"] == "507f1f77bcf86cd799439012"
            assert result[1]["min_age"] == 26
            assert result[1]["max_age"] == 35
            
            # Verifica terceiro documento
            assert result[2]["id"] == "507f1f77bcf86cd799439013"
            assert result[2]["min_age"] == 36
            assert result[2]["max_age"] == 45

    @pytest.mark.asyncio
    async def test_get_all_age_groups_empty(self):
        """Testa busca de todos os age groups sem dados"""
        mock_collection = MagicMock()
        mock_collection.find.return_value = iter([])  # Lista vazia
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            result = await get_all_age_groups()
            
            # Verificações
            mock_collection.find.assert_called_once()
            assert result == []

    @pytest.mark.asyncio
    async def test_update_age_group_success(self):
        """Testa atualização bem-sucedida de age group"""
        mock_collection = MagicMock()
        
        # Mock do resultado da atualização
        mock_update_result = MagicMock()
        mock_update_result.modified_count = 1
        mock_collection.update_one.return_value = mock_update_result
        
        # Mock do documento atualizado
        updated_doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "min_age": 20,
            "max_age": 30
        }
        mock_collection.find_one.return_value = updated_doc
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            age_group_update = AgeGroupUpdate(min_age=20, max_age=30)
            result = await update_age_group("507f1f77bcf86cd799439011", age_group_update)
            
            # Verificações
            mock_collection.update_one.assert_called_once_with(
                {"_id": ObjectId("507f1f77bcf86cd799439011")},
                {"$set": {"min_age": 20, "max_age": 30}}
            )
            mock_collection.find_one.assert_called_once_with({"_id": ObjectId("507f1f77bcf86cd799439011")})
            
            assert result["id"] == "507f1f77bcf86cd799439011"
            assert result["min_age"] == 20
            assert result["max_age"] == 30
            assert "_id" not in result

    @pytest.mark.asyncio
    async def test_update_age_group_not_modified(self):
        """Testa atualização de age group que não foi modificado"""
        mock_collection = MagicMock()
        
        # Mock do resultado da atualização (nenhum documento modificado)
        mock_update_result = MagicMock()
        mock_update_result.modified_count = 0
        mock_collection.update_one.return_value = mock_update_result
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            age_group_update = AgeGroupUpdate(min_age=20, max_age=30)
            result = await update_age_group("507f1f77bcf86cd799439011", age_group_update)
            
            # Verificações
            mock_collection.update_one.assert_called_once_with(
                {"_id": ObjectId("507f1f77bcf86cd799439011")},
                {"$set": {"min_age": 20, "max_age": 30}}
            )
            # find_one não deve ser chamado se modified_count == 0
            mock_collection.find_one.assert_not_called()
            
            assert result is None

    @pytest.mark.asyncio
    async def test_update_age_group_invalid_object_id(self):
        """Testa atualização com ObjectId inválido"""
        mock_collection = MagicMock()
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            age_group_update = AgeGroupUpdate(min_age=20, max_age=30)
            
            # ObjectId inválido deve gerar exceção
            with pytest.raises(Exception):  # bson.errors.InvalidId
                await update_age_group("invalid_id", age_group_update)

    @pytest.mark.asyncio
    async def test_delete_age_group_success(self):
        """Testa exclusão bem-sucedida de age group"""
        mock_collection = MagicMock()
        
        # Mock do resultado da exclusão
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 1
        mock_collection.delete_one.return_value = mock_delete_result
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            result = await delete_age_group("507f1f77bcf86cd799439011")
            
            # Verificações
            mock_collection.delete_one.assert_called_once_with({"_id": ObjectId("507f1f77bcf86cd799439011")})
            assert result == 1

    @pytest.mark.asyncio
    async def test_delete_age_group_not_found(self):
        """Testa exclusão de age group inexistente"""
        mock_collection = MagicMock()
        
        # Mock do resultado da exclusão (nenhum documento excluído)
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 0
        mock_collection.delete_one.return_value = mock_delete_result
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            result = await delete_age_group("507f1f77bcf86cd799439011")
            
            # Verificações
            mock_collection.delete_one.assert_called_once_with({"_id": ObjectId("507f1f77bcf86cd799439011")})
            assert result == 0

    @pytest.mark.asyncio
    async def test_delete_age_group_invalid_object_id(self):
        """Testa exclusão com ObjectId inválido"""
        mock_collection = MagicMock()
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            # ObjectId inválido deve gerar exceção
            with pytest.raises(Exception):  # bson.errors.InvalidId
                await delete_age_group("invalid_id")


class TestAgeGroupsServiceIntegration:
    """Testes de integração para o serviço age_groups"""

    @pytest.mark.asyncio
    async def test_create_and_get_age_group_flow(self):
        """Testa fluxo completo de criação e busca"""
        mock_collection = MagicMock()
        
        # Setup para create
        mock_insert_result = MagicMock()
        mock_insert_result.inserted_id = ObjectId("507f1f77bcf86cd799439011")
        mock_collection.insert_one.return_value = mock_insert_result
        
        # Mock para find_one - retorna documentos diferentes para cada chamada
        created_doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "min_age": 18,
            "max_age": 25
        }
        
        get_doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "min_age": 18,
            "max_age": 25
        }
        
        # Configura retornos diferentes para cada chamada
        mock_collection.find_one.side_effect = [created_doc, get_doc]
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            # Criar age group
            age_group_data = AgeGroupCreate(min_age=18, max_age=25)
            created = await create_age_group(age_group_data)
            
            # Buscar age group criado
            found = await get_age_group(created["id"])
            
            # Verificações
            assert created["id"] == found["id"]
            assert created["min_age"] == found["min_age"]
            assert created["max_age"] == found["max_age"]

    @pytest.mark.asyncio
    async def test_update_and_get_age_group_flow(self):
        """Testa fluxo completo de atualização e busca"""
        mock_collection = MagicMock()
        
        # Setup para update
        mock_update_result = MagicMock()
        mock_update_result.modified_count = 1
        mock_collection.update_one.return_value = mock_update_result
        
        # Mock para find_one - retorna documentos diferentes para cada chamada
        updated_doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "min_age": 20,
            "max_age": 30
        }
        
        get_doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "min_age": 20,
            "max_age": 30
        }
        
        # Configura retornos diferentes para cada chamada
        mock_collection.find_one.side_effect = [updated_doc, get_doc]
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            # Atualizar age group
            age_group_update = AgeGroupUpdate(min_age=20, max_age=30)
            updated = await update_age_group("507f1f77bcf86cd799439011", age_group_update)
            
            # Buscar age group atualizado
            found = await get_age_group(updated["id"])
            
            # Verificações
            assert updated["id"] == found["id"]
            assert updated["min_age"] == found["min_age"] == 20
            assert updated["max_age"] == found["max_age"] == 30

    @pytest.mark.asyncio
    async def test_create_multiple_and_get_all_flow(self):
        """Testa fluxo de criação múltipla e busca de todos"""
        mock_collection = MagicMock()
        
        # Setup para múltiplas criações (simplificado)
        mock_docs = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "min_age": 18, "max_age": 25},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "min_age": 26, "max_age": 35}
        ]
        mock_collection.find.return_value = iter(mock_docs)
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            # Buscar todos os age groups
            all_groups = await get_all_age_groups()
            
            # Verificações
            assert len(all_groups) == 2
            assert all_groups[0]["min_age"] == 18
            assert all_groups[1]["min_age"] == 26

    @pytest.mark.asyncio
    async def test_delete_and_verify_removal_flow(self):
        """Testa fluxo de exclusão e verificação"""
        mock_collection = MagicMock()
        
        # Setup para delete
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 1
        mock_collection.delete_one.return_value = mock_delete_result
        
        # Setup para get após delete (não encontrado)
        mock_collection.find_one.return_value = None
        
        with patch('app.services.age_groups.mongo_db') as mock_db:
            mock_db.age_groups = mock_collection
            
            # Excluir age group
            deleted_count = await delete_age_group("507f1f77bcf86cd799439011")
            
            # Verificar que foi excluído
            found = await get_age_group("507f1f77bcf86cd799439011")
            
            # Verificações
            assert deleted_count == 1
            assert found is None 