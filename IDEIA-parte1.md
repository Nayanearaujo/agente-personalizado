# Ideia do projeto: Parte 1

## O que eu quero

Construir o Aprendendo Dados, um agente de IA personalizado para ensinar Estatística e Machine Learning em português, com explicações claras, exemplos e exercícios.

## Qual IA eu quero usar

OpenRouter com google/gemma-4-31b-it:free, sem comprar créditos. Se o serviço gratuito atingir um limite, o chat deve explicar o problema, sem trocar para modelos pagos.

## Como ele deve ensinar

Adaptar a profundidade ao aluno. Começar pela intuição, explicar os símbolos e mostrar contas passo a passo. Oferecer exercícios e dicas quando solicitado. Reconhecer incertezas e usar dados fictícios.

## Como eu quero personalizar

Editar nome, descrição, cores, logo, modelo, limite de resposta, instruções e perguntas de exemplo pelo config.yaml no GitHub.

## Como eu quero publicar

Código no GitHub e chat no Hugging Face Spaces. Cada commit na main executa testes pelo GitHub Actions. Somente alterações aprovadas pelo portão são publicadas. Uma configuração inválida deve impedir o envio.

## Segurança

Chave do OpenRouter nos secrets do Space e token de publicação nos secrets do GitHub. Nenhuma chave, informação pessoal ou documento sigiloso nos arquivos públicos.

## Perguntas de exemplo

- Qual é a diferença entre média, mediana e desvio padrão?
- Explique probabilidade com um exemplo simples.
- Qual é a diferença entre regressão e classificação?
- Como identificar overfitting em um modelo?

## O que fica para depois

Consulta às apostilas com fontes na Parte 2 e interface própria na Parte 3. Execução de código, treinamento de modelos, upload de arquivos, login e histórico salvo ficam fora desta etapa.

## Como vou saber que deu certo

Abrir o chat e receber uma explicação em português. Fazer uma segunda pergunta mantendo o contexto. Limpar a conversa. Alterar uma configuração válida e conferir a atualização. Usar uma cor inválida e verificar que a publicação é barrada.
