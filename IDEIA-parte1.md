# Ideia do projeto: Parte 1

## O que eu quero

Quero construir o Chargeback Intelligence, um assistente de inteligência artificial em português sobre chargeback. Ele deve ajudar estudantes e profissionais a entender conceitos, analisar indicadores e estudar aplicações de Engenharia de Dados, Estatística e Machine Learning na prevenção de perdas.

Na primeira etapa, qualquer pessoa poderá abrir um link e conversar com o assistente. Ele será educativo e não executará análises de arquivos nem previsões de risco.

## Público e comportamento

O assistente deve explicar de forma clara, adaptar a profundidade ao conhecimento do usuário e usar exemplos fictícios. Deve distinguir chargeback, fraude e reembolso, reconhecer incertezas e não inventar regras, prazos ou resultados. Ao tratar procedimentos que dependem de bandeira, adquirente ou contrato, deve orientar a consulta à documentação aplicável. Não deve pedir dados pessoais, números de cartão ou informações sigilosas.

## Qual IA eu quero usar

Quero priorizar o OpenRouter e permitir configurar OpenAI e Anthropic como alternativas. Os provedores e modelos devem estar em ordem de preferência. Se um falhar antes de começar a resposta, o assistente deve tentar o próximo. Se nenhum funcionar, deve mostrar uma mensagem compreensível sem revelar chaves ou detalhes sensíveis.

## Como eu quero personalizar

Quero um único arquivo config.yml para editar nome, descrição, cores, logo e tamanho, provedores e modelos, limite de resposta, instruções e perguntas de exemplo. Quero editar esse arquivo pelo GitHub.

## Como eu quero publicar

O código fica no GitHub e o chat no Hugging Face Spaces. Cada commit na main deve executar os testes no GitHub Actions. Só depois da aprovação dos testes o projeto será enviado ao Space. Uma configuração inválida deve impedir a publicação e preservar a versão anterior.

## Segurança

Chaves de API ficam nos secrets do Hugging Face e nunca no código. O token de publicação fica nos secrets do GitHub. Os testes devem detectar padrões de chaves expostas nos arquivos. O repositório não deve conter dados reais de clientes ou documentos internos sigilosos.

## Aparência

A página deve mostrar nome, descrição e logo. A interface deve estar em português e ter cores com contraste adequado. As escolhas visuais serão definidas na especificação.

## Perguntas de exemplo

- O que é chargeback e como ele difere de um reembolso?
- Quais indicadores ajudam a acompanhar chargebacks?
- Como a qualidade dos dados afeta uma análise de chargeback?
- Como Machine Learning pode ajudar a estudar o risco de chargeback?

## O que fica para depois

- Consulta aos documentos e respostas com fontes: Parte 2.
- Interface própria: Parte 3.
- Ingestão de transações, análise de datasets e modelos preditivos: evoluções futuras.
- Login e histórico persistente de conversas.

## Como vou saber que deu certo

- Abro a URL pública e converso em português.
- Altero uma cor ou pergunta pelo GitHub e vejo a atualização automática.
- Uma configuração inválida bloqueia a publicação sem alterar a versão no ar.
- Nenhuma chave aparece nos arquivos ou nas mensagens do chat.

## Próxima etapa

Gerar SPEC-parte1-cicd-deploy.md a partir desta ideia, esclarecendo as decisões que faltam. Revisar e aprovar a especificação antes de implementar. Depois, executar uma tarefa por vez e verificar os critérios de aceite.
