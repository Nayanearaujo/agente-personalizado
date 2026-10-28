"""Conversão de PDF para Markdown (lógica de limpeza, sem precisar da biblioteca).

Testa a função limpar_paginas com páginas simuladas: remove cabeçalho/rodapé
repetidos e números de página, arruma títulos e barra PDF escaneado.
"""

import pytest

from agente.pdf import PdfSemTexto, limpar_paginas

CABECALHO = "INSTITUTO NTA"
RODAPE = "Material de consulta."


def _pagina(numero: int, corpo: str) -> str:
    return f"{CABECALHO}\n{corpo}\n{RODAPE}\n{numero}"


def test_remove_cabecalho_rodape_e_numero():
    paginas = [
        _pagina(1, "# 01 Introducao\n" + "Conteudo real da primeira secao. " * 8),
        _pagina(2, "## 02 Detalhes\n" + "Mais conteudo relevante aqui, bastante texto. " * 8),
        _pagina(3, "## 03 Final\n" + "Ultima secao com bastante conteudo de verdade. " * 8),
    ]
    md = limpar_paginas(paginas, "doc.pdf")
    assert CABECALHO not in md
    assert RODAPE not in md
    # Os números de página soltos (1, 2, 3) saíram.
    assert "\n1\n" not in md and not md.strip().endswith("3")
    # O conteúdo e os títulos ficaram.
    assert "01 Introducao" in md and "02 Detalhes" in md


def test_arruma_titulo_com_negrito():
    corpo = "## **01 O que e deploy**\n" + "Texto explicando o conceito com detalhes suficientes. " * 8
    paginas = [_pagina(1, corpo), _pagina(2, "## 02 Outra\n" + "Mais texto de conteudo aqui para validar. " * 8),
               _pagina(3, "## 03 Fim\n" + "Conteudo final para completar o documento todo. " * 8)]
    md = limpar_paginas(paginas, "doc.pdf")
    assert "## 01 O que e deploy" in md
    assert "**01 O que e deploy**" not in md


def test_pdf_escaneado_barra():
    # Páginas quase vazias (sem texto extraível) -> PdfSemTexto.
    paginas = ["", "  ", "\n"]
    with pytest.raises(PdfSemTexto) as exc:
        limpar_paginas(paginas, "escaneado.pdf")
    assert "escaneado" in str(exc.value).lower()
    assert "escaneado.pdf" in str(exc.value)


def test_garante_titulo_de_documento():
    # Sem nenhum '# ', usa o nome do arquivo como título.
    corpo = "Texto sem titulo nenhum, mas com bastante conteudo para passar do minimo. " * 6
    paginas = [corpo, corpo, corpo]
    md = limpar_paginas(paginas, "parte3-frontend-producao.pdf")
    assert md.startswith("# ")
    assert "Parte3 Frontend Producao" in md or "Parte3-Frontend-Producao" in md.replace(" ", "-")
