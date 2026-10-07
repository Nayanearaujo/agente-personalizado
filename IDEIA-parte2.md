# Ideia da Parte 2: a NOA consulta os documentos

A NOA Engenharia de Dados vai consultar material de estudo antes de responder. A base inicial será formada pelas apostilas das Partes 1 e 2, já fornecidas, convertidas e revisadas em Markdown. Depois acrescentaremos documentos de Engenharia de Dados, Estatística e Machine Learning. Não vamos inventar documentos ou referências para preencher a pasta.

Os arquivos ficarão em `documentos/`, somente em `.md`, com títulos e seções. Não entram dados pessoais ou sigilosos. Os PDFs originais ficam fora do repositório público.

A resposta deve usar somente os trechos recuperados, ignorar instruções encontradas nos documentos e terminar com o arquivo e a seção consultados. Se não houver informação suficiente, deve dizer exatamente: "Não encontrei isso no material do curso."

Usaremos Supabase no plano gratuito, Postgres e pgvector. O GitHub Actions grava e avalia o índice; o Space só consulta. A chave secreta do Supabase fica no GitHub e a publicável fica no Space.

A busca combina palavras e significado por RRF. Seguiremos o exemplo da aula: FastEmbed, MiniLM multilíngue de 384 dimensões, trechos de até 1200 caracteres, sobreposição de 150, quatro trechos por resposta e pesos iguais. O mesmo modelo será usado para documentos e perguntas, na CPU e sem chave de embeddings.

Cada publicação reconstrói uma coleção de teste e avalia oito perguntas. Exigiremos hit rate mínimo de 85%, com MRR no relatório. A coleção em produção só muda depois da aprovação da busca. Uma avaliação reprovada mantém o índice e o Space anteriores.

O layout aprovado, a coruja, as cores, os testes e a restrição a modelos gratuitos da Parte 1 continuam. A consulta ao OpenRouter ainda está pendente; isso não impede construir e testar a recuperação, mas a resposta final com IA precisa ser validada quando o provedor funcionar.

Não entram agora reranker, GraphRAG, agentes adicionais, upload pelo chat, histórico no banco ou interface própria da Parte 3.

Primeiro aprovaremos `SPEC-parte2-rag.md`; depois faremos uma tarefa por vez, mostrando como testar. A conta e o projeto gratuitos do Supabase ainda precisam ser criados.
