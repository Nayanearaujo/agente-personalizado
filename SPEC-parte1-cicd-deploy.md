# Especificação da Parte 1: chat e publicação automática

Status: proposta para revisão. Implementação ainda não iniciada.

## 1. Objetivo

Construir o Chargeback Intelligence, um chat em português para estudar chargeback e suas relações com Engenharia de Dados, Estatística e Machine Learning. Exemplos devem ser fictícios. O projeto deve funcionar localmente e estar preparado para publicação automática após testes.

## 2. Escopo e decisões iniciais

- Interface com Gradio e aplicação em Python.
- OpenRouter como provedor inicial, usando openrouter/free. Disponibilidade e limites serão conferidos na implementação.
- Suporte configurável a OpenAI e Anthropic como alternativas, desativadas inicialmente para evitar uso pago involuntário.
- Nome: Chargeback Intelligence.
- Descrição: Assistente para entender chargeback, analisar indicadores e estudar formas de prevenir perdas.
- Cores propostas: principal #142C40 e secundária #096B66, com texto branco nos elementos correspondentes.
- Logo SVG local simples, tamanho inicial de 64 pixels.
- Limite inicial de saída: 800 tokens.
- Sem upload de arquivos, execução de previsões, login ou histórico persistente.
- Consulta aos documentos fica para a Parte 2; interface própria fica para a Parte 3.

## 3. Situação da hospedagem

Repositório: Nayanearaujo/chargeback-intelligence. Usuário do Hugging Face: naycode. Nome proposto do Space: chargeback-intelligence.

A conta atual mostrou exigência de plano pago para Gradio. Nenhum Space está confirmado. Preparar o workflow, mas manter publicação desativada até existir um Space compatível. Não contratar plano ou hardware automaticamente.

O modo local permite validar o chat, mas não conclui o critério de URL pública. Se outro provedor de hospedagem for escolhido, revisar esta especificação antes de adaptar o deploy.

## 4. Stack e arquivos

Python, Gradio, PyYAML, cliente da API OpenAI para OpenRouter e OpenAI, cliente Anthropic para a alternativa correspondente. Fixar versões compatíveis após conferir documentação e testar na implementação.

| Arquivo | Papel |
| --- | --- |
| app.py | Interface, histórico da sessão e chamada aos provedores |
| config.yml | Personalização sem editar Python |
| validacao.py | Regras comuns ao aplicativo e aos testes |
| testes.py | Verificações T1 a T9 |
| requirements.txt | Dependências com versões fixadas |
| assets/logo.svg | Logo inicial |
| README.md | Como executar, configurar e publicar; metadados do Space |
| .gitignore | Impedir inclusão de arquivos locais sensíveis |
| .github/workflows/deploy.yml | Testes e publicação condicional |
| IDEIA-parte1.md | Ideia original |
| SPEC-parte1-cicd-deploy.md | Este contrato de implementação |

O HTML da ideia permanece como documento de leitura.

## 5. Contrato do config.yml

Nenhuma chave de API pode ser colocada neste arquivo.

| Campo | Regra | Valor inicial |
| --- | --- | --- |
| nome | Texto obrigatório, 1 a 80 caracteres | Chargeback Intelligence |
| descricao | Texto obrigatório, 1 a 240 caracteres | Descrição da seção 2 |
| cor_principal | Cor hexadecimal #RRGGBB; contraste com branco de pelo menos 3:1 | #142C40 |
| cor_secundaria | Mesma regra da cor principal | #096B66 |
| logo | Caminho SVG existente dentro do projeto ou URL HTTPS | assets/logo.svg |
| logo_tamanho | Inteiro entre 32 e 160 | 64 |
| provedores | Lista não vazia, em ordem de preferência | Somente OpenRouter |
| provedores[].tipo | openrouter, openai ou anthropic | openrouter |
| provedores[].modelo | Texto não vazio; OpenRouter exige fornecedor/modelo | openrouter/free |
| provedores[].max_tokens | Inteiro entre 1 e 4096 | 800 |
| prompt_sistema | Texto com pelo menos 80 caracteres | Comportamento da seção 6 |
| exemplos | Lista de 1 a 8 perguntas não vazias | Perguntas da ideia |

Campos desconhecidos devem produzir mensagem de validação para evitar erros de digitação silenciosos. Não permitir configurar URLs de API arbitrárias. Os endereços dos provedores ficam definidos no código.

## 6. Requisitos funcionais

- RF1: Mostrar nome, descrição, logo e cores definidos na configuração.
- RF2: Permitir conversa em português, mantendo histórico somente durante a sessão aberta e reenviando-o nas perguntas seguintes.
- RF3: Exibir a resposta progressivamente quando o provedor oferecer streaming.
- RF4: Aplicar o prompt de sistema em todas as chamadas.
- RF5: Mostrar perguntas de exemplo clicáveis e opção de limpar a conversa.
- RF6: Consultar provedores na ordem configurada. Chave ausente ou falha antes do primeiro conteúdo permite tentar o próximo.
- RF7: Se todos falharem, informar o motivo resumido por provedor, sem dados sensíveis.
- RF8: Se ocorrer falha após iniciar a resposta, avisar que foi interrompida. Não concatenar respostas de provedores diferentes.
- RF9: Validar a configuração antes de iniciar o chat, com mensagens claras sobre campo e correção.
- RF10: Executar testes a cada push na main e permitir execução manual do workflow.
- RF11: Publicar somente depois da aprovação dos testes e quando a publicação estiver habilitada.
- RF12: Ler credenciais exclusivamente das variáveis de ambiente.
- RF13: Funcionar localmente com publicação desativada.
- RF14: Explicar conceitos com exemplos fictícios, reconhecer incertezas e não afirmar regras ou prazos específicos sem suporte. Orientar consulta à documentação aplicável quando o procedimento variar.
- RF15: Não solicitar números de cartão ou informações sigilosas. Não gravar conteúdo de conversas em logs ou arquivos.
- RF16: Não apresentar o chat como um sistema que já analisa transações ou prevê risco.

O prompt deve distinguir chargeback, fraude e reembolso, adaptar a profundidade ao usuário e apresentar respostas claras. As instruções reduzem respostas inadequadas, mas não garantem ausência de erros do modelo. Na Parte 2, a consulta documental dará suporte verificável às respostas.

## 7. Verificações do portão

- T1: config.yml existe e é YAML válido, sem chaves duplicadas.
- T2: Campos obrigatórios, tipos, limites e ausência de campos desconhecidos.
- T3: Cores no formato #RRGGBB.
- T4: Contraste das duas cores com texto branco de pelo menos 3:1.
- T5: Logo local SVG existente e dentro do projeto, ou URL HTTPS válida; tamanho entre 32 e 160. URLs não são baixadas durante o teste.
- T6: Lista e tipos dos provedores válidos, modelos no formato aplicável e limites de tokens válidos.
- T7: Prompt preenchido com pelo menos 80 caracteres e exemplos válidos.
- T8: Arquivos Python do projeto compilam sem erro de sintaxe.
- T9: Arquivos rastreados não contêm padrões reconhecidos de chaves de API ou credenciais reais. Marcadores de exemplo devem ser claramente fictícios.

Os testes retornam código diferente de zero quando falham e listam todos os problemas encontrados. Não chamam modelos pagos ou exigem credenciais reais. A busca por padrões de chave é uma proteção adicional e não detecta todo segredo possível. Chave exposta deve ser revogada.

Testes de comportamento com chamadas simuladas devem verificar ordem de fallback, falha parcial no streaming, histórico e ocultação de credenciais. O teste manual com a chave real confirma integração, sem registrar seu valor.

## 8. Segredos e responsabilidades

| Nome | Onde fica | Uso |
| --- | --- | --- |
| OPENROUTER_API_KEY | Ambiente local ou secrets do Space | Provedor inicial |
| OPENAI_API_KEY | Ambiente local ou secrets do Space, se usado | Alternativa opcional |
| ANTHROPIC_API_KEY | Ambiente local ou secrets do Space, se usado | Alternativa opcional |
| HF_TOKEN | Secrets do repositório no GitHub | Publicar no Space |

Variáveis públicas do repositório: HF_USUARIO=naycode, HF_SPACE=chargeback-intelligence e PUBLICAR_SPACE=false inicialmente. Credencial de publicação deve ter a menor permissão suficiente para o Space.

Arquivos .env, ambientes virtuais, caches e logs ficam fora do Git. Nenhuma chave vai para HTML, configuração, mensagem de erro ou saída do workflow.

## 9. Pipeline

1. Push na main ou execução manual inicia o workflow.
2. Job testar baixa os arquivos, instala dependências necessárias e roda T1 a T9 e os testes de comportamento.
3. Falha interrompe a publicação e preserva a versão em execução.
4. Com testes aprovados e PUBLICAR_SPACE=true, job publicar envia apenas arquivos necessários à aplicação para o Space correto.
5. PUBLICAR_SPACE=false deixa o job publicar marcado como ignorado. Isso não significa que houve deploy.
6. Serializar publicações para evitar que uma versão antiga substitua uma mais recente.
7. Após enviar, conferir build, estado Running e uma conversa real.

Não enviar imagens PNG/JPG ou artefatos temporários junto ao código. A logo inicial é SVG. O teste anterior ao envio não garante sucesso do build remoto; se ele falhar, consultar logs e restaurar a última versão funcional.

## 10. Critérios de aceite

### Execução local

- [ ] T1 a T9 aprovados.
- [ ] Interface abre com nome, logo, descrição e perguntas.
- [ ] Uma conversa real funciona usando o provedor gratuito.
- [ ] A segunda pergunta recebe o histórico da sessão.
- [ ] Limpar remove a conversa da sessão.
- [ ] Chave ausente e indisponibilidade geram mensagens compreensíveis.
- [ ] Fallback e interrupção parcial são verificados com simulações.
- [ ] Nenhum segredo aparece nos arquivos ou erros.

### Publicação, pendente de hospedagem

- [ ] Space compatível criado e segredos cadastrados.
- [ ] Workflow aprovado e Space em Running.
- [ ] Chat acessível pela URL pública.
- [ ] Alteração válida no config atualiza a página automaticamente.
- [ ] Cor inválida reprova o teste e a versão anterior continua disponível.
- [ ] Restaurar a configuração válida faz os testes passarem novamente.

A Parte 1 só estará concluída quando as duas listas forem atendidas.

## 11. Ordem das tarefas

1. Criar config.yml, logo SVG e validacao.py. Conferir leitura da configuração e mensagens para erros reais.
2. Implementar T1 a T9 em testes.py e demonstrar sucesso e bloqueio de configuração inválida.
3. Implementar os adaptadores de provedor, histórico e streaming; testar falhas e fallback com simulações.
4. Construir a interface Gradio e conferir visual e funcionamento local.
5. Fixar dependências testadas, preparar README, .gitignore e workflow com publicação desativada.
6. Quando a hospedagem estiver disponível, cadastrar segredos, habilitar publicação e testar os critérios remotos.

Executar uma tarefa por vez, explicar como verificar e registrar o resultado. Não iniciar a implementação antes da revisão desta proposta.

## 12. Erros comuns

| Problema | Como investigar |
| --- | --- |
| YAML inválido | Verificar espaços, aspas e campo indicado pelo teste |
| Cor vazia | Usar aspas em valores que começam com # |
| Chave ausente | Conferir o nome da variável no ambiente ou nos secrets |
| Erro de autenticação | Conferir ou substituir a chave no painel do provedor |
| Limite do modelo gratuito | Aguardar a renovação do limite ou revisar o modelo |
| Publicação ignorada | Conferir PUBLICAR_SPACE; permanece false enquanto não houver hospedagem |
| Falha de envio ao Space | Conferir usuário, nome do Space e permissão do token |
| Falha de build remoto | Consultar logs e compatibilidade das versões fixadas |
| Chat sem memória após fechar a aba | Comportamento esperado nesta etapa |
