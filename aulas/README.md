# Aulas e etapas da NOA

Este repositório reúne o projeto NOA Engenharia de Dados e os materiais das aulas. Os materiais didáticos são do Instituto NTA, com responsabilidade técnica de Thiago Azeredo Rodrigues.

## Materiais por etapa

| Etapa | Apostila | Prática e montagem | Situação |
|---|---|---|---|
| Chat Parte 1: CI/CD e publicação | [Apostila](../documentos/parte1-cicd-deploy.md) | [Ideia](chat/parte1/IDEIA.md) | Implementada |
| Chat Parte 2: RAG e Supabase | [Apostila](../documentos/parte2-rag.md) | [Guia](chat/parte2/guia-montagem.md), [ideia](chat/parte2/IDEIA.md) | Implementada; resposta com fontes ainda precisa de validação real |
| Chat Parte 3: interface própria, PDF e produção | [Apostila](../documentos/parte3-frontend-producao.md) | [Guia](chat/parte3/guia-montagem.md), [ideia](chat/parte3/IDEIA.md) | Material organizado; implementação pendente |
| Python Parte 1: fundamentos e relatório de vendas | [Apostila](../documentos/python-parte1.md) | [Notebook e instruções](python/parte1/) | Material preparado para a aula de 15/10/2026 |
| Python Parte 2 | Ainda não recebida | Prevista para 29/10/2026 | Aguardar material |

As duas cópias recebidas da apostila de RAG têm o mesmo conteúdo textual e usam uma única versão Markdown. PDFs foram convertidos para texto; diagramas e tabelas devem ser consultados também nos PDFs originais recebidos no curso.

## Para a aula de 15/10, às 19h

1. Abra o [notebook no Colab](https://colab.research.google.com/github/Nayanearaujo/agente-personalizado/blob/main/aulas/python/parte1/Python_Engenharia_de_Dados_Parte1.ipynb).
2. Entre com sua conta Google e salve uma cópia no seu Drive para manter suas alterações.
3. Execute a primeira célula de código para confirmar que abriu corretamente.
4. Deixe a apostila ao lado e acompanhe as células na ordem com Shift + Enter.
5. Pratique o relatório de vendas e faça os cinco exercícios. Registre dúvidas para revisar depois.

Alternativa local: Python 3.11 ou superior e VS Code com Python e Jupyter. O notebook usa apenas bibliotecas padrão. Não é necessário contratar hospedagem ou usar chaves de IA para acompanhar esta aula.

## Próximas pendências do assistente

- Conferir a disponibilidade do projeto Supabase. As tentativas de atualização de 14/10 falharam com ConnectError; a causa ainda não foi confirmada.
- Após restabelecer a conexão, executar novamente indexação e avaliação. Guardar materiais no GitHub não significa que o índice em produção foi atualizado.
- Resolver o bloqueio de provedor do OpenRouter observado no último teste e validar uma resposta real com fontes.
- Implementar a Parte 3 por tarefas, mantendo a preferência por serviços gratuitos e verificando custos antes de escolher hospedagem.

Os documentos em documentos/ entram na base somente depois de o portão de avaliação aprovar. O notebook e os guias em aulas/ servem para estudo e prática.
