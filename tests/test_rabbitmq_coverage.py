"""
Testes específicos para melhorar cobertura do módulo rabbitMQ.py
"""

import pytest
from unittest.mock import patch, MagicMock
import pika
from app.db.rabbitMQ import (
    connect_rabbitmq_with_retry,
    reset_connections,
    get_rabbitmq_connection,
    get_rabbitmq_channel,
    publish_message
)


class TestRabbitMQCoverage:
    """Testes para melhorar cobertura do módulo rabbitMQ"""

    def test_connect_rabbitmq_with_retry_no_credentials_success(self):
        """Testa conexão bem-sucedida sem credenciais"""
        mock_connection = MagicMock()
        
        with patch('pika.BlockingConnection', return_value=mock_connection) as mock_pika:
            result = connect_rabbitmq_with_retry("localhost", 5672)
            assert result == mock_connection
            # Deve tentar primeiro sem credenciais
            mock_pika.assert_called_once()

    def test_connect_rabbitmq_with_retry_with_credentials_success(self):
        """Testa conexão bem-sucedida com credenciais após falha sem credenciais"""
        mock_connection = MagicMock()
        
        with patch('pika.BlockingConnection') as mock_pika:
            # Primeira chamada falha (sem credenciais), segunda sucede (com credenciais)
            mock_pika.side_effect = [Exception("Auth failed"), mock_connection]
            
            result = connect_rabbitmq_with_retry("localhost", 5672)
            assert result == mock_connection
            assert mock_pika.call_count == 2

    def test_connect_rabbitmq_with_retry_max_retries_exceeded(self):
        """Testa falha após esgotar tentativas"""
        with patch('pika.BlockingConnection') as mock_pika, \
             patch('time.sleep') as mock_sleep:
            mock_pika.side_effect = pika.exceptions.AMQPConnectionError("Connection failed")
            
            with pytest.raises(Exception, match="Não foi possível conectar ao RabbitMQ"):
                connect_rabbitmq_with_retry("localhost", 5672, retries=2, delay=1)
            
            assert mock_sleep.call_count == 2

    def test_reset_connections_with_open_connections(self):
        """Testa reset com conexões abertas"""
        mock_channel = MagicMock()
        mock_channel.is_closed = False
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        
        with patch('app.db.rabbitMQ._channel', mock_channel), \
             patch('app.db.rabbitMQ._connection', mock_connection):
            reset_connections()
            mock_channel.close.assert_called_once()
            mock_connection.close.assert_called_once()

    def test_reset_connections_with_closed_connections(self):
        """Testa reset com conexões já fechadas"""
        mock_channel = MagicMock()
        mock_channel.is_closed = True
        mock_connection = MagicMock()
        mock_connection.is_closed = True
        
        with patch('app.db.rabbitMQ._channel', mock_channel), \
             patch('app.db.rabbitMQ._connection', mock_connection):
            reset_connections()
            # Não deve tentar fechar conexões já fechadas
            mock_channel.close.assert_not_called()
            mock_connection.close.assert_not_called()

    def test_reset_connections_with_exception(self):
        """Testa reset quando close() gera exceção"""
        mock_channel = MagicMock()
        mock_channel.is_closed = False
        mock_channel.close.side_effect = Exception("Close failed")
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection.close.side_effect = Exception("Close failed")
        
        with patch('app.db.rabbitMQ._channel', mock_channel), \
             patch('app.db.rabbitMQ._connection', mock_connection):
            # Não deve gerar exceção mesmo com erros no close
            reset_connections()

    def test_get_rabbitmq_connection_create_new(self):
        """Testa criação de nova conexão"""
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        
        with patch('app.db.rabbitMQ._connection', None), \
             patch('app.db.rabbitMQ.connect_rabbitmq_with_retry', return_value=mock_connection):
            result = get_rabbitmq_connection()
            assert result == mock_connection

    def test_get_rabbitmq_connection_reuse_existing(self):
        """Testa reutilização de conexão existente"""
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        
        with patch('app.db.rabbitMQ._connection', mock_connection), \
             patch('app.db.rabbitMQ.connect_rabbitmq_with_retry') as mock_connect:
            result = get_rabbitmq_connection()
            assert result == mock_connection
            # Não deve criar nova conexão
            mock_connect.assert_not_called()

    def test_get_rabbitmq_connection_recreate_closed(self):
        """Testa recriação de conexão fechada"""
        mock_old_connection = MagicMock()
        mock_old_connection.is_closed = True
        mock_new_connection = MagicMock()
        mock_new_connection.is_closed = False
        
        with patch('app.db.rabbitMQ._connection', mock_old_connection), \
             patch('app.db.rabbitMQ.connect_rabbitmq_with_retry', return_value=mock_new_connection):
            result = get_rabbitmq_connection()
            assert result == mock_new_connection

    def test_get_rabbitmq_connection_exception(self):
        """Testa tratamento de exceção na conexão"""
        with patch('app.db.rabbitMQ._connection', None), \
             patch('app.db.rabbitMQ.connect_rabbitmq_with_retry', side_effect=Exception("Connection failed")), \
             patch('app.db.rabbitMQ.reset_connections') as mock_reset:
            
            with pytest.raises(Exception, match="Connection failed"):
                get_rabbitmq_connection()
            
            mock_reset.assert_called_once()

    def test_get_rabbitmq_channel_create_new(self):
        """Testa criação de novo canal"""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_channel.is_closed = False
        mock_connection.channel.return_value = mock_channel
        
        with patch('app.db.rabbitMQ._channel', None), \
             patch('app.db.rabbitMQ.get_rabbitmq_connection', return_value=mock_connection):
            result = get_rabbitmq_channel()
            assert result == mock_channel
            mock_channel.queue_declare.assert_called_once()

    def test_get_rabbitmq_channel_reuse_existing(self):
        """Testa reutilização de canal existente"""
        mock_channel = MagicMock()
        mock_channel.is_closed = False
        
        with patch('app.db.rabbitMQ._channel', mock_channel), \
             patch('app.db.rabbitMQ.get_rabbitmq_connection') as mock_get_conn:
            result = get_rabbitmq_channel()
            assert result == mock_channel
            # Não deve criar nova conexão
            mock_get_conn.assert_not_called()

    def test_get_rabbitmq_channel_recreate_closed(self):
        """Testa recriação de canal fechado"""
        mock_old_channel = MagicMock()
        mock_old_channel.is_closed = True
        mock_connection = MagicMock()
        mock_new_channel = MagicMock()
        mock_new_channel.is_closed = False
        mock_connection.channel.return_value = mock_new_channel
        
        with patch('app.db.rabbitMQ._channel', mock_old_channel), \
             patch('app.db.rabbitMQ.get_rabbitmq_connection', return_value=mock_connection):
            result = get_rabbitmq_channel()
            assert result == mock_new_channel
            mock_new_channel.queue_declare.assert_called_once()

    def test_get_rabbitmq_channel_exception(self):
        """Testa tratamento de exceção no canal"""
        with patch('app.db.rabbitMQ._channel', None), \
             patch('app.db.rabbitMQ.get_rabbitmq_connection', side_effect=Exception("Channel failed")), \
             patch('app.db.rabbitMQ.reset_connections') as mock_reset:
            
            with pytest.raises(Exception, match="Channel failed"):
                get_rabbitmq_channel()
            
            mock_reset.assert_called_once()

    def test_publish_message_success_first_try(self):
        """Testa publicação bem-sucedida na primeira tentativa"""
        mock_channel = MagicMock()
        
        with patch('app.db.rabbitMQ.get_rabbitmq_channel', return_value=mock_channel):
            publish_message("test message")
            mock_channel.basic_publish.assert_called_once()

    def test_publish_message_retry_then_success(self):
        """Testa publicação com retry após falha"""
        mock_channel = MagicMock()
        
        with patch('app.db.rabbitMQ.get_rabbitmq_channel', return_value=mock_channel), \
             patch('app.db.rabbitMQ.reset_connections') as mock_reset, \
             patch('time.sleep') as mock_sleep:
            
            # Primeira tentativa falha, segunda sucede
            mock_channel.basic_publish.side_effect = [Exception("Publish failed"), None]
            
            publish_message("test message")
            assert mock_channel.basic_publish.call_count == 2
            mock_reset.assert_called_once()
            mock_sleep.assert_called_once_with(1)

    def test_publish_message_max_retries_exceeded(self):
        """Testa falha após esgotar tentativas de publicação"""
        mock_channel = MagicMock()
        mock_channel.basic_publish.side_effect = Exception("Publish failed")
        
        with patch('app.db.rabbitMQ.get_rabbitmq_channel', return_value=mock_channel), \
             patch('app.db.rabbitMQ.reset_connections') as mock_reset, \
             patch('time.sleep') as mock_sleep:
            
            with pytest.raises(Exception, match="Publish failed"):
                publish_message("test message")
            
            assert mock_channel.basic_publish.call_count == 3  # max_retries
            assert mock_reset.call_count == 3
            assert mock_sleep.call_count == 2  # Não dorme na última tentativa

    def test_publish_message_with_properties(self):
        """Testa se a mensagem é publicada com propriedades corretas"""
        mock_channel = MagicMock()
        
        with patch('app.db.rabbitMQ.get_rabbitmq_channel', return_value=mock_channel):
            publish_message("test message")
            
            # Verifica se foi chamado com as propriedades corretas
            call_args = mock_channel.basic_publish.call_args
            assert call_args[1]['body'] == "test message"
            assert call_args[1]['properties'].delivery_mode == 2  # Persistente 