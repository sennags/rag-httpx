# Deploy no Hugging Face Spaces

## Criar o Space

1. Crie uma conta em <https://huggingface.co>.
2. Crie um Space do tipo **Docker** com hardware CPU gratuito, se disponivel.
3. Conecte ou envie este repositorio ao Space.

## Configurar segredo opcional

Em **Settings > Variables and secrets**, crie o Secret:

```text
GEMINI_API_KEY
```

Nao adicione um arquivo `.env` ao Space ou ao GitHub.

## Comportamento no Space

- O Dockerfile inicia a interface na porta 7860.
- Na primeira consulta, o projeto baixa o repositorio HTTPX e cria o indice local.
- O cache pode ser perdido quando o Space reiniciar; a aplicacao o recria.
- Ollama e exclusivo para uso local e nao e instalado no Space gratuito.
- Gemini permanece opcional: a busca mostra fontes mesmo sem Secret ou quando a API falhar.
