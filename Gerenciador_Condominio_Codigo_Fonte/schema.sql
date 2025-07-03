CREATE DATABASE IF NOT EXISTS condominio DEFAULT CHARSET=utf8mb4;
USE condominio;

-- Apartamentos
CREATE TABLE apartamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(10) NOT NULL,
    bloco  VARCHAR(10),
    andar  INT,
    UNIQUE (numero, bloco)
);

-- Moradores
CREATE TABLE morador (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome       VARCHAR(100) NOT NULL,
    email      VARCHAR(120) UNIQUE,
    telefone   VARCHAR(20),
    senha_hash VARCHAR(256),
    papel ENUM('SINDICO','MORADOR') DEFAULT 'MORADOR',
    apartamento_id INT,
    FOREIGN KEY (apartamento_id) REFERENCES apartamento(id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- Despesas
CREATE TABLE despesa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(150) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    vencimento DATE,
    pago ENUM('SIM','NAO') DEFAULT 'NAO',
    apartamento_id INT,
    FOREIGN KEY (apartamento_id) REFERENCES apartamento(id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Notificações
CREATE TABLE notificacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    morador_id INT,
    titulo VARCHAR(120),
    mensagem TEXT,
    criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lida ENUM('SIM','NAO') DEFAULT 'NAO',
    FOREIGN KEY (morador_id) REFERENCES morador(id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Pagamentos
CREATE TABLE pagamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    despesa_id INT NOT NULL,
    morador_id INT NOT NULL,
    valor_pago DECIMAL(10,2) NOT NULL,
    pago_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (despesa_id) REFERENCES despesa(id)
           ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (morador_id) REFERENCES morador(id)
           ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE (despesa_id, morador_id)
);

-- Índices auxiliares
CREATE INDEX idx_despesa_apto  ON despesa (apartamento_id);
CREATE INDEX idx_notif_morador ON notificacao (morador_id);

