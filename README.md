# Mini-RAG sobre a documentacao do HTTPX

## Identificacao

- Nome do aluno: Sillas Sena
- Formato da solucao: script Python de terminal
- Link do video: a preencher

## Objetivo

Construir o nucleo de recuperacao de um RAG para a documentacao do HTTPX. A
primeira etapa obtem o repositorio na versao exigida e localiza os documentos
Markdown que serao indexados.

## Arquitetura resumida

```text
RAGApplication -> RetrievalAgent -> documentos -> chunks -> embeddings -> busca
               -> Gemini opcional -> resposta fundamentada
```

`RAGApplication` e o agente principal: prepara o repositorio e coordena o
fluxo. `RetrievalAgent` e o subagente especializado no corpus e, nas proximas
etapas, na recuperacao semantica.

## Como executar do zero

1. Use Python 3.10 ou superior e Git instalados.
2. Na pasta deste projeto, execute:

   ```bash
   python -m pip install -r requirements.txt
   python main.py
   ```

3. O programa clona o HTTPX em `data/httpx`, fixa o commit
   `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`, lista os Markdown de `docs/` e
   exibe um chunk rastreavel de exemplo.
4. A validacao esperada nesta etapa e a descoberta de 23 arquivos e a criacao
   de chunks.
5. Para consultar a documentacao em portugues:

   ```bash
   python main.py --question "Como desativar o timeout de uma requisicao?"
   ```

6. Para listar os 23 arquivos e inspecionar um chunk antes da busca, acrescente
   `--inspect-corpus` ao comando.
7. Para gerar uma resposta opcional com Gemini, crie um arquivo `.env` na raiz
   do projeto com a linha abaixo e use `--generate`:

   ```text
   GEMINI_API_KEY=sua-chave
   ```

   Alternativamente, defina a chave apenas no ambiente do terminal:

   ```powershell
   $env:GEMINI_API_KEY="sua-chave"
   python main.py --question "Como desativar o timeout de uma requisicao?" --generate
   ```

   A chave nao deve ser adicionada a arquivos, commits, README ou video.

## Estado atual

- [x] Repositorio HTTPX obtido no commit exigido
- [x] Descoberta recursiva de Markdown em `httpx/docs/`
- [x] Leitura e chunking
- [x] Embeddings
- [x] Busca por similaridade
- [x] Integracao opcional com Gemini implementada
- [x] Chamada real ao Gemini validada com uma chave configurada localmente
- [ ] Perguntas de teste

## Decisoes tecnicas

### Chunking

- Estrategia: separar cada Markdown por titulos e dividir o corpo de cada secao.
- Tamanho aproximado: 80 palavras por chunk.
- Overlap: 15 palavras entre chunks consecutivos da mesma secao.
- Justificativa: o tamanho mantem contexto suficiente para a busca e fica abaixo
  do limite de 128 tokens do modelo de embeddings sugerido. O titulo da secao e
  repetido no texto de cada chunk para preservar o contexto.

### Metadados e fontes

Cada `DocumentChunk` guarda `chunk_id`, `text`, `source_path` e `section`. O
caminho e relativo ao repositorio HTTPX, o que permite reencontrar o documento
de origem na saida da busca.

### Embeddings e busca

- Modelo: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- Similaridade: produto escalar entre vetores normalizados, equivalente a
  similaridade cosseno.
- `top_k`: 3 por padrao, limitado a valores entre 3 e 5.
- Justificativa: o modelo e publico, executa localmente e representa perguntas
  em portugues e documentacao em ingles no mesmo espaco vetorial.

### Guardrails

- Perguntas vazias sao recusadas com mensagem compreensivel.
- `top_k` deve ser um inteiro entre 3 e 5.
- O indice precisa existir antes da busca.
- Um corpus sem chunks nao pode ser indexado.
- Score maximo abaixo de `0.25` gera aviso de possivel pergunta fora do escopo.
- O Gemini nao e chamado quando a evidencia recuperada e fraca.
- O prompt limita a resposta ao contexto recuperado e exige citacoes das fontes.

### Geracao opcional

- Modelo: `gemini-3.6-flash` pela Gemini API.
- O modelo recebe somente a pergunta e os chunks recuperados, nunca a chave de
  API ou documentos fora do contexto.

## Limitacoes conhecidas

A divisao por palavras simplifica Markdown e blocos de codigo. Os scores de
similaridade indicam proximidade vetorial, nao probabilidade ou garantia factual.
O limiar de `0.25` e experimental e sera reavaliado com as perguntas de teste.
Consultas amplas podem recuperar uma secao relacionada, mas nao necessariamente
a mais didatica. Por exemplo, uma pergunta sobre recursos do HTTPX priorizou
dependencias e pacotes relacionados em vez da lista principal de funcionalidades.

## Perguntas de teste

### 1. Pergunta com resposta clara

- Pergunta: `Como desativar o timeout de uma requisicao?`
- Resultado esperado: instrucao com `timeout=None`.
- Resultado observado: `docs/advanced/timeouts.md`, secao `Setting and disabling
  timeouts`, ficou na primeira posicao com score `0.4255`.
- O resultado foi relevante: sim. O trecho mostra `timeout=None` para requisicao
  individual e para cliente.
- Geracao opcional: Gemini respondeu usando esse trecho e citou
  `docs/advanced/timeouts.md`, secao `Setting and disabling timeouts`.

### 2. Pergunta ampla ou ambigua

- Pergunta: `Quais sao os principais recursos do HTTPX?`
- Resultado esperado: visao geral das funcionalidades do projeto.
- Resultado observado: a primeira fonte foi `docs/index.md`, mas na secao de
  dependencias; tambem apareceram pacotes de terceiros.
- O resultado foi relevante: parcialmente. As fontes pertencem ao ecossistema
  HTTPX, mas a busca pode melhorar para priorizar a secao `Features`.

### 3. Pergunta fora do escopo

- Pergunta: `Qual e a capital da Franca?`
- Como o sistema reagiu: mostrou apenas scores baixos, com maximo de `0.1070`, e
  avisou que nao havia evidencia suficiente na documentacao.
- Como essa reacao poderia melhorar: um limiar calibrado com mais perguntas e
  uma resposta gerada que se recuse a responder sem contexto suficiente.

## Uso de ferramentas de IA

- Ferramentas utilizadas: OpenCode e Gemini API.
- Tarefas em que ajudaram: OpenCode apoiou a orientacao e revisao da estrutura;
  Gemini pode gerar uma resposta opcional fundamentada nos trechos recuperados.
- Exemplo representativo de orientacao: separar o agente coordenador do agente
  de recuperacao e validar primeiro os 23 documentos obrigatorios.
- O que foi testado, modificado ou validado por voce: a preencher apos executar.

## Seguranca

- [x] Minha solucao usa segredo protegido e nenhuma chave foi publicada.
