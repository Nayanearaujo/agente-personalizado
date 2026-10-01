# Especificação da Parte 1: CI/CD e deploy

Status: aprovada para implementação em 01/10/2026. Tema adaptado para chargeback.

## 1. Objetivo, público e escopo

Construir um chat educativo em português para estudantes e profissionais interessados em chargeback, Engenharia de Dados, Estatística e Machine Learning. O usuário abre uma URL e conversa com o assistente.

Nesta etapa entram personalização por configuração, conversa com histórico de sessão, respostas progressivas e publicação automática com testes. Consulta a documentos fica para a Parte 2. Interface própria fica para a Parte 3. Login, histórico persistente, análise de transações e previsões ficam fora desta etapa.

## 2. Stack e restrições do Hugging Face

Python, Gradio, OpenAI SDK para acessar o OpenRouter e PyYAML. Fixar as versões após verificar compatibilidade na implementação.

Modelo inicial: openrouter/free. Somente OpenRouter nesta etapa, seguindo o exemplo da apostila.

Hugging Face: usuário naycode; Space pretendido chargeback-intelligence; SDK Gradio. A tela da conta atual exige plano pago para criar o Space. Nenhum Space está confirmado. Manter publicação desativada até resolver a hospedagem, sem contratar automaticamente.

A apostila usa ZeroGPU. Se esse hardware estiver disponível, conferir as exigências atuais da biblioteca spaces antes de implementar sua integração. Não inserir uma função fictícia de GPU sem verificar compatibilidade. Usar logo SVG evita envio de imagem binária no fluxo Git do exemplo.

## 3. Estrutura de arquivos

| Arquivo | Função |
| --- | --- |
| app.py | Interface e chamada ao OpenRouter |
| config.yml | Textos, cores, logo, modelo e instruções |
| logo.svg | Logo |
| validacao.py | Regras compartilhadas de configuração |
| testes.py | Portão T1 a T9 |
| requirements.txt | Dependências |
| README.md | Instruções e cabeçalho do Space |
| .gitignore | Exclusões locais |
| .github/workflows/deploy.yml | Testar e publicar |
| IDEIA-parte1.md | Ideia |
| SPEC-parte1-cicd-deploy.md | Esta especificação |

O HTML da ideia é um documento de leitura adicional.

## 4. Contrato da configuração

Todos os campos abaixo são obrigatórios. Os padrões são os valores entregues no arquivo inicial, sem substituir silenciosamente campos ausentes.

| Campo | Valores aceitos | Padrão |
| --- | --- | --- |
| nome | Texto de 1 a 80 caracteres | Chargeback Intelligence |
| descricao | Texto de 1 a 240 caracteres | Assistente para entender chargeback, analisar indicadores e estudar formas de prevenir perdas. |
| cor_principal | #RRGGBB entre aspas; contraste com branco de pelo menos 3:1 | #142C40 |
| cor_secundaria | Mesma regra | #096B66 |
| logo | SVG local dentro do projeto ou URL HTTPS sem credenciais | logo.svg |
| logo_tamanho | Inteiro entre 32 e 160 | 64 |
| modelo | Nome no formato fornecedor/modelo | openrouter/free |
| max_tokens | Inteiro entre 1 e 4096 | 800 |
| prompt_sistema | Texto com pelo menos 80 caracteres | Instruções educativas sobre chargeback |
| exemplos | De 1 a 8 perguntas preenchidas | Quatro perguntas sobre conceitos, indicadores, qualidade de dados e ML |

Rejeitar campos desconhecidos e duplicados. Nenhuma chave de API entra na configuração.

## 5. Requisitos funcionais

- RF1: Mostrar nome, descrição, cores e logo configurados.
- RF2: Responder em português usando o modelo configurado no OpenRouter.
- RF3: Enviar prompt de sistema e histórico da sessão a cada pergunta.
- RF4: Exibir respostas progressivamente.
- RF5: Mostrar exemplos clicáveis e opção de limpar conversa.
- RF6: Validar a configuração antes de iniciar.
- RF7: Explicar falhas sem revelar credenciais ou conteúdo sensível.
- RF8: Ler OPENROUTER_API_KEY do ambiente ou dos secrets do Space.
- RF9: Executar o portão a cada push na main e por acionamento manual.
- RF10: Publicar somente após aprovação do portão.
- RF11: Uma configuração reprovada não deve alterar a versão no ar.
- RF12: Permitir execução local enquanto a hospedagem está pendente.
- RF13: Usar exemplos fictícios, reconhecer incertezas e distinguir chargeback, fraude e reembolso.
- RF14: Não inventar regras, prazos ou fontes; orientar consulta à documentação aplicável quando houver variação por bandeira, adquirente ou contrato.
- RF15: Não pedir dados de cartão ou informações sigilosas, nem salvar conversas.

Instruções ao modelo não garantem ausência de erros. A Parte 2 acrescentará suporte documental.

## 6. Portão de testes

- T1: YAML válido, arquivo existente e ausência de campos duplicados.
- T2: Campos obrigatórios preenchidos, tipos e limites válidos.
- T3: Cores no formato #RRGGBB.
- T4: Contraste com branco de pelo menos 3:1.
- T5: Logo SVG local existente ou link HTTPS, tamanho de 32 a 160.
- T6: Modelo no formato fornecedor/modelo; limite de tokens válido.
- T7: Prompt com pelo menos 80 caracteres e perguntas de exemplo válidas.
- T8: Python sem erro de sintaxe.
- T9: Ausência de padrões reconhecidos de chaves de API nos arquivos rastreados.

O portão apresenta erros em português e retorna código de falha. Não chama a API. A detecção de padrões não identifica todo segredo possível. Credencial exposta deve ser revogada.

## 7. Pipeline e configuração manual

Fluxo: push na main ou workflow_dispatch; job testar; job publicar com needs: testar; envio ao Hugging Face; build e reinício do Space.

O envio segue o fluxo Git da apostila, com histórico completo. Serializar publicações para evitar substituição fora de ordem. Não imprimir o token. Verificar que o envio não inclui binários incompatíveis.

Configurar manualmente:
- OPENROUTER_API_KEY nos secrets do Space.
- HF_TOKEN nos secrets de Actions do GitHub, com permissão suficiente para o Space.
- HF_USUARIO=naycode e HF_SPACE=chargeback-intelligence.
- PUBLICAR_SPACE=false inicialmente; habilitar apenas quando houver Space compatível.

Com publicação desativada, testes podem passar e o job publicar será ignorado. Isso não é deploy concluído. Falha de build remoto exige consultar logs e restaurar uma versão funcional; o portão não garante que todo build remoto tenha sucesso.

## 8. Critérios de aceite

- [ ] T1 a T9 passam.
- [ ] Interface local apresenta a personalização.
- [ ] Conversa real funciona sem expor a chave.
- [ ] Uma segunda pergunta usa o histórico.
- [ ] Limpar remove o histórico da sessão.
- [ ] Erros de chave ausente, autenticação e limite são compreensíveis.
- [ ] Space compatível criado e estado Running confirmado.
- [ ] URL pública permite conversar.
- [ ] Alteração válida pelo GitHub atualiza o chat.
- [ ] Cor #FFD966 reprova o portão sem alterar a versão publicada.
- [ ] Restaurar a cor válida retorna o processo ao sucesso.

Publicação permanece pendente até resolver a restrição da conta. A Parte 1 não está concluída só com o teste local.

## 9. Ordem das tarefas

1. Configuração, logo SVG e validação dos campos.
2. Portão testes.py com T1 a T9.
3. Chat Gradio com OpenRouter, histórico e streaming.
4. Dependências verificadas, README, .gitignore e workflow com publicação desativada.
5. Segredos e publicação quando a hospedagem estiver disponível.
6. Testes manuais de atualização e bloqueio.

Uma tarefa por vez, com explicação de como testar antes de avançar.

## 10. Erros comuns

| Problema | Correção |
| --- | --- |
| YAML inválido | Conferir espaços, aspas e campos repetidos |
| Cor vazia | Colocar #RRGGBB entre aspas |
| Chave ausente | Conferir OPENROUTER_API_KEY no ambiente |
| Modelo inválido | Usar o identificador do OpenRouter |
| Limite gratuito atingido | Aguardar renovação ou revisar modelo |
| Workflow ausente | Conferir .github/workflows/deploy.yml |
| Publicação ignorada | Conferir PUBLICAR_SPACE e disponibilidade do Space |
| Erro de autenticação no deploy | Conferir nome e permissão de HF_TOKEN |
| Build remoto falha | Conferir cabeçalho do README e logs |
| Conversa some ao fechar a aba | Esperado, sem banco nesta etapa |
