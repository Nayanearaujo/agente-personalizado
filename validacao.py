"""Validação da configuração compartilhada pelo chat e pelo portão."""
from pathlib import Path
from urllib.parse import urlparse
import re
import sys
import yaml

CAMPOS = {
    "nome", "descricao", "cor_principal", "cor_secundaria", "logo",
    "logo_tamanho", "modelo", "max_tokens", "prompt_sistema", "exemplos",
}


class ConfiguracaoInvalida(ValueError):
    pass


class LeitorUnico(yaml.SafeLoader):
    """Não aceitar campos repetidos que ocultem um valor anterior."""


def _mapa(loader, node, deep=False):
    resultado = {}
    for chave_node, valor_node in node.value:
        chave = loader.construct_object(chave_node, deep=deep)
        if not isinstance(chave, str):
            raise ConfiguracaoInvalida("T1: os nomes dos campos devem ser textos.")
        if chave in resultado:
            raise ConfiguracaoInvalida(f"T1: campo repetido: {chave}.")
        resultado[chave] = loader.construct_object(valor_node, deep=deep)
    return resultado


LeitorUnico.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapa
)


def contraste_branco(cor):
    canais = [int(cor[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    canais = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
              for c in canais]
    luminancia = sum(c * peso for c, peso in zip(canais, (0.2126, 0.7152, 0.0722)))
    return 1.05 / (luminancia + 0.05)


def validar_config(config, pasta):
    erros = []
    if not isinstance(config, dict):
        return ["T2: a configuração deve ser um mapa de campos e valores."]
    for campo in sorted(CAMPOS - config.keys()):
        erros.append(f"T2: campo obrigatório ausente: {campo}.")
    for campo in sorted(config.keys() - CAMPOS):
        erros.append(f"T2: campo desconhecido: {campo}.")
    for campo, limite in (("nome", 80), ("descricao", 240)):
        valor = config.get(campo)
        if not isinstance(valor, str) or not 1 <= len(valor.strip()) <= limite:
            erros.append(f"T2: {campo} deve ter entre 1 e {limite} caracteres.")
    for campo in ("cor_principal", "cor_secundaria"):
        cor = config.get(campo)
        if not isinstance(cor, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", cor):
            erros.append(f"T3: {campo} deve usar o formato #RRGGBB entre aspas.")
        elif contraste_branco(cor) < 3:
            erros.append(f"T4: {campo} tem contraste insuficiente com branco; use uma cor mais escura.")
    logo = config.get("logo")
    if not isinstance(logo, str) or not logo.strip():
        erros.append("T5: informe uma logo SVG local ou URL HTTPS.")
    else:
        url = urlparse(logo)
        if url.scheme or url.netloc:
            if url.scheme != "https" or not url.hostname or url.username or url.password:
                erros.append("T5: a URL da logo deve ser HTTPS e não conter credenciais.")
        else:
            raiz = Path(pasta).resolve()
            arquivo = (raiz / logo).resolve()
            if not arquivo.is_relative_to(raiz) or arquivo.suffix.lower() != ".svg" or not arquivo.is_file():
                erros.append("T5: a logo deve ser um SVG existente dentro do projeto.")
    tamanho = config.get("logo_tamanho")
    if type(tamanho) is not int or not 32 <= tamanho <= 160:
        erros.append("T5: logo_tamanho deve ser um inteiro entre 32 e 160.")
    modelo = config.get("modelo")
    if not isinstance(modelo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.:-]+", modelo):
        erros.append("T6: modelo deve usar o formato fornecedor/modelo.")
    tokens = config.get("max_tokens")
    if type(tokens) is not int or not 1 <= tokens <= 4096:
        erros.append("T6: max_tokens deve ser um inteiro entre 1 e 4096.")
    prompt = config.get("prompt_sistema")
    if not isinstance(prompt, str) or len(prompt.strip()) < 80:
        erros.append("T7: prompt_sistema deve ter pelo menos 80 caracteres.")
    exemplos = config.get("exemplos")
    if not isinstance(exemplos, list) or not 1 <= len(exemplos) <= 8 or any(
        not isinstance(item, str) or not item.strip() for item in exemplos
    ):
        erros.append("T7: exemplos deve conter de 1 a 8 perguntas preenchidas.")
    return erros


def carregar_config(caminho=None):
    arquivo = Path(caminho) if caminho else Path(__file__).with_name("config.yaml")
    try:
        config = yaml.load(arquivo.read_text(encoding="utf-8"), Loader=LeitorUnico)
    except (OSError, yaml.YAMLError) as erro:
        # Não imprimir o conteúdo do YAML: ele pode conter um segredo por engano.
        raise ConfiguracaoInvalida("T1: não foi possível ler o YAML; confira o arquivo e a indentação.") from erro
    erros = validar_config(config, arquivo.parent)
    if erros:
        raise ConfiguracaoInvalida("\n".join(erros))
    return config


if __name__ == "__main__":
    try:
        carregar_config(sys.argv[1] if len(sys.argv) > 1 else None)
    except ConfiguracaoInvalida as erro:
        print(erro)
        sys.exit(1)
    print("Configuração válida. Nome, cores, logo, modelo e instruções conferidos.")
