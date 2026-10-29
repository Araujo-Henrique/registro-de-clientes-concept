from enum import Enum


class Consulado(str, Enum):
    POA = "POA"
    RIO = "RIO"
    BSB = "BSB"
    SP = "SP"
    REC = "REC"


class ConsuladoOBT(str, Enum):
    # N/D existe só para o histórico antigo, sem consulado registrado.
    # Cadastro novo não aceita N/D (ver ProcessoOBTCreate).
    POA = "POA"
    RIO = "RIO"
    BSB = "BSB"
    SP = "SP"
    REC = "REC"
    ND = "N/D"


class Rascunho(str, Enum):
    PENDENTE = "Pendente"
    PARCIAL = "Parcial"
    ENVIADO = "Enviado"


class StatusDS(str, Enum):
    PENDENTE = "Pendente"
    PARCIAL = "Parcial"
    ABERTO = "Aberto"
    PREENCHIDO = "Preenchido"
    REVISADO = "Revisado"
    FECHADO = "Fechado"


class SituacaoOBT(str, Enum):
    PAG_PENDENTE = "Pagamento Pendente"
    BOLETO = "Boleto"
    CREDITO = "Credito"
    LIMBO = "Limbo"
    PROCESSANDO = "Processando"
    CADASTRO = "Cadastro"
    ADMINISTRATIVO = "Administrativo"
    PAGO = "Pago"
    CONCLUIDO = "Concluido"


class SituacaoREN(str, Enum):
    PAG_PENDENTE = "Pagamento Pendente"
    BOLETO = "Boleto"
    CREDITO = "Credito"
    LIMBO = "Limbo"
    PROCESSANDO = "Processando"
    CADASTRO = "Cadastro"
    ADMINISTRATIVO = "Administrativo"
    ENTREVISTA = "Entrevista"  # clientes de renovação normalmente não são chamados para entrevista
    CONCLUIDO = "Concluido"


class SituacaoPassaporte(str, Enum):
    PENDENTE = "Pendente"
    PAG_PENDENTE = "Pagamento Pendente"
    PAGO = "Pago"
    BOLETO = "Boleto"
    PIX = "Pix"
    PROCESSANDO = "Processando"
    CONCLUIDO = "Concluido"


class Resultado(str, Enum):
    PROCESSANDO = "Processando"
    APROVADO = "Aprovado"
    NEGADO = "Negado"


class Orientacao(str, Enum):
    OPTA = "Opt A"
    FORNECIDAS = "Fornecidas"
    AGENDADA = "Agendada"
    PENDENTE = "Pendente"


class Monitoramento(str, Enum):
    ATIVO = "Ativo"
    CONCLUIDO = "Concluido"


class DocsREN(str, Enum):
    PENDENTE = "Pendente"
    PARCIAL = "Parcial"
    ENTREGUE = "Entregue"
