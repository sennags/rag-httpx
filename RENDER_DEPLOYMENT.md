# Deploy no Render

## Configuracao incluida

O `render.yaml` declara um Web Service Docker gratuito. O `Dockerfile` instala
Git, inicia a aplicacao com Gunicorn e usa a porta definida pelo Render em
`PORT`. O processo usa um unico worker para evitar carregar o modelo de
embeddings mais de uma vez.

## Publicar

1. Envie este commit para o repositorio GitHub.
2. No Render, escolha **New** > **Blueprint** e conecte o repositorio.
3. Confirme o servico `httpx-rag-sennags` e o plano **Free**.
4. Aguarde o primeiro build e abra a URL fornecida pelo Render.
5. Envie uma pergunta no modo **Somente evidencias**. A primeira consulta clona
   o HTTPX e cria os embeddings; as seguintes reutilizam o cache enquanto a
   instancia estiver ativa.

## Variaveis de ambiente

Nenhuma variavel e necessaria para recuperar trechos e fontes.

Se a geracao Gemini for desejada, adicione apenas no painel do Render:

```text
GEMINI_API_KEY=sua-chave
```

Nao crie, envie ou versiona um arquivo `.env` para o deploy. O Ollama local nao
e disponibilizado no Render, pois ele depende de um processo e modelo instalados
na maquina local.

## Limitacoes do plano gratuito

- A instancia pode entrar em repouso, produzindo uma inicializacao mais lenta.
- O disco e efemero: apos reinicio, o clone HTTPX e o indice local podem ser
  recriados na primeira consulta.
- O carregamento do modelo de embeddings consome memoria; manter um worker reduz
  esse consumo, mas o plano gratuito pode nao comportar picos de uso.
