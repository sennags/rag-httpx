# Mini-RAG sobre a documentacao do HTTPX

## Identificacao

- Nome do aluno: a preencher
- Formato da solucao: script Python de terminal
- Link do video: a preencher

## Objetivo

Construir o nucleo de recuperacao de um RAG para a documentacao do HTTPX. A
primeira etapa obtem o repositorio na versao exigida e localiza os documentos
Markdown que serao indexados.

## Arquitetura resumida

```text
RAGApplication -> RetrievalAgent -> documentos -> chunks -> embeddings -> busca
```

`RAGApplication` e o agente principal: prepara o repositorio e coordena o
fluxo. `RetrievalAgent` e o subagente especializado no corpus e, nas proximas
etapas, na recuperacao semantica.

## Como executar do zero

1. Use Python 3.10 ou superior e Git instalados.
2. Na pasta deste projeto, execute:

   ```bash
   python main.py
   ```

3. O programa clona o HTTPX em `data/httpx`, fixa o commit
   `b5addb64f0161ff6bfe94c124ef76f6a1fba5254` e lista os Markdown de `docs/`.
4. A validacao esperada nesta etapa e a descoberta de 23 arquivos.

## Estado atual

- [x] Repositorio HTTPX obtido no commit exigido
- [x] Descoberta recursiva de Markdown em `httpx/docs/`
- [ ] Leitura e chunking
- [ ] Embeddings
- [ ] Busca por similaridade
- [ ] Perguntas de teste

## Decisoes tecnicas

### Metadados e fontes

Neste primeiro passo, o caminho de cada arquivo e mantido como `Path`. Nas
proximas etapas, cada chunk guardara tambem arquivo, secao e identificador.

## Limitacoes conhecidas

A aplicacao ainda nao le o conteudo dos documentos nem responde perguntas. A
proxima etapa sera criar chunks rastreaveis antes de introduzir embeddings.

## Uso de ferramentas de IA

- Ferramentas utilizadas: OpenCode.
- Tarefas em que ajudaram: orientacao e revisao da estrutura inicial do projeto.
- Exemplo representativo de orientacao: separar o agente coordenador do agente
  de recuperacao e validar primeiro os 23 documentos obrigatorios.
- O que foi testado, modificado ou validado por voce: a preencher apos executar.

## Seguranca

- [x] Minha solucao nao usa API key.
