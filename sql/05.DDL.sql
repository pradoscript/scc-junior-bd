-- =====================================================================
-- SCC0640 - Bases de Dados - Projeto Copa do Mundo FIFA
-- Arquivo: 05.DDL.sql
-- Descrição: Criação do esquema, domínios, tabelas, constraints e triggers
-- =====================================================================

-- ---------------------------------------------------------------------
-- DOMÍNIOS
-- ---------------------------------------------------------------------

CREATE DOMAIN dom_continente AS VARCHAR(20)
  CHECK (VALUE IN ('Africa','America do Sul','America do Norte',
                   'America Central','Asia','Europa','Oceania'));

CREATE DOMAIN dom_tipo_fase AS VARCHAR(20)
  CHECK (VALUE IN ('fase_de_grupos','oitavas','quartas',
                   'semifinal','terceiro_lugar','final'));

CREATE DOMAIN dom_tipo_evento AS VARCHAR(25)
  CHECK (VALUE IN ('gol','gol_contra','penalti_convertido',
                   'cartao_amarelo','cartao_vermelho','substituicao'));

CREATE DOMAIN dom_tipo_gol AS VARCHAR(20)
  CHECK (VALUE IN ('normal','gol_contra','penalti_convertido'));

CREATE DOMAIN dom_tipo_cartao AS VARCHAR(10)
  CHECK (VALUE IN ('amarelo','vermelho'));

CREATE DOMAIN dom_funcao_arbitro AS VARCHAR(20)
  CHECK (VALUE IN ('principal','assistente_1','assistente_2',
                   'quarto_arbitro','var'));

CREATE DOMAIN dom_posicao AS VARCHAR(15)
  CHECK (VALUE IN ('goleiro','zagueiro','lateral','volante',
                   'meio_campo','atacante'));

-- ---------------------------------------------------------------------
-- TABELAS
-- ---------------------------------------------------------------------

CREATE TABLE Confederacao (
  IdConfederacao SERIAL PRIMARY KEY,
  Nome           VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Pais (
  Nome           VARCHAR(60) PRIMARY KEY,
  Continente     dom_continente NOT NULL,
  IdConfederacao INTEGER NOT NULL,
  CONSTRAINT fk_pais_confederacao
    FOREIGN KEY (IdConfederacao) REFERENCES Confederacao(IdConfederacao)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Selecao (
  IdSelecao SERIAL PRIMARY KEY,
  NomePais  VARCHAR(60) NOT NULL UNIQUE,
  CONSTRAINT fk_selecao_pais
    FOREIGN KEY (NomePais) REFERENCES Pais(Nome)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE EdicaoCopa (
  Ano          SMALLINT PRIMARY KEY CHECK (Ano BETWEEN 1930 AND 2100),
  DataInicio   DATE NOT NULL,
  DataTermino  DATE NOT NULL,
  IdCampea     INTEGER,
  IdVice       INTEGER,
  IdTerceiro   INTEGER,
  CONSTRAINT ck_edicao_datas CHECK (DataTermino >= DataInicio),
  CONSTRAINT fk_edicao_campea
    FOREIGN KEY (IdCampea) REFERENCES Selecao(IdSelecao)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_edicao_vice
    FOREIGN KEY (IdVice) REFERENCES Selecao(IdSelecao)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_edicao_terceiro
    FOREIGN KEY (IdTerceiro) REFERENCES Selecao(IdSelecao)
    ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE CidadeSede (
  IdCidade   SERIAL PRIMARY KEY,
  NomeCidade VARCHAR(80) NOT NULL,
  Pais       VARCHAR(60) NOT NULL,
  CONSTRAINT uq_cidade_pais UNIQUE (NomeCidade, Pais),
  CONSTRAINT fk_cidade_pais
    FOREIGN KEY (Pais) REFERENCES Pais(Nome)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE EdicaoCidade (
  AnoCopa  SMALLINT NOT NULL,
  IdCidade INTEGER NOT NULL,
  PRIMARY KEY (AnoCopa, IdCidade),
  CONSTRAINT fk_ec_edicao
    FOREIGN KEY (AnoCopa) REFERENCES EdicaoCopa(Ano)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_ec_cidade
    FOREIGN KEY (IdCidade) REFERENCES CidadeSede(IdCidade)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Estadio (
  IdEstadio    SERIAL PRIMARY KEY,
  Nome         VARCHAR(100) NOT NULL,
  Capacidade   INTEGER NOT NULL CHECK (Capacidade > 0),
  Localizacao  VARCHAR(150),
  IdCidade     INTEGER NOT NULL,
  CONSTRAINT uq_estadio_nome_cidade UNIQUE (Nome, IdCidade),
  CONSTRAINT fk_estadio_cidade
    FOREIGN KEY (IdCidade) REFERENCES CidadeSede(IdCidade)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Tecnico (
  IdTecnico    SERIAL PRIMARY KEY,
  Nome         VARCHAR(100) NOT NULL,
  Nacionalidade VARCHAR(60) NOT NULL
);

CREATE TABLE Jogador (
  IdJogador      SERIAL PRIMARY KEY,
  Nome           VARCHAR(100) NOT NULL,
  Posicao        dom_posicao NOT NULL,
  DataNascimento DATE NOT NULL,
  Nacionalidade  VARCHAR(60) NOT NULL,
  CONSTRAINT ck_jogador_nascimento CHECK (DataNascimento < CURRENT_DATE)
);

CREATE TABLE Arbitro (
  IdArbitro     SERIAL PRIMARY KEY,
  Nome          VARCHAR(100) NOT NULL,
  Nacionalidade VARCHAR(60) NOT NULL
);

CREATE TABLE Fase (
  IdFase  SERIAL PRIMARY KEY,
  Nome    VARCHAR(40) NOT NULL,
  Tipo    dom_tipo_fase NOT NULL,
  AnoCopa SMALLINT NOT NULL,
  CONSTRAINT uq_fase_edicao UNIQUE (AnoCopa, Tipo),
  CONSTRAINT fk_fase_edicao
    FOREIGN KEY (AnoCopa) REFERENCES EdicaoCopa(Ano)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Grupo (
  IdGrupo SERIAL PRIMARY KEY,
  Letra   CHAR(1) NOT NULL CHECK (Letra ~ '^[A-H]$'),
  IdFase  INTEGER NOT NULL,
  CONSTRAINT uq_grupo_fase UNIQUE (IdFase, Letra),
  CONSTRAINT fk_grupo_fase
    FOREIGN KEY (IdFase) REFERENCES Fase(IdFase)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE GrupoSelecao (
  IdGrupo   INTEGER NOT NULL,
  IdSelecao INTEGER NOT NULL,
  PRIMARY KEY (IdGrupo, IdSelecao),
  CONSTRAINT fk_gs_grupo
    FOREIGN KEY (IdGrupo) REFERENCES Grupo(IdGrupo)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_gs_selecao
    FOREIGN KEY (IdSelecao) REFERENCES Selecao(IdSelecao)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Participacao (
  AnoCopa   SMALLINT NOT NULL,
  IdSelecao INTEGER NOT NULL,
  IdTecnico INTEGER NOT NULL,
  PRIMARY KEY (AnoCopa, IdSelecao),
  CONSTRAINT fk_part_edicao
    FOREIGN KEY (AnoCopa) REFERENCES EdicaoCopa(Ano)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_part_selecao
    FOREIGN KEY (IdSelecao) REFERENCES Selecao(IdSelecao)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_part_tecnico
    FOREIGN KEY (IdTecnico) REFERENCES Tecnico(IdTecnico)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Convocacao (
  AnoCopa       SMALLINT NOT NULL,
  IdSelecao     INTEGER NOT NULL,
  IdJogador     INTEGER NOT NULL,
  NumeroCamisa  SMALLINT NOT NULL CHECK (NumeroCamisa BETWEEN 1 AND 99),
  PRIMARY KEY (AnoCopa, IdSelecao, IdJogador),
  CONSTRAINT uq_convocacao_camisa UNIQUE (AnoCopa, IdSelecao, NumeroCamisa),
  CONSTRAINT fk_conv_part
    FOREIGN KEY (AnoCopa, IdSelecao) REFERENCES Participacao(AnoCopa, IdSelecao)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_conv_jogador
    FOREIGN KEY (IdJogador) REFERENCES Jogador(IdJogador)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Partida (
  IdPartida          SERIAL PRIMARY KEY,
  DataHora           TIMESTAMP NOT NULL,
  GolsTime1          SMALLINT NOT NULL DEFAULT 0 CHECK (GolsTime1 >= 0),
  GolsTime2          SMALLINT NOT NULL DEFAULT 0 CHECK (GolsTime2 >= 0),
  TemProrrogacao     BOOLEAN NOT NULL DEFAULT FALSE,
  ResultadoPenaltis  VARCHAR(20),
  IdClassificado     INTEGER,
  IdFase             INTEGER NOT NULL,
  IdEstadio          INTEGER NOT NULL,
  IdSelecao1         INTEGER NOT NULL,
  IdSelecao2         INTEGER NOT NULL,
  CONSTRAINT ck_partida_selecoes CHECK (IdSelecao1 <> IdSelecao2),
  CONSTRAINT fk_partida_fase
    FOREIGN KEY (IdFase) REFERENCES Fase(IdFase)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_partida_estadio
    FOREIGN KEY (IdEstadio) REFERENCES Estadio(IdEstadio)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_partida_sel1
    FOREIGN KEY (IdSelecao1) REFERENCES Selecao(IdSelecao)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_partida_sel2
    FOREIGN KEY (IdSelecao2) REFERENCES Selecao(IdSelecao)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_partida_classificado
    FOREIGN KEY (IdClassificado) REFERENCES Selecao(IdSelecao)
    ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE Arbitragem (
  IdPartida INTEGER NOT NULL,
  IdArbitro INTEGER NOT NULL,
  Funcao    dom_funcao_arbitro NOT NULL,
  PRIMARY KEY (IdPartida, IdArbitro),
  CONSTRAINT uq_arb_funcao_partida UNIQUE (IdPartida, Funcao),
  CONSTRAINT fk_arb_partida
    FOREIGN KEY (IdPartida) REFERENCES Partida(IdPartida)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_arb_arbitro
    FOREIGN KEY (IdArbitro) REFERENCES Arbitro(IdArbitro)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Evento (
  IdEvento  SERIAL PRIMARY KEY,
  Minuto    SMALLINT NOT NULL CHECK (Minuto BETWEEN 0 AND 130),
  Tipo      dom_tipo_evento NOT NULL,
  IdPartida INTEGER NOT NULL,
  CONSTRAINT fk_evento_partida
    FOREIGN KEY (IdPartida) REFERENCES Partida(IdPartida)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Gol (
  IdEvento  INTEGER PRIMARY KEY,
  TipoGol   dom_tipo_gol NOT NULL,
  IdJogador INTEGER NOT NULL,
  IdSelecao INTEGER NOT NULL,
  CONSTRAINT fk_gol_evento
    FOREIGN KEY (IdEvento) REFERENCES Evento(IdEvento)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_gol_jogador
    FOREIGN KEY (IdJogador) REFERENCES Jogador(IdJogador)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_gol_selecao
    FOREIGN KEY (IdSelecao) REFERENCES Selecao(IdSelecao)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Substituicao (
  IdEvento       INTEGER PRIMARY KEY,
  IdJogadorSai   INTEGER NOT NULL,
  IdJogadorEntra INTEGER NOT NULL,
  CONSTRAINT ck_subst_jogadores CHECK (IdJogadorSai <> IdJogadorEntra),
  CONSTRAINT fk_subst_evento
    FOREIGN KEY (IdEvento) REFERENCES Evento(IdEvento)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_subst_sai
    FOREIGN KEY (IdJogadorSai) REFERENCES Jogador(IdJogador)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_subst_entra
    FOREIGN KEY (IdJogadorEntra) REFERENCES Jogador(IdJogador)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Cartao (
  IdEvento   INTEGER PRIMARY KEY,
  TipoCartao dom_tipo_cartao NOT NULL,
  IdJogador  INTEGER NOT NULL,
  CONSTRAINT fk_cartao_evento
    FOREIGN KEY (IdEvento) REFERENCES Evento(IdEvento)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_cartao_jogador
    FOREIGN KEY (IdJogador) REFERENCES Jogador(IdJogador)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- TRIGGERS
-- ---------------------------------------------------------------------

-- Trigger 1: impedir que IdSelecao1 = IdSelecao2 (redundância ao CHECK,
-- garante mensagem amigável e cobre updates parciais)
CREATE OR REPLACE FUNCTION fn_check_selecoes_diferentes()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.IdSelecao1 = NEW.IdSelecao2 THEN
    RAISE EXCEPTION 'Uma partida nao pode ter a mesma selecao nos dois lados';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_selecoes_diferentes
  BEFORE INSERT OR UPDATE ON Partida
  FOR EACH ROW EXECUTE FUNCTION fn_check_selecoes_diferentes();

-- Trigger 2: validar minuto do evento (0..130)
CREATE OR REPLACE FUNCTION fn_check_minuto_evento()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.Minuto < 0 OR NEW.Minuto > 130 THEN
    RAISE EXCEPTION 'Minuto do evento deve estar entre 0 e 130 (recebido: %)', NEW.Minuto;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_minuto_evento
  BEFORE INSERT OR UPDATE ON Evento
  FOR EACH ROW EXECUTE FUNCTION fn_check_minuto_evento();

-- Trigger 3: atualizar automaticamente GolsTime1/GolsTime2 ao
-- inserir ou remover um Gol
CREATE OR REPLACE FUNCTION fn_atualizar_placar()
RETURNS TRIGGER AS $$
DECLARE
  v_partida INTEGER;
  v_sel1    INTEGER;
  v_sel2    INTEGER;
BEGIN
  IF TG_OP = 'INSERT' THEN
    SELECT e.IdPartida INTO v_partida FROM Evento e WHERE e.IdEvento = NEW.IdEvento;
    SELECT IdSelecao1, IdSelecao2 INTO v_sel1, v_sel2
      FROM Partida WHERE IdPartida = v_partida;

    IF NEW.TipoGol = 'gol_contra' THEN
      -- gol contra conta para o adversário
      IF NEW.IdSelecao = v_sel1 THEN
        UPDATE Partida SET GolsTime2 = GolsTime2 + 1 WHERE IdPartida = v_partida;
      ELSE
        UPDATE Partida SET GolsTime1 = GolsTime1 + 1 WHERE IdPartida = v_partida;
      END IF;
    ELSE
      IF NEW.IdSelecao = v_sel1 THEN
        UPDATE Partida SET GolsTime1 = GolsTime1 + 1 WHERE IdPartida = v_partida;
      ELSIF NEW.IdSelecao = v_sel2 THEN
        UPDATE Partida SET GolsTime2 = GolsTime2 + 1 WHERE IdPartida = v_partida;
      ELSE
        RAISE EXCEPTION 'Selecao do gol (%) nao participa da partida %', NEW.IdSelecao, v_partida;
      END IF;
    END IF;
    RETURN NEW;

  ELSIF TG_OP = 'DELETE' THEN
    SELECT e.IdPartida INTO v_partida FROM Evento e WHERE e.IdEvento = OLD.IdEvento;
    IF v_partida IS NULL THEN
      RETURN OLD; -- partida ja removida em cascata
    END IF;
    SELECT IdSelecao1, IdSelecao2 INTO v_sel1, v_sel2
      FROM Partida WHERE IdPartida = v_partida;

    IF OLD.TipoGol = 'gol_contra' THEN
      IF OLD.IdSelecao = v_sel1 THEN
        UPDATE Partida SET GolsTime2 = GREATEST(GolsTime2 - 1, 0) WHERE IdPartida = v_partida;
      ELSE
        UPDATE Partida SET GolsTime1 = GREATEST(GolsTime1 - 1, 0) WHERE IdPartida = v_partida;
      END IF;
    ELSE
      IF OLD.IdSelecao = v_sel1 THEN
        UPDATE Partida SET GolsTime1 = GREATEST(GolsTime1 - 1, 0) WHERE IdPartida = v_partida;
      ELSIF OLD.IdSelecao = v_sel2 THEN
        UPDATE Partida SET GolsTime2 = GREATEST(GolsTime2 - 1, 0) WHERE IdPartida = v_partida;
      END IF;
    END IF;
    RETURN OLD;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_atualizar_placar
  AFTER INSERT OR DELETE ON Gol
  FOR EACH ROW EXECUTE FUNCTION fn_atualizar_placar();

-- Trigger 4: impedir mais de 1 tecnico por selecao na mesma edicao
-- (redundância segura, pois a PK ja garante via (AnoCopa, IdSelecao))
CREATE OR REPLACE FUNCTION fn_check_unico_tecnico()
RETURNS TRIGGER AS $$
DECLARE
  v_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO v_count
    FROM Participacao
    WHERE AnoCopa = NEW.AnoCopa AND IdSelecao = NEW.IdSelecao;
  IF v_count > 0 AND TG_OP = 'INSERT' THEN
    RAISE EXCEPTION 'Selecao % ja possui tecnico na edicao %', NEW.IdSelecao, NEW.AnoCopa;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_unico_tecnico
  BEFORE INSERT ON Participacao
  FOR EACH ROW EXECUTE FUNCTION fn_check_unico_tecnico();

-- Trigger 5 (extra): impedir 2+ amarelos ou 1+ vermelho do mesmo jogador
-- na mesma partida
CREATE OR REPLACE FUNCTION fn_check_cartoes_jogador()
RETURNS TRIGGER AS $$
DECLARE
  v_partida    INTEGER;
  v_amarelos   INTEGER;
  v_vermelhos  INTEGER;
BEGIN
  SELECT IdPartida INTO v_partida FROM Evento WHERE IdEvento = NEW.IdEvento;

  SELECT COUNT(*) INTO v_amarelos
    FROM Cartao c
    JOIN Evento e ON e.IdEvento = c.IdEvento
    WHERE e.IdPartida = v_partida
      AND c.IdJogador = NEW.IdJogador
      AND c.TipoCartao = 'amarelo'
      AND c.IdEvento <> NEW.IdEvento;

  SELECT COUNT(*) INTO v_vermelhos
    FROM Cartao c
    JOIN Evento e ON e.IdEvento = c.IdEvento
    WHERE e.IdPartida = v_partida
      AND c.IdJogador = NEW.IdJogador
      AND c.TipoCartao = 'vermelho'
      AND c.IdEvento <> NEW.IdEvento;

  IF NEW.TipoCartao = 'amarelo' AND v_amarelos >= 2 THEN
    RAISE EXCEPTION 'Jogador % ja possui 2 cartoes amarelos na partida %', NEW.IdJogador, v_partida;
  END IF;

  IF NEW.TipoCartao = 'vermelho' AND v_vermelhos >= 1 THEN
    RAISE EXCEPTION 'Jogador % ja possui cartao vermelho na partida %', NEW.IdJogador, v_partida;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_cartoes_jogador
  BEFORE INSERT OR UPDATE ON Cartao
  FOR EACH ROW EXECUTE FUNCTION fn_check_cartoes_jogador();
