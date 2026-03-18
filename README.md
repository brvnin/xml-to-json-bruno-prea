Aqui está o **README.md** atualizado, destacando que o fluxo foi projetado especificamente para quem utiliza o **Bling ERP** e o site de **Pré-Postagem dos Correios**.

---

# 📦 Conversor NFe (Bling) para Pré-Postagem Correios

Este aplicativo foi desenvolvido para servir como a "ponte" ideal entre o seu faturamento e a sua logística. Ele automatiza a conversão de Notas Fiscais Eletrônicas (XML) exportadas do **Bling.com.br** para o formato de importação em lote aceito pelo site oficial de **Pré-Postagem dos Correios** (JSON).

## 🚀 Fluxo de Operação

O sistema foi desenhado para seguir estas 3 etapas principais:

1.  **Bling ➔ App:** Você exporta os arquivos XML das suas notas emitidas no **Bling**.
2.  **App ➔ JSON:** O aplicativo lê os XMLs, permite que você escolha o tamanho das caixas padronizadas, corrija telefones ausentes e gere um único arquivo JSON compatível com o validador dos Correios.
3.  **App ➔ Correios:** Você faz o upload deste JSON no site [prepostagem.correios.com.br](https://prepostagem.correios.com.br/), gerando todas as etiquetas de uma só vez, sem precisar digitar endereço por endereço.

## 🛠️ Funcionalidades Principais

*   **Compatibilidade Total com Bling:** Extração precisa de campos como Chave da NFe, Valor dos Produtos (para Seguro) e dados do destinatário.
*   **Tratamento de Dados Logísticos:** 
    *   Separação automática de **DDD** e **Número** de celular (exigência do portal Correios).
    *   Preenchimento de campos obrigatórios que o XML não possui (como o campo de ciência de objeto não proibido).
*   **Tabela de Embalagens (Bruno do Preá):** Seleção rápida de caixas como *Baianinha*, *Casadeira*, *Trinca*, etc., com pesos e medidas pré-configurados.
*   **Pós-Venda via WhatsApp:** Após postar, o app permite colar o código de rastreio e abrir o chat do cliente com uma mensagem de agradecimento e oferta de frete grátis.

## 📦 Configuração de Caixas (Banco de Dados)

O app utiliza as dimensões padrão da sua operação:

| Descrição | Peso (g) | Altura | Largura | Comprimento |
| :--- | :--- | :--- | :--- | :--- |
| **Baianinha** | 4000 | 44 | 25 | 44 |
| **Casadeira** | 6000 | 44 | 25 | 55 |
| **Trinca** | 6000 | 50 | 30 | 50 |
| **Piracicaba** | 8000 | 60 | 55 | 30 |
| **2Baianinha** | 8000 | 44 | 44 | 44 |
| **2Casadeiras** | 12000 | 44 | 44 | 55 |
| **3Baianinhas** | 12000 | 44 | 44 | 60 |

## 💻 Como Instalar e Rodar

1.  **Pré-requisito:** Instale o Python em seu computador.
2.  **Bibliotecas:** Abra o terminal e instale as dependências:
    ```bash
    pip install streamlit pandas
    ```
3.  **Execução:** Na pasta do arquivo `conversor_correios.py`, execute:
    ```bash
    streamlit run conversor_correios.py
    ```
4.  **Navegador:** O sistema abrirá em `http://localhost:8501`.

## 📝 Exemplo de Mensagem de WhatsApp Gerada

> "Olá **[Nome do Cliente]**, aqui é do **[Sua Loja]**. 🐾
>
> Segue o código de rastreio do seu pedido: **[CÓDIGO]**
> Você pode acompanhar clicando aqui: https://rastreamento.correios.com.br/...
>
> Também preparamos um tutorial para te ajudar: um dos nossos atendentes vai entrar em contato com você para, caso queira comprar algo a mais, aproveitar o frete grátis! 📦
>
> Obrigado pela preferência!"

---
**Foco do Projeto:** Produtividade e redução de erros manuais na integração Bling ➔ Correios.
