---
title: Aprendendo Dados
emoji: 📊
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
python_version: "3.12"
pinned: false
---

# Aprendendo Dados

Agente de IA personalizado que explica estatística e machine learning com exemplos práticos e exercícios, passo a passo. Nesta etapa, responde pelo OpenRouter. A consulta aos documentos será acrescentada na Parte 2.

## Rodar no computador

Instale Python 3.11 ou 3.12. Baixe este repositório em **Code > Download ZIP**, extraia e abra o terminal na pasta que contém app.py.

### macOS ou Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-local.txt
python testes.py
python iniciar.py
```

### Windows, usando PowerShell

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-local.txt
.venv\Scripts\python.exe testes.py
.venv\Scripts\python.exe iniciar.py
```

O iniciador solicita sua chave do OpenRouter de forma oculta. Ela fica no ambiente do processo e não é salva em arquivo. Abra **http://localhost:7860**. Para encerrar, use Ctrl+C no terminal. Se a chave já estiver na variável OPENROUTER_API_KEY, também pode executar python app.py.

## Personalização

Edite config.yaml para alterar nome, descrição, cores, logo, modelo, limite de resposta, instruções e perguntas. Cores devem estar entre aspas. O modelo inicial google/gemma-4-31b-it:free usa um modelo gratuito específico, sujeito a limites e disponibilidade.

## Verificações

```bash
python testes.py
python -m unittest test_comportamento.py
```

O portão confere T1 a T9. Os testes de conversa usam simulações e não gastam créditos. Uma conversa real exige sua chave e acesso ao OpenRouter.

## Publicar no Hugging Face

Space criado: https://huggingface.co/spaces/oaraujo/chargeback-intelligence, com SDK Gradio e ZeroGPU confirmado pela tela de configurações. O app registra uma função com @spaces.GPU, conforme o exemplo da aula, sem solicitar GPU nas conversas. A geração de respostas acontece no OpenRouter.

Para concluir a publicação:

1. Use o Space oaraujo/chargeback-intelligence com SDK Gradio e hardware ZeroGPU.
2. Em Settings do Space, cadastre OPENROUTER_API_KEY como **secret**.
3. No GitHub, em Settings > Secrets and variables > Actions, cadastre HF_TOKEN como **secret**, com permissão de escrita no Space.
4. Na aba Variables do mesmo painel, cadastre PUBLICAR_SPACE com valor true. HF_USUARIO e HF_SPACE têm padrões oaraujo e chargeback-intelligence; use variáveis com esses nomes se precisar alterar.
5. Na aba Actions, execute o workflow **Testar e publicar**.
6. Confira os jobs, o build do Space e o estado Running. Abra a URL e teste uma conversa.

Sem PUBLICAR_SPACE=true, somente os testes rodam. Não coloque chaves no código, no config ou no HTML. A publicação usa Git com histórico completo, como no exemplo da aula, e substitui a main do Space com a main deste projeto. Não edite código separadamente no Space.

## Testar o bloqueio

Troque temporariamente cor_principal por "#FFD966" e faça commit. O teste de contraste deve falhar e o job publicar não deve começar. Restaure "#142C40" em seguida.

## Próxima aula

Prepare de 3 a 5 documentos públicos sobre estatística e machine learning em Markdown, sem dados pessoais ou sigilosos. Crie sua conta no Supabase. O banco, a indexação e a busca documental serão implementados na Parte 2.

## Referência da aula

Referência: https://github.com/azrosolucoestecnologicas/agente-personalizado e apostila da Parte 1. Especialidade: Estatística e Machine Learning. A logo fica em assets/logo.svg. Somente o modelo gratuito google/gemma-4-31b-it:free é usado. O SSR experimental do Gradio fica desativado.

## Alternativa gratuita

O Gemma é tentado primeiro. Quando o OpenRouter identifica uma falha elegível antes da resposta, pode tentar openai/gpt-oss-20b:free. A solicitação limita o preço dos tokens de entrada e saída a zero. Nenhuma chave adicional é necessária. Limites da conta ou indisponibilidade de ambos os modelos ainda podem impedir uma resposta.
